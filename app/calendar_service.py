import os
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Configuration Settings
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'  # Root folder mein rakhi hui file
CALENDAR_ID = os.getenv("CALENDAR_ID")

def get_calendar_service():
    """Authenticate aur Google Calendar service return karein"""
    if not CALENDAR_ID:
        raise ValueError("CALENDAR_ID is missing in .env file")
        
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    return service

def create_calendar_event(patient_name: str, patient_phone: str, appointment_date, appointment_time):
    """Naya appointment aate hi Google Calendar mein event banayein"""
    try:
        service = get_calendar_service()
        
        # Date aur Time ko combine karke event ka Start Time banana
        start_datetime = datetime.combine(appointment_date, appointment_time)
        
        # Maan lete hain ki har appointment 30 minutes ka hoga
        end_datetime = start_datetime + timedelta(minutes=30)
        
        # Calendar Event ka format
        event = {
            'summary': f'Clinic Booking: {patient_name}',
            'description': f'Patient Phone: {patient_phone}\nAutomated booking by AI Agent.',
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata',  # IST (Indian Standard Time)
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'colorId': '5',  # Yellow color for AI bookings
        }
        
        # API Call to insert event
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return created_event.get('htmlLink')  # Event ka web link return karega
        
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return None