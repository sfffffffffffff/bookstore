from fastapi import Depends, HTTPException, status  
from fastapi.security import OAuth2PasswordBearer  
from sqlalchemy.orm import Session  
from sqlalchemy import text  
from datetime import datetime, timedelta  
import jwt  
from typing import Optional  
from db import get_db  

# JWT configuration  
SECRET_KEY = "your-secret-key"  # Use environment variables in production  
ALGORITHM = "HS256"  
ACCESS_TOKEN_EXPIRE_MINUTES = 30  

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):  
    """Create a JWT token."""  
    to_encode = data.copy()  
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))  
    to_encode.update({"exp": expire})  
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):  
    """Validate token and retrieve the user."""  
    credentials_exception = HTTPException(  
        status_code=status.HTTP_401_UNAUTHORIZED,  
        detail="Could not validate credentials",  
        headers={"WWW-Authenticate": "Bearer"},  
    )  
    try:  
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
        user_id: str = payload.get("sub")  
        if user_id is None:  
            raise credentials_exception  
    except jwt.JWTError:  
        raise credentials_exception  

    sql = text("SELECT * FROM participants WHERE id = :user_id")  
    user = db.execute(sql, {"user_id": user_id}).fetchone()  
    
    if user is None:  
        raise credentials_exception  
        
    return user  

async def get_current_admin(current_user = Depends(get_current_user)):  
    """Check if the current user is an administrator."""  
    if current_user.type != "administrator":  
        raise HTTPException(  
            status_code=status.HTTP_403_FORBIDDEN,  
            detail="The user doesn't have admin privileges"  
        )  
    return current_user  

async def get_current_store(current_user = Depends(get_current_user)):  
    """Check if the current user is a store."""  
    if current_user.type != "store":  
        raise HTTPException(  
            status_code=status.HTTP_403_FORBIDDEN,  
            detail="The user doesn't have store privileges"  
        )  
    return current_user  

async def get_current_buyer(current_user = Depends(get_current_user)):  
    """Check if the current user is a buyer."""  
    if current_user.type != "buyer":  
        raise HTTPException(  
            status_code=status.HTTP_403_FORBIDDEN,  
            detail="The user doesn't have buyer privileges"  
        )  
    return current_user  

async def verify_user_access(user_id: int, current_user = Depends(get_current_user)):  
    """Verify if the user has access to the specified user ID's resources."""  
    if current_user.id != user_id and current_user.type != "administrator":  
        raise HTTPException(  
            status_code=status.HTTP_403_FORBIDDEN,  
            detail="Not authorized to access this resource"  
        )  
    return current_user  

async def verify_store_access(store_id: int, current_user = Depends(get_current_user)):  
    """Verify if the user has access to the specified store's resources."""  
    if current_user.id != store_id and current_user.type != "administrator":  
        raise HTTPException(  
            status_code=status.HTTP_403_FORBIDDEN,  
            detail="Not authorized to access this store's resources"  
        )  
    return current_user