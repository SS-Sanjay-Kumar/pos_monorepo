from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings, ACCESS_TOKEN_EXPIRE, REFRESH_TOKEN_EXPIRE
from argon2 import PasswordHasher
from typing import Optional
from sqlalchemy import select
from app.db.models import UserAccount, RefreshToken
from app.db.session import AsyncSessionLocal

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hash_: str) -> bool:
    try:
        return ph.verify(hash_, password)
    except Exception:
        return False

def create_access_token(subject: str, roles: Optional[str] = None):
    to_encode = {"sub": str(subject)}
    if roles:
        to_encode["roles"] = roles
    expire = datetime.utcnow() + ACCESS_TOKEN_EXPIRE
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# NOTE: for refresh tokens we recommend storing hashed tokens in DB and rotating them.
# This is a minimal example — extend in production to store hashed refresh tokens and rotation.
def create_refresh_token(subject: str):
    expire = datetime.utcnow() + REFRESH_TOKEN_EXPIRE
    to_encode = {"sub": str(subject), "exp": expire}
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token
