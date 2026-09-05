import logging
from fastapi import FastAPI, Request
from app.database.connection import engine
from app import models 
from app.routers import appointments, auth
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(
    filename="clinic_api.log",  # Is file mein saare errors save honge
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

app = FastAPI(
    title="Clinic AI Voice Agent"
)

app.include_router(appointments.router)
app.include_router(auth.router)

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


@app.exception_handler(SQLAlchemyError)
def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database Error on {request.url}: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={"message": "An internal database error occurred. Please try again later."}
    )

logger.info("Clinic Appointment API Server Started Successfully!")