from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import LoginRequest, Token
from app.db.models import UserAccount
from sqlalchemy import select
from app.auth import verify_password, create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(form: LoginRequest, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(UserAccount).where(UserAccount.email == form.email))
    user = q.scalar_one_or_none()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token(str(user.id), roles=str(user.role_id))
    refresh = create_refresh_token(str(user.id))
    # In production: store hashed refresh in DB and rotate
    return {"access_token": access, "token_type": "bearer", "refresh_token": refresh}
