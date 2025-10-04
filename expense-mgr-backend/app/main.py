from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import ORJSONResponse
from .database import Base, engine
from .config import settings
from . import deps, utils
from .routers import (
    auth as auth_router,
    users as users_router,
    expenses as expenses_router,
    approvals as approvals_router,
    admin as admin_router,
    currency as currency_router,
)
from .services.analytics import generate_analytics
from .services.currency_service import init_http_clients, close_http_clients, warm_caches
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Expense Management System",
    description="Backend API for Expense Management with multi-level approvals and AI insights",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable gzip compression for large responses
app.add_middleware(GZipMiddleware, minimum_size=512)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    # Initialize HTTP clients and warm caches
    await init_http_clients()
    await warm_caches()

    # In development, auto-create tables for convenience; avoid in production for faster startup
    if settings.DEBUG:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables ensured (development mode)")

@app.on_event("shutdown")
async def shutdown_event():
    await close_http_clients()
    logger.info("Application shutting down")

@app.get("/analytics", dependencies=[Depends(deps.is_admin)])
async def get_analytics():
    return await generate_analytics()

app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(users_router.router, prefix="/users", tags=["Users"])
app.include_router(expenses_router.router, prefix="/expenses", tags=["Expenses"])
app.include_router(approvals_router.router, prefix="/approvals", tags=["Approvals"])
app.include_router(admin_router.router, prefix="/admin", tags=["Admin"])
app.include_router(currency_router.router, prefix="/currency", tags=["Currency"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Expense Management System. Visit /static/index.html", "time": utils.get_current_datetime().isoformat()}