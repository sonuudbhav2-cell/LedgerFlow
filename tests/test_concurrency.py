import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_concurrent_journal_entries(async_client: AsyncClient):
    # Setup accounts
    acc1 = (await async_client.post("/api/v1/accounts", json={"name": "Vault", "type": "ASSET", "currency": "USD"})).json()["id"]
    acc2 = (await async_client.post("/api/v1/accounts", json={"name": "Sales", "type": "REVENUE", "currency": "USD"})).json()["id"]

    async def send_entry(amount: str):
        payload = {
            "description": f"Concurrent Tx {amount}",
            "postings": [
                {"account_id": acc1, "amount": amount, "direction": "DEBIT"},
                {"account_id": acc2, "amount": amount, "direction": "CREDIT"}
            ]
        }
        return await async_client.post("/api/v1/entries", json=payload)

    # Fire 5 requests concurrently
    tasks = [send_entry("10.00") for _ in range(5)]
    responses = await asyncio.gather(*tasks)

    for res in responses:
        assert res.status_code == 201

    # Verify final balance equals 5 * 10.00 = 50.00
    bal_res = await async_client.get(f"/api/v1/accounts/{acc1}/balance")
    assert bal_res.status_code == 200
    assert float(bal_res.json()["balance"]) == 50.00