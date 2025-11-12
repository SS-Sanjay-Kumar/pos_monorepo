# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from app.core.config import settings

# engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
# AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# # dependency
# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session

# backend/app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
# No need to import asyncmy anymore

# The DATABASE_URL from Render will start with "postgres://"
# We change it to "postgresql+asyncpg://" for SQLAlchemy
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(db_url, pool_pre_ping=True)

# Create a configured "AsyncSession" class
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

# Dependency to get a DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session