from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ledger import Account, IdempotencyRecord, JournalEntry, Posting
from app.schemas.ledger import AccountCreate, AccountType, JournalEntryCreate, PostingDirection


class LedgerService:

    @staticmethod
    async def create_account(session: AsyncSession, account_in: AccountCreate) -> Account:
        """Creates a new financial account (e.g., Checking, Revenue, Expense)."""
        account = Account(
            name=account_in.name,
            type=account_in.type.value,
            currency=account_in.currency,
        )
        session.add(account)
        await session.commit()
        await session.refresh(account)
        return account

    @staticmethod
    async def get_account(session: AsyncSession, account_id: UUID) -> Optional[Account]:
        """Fetches an account by its unique UUID."""
        result = await session.execute(select(Account).where(Account.id == account_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_account_balance(session: AsyncSession, account_id: UUID) -> Decimal:
        """
        Calculates the live balance of an account using double-entry rules:
        - ASSET / EXPENSE: Balance = Total DEBITs - Total CREDITs
        - LIABILITY / EQUITY / REVENUE: Balance = Total CREDITs - Total DEBITs
        """
        account = await LedgerService.get_account(session, account_id)
        if not account:
            raise ValueError(f"Account with ID '{account_id}' does not exist.")

        # Aggregate Total Debits
        debit_stmt = select(func.coalesce(func.sum(Posting.amount), Decimal("0.0000"))).where(
            Posting.account_id == account_id,
            Posting.direction == PostingDirection.DEBIT.value
        )
        debit_res = await session.execute(debit_stmt)
        total_debits: Decimal = debit_res.scalar_one()

        # Aggregate Total Credits
        credit_stmt = select(func.coalesce(func.sum(Posting.amount), Decimal("0.0000"))).where(
            Posting.account_id == account_id,
            Posting.direction == PostingDirection.CREDIT.value
        )
        credit_res = await session.execute(credit_stmt)
        total_credits: Decimal = credit_res.scalar_one()

        # Normal Balance Calculation Rule
        if account.type in [AccountType.ASSET.value, AccountType.EXPENSE.value]:
            return total_debits - total_credits
        else:
            return total_credits - total_debits

    @staticmethod
    async def create_journal_entry(
        session: AsyncSession,
        entry_in: JournalEntryCreate,
        idempotency_key: Optional[str] = None
    ) -> JournalEntry:
        """
        Executes an Atomic Double-Entry Transaction.
        Handles idempotency to prevent duplicate charges from network retries.
        """
        # Step 1: Idempotency Gatekeeper Check
        if idempotency_key:
            stmt = select(IdempotencyRecord).where(IdempotencyRecord.key == idempotency_key)
            res = await session.execute(stmt)
            existing_record = res.scalar_one_or_none()

            if existing_record:
                entry_stmt = (
                    select(JournalEntry)
                    .options(selectinload(JournalEntry.postings))
                    .where(JournalEntry.id == existing_record.journal_entry_id)
                )
                entry_res = await session.execute(entry_stmt)
                return entry_res.scalar_one()

        # Step 2: Atomic Transaction Execution Block
        async with session.begin_nested():
            # Validate that all target accounts exist
            account_ids = {posting.account_id for posting in entry_in.postings}
            acc_stmt = select(Account.id).where(Account.id.in_(account_ids))
            acc_res = await session.execute(acc_stmt)
            found_ids = set(acc_res.scalars().all())

            if len(found_ids) != len(account_ids):
                missing = account_ids - found_ids
                raise ValueError(f"Transaction rejected. The following account IDs do not exist: {missing}")

            # Insert Parent Journal Entry
            journal_entry = JournalEntry(
                description=entry_in.description,
                idempotency_key=idempotency_key
            )
            session.add(journal_entry)
            await session.flush()

            # Insert Child Postings
            for posting_in in entry_in.postings:
                posting = Posting(
                    journal_entry_id=journal_entry.id,
                    account_id=posting_in.account_id,
                    amount=posting_in.amount,
                    direction=posting_in.direction.value
                )
                session.add(posting)

            # Record Idempotency Key
            if idempotency_key:
                idempotency_rec = IdempotencyRecord(
                    key=idempotency_key,
                    journal_entry_id=journal_entry.id
                )
                session.add(idempotency_rec)

        # Step 3: Commit Outer Transaction to Disk
        await session.commit()

        # Step 4: Retrieve and Return the Full Record
        final_stmt = (
            select(JournalEntry)
            .options(selectinload(JournalEntry.postings))
            .where(JournalEntry.id == journal_entry.id)
        )
        final_res = await session.execute(final_stmt)
        return final_res.scalar_one()

    @staticmethod
    async def get_trial_balance(session: AsyncSession) -> dict:
        """
        Generates a system-wide Trial Balance report.
        Aggregates all accounts, calculates their individual balances,
        and verifies that total system debits equal total system credits.
        """
        acc_result = await session.execute(select(Account))
        accounts = acc_result.scalars().all()

        account_items = []
        for acc in accounts:
            balance = await LedgerService.get_account_balance(session, acc.id)
            account_items.append({
                "account_id": acc.id,
                "name": acc.name,
                "type": acc.type,
                "balance": balance
            })

        total_debits_stmt = select(func.coalesce(func.sum(Posting.amount), Decimal("0.0000"))).where(
            Posting.direction == PostingDirection.DEBIT.value
        )
        total_debits_res = await session.execute(total_debits_stmt)
        total_system_debits = total_debits_res.scalar_one()

        total_credits_stmt = select(func.coalesce(func.sum(Posting.amount), Decimal("0.0000"))).where(
            Posting.direction == PostingDirection.CREDIT.value
        )
        total_credits_res = await session.execute(total_credits_stmt)
        total_system_credits = total_credits_res.scalar_one()

        is_balanced = (total_system_debits == total_system_credits)

        return {
            "accounts": account_items,
            "total_system_debits": total_system_debits,
            "total_system_credits": total_system_credits,
            "is_balanced": is_balanced
        }