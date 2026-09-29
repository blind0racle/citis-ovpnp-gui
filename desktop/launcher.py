"""Native window wrapper — pywebview opens a real desktop window over the local server."""
from __future__ import annotations
import threading, time, sys
import uvicorn
import webview

from citis_gui.config import DEFAULT_PORT


def serve() -> None:
    uvicorn.run("citis_gui.main:app", host="127.0.0.1", port=DEFAULT_PORT, log_level="warning")


def main() -> None:
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    time.sleep(0.6)   # let uvicorn bind
    webview.create_window(
        "Citis OVPN",
        f"http://127.0.0.1:{DEFAULT_PORT}",
        width=1400, height=900, min_size=(900, 600),
    )
    webview.start()


if __name__ == "__main__":
    sys.exit(main())