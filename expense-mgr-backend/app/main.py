from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth_router, users_router, expenses_router, approvals_router, admin_router

# Create all database tables
Base.metadata.create_all(bind=engine)

# FastAPI app instance
app = FastAPI(
    title="Expense Management System",
    description="Backend API for Expense Management with multi-level approvals",
    version="1.0.0"
)

# Allow CORS (frontend can call APIs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(users_router.router, prefix="/users", tags=["Users"])
app.include_router(expenses_router.router, prefix="/expenses", tags=["Expenses"])
app.include_router(approvals_router.router, prefix="/approvals", tags=["Approvals"])
app.include_router(admin_router.router, prefix="/admin", tags=["Admin"])

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Expense Management System API"}