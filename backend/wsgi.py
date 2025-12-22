"""
WSGI entry point for production deployment
"""
import os
from src.app_factory import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
