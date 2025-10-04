from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_active_user
from app.services.ocr import process_ocr

router = APIRouter()

@router.post("/ocr", response_model=dict)
async def upload_receipt_for_ocr(
    receipt: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    try:
        extracted = await process_ocr(receipt)
        return extracted
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))