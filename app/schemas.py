from pydantic import BaseModel, ConfigDict
from datetime import date, time

class PatientCreate(BaseModel):
    name: str
    phone: str

class PatientResponse(BaseModel):
    id: int
    name: str
    phone: str

    # Pydantic V2 ka naya tarika
    model_config = ConfigDict(from_attributes=True)

class AppointmentCreate(BaseModel):
    patient_id: int
    appt_date: date
    appt_time: time

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    date: date
    time: time
    status: str

    # Pydantic V2 ka naya tarika
    model_config = ConfigDict(from_attributes=True)

class AvailabilityResponse(BaseModel):
    available: bool
    message: str