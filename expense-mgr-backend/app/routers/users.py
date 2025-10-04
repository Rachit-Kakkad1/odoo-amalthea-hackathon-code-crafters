from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas import User, UserCreate
from app.crud import create_user, get_users_by_company, get_user, update_user
from app.deps import get_db, is_admin
from app.models import User as UserModel
from app.auth import get_password_hash

router = APIRouter()

@router.post("/", response_model=User)
async def create_new_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_admin)
):
    user = await get_user_by_username(db, user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user_in.password)
    new_user = await create_user(db, {
        "username": user_in.username,
        "email": user_in.email,
        "hashed_password": hashed_password,
        "role": user_in.role,
        "company_id": current_user.company_id
    })
    return new_user

@router.get("/", response_model=List[User])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_admin)
):
    return await get_users_by_company(db, current_user.company_id)

@router.patch("/{user_id}", response_model=User)
async def update_user_role(
    user_id: int,
    role: Role = None,
    manager_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_admin)
):
    user = await get_user(db, user_id)
    if not user or user.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="User not found")
    updates = {}
    if role:
        updates["role"] = role
    if manager_id:
        updates["manager_id"] = manager_id
    updated_user = await update_user(db, user_id, updates)
    return updated_user