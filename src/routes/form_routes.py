from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models import Form
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Enum as SqlEnum
from src.database import get_db
from pydantic import BaseModel
from typing import List
import logging
from datetime import datetime
from enum import Enum

class ApprovedStatusEnum(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"

# Create a logger
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request and response
class FormCreate(BaseModel):
    table_name: str
    fields: dict
    created_by: int
    desciption: str = ""

class FormUpdate(BaseModel):
    table_name: str
    fields: dict

class FormResponse(BaseModel):
    id: int
    name: str
    fields: dict
    created_by: int
    description: str = ""

    class Config:
        orm_mode = True


# Define a mapping from string representation to SQLAlchemy column types
type_mapping = {
    'Integer': Integer,
    'String': String,
    'DateTime': DateTime,
    'Boolean': Boolean,
    'Float': Float,
    'Text': Text
}


# Read all forms
@router.get("/forms", response_model=List[FormResponse])
def get_forms(db: Session = Depends(get_db)):
    forms = db.query(Form).all()
    return forms

# Read a single form by ID
@router.get("/forms/{form_id}", response_model=FormResponse)
def get_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    _ = create_table_from_form(form, db)
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    return form

# Update a form by ID
@router.put("/forms/{form_id}", response_model=FormResponse)
def update_form(form_id: int, form_update: FormUpdate, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    
    form.name = form_update.table_name
    form.fields = form_update.fields
    db.commit()
    db.refresh(form)
    return form

# Delete a form by ID
@router.delete("/forms/{form_id}", response_model=FormResponse)
def delete_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    
    db.delete(form)
    db.commit()
    return form


# Create a form
@router.post("/forms", response_model=FormResponse)
def create_form(form: FormCreate, db: Session = Depends(get_db)):
    db_form = Form(name=form.table_name, fields=form.fields, created_by=form.created_by, description=form.desciption)
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    table = create_table_from_form(db_form, db)
    logger.info(f"TABLE CREATED - {table}")
    return db_form


def create_table_from_form(form, db):
    """
    Create a dynamic table from the form definition and add additional fields.
    """
    metadata = MetaData()

    # Ensure referenced tables exist
    users_table = Table('users', metadata, autoload_with=db.get_bind())  # noqa: F841
    roles_table = Table('roles', metadata, autoload_with=db.get_bind())  # noqa: F841

    columns = [
        Column('id', Integer, primary_key=True, autoincrement=True)  # Add auto-incremented primary key
    ]
    # {"name":"arpit1","age":24,"bool":false}

    for field_name, field_type in form.fields.items():
        column_type = type_mapping.get(field_type)
        if column_type:
            columns.append(Column(field_name, column_type))
    
    # Add the additional fields
    columns.extend([
        Column('approved_status', SqlEnum(ApprovedStatusEnum), default="PENDING"),
        Column('last_approved_by', Integer, ForeignKey('users.id'), nullable=True),
        Column('last_approved_by_role', Integer, ForeignKey('roles.id'), nullable=True),
        Column('last_approved_at', DateTime, nullable=True),
        Column('created_at', DateTime, nullable=False, default=datetime.now),
        Column('updated_at', DateTime, nullable=False, default=datetime.now, onupdate=datetime.now),
        Column('created_by', Integer, ForeignKey('users.id'), nullable=True),
        Column('updated_by', Integer, ForeignKey('users.id'), nullable=True)
    ])
    
    table = Table(form.name, metadata, *columns)
    metadata.create_all(db.get_bind())
    return table
