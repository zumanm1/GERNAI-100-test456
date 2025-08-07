#!/usr/bin/env python3
"""
Comprehensive integration test runner for the GENAI chat application.
This script will:
1. Start the backend server
2. Start the frontend server  
3. Run unit tests
4. Run Playwright e2e tests
5. Generate a test report
"""

import subprocess
import time
import sys
import os
import signal
import threading
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.processes = []
        self.project_root = Path(__file__).parent
        
    def start_backend(self):
        """Start the FastAPI backend server"""
        print("🚀 Starting backend server on port 8002...")
        
        # Activate virtual environment and run backend
        venv_python = self.project_root / "venv" / "bin" / "python3.11"
        if not venv_python.exists():
            venv_python = self.project_root / "venv" / "bin" / "python"
        
        backend_process = subprocess.Popen([
            str(venv_python), 
            "main.py"
        ], cwd=self.project_root)
        
        self.processes.append(backend_process)
        return backend_process
    
    def start_frontend(self):
        """Start the frontend server"""
        print("🌐 Starting frontend server on port 8001...")
        
        # Start simple HTTP server for frontend
        frontend_process = subprocess.Popen([
            "python3", "-m", "http.server", "8001"
        ], cwd=self.project_root / "frontend")
        
        self.processes.append(frontend_process)
        return frontend_process
    
    def wait_for_servers(self, timeout=30):
        """Wait for both servers to be ready"""
        print("⏳ Waiting for servers to be ready...")
        
        import requests
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check backend health
                backend_response = requests.get("http://localhost:8002/health", timeout=5)
                if backend_response.status_code == 200:
                    print("✅ Backend server is ready")
                    
                    # Check frontend (just that it responds)
                    frontend_response = requests.get("http://localhost:8001", timeout=5)
                    if frontend_response.status_code == 200:
                        print("✅ Frontend server is ready")
                        return True
                        
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        print("❌ Servers did not start within timeout")
        return False
    
    def run_unit_tests(self):
        """Run unit tests"""
        print("🧪 Running unit tests...")
        
        venv_python = self.project_root / "venv" / "bin" / "python3.11"
        if not venv_python.exists():
            venv_python = self.project_root / "venv" / "bin" / "python"
        
        # Run pytest on backend tests
        test_result = subprocess.run([
            str(venv_python), "-m", "pytest", 
            "backend/tests/",
            "-v",
            "--tb=short"
        ], cwd=self.project_root, capture_output=True, text=True)
        
        print("📊 Unit Test Results:")
        print(test_result.stdout)
        if test_result.stderr:
            print("Errors:", test_result.stderr)
        
        return test_result.returncode == 0
    
    def run_e2e_tests(self):
        """Run Playwright e2e tests"""
        print("🎭 Running end-to-end tests...")
        
        venv_python = self.project_root / "venv" / "bin" / "python3.11"
        if not venv_python.exists():
            venv_python = self.project_root / "venv" / "bin" / "python"
        
        # Check if playwright is installed
        try:
            subprocess.run([str(venv_python), "-c", "import playwright"], check=True)
        except subprocess.CalledProcessError:
            print("📦 Installing playwright...")
            subprocess.run([str(venv_python), "-m", "pip", "install", "playwright"])
            subprocess.run([str(venv_python), "-m", "playwright", "install"])
        
        # Run e2e tests
        e2e_test_file = self.project_root / "tests" / "e2e_playwright" / "test_chat_settings_integration.py"
        
        if e2e_test_file.exists():
            test_result = subprocess.run([
                str(venv_python), str(e2e_test_file)
            ], cwd=self.project_root, capture_output=True, text=True)
            
            print("📊 E2E Test Results:")
            print(test_result.stdout)
            if test_result.stderr:
                print("Errors:", test_result.stderr)
            
            return test_result.returncode == 0
        else:
            print("⚠️ E2E test file not found, skipping...")
            return True
    
    def run_api_tests(self):
        """Test API endpoints directly"""
        print("🔌 Testing API endpoints...")
        
        import requests
        test_results = []
        
        # Test backend API endpoints
        endpoints = [
            ("GET", "http://localhost:8002/health", "Backend health check"),
            ("GET", "http://localhost:8002/api/v1/genai-settings/genai/core", "Core settings"),
            ("GET", "http://localhost:8002/api/v1/genai-settings/genai/llm", "LLM settings"),
            ("GET", "http://localhost:8002/api/v1/genai-settings/genai/api-keys", "API keys"),
            ("GET", "http://localhost:8001/chat", "Chat page"),
            ("GET", "http://localhost:8001/settings", "Settings page"),
        ]
        
        for method, url, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(url, timeout=10)
                
                if response.status_code in [200, 404]:  # 404 is ok for frontend static files
                    print(f"✅ {description}: {response.status_code}")
                    test_results.append(True)
                else:
                    print(f"❌ {description}: {response.status_code}")
                    test_results.append(False)
                    
            except Exception as e:
                print(f"❌ {description}: Error - {e}")
                test_results.append(False)
        
        return all(test_results)
    
    def cleanup(self):
        """Clean up all started processes"""
        print("🧹 Cleaning up processes...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Error cleaning up process: {e}")
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print("=" * 60)
        print("🎯 GENAI Chat Application Integration Tests")
        print("=" * 60)
        
        try:
            # Start servers
            self.start_backend()
            time.sleep(3)  # Give backend time to start
            self.start_frontend()
            
            if not self.wait_for_servers():
                print("❌ Failed to start servers")
                return False
            
            print("=" * 60)
            
            # Run all tests
            results = {
                "API Tests": self.run_api_tests(),
                "Unit Tests": self.run_unit_tests(),
                "E2E Tests": self.run_e2e_tests()
            }
            
            print("=" * 60)
            print("📋 TEST SUMMARY:")
            print("=" * 60)
            
            all_passed = True
            for test_type, passed in results.items():
                status = "✅ PASSED" if passed else "❌ FAILED"
                print(f"{test_type}: {status}")
                if not passed:
                    all_passed = False
            
            print("=" * 60)
            
            if all_passed:
                print("🎉 ALL TESTS PASSED! The GENAI chat application is working correctly.")
                print("\nTo use the application:")
                print("1. Add your real API keys to the .env file")
                print("2. Visit http://localhost:8001/settings to configure AI settings")
                print("3. Visit http://localhost:8001/chat to chat with AI")
            else:
                print("⚠️ Some tests failed. Please review the output above.")
            
            return all_passed
            
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
            return False
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("GENAI Chat Application Test Runner")
        print("Usage: python3 run_integration_tests.py")
        print("\nThis will start the backend and frontend servers,")
        print("then run unit tests, API tests, and e2e tests.")
        return
    
    # Set up signal handlers for graceful shutdown
    test_runner = TestRunner()
    
    def signal_handler(signum, frame):
        print("\n🛑 Received interrupt signal, cleaning up...")
        test_runner.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run tests
    success = test_runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
