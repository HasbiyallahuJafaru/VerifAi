#!/usr/bin/env python3
"""
One-time script to create an admin user in the local database.
Note: With Auth0 enabled, this is mainly for database records.
Auth0 handles actual authentication.

Usage: python create_admin.py
"""

import sys
from pathlib import Path

# Add src to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.database import session_scope
from src.models import User
from werkzeug.security import generate_password_hash
from sqlalchemy import select


def create_admin_user():
    email = input("Enter admin email: ").strip().lower()
    password = input("Enter admin password: ").strip()
    
    if not email or not password:
        print("Error: Email and password are required")
        return
    
    with session_scope() as db:
        # Check if user exists
        existing = db.scalar(select(User).where(User.email == email))
        if existing:
            print(f"User {email} already exists with role: {existing.role}")
            update = input("Update to admin? (y/n): ").strip().lower()
            if update == 'y':
                existing.role = 'admin'
                db.flush()
                print(f"✓ User {email} updated to admin")
            return
        
        # Create new admin user
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role='admin'
        )
        db.add(user)
        db.flush()
        print(f"✓ Admin user created: {email}")
        print(f"  ID: {user.id}")
        print(f"  Role: {user.role}")


if __name__ == "__main__":
    print("Creating admin user...")
    print("=" * 50)
    create_admin_user()
    print("=" * 50)
    print("Done!")
