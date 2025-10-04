from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas import Token, PasswordResetRequest, PasswordReset, User as UserSchema
from app.crud import get_user_by_username, create_company, create_user, update_user_reset_token, update_user_password
from app.auth import get_password_hash, create_access_token, authenticate_user, create_reset_token, verify_reset_token, send_email, generate_random_password, get_current_user
from app.deps import get_db
from app.models import User, Role
from datetime import datetime

# --- NEW: Import the email utility ---
from .. import email_utils

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
    currency = "USD"  # Placeholder, replace with actual currency service
    company = await create_company(db, {"name": f"{form_data.username}'s Company", "currency": currency})
    hashed_password = get_password_hash(form_data.password)
    new_user = await create_user(db, {
        "username": form_data.username,
        "email": f"{form_data.username}@example.com",  # Default email
        "mobile_number": None,
        "hashed_password": hashed_password,
        "role": Role.EMPLOYEE,
        "company_id": company.id
    })
    access_token = create_access_token({"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
# --- MODIFIED: Added `background_tasks: BackgroundTasks` ---
async def login(
    background_tasks: BackgroundTasks,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token({"sub": user.username})

    # --- MODIFIED: Check for Admin/Manager and send email in the background ---
    if user.role in [Role.ADMIN, Role.MANAGER]:
        user_details = {"email": user.email, "role": user.role.value}
        background_tasks.add_task(email_utils.send_login_notification_email, user_details)
        
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/admin-login", response_model=dict)
async def notify_admin_login(current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can trigger this")
    
    # This endpoint still uses the original send_email function for its specific purpose
    await send_email(
        current_user.email, # Assuming this should go to the admin's own email
        "Admin Login Notification",
        f"Admin {current_user.username} logged in at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC."
    )
    return {"message": "Admin login notification sent"}

@router.post("/forgot-password", response_model=dict)
async def forgot_password(request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, request.username)
    if not user or not user.email:
        raise HTTPException(status_code=404, detail="User not found or email not set")

    new_password = generate_random_password()
    hashed_password = get_password_hash(new_password)
    await update_user_password(db, user.username, hashed_password)

    await send_email(
        user.email,
        "Password Reset",
        f"Your new password is: {new_password}. Please change it after logging in."
    )

    return {"message": "A new password has been sent to your email."}

@router.post("/reset-password", response_model=dict)
async def reset_password(request: PasswordReset, db: AsyncSession = Depends(get_db)):
    username = verify_reset_token(request.token)
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user or user.reset_token != request.token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    hashed_password = get_password_hash(request.new_password)
    await update_user_password(db, username, hashed_password)
    await update_user_reset_token(db, username, None)
    return {"message": "Password reset successful"}