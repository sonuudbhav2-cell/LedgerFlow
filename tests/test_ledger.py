import pytest
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError
from app.models.ledger import JournalEntry, Posting


@pytest.mark.asyncio
async def test_balance_trigger_rejects_unbalanced_entry(async_client: AsyncClient, async_session, engine_test):
    # This test requires real PostgreSQL where the trigger is active
    if "sqlite" in str(engine_test.url):
        pytest.skip("Balance trigger is PostgreSQL-specific")

    async with async_session as session:
        acc1_res = await async_client.post("/api/v1/accounts", json={"name": "TriggerAsset", "type": "ASSET", "currency": "USD"})
        acc2_res = await async_client.post("/api/v1/accounts", json={"name": "TriggerExpense", "type": "EXPENSE", "currency": "USD"})
        acc1_id = acc1_res.json()["id"]
        acc2_id = acc2_res.json()["id"]

        entry = JournalEntry(description="Unbalanced Direct Insert")
        session.add(entry)
        await session.flush()

        session.add(Posting(journal_entry_id=entry.id, account_id=acc1_id, amount="100.00", direction="DEBIT"))
        session.add(Posting(journal_entry_id=entry.id, account_id=acc2_id, amount="50.00", direction="CREDIT"))

        with pytest.raises(Exception) as exc_info:
            await session.commit()
        
        assert "Double-entry violation" in str(exc_info.value) or isinstance(exc_info.value, IntegrityError)
        await session.rollback()