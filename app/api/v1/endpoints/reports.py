from uuid import UUID
from datetime import datetime
from typing import Optionalfrom decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.db.session import get_db
from app.models.ledger import Account, Posting, JournalEntry
from app.schemas.reports import TrialBalanceResponse, TrialBalanceItem, AccountActivityResponse, AccountActivityItem
from app.db.redis import redis_client
import json

router = APIRouter()

@router.get("/trial-balance", response_model=TrialBalanceResponse)
async def get_trial_balance(db: AsyncSession = Depends(get_db)):
    cache_key = "report:trial_balance"
    cached = await redis_client.get(cache_key)
    if cached:
        return TrialBalanceResponse.model_validate_json(cached)

    stmt = (
        select(
            Account.id,
            Account.name,
            Account.type,
            Account.currency,
            func.coalesce(func.sum(func.case((Posting.direction == 'DEBIT', Posting.amount), else_=0)), 0).label("debits"),
            func.coalesce(func.sum(func.case((Posting.direction == 'CREDIT', Posting.amount), else_=0)), 0).label("credits")
        )
        .outerjoin(Posting, Account.id == Posting.account_id)
        .group_by(Account.id)
    )
    result = await db.execute(stmt)
    rows = result.all()

    items = []
    for row in rows:
        acc_type = str(row.type).upper()
        net = (row.debits - row.credits) if acc_type in ["ASSET", "EXPENSE"] else (row.credits - row.debits)
        items.append(
            TrialBalanceItem(
                account_id=row.id,
                account_name=row.name,
                account_type=row.type,
                currency=row.currency,
                total_debits=row.debits,
                total_credits=row.credits,
                net_balance=net
            )
        )

    response_obj = TrialBalanceResponse(items=items)
    await redis_client.set(cache_key, response_obj.model_dump_json(), ex=60)
    return response_obj

@router.get("/account-activity", response_model=AccountActivityResponse)
async def get_account_activity(
    account_id: UUID = Query(...),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    query = (
        select(Posting, JournalEntry.description, JournalEntry.created_at)
        .join(JournalEntry, Posting.journal_entry_id == JournalEntry.id)
        .where(Posting.account_id == account_id)
    )

    if from_date:
        query = query.where(JournalEntry.created_at >= from_date)
    if to_date:
        query = query.where(JournalEntry.created_at <= to_date)

    query = query.order_by(JournalEntry.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    rows = result.all()

    items = [
        AccountActivityItem(
            posting_id=row.Posting.id,
            journal_entry_id=row.Posting.journal_entry_id,
            description=row.description,
            amount=row.Posting.amount,
            direction=row.Posting.direction,
            created_at=row.created_at.isoformat() if row.created_at else None
        )
        for row in rows
    ]

    return AccountActivityResponse(account_id=account_id, items=items, limit=limit, offset=offset)