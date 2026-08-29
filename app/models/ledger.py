import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, CheckConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    currency = Column(String(3), nullable=False, default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    postings = relationship("Posting", back_populates="account")

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    postings = relationship("Posting", back_populates="journal_entry", cascade="all, delete-orphan")
    idempotency_record = relationship("IdempotencyRecord", back_populates="journal_entry", uselist=False)

class Posting(Base):
    __tablename__ = "postings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    amount = Column(Numeric(18, 4), nullable=False)
    direction = Column(String(6), nullable=False)  # DEBIT, CREDIT

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_positive_amount"),
    )

    journal_entry = relationship("JournalEntry", back_populates="postings")
    account = relationship("Account", back_populates="postings")

class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(255), unique=True, index=True, nullable=False)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True)
    response_payload = Column(String, nullable=True)
    status_code = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    journal_entry = relationship("JournalEntry", back_populates="idempotency_record")