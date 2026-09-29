from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from ..db import get_session
from ..deps import current_user
from ..models import Server
from ..security import encrypt
from ..ssh_pool import get_pool
from ..agent import AgentAdapter
from .auth import vault_key

router = APIRouter(prefix="/api/servers", tags=["servers"],
                   dependencies=[Depends(current_user)])


class ServerIn(BaseModel):
    name: str
    host: str
    port: int = 22
    username: str = "root"
    auth_kind: str = "password"     # "password" | "key"
    secret: str
    jump_server_id: str | None = None
    agent_python: str = "python3"
    agent_dir: str = "/opt/citis-ovpnpackage"


def _public(s: Server) -> dict:
    return {
        "id": s.id, "name": s.name, "host": s.host, "port": s.port,
        "username": s.username, "auth_kind": s.auth_kind,
        "jump_server_id": s.jump_server_id,
        "agent_python": s.agent_python, "agent_dir": s.agent_dir,
    }


@router.get("")
def list_servers(db: Session = Depends(get_session)):
    return [_public(s) for s in db.exec(select(Server)).all()]


@router.post("")
def create(body: ServerIn, db: Session = Depends(get_session)):
    s = Server(
        name=body.name, host=body.host, port=body.port,
        username=body.username, auth_kind=body.auth_kind,
        jump_server_id=body.jump_server_id,
        agent_python=body.agent_python, agent_dir=body.agent_dir,
        secret_blob=encrypt(vault_key(), body.secret),
    )
    db.add(s); db.commit(); db.refresh(s)
    return _public(s)


@router.delete("/{sid}")
def delete(sid: str, db: Session = Depends(get_session)):
    s = db.get(Server, sid)
    if not s:
        raise HTTPException(404, "not found")
    db.delete(s); db.commit()
    return {"ok": True}


@router.post("/{sid}/test")
async def test(sid: str, db: Session = Depends(get_session)):
    s = db.get(Server, sid)
    if not s:
        raise HTTPException(404, "not found")
    try:
        ver = await AgentAdapter(get_pool(), db).version(s)
        return {"ok": True, "agent_version": ver}
    except Exception as e:
        return {"ok": False, "error": str(e)}