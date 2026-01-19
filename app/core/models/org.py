import uuid
from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from app.db.base import Base

if TYPE_CHECKING:
    from app.core.models.source import Source
    from app.core.models.incident import Incident


class Org(Base):
    __tablename__ = "orgs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(String, nullable=False)

    plan: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="FREE",  # FREE | PRO | ENTERPRISE
    )

    sources: Mapped[list["Source"]] = relationship(
        "Source",
        back_populates="org",
        cascade="all, delete-orphan",
    )

    incidents: Mapped[list["Incident"]] = relationship(
        "Incident",
        back_populates="org",
        cascade="all, delete-orphan",
    )
