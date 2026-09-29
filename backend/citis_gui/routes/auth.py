from __future__ import annotations
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlmodel import Session, select
from ..db import get_session
from ..models import AppState, SessionRow
from ..security import (
    hash_master, verify_master, derive_vault_key, new_salt, new_token,
)
from ..config import SESSION_COOKIE

router = APIRouter(prefix="/api/auth", tags=["auth"])

# in-memory vault key for the running session (single-user, local app)
_VAULT_KEY: bytes | None = None


def vault_key() -> bytes:
    if _VAULT_KEY is None:
        raise HTTPException(401, "vault locked")
    return _VAULT_KEY


def set_vault_key(k: bytes | None) -> None:
    global _VAULT_KEY
    _VAULT_KEY = k


class SetupBody(BaseModel):
    password: str


class LoginBody(BaseModel):
    password: str
    remember: bool = False


@router.get("/status")
def status_(db: Session = Depends(get_session)):
    return {
        "initialised": db.get(AppState, 1) is not None,
        "unlocked": _VAULT_KEY is not None,
    }


@router.post("/setup")
def setup(body: SetupBody, db: Session = Depends(get_session)):
    if db.get(AppState, 1) is not None:
        raise HTTPException(400, "already initialised")
    salt = new_salt()
    db.add(AppState(master_hash=hash_master(body.password), vault_salt=salt))
    db.commit()
    set_vault_key(derive_vault_key(body.password, salt))
    return {"ok": True}


@router.post("/login")
def login(body: LoginBody, response: Response, db: Session = Depends(get_session)):
    st = db.get(AppState, 1)
    if not st or not verify_master(body.password, st.master_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad password")

    set_vault_key(derive_vault_key(body.password, st.vault_salt))

    if body.remember:
        tok = new_token()
        db.add(SessionRow(
            token=tok,
            expires_at=datetime.utcnow() + timedelta(days=30),
        ))
        db.commit()
        response.set_cookie(
            SESSION_COOKIE, tok, httponly=True, samesite="lax", max_age=30 * 86400,
        )
    return {"ok": True}


@router.post("/logout")
def logout(response: Response, db: Session = Depends(get_session)):
    set_vault_key(None)
    response.delete_cookie(SESSION_COOKIE)
    return {"ok": True}