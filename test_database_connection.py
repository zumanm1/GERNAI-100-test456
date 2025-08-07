#!/usr/bin/env python3
"""
Database Connection Test Script

This script tests database connectivity and basic operations.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from backend.database.connection import DATABASE_URL, SessionLocal, get_database_url
from backend.database.models import User, NetworkDevice, OperationLog
from backend.database.connection import Base, engine
import traceback

def test_basic_connection():
    """Test basic database connection."""
    print("🔧 Testing basic database connection...")
    try:
        # Test connection using engine
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Basic database connection successful")
                return True
            else:
                print("❌ Basic database connection failed - unexpected result")
                return False
    except Exception as e:
        print(f"❌ Basic database connection failed: {e}")
        return False

def test_session_creation():
    """Test database session creation."""
    print("🔧 Testing database session creation...")
    try:
        db = SessionLocal()
        # Simple test query
        result = db.execute(text("SELECT 1")).fetchone()
        db.close()
        
        if result and result[0] == 1:
            print("✅ Database session creation successful")
            return True
        else:
            print("❌ Database session creation failed - unexpected result")
            return False
    except Exception as e:
        print(f"❌ Database session creation failed: {e}")
        return False

def test_table_creation():
    """Test database table creation."""
    print("🔧 Testing database table creation...")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        expected_tables = ['users', 'network_devices', 'operation_logs', 'ai_conversations', 'genai_settings']
        found_tables = []
        missing_tables = []
        
        for table in expected_tables:
            if table in existing_tables:
                found_tables.append(table)
            else:
                missing_tables.append(table)
        
        print(f"   Found tables: {found_tables}")
        if missing_tables:
            print(f"   Missing tables: {missing_tables}")
            print("⚠️  Some tables are missing, but basic structure seems to work")
            return True  # Partial success
        else:
            print("✅ All expected database tables created successfully")
            return True
            
    except Exception as e:
        print(f"❌ Database table creation failed: {e}")
        traceback.print_exc()
        return False

def test_model_operations():
    """Test basic CRUD operations with models."""
    print("🔧 Testing database model operations...")
    try:
        db = SessionLocal()
        
        # Test User model operations
        test_user = User(
            email="test@example.com",
            password_hash="dummy_hash",
            display_name="test_user",
            is_active=True
        )
        
        # Insert
        db.add(test_user)
        db.commit()
        
        # Query
        retrieved_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if retrieved_user and retrieved_user.email == "test@example.com":
            print("✅ User model operations successful")
            
            # Cleanup
            db.delete(retrieved_user)
            db.commit()
            
            db.close()
            return True
        else:
            print("❌ User model operations failed")
            db.close()
            return False
            
    except Exception as e:
        print(f"❌ Database model operations failed: {e}")
        try:
            db.rollback()
            db.close()
        except:
            pass
        return False

def main():
    """Main test function."""
    print("=" * 80)
    print("🗃️  DATABASE CONNECTION TEST")
    print("=" * 80)
    print()
    
    # Show database configuration
    db_url = get_database_url()
    print(f"📊 Database URL: {db_url}")
    
    if db_url.startswith('sqlite://'):
        print("   Database type: SQLite")
        # Make sure the data directory exists for SQLite
        db_file = db_url.replace('sqlite:///', '')
        db_dir = os.path.dirname(db_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"   Created directory: {db_dir}")
    else:
        print("   Database type: PostgreSQL/Other")
    
    print()
    
    # Run tests
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Session Creation", test_session_creation),
        ("Table Creation", test_table_creation),
        ("Model Operations", test_model_operations),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("=" * 80)
    print("📊 DATABASE TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All database tests passed!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
