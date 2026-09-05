from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_check_availability_format():
    response = client.get("/appointments/check-availability?check_date=2026-09-01&check_time=10:30:00")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "available" in data

def test_prevent_double_booking():
    test_data = {
        "patient_id": 1,
        "appt_date": "2026-12-31",
        "appt_time": "14:00:00"
    }
    
    client.post("/appointments", json=test_data)
    
    response = client.post("/appointments", json=test_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "This time slot is already booked"