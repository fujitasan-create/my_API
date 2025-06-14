from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal,engine
import models
import secrets
from dotenv import load_dotenv
import os

load_dotenv()

BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")
BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")

security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):

    is_correct_username = secrets.compare_digest(credentials.username, BASIC_AUTH_USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, BASIC_AUTH_PASSWORD)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証に失敗しました",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

models.Base.metadata.create_all(bind=engine)
app= FastAPI()

origins = [
    "https://fujitasan-create.github.io",  
    "http://localhost:3000",                
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ContactCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    message: str

router = APIRouter()

@router.get("/")
def root():
    return {"message": "I'm alive!"}

@router.post("/contact")
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return {"message": "お問い合わせを受け付けました"}

@router.get("/contacts")
def read_contacts(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username)
):
    contacts = db.query(models.Contact).all()
    return contacts