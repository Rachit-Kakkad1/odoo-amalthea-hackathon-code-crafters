from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, crud
from ..deps import get_current_active_user, get_db
from ..services.currency_service import convert_currency
from ..models import Expense, Company

router = APIRouter()

@router.post("/", response_model=schemas.Expense)
async def create_expense(
    expense_in: schemas.ExpenseCreate,
    receipt: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    db_company = await crud.get_company_by_id(db, current_user.company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    company_currency = db_company.currency

    try:
        converted_amount = convert_currency(expense_in.amount, expense_in.currency, company_currency)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    new_expense = Expense(
        employee_id=current_user.id,
        company_id=current_user.company_id,
        amount=expense_in.amount,
        currency=expense_in.currency,
        amount_in_company_currency=converted_amount,
        category=expense_in.category,
        description=expense_in.description,
        date=expense_in.date or func.now(),
    )

    db.add(new_expense)
    await db.commit()
    await db.refresh(new_expense)

    if receipt:
        new_expense.receipt_path = f"receipts/{receipt.filename}"  # Placeholder; implement storage

    return new_expense