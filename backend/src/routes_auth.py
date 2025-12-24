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


@bp_auth.get("/users")
@jwt_required()
def list_users():
    """List all users (admin only)"""
    try:
        from flask_jwt_extended import get_jwt
        from .services_auth import list_all_users
        
        claims = get_jwt()
        user_role = claims.get('role')
        
        logger.info(f"[LIST_USERS] User role: {user_role}")
        
        if user_role != 'admin':
            logger.warning(f"[LIST_USERS] Non-admin user attempted to list users")
            return jsonify({"error": "Admin access required"}), 403
        
        users = list_all_users()
        logger.info(f"[LIST_USERS] Returning {len(users)} users")
        return jsonify({"users": users}), 200
    except Exception as e:
        logger.error(f"[LIST_USERS] Error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Failed to list users: {str(e)}"}), 500


@bp_auth.post("/users")
@jwt_required()
def create_user_admin():
    """Create a new user (admin only)"""
    try:
        from flask_jwt_extended import get_jwt
        from .services_auth import create_user_by_admin
        
        claims = get_jwt()
        user_role = claims.get('role')
        
        if user_role != 'admin':
            logger.warning(f"[CREATE_USER_ADMIN] Non-admin attempted to create user")
            return jsonify({"error": "Admin access required"}), 403
        
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "user")
        
        logger.info(f"[CREATE_USER_ADMIN] Creating user: {email} with role: {role}")
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not password:
            return jsonify({"error": "Password is required"}), 400
        
        result = create_user_by_admin(email, password, role)
        logger.info(f"[CREATE_USER_ADMIN] User created: {email}")
        return jsonify({"message": "User created successfully", "user": result}), 201
    except AppError as exc:
        logger.error(f"[CREATE_USER_ADMIN] AppError: {exc.message}")
        return jsonify({"error": exc.message}), exc.status_code
    except Exception as e:
        logger.error(f"[CREATE_USER_ADMIN] Error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Failed to create user: {str(e)}"}), 500


@bp_auth.delete("/users/<user_id>")
@jwt_required()
def delete_user_admin(user_id):
    """Delete a user (admin only)"""
    try:
        from flask_jwt_extended import get_jwt
        from .services_auth import delete_user_by_admin
        
        claims = get_jwt()
        user_role = claims.get('role')
        current_user_id = get_jwt_identity()
        
        if user_role != 'admin':
            logger.warning(f"[DELETE_USER] Non-admin attempted to delete user")
            return jsonify({"error": "Admin access required"}), 403
        
        if user_id == current_user_id:
            logger.warning(f"[DELETE_USER] Admin attempted to delete themselves")
            return jsonify({"error": "Cannot delete your own account"}), 400
        
        logger.info(f"[DELETE_USER] Deleting user: {user_id}")
        delete_user_by_admin(user_id)
        logger.info(f"[DELETE_USER] User deleted: {user_id}")
        return jsonify({"message": "User deleted successfully"}), 200
    except AppError as exc:
        logger.error(f"[DELETE_USER] AppError: {exc.message}")
        return jsonify({"error": exc.message}), exc.status_code
    except Exception as e:
        logger.error(f"[DELETE_USER] Error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Failed to delete user: {str(e)}"}), 500
