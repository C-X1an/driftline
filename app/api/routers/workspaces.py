from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.models import Workspace

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("/")
def create_workspace(
    payload: dict,
    db: Session = Depends(get_db),
):
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="name is required")

    workspace = Workspace(name=name)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    return {
        "id": str(workspace.id),
        "name": workspace.name,
        "created_at": workspace.created_at,
    }


@router.get("/")
def list_workspaces(db: Session = Depends(get_db)):
    workspaces = db.query(Workspace).all()

    return [
        {
            "id": str(w.id),
            "name": w.name,
            "created_at": w.created_at,
        }
        for w in workspaces
    ]
