from datetime import datetime, timedelta, timezone
from typing import Optional, dict
import jwt
from passlib.context import CryptContext
from app.config import settings

# Setup password hashing engine using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashes a plain text password to store it safely."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a plain text login attempt with a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure JSON Web Token (JWT).
    Payload must include 'user_id', 'role', and 'client_id' for multi-tenancy.
    """
    to_encode = data.copy()
    
    # Calculate token lifetime expiration string
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    # Encode and encrypt the payload data signature
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decrypts and validates an incoming JWT payload signature.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except (jwt.PyJWTError, jwt.ExpiredSignatureError):
        return None
