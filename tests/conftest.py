import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base  # adjust if your Base import path differs


@pytest.fixture(scope="function")
def db():
    """
    Provides a clean, isolated database session for each test.
    Uses in-memory SQLite for speed and determinism.
    """

    engine = create_engine("sqlite:///:memory:", echo=False)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
