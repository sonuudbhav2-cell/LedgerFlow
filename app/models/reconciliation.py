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