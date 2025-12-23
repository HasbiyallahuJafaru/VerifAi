from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS

from .config import load_settings
from .database import Base, engine
from .errors import AppError
from .routes_api_keys import bp_api_keys
from .routes_auth import bp_auth
from .routes_verification import bp_verification


def create_app() -> Flask:
    settings = load_settings()
    app = Flask(__name__)

    CORS(
        app,
        origins=settings.cors_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    Base.metadata.create_all(bind=engine)

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return jsonify({"error": error.message}), error.status_code

    @app.route("/")
    def root_health():
        return jsonify({"message": "Address verification API is running", "status": "healthy", "version": "1.0.0"})

    @app.route("/api/health")
    def api_health():
        return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_verification)
    app.register_blueprint(bp_api_keys)

    return app


app = create_app()
