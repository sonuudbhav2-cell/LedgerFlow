# PROJECT COMPLETE DOCUMENTATION

This document contains the complete source code, repository structure, file explanations, and component interconnections for the project.

## Repository Structure

```text
LedgerFlow/
├── alembic/
│   ├── versions/
│   │   └── 7bb8fd203663_create_initial_ledger_tables.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   └── ledger.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── ledger.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── ledger.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── ledger.py
│   ├── __init__.py
│   └── main.py
├── pipelines/
├── scripts/
│   └── generate_docs.py
├── tests/
│   ├── conftest.py
│   └── test_ledger.py
├── .env
├── .gitignore
├── alembic.ini
├── docker-compose.yml
└── requirements.txt
```

---

# .env

## Purpose
Local environment variables configuration file.

## Complete Code
```text
PROJECT_NAME="LedgerFlow"
ENVIRONMENT="development"
DATABASE_URL="postgresql+asyncpg://ledger_user:ledger_password@localhost:5432/ledgerflow"
REDIS_URL="redis://localhost:6379/0"

```

## Code Explanation
Contains key-value pairs for secret keys, environment modes, and local database connection strings.

## Project Connections
Read automatically by `app/core/config.py` during application boot.

---

# .gitignore

## Purpose
Utility, script, or configuration file supporting `.gitignore` functionality.

## Complete Code
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

## Code Explanation
Contains definitions or settings required for `.gitignore`.

## Project Connections
Integrated into the project repository structure.

---

# alembic/README

## Purpose
Utility, script, or configuration file supporting `alembic/README` functionality.

## Complete Code
```text
Generic single-database configuration with an async dbapi.
```

## Code Explanation
Contains definitions or settings required for `README`.

## Project Connections
Integrated into the project repository structure.

---

# alembic/env.py

## Purpose
Utility, script, or configuration file supporting `alembic/env.py` functionality.

## Complete Code
```python
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

## Code Explanation
Contains definitions or settings required for `env.py`.

## Project Connections
Integrated into the project repository structure.

---

# alembic/script.py.mako

## Purpose
Utility, script, or configuration file supporting `alembic/script.py.mako` functionality.

## Complete Code
```text
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

## Code Explanation
Contains definitions or settings required for `script.py.mako`.

## Project Connections
Integrated into the project repository structure.

---

# alembic/versions/7bb8fd203663_create_initial_ledger_tables.py

## Purpose
Utility, script, or configuration file supporting `alembic/versions/7bb8fd203663_create_initial_ledger_tables.py` functionality.

## Complete Code
```python
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

## Code Explanation
Contains definitions or settings required for `7bb8fd203663_create_initial_ledger_tables.py`.

## Project Connections
Integrated into the project repository structure.

---

# alembic.ini

## Purpose
Utility, script, or configuration file supporting `alembic.ini` functionality.

## Complete Code
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

## Code Explanation
Contains definitions or settings required for `alembic.ini`.

## Project Connections
Integrated into the project repository structure.

---

# app/__init__.py

## Purpose
Utility, script, or configuration file supporting `app/__init__.py` functionality.

## Complete Code
```python

```

## Code Explanation
Contains definitions or settings required for `__init__.py`.

## Project Connections
Integrated into the project repository structure.

---

# app/api/__init__.py

## Purpose
Utility, script, or configuration file supporting `app/api/__init__.py` functionality.

## Complete Code
```python

```

## Code Explanation
Contains definitions or settings required for `__init__.py`.

## Project Connections
Integrated into the project repository structure.

---

# app/api/v1/__init__.py

## Purpose
Utility, script, or configuration file supporting `app/api/v1/__init__.py` functionality.

## Complete Code
```python

```

## Code Explanation
Contains definitions or settings required for `__init__.py`.

## Project Connections
Integrated into the project repository structure.

---

# app/api/v1/endpoints/__init__.py

## Purpose
Utility, script, or configuration file supporting `app/api/v1/endpoints/__init__.py` functionality.

## Complete Code
```python

```

## Code Explanation
Contains definitions or settings required for `__init__.py`.

## Project Connections
Integrated into the project repository structure.

---

# app/api/v1/endpoints/ledger.py

## Purpose
FastAPI router exposing RESTful HTTP endpoints for ledger operations.

## Complete Code
```python
# app/api/v1/endpoints/ledger.py

from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.ledger import (
    AccountCreate,
    AccountResponse,
    JournalEntryCreate,
    JournalEntryResponse,
    TrialBalanceResponse,
)
from app.services.ledger import LedgerService

router = APIRouter()


@router.post(
    "/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_account(
    account_in: AccountCreate,
    db: AsyncSession = Depends(get_db)
):
    return await LedgerService.create_account(db, account_in)


@router.get(
    "/accounts/{account_id}/balance",
)
async def get_account_balance(
    account_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    try:
        balance = await LedgerService.get_account_balance(db, account_id)
        return {
            "account_id": account_id,
            "balance": balance,
            "currency": "USD"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/journal-entries",
    response_model=JournalEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_journal_entry(
    entry_in: JournalEntryCreate,
    idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await LedgerService.create_journal_entry(db, entry_in, idempotency_key)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/reports/trial-balance",
    response_model=TrialBalanceResponse,
)
async def get_trial_balance(
    db: AsyncSession = Depends(get_db)
):
    try:
        return await LedgerService.get_trial_balance(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trial Balance Error: {str(e)}"
        )
```

## Code Explanation
Maps HTTP routes (`POST /accounts`, `POST /journal-entries`, `GET /accounts/{id}/balance`) to service functions, handles dependency injection via `get_db`, and returns serialized responses.

## Project Connections
Included in `app/main.py`. Connects incoming client HTTP requests to `app/services/ledger.py` and validates inputs with `app/schemas/ledger.py`.

---

# app/core/__init__.py

## Purpose
Utility, script, or configuration file supporting `app/core/__init__.py` functionality.

## Complete Code
```python

```

## Code Explanation
Contains definitions or settings required for `__init__.py`.

## Project Connections
Integrated into the project repository structure.

---

# app/core/config.py

## Purpose
Centralized application configuration and environment variables parser.

## Complete Code
```python
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

## Code Explanation
Uses Pydantic `BaseSettings` to load and validate environment variables such as `DATABASE_URL`, `PROJECT_NAME`, and runtime flags.

## Project Connections
Loaded by `app/main.py` and `app/db/session.py` to configure system-wide database connections and application meta settings.

---

# app/db/__init__.py

## Purpose
Utility, script, or configuration file supporting `app/db/__init__.py` functionality.

## Complete Code
```python

```

## Code Explanation
Contains definitions or settings required for `__init__.py`.

## Project Connections
Integrated into the project repository structure.

---

# app/db/session.py

## Purpose
Database configuration layer managing async engine initialization and session management.

## Complete Code
```python
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

## Code Explanation
Creates an asynchronous SQLAlchemy engine using `create_async_engine`, defines `AsyncSessionLocal` for transactional database sessions, establishes `Base` declarative model parent, and exposes the `get_db` async generator dependency.

## Project Connections
Utilized across all model definitions (`app/models/ledger.py`) and injected into FastAPI route dependencies.

---

# app/main.py

## Purpose
Entry point for the FastAPI application. Sets up global error handlers, route controllers, and health checks.

## Complete Code
```python
# app/main.py

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import ledger
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    description="High-Throughput Financial Ledger Engine built with FastAPI, SQLAlchemy, and PostgreSQL."
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},  # Ensure string conversion here too if needed
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},  # <--- CRITICAL: wrap exc in str()
    )

app.include_router(
    ledger.router,
    prefix="/api/v1",
    tags=["Ledger"]
)

@app.get("/", summary="Root Endpoint")
def read_root():
    return {
        "project": "LedgerFlow API",
        "version": "1.0.0",
        "documentation": "/docs"
    }
```

## Code Explanation
Instantiates the `FastAPI` application, configures custom exception handlers to convert `RequestValidationError` and `ValueError` into standard `400 Bad Request` responses, and mounts the v1 API routes.

## Project Connections
Mounts routers from `app/api/v1/endpoints/ledger.py` and uses global settings from `app/core/config.py`.

---

# app/models/__init__.py

## Purpose
Utility, script, or configuration file supporting `app/models/__init__.py` functionality.

## Complete Code
```python

```

## Code Explanation
Contains definitions or settings required for `__init__.py`.

## Project Connections
Integrated into the project repository structure.

---

# app/models/ledger.py

## Purpose
SQLAlchemy ORM domain models defining the double-entry accounting database schema.

## Complete Code
```python
import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import String, DateTime, ForeignKey, Numeric, Enum as SQLEnum, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

# Account Categories based on Standard Accounting Rules
class AccountType(str, enum.Enum):
    ASSET = "ASSET"         # e.g., Cash reserves
    LIABILITY = "LIABILITY" # e.g., Deposits owed back to users
    EQUITY = "EQUITY"       # e.g., Capital
    REVENUE = "REVENUE"     # e.g., Platform fee income
    EXPENSE = "EXPENSE"     # e.g., Server hosting costs

class Direction(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[AccountType] = mapped_column(SQLEnum(AccountType), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationship to postings
    postings: Mapped[List["Posting"]] = relationship("Posting", back_populates="account")

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # 1-to-Many Relationship: One JournalEntry contains Multiple Postings
    postings: Mapped[List["Posting"]] = relationship("Posting", back_populates="journal_entry", cascade="all, delete-orphan")

class Posting(Base):
    __tablename__ = "postings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False, index=True)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True)
    
    # Numeric(18, 4) guarantees exact decimal money calculations
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=4), nullable=False)
    direction: Mapped[Direction] = mapped_column(SQLEnum(Direction), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Reverse Relationships
    journal_entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="postings")
    account: Mapped["Account"] = relationship("Account", back_populates="postings")

    __table_args__ = (
        # Ensure positive numbers only
        CheckConstraint("amount > 0", name="check_positive_amount"),
        # Index for fast balance calculations
        Index("idx_posting_account_created", "account_id", "created_at"),
    )

class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    response_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status_code: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

## Code Explanation
Defines relational tables: `Account`, `JournalEntry`, `Posting`, and `IdempotencyRecord`. Implements strict numeric precision `Numeric(18, 4)` for financial math, check constraints (`amount > 0`), database indexes, and foreign key relationships.

## Project Connections
Inherits from `Base` in `app/db/session.py`. Used by `app/services/ledger.py` for DB queries and referenced by Pydantic schemas in `app/schemas/ledger.py`.

---

# app/schemas/__init__.py

## Purpose
Utility, script, or configuration file supporting `app/schemas/__init__.py` functionality.

## Complete Code
```python

```

## Code Explanation
Contains definitions or settings required for `__init__.py`.

## Project Connections
Integrated into the project repository structure.

---

# app/schemas/ledger.py

## Purpose
Pydantic models for request validation, data serialization, and response formatting.

## Complete Code
```python
# app/schemas/ledger.py

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class PostingDirection(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: AccountType
    currency: str = Field(default="USD", min_length=3, max_length=3)


class AccountCreate(AccountBase):
    pass


class AccountResponse(AccountBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostingCreate(BaseModel):
    account_id: UUID
    amount: Decimal = Field(..., gt=0, decimal_places=4)
    direction: PostingDirection


class PostingResponse(PostingCreate):
    id: UUID
    journal_entry_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JournalEntryCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    postings: List[PostingCreate]

    @model_validator(mode="after")
    def validate_double_entry_balance(self) -> "JournalEntryCreate":
        if len(self.postings) < 2:
            raise ValueError("A journal entry must contain at least two postings.")

        total_debits = Decimal("0.0000")
        total_credits = Decimal("0.0000")

        has_debit = False
        has_credit = False

        for posting in self.postings:
            if posting.direction == PostingDirection.DEBIT:
                total_debits += posting.amount
                has_debit = True
            elif posting.direction == PostingDirection.CREDIT:
                total_credits += posting.amount
                has_credit = True

        if not (has_debit and has_credit):
            raise ValueError("A journal entry must contain at least one DEBIT and one CREDIT posting.")

        if total_debits != total_credits:
            raise ValueError(
                f"Unbalanced journal entry: Total DEBITs ({total_debits}) "
                f"must equal Total CREDITs ({total_credits})."
            )

        return self


class JournalEntryResponse(BaseModel):
    id: UUID
    description: str
    idempotency_key: Optional[str] = None
    created_at: datetime
    postings: List[PostingResponse]

    model_config = ConfigDict(from_attributes=True)


class AccountTrialBalanceItem(BaseModel):
    account_id: UUID
    name: str
    type: str
    balance: Decimal


class TrialBalanceResponse(BaseModel):
    accounts: List[AccountTrialBalanceItem]
    total_system_debits: Decimal
    total_system_credits: Decimal
    is_balanced: bool
```

## Code Explanation
Validates API payloads for creating accounts, postings, and journal entries. Guarantees field-level constraints such as valid currency codes, account types, debit/credit directions, and non-negative numbers.

## Project Connections
Acts as the input validation layer between HTTP client payloads in `app/api/v1/endpoints/ledger.py` and service operations in `app/services/ledger.py`.

---

# app/services/__init__.py

## Purpose
Utility, script, or configuration file supporting `app/services/__init__.py` functionality.

## Complete Code
```python

```

## Code Explanation
Contains definitions or settings required for `__init__.py`.

## Project Connections
Integrated into the project repository structure.

---

# app/services/ledger.py

## Purpose
Business logic and service layer enforcing financial rules and double-entry invariants.

## Complete Code
```python
# app/services/ledger.py

from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ledger import Account, IdempotencyRecord, JournalEntry, Posting
from app.schemas.ledger import AccountCreate, AccountType, JournalEntryCreate, PostingDirection


class LedgerService:

    @staticmethod
    async def create_account(session: AsyncSession, account_in: AccountCreate) -> Account:
        """Creates a new financial account."""
        account = Account(
            name=account_in.name,
            type=account_in.type.value,
            currency=account_in.currency,
        )
        session.add(account)
        await session.commit()
        await session.refresh(account)
        return account

    @staticmethod
    async def get_account(session: AsyncSession, account_id: UUID) -> Optional[Account]:
        """Fetches an account by its unique UUID."""
        result = await session.execute(select(Account).where(Account.id == account_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_account_balance(session: AsyncSession, account_id: UUID) -> Decimal:
        """Calculates live balance using normal balance rules with safe type normalization."""
        account = await LedgerService.get_account(session, account_id)
        if not account:
            raise ValueError(f"Account with ID '{account_id}' does not exist.")

        debit_stmt = select(func.coalesce(func.sum(Posting.amount), Decimal("0.0000"))).where(
            Posting.account_id == account_id,
            Posting.direction == PostingDirection.DEBIT.value
        )
        debit_res = await session.execute(debit_stmt)
        total_debits = debit_res.scalar_one() or Decimal("0.0000")

        credit_stmt = select(func.coalesce(func.sum(Posting.amount), Decimal("0.0000"))).where(
            Posting.account_id == account_id,
            Posting.direction == PostingDirection.CREDIT.value
        )
        credit_res = await session.execute(credit_stmt)
        total_credits = credit_res.scalar_one() or Decimal("0.0000")

        acc_type = account.type.value if hasattr(account.type, "value") else str(account.type)

        if acc_type in [AccountType.ASSET.value, AccountType.EXPENSE.value]:
            return total_debits - total_credits
        else:
            return total_credits - total_debits

    @staticmethod
    async def create_journal_entry(
        session: AsyncSession,
        entry_in: JournalEntryCreate,
        idempotency_key: Optional[str] = None
    ) -> JournalEntry:
        """Executes an Atomic Double-Entry Transaction with idempotency checks."""
        if idempotency_key:
            stmt = select(IdempotencyRecord).where(IdempotencyRecord.key == idempotency_key)
            res = await session.execute(stmt)
            existing_record = res.scalar_one_or_none()

            if existing_record:
                entry_stmt = (
                    select(JournalEntry)
                    .options(selectinload(JournalEntry.postings))
                    .where(JournalEntry.id == existing_record.journal_entry_id)
                )
                entry_res = await session.execute(entry_stmt)
                return entry_res.scalar_one()

        async with session.begin_nested():
            account_ids = {posting.account_id for posting in entry_in.postings}
            acc_stmt = select(Account.id).where(Account.id.in_(account_ids))
            acc_res = await session.execute(acc_stmt)
            found_ids = set(acc_res.scalars().all())

            if len(found_ids) != len(account_ids):
                missing = account_ids - found_ids
                raise ValueError(f"Transaction rejected. Account IDs do not exist: {missing}")

            journal_entry = JournalEntry(
                description=entry_in.description,
                idempotency_key=idempotency_key
            )
            session.add(journal_entry)
            await session.flush()

            for posting_in in entry_in.postings:
                posting = Posting(
                    journal_entry_id=journal_entry.id,
                    account_id=posting_in.account_id,
                    amount=posting_in.amount,
                    direction=posting_in.direction.value
                )
                session.add(posting)

            if idempotency_key:
                idempotency_rec = IdempotencyRecord(
                    key=idempotency_key,
                    journal_entry_id=journal_entry.id
                )
                session.add(idempotency_rec)

        await session.commit()

        final_stmt = (
            select(JournalEntry)
            .options(selectinload(JournalEntry.postings))
            .where(JournalEntry.id == journal_entry.id)
        )
        final_res = await session.execute(final_stmt)
        return final_res.scalar_one()

    @staticmethod
    async def get_trial_balance(session: AsyncSession) -> dict:
        """Generates a system-wide Trial Balance report and verifies total balance equality."""
        acc_result = await session.execute(select(Account))
        accounts = acc_result.scalars().all()

        account_items = []
        for acc in accounts:
            balance = await LedgerService.get_account_balance(session, acc.id)
            acc_type = acc.type.value if hasattr(acc.type, "value") else str(acc.type)
            account_items.append({
                "account_id": acc.id,
                "name": acc.name,
                "type": acc_type,
                "balance": balance
            })

        total_debits_stmt = select(func.coalesce(func.sum(Posting.amount), Decimal("0.0000"))).where(
            Posting.direction == PostingDirection.DEBIT.value
        )
        total_debits_res = await session.execute(total_debits_stmt)
        total_system_debits = total_debits_res.scalar_one() or Decimal("0.0000")

        total_credits_stmt = select(func.coalesce(func.sum(Posting.amount), Decimal("0.0000"))).where(
            Posting.direction == PostingDirection.CREDIT.value
        )
        total_credits_res = await session.execute(total_credits_stmt)
        total_system_credits = total_credits_res.scalar_one() or Decimal("0.0000")

        is_balanced = (total_system_debits == total_system_credits)

        return {
            "accounts": account_items,
            "total_system_debits": total_system_debits,
            "total_system_credits": total_system_credits,
            "is_balanced": is_balanced
        }

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ledger import JournalEntry, Posting, Direction
from app.schemas.ledger import JournalEntryCreate

async def create_journal_entry(db: AsyncSession, payload: JournalEntryCreate) -> JournalEntry:
    # 1. Calculate total debits and credits
    total_debits = sum(p.amount for p in payload.postings if p.direction == Direction.DEBIT)
    total_credits = sum(p.amount for p in payload.postings if p.direction == Direction.CREDIT)

    # 2. Enforce double-entry invariant (Debits must equal Credits)
    if total_debits != total_credits:
        raise HTTPException(
            status_code=400,
            detail=f"Unbalanced journal entry: Debits ({total_debits}) must equal Credits ({total_credits})."
        )

    # 3. Proceed with saving the journal entry and postings...
    db_entry = JournalEntry(
        description=payload.description,
        idempotency_key=payload.idempotency_key,
    )
    
    for posting_data in payload.postings:
        db_entry.postings.append(
            Posting(
                account_id=posting_data.account_id,
                amount=posting_data.amount,
                direction=posting_data.direction,
            )
        )

    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)
    return db_entry
```

## Code Explanation
Contains transactional workflow logic for creating ledger accounts, verifying that total debits equal total credits prior to committing journal entries, handling idempotency locks, and querying balance rollups.

## Project Connections
Called directly by endpoints in `app/api/v1/endpoints/ledger.py`. Interacts directly with database models in `app/models/ledger.py` via `AsyncSession`.

---

# docker-compose.yml

## Purpose
Container orchestration file for local development services.

## Complete Code
```yaml
version: '3.8'

services:
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

volumes:
  postgres_data:
  redis_data:
```

## Code Explanation
Spins up local PostgreSQL database instances with health checks and persistent volume storage.

## Project Connections
Provides the database environment specified by settings in `.env` and `app/core/config.py`.

---

# requirements.txt

## Purpose
Project dependency lockfile.

## Complete Code
```text
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

## Code Explanation
Lists all third-party Python packages required to run the project, including FastAPI, uvicorn, SQLAlchemy, aiosqlite, asyncpg, pydantic, and pytest.

## Project Connections
Used by pip, Docker container builds, and virtual environment installation setups.

---

# scripts/generate_docs.py

## Purpose
Utility, script, or configuration file supporting `scripts/generate_docs.py` functionality.

## Complete Code
```python
# scripts/generate_docs.py

import os
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration: Directories and files to exclude from scanning
EXCLUDE_DIRS = {
    ".venv", "venv", "env", "__pycache__", ".git", 
    ".pytest_cache", ".idea", ".vscode", "build", "dist", ".mypy_cache"
}

EXCLUDE_FILES = {
    ".DS_Store", "PROJECT_COMPLETE_DOCUMENTATION.md", "*.pyc", "*.pyo"
}

# File extension language mapping for Markdown code blocks
LANGUAGE_MAP = {
    ".py": "python",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".json": "json",
    ".ini": "ini",
    ".env": "bash",
    ".sh": "bash",
    ".md": "markdown",
    ".sql": "sql",
    ".txt": "text",
}

# Pre-populated metadata for core project files
FILE_METADATA = {
    "app/main.py": {
        "purpose": "Entry point for the FastAPI application. Sets up global error handlers, route controllers, and health checks.",
        "explanation": "Instantiates the `FastAPI` application, configures custom exception handlers to convert `RequestValidationError` and `ValueError` into standard `400 Bad Request` responses, and mounts the v1 API routes.",
        "connections": "Mounts routers from `app/api/v1/endpoints/ledger.py` and uses global settings from `app/core/config.py`."
    },
    "app/db/session.py": {
        "purpose": "Database configuration layer managing async engine initialization and session management.",
        "explanation": "Creates an asynchronous SQLAlchemy engine using `create_async_engine`, defines `AsyncSessionLocal` for transactional database sessions, establishes `Base` declarative model parent, and exposes the `get_db` async generator dependency.",
        "connections": "Utilized across all model definitions (`app/models/ledger.py`) and injected into FastAPI route dependencies."
    },
    "app/models/ledger.py": {
        "purpose": "SQLAlchemy ORM domain models defining the double-entry accounting database schema.",
        "explanation": "Defines relational tables: `Account`, `JournalEntry`, `Posting`, and `IdempotencyRecord`. Implements strict numeric precision `Numeric(18, 4)` for financial math, check constraints (`amount > 0`), database indexes, and foreign key relationships.",
        "connections": "Inherits from `Base` in `app/db/session.py`. Used by `app/services/ledger.py` for DB queries and referenced by Pydantic schemas in `app/schemas/ledger.py`."
    },
    "app/schemas/ledger.py": {
        "purpose": "Pydantic models for request validation, data serialization, and response formatting.",
        "explanation": "Validates API payloads for creating accounts, postings, and journal entries. Guarantees field-level constraints such as valid currency codes, account types, debit/credit directions, and non-negative numbers.",
        "connections": "Acts as the input validation layer between HTTP client payloads in `app/api/v1/endpoints/ledger.py` and service operations in `app/services/ledger.py`."
    },
    "app/services/ledger.py": {
        "purpose": "Business logic and service layer enforcing financial rules and double-entry invariants.",
        "explanation": "Contains transactional workflow logic for creating ledger accounts, verifying that total debits equal total credits prior to committing journal entries, handling idempotency locks, and querying balance rollups.",
        "connections": "Called directly by endpoints in `app/api/v1/endpoints/ledger.py`. Interacts directly with database models in `app/models/ledger.py` via `AsyncSession`."
    },
    "app/api/v1/endpoints/ledger.py": {
        "purpose": "FastAPI router exposing RESTful HTTP endpoints for ledger operations.",
        "explanation": "Maps HTTP routes (`POST /accounts`, `POST /journal-entries`, `GET /accounts/{id}/balance`) to service functions, handles dependency injection via `get_db`, and returns serialized responses.",
        "connections": "Included in `app/main.py`. Connects incoming client HTTP requests to `app/services/ledger.py` and validates inputs with `app/schemas/ledger.py`."
    },
    "app/core/config.py": {
        "purpose": "Centralized application configuration and environment variables parser.",
        "explanation": "Uses Pydantic `BaseSettings` to load and validate environment variables such as `DATABASE_URL`, `PROJECT_NAME`, and runtime flags.",
        "connections": "Loaded by `app/main.py` and `app/db/session.py` to configure system-wide database connections and application meta settings."
    },
    "tests/conftest.py": {
        "purpose": "Pytest configuration suite and shared test fixtures.",
        "explanation": "Configures an isolated in-memory SQLite database (`sqlite+aiosqlite:///:memory:`) using SQLAlchemy `StaticPool`, sets up PostgreSQL-to-SQLite `JSONB` compilation rules, overrides `get_db` dependency, and exposes an `async_client` fixture.",
        "connections": "Overrides database dependencies in `app/main.py` and loads ORM schemas from `app/models/ledger.py` for testing execution."
    },
    "tests/test_ledger.py": {
        "purpose": "Automated integration and unit test suite for ledger endpoints and business logic.",
        "explanation": "Tests core account creation, valid journal entry lifecycles, idempotency enforcement, and rejects unbalanced double-entry transactions with expected HTTP status codes.",
        "connections": "Executes against `app/main.py` endpoints using fixtures defined in `tests/conftest.py`."
    },
    "docker-compose.yml": {
        "purpose": "Container orchestration file for local development services.",
        "explanation": "Spins up local PostgreSQL database instances with health checks and persistent volume storage.",
        "connections": "Provides the database environment specified by settings in `.env` and `app/core/config.py`."
    },
    "requirements.txt": {
        "purpose": "Project dependency lockfile.",
        "explanation": "Lists all third-party Python packages required to run the project, including FastAPI, uvicorn, SQLAlchemy, aiosqlite, asyncpg, pydantic, and pytest.",
        "connections": "Used by pip, Docker container builds, and virtual environment installation setups."
    },
    ".env": {
        "purpose": "Local environment variables configuration file.",
        "explanation": "Contains key-value pairs for secret keys, environment modes, and local database connection strings.",
        "connections": "Read automatically by `app/core/config.py` during application boot."
    }
}


def is_excluded(path: Path) -> bool:
    """Check if a path or file should be excluded from scanning."""
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    if path.name in EXCLUDE_FILES:
        return True
    return False


def build_tree_structure(root_dir: Path, prefix: str = "") -> str:
    """Generates a hierarchical tree representation of the repository."""
    lines = []
    contents = sorted([p for p in root_dir.iterdir() if not is_excluded(p)], key=lambda x: (x.is_file(), x.name.lower()))
    
    pointers = ["├── "] * (len(contents) - 1) + ["└── "] if contents else []
    
    for pointer, path in zip(pointers, contents):
        if path.is_dir():
            lines.append(f"{prefix}{pointer}{path.name}/")
            extension = "│   " if pointer == "├── " else "    "
            lines.append(build_tree_structure(path, prefix=prefix + extension))
        else:
            lines.append(f"{prefix}{pointer}{path.name}")
            
    return "\n".join(filter(None, lines))


def scan_files(root_dir: Path) -> List[Tuple[str, Path]]:
    """Recursively retrieves all non-excluded project files."""
    file_list = []
    for path in sorted(root_dir.rglob("*")):
        if path.is_file() and not is_excluded(path):
            rel_path = path.relative_to(root_dir).as_posix()
            file_list.append((rel_path, path))
    return file_list


def generate_documentation():
    """Generates the complete PROJECT_COMPLETE_DOCUMENTATION.md markdown file."""
    root_dir = Path.cwd()
    output_filename = "PROJECT_COMPLETE_DOCUMENTATION.md"
    
    print(f"Scanning project directory: {root_dir}")
    
    # 1. Build project tree
    tree_str = f"{root_dir.name}/\n" + build_tree_structure(root_dir)
    
    # 2. Collect all files
    files = scan_files(root_dir)
    
    doc_content = []
    doc_content.append("# PROJECT COMPLETE DOCUMENTATION\n")
    doc_content.append("This document contains the complete source code, repository structure, file explanations, and component interconnections for the project.\n")
    doc_content.append("## Repository Structure\n")
    doc_content.append("```text")
    doc_content.append(tree_str)
    doc_content.append("```\n")
    doc_content.append("---\n")
    
    # 3. Process each file
    for rel_path, file_path in files:
        print(f"Processing: {rel_path}")
        
        # Determine language for markdown code block
        lang = LANGUAGE_MAP.get(file_path.suffix, "text")
        
        # Retrieve content
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            content = f"[Unreadable or Binary File: {str(e)}]"
            
        # Get metadata from lookup or generate fallback
        meta = FILE_METADATA.get(rel_path, {
            "purpose": f"Utility, script, or configuration file supporting `{rel_path}` functionality.",
            "explanation": f"Contains definitions or settings required for `{file_path.name}`.",
            "connections": "Integrated into the project repository structure."
        })
        
        doc_content.append(f"# {rel_path}\n")
        doc_content.append("## Purpose")
        doc_content.append(f"{meta['purpose']}\n")
        
        doc_content.append("## Complete Code")
        doc_content.append(f"```{lang}")
        doc_content.append(content)
        doc_content.append("```\n")
        
        doc_content.append("## Code Explanation")
        doc_content.append(f"{meta['explanation']}\n")
        
        doc_content.append("## Project Connections")
        doc_content.append(f"{meta['connections']}\n")
        
        doc_content.append("---\n")
        
    # Write output to file
    output_path = root_dir / output_filename
    output_path.write_text("\n".join(doc_content), encoding="utf-8")
    
    print(f"\nDocumentation successfully generated at: {output_path}")

if __name__ == "__main__":
    generate_documentation()
```

## Code Explanation
Contains definitions or settings required for `generate_docs.py`.

## Project Connections
Integrated into the project repository structure.

---

# tests/conftest.py

## Purpose
Pytest configuration suite and shared test fixtures.

## Complete Code
```python
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

## Code Explanation
Configures an isolated in-memory SQLite database (`sqlite+aiosqlite:///:memory:`) using SQLAlchemy `StaticPool`, sets up PostgreSQL-to-SQLite `JSONB` compilation rules, overrides `get_db` dependency, and exposes an `async_client` fixture.

## Project Connections
Overrides database dependencies in `app/main.py` and loads ORM schemas from `app/models/ledger.py` for testing execution.

---

# tests/test_ledger.py

## Purpose
Automated integration and unit test suite for ledger endpoints and business logic.

## Complete Code
```python
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_account(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/accounts",
        json={"name": "Test Asset", "type": "ASSET", "currency": "USD"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Asset"
    assert data["type"] == "ASSET"
    assert "id" in data


@pytest.mark.anyio
async def test_journal_entry_lifecycle(async_client: AsyncClient):
    # 1. Create Asset Account
    acc1_res = await async_client.post(
        "/api/v1/accounts",
        json={"name": "Checking", "type": "ASSET", "currency": "USD"}
    )
    acc1_id = acc1_res.json()["id"]

    # 2. Create Revenue Account
    acc2_res = await async_client.post(
        "/api/v1/accounts",
        json={"name": "Revenue", "type": "REVENUE", "currency": "USD"}
    )
    acc2_id = acc2_res.json()["id"]

    # 3. Post Balanced Transaction
    je_res = await async_client.post(
        "/api/v1/journal-entries",
        json={
            "description": "Client Payment",
            "postings": [
                {"account_id": acc1_id, "amount": "500.0000", "direction": "DEBIT"},
                {"account_id": acc2_id, "amount": "500.0000", "direction": "CREDIT"}
            ]
        }
    )
    assert je_res.status_code == 201
    je_data = je_res.json()
    assert len(je_data["postings"]) == 2

    # 4. Verify Trial Balance
    tb_res = await async_client.get("/api/v1/reports/trial-balance")
    assert tb_res.status_code == 200
    tb_data = tb_res.json()
    assert tb_data["is_balanced"] is True
    assert tb_data["total_system_debits"] == "500.0000"
    assert tb_data["total_system_credits"] == "500.0000"


@pytest.mark.anyio
async def test_unbalanced_journal_entry_rejection(async_client: AsyncClient):
    acc1_res = await async_client.post(
        "/api/v1/accounts",
        json={"name": "Checking", "type": "ASSET", "currency": "USD"}
    )
    acc1_id = acc1_res.json()["id"]

    acc2_res = await async_client.post(
        "/api/v1/accounts",
        json={"name": "Revenue", "type": "REVENUE", "currency": "USD"}
    )
    acc2_id = acc2_res.json()["id"]

    # Post Unbalanced Transaction (Debits != Credits)
    je_res = await async_client.post(
        "/api/v1/journal-entries",
        json={
            "description": "Unbalanced Entry",
            "postings": [
                {"account_id": acc1_id, "amount": "500.0000", "direction": "DEBIT"},
                {"account_id": acc2_id, "amount": "300.0000", "direction": "CREDIT"}
            ]
        }
    )
    assert je_res.status_code == 400
```

## Code Explanation
Tests core account creation, valid journal entry lifecycles, idempotency enforcement, and rejects unbalanced double-entry transactions with expected HTTP status codes.

## Project Connections
Executes against `app/main.py` endpoints using fixtures defined in `tests/conftest.py`.

---
