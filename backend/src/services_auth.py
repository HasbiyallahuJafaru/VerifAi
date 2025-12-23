from datetime import datetime
from typing import Optional
import logging
import traceback

from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import select

from .database import session_scope
from .errors import ValidationError, UnauthorizedError
from .models import User

logger = logging.getLogger(__name__)


def create_user(email: str, password: str) -> dict:
    try:
        logger.info(f"[CREATE_USER] Starting user creation for: {email}")
        email_normalized = email.strip().lower()
        
        if not email_normalized or not password:
            logger.warning(f"[CREATE_USER] Missing email or password")
            raise ValidationError("Email and password are required")

        with session_scope() as db:
            existing = db.scalar(select(User).where(User.email == email_normalized))
            if existing:
                # User already exists - authenticate them instead
                logger.info(f"[CREATE_USER] User already exists, attempting auto sign-in: {email_normalized}")
                # Verify password and return authentication tokens
                if not check_password_hash(existing.password_hash, password):
                    logger.warning(f"[CREATE_USER] Password mismatch for existing user: {email_normalized}")
                    raise UnauthorizedError("Invalid credentials")
                
                logger.info(f"[CREATE_USER] Auto sign-in successful for: {email_normalized}")
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
            logger.info(f"[CREATE_USER] Creating new user: {email_normalized} with role: {role}")
            user = User(email=email_normalized, password_hash=generate_password_hash(password), role=role)
            db.add(user)
            db.flush()
            logger.info(f"[CREATE_USER] User created successfully: {email_normalized}")
            return {"id": user.id, "email": user.email, "role": user.role, "created_at": datetime.utcnow().isoformat()}
    except (ValidationError, UnauthorizedError):
        raise
    except Exception as e:
        logger.error(f"[CREATE_USER] Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        raise ValidationError(f"User creation failed: {str(e)}")


def authenticate_user(email: str, password: str) -> dict:
    try:
        logger.info(f"[AUTHENTICATE] Starting authentication for: {email}")
        email_normalized = (email or "").strip().lower()
        
        if not email_normalized:
            logger.warning(f"[AUTHENTICATE] Email is empty or None")
            raise ValidationError("Email is required")
        
        if not password:
            logger.warning(f"[AUTHENTICATE] Password is empty for email: {email_normalized}")
            raise ValidationError("Password is required")

        with session_scope() as db:
            logger.debug(f"[AUTHENTICATE] Querying database for user: {email_normalized}")
            user = db.scalar(select(User).where(User.email == email_normalized))
            
            if not user:
                logger.warning(f"[AUTHENTICATE] User not found in database: {email_normalized}")
                # List all users for debugging (remove in production)
                all_users = db.scalars(select(User.email)).all()
                logger.debug(f"[AUTHENTICATE] Available users in DB: {all_users}")
                raise UnauthorizedError("Invalid credentials")
            
            logger.info(f"[AUTHENTICATE] User found: {email_normalized}, verifying password")
            if not check_password_hash(user.password_hash, password):
                logger.warning(f"[AUTHENTICATE] Password verification failed for: {email_normalized}")
                raise UnauthorizedError("Invalid credentials")

            logger.info(f"[AUTHENTICATE] Authentication successful for: {email_normalized}")
            claims = {"role": user.role, "email": user.email}
            
            logger.debug(f"[AUTHENTICATE] Creating JWT tokens for user ID: {user.id}")
            access = create_access_token(identity=user.id, additional_claims=claims)
            refresh = create_refresh_token(identity=user.id)
            
            logger.info(f"[AUTHENTICATE] Tokens generated successfully for: {email_normalized}")
            return {
                "access_token": access,
                "refresh_token": refresh,
                "user": {"id": user.id, "email": user.email, "role": user.role},
            }
    except (ValidationError, UnauthorizedError):
        raise
    except Exception as e:
        logger.error(f"[AUTHENTICATE] Unexpected error during authentication: {str(e)}")
        logger.error(traceback.format_exc())
        raise UnauthorizedError(f"Authentication failed: {str(e)}")


def get_user(user_id: str) -> Optional[dict]:
    with session_scope() as db:
        user = db.get(User, user_id)
        if not user:
            return None
        return {"id": user.id, "email": user.email, "role": user.role}
