from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException  # noqa: F401
from sqlalchemy.orm import Session
from src.models import Form, User  # noqa: F401
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Boolean, Float, Text, insert, select, update  # noqa: F401
from src.database import get_db
from pydantic import BaseModel  # noqa: F401
from typing import List  # noqa: F401
import logging
from src.utils import get_current_active_admin, get_current_active_user

# Create a logger
logger = logging.getLogger(__name__)

router = APIRouter()

class DataEntryCreate(BaseModel):
    data: dict

class DataEntryApprove(BaseModel):
    user_id: int


@router.post("/data/{table_name}/insert")
def insert_form_record(table_name: str, insert_data: DataEntryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    insert_data = insert_data.data
    insert_data.update({
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'created_by': current_user.id,
        'updated_by': current_user.id,
        "approved_status": "PENDING"
        })
    logger.info(f"UPDATED PAYLOAD: {insert_data}")
    return insert_into_dynamic_table(table_name, insert_data, db)


@router.put("/data/{table_name}/{record_id}")
def update_form_record(table_name: str, record_id: int, update_data: DataEntryCreate, db: Session = Depends(get_db)):
    return update_dynamic_table(table_name, record_id, update_data.data, db)

# Retrieve data from a dynamic table
@router.get("/data/{table_name}")
def get_all_data(table_name: str, db: Session = Depends(get_db)):
    data = get_data_from_dynamic_table(table_name, db)
    logger.info(f"DATA: {data}")
    return data


@router.get("/data/{table_name}/{record_id}")
def get_data(table_name: str, record_id:int, db: Session = Depends(get_db)):
    logger.info(f"GETTING DATA FROM FORM {table_name} | DATA ID: {record_id}")
    return get_record_from_dynamic_table(table_name, record_id, db)


@router.post("/data/{table_name}/{record_id}/approve")
def approve_data(approval_payload: DataEntryApprove, table_name: str, record_id:int, db: Session = Depends(get_db)):
    logger.info(f"APPROVING DATA FROM TABLE {table_name} | RECORD ID: {record_id} | APPROVED BY: {approval_payload}")
    approved_by = approval_payload.user_id
    user = db.query(User).filter(User.id == approved_by).first()

    record = get_record_from_dynamic_table(table_name, record_id, db)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    if record["approved_status"] == "APPROVED":
        raise HTTPException(status_code=400, detail="Record already approved")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = user.role

    if role.actions.value not in ("UPDATE_APPROVE", "SIGNOFF"):
        raise HTTPException(status_code=401, detail="User not authorized to approve data")
    
    update_payload = {
        "approved_status": "APPROVED" if role.actions.value == "SIGNOFF" else "IN_PROGRESS",
        "last_approved_by": approval_payload.user_id,
        "last_approved_at": datetime.now(),
        "updated_at": datetime.now(),
        "updated_by": approval_payload.user_id
    }
    logger.info(f"UPDATE PAYLOAD: {update_payload}")

    return update_dynamic_table(table_name, record_id, update_payload, db)


@router.post("/data/{table_name}/{record_id}/delete")
def delete_data(table_name: str, record_id:int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_admin)):
    logger.info(f"DELETING DATA FROM FORM {table_name} | DATA ID: {record_id}")

    return {"message": "Data deleted successfully"}


def get_dynamic_table(table_name, db):
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=db.get_bind())
    return table


def get_record_from_dynamic_table(table_name: str, record_id:int, db: Session):
    """
    Retrieve data from a dynamic table.
    """
    metadata = MetaData()
    metadata.reflect(bind=db.get_bind())
    table = Table(table_name, metadata, autoload_with=db.get_bind())
    
    stmt = select(table).where(table.c.id == record_id)
    result = db.execute(stmt)
    data = result.fetchone()
    
    if data is None:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return data._asdict()


def get_data_from_dynamic_table(table_name: str, db: Session):
    """
    Retrieve data from a dynamic table.
    """
    metadata = MetaData()
    metadata.reflect(bind=db.get_bind())
    table = Table(table_name, metadata, autoload_with=db.get_bind())
    
    stmt = select(table)
    result = db.execute(stmt)
    data = result.fetchall()
    
    # Convert the result to a list of dictionaries
    data_dicts = [row._asdict() for row in data]
    
    return data_dicts


def insert_into_dynamic_table(table_name, insert_data, db: Session):
    """
    Insert data into a dynamic table.
    """
    metadata = MetaData()
    metadata.reflect(bind=db.get_bind())
    table = Table(table_name, metadata, autoload_with=db.get_bind())
    
    stmt = insert(table).values(**insert_data)

    result = db.execute(stmt)
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=400, detail="Insert failed")
    
    return {"message": f"{result.rowcount} records inserted successfully"}


def update_dynamic_table(table_name, primary_key, update_data, db: Session):
    """
    Update data in a dynamic table.
    """
    metadata = MetaData()
    metadata.reflect(bind=db.get_bind())
    table = Table(table_name, metadata, autoload_with=db.get_bind())
    
    stmt = (
        update(table).
        where(table.c.id == primary_key).
        values(**update_data)
    )
    
    result = db.execute(stmt)
    db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {"message": "Record updated successfully"}