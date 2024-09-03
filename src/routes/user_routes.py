from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models import User, Role, ActionEnum
from src.database import get_db
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from src.utils import create_access_token, get_current_active_admin, get_current_active_user
import logging

# Create a logger
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request and response
class UserCreate(BaseModel):
    name: str
    email: str
    phonenumber: str
    is_admin: bool = False
    address: str = None
    date_of_birth: datetime = None
    role_id: int
    password: str

class UserUpdate(BaseModel):
    name: str
    email: str
    phonenumber: str
    is_admin: bool
    address: str = None
    date_of_birth: datetime = None
    role_id: int

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phonenumber: str
    is_admin: bool
    address: str = None
    date_of_birth: datetime = None
    role_id: int

    class Config:
        orm_mode = True

class RoleCreate(BaseModel):
    role: str
    actions: ActionEnum

class RoleUpdate(BaseModel):
    role: str
    actions: ActionEnum

class RoleResponse(BaseModel):
    id: int
    role: str
    actions: ActionEnum

    class Config:
        orm_mode = True

# CRUD operations for User
@router.post("/users", response_model=UserResponse)
def create_user(user_payload: UserCreate, db: Session = Depends(get_db)):
    user = User(
        name=user_payload.name,
        email=user_payload.email,
        phonenumber=user_payload.phonenumber,
        role_id=user_payload.role_id,
        is_admin=user_payload.is_admin,
        address=user_payload.address,
        date_of_birth=user_payload.date_of_birth
    )
    user.set_password(user_payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token")
def authenticate_user(email: str, password: str, db: Session = Depends(get_db)):
    user = User.authenticate(db, email, password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token_expires = timedelta(hours=1)
    access_token = create_access_token(
        data={"sub": user.id, "role": "admin" if user.is_admin else "app_user"}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_update.dict().items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return user

# CRUD operations for Role
@router.post("/roles", response_model=RoleResponse)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    db_role = Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@router.get("/roles", response_model=List[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    # logger.info(f"CURRENT USER: {current_user}")
    roles = db.query(Role).all()
    return roles

@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, role_update: RoleUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_admin)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    for key, value in role_update.dict().items():
        setattr(role, key, value)
    
    db.commit()
    db.refresh(role)
    return role

@router.delete("/roles/{role_id}", response_model=RoleResponse)
def delete_role(role_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_admin)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    db.delete(role)
    db.commit()
    return role

@router.get("/test/users/me", response_model=UserResponse, dependencies=[Depends(get_current_active_user)])
def read_users_me(current_user: User = Depends(get_current_active_user)):
    logger.info(f"CURRENT USER: {current_user}")
    return current_user

@router.get("/admin", response_model=UserResponse, dependencies=[Depends(get_current_active_user)])
def read_admin_data(current_user: User = Depends(get_current_active_admin)):
    return {"message": "Admin access granted"}

# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInJvbGUiOiJhcHBfdXNlciIsImV4cCI6MTcyNTE4OTQ3OX0.4eH2HmjKjXPlbjT_mLucEkvVVHbeWQUw_Dlgh7g9H8s

"""
curl -X 'GET' \
  'http://0.0.0.0:8000/api/test/users/me' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInJvbGUiOiJhcHBfdXNlciIsImV4cCI6MTcyNTE5NDIwNH0._pqbrXjZfvmr2wloO5esm8NZ8EjxwkiOYiDDw8ZRRK8"

curl -X 'GET' \
  'http://0.0.0.0:8000/api/users' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInJvbGUiOiJhcHBfdXNlciIsImV4cCI6MTcyNTE5NDIwNH0._pqbrXjZfvmr2wloO5esm8NZ8EjxwkiOYiDDw8ZRRK8"
"""