from datetime import datetime, timedelta
from typing import Dict

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from sqlalchemy import select

from .database import session_scope
from .errors import ValidationError, NotFoundError
from .models import VerificationToken


def generate_token(serializer: URLSafeTimedSerializer, payload: Dict, expires_hours: int = 24) -> Dict:
    token_id = payload["tokenId"]
    token = serializer.dumps(payload, salt="verification-link")
    expires_at = datetime.utcnow() + timedelta(hours=expires_hours)

    with session_scope() as db:
        db.add(
            VerificationToken(
                id=token_id,
                token=token,
                email=payload["email"],
                full_name=payload["fullName"],
                organization_name=payload["organizationName"],
                expires_at=expires_at,
                status="active",
                api_key_id=payload.get("apiKeyId"),
            )
        )
    return {
        "token": token,
        "expires_at": expires_at,
        "token_id": token_id,
    }


def validate_token(serializer: URLSafeTimedSerializer, token: str) -> Dict:
    if not token:
        raise ValidationError("No token provided")

    try:
        data = serializer.loads(token, salt="verification-link", max_age=86400)
    except SignatureExpired as e:
        raise ValidationError("This verification link has expired") from e
    except BadSignature as e:
        raise ValidationError("Invalid or corrupted verification link") from e

    token_id = data.get("tokenId")
    with session_scope() as db:
        record = db.get(VerificationToken, token_id)
        if not record:
            raise ValidationError("Invalid verification token")
        if record.used:
            raise ValidationError("This verification link has already been used")
        if record.status != "active":
            raise ValidationError("This verification link is no longer active")
        if record.expires_at and record.expires_at < datetime.utcnow():
            raise ValidationError("This verification link has expired")
    return data


def mark_token_status(token_id: str, status: str, used: bool = False) -> None:
    with session_scope() as db:
        record = db.get(VerificationToken, token_id)
        if not record:
            raise NotFoundError("Token not found")
        record.status = status
        if used:
            record.used = True
            record.used_at = datetime.utcnow()
        db.add(record)


def list_tokens() -> list:
    with session_scope() as db:
        return [
            {
                "id": t.id,
                "email": t.email,
                "fullName": t.full_name,
                "organizationName": t.organization_name,
                "createdAt": t.created_at.isoformat(),
                "expiresAt": t.expires_at.isoformat(),
                "used": t.used,
                "usedAt": t.used_at.isoformat() if t.used_at else None,
                "status": t.status,
            }
            for t in db.scalars(select(VerificationToken)).all()
        ]
