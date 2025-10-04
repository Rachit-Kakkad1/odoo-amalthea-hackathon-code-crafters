# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import Token
from app.crud import get_user_by_username, create_company, create_user
from app.auth import get_password_hash, create_access_token, authenticate_user
from app.deps import get_db
from app.services.currency_service import get_currency_from_country

router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    country: str = "United States"
):
    user = await get_user_by_username(db, form_data.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    currency = get_currency_from_country(country)
    company = await create_company(db, {"name": f"{form_data.username}'s Company", "currency": currency})
    hashed_password = get_password_hash(form_data.password)
    new_user = await create_user(db, {
        "username": form_data.username,
        "email": form_data.username,  # Use username as email or adjust
        "hashed_password": hashed_password,
        "role": "ADMIN",
        "company_id": company.id
    })
    access_token = create_access_token({"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}