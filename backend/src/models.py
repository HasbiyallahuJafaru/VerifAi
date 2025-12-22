import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, default="admin")  # admin | user
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class VerificationToken(Base):
    __tablename__ = "verification_tokens"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    token: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    organization_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active")  # active | completed | declined | revoked
    api_key_id: Mapped[str | None] = mapped_column(String, nullable=True)


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    token_id: Mapped[str | None] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    personal_info: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    location_data: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    security_data: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    verification_results: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    consent_provided: Mapped[bool] = mapped_column(Boolean, default=True)


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False)
    key_prefix: Mapped[str] = mapped_column(String, nullable=False)
    key_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    permissions: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string list
    rate_limit: Mapped[int] = mapped_column(Integer, default=1000)
    environment: Mapped[str] = mapped_column(String, default="production")


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    filepath: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    document_type: Mapped[str] = mapped_column(String, default="unknown")
    verification_id: Mapped[str | None] = mapped_column(String, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
