# app/api/v1/endpoints/reconciliation.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.reconciliation import ReconciliationService
from app.schemas.reconciliation import (
    ExternalTransactionResponse,
    ManualResolveRequest,
    ReconciliationRunResponse,
)

router = APIRouter()


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_statement(
    source: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Imports an external bank statement CSV feed using Polars."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported."
        )
    
    file_content = await file.read()
    service = ReconciliationService(db)
    imported_count = await service.import_csv_statement(source=source, file_content=file_content)
    
    return {"message": f"Successfully imported {imported_count} external transactions."}


@router.post("/run", response_model=ReconciliationRunResponse)
async def run_reconciliation(db: AsyncSession = Depends(get_db)):
    """Triggers the tiered reconciliation engine (Exact -> Window -> Manual Review)."""
    service = ReconciliationService(db)
    result = await service.run_reconciliation()
    return result


@router.get("/unmatched", response_model=List[ExternalTransactionResponse])
async def get_unmatched_transactions(db: AsyncSession = Depends(get_db)):
    """Retrieves all unmatched and manual review queue external transactions."""
    service = ReconciliationService(db)
    return await service.get_unmatched_transactions()


@router.post("/{transaction_id}/resolve", response_model=ExternalTransactionResponse)
async def resolve_manual_match(
    transaction_id: uuid.UUID,
    body: ManualResolveRequest,
    db: AsyncSession = Depends(get_db)
):
    """Manually maps an external transaction to a specific ledger posting."""
    service = ReconciliationService(db)
    return await service.resolve_manual_match(transaction_id=transaction_id, posting_id=body.posting_id)