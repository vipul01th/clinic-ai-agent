from sqlalchemy.orm import Session
from app import models, schemas
from datetime import date, time

def get_patient_by_phone(db: Session, phone: str):
    return db.query(models.Patient).filter(models.Patient.phone == phone).first()

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(name=patient.name, phone=patient.phone)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def get_appointment_by_time(db: Session, appt_date: date, appt_time: time):
    return db.query(models.Appointment).filter(
        models.Appointment.date == appt_date,
        models.Appointment.time == appt_time,
        models.Appointment.status.in_(["booked", "rescheduled"])
    ).first()

def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    db_appointment = models.Appointment(
        patient_id=appointment.patient_id,
        date=appointment.appt_date,
        time=appointment.appt_time,
        status="booked"
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_appointments_by_date(db: Session, appointment_date: date):
    return db.query(models.Appointment).filter(
        models.Appointment.date == appointment_date,
        models.Appointment.status == "booked"
    ).all()

def update_appointment_status(db: Session, appointment_id: int, new_status: str):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment:
        db_appointment.status = new_status
        db.commit()
        db.refresh(db_appointment)
    return db_appointment