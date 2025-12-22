from datetime import datetime
from typing import Optional

from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import select

from .database import session_scope
from .errors import ValidationError, UnauthorizedError
from .models import User


def create_user(email: str, password: str) -> dict:
    email_normalized = email.strip().lower()
    if not email_normalized or not password:
        raise ValidationError("Email and password are required")

    with session_scope() as db:
        existing = db.scalar(select(User).where(User.email == email_normalized))
        if existing:
            raise ValidationError("User already exists")

        is_first_user = db.scalar(select(User.id)) is None
        role = "admin" if is_first_user else "user"
        user = User(email=email_normalized, password_hash=generate_password_hash(password), role=role)
        db.add(user)
        db.flush()
        return {"id": user.id, "email": user.email, "role": user.role, "created_at": datetime.utcnow().isoformat()}


def authenticate_user(email: str, password: str) -> dict:
    email_normalized = (email or "").strip().lower()
    if not email_normalized or not password:
        raise ValidationError("Email and password are required")

    with session_scope() as db:
        user = db.scalar(select(User).where(User.email == email_normalized))
        if not user or not check_password_hash(user.password_hash, password):
            raise UnauthorizedError("Invalid credentials")

        claims = {"role": user.role, "email": user.email}
        access = create_access_token(identity=user.id, additional_claims=claims)
        refresh = create_refresh_token(identity=user.id)
        return {
            "access_token": access,
            "refresh_token": refresh,
            "user": {"id": user.id, "email": user.email, "role": user.role},
        }


def get_user(user_id: str) -> Optional[dict]:
    with session_scope() as db:
        user = db.get(User, user_id)
        if not user:
            return None
        return {"id": user.id, "email": user.email, "role": user.role}
