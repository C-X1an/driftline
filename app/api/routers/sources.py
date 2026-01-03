from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.models import Source

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("")
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).all()

    return [
        {
            "id": str(source.id),
            "name": source.name,
            "type": source.type,
            "active": source.active,
        }
        for source in sources
    ]
