from decimal import Decimal
import json
from uuid import UUID
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.ledger import Account, JournalEntry, Posting, IdempotencyRecord
from app.schemas.ledger import AccountCreate, JournalEntryCreate

class LedgerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_account(self, account_in: AccountCreate) -> Account:
        account = Account(
            name=account_in.name,
            type=account_in.type.value,
            currency=account_in.currency
        )
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def get_account_balance(self, account_id: UUID) -> Optional[Tuple[Account, Decimal]]:
        result = await self.db.execute(select(Account).where(Account.id == account_id))
        account = result.scalar_one_or_none()
        if not account:
            return None

        debit_stmt = select(func.coalesce(func.sum(Posting.amount), 0)).where(
            Posting.account_id == account_id,
            Posting.direction == "DEBIT"
        )
        debit_res = await self.db.execute(debit_stmt)
        debit_sum = debit_res.scalar() or Decimal("0")

        credit_stmt = select(func.coalesce(func.sum(Posting.amount), 0)).where(
            Posting.account_id == account_id,
            Posting.direction == "CREDIT"
        )
        credit_res = await self.db.execute(credit_stmt)
        credit_sum = credit_res.scalar() or Decimal("0")

        if account.type in ["ASSET", "EXPENSE"]:
            balance = debit_sum - credit_sum
        else:
            balance = credit_sum - debit_sum

        return account, balance

    async def create_journal_entry(
        self, entry_in: JournalEntryCreate, idempotency_key: Optional[str] = None
    ) -> JournalEntry:
        if idempotency_key:
            stmt = select(IdempotencyRecord).where(IdempotencyRecord.key == idempotency_key)
            result = await self.db.execute(stmt)
            existing_record = result.scalar_one_or_none()

            if existing_record and existing_record.journal_entry_id:
                entry_stmt = (
                    select(JournalEntry)
                    .options(selectinload(JournalEntry.postings))
                    .where(JournalEntry.id == existing_record.journal_entry_id)
                )
                entry_res = await self.db.execute(entry_stmt)
                existing_entry = entry_res.scalar_one_or_none()
                if existing_entry:
                    return existing_entry

        account_ids = sorted(list(set([p.account_id for p in entry_in.postings])))
        
        # Acquire row-level lock (FOR UPDATE) in deterministically sorted order to prevent deadlocks
        acc_stmt = select(Account.id).where(Account.id.in_(account_ids)).with_for_update()
        acc_res = await self.db.execute(acc_stmt)
        found_account_ids = set(acc_res.scalars().all())

        missing_accounts = set(account_ids) - found_account_ids
        if missing_accounts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Accounts not found: {[str(i) for i in missing_accounts]}"
            )

        journal_entry = JournalEntry(description=entry_in.description)
        self.db.add(journal_entry)
        await self.db.flush()

        postings = [
            Posting(
                journal_entry_id=journal_entry.id,
                account_id=p.account_id,
                amount=p.amount,
                direction=p.direction.value
            )
            for p in entry_in.postings
        ]
        self.db.add_all(postings)

        if idempotency_key:
            idempotency_rec = IdempotencyRecord(
                key=idempotency_key,
                journal_entry_id=journal_entry.id,
                status_code=201
            )
            self.db.add(idempotency_rec)

        await self.db.commit()

        entry_stmt = (
            select(JournalEntry)
            .options(selectinload(JournalEntry.postings))
            .where(JournalEntry.id == journal_entry.id)
        )
        entry_res = await self.db.execute(entry_stmt)
        return entry_res.scalar_one()