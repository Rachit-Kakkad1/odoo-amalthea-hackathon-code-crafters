from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Company, User, Expense, ExpenseCategory, ApprovalRule, ApprovalRequest, AuditLog

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