from __future__ import annotations
import asyncio
from typing import Optional
import asyncssh
from sqlmodel import Session
from .models import Server
from .security import decrypt


class SSHPool:
    """One live asyncssh connection per server, created lazily."""

    def __init__(self, vault_key: bytes):
        self.vault_key = vault_key
        self._conns: dict[str, asyncssh.SSHClientConnection] = {}
        self._lock = asyncio.Lock()

    async def get(self, db: Session, server: Server) -> asyncssh.SSHClientConnection:
        async with self._lock:
            conn = self._conns.get(server.id)
            if conn is not None and not conn.is_closed():
                return conn
            conn = await self._open(db, server)
            self._conns[server.id] = conn
            return conn

    async def _open(self, db: Session, server: Server) -> asyncssh.SSHClientConnection:
        secret = decrypt(self.vault_key, server.secret_blob)

        kwargs: dict = dict(
            host=server.host,
            port=server.port,
            username=server.username,
            known_hosts=None,
            keepalive_interval=30,
        )
        if server.auth_kind == "password":
            kwargs["password"] = secret
        else:
            kwargs["client_keys"] = [asyncssh.import_private_key(secret)]

        if server.jump_server_id:
            jump = db.get(Server, server.jump_server_id)
            if not jump:
                raise RuntimeError(f"jump server {server.jump_server_id} missing")
            jump_conn = await self._open(db, jump)   # recursive, works for chains
            kwargs["tunnel"] = jump_conn

        return await asyncssh.connect(**kwargs)

    async def close(self, server_id: str) -> None:
        conn = self._conns.pop(server_id, None)
        if conn and not conn.is_closed():
            conn.close()
            await conn.wait_closed()

    async def close_all(self) -> None:
        for sid in list(self._conns):
            await self.close(sid)


_pool: Optional[SSHPool] = None


def set_pool(pool: SSHPool) -> None:
    global _pool
    _pool = pool


def get_pool() -> SSHPool:
    if _pool is None:
        raise RuntimeError("ssh pool not initialised")
    return _pool