from flask import Blueprint, jsonify

from .auth0_utils import requires_auth, current_user_sub
from .errors import AppError

bp_auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp_auth.post("/signup")
def signup():
    return jsonify({"error": "Local signup disabled. Use Auth0."}), 410


@bp_auth.post("/login")
def login():
    return jsonify({"error": "Local login disabled. Use Auth0."}), 410


@bp_auth.post("/refresh")
def refresh():
    return jsonify({"error": "Local refresh disabled. Use Auth0."}), 410


@bp_auth.get("/me")
def me():
    """Return Auth0 token claims for the current user."""
    @requires_auth
    def _inner():
        # auth0_utils stores decoded JWT in flask.g.current_user
        from flask import g

        claims = getattr(g, "current_user", {}) or {}
        sub = claims.get("sub") or current_user_sub()
        email = claims.get("email") or claims.get("upn")
        return jsonify({"sub": sub, "email": email, "claims": claims})

    return _inner()
