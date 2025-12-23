from flask import Blueprint, jsonify, request

from .auth0_utils import requires_auth
from .errors import AppError
from .services_api_keys import create_api_key, list_api_keys, update_api_key, deactivate_api_key

bp_api_keys = Blueprint("api_keys", __name__, url_prefix="/api/api-keys")


@bp_api_keys.get("")
@requires_auth
def list_keys():
    return jsonify({"apiKeys": list_api_keys()})


@bp_api_keys.post("")
@requires_auth
def create_key():
    try:
        data = request.get_json() or {}
        print(f"[API Keys] Creating API key with data: {data}")
        result = create_api_key(data)
        result["message"] = "API key created successfully"
        result["warning"] = "Save this key securely. You won't be able to see it again!"
        result["status"] = "success"
        print(f"[API Keys] Successfully created key: {result.get('apiKeyData', {}).get('id')}")
        return jsonify(result), 201
    except AppError as exc:
        print(f"[API Keys] AppError during creation: {exc.message}")
        return jsonify({"error": exc.message, "status": "error"}), exc.status_code
    except Exception as e:
        print(f"[API Keys] Unexpected error during creation: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to create API key: {str(e)}", "status": "error"}), 500


@bp_api_keys.put("/<key_id>")
@requires_auth
def update_key(key_id):
    try:
        data = request.get_json() or {}
        updated = update_api_key(key_id, data)
        return jsonify({"message": "API key updated successfully", "status": "success", "apiKeyData": updated}), 200
    except AppError as exc:
        return jsonify({"error": exc.message, "status": "error"}), exc.status_code


@bp_api_keys.delete("/<key_id>")
@requires_auth
def delete_key(key_id):
    try:
        deactivate_api_key(key_id)
        return jsonify({"message": "API key deleted successfully", "status": "success"}), 200
    except AppError as exc:
        return jsonify({"error": exc.message, "status": "error"}), exc.status_code
