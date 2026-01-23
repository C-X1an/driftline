import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base

# 🔥 IMPORTANT: import ALL models so metadata is registered
from app.core.models.org import Org
from app.core.models.incident import Incident
from app.core.models.snapshot import Snapshot
from app.core.models.explanation import Explanation
from app.core.models.usage_event import UsageEvent
from app.core.models.drift_signal import DriftSignal
from app.core.models.risk_assessment import RiskAssessment


@pytest.fixture(scope="function")
def db():
    engine = create_engine("sqlite:///:memory:", echo=False)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )

    # ✅ now ALL tables exist
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
