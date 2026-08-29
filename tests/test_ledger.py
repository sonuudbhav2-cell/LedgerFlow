import pytest
from httpx import AsyncClient
from uuid import uuid4

@pytest.mark.asyncio
async def test_create_account_and_check_balance(client: AsyncClient):
    # Create EUR Account
    res = await client.post("/api/v1/accounts", json={"name": "EUR Bank", "type": "ASSET", "currency": "EUR"})
    assert res.status_code == 201
    account_id = res.json()["id"]
    assert res.json()["currency"] == "EUR"

    # Verify Balance Endpoint Returns EUR
    bal_res = await client.get(f"/api/v1/accounts/{account_id}/balance")
    assert bal_res.status_code == 200
    assert bal_res.json()["currency"] == "EUR"
    assert bal_res.json()["balance"] == "0.0000"

@pytest.mark.asyncio
async def test_idempotent_entry_creation(client: AsyncClient):
    # Setup 2 Accounts
    acc1 = (await client.post("/api/v1/accounts", json={"name": "Cash", "type": "ASSET", "currency": "USD"})).json()["id"]
    acc2 = (await client.post("/api/v1/accounts", json={"name": "Revenue", "type": "REVENUE", "currency": "USD"})).json()["id"]

    idempotency_key = str(uuid4())
    payload = {
        "description": "Payment",
        "postings": [
            {"account_id": acc1, "amount": "100.00", "direction": "DEBIT"},
            {"account_id": acc2, "amount": "100.00", "direction": "CREDIT"}
        ]
    }

    # First Request
    res1 = await client.post("/api/v1/entries", json=payload, headers={"Idempotency-Key": idempotency_key})
    assert res1.status_code == 201
    entry_id_1 = res1.json()["id"]

    # Replay Request with Same Key
    res2 = await client.post("/api/v1/entries", json=payload, headers={"Idempotency-Key": idempotency_key})
    assert res2.status_code == 201
    entry_id_2 = res2.json()["id"]

    # Verify identical journal entry is returned without duplicating records
    assert entry_id_1 == entry_id_2