import asyncio
from prefect import flow, task

from app.db.session import AsyncSessionLocal
from app.services.reconciliation import ReconciliationService


@task(name="Run Automated Reconciliation")
async def trigger_reconciliation() -> dict:
    async with AsyncSessionLocal() as session:
        service = ReconciliationService(session)
        return await service.run_reconciliation()


@flow(name="LedgerFlow Daily Reconciliation Pipeline")
async def reconciliation_flow() -> dict:
    summary = await trigger_reconciliation()
    print(f"Reconciliation completed successfully: {summary}")
    return summary


if __name__ == "__main__":
    asyncio.run(reconciliation_flow())