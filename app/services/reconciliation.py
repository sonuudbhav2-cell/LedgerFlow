import io
import uuid
import polars as pl
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.reconciliation import ExternalTransaction, MatchStatus
from app.models.ledger import Posting


class ReconciliationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def import_csv_statement(self, source: str, file_content: bytes) -> int:
        """Parses CSV statement data using Polars and upserts into external_transactions."""
        try:
            df = pl.read_csv(io.BytesIO(file_content))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse CSV file: {str(e)}"
            )

        required_columns = {"external_ref", "amount", "currency", "transaction_date"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns. Expected: {list(required_columns)}"
            )

        count = 0
        for row in df.to_dicts():
            # Check if external_ref already exists
            existing_res = await self.db.execute(
                select(ExternalTransaction).where(ExternalTransaction.external_ref == str(row["external_ref"]))
            )
            if existing_res.scalar_one_or_none():
                continue

            tx_date = row["transaction_date"]
            if isinstance(tx_date, str):
                tx_date = datetime.fromisoformat(tx_date)

            ext_tx = ExternalTransaction(
                source=source,
                external_ref=str(row["external_ref"]),
                amount=Decimal(str(row["amount"])),
                currency=str(row["currency"]),
                transaction_date=tx_date,
                match_status=MatchStatus.UNMATCHED
            )
            self.db.add(ext_tx)
            count += 1

        await self.db.commit()
        return count

    async def run_reconciliation(self) -> dict:
        """Executes Tier 1 (Exact), Tier 2 (Window), and Tier 3 (Manual Review) matching."""
        unmatched_res = await self.db.execute(
            select(ExternalTransaction).where(ExternalTransaction.match_status == MatchStatus.UNMATCHED)
        )
        unmatched_txs = unmatched_res.scalars().all()

        # Get all postings that are not yet matched to any external transaction
        matched_posting_ids = select(ExternalTransaction.matched_posting_id).where(
            ExternalTransaction.matched_posting_id != None
        )
        postings_res = await self.db.execute(
            select(Posting).where(Posting.id.not_in(matched_posting_ids))
        )
        available_postings = postings_res.scalars().all()

        exact_matches = 0
        window_matches = 0
        flagged_for_review = 0

        for ext_tx in unmatched_txs:
            matched_posting = None

            # Tier 1: Exact Match (Amount & Currency match, exact timestamp or reference link if applicable)
            for p in available_postings:
                if p.amount == ext_tx.amount:
                    matched_posting = p
                    break

            if matched_posting:
                ext_tx.match_status = MatchStatus.EXACT_MATCH
                ext_tx.matched_posting_id = matched_posting.id
                available_postings.remove(matched_posting)
                exact_matches += 1
                continue

            # Tier 2: Window Match (Amount matches, within a 3-day date window)
            for p in available_postings:
                if p.amount == ext_tx.amount and p.created_at:
                    delta = abs(p.created_at.replace(tzinfo=None) - ext_tx.transaction_date.replace(tzinfo=None))
                    if delta <= timedelta(days=3):
                        matched_posting = p
                        break

            if matched_posting:
                ext_tx.match_status = MatchStatus.WINDOW_MATCH
                ext_tx.matched_posting_id = matched_posting.id
                available_postings.remove(matched_posting)
                window_matches += 1
                continue

            # Tier 3: Flag for Manual Review
            ext_tx.match_status = MatchStatus.MANUAL_REVIEW
            flagged_for_review += 1

        await self.db.commit()
        return {
            "total_processed": len(unmatched_txs),
            "exact_matches": exact_matches,
            "window_matches": window_matches,
            "flagged_for_review": flagged_for_review
        }

    async def get_unmatched_transactions(self) -> List[ExternalTransaction]:
        res = await self.db.execute(
            select(ExternalTransaction).where(
                ExternalTransaction.match_status.in_([MatchStatus.UNMATCHED, MatchStatus.MANUAL_REVIEW])
            )
        )
        return res.scalars().all()

    async def resolve_manual_match(self, transaction_id: uuid.UUID, posting_id: uuid.UUID) -> ExternalTransaction:
        ext_tx = await self.db.get(ExternalTransaction, transaction_id)
        if not ext_tx:
            raise HTTPException(status_code=404, detail="External transaction not found.")

        posting = await self.db.get(Posting, posting_id)
        if not posting:
            raise HTTPException(status_code=404, detail="Ledger posting not found.")

        ext_tx.matched_posting_id = posting.id
        ext_tx.match_status = MatchStatus.RESOLVED
        await self.db.commit()
        await self.db.refresh(ext_tx)
        return ext_tx