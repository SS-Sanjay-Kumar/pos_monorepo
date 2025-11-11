from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
import asyncio
from sqlalchemy.exc import SQLAlchemyError
from app.db import models
from app.db.session import engine
from app.api import auth as auth_router
from app.api import products as products_router
from app.api import employees as employees_router
from app.api import invoices as invoices_router
from app.api import payments as payments_router
from app.api import tax_slabs as tax_slabs_router

from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

app = FastAPI(title="Hotel Billing API (dev)")


# For local dev use this set — restrict to your live-server origin if you prefer:
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    # Vite React dev server (for local frontend)
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # set to ["*"] to allow all origins (dev only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# include routers (these imports must exist)
app.include_router(auth_router.router)
app.include_router(products_router.router)
app.include_router(employees_router.router)
app.include_router(invoices_router.router)
app.include_router(payments_router.router)
app.include_router(tax_slabs_router.router)

@app.get("/health", tags=["health"])
async def health():
    return JSONResponse({"status": "ok"})

@app.on_event("startup")
async def on_startup():
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)

    try:
        await asyncio.wait_for(create_tables(), timeout=6.0)
        logger.info("DB tables ensured")
    except asyncio.TimeoutError:
        logger.error("Timeout creating DB tables (continuing without blocking)")
    except SQLAlchemyError as e:
        logger.exception("SQLAlchemy error during startup: %s", e)
    except Exception as e:
        logger.exception("Unexpected error during startup: %s", e)
