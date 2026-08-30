import pytest
import asyncio
from httpx import AsyncClient
from uuid import uuid4

@pytest.mark.asyncio
async def test_concurrent_journal_entries(async_client: AsyncClient):
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

    tasks = [send_entry("10.00") for _ in range(5)]
    responses = await asyncio.gather(*tasks)

    for res in responses:
        assert res.status_code == 201

    bal_res = await async_client.get(f"/api/v1/accounts/{acc1}/balance")
    assert bal_res.status_code == 200
    assert float(bal_res.json()["balance"]) == 50.00

@pytest.mark.asyncio
async def test_concurrent_idempotent_race_safety(async_client: AsyncClient):
    acc1 = (await async_client.post("/api/v1/accounts", json={"name": "CashBox", "type": "ASSET", "currency": "USD"})).json()["id"]
    acc2 = (await async_client.post("/api/v1/accounts", json={"name": "FeeRevenue", "type": "REVENUE", "currency": "USD"})).json()["id"]

    shared_key = str(uuid4())
    payload = {
        "description": "Idempotent Race Test",
        "postings": [
            {"account_id": acc1, "amount": "25.00", "direction": "DEBIT"},
            {"account_id": acc2, "amount": "25.00", "direction": "CREDIT"}
        ]
    }

    async def send_with_key():
        return await async_client.post(
            "/api/v1/entries",
            json=payload,
            headers={"Idempotency-Key": shared_key}
        )

    # Fire 10 simultaneous requests with the exact same idempotency key
    responses = await asyncio.gather(*(send_with_key() for _ in range(10)))

    status_codes = [r.status_code for r in responses]
    created_count = status_codes.count(201)
    conflict_count = status_codes.count(409)

    # Exactly one request should succeed (201), and any concurrent overlaps either succeed via idempotency lookup or get locked/rejected cleanly (409)
    assert created_count >= 1
    
    entry_ids = [r.json()["id"] for r in responses if r.status_code == 201]
    assert len(set(entry_ids)) == 1  # All successful responses must point to the exact same entry ID

    # Verify balance reflects ONLY ONE posting (25.00), not N postings
    bal_res = await async_client.get(f"/api/v1/accounts/{acc1}/balance")
    assert float(bal_res.json()["balance"]) == 25.00

@pytest.mark.asyncio
async def test_concurrent_distinct_entries_same_account_no_deadlock(async_client: AsyncClient):
    shared = (await async_client.post(
        "/api/v1/accounts", json={"name": "SharedPool", "type": "ASSET", "currency": "USD"}
    )).json()["id"]
    counterparty = (await async_client.post(
        "/api/v1/accounts", json={"name": "SharedRevenue", "type": "REVENUE", "currency": "USD"}
    )).json()["id"]

    async def post_distinct_entry(i: int):
        return await async_client.post(
            "/api/v1/entries",
            json={
                "description": f"Distinct entry {i}",
                "postings": [
                    {"account_id": shared, "amount": "5.00", "direction": "DEBIT"},
                    {"account_id": counterparty, "amount": "5.00", "direction": "CREDIT"},
                ],
            },
            headers={"Idempotency-Key": str(uuid4())},  # different key each time
        )

    responses = await asyncio.gather(*(post_distinct_entry(i) for i in range(20)))
    assert all(r.status_code == 201 for r in responses)

    bal_res = await async_client.get(f"/api/v1/accounts/{shared}/balance")
    assert float(bal_res.json()["balance"]) == 100.00  # 20 * 5.00, no lost updates, no deadlock