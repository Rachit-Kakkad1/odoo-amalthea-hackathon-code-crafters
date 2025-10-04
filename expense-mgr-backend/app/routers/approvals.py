from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas import ApprovalRequest, ApprovalRequestBase
from app.crud import get_pending_approvals, update_approval_request
from app.deps import get_db, is_manager_or_admin
from app.services.approval_workflow import evaluate_approval

router = APIRouter()

@router.get("/pending", response_model=List[ApprovalRequest])
async def view_pending_approvals(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_manager_or_admin)
):
    return await get_pending_approvals(db, current_user.id)

@router.patch("/{approval_id}", response_model=ApprovalRequest)
async def approve_or_reject(
    approval_id: int,
    approval_in: ApprovalRequestBase,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_manager_or_admin)
):
    approval = await get_approval_request(db, approval_id)
    if not approval or approval.approver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this approval")
    updated_approval = await update_approval_request(db, approval_id, approval_in.dict(exclude_unset=True))
    await evaluate_approval(db, approval.expense_id)
    return updated_approval