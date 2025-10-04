from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .routers import auth_router, users_router, expenses_router, approvals_router, admin_router, currency_router
from .services.analytics import generate_analytics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Expense Management System",
    description="Backend API for Expense Management with multi-level approvals and AI insights",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

@app.on_event("shutdown")
async def shutdown_event():
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