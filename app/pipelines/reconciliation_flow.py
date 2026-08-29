import os
import httpx
from prefect import flow, task

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/reconciliation/run")


@task(retries=3, retry_delay_seconds=10)
def trigger_reconciliation_run() -> dict:
    """Triggers the backend reconciliation engine endpoint."""
    with httpx.Client(timeout=30.0) as client:
        response = client.post(API_URL)
        response.raise_for_status()
        return response.json()


@flow(name="ledgerflow-automated-reconciliation", log_prints=True)
def reconciliation_pipeline():
    print("Starting automated ledger reconciliation workflow...")
    result = trigger_reconciliation_run()
    print(f"Reconciliation completed successfully. Summary: {result}")
    return result


if __name__ == "__main__":
    reconciliation_pipeline()