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