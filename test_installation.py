#!/usr/bin/env python3
"""
Installation Verification Test Script

This script tests that all major modules can be imported correctly
and verifies the installation is complete.
"""

import sys
import traceback
from typing import Dict, List, Tuple

def test_import(module_name: str, description: str = "") -> Tuple[bool, str]:
    """
    Test importing a module and return success status with message.
    
    Args:
        module_name: The module to import
        description: Optional description of what this module is for
        
    Returns:
        Tuple of (success, message)
    """
    try:
        if '.' in module_name:
            # For submodules, import the parent first
            parts = module_name.split('.')
            for i in range(1, len(parts) + 1):
                partial_name = '.'.join(parts[:i])
                __import__(partial_name)
        else:
            __import__(module_name)
        
        desc_text = f" ({description})" if description else ""
        return True, f"✅ {module_name}{desc_text}"
    except ImportError as e:
        desc_text = f" ({description})" if description else ""
        return False, f"❌ {module_name}{desc_text} - ImportError: {str(e)}"
    except Exception as e:
        desc_text = f" ({description})" if description else ""
        return False, f"❌ {module_name}{desc_text} - Error: {str(e)}"

def main():
    """Main test function."""
    print("=" * 80)
    print("🚀 INSTALLATION VERIFICATION TEST")
    print("=" * 80)
    print()
    
    # Define modules to test with descriptions
    test_modules = [
        # Core Python modules
        ("os", "Operating system interface"),
        ("sys", "System-specific parameters"),
        ("json", "JSON encoder/decoder"),
        ("asyncio", "Asynchronous programming"),
        
        # Core Web Framework
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        
        # Database modules
        ("sqlalchemy", "SQL toolkit and ORM"),
        ("psycopg2", "PostgreSQL adapter"),
        
        # Authentication & Security
        ("passlib", "Password hashing"),
        ("bcrypt", "Password hashing"),
        ("jose", "JWT tokens"),
        
        # Network Automation
        ("netmiko", "Network device automation"),
        
        # HTTP & WebSockets
        ("aiohttp", "Async HTTP client/server"),
        ("httpx", "HTTP client"),
        ("websockets", "WebSocket implementation"),
        
        # Utilities
        ("dotenv", "Environment variables"),
        
        # Application modules - Core
        ("backend", "Backend package"),
        ("backend.api", "API routes"),
        ("backend.database", "Database layer"),
        ("backend.auth", "Authentication"),
        ("backend.utils", "Utilities"),
        
        # Application modules - Features
        ("backend.ai", "AI services"),
        ("backend.devices", "Device management"),
        ("backend.automation", "Network automation"),
        ("backend.operations", "Operations management"),
        ("backend.chat", "Chat/WebSocket"),
        ("backend.dashboard", "Dashboard"),
        ("backend.settings", "Settings management"),
        
        # Main application
        ("main", "Main FastAPI application"),
    ]
    
    # Run tests
    results = []
    for module_name, description in test_modules:
        success, message = test_import(module_name, description)
        results.append((success, message))
        print(message)
    
    # Summary
    print()
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for success, _ in results if success)
    total = len(results)
    failed = total - successful
    
    print(f"✅ Successful imports: {successful}/{total}")
    if failed > 0:
        print(f"❌ Failed imports: {failed}/{total}")
        print("\nFailed modules:")
        for success, message in results:
            if not success:
                print(f"  {message}")
    else:
        print("🎉 All modules imported successfully!")
    
    print()
    
    # Test specific functionality
    print("=" * 80)
    print("🔧 FUNCTIONALITY TESTS")
    print("=" * 80)
    
    # Test FastAPI app creation
    try:
        from main import app
        print("✅ FastAPI app instance created successfully")
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}")
    
    # Test database connection setup
    try:
        from backend.database.connection import get_database_url
        db_url = get_database_url()
        print(f"✅ Database configuration loaded")
        print(f"   Database URL pattern: {db_url[:20]}...")
    except Exception as e:
        print(f"❌ Failed to load database configuration: {e}")
    
    # Test LLM manager
    try:
        from backend.ai.llm_manager import llm_manager
        print("✅ LLM manager initialized")
        providers = llm_manager.list_providers()
        print(f"   Available providers: {len(providers)}")
    except Exception as e:
        print(f"❌ Failed to initialize LLM manager: {e}")
    
    print()
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
