from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenPayload(BaseModel):
    sub: str
    roles: Optional[str]
    exp: int

