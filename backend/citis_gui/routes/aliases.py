from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from ..db import get_session
from ..deps import current_user
from ..models import Alias

router = APIRouter(prefix="/api/aliases", tags=["aliases"],
                   dependencies=[Depends(current_user)])


class AliasIn(BaseModel):
    ip: str
    alias: str
    scope: str = "global"
    notes: str | None = None


@router.get("")
def list_(db: Session = Depends(get_session)):
    return db.exec(select(Alias)).all()


@router.post("")
def create(body: AliasIn, db: Session = Depends(get_session)):
    a = Alias(**body.model_dump())
    db.add(a); db.commit(); db.refresh(a)
    return a


@router.put("/{aid}")
def update(aid: str, body: AliasIn, db: Session = Depends(get_session)):
    a = db.get(Alias, aid)
    if not a:
        raise HTTPException(404, "not found")
    for k, v in body.model_dump().items():
        setattr(a, k, v)
    db.add(a); db.commit(); db.refresh(a)
    return a


@router.delete("/{aid}")
def delete(aid: str, db: Session = Depends(get_session)):
    a = db.get(Alias, aid)
    if not a:
        raise HTTPException(404, "not found")
    db.delete(a); db.commit()
    return {"ok": True}