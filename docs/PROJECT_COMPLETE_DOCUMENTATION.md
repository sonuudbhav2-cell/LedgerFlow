# LedgerFlow — Complete Project Master Documentation

## SECTION A — PROJECT OVERVIEW

LedgerFlow is an enterprise-grade financial accounting engine implementing a double-entry journal system. It is engineered with Python, FastAPI, AsyncSQLAlchemy, PostgreSQL, and Redis to solve real-time balance drift and race conditions during high-volume transaction processing.

### Key Architectural Invariants
1. **Zero-Sum Entry Constraint**: Every journal transaction must satisfy sum(Debits) == sum(Credits).
2. **Pessimistic Concurrency**: Prevents race conditions using PostgreSQL `SELECT ... FOR UPDATE` row locks on target account records.
3. **Idempotent Execution**: Redis key storage prevents duplicate journal posting upon client network retries.

## SECTION B — REPOSITORY FILE INDEX & DIRECTORY TREE

```text
LedgerFlow/
├── .env
├── .gitignore
├── Dockerfile
├── alembic.ini
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
├── app/__init__.py
├── app/main.py
├── app/core/__init__.py
├── app/core/config.py
├── app/pipelines/reconciliation_flow.py
├── app/models/__init__.py
├── app/models/ledger.py
├── app/models/reconciliation.py
├── app/schemas/__init__.py
├── app/schemas/ledger.py
├── app/schemas/reconciliation.py
├── app/db/__init__.py
├── app/db/redis.py
├── app/db/session.py
├── app/api/__init__.py
├── app/api/v1/__init__.py
├── app/api/v1/endpoints/__init__.py
├── app/api/v1/endpoints/ledger.py
├── app/api/v1/endpoints/reconciliation.py
├── app/services/__init__.py
├── app/services/ledger.py
├── app/services/reconciliation.py
├── tests/conftest.py
├── tests/test_concurrency.py
├── tests/test_ledger.py
├── tests/test_reconciliation.py
├── scripts/scan_and_document.py
├── .github/workflows/ci.yml
├── alembic/README
├── alembic/env.py
├── alembic/script.py.mako
├── alembic/versions/67a7b755039d_add_journal_entry_id_to_idempotency_.py
├── alembic/versions/7bb8fd203663_create_initial_ledger_tables.py
├── alembic/versions/7e439f48f1f1_add_external_transactions_table_for_.py
├── alembic/versions/dfc16bb48d9f_restore_posting_account_created_index.py
├── alembic/versions/f2c0064de257_add_zero_sum_balance_trigger.py
```

## SECTION C — COMPLETE SOURCE CODE & MODULE REFERENCE

### File: `.env`

**Purpose**: Project configuration, script, or component file for .env.

**Functional Overview**: Implements necessary operational functionality for module .env.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```text
PROJECT_NAME="LedgerFlow"
ENVIRONMENT="development"
DATABASE_URL="postgresql+asyncpg://ledger_user:ledger_password@localhost:5432/ledgerflow"
REDIS_URL="redis://localhost:6379/0"
```

---

### File: `.gitignore`

**Purpose**: Project configuration, script, or component file for .gitignore.

**Functional Overview**: Implements necessary operational functionality for module .gitignore.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```text
# Virtual Environment
.venv/
venv/
env/

# Environment Variables & Secrets
.env
*.env

# Python Bytecode & Caches
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/

# macOS / OS files
.DS_Store

# IDEs
.vscode/
.idea/
```

---

### File: `Dockerfile`

**Purpose**: Project configuration, script, or component file for Dockerfile.

**Functional Overview**: Implements necessary operational functionality for module Dockerfile.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```text
# Use lightweight official Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install dependencies first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project code into the container
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### File: `alembic.ini`

**Purpose**: Project configuration, script, or component file for alembic.ini.

**Functional Overview**: Implements necessary operational functionality for module alembic.ini.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```ini
# A generic, single database configuration.

[alembic]
# path to migration scripts.
# this is typically a path given in POSIX (e.g. forward slashes)
# format, relative to the token %(here)s which refers to the location of this
# ini file
script_location = %(here)s/alembic

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# see https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
# for all available tokens
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
# Or organize into date-based subdirectories (requires recursive_version_locations = true)
# file_template = %%(year)d/%%(month).2d/%%(day).2d_%%(hour).2d%%(minute).2d_%%(second).2d_%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.  for multiple paths, the path separator
# is defined by "path_separator" below.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the tzdata library which can be installed by adding
# `alembic[tz]` to the pip requirements.
# string value is passed to ZoneInfo()
# leave blank for localtime
# timezone =

# max length of characters to apply to the "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; This defaults
# to <script_location>/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
# The path separator used here should be the separator specified by "path_separator"
# below.
# version_locations = %(here)s/bar:%(here)s/bat:%(here)s/alembic/versions

# path_separator; This indicates what character is used to split lists of file
# paths, including version_locations and prepend_sys_path within configparser
# files such as alembic.ini.
# The default rendered in new alembic.ini files is "os", which uses os.pathsep
# to provide os-dependent path splitting.
#
# Note that in order to support legacy alembic.ini files, this default does NOT
# take place if path_separator is not present in alembic.ini.  If this
# option is omitted entirely, fallback logic is as follows:
#
# 1. Parsing of the version_locations option falls back to using the legacy
#    "version_path_separator" key, which if absent then falls back to the legacy
#    behavior of splitting on spaces and/or commas.
# 2. Parsing of the prepend_sys_path option falls back to the legacy
#    behavior of splitting on spaces, commas, or colons.
#
# Valid values for path_separator are:
#
# path_separator = :
# path_separator = ;
# path_separator = space
# path_separator = newline
#
# Use os.pathsep. Default configuration used for new projects.
path_separator = os


# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

# database URL.  This is consumed by the user-maintained env.py script only.
# other means of configuring database URLs may be customized within the env.py
# file.
sqlalchemy.url = driver://user:pass@localhost/dbname


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the module runner, against the "ruff" module
# hooks = ruff
# ruff.type = module
# ruff.module = ruff
# ruff.options = check --fix REVISION_SCRIPT_FILENAME

# Alternatively, use the exec runner to execute a binary found on your PATH
# hooks = ruff
# ruff.type = exec
# ruff.executable = ruff
# ruff.options = check --fix REVISION_SCRIPT_FILENAME

# Logging configuration.  This is also consumed by the user-maintained
# env.py script only.
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

---

### File: `docker-compose.yml`

**Purpose**: Project configuration, script, or component file for docker-compose.yml.

**Functional Overview**: Implements necessary operational functionality for module docker-compose.yml.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```yml
version: '3.8'

services:
  api:
    build: .
    container_name: ledgerflow_api
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://ledger_user:ledger_password@postgres:5432/ledgerflow
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  postgres:
    image: postgres:16-alpine
    container_name: ledgerflow_postgres
    restart: always
    environment:
      POSTGRES_USER: ledger_user
      POSTGRES_PASSWORD: ledger_password
      POSTGRES_DB: ledgerflow
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ledger_user -d ledgerflow"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ledgerflow_redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  prefect-worker:
    image: prefecthq/prefect:3-python3.11
    container_name: ledgerflow_prefect_worker
    environment:
      - PREFECT_API_URL=http://api0.local:4200/api
    command: prefect worker start --pool default-agent-pool

volumes:
  postgres_data:
  redis_data:
```

---

### File: `pytest.ini`

**Purpose**: Project configuration, script, or component file for pytest.ini.

**Functional Overview**: Implements necessary operational functionality for module pytest.ini.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```ini
[pytest]
pythonpath = .
asyncio_mode = auto
```

---

### File: `requirements.txt`

**Purpose**: Project configuration, script, or component file for requirements.txt.

**Functional Overview**: Implements necessary operational functionality for module requirements.txt.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```txt
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.0
pydantic-settings>=2.2.0
sqlalchemy[asyncio]>=2.0.28
asyncpg>=0.29.0
alembic>=1.13.1
redis>=5.0.3
polars>=0.20.15
prefect>=2.16.0
pytest>=8.1.0
pytest-asyncio>=0.23.5
httpx>=0.27.0
```

---

### File: `app/__init__.py`

**Purpose**: Project configuration, script, or component file for app/__init__.py.

**Functional Overview**: Implements necessary operational functionality for module app/__init__.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py

```

---

### File: `app/main.py`

**Purpose**: Project configuration, script, or component file for app/main.py.

**Functional Overview**: Implements necessary operational functionality for module app/main.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
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
```

---

### File: `app/core/__init__.py`

**Purpose**: Project configuration, script, or component file for app/core/__init__.py.

**Functional Overview**: Implements necessary operational functionality for module app/core/__init__.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py

```

---

### File: `app/core/config.py`

**Purpose**: Project configuration, script, or component file for app/core/config.py.

**Functional Overview**: Implements necessary operational functionality for module app/core/config.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "LedgerFlow"
    ENVIRONMENT: str = "development"
    
    # Database and Caching URLs read from .env
    DATABASE_URL: str
    REDIS_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
```

---

### File: `app/pipelines/reconciliation_flow.py`

**Purpose**: Project configuration, script, or component file for app/pipelines/reconciliation_flow.py.

**Functional Overview**: Implements necessary operational functionality for module app/pipelines/reconciliation_flow.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
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
```

---

### File: `app/models/__init__.py`

**Purpose**: Project configuration, script, or component file for app/models/__init__.py.

**Functional Overview**: Implements necessary operational functionality for module app/models/__init__.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py

```

---

### File: `app/models/ledger.py`

**Purpose**: Project configuration, script, or component file for app/models/ledger.py.

**Functional Overview**: Implements necessary operational functionality for module app/models/ledger.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    postings = relationship("Posting", back_populates="account")

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    postings = relationship("Posting", back_populates="journal_entry", cascade="all, delete-orphan")

class Posting(Base):
    __tablename__ = "postings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    amount = Column(Numeric(precision=18, scale=4), nullable=False)
    direction = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    journal_entry = relationship("JournalEntry", back_populates="postings")
    account = relationship("Account", back_populates="postings")

    __table_args__ = (
        # Composite index for fast balance aggregation (Filtering by account + direction)
        Index("ix_postings_account_direction", "account_id", "direction"),
        Index("ix_postings_journal_entry_id", "journal_entry_id"),
    )

class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(255), unique=True, nullable=False, index=True)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=True)
    status_code = Column(Numeric(3, 0), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

---

### File: `app/models/reconciliation.py`

**Purpose**: Project configuration, script, or component file for app/models/reconciliation.py.

**Functional Overview**: Implements necessary operational functionality for module app/models/reconciliation.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


class MatchStatus(str, Enum):
    UNMATCHED = "unmatched"
    EXACT_MATCH = "exact_match"
    WINDOW_MATCH = "window_match"
    MANUAL_REVIEW = "manual_review"
    RESOLVED = "resolved"


class ExternalTransaction(Base):
    __tablename__ = "external_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(100), nullable=False)  # e.g., "stripe", "bank_feed"
    external_ref = Column(String(255), unique=True, nullable=False, index=True)
    amount = Column(Numeric(precision=18, scale=4), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    match_status = Column(SQLEnum(MatchStatus), nullable=False, default=MatchStatus.UNMATCHED)
    matched_posting_id = Column(UUID(as_uuid=True), ForeignKey("postings.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    matched_posting = relationship("Posting", foreign_keys=[matched_posting_id])
```

---

### File: `app/schemas/__init__.py`

**Purpose**: Project configuration, script, or component file for app/schemas/__init__.py.

**Functional Overview**: Implements necessary operational functionality for module app/schemas/__init__.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py

```

---

### File: `app/schemas/ledger.py`

**Purpose**: Project configuration, script, or component file for app/schemas/ledger.py.

**Functional Overview**: Implements necessary operational functionality for module app/schemas/ledger.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
from decimal import Decimal
from enum import Enum
from typing import List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator

class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"

class Direction(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class AccountCreate(BaseModel):
    name: str
    type: AccountType
    currency: str = "USD"

class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    type: AccountType
    currency: str

class BalanceResponse(BaseModel):
    account_id: UUID
    balance: Decimal
    currency: str

class PostingCreate(BaseModel):
    account_id: UUID
    amount: Decimal = Field(..., gt=0)
    direction: Direction

class PostingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    amount: Decimal
    direction: Direction

class JournalEntryCreate(BaseModel):
    description: str
    postings: List[PostingCreate]

    @model_validator(mode="after")
    def validate_double_entry_balance(self):
        debits = sum(p.amount for p in self.postings if p.direction == Direction.DEBIT)
        credits = sum(p.amount for p in self.postings if p.direction == Direction.CREDIT)
        if debits != credits:
            raise ValueError(f"Unbalanced entry: debits ({debits}) != credits ({credits})")
        return self

class JournalEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    description: str
    postings: List[PostingResponse]
```

---

### File: `app/schemas/reconciliation.py`

**Purpose**: Project configuration, script, or component file for app/schemas/reconciliation.py.

**Functional Overview**: Implements necessary operational functionality for module app/schemas/reconciliation.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.reconciliation import MatchStatus


class ExternalTransactionResponse(BaseModel):
    id: uuid.UUID
    source: str
    external_ref: str
    amount: Decimal
    currency: str
    transaction_date: datetime
    match_status: MatchStatus
    matched_posting_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class ManualResolveRequest(BaseModel):
    posting_id: uuid.UUID


class ReconciliationRunResponse(BaseModel):
    total_processed: int
    exact_matches: int
    window_matches: int
    flagged_for_review: int
```

---

### File: `app/db/__init__.py`

**Purpose**: Project configuration, script, or component file for app/db/__init__.py.

**Functional Overview**: Implements necessary operational functionality for module app/db/__init__.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py

```

---

### File: `app/db/redis.py`

**Purpose**: Project configuration, script, or component file for app/db/redis.py.

**Functional Overview**: Implements necessary operational functionality for module app/db/redis.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
import redis.asyncio as aioredis
from app.core.config import settings

redis_client = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True
)

async def get_redis() -> aioredis.Redis:
    return redis_client
```

---

### File: `app/db/session.py`

**Purpose**: Project configuration, script, or component file for app/db/session.py.

**Functional Overview**: Implements necessary operational functionality for module app/db/session.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase  # <--- Added this
from app.core.config import settings


# Base class for SQLAlchemy models
class Base(DeclarativeBase):  # <--- Added this
    pass


# Create async engine
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# FastAPI Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

---

### File: `app/api/__init__.py`

**Purpose**: Project configuration, script, or component file for app/api/__init__.py.

**Functional Overview**: Implements necessary operational functionality for module app/api/__init__.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py

```

---

### File: `app/api/v1/__init__.py`

**Purpose**: Project configuration, script, or component file for app/api/v1/__init__.py.

**Functional Overview**: Implements necessary operational functionality for module app/api/v1/__init__.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py

```

---

### File: `app/api/v1/endpoints/__init__.py`

**Purpose**: Project configuration, script, or component file for app/api/v1/endpoints/__init__.py.

**Functional Overview**: Implements necessary operational functionality for module app/api/v1/endpoints/__init__.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py

```

---

### File: `app/api/v1/endpoints/ledger.py`

**Purpose**: Project configuration, script, or component file for app/api/v1/endpoints/ledger.py.

**Functional Overview**: Implements necessary operational functionality for module app/api/v1/endpoints/ledger.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.ledger import AccountCreate, AccountResponse, BalanceResponse, JournalEntryCreate, JournalEntryResponse
from app.services.ledger import LedgerService

router = APIRouter()

@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(account_in: AccountCreate, db: AsyncSession = Depends(get_db)):
    service = LedgerService(db)
    return await service.create_account(account_in)

@router.get("/accounts/{account_id}/balance", response_model=BalanceResponse)
async def get_account_balance(account_id: UUID, db: AsyncSession = Depends(get_db)):
    service = LedgerService(db)
    result = await service.get_account_balance(account_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    account, balance = result
    return BalanceResponse(
        account_id=account.id,
        balance=balance,
        currency=account.currency  # Dynamically returning account's currency
    )

@router.post("/entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    entry_in: JournalEntryCreate,
    idempotency_key: str = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db)
):
    service = LedgerService(db)
    return await service.create_journal_entry(entry_in, idempotency_key=idempotency_key)
```

---

### File: `app/api/v1/endpoints/reconciliation.py`

**Purpose**: Project configuration, script, or component file for app/api/v1/endpoints/reconciliation.py.

**Functional Overview**: Implements necessary operational functionality for module app/api/v1/endpoints/reconciliation.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
# app/api/v1/endpoints/reconciliation.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.reconciliation import ReconciliationService
from app.schemas.reconciliation import (
    ExternalTransactionResponse,
    ManualResolveRequest,
    ReconciliationRunResponse,
)

router = APIRouter()


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_statement(
    source: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Imports an external bank statement CSV feed using Polars."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported."
        )
    
    file_content = await file.read()
    service = ReconciliationService(db)
    imported_count = await service.import_csv_statement(source=source, file_content=file_content)
    
    return {"message": f"Successfully imported {imported_count} external transactions."}


@router.post("/run", response_model=ReconciliationRunResponse)
async def run_reconciliation(db: AsyncSession = Depends(get_db)):
    """Triggers the tiered reconciliation engine (Exact -> Window -> Manual Review)."""
    service = ReconciliationService(db)
    result = await service.run_reconciliation()
    return result


@router.get("/unmatched", response_model=List[ExternalTransactionResponse])
async def get_unmatched_transactions(db: AsyncSession = Depends(get_db)):
    """Retrieves all unmatched and manual review queue external transactions."""
    service = ReconciliationService(db)
    return await service.get_unmatched_transactions()


@router.post("/{transaction_id}/resolve", response_model=ExternalTransactionResponse)
async def resolve_manual_match(
    transaction_id: uuid.UUID,
    body: ManualResolveRequest,
    db: AsyncSession = Depends(get_db)
):
    """Manually maps an external transaction to a specific ledger posting."""
    service = ReconciliationService(db)
    return await service.resolve_manual_match(transaction_id=transaction_id, posting_id=body.posting_id)
```

---

### File: `app/services/__init__.py`

**Purpose**: Project configuration, script, or component file for app/services/__init__.py.

**Functional Overview**: Implements necessary operational functionality for module app/services/__init__.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py

```

---

### File: `app/services/ledger.py`

**Purpose**: Project configuration, script, or component file for app/services/ledger.py.

**Functional Overview**: Implements necessary operational functionality for module app/services/ledger.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
import uuid
from decimal import Decimal
from typing import Optional, Union, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.ledger import Account, JournalEntry, Posting, IdempotencyRecord
from app.schemas.ledger import AccountCreate, JournalEntryCreate
from app.db.redis import redis_client


class LedgerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_account(self, account_data: AccountCreate) -> Account:
        existing = await self.db.execute(
            select(Account).where(Account.name == account_data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account with name '{account_data.name}' already exists."
            )

        account = Account(**account_data.model_dump())
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def _resolve_account(self, account_id_or_name: Union[uuid.UUID, str]) -> Account:
        parsed_uuid = None
        if isinstance(account_id_or_name, uuid.UUID):
            parsed_uuid = account_id_or_name
        elif isinstance(account_id_or_name, str):
            try:
                parsed_uuid = uuid.UUID(account_id_or_name)
            except ValueError:
                pass

        account = None
        if parsed_uuid:
            res = await self.db.execute(
                select(Account).where(Account.id == parsed_uuid)
            )
            account = res.scalar_one_or_none()

        if not account and isinstance(account_id_or_name, str):
            res = await self.db.execute(
                select(Account).where(Account.name == account_id_or_name)
            )
            account = res.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account '{account_id_or_name}' not found."
            )
        return account

    async def get_account_balance(
        self, account_id: Union[uuid.UUID, str]
    ) -> Tuple[Account, Decimal]:
        account = await self._resolve_account(account_id)

        res = await self.db.execute(
            select(Posting).where(Posting.account_id == account.id)
        )
        postings = res.scalars().all()

        debits = Decimal(
            sum(p.amount for p in postings if getattr(p.direction, "value", p.direction) == "DEBIT")
        )
        credits = Decimal(
            sum(p.amount for p in postings if getattr(p.direction, "value", p.direction) == "CREDIT")
        )

        account_type = getattr(account.type, "value", account.type)
        if str(account_type).upper() in ["ASSET", "EXPENSE"]:
            balance_val = debits - credits
        else:
            balance_val = credits - debits

        return account, balance_val

    async def _get_entry_with_postings(self, entry_id: Union[uuid.UUID, str]) -> JournalEntry:
        if isinstance(entry_id, str):
            try:
                entry_id = uuid.UUID(entry_id)
            except ValueError:
                pass

        res = await self.db.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.postings))
            .where(JournalEntry.id == entry_id)
        )
        return res.scalar_one()

    async def create_journal_entry(
        self,
        entry_data: JournalEntryCreate,
        idempotency_key: Optional[str] = None
    ) -> JournalEntry:
        lock_acquired = False
        lock_key = f"lock:idempotency:{idempotency_key}" if idempotency_key else None

        if lock_key:
            lock_acquired = await redis_client.set(lock_key, "locked", nx=True, ex=30)
            if not lock_acquired:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A transaction with this idempotency key is currently being processed."
                )

        try:
            if idempotency_key:
                existing = await self.db.execute(
                    select(IdempotencyRecord).where(
                        IdempotencyRecord.key == idempotency_key
                    )
                )
                record = existing.scalar_one_or_none()
                if record:
                    return await self._get_entry_with_postings(record.journal_entry_id)

            resolved_postings = []
            for posting_data in entry_data.postings:
                account = await self._resolve_account(posting_data.account_id)
                resolved_postings.append((account.id, posting_data))

            journal_entry = JournalEntry(
                description=entry_data.description
            )
            self.db.add(journal_entry)
            await self.db.flush()

            for account_id, posting_data in resolved_postings:
                posting = Posting(
                    journal_entry_id=journal_entry.id,
                    account_id=account_id,
                    amount=posting_data.amount,
                    direction=posting_data.direction
                )
                self.db.add(posting)

            if idempotency_key:
                idempotency_rec = IdempotencyRecord(
                    key=idempotency_key,
                    journal_entry_id=journal_entry.id,
                    status_code=201
                )
                self.db.add(idempotency_rec)

            await self.db.commit()
            return await self._get_entry_with_postings(journal_entry.id)

        finally:
            if lock_key and lock_acquired:
                await redis_client.delete(lock_key)
```

---

### File: `app/services/reconciliation.py`

**Purpose**: Project configuration, script, or component file for app/services/reconciliation.py.

**Functional Overview**: Implements necessary operational functionality for module app/services/reconciliation.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
import io
import uuid
import polars as pl
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.reconciliation import ExternalTransaction, MatchStatus
from app.models.ledger import Posting


class ReconciliationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def import_csv_statement(self, source: str, file_content: bytes) -> int:
        """Parses CSV statement data using Polars and upserts into external_transactions."""
        try:
            df = pl.read_csv(io.BytesIO(file_content))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse CSV file: {str(e)}"
            )

        required_columns = {"external_ref", "amount", "currency", "transaction_date"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns. Expected: {list(required_columns)}"
            )

        count = 0
        for row in df.to_dicts():
            # Check if external_ref already exists
            existing_res = await self.db.execute(
                select(ExternalTransaction).where(ExternalTransaction.external_ref == str(row["external_ref"]))
            )
            if existing_res.scalar_one_or_none():
                continue

            tx_date = row["transaction_date"]
            if isinstance(tx_date, str):
                tx_date = datetime.fromisoformat(tx_date)

            ext_tx = ExternalTransaction(
                source=source,
                external_ref=str(row["external_ref"]),
                amount=Decimal(str(row["amount"])),
                currency=str(row["currency"]),
                transaction_date=tx_date,
                match_status=MatchStatus.UNMATCHED
            )
            self.db.add(ext_tx)
            count += 1

        await self.db.commit()
        return count

    async def run_reconciliation(self) -> dict:
        """Executes Tier 1 (Exact), Tier 2 (Window), and Tier 3 (Manual Review) matching."""
        unmatched_res = await self.db.execute(
            select(ExternalTransaction).where(ExternalTransaction.match_status == MatchStatus.UNMATCHED)
        )
        unmatched_txs = unmatched_res.scalars().all()

        # Get all postings that are not yet matched to any external transaction
        matched_posting_ids = select(ExternalTransaction.matched_posting_id).where(
            ExternalTransaction.matched_posting_id != None
        )
        postings_res = await self.db.execute(
            select(Posting).where(Posting.id.not_in(matched_posting_ids))
        )
        available_postings = postings_res.scalars().all()

        exact_matches = 0
        window_matches = 0
        flagged_for_review = 0

        for ext_tx in unmatched_txs:
            matched_posting = None

            # Tier 1: Exact Match (Amount & Currency match, exact timestamp or reference link if applicable)
            for p in available_postings:
                if p.amount == ext_tx.amount:
                    matched_posting = p
                    break

            if matched_posting:
                ext_tx.match_status = MatchStatus.EXACT_MATCH
                ext_tx.matched_posting_id = matched_posting.id
                available_postings.remove(matched_posting)
                exact_matches += 1
                continue

            # Tier 2: Window Match (Amount matches, within a 3-day date window)
            for p in available_postings:
                if p.amount == ext_tx.amount and p.created_at:
                    delta = abs(p.created_at.replace(tzinfo=None) - ext_tx.transaction_date.replace(tzinfo=None))
                    if delta <= timedelta(days=3):
                        matched_posting = p
                        break

            if matched_posting:
                ext_tx.match_status = MatchStatus.WINDOW_MATCH
                ext_tx.matched_posting_id = matched_posting.id
                available_postings.remove(matched_posting)
                window_matches += 1
                continue

            # Tier 3: Flag for Manual Review
            ext_tx.match_status = MatchStatus.MANUAL_REVIEW
            flagged_for_review += 1

        await self.db.commit()
        return {
            "total_processed": len(unmatched_txs),
            "exact_matches": exact_matches,
            "window_matches": window_matches,
            "flagged_for_review": flagged_for_review
        }

    async def get_unmatched_transactions(self) -> List[ExternalTransaction]:
        res = await self.db.execute(
            select(ExternalTransaction).where(
                ExternalTransaction.match_status.in_([MatchStatus.UNMATCHED, MatchStatus.MANUAL_REVIEW])
            )
        )
        return res.scalars().all()

    async def resolve_manual_match(self, transaction_id: uuid.UUID, posting_id: uuid.UUID) -> ExternalTransaction:
        ext_tx = await self.db.get(ExternalTransaction, transaction_id)
        if not ext_tx:
            raise HTTPException(status_code=404, detail="External transaction not found.")

        posting = await self.db.get(Posting, posting_id)
        if not posting:
            raise HTTPException(status_code=404, detail="Ledger posting not found.")

        ext_tx.matched_posting_id = posting.id
        ext_tx.match_status = MatchStatus.RESOLVED
        await self.db.commit()
        await self.db.refresh(ext_tx)
        return ext_tx
```

---

### File: `tests/conftest.py`

**Purpose**: Project configuration, script, or component file for tests/conftest.py.

**Functional Overview**: Implements necessary operational functionality for module tests/conftest.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
# tests/conftest.py

import asyncio
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# CHANGE 1: Import StaticPool instead of NullPool
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles

from app.db.session import Base, get_db
from app.main import app

# CHANGE 2: Explicitly import models so linters don't remove the import
from app.models.ledger import Account, JournalEntry, Posting, IdempotencyRecord


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(element, compiler, **kw):
    return "JSON"


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# CHANGE 3: Use StaticPool so all sessions share the same in-memory database
engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool, 
)

async_session_test = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_test() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_database():
    """Create tables before each test and drop them afterward."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an asynchronous HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
```

---

### File: `tests/test_concurrency.py`

**Purpose**: Project configuration, script, or component file for tests/test_concurrency.py.

**Functional Overview**: Implements necessary operational functionality for module tests/test_concurrency.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
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
```

---

### File: `tests/test_ledger.py`

**Purpose**: Project configuration, script, or component file for tests/test_ledger.py.

**Functional Overview**: Implements necessary operational functionality for module tests/test_ledger.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
import pytest
from decimal import Decimal
from httpx import AsyncClient
from uuid import uuid4

@pytest.mark.asyncio
async def test_create_account_and_check_balance(async_client: AsyncClient):
    res = await async_client.post("/api/v1/accounts", json={"name": "EUR Bank", "type": "ASSET", "currency": "EUR"})
    assert res.status_code == 201
    account_id = res.json()["id"]
    assert res.json()["currency"] == "EUR"

    bal_res = await async_client.get(f"/api/v1/accounts/{account_id}/balance")
    assert bal_res.status_code == 200
    assert bal_res.json()["currency"] == "EUR"
    assert Decimal(str(bal_res.json()["balance"])) == Decimal("0")

@pytest.mark.asyncio
async def test_idempotent_entry_creation(async_client: AsyncClient):
    acc1 = (await async_client.post("/api/v1/accounts", json={"name": "Cash", "type": "ASSET", "currency": "USD"})).json()["id"]
    acc2 = (await async_client.post("/api/v1/accounts", json={"name": "Revenue", "type": "REVENUE", "currency": "USD"})).json()["id"]

    idempotency_key = str(uuid4())
    payload = {
        "description": "Payment",
        "postings": [
            {"account_id": acc1, "amount": "100.00", "direction": "DEBIT"},
            {"account_id": acc2, "amount": "100.00", "direction": "CREDIT"}
        ]
    }

    res1 = await async_client.post("/api/v1/entries", json=payload, headers={"Idempotency-Key": idempotency_key})
    assert res1.status_code == 201
    entry_id_1 = res1.json()["id"]

    res2 = await async_client.post("/api/v1/entries", json=payload, headers={"Idempotency-Key": idempotency_key})
    assert res2.status_code == 201
    entry_id_2 = res2.json()["id"]

    assert entry_id_1 == entry_id_2
```

---

### File: `tests/test_reconciliation.py`

**Purpose**: Project configuration, script, or component file for tests/test_reconciliation.py.

**Functional Overview**: Implements necessary operational functionality for module tests/test_reconciliation.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_import_and_reconciliation_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Sample CSV content for bank statement import
        csv_data = (
            "external_ref,amount,currency,transaction_date\n"
            "EXT-1001,150.00,USD,2026-06-01T12:00:00\n"
            "EXT-1002,500.00,USD,2026-06-02T12:00:00\n"
        )
        
        response = await ac.post(
            "/api/v1/reconciliation/import",
            params={"source": "stripe"},
            files={"file": ("statement.csv", csv_data.encode("utf-8"), "text/csv")}
        )
        assert response.status_code == 201
        assert "Successfully imported 2 external transactions" in response.json()["message"]

        # Run reconciliation
        run_res = await ac.post("/api/v1/reconciliation/run")
        assert run_res.status_code == 200
        data = run_res.json()
        assert data["total_processed"] == 2

        # Check unmatched / review queue
        unmatched_res = await ac.get("/api/v1/reconciliation/unmatched")
        assert unmatched_res.status_code == 200
        assert isinstance(unmatched_res.json(), list)
```

---

### File: `scripts/scan_and_document.py`

**Purpose**: Project configuration, script, or component file for scripts/scan_and_document.py.

**Functional Overview**: Implements necessary operational functionality for module scripts/scan_and_document.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
#!/usr/bin/env python3
"""LedgerFlow Codebase Scanner and Master Documentation Generator."""

import os
from pathlib import Path


class LedgerFlowDocGenerator:

  def __init__(self, root_dir: str = "."):
    self.root_dir = Path(root_dir).resolve()
    self.ignored_dirs = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        ".pytest_cache",
        ".idea",
        ".vscode",
        "build",
        "dist",
    }
    self.ignored_files = {".DS_Store", "repository_structure.png"}
    self.docs_output_path = (
        self.root_dir / "docs" / "PROJECT_COMPLETE_DOCUMENTATION.md"
    )

  def scan_and_generate(self):
    """Scans repository and outputs the master markdown documentation."""
    files_data = []

    for current_root, dirs, files in os.walk(self.root_dir):
      dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
      rel_root = Path(current_root).relative_to(self.root_dir)

      for file in sorted(files):
        if file in self.ignored_files or file.endswith(".pyc"):
          continue
        file_path = Path(current_root) / file
        rel_path = str(file_path.relative_to(self.root_dir))

        if rel_path == "docs/PROJECT_COMPLETE_DOCUMENTATION.md":
          continue

        files_data.append(self._process_file(file_path, rel_path))

    self._write_markdown(files_data)
    print(
        f"Master documentation successfully generated at: {self.docs_output_path}"
    )

  def _process_file(self, file_path: Path, rel_path: str) -> dict:
    """Reads file contents and extracts metadata."""
    try:
      with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    except Exception as e:
      content = f"# Error reading file: {e}"

    purpose, explanation, connections = self._get_file_metadata(rel_path)

    return {
        "path": rel_path,
        "extension": file_path.suffix.lstrip("."),
        "purpose": purpose,
        "content": content,
        "explanation": explanation,
        "connections": connections,
    }

  def _get_file_metadata(self, path: str) -> tuple[str, str, str]:
    """Provides architectural context per file."""
    metadata = {
        "src/app/main.py": (
            "FastAPI application entrypoint, middleware, lifespan management,"
            " and router mounting.",
            (
                "Initializes the FastAPI ASGI application, configures CORS"
                " middleware, defines the health check endpoint `/health`, and"
                " mounts the V1 API router."
            ),
            (
                "Imports `api_router` from `app.api.v1.router` and exports `app`"
                " for Uvicorn/Gunicorn execution."
            ),
        ),
        "src/app/api/v1/router.py": (
            "Central router aggregator for API version 1.",
            (
                "Aggregates modular endpoint routers under a single `APIRouter`"
                " instance to decouple endpoint implementation from main app"
                " initialization."
            ),
            (
                "Imports `ledger.router` from `app.api.v1.endpoints.ledger` and"
                " is consumed by `app.main`."
            ),
        ),
        "src/app/api/v1/endpoints/ledger.py": (
            "REST API endpoint handlers for double-entry ledger operations.",
            (
                "Exposes endpoints to create accounts, query balances, and"
                " post journal entries. Handles request deserialization,"
                " dependency injection, and maps domain errors to HTTP"
                " status codes."
            ),
            (
                "Uses schemas from `app.schemas.ledger`, session generators"
                " from `app.db.session`, and service logic from"
                " `app.services.ledger_service`."
            ),
        ),
        "src/app/services/ledger_service.py": (
            "Core accounting engine implementing business logic, zero-sum"
            " verification, and row locks.",
            (
                "Validates zero-sum entry invariant (Debits = Credits),"
                " checks Redis for duplicate idempotency keys, acquires"
                " `SELECT ... FOR UPDATE` row locks in PostgreSQL, and records"
                " journal postings within an explicit transaction."
            ),
            (
                "Called by endpoint handlers in"
                " `app.api.v1.endpoints.ledger`. Interacts with `app.models.ledger`"
                " and database sessions."
            ),
        ),
        "src/app/schemas/ledger.py": (
            "Pydantic validation models and Data Transfer Objects (DTOs).",
            (
                "Enforces structural validation for accounts, postings, and"
                " journal entries. Ensures posting amounts are strictly"
                " positive and side directions match CREDIT or DEBIT."
            ),
            (
                "Used across API endpoints (`app.api.v1.endpoints.ledger`) for"
                " request body parsing and response serialization."
            ),
        ),
        "src/app/models/ledger.py": (
            "SQLAlchemy ORM models defining database tables and relationships.",
            (
                "Defines `Account`, `JournalEntry`, and `Posting` relational"
                " tables. Establishes foreign key constraints, composite"
                " indices for balance scanning, and relationship cascading."
            ),
            (
                "Inherits from `Base` in `app.db.base` and queried by"
                " `app.services.ledger_service`."
            ),
        ),
        "src/app/db/session.py": (
            "Async Database engine creation and session factory setup.",
            (
                "Creates an AsyncEngine using `asyncpg` and constructs an"
                " `async_sessionmaker` for context management and FastAPI"
                " dependency injection."
            ),
            (
                "Reads `DATABASE_URL` from `app.core.config` and provides"
                " session instances to API routes and service modules."
            ),
        ),
        "src/app/core/config.py": (
            "Application settings and environment variable parser.",
            (
                "Uses Pydantic BaseSettings to read `DATABASE_URL`, `REDIS_URL`,"
                " and runtime options from environment variables with fallback"
                " defaults."
            ),
            (
                "Imported by `app.db.session`, database connection harnesses,"
                " and test utilities."
            ),
        ),
    }

    default_meta = (
        f"Project configuration, script, or component file for {path}.",
        f"Implements necessary operational functionality for module {path}.",
        "Integrates into the LedgerFlow build, testing, or execution pipeline.",
    )
    return metadata.get(path, default_meta)

  def _write_markdown(self, files_data: list[dict]):
    """Renders the master markdown file."""
    self.docs_output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(self.docs_output_path, "w", encoding="utf-8") as f:
      f.write("# LedgerFlow — Complete Project Master Documentation\n\n")

      f.write("## SECTION A — PROJECT OVERVIEW\n\n")
      f.write(
          "LedgerFlow is an enterprise-grade financial accounting engine"
          " implementing a double-entry journal system. It is engineered with"
          " Python, FastAPI, AsyncSQLAlchemy, PostgreSQL, and Redis to solve"
          " real-time balance drift and race conditions during high-volume"
          " transaction processing.\n\n"
      )

      f.write("### Key Architectural Invariants\n")
      f.write(
          "1. **Zero-Sum Entry Constraint**: Every journal transaction must"
          " satisfy sum(Debits) == sum(Credits).\n"
      )
      f.write(
          "2. **Pessimistic Concurrency**: Prevents race conditions using"
          " PostgreSQL `SELECT ... FOR UPDATE` row locks on target account"
          " records.\n"
      )
      f.write(
          "3. **Idempotent Execution**: Redis key storage prevents duplicate"
          " journal posting upon client network retries.\n\n"
      )

      f.write("## SECTION B — REPOSITORY FILE INDEX & DIRECTORY TREE\n\n")
      f.write("```text\nLedgerFlow/\n")
      for file_info in files_data:
        f.write(f"├── {file_info['path']}\n")
      f.write("```\n\n")

      f.write("## SECTION C — COMPLETE SOURCE CODE & MODULE REFERENCE\n\n")

      for file_info in files_data:
        f.write(f"### File: `{file_info['path']}`\n\n")
        f.write(f"**Purpose**: {file_info['purpose']}\n\n")
        f.write(
            f"**Functional Overview**: {file_info['explanation']}\n\n"
        )
        f.write(
            "**Module Interconnections**:"
            f" {file_info['connections']}\n\n"
        )
        f.write("**Complete File Source Code**:\n\n")

        ext = file_info["extension"] if file_info["extension"] else "text"
        f.write(f"```{ext}\n")
        f.write(file_info["content"])
        if not file_info["content"].endswith("\n"):
          f.write("\n")
        f.write("```\n\n")
        f.write("---\n\n")


if __name__ == "__main__":
  generator = LedgerFlowDocGenerator()
  generator.scan_and_generate()
```

---

### File: `.github/workflows/ci.yml`

**Purpose**: Project configuration, script, or component file for .github/workflows/ci.yml.

**Functional Overview**: Implements necessary operational functionality for module .github/workflows/ci.yml.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```yml
name: LedgerFlow CI Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    name: Run Test Suite
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: ledger_user
          POSTGRES_PASSWORD: ledger_password
          POSTGRES_DB: ledgerflow_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Check out repository code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Pytest suite
        env:
          DATABASE_URL: postgresql+asyncpg://ledger_user:ledger_password@localhost:5432/ledgerflow_test
          REDIS_URL: redis://localhost:6379/0
        run: |
          pytest -v

  docker-build:
    name: Verify Container Build
    runs-on: ubuntu-latest
    needs: test

    steps:
      - name: Check out repository code
        uses: actions/checkout@v4

      - name: Build Docker Image
        run: |
          docker build -t ledgerflow-api:ci .
```

---

### File: `alembic/README`

**Purpose**: Project configuration, script, or component file for alembic/README.

**Functional Overview**: Implements necessary operational functionality for module alembic/README.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```text
Generic single-database configuration with an async dbapi.
```

---

### File: `alembic/env.py`

**Purpose**: Project configuration, script, or component file for alembic/env.py.

**Functional Overview**: Implements necessary operational functionality for module alembic/env.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 1. Import application settings and Base model
from app.core.config import settings
from app.db.session import Base
# Import models so Alembic registers them on Base.metadata
import app.models.ledger  # noqa: F401

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata

# Inject database URL from pydantic settings dynamically
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

### File: `alembic/script.py.mako`

**Purpose**: Project configuration, script, or component file for alembic/script.py.mako.

**Functional Overview**: Implements necessary operational functionality for module alembic/script.py.mako.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade schema."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Downgrade schema."""
    ${downgrades if downgrades else "pass"}
```

---

### File: `alembic/versions/67a7b755039d_add_journal_entry_id_to_idempotency_.py`

**Purpose**: Project configuration, script, or component file for alembic/versions/67a7b755039d_add_journal_entry_id_to_idempotency_.py.

**Functional Overview**: Implements necessary operational functionality for module alembic/versions/67a7b755039d_add_journal_entry_id_to_idempotency_.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
"""add_journal_entry_id_to_idempotency_records

Revision ID: 67a7b755039d
Revises: 7bb8fd203663
Create Date: 2026-08-29 15:40:39.934464

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '67a7b755039d'
down_revision: Union[str, Sequence[str], None] = '7bb8fd203663'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('accounts', 'name',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=255),
               existing_nullable=False)
    op.alter_column('accounts', 'type',
               existing_type=postgresql.ENUM('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE', name='accounttype'),
               type_=sa.String(length=50),
               existing_nullable=False)
    op.add_column('idempotency_records', sa.Column('id', sa.UUID(), nullable=False))
    op.add_column('idempotency_records', sa.Column('journal_entry_id', sa.UUID(), nullable=True))
    op.alter_column('idempotency_records', 'response_payload',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               type_=sa.String(),
               nullable=True)
    op.alter_column('idempotency_records', 'status_code',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_index(op.f('ix_idempotency_records_key'), 'idempotency_records', ['key'], unique=True)
    op.create_foreign_key(None, 'idempotency_records', 'journal_entries', ['journal_entry_id'], ['id'], ondelete='SET NULL')
    op.drop_index(op.f('ix_journal_entries_idempotency_key'), table_name='journal_entries')
    op.drop_column('journal_entries', 'idempotency_key')
    op.alter_column('postings', 'direction',
               existing_type=postgresql.ENUM('DEBIT', 'CREDIT', name='direction'),
               type_=sa.String(length=6),
               existing_nullable=False)
    op.drop_index(op.f('idx_posting_account_created'), table_name='postings')
    op.drop_index(op.f('ix_postings_account_id'), table_name='postings')
    op.drop_index(op.f('ix_postings_journal_entry_id'), table_name='postings')
    op.drop_constraint(op.f('postings_journal_entry_id_fkey'), 'postings', type_='foreignkey')
    op.create_foreign_key(None, 'postings', 'journal_entries', ['journal_entry_id'], ['id'], ondelete='CASCADE')
    op.drop_column('postings', 'created_at')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('postings', sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'postings', type_='foreignkey')
    op.create_foreign_key(op.f('postings_journal_entry_id_fkey'), 'postings', 'journal_entries', ['journal_entry_id'], ['id'])
    op.create_index(op.f('ix_postings_journal_entry_id'), 'postings', ['journal_entry_id'], unique=False)
    op.create_index(op.f('ix_postings_account_id'), 'postings', ['account_id'], unique=False)
    op.create_index(op.f('idx_posting_account_created'), 'postings', ['account_id', 'created_at'], unique=False)
    op.alter_column('postings', 'direction',
               existing_type=sa.String(length=6),
               type_=postgresql.ENUM('DEBIT', 'CREDIT', name='direction'),
               existing_nullable=False)
    op.add_column('journal_entries', sa.Column('idempotency_key', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.create_index(op.f('ix_journal_entries_idempotency_key'), 'journal_entries', ['idempotency_key'], unique=True)
    op.drop_constraint(None, 'idempotency_records', type_='foreignkey')
    op.drop_index(op.f('ix_idempotency_records_key'), table_name='idempotency_records')
    op.alter_column('idempotency_records', 'status_code',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('idempotency_records', 'response_payload',
               existing_type=sa.String(),
               type_=postgresql.JSONB(astext_type=sa.Text()),
               nullable=False)
    op.drop_column('idempotency_records', 'journal_entry_id')
    op.drop_column('idempotency_records', 'id')
    op.alter_column('accounts', 'type',
               existing_type=sa.String(length=50),
               type_=postgresql.ENUM('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE', name='accounttype'),
               existing_nullable=False)
    op.alter_column('accounts', 'name',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)
    # ### end Alembic commands ###
```

---

### File: `alembic/versions/7bb8fd203663_create_initial_ledger_tables.py`

**Purpose**: Project configuration, script, or component file for alembic/versions/7bb8fd203663_create_initial_ledger_tables.py.

**Functional Overview**: Implements necessary operational functionality for module alembic/versions/7bb8fd203663_create_initial_ledger_tables.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
"""create_initial_ledger_tables

Revision ID: 7bb8fd203663
Revises: 
Create Date: 2026-08-03 16:22:15.157479

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7bb8fd203663'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accounts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('type', sa.Enum('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE', name='accounttype'), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('idempotency_records',
    sa.Column('key', sa.String(length=255), nullable=False),
    sa.Column('response_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('status_code', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('key')
    )
    op.create_table('journal_entries',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('idempotency_key', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_journal_entries_idempotency_key'), 'journal_entries', ['idempotency_key'], unique=True)
    op.create_table('postings',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('journal_entry_id', sa.UUID(), nullable=False),
    sa.Column('account_id', sa.UUID(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=18, scale=4), nullable=False),
    sa.Column('direction', sa.Enum('DEBIT', 'CREDIT', name='direction'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('amount > 0', name='check_positive_amount'),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
    sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_posting_account_created', 'postings', ['account_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_postings_account_id'), 'postings', ['account_id'], unique=False)
    op.create_index(op.f('ix_postings_journal_entry_id'), 'postings', ['journal_entry_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_postings_journal_entry_id'), table_name='postings')
    op.drop_index(op.f('ix_postings_account_id'), table_name='postings')
    op.drop_index('idx_posting_account_created', table_name='postings')
    op.drop_table('postings')
    op.drop_index(op.f('ix_journal_entries_idempotency_key'), table_name='journal_entries')
    op.drop_table('journal_entries')
    op.drop_table('idempotency_records')
    op.drop_table('accounts')
    # ### end Alembic commands ###
```

---

### File: `alembic/versions/7e439f48f1f1_add_external_transactions_table_for_.py`

**Purpose**: Project configuration, script, or component file for alembic/versions/7e439f48f1f1_add_external_transactions_table_for_.py.

**Functional Overview**: Implements necessary operational functionality for module alembic/versions/7e439f48f1f1_add_external_transactions_table_for_.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
"""Add external_transactions table for reconciliation

Revision ID: 7e439f48f1f1
Revises: dfc16bb48d9f
Create Date: 2026-08-29 16:58:05.441741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7e439f48f1f1'
down_revision: Union[str, Sequence[str], None] = 'dfc16bb48d9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('accounts', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.alter_column('idempotency_records', 'status_code',
               existing_type=sa.INTEGER(),
               type_=sa.Numeric(precision=3, scale=0),
               nullable=False)
    op.alter_column('idempotency_records', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.drop_constraint(op.f('idempotency_records_journal_entry_id_fkey'), 'idempotency_records', type_='foreignkey')
    op.create_foreign_key(None, 'idempotency_records', 'journal_entries', ['journal_entry_id'], ['id'])
    op.drop_column('idempotency_records', 'response_payload')
    op.alter_column('journal_entries', 'description',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=500),
               existing_nullable=False)
    op.alter_column('journal_entries', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.add_column('postings', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
    op.alter_column('postings', 'direction',
               existing_type=sa.VARCHAR(length=6),
               type_=sa.String(length=10),
               existing_nullable=False)
    op.create_index('ix_postings_journal_entry_id', 'postings', ['journal_entry_id'], unique=False)
    op.drop_constraint(op.f('postings_journal_entry_id_fkey'), 'postings', type_='foreignkey')
    op.create_foreign_key(None, 'postings', 'journal_entries', ['journal_entry_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'postings', type_='foreignkey')
    op.create_foreign_key(op.f('postings_journal_entry_id_fkey'), 'postings', 'journal_entries', ['journal_entry_id'], ['id'], ondelete='CASCADE')
    op.drop_index('ix_postings_journal_entry_id', table_name='postings')
    op.alter_column('postings', 'direction',
               existing_type=sa.String(length=10),
               type_=sa.VARCHAR(length=6),
               existing_nullable=False)
    op.drop_column('postings', 'created_at')
    op.alter_column('journal_entries', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    op.alter_column('journal_entries', 'description',
               existing_type=sa.String(length=500),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
    op.add_column('idempotency_records', sa.Column('response_payload', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'idempotency_records', type_='foreignkey')
    op.create_foreign_key(op.f('idempotency_records_journal_entry_id_fkey'), 'idempotency_records', 'journal_entries', ['journal_entry_id'], ['id'], ondelete='SET NULL')
    op.alter_column('idempotency_records', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    op.alter_column('idempotency_records', 'status_code',
               existing_type=sa.Numeric(precision=3, scale=0),
               type_=sa.INTEGER(),
               nullable=True)
    op.alter_column('accounts', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    # ### end Alembic commands ###
```

---

### File: `alembic/versions/dfc16bb48d9f_restore_posting_account_created_index.py`

**Purpose**: Project configuration, script, or component file for alembic/versions/dfc16bb48d9f_restore_posting_account_created_index.py.

**Functional Overview**: Implements necessary operational functionality for module alembic/versions/dfc16bb48d9f_restore_posting_account_created_index.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
"""restore_posting_account_created_index

Revision ID: dfc16bb48d9f
Revises: f2c0064de257
Create Date: 2026-08-29 16:44:32.305118

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'dfc16bb48d9f'
down_revision = 'f2c0064de257'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        'ix_postings_account_direction',
        'postings',
        ['account_id', 'direction'],
        unique=False,
        if_not_exists=True
    )


def downgrade() -> None:
    op.drop_index('ix_postings_account_direction', table_name='postings', if_exists=True)
```

---

### File: `alembic/versions/f2c0064de257_add_zero_sum_balance_trigger.py`

**Purpose**: Project configuration, script, or component file for alembic/versions/f2c0064de257_add_zero_sum_balance_trigger.py.

**Functional Overview**: Implements necessary operational functionality for module alembic/versions/f2c0064de257_add_zero_sum_balance_trigger.py.

**Module Interconnections**: Integrates into the LedgerFlow build, testing, or execution pipeline.

**Complete File Source Code**:

```py
"""add_zero_sum_balance_trigger

Revision ID: f2c0064de257
Revises: 67a7b755039d
Create Date: 2026-08-29 16:41:58.153564

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f2c0064de257'
down_revision = '67a7b755039d'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create function to check debit/credit balance equality per journal entry
    op.execute("""
    CREATE OR REPLACE FUNCTION check_journal_entry_balance()
    RETURNS TRIGGER AS $$
    DECLARE
        v_debit_sum NUMERIC(20, 4);
        v_credit_sum NUMERIC(20, 4);
        v_entry_id UUID;
    BEGIN
        v_entry_id := COALESCE(NEW.journal_entry_id, OLD.journal_entry_id);

        SELECT 
            COALESCE(SUM(CASE WHEN direction = 'DEBIT' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN direction = 'CREDIT' THEN amount ELSE 0 END), 0)
        INTO v_debit_sum, v_credit_sum
        FROM postings
        WHERE journal_entry_id = v_entry_id;

        IF v_debit_sum <> v_credit_sum THEN
            RAISE EXCEPTION 'Double-entry violation: Total DEBIT (%) does not equal total CREDIT (%) for journal entry %',
                v_debit_sum, v_credit_sum, v_entry_id;
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # 2. Create constraint trigger deferred until transaction COMMIT
    op.execute("""
    CREATE CONSTRAINT TRIGGER trigger_check_journal_entry_balance
    AFTER INSERT OR UPDATE OR DELETE ON postings
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW
    EXECUTE FUNCTION check_journal_entry_balance();
    """)

def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trigger_check_journal_entry_balance ON postings;")
    op.execute("DROP FUNCTION IF EXISTS check_journal_entry_balance();")
```

---

