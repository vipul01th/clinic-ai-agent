from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, time
from pydantic import BaseModel
from app import crud, schemas, models
from app.database.connection import get_db

router = APIRouter(prefix="/appointments", tags=["Appointments"])

class BookingRequest(BaseModel):
    name: str
    phone: str
    date: date
    time: time

@router.post("/book")
def book_appointment(request: BookingRequest, db: Session = Depends(get_db)):
    """Book a new appointment (creates patient if not exists)"""
    patient = crud.get_patient_by_phone(db, phone=request.phone)
    
    if not patient:
        patient_data = schemas.PatientCreate(name=request.name, phone=request.phone)
        patient = crud.create_patient(db, patient_data)
    
    # 2. Appointment create karein
    appointment_data = schemas.AppointmentCreate(
        patient_id=patient.id, 
        date=request.date, 
        time=request.time
    )
    appointment = crud.create_appointment(db, appointment_data)
    
    return {
        "status": "success", 
        "message": f"Appointment booked for {request.name} on {request.date} at {request.time}",
        "appointment_id": appointment.id
    }

@router.get("/check-availability")
def check_availability(check_date: date, db: Session = Depends(get_db)):
    """Check how many slots are already booked for a specific date"""
    booked_appointments = crud.get_appointments_by_date(db, appointment_date=check_date)
    
    booked_times = [app.time.strftime("%H:%M") for app in booked_appointments]
    
    return {
        "date": check_date,
        "booked_slots": booked_times,
        "message": f"There are {len(booked_times)} appointments booked on this date."
    }

@router.put("/reschedule/{appointment_id}")
def reschedule_appointment(appointment_id: int, new_date: date, new_time: time, db: Session = Depends(get_db)):
    """Reschedule an existing appointment"""
    # Find the appointment
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update details
    appointment.date = new_date
    appointment.time = new_time
    appointment.status = "rescheduled"
    
    db.commit()
    db.refresh(appointment)
    
    return {
        "status": "success",
        "message": f"Appointment {appointment_id} rescheduled to {new_date} at {new_time}",
        "appointment": {
            "id": appointment.id, 
            "date": appointment.date, 
            "time": appointment.time, 
            "status": appointment.status
        }
    }

@router.delete("/cancel/{appointment_id}")
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Cancel an appointment (Updates status to cancelled)"""
    appointment = crud.update_appointment_status(db, appointment_id=appointment_id, new_status="cancelled")
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    return {
        "status": "success",
        "message": f"Appointment {appointment_id} has been cancelled successfully."
    }