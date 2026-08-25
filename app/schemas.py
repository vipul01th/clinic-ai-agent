from pydantic import BaseModel
from datetime import date, time
from typing import Optional

# ---- Patient Schemas ----
class PatientCreate(BaseModel):
    name: str
    phone: str

class PatientResponse(PatientCreate):
    id: int
    
    class Config:
        from_attributes = True

# ---- Appointment Schemas ----
class AppointmentCreate(BaseModel):
    patient_id: int
    date: date
    time: time

class AppointmentReschedule(BaseModel):
    date: date
    time: time
    status: str = "rescheduled"

class AppointmentResponse(AppointmentCreate):
    id: int
    status: str
    
    class Config:
        from_attributes = True