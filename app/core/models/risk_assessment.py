import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.core.models.drift_signal import DriftSignal



class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    drift_signal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("drift_signals.id"),
        nullable=False,
    )

    drift_signal = relationship(
        "DriftSignal",
        back_populates="risk_assessments",
    )


    risk_level: Mapped[str] = mapped_column(String, nullable=False)
    magnitude: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
