from prefect import flow, task
from app.db.session import SessionLocal
from app.services.reconciliation import run_reconciliation_pipeline

@task(name="Run Automated Reconciliation")
def trigger_reconciliation():
    db = SessionLocal()
    try:
        result = run_reconciliation_pipeline(db)
        return result
    finally:
        db.close()

@flow(name="LedgerFlow Daily Reconciliation Pipeline")
def reconciliation_flow():
    summary = trigger_reconciliation()
    print(f"Reconciliation completed successfully: {summary}")
    return summary

if __name__ == "__main__":
    reconciliation_flow()