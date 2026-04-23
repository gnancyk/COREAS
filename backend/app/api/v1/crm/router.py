from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter(prefix="/crm", tags=["CRM Dynamics"])

@router.get("/")
async def get_crm_status(current_user: str = Depends(get_current_user)):
    return {"module": "CRM Dynamics", "status": "Ready", "authorized_user": current_user}
