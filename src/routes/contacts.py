from typing import List
from datetime import datetime, timedelta

from fastapi import HTTPException, Depends, Query,APIRouter, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.db.models import Contact, ContactRequest, ContactResponse
from src.db.db_connect import get_db


router = APIRouter(prefix="/contacts", tags=['contacts'])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactRequest, db: Session = Depends(get_db)):
    if db.query(Contact).filter_by(phone_number=contact.phone_number).first():
        raise HTTPException(status_code=400, detail="Phone number already exists")

    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    contacts = db.query(Contact).offset(skip).limit(limit).all()
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, updated_contact: ContactRequest, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    for attr, value in updated_contact.model_dump().items():
        setattr(contact, attr, value)

    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return contact


@router.get("/", response_model=List[ContactResponse])
async def search_contacts(
        q: str = Query(..., description="Search query for name, last name, or email"),
        skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    contacts = db.query(Contact).filter(
        Contact.first_name.ilike(f"%{q}%")
        | Contact.last_name.ilike(f"%{q}%")
        | Contact.email.ilike(f"%{q}%")
    ).offset(skip).limit(limit).all()
    return contacts


@router.get("/birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(db: Session = Depends(get_db)):
    today = datetime.today()
    seven_days_later = today + timedelta(days=7)

    upcoming_birthdays_this_year = db.query(Contact).filter(
        text("TO_CHAR(birthday, 'MM-DD') BETWEEN :start_date AND :end_date")
    ).params(start_date=today.strftime('%m-%d'), end_date=seven_days_later.strftime('%m-%d')).all()

    return upcoming_birthdays_this_year
