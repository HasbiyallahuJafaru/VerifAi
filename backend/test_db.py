"""Test database connection"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import load_settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load settings
settings = load_settings()

# Convert postgresql:// to postgresql+psycopg:// for psycopg 3.x compatibility
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_connection():
    """Test basic database connection"""
    print("Testing database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Database connected successfully!")
            print(f"PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_tables():
    """Test if tables exist"""
    print("\nChecking database tables...")
    try:
        with engine.connect() as conn:
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"✅ Found {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("⚠️  No tables found. Run migrations to create tables.")
            return True
    except Exception as e:
        print(f"❌ Failed to check tables: {e}")
        return False

def test_query():
    """Test querying data"""
    print("\nTesting database queries...")
    try:
        session = SessionLocal()
        # Try to query tables
        result = session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        
        result = session.execute(text("SELECT COUNT(*) FROM verification_tokens"))
        token_count = result.scalar()
        
        session.close()
        
        print(f"✅ Query successful!")
        print(f"   Users: {user_count}")
        print(f"   Verification Tokens: {token_count}")
        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        print(f"   This might mean tables don't exist yet.")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    
    connection_ok = test_connection()
    if connection_ok:
        tables_ok = test_tables()
        if tables_ok:
            test_query()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
