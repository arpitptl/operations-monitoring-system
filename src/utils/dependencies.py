from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from .jwt_utils import SECRET_KEY, ALGORITHM
from src.models import User
from src.database import get_db
from sqlalchemy.orm import Session
import logging

# Create a logger
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"PAYLOAD: {payload}")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user:
        return current_user
    raise HTTPException(status_code=400, detail="Inactive user")

def get_current_active_admin(current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        return current_user
    raise HTTPException(status_code=403, detail="Not enough permissions")