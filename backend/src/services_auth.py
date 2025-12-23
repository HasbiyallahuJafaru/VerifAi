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
            # User already exists - authenticate them instead
            print(f"[AUTH SERVICE] User already exists, proceeding to sign in: {email_normalized}")
            # Verify password and return authentication tokens
            if not check_password_hash(existing.password_hash, password):
                raise UnauthorizedError("Invalid credentials")
            
            claims = {"role": existing.role, "email": existing.email}
            access = create_access_token(identity=existing.id, additional_claims=claims)
            refresh = create_refresh_token(identity=existing.id)
            return {
                "id": existing.id,
                "email": existing.email,
                "role": existing.role,
                "access_token": access,
                "refresh_token": refresh,
                "user": {"id": existing.id, "email": existing.email, "role": existing.role},
                "already_existed": True
            }

        is_first_user = db.scalar(select(User.id)) is None
        role = "admin" if is_first_user else "user"
        user = User(email=email_normalized, password_hash=generate_password_hash(password), role=role)
        db.add(user)
        db.flush()
        return {"id": user.id, "email": user.email, "role": user.role, "created_at": datetime.utcnow().isoformat()}


def authenticate_user(email: str, password: str) -> dict:
    print(f"[AUTH SERVICE] Authenticating user: {email}")
    email_normalized = (email or "").strip().lower()
    
    if not email_normalized or not password:
        print("[AUTH SERVICE] Missing email or password")
        raise ValidationError("Email and password are required")

    with session_scope() as db:
        user = db.scalar(select(User).where(User.email == email_normalized))
        if not user:
            print(f"[AUTH SERVICE] User not found: {email_normalized}")
            raise UnauthorizedError("Invalid credentials")
        
        print(f"[AUTH SERVICE] User found: {email_normalized}, verifying password")
        if not check_password_hash(user.password_hash, password):
            print(f"[AUTH SERVICE] Password verification failed for: {email_normalized}")
            raise UnauthorizedError("Invalid credentials")

        print(f"[AUTH SERVICE] Authentication successful for: {email_normalized}")
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
