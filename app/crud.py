from sqlalchemy.orm import Session
from app import models, schemas
from datetime import date

# ==========================================
# PATIENT OPERATIONS
# ==========================================

def get_patient_by_phone(db: Session, phone: str):
    """Check if patient already exists using their phone number"""
    return db.query(models.Patient).filter(models.Patient.phone == phone).first()

def create_patient(db: Session, patient: schemas.PatientCreate):
    """Create a new patient in the database"""
    db_patient = models.Patient(name=patient.name, phone=patient.phone)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


# ==========================================
# APPOINTMENT OPERATIONS
# ==========================================

def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    """Book a new appointment"""
    db_appointment = models.Appointment(
        patient_id=appointment.patient_id,
        date=appointment.date,
        time=appointment.time,
        status="booked"
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_appointments_by_date(db: Session, appointment_date: date):
    """Get all booked appointments for a specific date (Helps in checking availability)"""
    return db.query(models.Appointment).filter(
        models.Appointment.date == appointment_date,
        models.Appointment.status == "booked"
    ).all()

def update_appointment_status(db: Session, appointment_id: int, new_status: str):
    """Update appointment status (e.g., to 'cancelled' or 'rescheduled')"""
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment:
        db_appointment.status = new_status
        db.commit()
        db.refresh(db_appointment)
    return db_appointment
