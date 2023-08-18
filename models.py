from datetime import date
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

from phone_number import PhoneNumber

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:password2023@localhost:5432/fastapi"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


class ContactRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date

    @field_validator("phone_number")
    def validate_phone_number(cls, v):
        if not PhoneNumber.is_valid_phone_number(v):
            raise ValueError("Invalid phone number")
        return v


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, index=True)
    phone_number = Column(String, unique=True, index=True)
    birthday = Column(TIMESTAMP)
