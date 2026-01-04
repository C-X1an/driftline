from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.metrics.explanations import explanation_stats

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")  # ← THIS IS THE MISSING PIECE
def metrics_root(db: Session = Depends(get_db)):
    return explanation_stats(db)


@router.get("/explanations")
def explanation_metrics(db: Session = Depends(get_db)):
    return explanation_stats(db)
