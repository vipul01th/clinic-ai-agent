from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, time
from app import crud, schemas
from app.database.connection import get_db
from app.auth import get_current_admin
from app.models import Appointment

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("", response_model=schemas.AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(request: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    # Direct DB check hatakar CRUD ka use kiya
    existing_appointment = crud.get_appointment_by_time(db, request.appt_date, request.appt_time)
    
    if existing_appointment:
        raise HTTPException(status_code=400, detail="This time slot is already booked")
        
    return crud.create_appointment(db, request)

@router.get("/check-availability", response_model=schemas.AvailabilityResponse)
def check_availability(check_date: date, check_time: time, db: Session = Depends(get_db)):
    # Direct DB check hatakar CRUD ka use kiya
    existing = crud.get_appointment_by_time(db, check_date, check_time)
    
    if existing:
        return schemas.AvailabilityResponse(available=False, message="Time slot is already taken")
    return schemas.AvailabilityResponse(available=True, message="Time slot is free")

@router.put("/reschedule/{appointment_id}")
def reschedule_appointment(appointment_id: int, new_date: date, new_time: time, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    # Reschedule mein bhi double booking rokne ke liye CRUD lagaya
    clash_appointment = crud.get_appointment_by_time(db, new_date, new_time)
    
    if clash_appointment:
        raise HTTPException(status_code=400, detail="The new time slot is already booked")
    
    appointment.date = new_date
    appointment.time = new_time
    appointment.status = "rescheduled"
    db.commit()
    db.refresh(appointment)
    return {"message": "Appointment rescheduled successfully", "appointment": appointment}

@router.delete("/cancel/{appointment_id}")
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db.delete(appointment)
    db.commit()
    return {"message": "Appointment cancelled successfully"}