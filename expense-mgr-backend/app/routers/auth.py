from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import Token, PasswordResetRequest, PasswordReset, User as UserSchema
from app.crud import get_user_by_username, create_company, create_user, update_user_reset_token, update_user_password
from app.auth import get_password_hash, create_access_token, authenticate_user, create_reset_token, verify_reset_token, send_email, generate_random_password, get_current_user
from app.database import get_db  # <-- FIXED: Import get_db from database, not deps
from app.models import User, Role
from datetime import datetime

router = APIRouter()

@router.post("/signup", response_model=UserSchema)
async def signup(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    country: str = "United States"
):
    user = await get_user_by_username(db, form_data.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    currency = "USD"  # Placeholder
    company = await create_company(db, {"name": f"{form_data.username}'s Company", "currency": currency})
    hashed_password = get_password_hash(form_data.password)
    new_user = await create_user(db, {
        "username": form_data.username,
        "email": f"{form_data.username}@example.com",
        "mobile_number": None,
        "hashed_password": hashed_password,
        "role": Role.EMPLOYEE,
        "company_id": company.id
    })
    access_token = create_access_token({"sub": new_user.username})
    return new_user

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})
    
    # NOTE: Your email logic has been moved to the main App controller
    # This keeps the API response fast.
    
    return {"access_token": access_token, "token_type": "bearer"}

# ... (the rest of your router file for forgot-password, etc.) ...

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# (You can add your other endpoints like /forgot-password back in here)