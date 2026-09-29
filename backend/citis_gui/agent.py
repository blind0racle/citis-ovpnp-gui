from __future__ import annotations
import asyncio, shlex
from .models import Server
from .ssh_pool import SSHPool


class AgentError(RuntimeError):
    def __init__(self, cmd: str, rc: int, stderr: str):
        super().__init__(f"{cmd} exited {rc}: {stderr.strip()}")
        self.cmd, self.rc, self.stderr = cmd, rc, stderr


class AgentAdapter:
    """Runs the remote covpn_*.py scripts over an existing SSH connection."""

    def __init__(self, pool: SSHPool, db):
        self.pool = pool
        self.db = db

    async def _run(self, server: Server, script: str, *args: str) -> str:
        conn = await self.pool.get(self.db, server)
        cmd = " ".join(
            [shlex.quote(server.agent_python),
             shlex.quote(f"{server.agent_dir}/{script}")]
            + [shlex.quote(a) for a in args]
        )
        proc = await conn.run(cmd, check=False)
        if proc.exit_status != 0:
            raise AgentError(cmd, proc.exit_status or -1, proc.stderr or "")
        return proc.stdout or ""

    # ---- high-level wrappers -------------------------------------------------

    async def version(self, server: Server) -> str:
        return (await self._run(server, "covpn.py", "--version")).strip()

    async def info(self, server: Server) -> str:
        return await self._run(server, "covpn_info.py")

    async def list_users(self, server: Server) -> list[str]:
        out = await self._run(server, "covpn_info.py", "--users")
        return [l.strip() for l in out.splitlines() if l.strip()]

    async def add_user(self, server: Server, name: str) -> str:
        return await self._run(server, "covpn_add.py", name)

    async def remove_user(self, server: Server, name: str) -> str:
        # adjust to your real script/flag
        return await self._run(server, "covpn_add.py", "--remove", name)