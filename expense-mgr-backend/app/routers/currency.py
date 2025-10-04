from fastapi import APIRouter, Query, HTTPException
from ..services.currency_service import get_countries_and_currencies, convert_currency

router = APIRouter()

@router.get("/countries", response_model=dict)
def list_countries_and_currencies():
    try:
        return get_countries_and_currencies()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/convert", response_model=dict)
def convert(
    amount: float = Query(..., description="Amount to convert", ge=0),
    from_currency: str = Query(..., description="Currency code of source (e.g., USD)", min_length=3, max_length=3),
    to_currency: str = Query(..., description="Currency code of target (e.g., INR)", min_length=3, max_length=3)
):
    try:
        converted = convert_currency(amount, from_currency, to_currency)
        return {
            "amount": amount,
            "from": from_currency.upper(),
            "to": to_currency.upper(),
            "converted_amount": converted
        }
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400 if isinstance(e, ValueError) else 500, detail=str(e))