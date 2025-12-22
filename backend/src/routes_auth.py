from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

from .errors import AppError
from .services_auth import authenticate_user, create_user, get_user

bp_auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp_auth.post("/signup")
def signup():
    try:
        data = request.get_json() or {}
        created = create_user(data.get("email"), data.get("password"))
        return jsonify({"message": "User created", "role": created["role"]}), 201
    except AppError as exc:
        return jsonify({"error": exc.message}), exc.status_code


@bp_auth.post("/login")
def login():
    try:
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")
        
        print(f"[LOGIN] Login attempt for email: {email}")
        
        if not email:
            print("[LOGIN] Error: Email is missing")
            return jsonify({"error": "Email is required", "details": "No email provided"}), 400
        if not password:
            print("[LOGIN] Error: Password is missing")
            return jsonify({"error": "Password is required", "details": "No password provided"}), 400
            
        result = authenticate_user(email, password)
        print(f"[LOGIN] Success for email: {email}")
        return jsonify(result), 200
    except AppError as exc:
        print(f"[LOGIN] AppError: {exc.message} (status: {exc.status_code})")
        return jsonify({"error": exc.message, "details": str(exc)}), exc.status_code
    except Exception as e:
        print(f"[LOGIN] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


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
