from fastapi import APIRouter

router = APIRouter(prefix="/sql", tags=["SQL Server"])

@router.get("/")
async def get_sql_status():
    return {"module": "SQL Server", "status": "Ready"}
