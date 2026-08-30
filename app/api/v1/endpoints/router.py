from fastapi import APIRouter
from app.api.v1.endpoints import reconciliation, reports

api_router = APIRouter()
api_router.include_router(reconciliation.router, prefix="/reconciliation")
api_router.include_router(reports.router)