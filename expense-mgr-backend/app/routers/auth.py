from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import Token, PasswordResetRequest, PasswordReset
from app.crud import get_user_by_username, create_company, create_user, update_user_reset_token, update_user_password
from app.auth import get_password_hash, create_access_token, authenticate_user, create_reset_token, verify_reset_token
from app.deps import get_db
from app.services.currency_service import get_currency_from_country
import smtplib
from email.mime.text import MIMEText
from app.config import settings
from sqlalchemy import select

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

@router.post("/forgot-password", response_model=dict)
async def forgot_password(request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    reset_token = create_reset_token(request.email)
    await update_user_reset_token(db, request.email, reset_token)

    msg = MIMEText(f"Click this link to reset your password: http://127.0.0.1:8000/static/reset-password.html?token={reset_token}")
    msg['Subject'] = 'Password Reset Request'
    msg['From'] = settings.SMTP_USER
    msg['To'] = request.email

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return {"message": "Password reset email sent. Check your inbox."}

@router.post("/reset-password", response_model=dict)
async def reset_password(request: PasswordReset, db: AsyncSession = Depends(get_db)):
    email = verify_reset_token(request.token)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or user.reset_token != request.token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    hashed_password = get_password_hash(request.new_password)
    await update_user_password(db, email, hashed_password)
    await update_user_reset_token(db, email, None)  # Clear the token after reset
    return {"message": "Password reset successful"}