import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Text,
    ForeignKey,
    String,
    UniqueConstraint,   
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Explanation(Base):
    __tablename__ = "explanations"

    __table_args__ = (
        UniqueConstraint(
            "explanation_key",
            "version",
            name="uq_explanations_key_version",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    risk_assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("risk_assessments.id"),
        nullable=True,
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    model: Mapped[str] = mapped_column(Text, nullable=False)
    
    prompt_version: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    explanation_key: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    incident_id: Mapped[UUID] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
    )

    incident: Mapped["Incident"] = relationship(
        "Incident",
        back_populates="explanations",
    )


