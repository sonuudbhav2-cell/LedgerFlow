from fastapi import FastAPI
from app.api.v1.endpoints import ledger
from app.core.config import settings

# 1. Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    description="High-Throughput Financial Ledger Engine built with FastAPI, SQLAlchemy, and PostgreSQL."
)

# 2. Register API Routers
app.include_router(
    ledger.router,
    prefix="/api/v1",
    tags=["Ledger"]
)


# 3. Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify server availability."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "project": settings.PROJECT_NAME
    }