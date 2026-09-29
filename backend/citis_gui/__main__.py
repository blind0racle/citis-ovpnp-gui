import uvicorn
from .config import DEFAULT_PORT


def main() -> None:
    uvicorn.run("citis_gui.main:app", host="127.0.0.1", port=DEFAULT_PORT, reload=False)


if __name__ == "__main__":
    main()