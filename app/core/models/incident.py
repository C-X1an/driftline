import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id"),
        nullable=False,
    )

    # Deterministic hash of semantic drift
    drift_fingerprint: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    baseline_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("snapshots.id"),
        nullable=False,
    )

    origin: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="RUNTIME",  # INITIAL | RUNTIME
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="OPEN",  # OPEN | ACKED | RESOLVED
        index=True,
    )

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    )

    current_risk_level: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    current_magnitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    explanation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("explanations.id"),
        nullable=True,
    )
