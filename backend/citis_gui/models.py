from __future__ import annotations
from datetime import datetime
from uuid import uuid4
from sqlmodel import SQLModel, Field


def _uuid() -> str:
    return uuid4().hex


class AppState(SQLModel, table=True):
    """Single row (id=1) holding master credentials + vault salt."""
    id: int = Field(default=1, primary_key=True)
    master_hash: str
    vault_salt: bytes
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Server(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    name: str
    host: str
    port: int = 22
    username: str = "root"
    auth_kind: str = "password"          # "password" | "key"
    secret_blob: bytes                    # Fernet-encrypted password or private key
    jump_server_id: str | None = None     # self-referential
    agent_python: str = "python3"
    agent_dir: str = "/opt/citis-ovpnpackage"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Alias(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    ip: str
    alias: str
    scope: str = "global"                 # "global" or "server:<id>"
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SessionRow(SQLModel, table=True):
    """Persisted login tokens ('remember me')."""
    token: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime