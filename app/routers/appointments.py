from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import date, time, datetime
from typing import Union
import json
from pydantic import BaseModel
from app import crud, schemas
from app.database.connection import get_db
from app.auth import get_current_admin
from app.models import Appointment

router = APIRouter(prefix="/appointments", tags=["Appointments"])

def parse_vapi_request(payload: dict):
    args = {}
    tool_call_id = None
    try:
        if "message" in payload and "toolWithToolCallList" in payload["message"]:
            tc = payload["message"]["toolWithToolCallList"][0]["toolCall"]
            tool_call_id = tc.get("id")
            args = tc["function"]["arguments"]
        elif "message" in payload and "toolCalls" in payload["message"]:
            tc = payload["message"]["toolCalls"][0]
            tool_call_id = tc.get("id")
            args = tc["function"]["arguments"]
        elif "toolCalls" in payload:
            tc = payload["toolCalls"][0]
            tool_call_id = tc.get("id")
            args = tc["function"]["arguments"]
        else:
            args = payload
            
        if isinstance(args, str):
            args = json.loads(args)
    except Exception:
        pass
    
    return args, tool_call_id

def vapi_response(tool_call_id: str, result_message: str):
    if tool_call_id:
        return {
            "results": [
                {
                    "toolCallId": tool_call_id,
                    "result": result_message
                }
            ]
        }
    return {"results": [{"toolCallId": "unknown_id", "result": result_message}]}

@router.post("", response_model=None)
async def create_appointment(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    args, tool_call_id = parse_vapi_request(payload)
    
    try:
        if "patient_id" not in args:
            args["patient_id"] = 1
        if "doctor_id" not in args:
            args["doctor_id"] = 1
        if "patient_name" not in args:
            args["patient_name"] = "AI Booking"
        if "doctor_name" not in args:
            args["doctor_name"] = "Dr. Default"
            
        req_data = schemas.AppointmentCreate(**args)
        
        if isinstance(req_data.appt_time, str):
            time_obj = datetime.strptime(req_data.appt_time, "%H:%M:%S").time()
        else:
            time_obj = req_data.appt_time
            
        if isinstance(req_data.appt_date, str):
            date_obj = datetime.strptime(req_data.appt_date, "%Y-%m-%d").date()
        else:
            date_obj = req_data.appt_date

        existing_appointment = crud.get_appointment_by_time(db, date_obj, time_obj)
        
        if existing_appointment:
            return vapi_response(tool_call_id, "Sorry, this time slot is already booked. Please pick another time.")
            
        new_appt = crud.create_appointment(db, req_data)
        success_msg = f"Success! The appointment has been booked. Please tell the user their Appointment ID is {new_appt.id}"
        return vapi_response(tool_call_id, success_msg)
        
    except Exception as e:
        return vapi_response(tool_call_id, str(e))

@router.post("/check-availability", response_model=None)
async def check_availability(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    args, tool_call_id = parse_vapi_request(payload)
    
    try:
        check_date_obj = datetime.strptime(args.get("check_date", ""), "%Y-%m-%d").date()
        check_time_obj = datetime.strptime(args.get("check_time", ""), "%H:%M:%S").time()
        
        existing = crud.get_appointment_by_time(db, check_date_obj, check_time_obj)
        
        if existing:
            return vapi_response(tool_call_id, "The time slot is already booked. Please suggest another time.")
        
        return vapi_response(tool_call_id, "The time slot is free and available for booking.")
        
    except Exception as e:
        return vapi_response(tool_call_id, str(e))

@router.post("/reschedule", response_model=None)
async def reschedule_appointment(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    args, tool_call_id = parse_vapi_request(payload)
    
    try:
        appt_id = args.get("appointment_id")
        new_date_str = args.get("new_date")
        new_time_str = args.get("new_time")
        
        if not appt_id or not new_date_str or not new_time_str:
            return vapi_response(tool_call_id, "Please provide the appointment ID, new date, and new time.")
            
        appointment = db.query(Appointment).filter(Appointment.id == int(appt_id)).first()
        if not appointment:
            return vapi_response(tool_call_id, "Sorry, no appointment found with that ID.")
            
        new_time_obj = datetime.strptime(new_time_str, "%H:%M:%S").time() if isinstance(new_time_str, str) else new_time_str
        new_date_obj = datetime.strptime(new_date_str, "%Y-%m-%d").date() if isinstance(new_date_str, str) else new_date_str
            
        clash = crud.get_appointment_by_time(db, new_date_obj, new_time_obj)
        if clash:
            return vapi_response(tool_call_id, "The new time slot is already booked. Please choose another time.")
        
        appointment.date = new_date_obj
        appointment.time = new_time_obj
        appointment.status = "rescheduled"
        db.commit()
        
        return vapi_response(tool_call_id, "Success! The appointment has been rescheduled.")
        
    except Exception as e:
        return vapi_response(tool_call_id, str(e))

@router.post("/cancel", response_model=None)
async def cancel_appointment(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    args, tool_call_id = parse_vapi_request(payload)
    
    try:
        appt_id = args.get("appointment_id")
        if not appt_id:
            return vapi_response(tool_call_id, "Please provide the appointment ID to cancel.")
            
        appointment = db.query(Appointment).filter(Appointment.id == int(appt_id)).first()
        if not appointment:
            return vapi_response(tool_call_id, "Sorry, no appointment found with that ID.")
        
        db.delete(appointment)
        db.commit()
        return vapi_response(tool_call_id, "Success! The appointment has been cancelled.")
        
    except Exception as e:
        return vapi_response(tool_call_id, str(e))