from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas import Expense, ExpenseCreate
from app.crud import create_expense, get_expenses_by_user
from app.deps import get_db, get_current_active_user
from app.services.currency_service import convert_currency
from app.services.ocr import process_ocr
from app.models import Expense as ExpenseModel, User as UserModel, Company
from sqlalchemy.sql import func

router = APIRouter()

@router.post("/", response_model=Expense)
async def submit_expense(
    expense_in: ExpenseCreate,
    receipt: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    if current_user.role not in [Role.EMPLOYEE, Role.MANAGER, Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Permission denied")
    db_company = await get_company_by_id(db, current_user.company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    company_currency = db_company.currency

    converted_amount = convert_currency(expense_in.amount, expense_in.currency, company_currency)

    receipt_path = None
    if receipt:
        receipt_path = await process_ocr(receipt)

    new_expense = ExpenseModel(
        employee_id=current_user.id,
        company_id=current_user.company_id,
        amount=expense_in.amount,
        currency=expense_in.currency,
        amount_in_company_currency=converted_amount,
        category=expense_in.category,
        description=expense_in.description,
        date=expense_in.date or func.now(),
        receipt_path=receipt_path
    )

    db.add(new_expense)
    await db.commit()
    await db.refresh(new_expense)
    return new_expense

@router.get("/", response_model=List[Expense])
async def view_expense_history(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    return await get_expenses_by_user(db, current_user.id)