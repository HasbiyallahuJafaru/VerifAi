from datetime import datetime

from flask import Flask

try:
    from .app_factory import create_app
    from .config import load_settings
except ImportError:
    # Fallback for direct script execution: ensure src directory is on sys.path
    import sys
    from pathlib import Path

    CURRENT_DIR = Path(__file__).resolve().parent
    if str(CURRENT_DIR) not in sys.path:
        sys.path.insert(0, str(CURRENT_DIR))
    from app_factory import create_app  # type: ignore
    from config import load_settings  # type: ignore

app: Flask = create_app()

if __name__ == "__main__":
    settings = load_settings()
    app.run(host="0.0.0.0", port=settings.port)
