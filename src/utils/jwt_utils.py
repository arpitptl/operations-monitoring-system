import jwt
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from functools import wraps
from typing import Callable
import logging
SECRET_KEY = "AJNSH^$#1@0LP7"
ALGORITHM = "HS256"

# Create a logger
logger = logging.getLogger(__name__)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def requires_auth(func: Callable):
    @wraps(func)
    async def decorated_function(request: Request, *args, **kwargs):
       
        logger.info(f"DECORATOR ARGS: {args} | KWARGS: {kwargs}")
        # request: Request = kwargs.get('request')
        # if request is None:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Request object is required"
        #     )
        # Get the Authorization header
        logger.info(f"HEADERS: {request.headers}") 
        auth_header = request.headers.get("Authorization")
        if auth_header is None or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing or invalid"
            )
        
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            logger.info(f"PAYLOAD: {payload}")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token payload invalid"
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid"
            )
        
        return await func(*args, **kwargs)
    
    return decorated_function