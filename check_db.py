
#!/usr/bin/env python3
"""
Database connection checker script
"""

import os
from sqlalchemy import create_engine, text

def check_database_connection():
    """Check if database connection is working"""
    try:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL environment variable not found")
            return False
        
        print(f"🔍 Checking connection to: {database_url[:50]}...")
        
        # Create engine with connection timeout
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 10}
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Solutions:")
        print("1. Go to Database tab in Replit sidebar")
        print("2. Click to enable/wake up your PostgreSQL database")
        print("3. If that doesn't work, create a new database")
        return False

if __name__ == "__main__":
    check_database_connection()
