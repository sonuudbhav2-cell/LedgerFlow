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