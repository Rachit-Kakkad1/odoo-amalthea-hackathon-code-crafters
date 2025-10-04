# app/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas import ApprovalRule, ApprovalRuleCreate, Expense
from app.crud import create_approval_rule, get_approval_rules, get_all_expenses, update_expense_status
from app.deps import get_db, is_admin

router = APIRouter()

@router.post("/rules", response_model=ApprovalRule)
async def create_approval_rule(
    rule_in: ApprovalRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_admin)
):
    new_rule = await create_approval_rule(db, rule_in.dict(), current_user.company_id)
    return new_rule

@router.get("/rules", response_model=List[ApprovalRule])
async def get_company_rules(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_admin)
):
    return await get_approval_rules(db, current_user.company_id)

@router.get("/expenses", response_model=List[Expense])
async def view_all_expenses(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_admin)
):
    return await get_all_expenses(db, current_user.company_id)

@router.patch("/expenses/{expense_id}", response_model=Expense)
async def override_expense(
    expense_id: int,
    status: ExpenseStatus,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_admin)
):
    updated_expense = await update_expense_status(db, expense_id, status, current_user.company_id)
    return updated_expense