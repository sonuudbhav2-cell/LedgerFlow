from decimal import Decimal
from enum import Enum
from typing import List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator

class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"

class Direction(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class AccountCreate(BaseModel):
    name: str
    type: AccountType
    currency: str = "USD"

class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    type: AccountType
    currency: str

class BalanceResponse(BaseModel):
    account_id: UUID
    balance: Decimal
    currency: str

class PostingCreate(BaseModel):
    account_id: UUID
    amount: Decimal = Field(..., gt=0)
    direction: Direction

class PostingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    amount: Decimal
    direction: Direction

class JournalEntryCreate(BaseModel):
    description: str
    postings: List[PostingCreate]

    @model_validator(mode="after")
    def validate_double_entry_balance(self):
        debits = sum(p.amount for p in self.postings if p.direction == Direction.DEBIT)
        credits = sum(p.amount for p in self.postings if p.direction == Direction.CREDIT)
        if debits != credits:
            raise ValueError(f"Unbalanced entry: debits ({debits}) != credits ({credits})")
        return self

class JournalEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    description: str
    postings: List[PostingResponse]