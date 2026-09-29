from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import FRONTEND_DIST
from .db import init_db
from .ssh_pool import SSHPool, set_pool
from .routes import auth, servers, aliases, terminal


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # vault key is set on /login; pool rebuilds lazily
    set_pool(SSHPool(vault_key=b"\0" * 44))   # placeholder, replaced on login
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="citis-ovpnp-gui", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth.router)
    app.include_router(servers.router)
    app.include_router(aliases.router)
    app.include_router(terminal.router)

    if FRONTEND_DIST.exists():
        app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

        @app.get("/{full_path:path}")
        def spa(full_path: str):
            return FileResponse(FRONTEND_DIST / "index.html")

    return app


app = create_app()