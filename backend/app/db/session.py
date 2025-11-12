# backend/app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

db_url = settings.DATABASE_URL or ""
if not db_url:
    raise RuntimeError("DATABASE_URL is not set in environment (app/core/config.py)")

# convert old Heroku-style prefix if needed
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

# ensure the URL uses the asyncpg dialect
if not db_url.startswith("postgresql+asyncpg://"):
    # optionally: log or raise — here we just try to be helpful
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(db_url, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
