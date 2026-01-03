import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DriftSignal(Base):
    __tablename__ = "drift_signals"

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

    baseline_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("snapshots.id"),
        nullable=False,
    )

    current_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("snapshots.id"),
        nullable=False,
    )

    component_count: Mapped[int] = mapped_column(Integer, nullable=False)
    magnitude: Mapped[float] = mapped_column(Float, nullable=False)

    components: Mapped[list] = mapped_column(JSONB, nullable=False)

    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    risk_assessments = relationship(
        "RiskAssessment",
        back_populates="drift_signal",
    )
