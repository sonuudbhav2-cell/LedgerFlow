from fastapi import APIRouter
from app.api.v1.endpoints.ledger import router as ledger_router

api_router = APIRouter()
api_router.include_router(ledger_router)