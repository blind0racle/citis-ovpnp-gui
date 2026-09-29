from __future__ import annotations
from datetime import datetime
from fastapi import Cookie, HTTPException, Depends, status
from sqlmodel import Session, select
from .db import get_session
from .models import SessionRow
from .config import SESSION_COOKIE


def current_user(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    db: Session = Depends(get_session),
) -> None:
    if not session_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not authenticated")
    row = db.get(SessionRow, session_token)
    if not row or row.expires_at < datetime.utcnow():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "session expired")