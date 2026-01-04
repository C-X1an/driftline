from sqlalchemy.orm import Session
from app.core.models import Explanation

def explanation_stats(db: Session):
    total = db.query(Explanation).count()

    return {
        "total_explanations": total,
    }
