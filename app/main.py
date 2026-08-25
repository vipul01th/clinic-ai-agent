from fastapi import FastAPI
from app.database.connection import engine
from app import models  # Models import karein
from app.routers import appointments

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Clinic AI Voice Agent"
)

app.include_router(appointments.router)

@app.get("/")
def root():
    return {
        "message": "Clinic AI Agent API is running"
    }

@app.get("/db-test")
def database_test():
    try:
        with engine.connect() as connection:
            return {
                "status": "success",
                "message": "PostgreSQL connected successfully"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }