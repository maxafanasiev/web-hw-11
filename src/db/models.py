from datetime import date

from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

from src.utils.phone_number import PhoneNumber
from src.db.db_connect import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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
