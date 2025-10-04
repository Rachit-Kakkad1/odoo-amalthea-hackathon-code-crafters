from fastapi import Depends, HTTPException, status
from .auth import get_current_user
from .database import get_db
from .models import User

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def is_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user