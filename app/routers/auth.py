from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models import Admin
from app.auth import verify_password, get_password_hash, create_access_token

router = APIRouter(tags=["Authentication"])

@router.post("/create-admin")
def create_admin(username: str, password: str, db: Session = Depends(get_db)):
    existing_admin = db.query(Admin).filter(Admin.username == username).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin pehle se maujood hai")
    
    hashed_password = get_password_hash(password)
    new_admin = Admin(username=username, hashed_password=hashed_password)
    db.add(new_admin)
    db.commit()
    return {"message": "Admin successfully ban gaya!"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == form_data.username).first()
    if not admin:
        raise HTTPException(status_code=401, detail="Galat username ya password")
    
    if not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="Galat username ya password")
    
    access_token = create_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}