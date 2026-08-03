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