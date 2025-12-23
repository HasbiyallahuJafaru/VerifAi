from datetime import datetime
import logging

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .config import load_settings
from .database import Base, engine
from .errors import AppError
from .routes_api_keys import bp_api_keys
from .routes_auth import bp_auth
from .routes_verification import bp_verification

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    settings = load_settings()
    app = Flask(__name__)
    
    logger.info("[APP] Initializing Flask application")
    
    # Configure JWT
    logger.info("[APP] Configuring JWT")
    app.config["JWT_SECRET_KEY"] = settings.jwt_secret
    jwt = JWTManager(app)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.warning(f"[JWT] Expired token detected")
        return jsonify({"error": "Token has expired"}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.warning(f"[JWT] Invalid token: {error}")
        return jsonify({"error": "Invalid token"}), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        logger.warning(f"[JWT] Unauthorized access: {error}")
        return jsonify({"error": "Missing or invalid authorization"}), 401

    logger.info(f"[APP] Configuring CORS with origins: {settings.cors_origins}")
    CORS(
        app,
        origins=settings.cors_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    logger.info("[APP] Creating database tables")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("[APP] Database tables created successfully")
    except Exception as e:
        logger.error(f"[APP] Database initialization failed: {str(e)}")
        raise

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        logger.error(f"[APP] AppError: {error.message} (status: {error.status_code})")
        return jsonify({"error": error.message}), error.status_code
    
    @app.errorhandler(Exception)
    def handle_exception(error: Exception):
        logger.error(f"[APP] Unhandled exception: {str(error)}")
        logger.error(f"[APP] Exception type: {type(error).__name__}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error", "details": str(error)}), 500

    @app.route("/")
    def root_health():
        return jsonify({"message": "Address verification API is running", "status": "healthy", "version": "1.0.0"})

    @app.route("/api/health")
    def api_health():
        return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

    logger.info("[APP] Registering blueprints")
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_verification)
    app.register_blueprint(bp_api_keys)
    logger.info("[APP] All blueprints registered successfully")

    logger.info("[APP] Flask application initialized successfully")
    return app


app = create_app()
