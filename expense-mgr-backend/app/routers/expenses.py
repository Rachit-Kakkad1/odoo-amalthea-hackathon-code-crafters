from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import schemas, auth
from ..crud import create_expense, get_expenses_for_user  # <-- FIXED: Renamed the function here
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Expense)
async def create_new_expense(
    expense: schemas.ExpenseCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    Create a new expense for the currently logged-in user.
    """
    return await create_expense(db=db, expense=expense, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Expense])
async def read_user_expenses(
    db: AsyncSession = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    Retrieve all expenses for the currently logged-in user.
    """
    return await get_expenses_for_user(db=db, user_id=current_user.id)