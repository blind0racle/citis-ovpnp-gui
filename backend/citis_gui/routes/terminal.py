from __future__ import annotations
import asyncio, json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session
from ..db import engine
from ..models import Server
from ..ssh_pool import get_pool

router = APIRouter()


@router.websocket("/ws/term/{sid}")
async def term(ws: WebSocket, sid: str):
    await ws.accept()

    with Session(engine) as db:
        server = db.get(Server, sid)
        if not server:
            await ws.send_text(json.dumps({"type": "error", "error": "server not found"}))
            await ws.close()
            return
        try:
            conn = await get_pool().get(db, server)
        except Exception as e:
            await ws.send_text(json.dumps({"type": "error", "error": str(e)}))
            await ws.close()
            return

    proc = await conn.create_process(
        term_type="xterm-256color", term_size=(120, 32), encoding=None,
    )

    async def pump_out():
        try:
            async for chunk in proc.stdout.read(4096):
                await ws.send_bytes(chunk)
        except Exception:
            pass

    out_task = asyncio.create_task(pump_out())

    try:
        while True:
            msg = await ws.receive()
            if msg.get("type") == "websocket.disconnect":
                break
            if "bytes" in msg and msg["bytes"]:
                proc.stdin.write(msg["bytes"])
            elif "text" in msg and msg["text"]:
                try:
                    ctl = json.loads(msg["text"])
                except Exception:
                    proc.stdin.write(msg["text"].encode())
                    continue
                t = ctl.get("type")
                if t == "resize":
                    proc.change_terminal_size(ctl["cols"], ctl["rows"])
                elif t == "input":
                    proc.stdin.write(ctl["data"].encode())
    except WebSocketDisconnect:
        pass
    finally:
        out_task.cancel()
        try:
            proc.terminate()
        except Exception:
            pass