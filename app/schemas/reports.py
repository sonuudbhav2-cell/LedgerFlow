from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.schemas.ledger import AccountType

class TrialBalanceItem(BaseModel):
    account_id: UUID
    account_name: str
    account_type: AccountType
    currency: str
    total_debits: Decimal
    total_credits: Decimal
    net_balance: Decimal

class TrialBalanceResponse(BaseModel):
    items: List[TrialBalanceItem]

class AccountActivityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    posting_id: UUID
    journal_entry_id: UUID
    description: str
    amount: Decimal
    direction: str
    created_at: Optional[str] = None

class AccountActivityResponse(BaseModel):
    account_id: UUID
    items: List[AccountActivityItem]
    limit: int
    offset: int