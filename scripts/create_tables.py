from app.db.session import engine
from app.db.base import Base

from app.core.models import (
    Workspace,
    Source,
    Snapshot,
    SnapshotError,
    DriftSignal,
    RiskAssessment,
    Explanation,
    Incident,
)

def main():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    main()
