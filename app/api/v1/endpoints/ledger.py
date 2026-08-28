from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.ledger import (
    AccountCreate,
    AccountResponse,
    JournalEntryCreate,
    JournalEntryResponse,
    TrialBalanceResponse,
)
from app.services.ledger import LedgerService

# Initialize the APIRouter instance for ledger endpoints
router = APIRouter()


@router.post(
    "/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
    description="Creates a financial account (ASSET, LIABILITY, EQUITY, REVENUE, or EXPENSE)."
)
async def create_account(
    account_in: AccountCreate,
    db: AsyncSession = Depends(get_db)
):
    """Creates an account record inside PostgreSQL."""
    return await LedgerService.create_account(db, account_in)


@router.get(
    "/accounts/{account_id}/balance",
    summary="Get account balance",
    description="Calculates the real-time normal balance based on all historical postings."
)
async def get_account_balance(
    account_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Fetches the dynamic double-entry balance for a given account UUID."""
    try:
        balance = await LedgerService.get_account_balance(db, account_id)
        return {
            "account_id": account_id,
            "balance": balance,
            "currency": "USD"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/journal-entries",
    response_model=JournalEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Post a double-entry transaction",
    description="Executes an atomic transaction with balanced DEBITs and CREDITs."
)
async def create_journal_entry(
    entry_in: JournalEntryCreate,
    idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    db: AsyncSession = Depends(get_db)
):
    """
    Validates double-entry rules, checks optional idempotency keys,
    and commits parent journal entries along with child postings atomically.
    """
    try:
        return await LedgerService.create_journal_entry(db, entry_in, idempotency_key)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/reports/trial-balance",
    response_model=TrialBalanceResponse,
    summary="Generate Trial Balance Report",
    description="Aggregates all account balances and verifies system-wide DEBIT and CREDIT equality."
)
async def get_trial_balance(
    db: AsyncSession = Depends(get_db)
):
    """Computes and returns the system trial balance report."""
    return await LedgerService.get_trial_balance(db)