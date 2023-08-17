# main.py
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from models import Contact, ContactModel, ContactResponse, get_db
from typing import List
from datetime import datetime, timedelta

app = FastAPI()


@app.post("/contacts/", response_model=ContactResponse)
async def create_contact(contact: ContactModel, db: Session = Depends(get_db)):
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@app.get("/contacts/", response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    contacts = db.query(Contact).offset(skip).limit(limit).all()
    return contacts


@app.get("/contacts/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@app.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, updated_contact: ContactModel, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    for attr, value in updated_contact.dict().items():
        setattr(contact, attr, value)

    db.commit()
    db.refresh(contact)
    return contact


@app.delete("/contacts/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return contact


@app.get("/contacts/", response_model=List[ContactResponse])
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


@app.get("/contacts/birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(db: Session = Depends(get_db)):
    today = datetime.today()
    current_year = today.year
    seven_days_later = today + timedelta(days=7)

    contacts = db.query(Contact).all()

    upcoming_birthdays_this_year = [
        contact for contact in contacts
        if (contact.birthday.replace(year=current_year) >= today) and
           (contact.birthday.replace(year=current_year) <= seven_days_later)
    ]

    return upcoming_birthdays_this_year
