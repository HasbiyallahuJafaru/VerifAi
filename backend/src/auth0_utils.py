import json
from functools import wraps
from typing import Any, Dict

import requests
from flask import request, jsonify, g
try:
    from jose import jwt  # type: ignore
except Exception:
    import jwt  # type: ignore

from .config import load_settings

settings = load_settings()

ALGORITHMS = ["RS256"]
_jwks_cache: Dict[str, Any] | None = None


def _get_jwks():
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
    resp = requests.get(jwks_url, timeout=5)
    resp.raise_for_status()
    _jwks_cache = resp.json()
    return _jwks_cache


def _get_token_auth_header() -> str:
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise ValueError("Authorization header is expected")

    parts = auth.split()
    if parts[0].lower() != "bearer":
        raise ValueError("Authorization header must start with Bearer")
    if len(parts) == 1:
        raise ValueError("Token not found")
    if len(parts) > 2:
        raise ValueError("Authorization header must be 'Bearer <token>'")

    return parts[1]


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = _get_token_auth_header()
            unverified_header = jwt.get_unverified_header(token)
            jwks = _get_jwks()
            rsa_key = {}
            for key in jwks.get("keys", []):
                if key.get("kid") == unverified_header.get("kid"):
                    rsa_key = {
                        "kty": key.get("kty"),
                        "kid": key.get("kid"),
                        "use": key.get("use"),
                        "n": key.get("n"),
                        "e": key.get("e"),
                    }
                    break
            if not rsa_key:
                raise ValueError("Appropriate key not found")

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=settings.auth0_audience,
                issuer=f"https://{settings.auth0_domain}/",
            )
            g.current_user = payload
        except Exception as e:
            return jsonify({"error": "Unauthorized", "details": str(e)}), 401
        return f(*args, **kwargs)

    return decorated


def current_user_sub() -> str | None:
    user = getattr(g, "current_user", None)
    if user:
        return user.get("sub")
    return None
