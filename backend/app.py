"""Thin runner to keep backward compatibility with `python app.py`.

This delegates to the modular app factory in src.app_factory.
"""

import os
import sys
from pathlib import Path

from flask import Flask


BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from src.app_factory import create_app  # type: ignore
    from src.config import load_settings  # type: ignore
except ImportError:
    # Fallback if relative import resolution differs
    from app_factory import create_app  # type: ignore
    from config import load_settings  # type: ignore


app: Flask = create_app()


if __name__ == "__main__":
    settings = load_settings()
    port = int(os.environ.get("PORT", settings.port))
    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
