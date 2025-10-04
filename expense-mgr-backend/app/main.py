from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base
from .routers import auth, expenses, approvals, users
import os

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ExpensoMan API",
    description="Backend for the Expense Management System.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://stellular-cactus-2a9ff5.netlify.app/"],  # TODO: restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
app.include_router(approvals.router, prefix="/approvals", tags=["Approvals"])

# Static frontend serving
static_file_path = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/static", StaticFiles(directory=static_file_path), name="static")

# Root → index.html
@app.get("/", response_class=FileResponse, tags=["Root"])
async def read_index():
    return FileResponse(os.path.join(static_file_path, "index.html"))

# Catch-all → index.html (for React Router)
@app.get("/{full_path:path}", response_class=FileResponse, tags=["Root"])
async def catch_all(full_path: str, request: Request):
    index_path = os.path.join(static_file_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Not found"}
