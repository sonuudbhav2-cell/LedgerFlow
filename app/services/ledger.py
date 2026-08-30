import uuid
from decimal import Decimal
from typing import Optional, Union, Tuple, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.ledger import Account, JournalEntry, Posting, IdempotencyRecord
from app.schemas.ledger import AccountCreate, JournalEntryCreate
from app.db.redis import redis_client


class LedgerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_account(self, account_data: AccountCreate) -> Account:
        existing = await self.db.execute(
            select(Account).where(Account.name == account_data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account with name '{account_data.name}' already exists."
            )

        account = Account(**account_data.model_dump())
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def _resolve_account(self, account_id_or_name: Union[uuid.UUID, str]) -> Account:
        parsed_uuid = None
        if isinstance(account_id_or_name, uuid.UUID):
            parsed_uuid = account_id_or_name
        elif isinstance(account_id_or_name, str):
            try:
                parsed_uuid = uuid.UUID(account_id_or_name)
            except ValueError:
                pass

        account = None
        if parsed_uuid:
            res = await self.db.execute(
                select(Account).where(Account.id == parsed_uuid)
            )
            account = res.scalar_one_or_none()

        if not account and isinstance(account_id_or_name, str):
            res = await self.db.execute(
                select(Account).where(Account.name == account_id_or_name)
            )
            account = res.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account '{account_id_or_name}' not found."
            )
        return account

    async def _lock_accounts(self, account_ids: List[uuid.UUID]) -> dict:
        """Acquire PostgreSQL row-level locks (SELECT ... FOR UPDATE) on the given
        accounts, always in sorted-by-id order, to serialize concurrent journal
        entries that touch the same account and to prevent deadlocks between
        two entries that share overlapping account sets."""
        unique_ids = sorted(set(account_ids))
        if not unique_ids:
            return {}

        stmt = (
            select(Account)
            .where(Account.id.in_(unique_ids))
            .order_by(Account.id)
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        locked = {a.id: a for a in result.scalars().all()}

        missing = set(unique_ids) - set(locked.keys())
        if missing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account(s) not found: {', '.join(str(m) for m in missing)}"
            )
        return locked

    async def get_account_balance(
        self, account_id: Union[uuid.UUID, str]
    ) -> Tuple[Account, Decimal]:
        account = await self._resolve_account(account_id)

        res = await self.db.execute(
            select(Posting).where(Posting.account_id == account.id)
        )
        postings = res.scalars().all()

        debits = Decimal(
            sum(p.amount for p in postings if getattr(p.direction, "value", p.direction) == "DEBIT")
        )
        credits = Decimal(
            sum(p.amount for p in postings if getattr(p.direction, "value", p.direction) == "CREDIT")
        )

        account_type = getattr(account.type, "value", account.type)
        if str(account_type).upper() in ["ASSET", "EXPENSE"]:
            balance_val = debits - credits
        else:
            balance_val = credits - debits

        return account, balance_val

    async def _get_entry_with_postings(self, entry_id: Union[uuid.UUID, str]) -> JournalEntry:
        if isinstance(entry_id, str):
            try:
                entry_id = uuid.UUID(entry_id)
            except ValueError:
                pass

        res = await self.db.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.postings))
            .where(JournalEntry.id == entry_id)
        )
        return res.scalar_one()

    async def create_journal_entry(
        self,
        entry_data: JournalEntryCreate,
        idempotency_key: Optional[str] = None
    ) -> JournalEntry:
        lock_acquired = False
        lock_key = f"lock:idempotency:{idempotency_key}" if idempotency_key else None

        if lock_key:
            lock_acquired = await redis_client.set(lock_key, "locked", nx=True, ex=30)
            if not lock_acquired:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A transaction with this idempotency key is currently being processed."
                )

        try:
            if idempotency_key:
                existing = await self.db.execute(
                    select(IdempotencyRecord).where(
                        IdempotencyRecord.key == idempotency_key
                    )
                )
                record = existing.scalar_one_or_none()
                if record:
                    return await self._get_entry_with_postings(record.journal_entry_id)

            # Resolve account references (id or name) to real account ids first,
            # without holding a lock yet.
            resolved_ids = []
            for posting_data in entry_data.postings:
                account = await self._resolve_account(posting_data.account_id)
                resolved_ids.append(account.id)

            # Now acquire row-level locks on every distinct account involved,
            # always in sorted order, BEFORE writing any postings. This is what
            # serializes two concurrent, DISTINCT journal entries that both touch
            # the same account — the Redis lock above only protects against the
            # same idempotency key being replayed, it does not serialize
            # different requests hitting the same account.
            locked_accounts = await self._lock_accounts(resolved_ids)

            journal_entry = JournalEntry(
                description=entry_data.description
            )
            self.db.add(journal_entry)
            await self.db.flush()

            for account_id, posting_data in zip(resolved_ids, entry_data.postings):
                posting = Posting(
                    journal_entry_id=journal_entry.id,
                    account_id=account_id,
                    amount=posting_data.amount,
                    direction=posting_data.direction
                )
                self.db.add(posting)

            if idempotency_key:
                idempotency_rec = IdempotencyRecord(
                    key=idempotency_key,
                    journal_entry_id=journal_entry.id,
                    status_code=201
                )
                self.db.add(idempotency_rec)

            await self.db.commit()
            return await self._get_entry_with_postings(journal_entry.id)

        finally:
            if lock_key and lock_acquired:
                await redis_client.delete(lock_key)