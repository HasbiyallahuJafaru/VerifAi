from flask import Blueprint, jsonify

bp_auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp_auth.post("/signup")
def signup():
    return jsonify({"error": "Local authentication disabled. Please use Auth0."}), 410


@bp_auth.post("/login")
def login():
    return jsonify({"error": "Local authentication disabled. Please use Auth0."}), 410


@bp_auth.post("/refresh")
def refresh():
    return jsonify({"error": "Local authentication disabled. Please use Auth0."}), 410


@bp_auth.get("/me")
def me():
    return jsonify({"error": "Local authentication disabled. Please use Auth0."}), 410
