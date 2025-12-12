from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt  # <--- using PyJWT instead of jose
from bson.objectid import ObjectId
from app.core.config import settings
from app.database.connection import db_manager

# This tells FastAPI that the token comes from the "/admin/login" url
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the token using PyJWT
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError: # Catch PyJWT specific errors
        raise credentials_exception

    # Check if user actually exists in DB
    # We use ObjectId to find the user by the ID stored in the token
    user = db_manager.get_database()["users"].find_one({"_id": ObjectId(user_id)})
    
    if user is None:
        raise credentials_exception
        
    return user