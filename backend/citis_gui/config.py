from pathlib import Path
import os

APP_NAME = "citis-ovpnp-gui"
DATA_DIR = Path(os.environ.get("CITIS_GUI_DATA", Path.home() / ".citis-ovpnp-gui"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "gui.db"
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

DEFAULT_PORT = 8765
SESSION_COOKIE = "citis_session"