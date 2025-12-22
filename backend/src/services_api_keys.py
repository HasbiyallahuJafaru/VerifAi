import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import select

from .database import session_scope
from .errors import ValidationError, NotFoundError
from .models import ApiKey


def generate_api_key() -> str:
    random_part = secrets.token_urlsafe(32)
    return f"verifai_live_{random_part}"


def hash_api_key(api_key: str) -> str:
    import hashlib

    return hashlib.sha256(api_key.encode()).hexdigest()


def create_api_key(payload: Dict) -> Dict:
    for field in ["name", "company"]:
        if field not in payload:
            raise ValidationError(f"Missing required field: {field}")

    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    api_key_id = f"key_{secrets.token_urlsafe(8)}"
    key_prefix = api_key[:20] + "..."

    expires_in_days = payload.get("expiresInDays")
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days) if expires_in_days else None

    try:
        record = ApiKey(
            id=api_key_id,
            name=payload["name"],
            company=payload["company"],
            key_prefix=key_prefix,
            key_hash=key_hash,
            active=True,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            usage_count=0,
            permissions=json.dumps(payload.get("permissions", ["verification:create", "verification:read"])),
            rate_limit=payload.get("rateLimit", 1000),
            environment=payload.get("environment", "production"),
        )

        with session_scope() as db:
            db.add(record)
            db.flush()  # Force write to get any database errors
            
        print(f"[API Keys Service] Created API key: {api_key_id}")

        return {
            "apiKey": api_key,
            "apiKeyData": {
                "id": api_key_id,
                "name": payload["name"],
                "company": payload["company"],
                "keyPrefix": key_prefix,
                "createdAt": record.created_at.isoformat(),
                "expiresAt": expires_at.isoformat() if expires_at else None,
                "permissions": json.loads(record.permissions),
            },
        }
    except Exception as e:
        print(f"[API Keys Service] Error creating API key: {str(e)}")
        import traceback
        traceback.print_exc()
        raise ValidationError(f"Failed to create API key: {str(e)}")


def list_api_keys() -> List[Dict]:
    with session_scope() as db:
        keys = db.scalars(select(ApiKey)).all()
        return [
            {
                "id": k.id,
                "name": k.name,
                "company": k.company,
                "keyPrefix": k.key_prefix,
                "active": k.active,
                "createdAt": k.created_at.isoformat() if k.created_at else None,
                "expiresAt": k.expires_at.isoformat() if k.expires_at else None,
                "lastUsedAt": k.last_used_at.isoformat() if k.last_used_at else None,
                "usageCount": k.usage_count,
                "permissions": json.loads(k.permissions or "[]"),
            }
            for k in keys
        ]


def update_api_key(key_id: str, payload: Dict) -> Dict:
    with session_scope() as db:
        record = db.get(ApiKey, key_id)
        if not record:
            raise NotFoundError("API key not found")

        if "active" in payload:
            record.active = payload["active"]
        if "name" in payload:
            record.name = payload["name"]
        if "permissions" in payload:
            record.permissions = json.dumps(payload["permissions"])
        if "rateLimit" in payload:
            record.rate_limit = payload["rateLimit"]

        db.add(record)
        return {
            "id": record.id,
            "name": record.name,
            "active": record.active,
            "updatedAt": datetime.utcnow().isoformat(),
        }


def deactivate_api_key(key_id: str) -> None:
    with session_scope() as db:
        record = db.get(ApiKey, key_id)
        if not record:
            raise NotFoundError("API key not found")
        record.active = False
        record.expires_at = record.expires_at or datetime.utcnow()
        db.add(record)
