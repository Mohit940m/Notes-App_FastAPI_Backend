from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from bson import ObjectId
from app.utils.jwt_handler import oauth2_scheme, decode_access_token
from passlib.context import CryptContext

from app.core.config import settings
from app.models.user_models import UserLogin
from app.core.database import db
 

# ---------------- Password hashing ----------------
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str) -> str:
#     """Hash plain password using bcrypt"""
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verify plain password against hashed password"""
#     return pwd_context.verify(plain_password, hashed_password)


# ---------------- JWT handling ----------------
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# def create_access_token(data: dict, expires_delta: Optional[int] = 60):
#     """Create JWT access token"""
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=expires_delta)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

# def decode_access_token(token: str):
#     """Decode JWT and return payload"""
#     try:
#         payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
#         return payload
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )


# ---------------- User Dependency ----------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
async def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")  # we put user_id in "sub" at login
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        # Convert user_id string to ObjectId for the query
    user = await db.get_collection("users").find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
