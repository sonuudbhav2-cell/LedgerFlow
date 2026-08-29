from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.ledger import AccountCreate, AccountResponse, BalanceResponse, JournalEntryCreate, JournalEntryResponse
from app.services.ledger import LedgerService

router = APIRouter()

@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(account_in: AccountCreate, db: AsyncSession = Depends(get_db)):
    service = LedgerService(db)
    return await service.create_account(account_in)

@router.get("/accounts/{account_id}/balance", response_model=BalanceResponse)
async def get_account_balance(account_id: UUID, db: AsyncSession = Depends(get_db)):
    service = LedgerService(db)
    result = await service.get_account_balance(account_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    account, balance = result
    return BalanceResponse(
        account_id=account.id,
        balance=balance,
        currency=account.currency  # Dynamically returning account's currency
    )

@router.post("/entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    entry_in: JournalEntryCreate,
    idempotency_key: str = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db)
):
    service = LedgerService(db)
    return await service.create_journal_entry(entry_in, idempotency_key=idempotency_key)