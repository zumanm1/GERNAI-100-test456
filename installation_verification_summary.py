#!/usr/bin/env python3
"""
Installation Verification Summary

This script runs all verification tests and provides a comprehensive summary.
"""

import sys
import subprocess
import json
from datetime import datetime
import os

def run_test_script(script_name, description):
    """Run a test script and capture results."""
    print(f"\n{'='*80}")
    print(f"🔍 RUNNING: {description}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        success = result.returncode == 0
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status}: {description}")
        
        return success, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT: {description} took too long to complete")
        return False, "", "Timeout expired"
    except Exception as e:
        print(f"❌ ERROR running {description}: {e}")
        return False, "", str(e)

def test_uvicorn_server():
    """Test that uvicorn can start the server."""
    print(f"\n{'='*80}")
    print(f"🔍 RUNNING: FastAPI Server Test")
    print(f"{'='*80}")
    
    try:
        # Test server startup
        test_code = '''
import uvicorn
from main import app
import threading
import time
import requests

def run_server():
    try:
        uvicorn.run(app, host="127.0.0.1", port=8003, log_level="error")
    except Exception:
        pass

print("Starting server test...")
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# Wait for server to start
time.sleep(2)

try:
    response = requests.get("http://127.0.0.1:8003/health", timeout=5)
    if response.status_code == 200:
        print("✅ Server responds to health check")
        data = response.json()
        print(f"   Status: {data.get('status', 'unknown')}")
        print(f"   Service: {data.get('service', 'unknown')}")
        exit(0)
    else:
        print(f"❌ Server health check failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Server test failed: {e}")
    exit(1)
'''
        
        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        success = result.returncode == 0
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status}: FastAPI Server Test")
        
        return success, result.stdout, result.stderr
        
    except Exception as e:
        print(f"❌ ERROR running server test: {e}")
        return False, "", str(e)

def main():
    """Main verification function."""
    print("=" * 120)
    print("🚀 COMPREHENSIVE INSTALLATION VERIFICATION")
    print("=" * 120)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    print(f"📂 Working Directory: {os.getcwd()}")
    print()
    
    # Define all tests to run
    tests = [
        ("test_installation.py", "Module Import Tests"),
        ("test_database_connection.py", "Database Connection Tests"),
    ]
    
    # Run all tests
    results = []
    
    for script, description in tests:
        success, stdout, stderr = run_test_script(script, description)
        results.append((description, success, stdout, stderr))
    
    # Run server test
    success, stdout, stderr = test_uvicorn_server()
    results.append(("FastAPI Server Test", success, stdout, stderr))
    
    # Final Summary
    print(f"\n{'='*120}")
    print("📊 FINAL VERIFICATION SUMMARY")
    print(f"{'='*120}")
    
    passed = sum(1 for _, success, _, _ in results if success)
    total = len(results)
    
    print(f"📈 Overall Results: {passed}/{total} test suites passed\n")
    
    for description, success, _, _ in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {description}")
    
    print()
    
    if passed == total:
        print("🎉 INSTALLATION VERIFICATION SUCCESSFUL!")
        print("✨ All systems are operational and ready for use")
        print()
        print("Next steps:")
        print("  1. Configure your environment variables (.env file)")
        print("  2. Set up API keys for LLM providers (optional)")
        print("  3. Start the application: python main.py")
        print("  4. Access the API at: http://localhost:8002")
        return True
    else:
        print("⚠️  INSTALLATION VERIFICATION INCOMPLETE")
        print(f"   {total - passed} test suite(s) failed")
        print()
        print("Please review the failed tests above and address any issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
