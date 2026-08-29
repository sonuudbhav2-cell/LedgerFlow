from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import ledger, reconciliation

app = FastAPI(
    title="LedgerFlow Core Ledger API",
    description="A double-entry accounting engine providing idempotent transactions, financial balance auditing, and race-condition prevention.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ledger.router, prefix="/api/v1", tags=["Ledger"])
app.include_router(reconciliation.router, prefix="/api/v1/reconciliation", tags=["Reconciliation"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}