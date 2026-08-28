from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class PostingDirection(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="Main Operating Checking")
    type: AccountType
    currency: str = Field(default="USD", min_length=3, max_length=3, example="USD")


class AccountCreate(AccountBase):
    pass


class AccountResponse(AccountBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostingCreate(BaseModel):
    account_id: UUID
    amount: Decimal = Field(..., gt=0, decimal_places=4, example=100.00)
    direction: PostingDirection


class PostingResponse(PostingCreate):
    id: UUID
    journal_entry_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JournalEntryCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=255, example="Customer Deposit")
    postings: List[PostingCreate]

    @model_validator(mode="after")
    def validate_double_entry_balance(self) -> "JournalEntryCreate":
        """
        Enforces double-entry accounting rules:
        1. Must contain at least two postings (at least one DEBIT and one CREDIT).
        2. Total DEBIT amount must equal Total CREDIT amount.
        """
        if len(self.postings) < 2:
            raise ValueError("A journal entry must contain at least two postings.")

        total_debits = Decimal("0.0000")
        total_credits = Decimal("0.0000")

        has_debit = False
        has_credit = False

        for posting in self.postings:
            if posting.direction == PostingDirection.DEBIT:
                total_debits += posting.amount
                has_debit = True
            elif posting.direction == PostingDirection.CREDIT:
                total_credits += posting.amount
                has_credit = True

        if not (has_debit and has_credit):
            raise ValueError("A journal entry must contain at least one DEBIT and one CREDIT posting.")

        if total_debits != total_credits:
            raise ValueError(
                f"Unbalanced journal entry: Total DEBITs ({total_debits}) "
                f"must equal Total CREDITs ({total_credits})."
            )

        return self


class JournalEntryResponse(BaseModel):
    id: UUID
    description: str
    idempotency_key: Optional[str] = None
    created_at: datetime
    postings: List[PostingResponse]

    model_config = ConfigDict(from_attributes=True)


class AccountTrialBalanceItem(BaseModel):
    account_id: UUID
    name: str
    type: str
    balance: Decimal


class TrialBalanceResponse(BaseModel):
    accounts: List[AccountTrialBalanceItem]
    total_system_debits: Decimal
    total_system_credits: Decimal
    is_balanced: bool