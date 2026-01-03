from app.db.session import SessionLocal
from app.core.models import Snapshot

db = SessionLocal()

snaps = (
    db.query(Snapshot)
    .filter(Snapshot.source_id == "751cb0db-ed76-4bf4-87b6-e670c5d58341")
    .order_by(Snapshot.captured_at.desc())
    .limit(2)
    .all()
)

for s in snaps:
    print(s.id, s.captured_at, s.normalized_state)
