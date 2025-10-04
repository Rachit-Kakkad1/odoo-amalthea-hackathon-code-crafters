from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Company, User, Expense, ExpenseCategory, ApprovalRule, ApprovalRequest, AuditLog
from fastapi import HTTPException

async def create_company(db: AsyncSession, company: dict):
    db_company = Company(**company)
    db.add(db_company)
    await db.commit()
    await db.refresh(db_company)
    return db_company

async def create_user(db: AsyncSession, user: dict):
    db_user = User(**user)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_company_by_id(db: AsyncSession, company_id: int):
    result = await db.execute(select(Company).where(Company.id == company_id))
    return result.scalars().first()

async def create_expense(db: AsyncSession, expense: dict):
    db_expense = Expense(**expense)
    db.add(db_expense)
    await db.commit()
    await db.refresh(db_expense)
    return db_expense

async def update_user_reset_token(db: AsyncSession, email: str, reset_token: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.reset_token = reset_token
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_password(db: AsyncSession, email: str, hashed_password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = hashed_password
    await db.commit()
    await db.refresh(user)
    return user