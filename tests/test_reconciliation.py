import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_import_and_reconciliation_flow(async_client: AsyncClient):
    # Sample CSV content for bank statement import
    csv_data = (
        "external_ref,amount,currency,transaction_date\n"
        "EXT-1001,150.00,USD,2026-06-01T12:00:00\n"
        "EXT-1002,500.00,USD,2026-06-02T12:00:00\n"
    )

    response = await async_client.post(
        "/api/v1/reconciliation/import",
        params={"source": "stripe"},
        files={"file": ("statement.csv", csv_data.encode("utf-8"), "text/csv")}
    )
    assert response.status_code == 201
    assert "Successfully imported 2 external transactions" in response.json()["message"]

    # Run reconciliation
    run_res = await async_client.post("/api/v1/reconciliation/run")
    assert run_res.status_code == 200
    data = run_res.json()
    assert data["total_processed"] == 2

    # Check unmatched / review queue
    unmatched_res = await async_client.get("/api/v1/reconciliation/unmatched")
    assert unmatched_res.status_code == 200
    assert isinstance(unmatched_res.json(), list)