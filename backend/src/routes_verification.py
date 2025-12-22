import secrets
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from .config import load_settings
from .errors import AppError
from .models import VerificationToken
from .services_tokens import generate_token, validate_token, mark_token_status, list_tokens
from .services_verifications import create_verification_from_payload, list_verifications, list_verifications_for_tokens
from sqlalchemy import select
from .database import session_scope

settings = load_settings()
serializer_salt = "verification-link"

bp_verification = Blueprint("verification", __name__, url_prefix="/api")


def _token_payload_from_request(data: dict, token_id: str) -> dict:
    return {
        "tokenId": token_id,
        "fullName": data['fullName'],
        "email": data['email'],
        "address": data['address'],
        "city": data['city'],
        "state": data['state'],
        "zipCode": data['zipCode'],
        "organizationName": data['organizationName'],
        "createdAt": None,
        "expiresIn": data.get('expiresIn', '24 hours'),
    }


@bp_verification.post("/generate-verification-link")
@jwt_required()
def generate_link():
    try:
        data = request.get_json() or {}
        required_fields = ['fullName', 'email', 'address', 'city', 'state', 'zipCode', 'organizationName']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        token_id = secrets.token_urlsafe(32)
        payload = _token_payload_from_request(data, token_id)
        from itsdangerous import URLSafeTimedSerializer

        serializer = URLSafeTimedSerializer(settings.secret_key)
        token_info = generate_token(serializer, payload)

        verification_url = f"{settings.frontend_url}/verify?token={token_info['token']}"

        return jsonify({
            "message": "Verification link generated successfully",
            "status": "success",
            "tokenId": token_info["token_id"],
            "verificationUrl": verification_url,
            "token": token_info["token"],
            "expiresAt": token_info["expires_at"].isoformat(),
            "expiresIn": "24 hours",
            "recipient": {"name": data['fullName'], "email": data['email']},
        }), 200
    except AppError as exc:
        return jsonify({"error": exc.message}), exc.status_code


@bp_verification.post("/validate-token")
def validate_link_token():
    try:
        data = request.get_json() or {}
        token = data.get("token")
        from itsdangerous import URLSafeTimedSerializer

        serializer = URLSafeTimedSerializer(settings.secret_key)
        verification_data = validate_token(serializer, token)
        return jsonify({
            "message": "Token is valid",
            "status": "success",
            "verification_data": {
                "fullName": verification_data['fullName'],
                "email": verification_data['email'],
                "address": verification_data['address'],
                "city": verification_data['city'],
                "state": verification_data['state'],
                "zipCode": verification_data['zipCode'],
                "organizationName": verification_data['organizationName'],
                "expiresIn": verification_data.get('expiresIn', '24 hours')
            }
        }), 200
    except AppError as exc:
        return jsonify({"error": exc.message, "status": "error"}), exc.status_code


@bp_verification.post("/verification-declined")
def decline_verification():
    try:
        data = request.get_json() or {}
        token = data.get("token")
        from itsdangerous import URLSafeTimedSerializer

        serializer = URLSafeTimedSerializer(settings.secret_key)
        verification_data = validate_token(serializer, token)
        token_id = verification_data["tokenId"]
        mark_token_status(token_id, status="declined", used=True)

        payload = {
            "fullName": verification_data['fullName'],
            "email": verification_data['email'],
            "address": verification_data['address'],
            "city": verification_data['city'],
            "state": verification_data['state'],
            "zipCode": verification_data['zipCode'],
            "organizationName": verification_data.get('organizationName', 'Organization'),
            "location": {},
            "consent": False,
        }
        create_verification_from_payload(payload, token_id, request.remote_addr)
        return jsonify({"message": "Verification decline recorded", "status": "success"}), 200
    except AppError as exc:
        return jsonify({"error": exc.message, "status": "error"}), exc.status_code


@bp_verification.post("/submit-verification")
def submit_verification():
    try:
        data = request.get_json() or {}
        token = data.get("token")
        token_id = None
        verification_payload = data

        if token:
            from itsdangerous import URLSafeTimedSerializer

            serializer = URLSafeTimedSerializer(settings.secret_key)
            verification_data = validate_token(serializer, token)
            token_id = verification_data["tokenId"]
            mark_token_status(token_id, status="completed", used=True)
            verification_payload = {**verification_payload, **verification_data}

        result = create_verification_from_payload(verification_payload, token_id, request.remote_addr)
        return jsonify(result), 200
    except AppError as exc:
        return jsonify({"error": exc.message, "status": "error"}), exc.status_code


@bp_verification.get("/verification-tokens")
@jwt_required()
def tokens_admin():
    tokens = list_tokens()
    return jsonify({"tokens": tokens, "total_count": len(tokens)})


@bp_verification.get("/verifications")
@jwt_required()
def verifications_admin():
    verifications = list_verifications()
    return jsonify({"verifications": verifications, "total_count": len(verifications)})


@bp_verification.post("/revoke-token")
@jwt_required()
def revoke_token():
    try:
        data = request.get_json() or {}
        token_id = data.get("tokenId")
        if not token_id:
            return jsonify({"error": "Invalid token ID", "status": "error"}), 400
        mark_token_status(token_id, status="revoked", used=False)
        return jsonify({"message": "Token revoked successfully", "status": "success"}), 200
    except AppError as exc:
        return jsonify({"error": exc.message, "status": "error"}), exc.status_code


@bp_verification.get("/v1/verifications")
@bp_verification.get("/v1/verifications/<verification_id>")
@bp_verification.get("/v1/generate-verification")
def deprecated_notice(*args, **kwargs):
    return jsonify({"error": "Use updated endpoints"}), 410


@bp_verification.get("/v1/verifications")
@jwt_required()
def api_list_by_key():
    # Deprecated placeholder; kept for compatibility but signals removal.
    return jsonify({"verifications": []})
