from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router

app = FastAPI(
    title="LedgerFlow Core Ledger API",
    description="A double-entry accounting engine providing idempotent transactions, financial balance auditing, and race-condition prevention.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Accounts",
            "description": "Operations for managing financial chart of accounts and querying real-time balance aggregations."
        },
        {
            "name": "Journal Entries",
            "description": "Double-entry posting operations with guaranteed idempotency and pessimistic row locking."
        },
        {
            "name": "System",
            "description": "Healthcheck and runtime status verification endpoints."
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "LedgerFlow Core"}