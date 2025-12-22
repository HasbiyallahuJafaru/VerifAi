from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from .errors import AppError
from .services_api_keys import create_api_key, list_api_keys, update_api_key, deactivate_api_key

bp_api_keys = Blueprint("api_keys", __name__, url_prefix="/api/api-keys")


@bp_api_keys.get("")
@jwt_required()
def list_keys():
    return jsonify({"apiKeys": list_api_keys()})


@bp_api_keys.post("")
@jwt_required()
def create_key():
    try:
        data = request.get_json() or {}
        result = create_api_key(data)
        result["message"] = "API key created successfully"
        result["warning"] = "Save this key securely. You won't be able to see it again!"
        result["status"] = "success"
        return jsonify(result), 201
    except AppError as exc:
        return jsonify({"error": exc.message, "status": "error"}), exc.status_code


@bp_api_keys.put("/<key_id>")
@jwt_required()
def update_key(key_id):
    try:
        data = request.get_json() or {}
        updated = update_api_key(key_id, data)
        return jsonify({"message": "API key updated successfully", "status": "success", "apiKeyData": updated}), 200
    except AppError as exc:
        return jsonify({"error": exc.message, "status": "error"}), exc.status_code


@bp_api_keys.delete("/<key_id>")
@jwt_required()
def delete_key(key_id):
    try:
        deactivate_api_key(key_id)
        return jsonify({"message": "API key deleted successfully", "status": "success"}), 200
    except AppError as exc:
        return jsonify({"error": exc.message, "status": "error"}), exc.status_code
