import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.reconciliation import MatchStatus


class ExternalTransactionResponse(BaseModel):
    id: uuid.UUID
    source: str
    external_ref: str
    amount: Decimal
    currency: str
    transaction_date: datetime
    match_status: MatchStatus
    matched_posting_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class ManualResolveRequest(BaseModel):
    posting_id: uuid.UUID


class ReconciliationRunResponse(BaseModel):
    total_processed: int
    exact_matches: int
    window_matches: int
    flagged_for_review: int