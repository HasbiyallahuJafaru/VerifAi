from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
import logging
import traceback

from .errors import AppError
from .services_auth import authenticate_user, create_user, get_user

logger = logging.getLogger(__name__)
bp_auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp_auth.post("/signup")
def signup():
    try:
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")
        
        logger.info(f"[SIGNUP] Signup request for email: {email}")
        
        if not email:
            logger.warning("[SIGNUP] Email missing in request")
            return jsonify({"error": "Email is required"}), 400
        
        if not password:
            logger.warning(f"[SIGNUP] Password missing for email: {email}")
            return jsonify({"error": "Password is required"}), 400
        
        result = create_user(email, password)
        
        # If user already existed, return 200 with tokens instead of 201
        if result.get("already_existed"):
            logger.info(f"[SIGNUP] User existed, auto-signed in: {email}")
            return jsonify({
                "message": "User already exists, signed in successfully",
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "user": result["user"]
            }), 200
        
        # New user created
        logger.info(f"[SIGNUP] New user created: {email}")
        return jsonify({"message": "User created", "role": result["role"]}), 201
    except AppError as exc:
        logger.error(f"[SIGNUP] AppError: {exc.message}")
        return jsonify({"error": exc.message}), exc.status_code
    except Exception as e:
        logger.error(f"[SIGNUP] Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Signup failed: {str(e)}"}), 500


@bp_auth.post("/login")
def login():
    try:
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")
        
        logger.info(f"[LOGIN] Login attempt for email: {email}")
        
        if not email:
            logger.warning("[LOGIN] Email missing in request")
            return jsonify({"error": "Email is required"}), 400
        if not password:
            logger.warning(f"[LOGIN] Password missing for email: {email}")
            return jsonify({"error": "Password is required"}), 400
            
        result = authenticate_user(email, password)
        logger.info(f"[LOGIN] Login successful for: {email}")
        return jsonify(result), 200
    except AppError as exc:
        logger.error(f"[LOGIN] AppError for {email}: {exc.message} (status: {exc.status_code})")
        return jsonify({"error": exc.message}), exc.status_code
    except Exception as e:
        logger.error(f"[LOGIN] Unexpected error for {email}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@bp_auth.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    token = create_access_token(identity=identity)
    return jsonify({"access_token": token})


@bp_auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)
