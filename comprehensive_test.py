#!/usr/bin/env python3
"""
Comprehensive Test Suite for Network Automation Platform
Tests backend API, frontend integration, and AI services
"""

import requests
import json
import time
import sys
import os
from urllib.parse import urljoin

class NetworkAutomationTester:
    def __init__(self):
        self.backend_url = "http://localhost:8002"
        self.frontend_url = "http://localhost:8001"
        self.test_results = []
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"    Details: {details}")
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("Backend Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health", False, "Connection failed", str(e))
            return False
    
    def test_backend_api_root(self):
        """Test backend API root endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend API Root", True, f"Service: {data.get('service', 'unknown')}")
                return True
            else:
                self.log_test("Backend API Root", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend API Root", False, "Connection failed", str(e))
            return False
    
    def test_chat_status(self):
        """Test chat status endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/api/chat/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                providers = data.get('providers', {})
                active_providers = [k for k, v in providers.items() if v]
                self.log_test("Chat Status", True, f"Model: {data.get('model', 'unknown')}, Providers: {', '.join(active_providers)}")
                return True
            else:
                self.log_test("Chat Status", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Chat Status", False, "Connection failed", str(e))
            return False
    
    def test_chat_send(self):
        """Test chat send endpoint"""
        try:
            payload = {
                "message": "Hello, this is a test message for the API validation",
                "session_id": "test_session_validation"
            }
            response = requests.post(
                f"{self.backend_url}/api/v1/chat/send",
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                self.log_test("Chat Send", True, f"Response length: {len(response_text)} chars")
                return True
            else:
                self.log_test("Chat Send", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Chat Send", False, "Request failed", str(e))
            return False
    
    def test_frontend_chat_page(self):
        """Test frontend chat page loads"""
        try:
            response = requests.get(f"{self.frontend_url}/chat", timeout=10)
            if response.status_code == 200:
                content = response.text
                has_input = 'message-input' in content
                has_status = 'connection-status' in content
                has_model = 'model-status' in content
                
                if has_input and has_status and has_model:
                    self.log_test("Frontend Chat Page", True, "All required elements found")
                    return True
                else:
                    missing = []
                    if not has_input: missing.append('message-input')
                    if not has_status: missing.append('connection-status')
                    if not has_model: missing.append('model-status')
                    self.log_test("Frontend Chat Page", False, f"Missing elements: {', '.join(missing)}")
                    return False
            else:
                self.log_test("Frontend Chat Page", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Chat Page", False, "Connection failed", str(e))
            return False
    
    def test_frontend_settings_page(self):
        """Test frontend settings page loads"""
        try:
            response = requests.get(f"{self.frontend_url}/settings", timeout=10)
            if response.status_code == 200:
                content = response.text
                has_provider = 'model-provider' in content
                has_groq = 'groq' in content.lower()
                has_openrouter = 'openrouter' in content.lower()
                has_save = 'save-settings' in content
                
                if has_provider and has_groq and has_openrouter and has_save:
                    self.log_test("Frontend Settings Page", True, "All required elements found")
                    return True
                else:
                    missing = []
                    if not has_provider: missing.append('model-provider')
                    if not has_groq: missing.append('groq')
                    if not has_openrouter: missing.append('openrouter')
                    if not has_save: missing.append('save-settings')
                    self.log_test("Frontend Settings Page", False, f"Missing elements: {', '.join(missing)}")
                    return False
            else:
                self.log_test("Frontend Settings Page", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Settings Page", False, "Connection failed", str(e))
            return False
    
    def test_environment_variables(self):
        """Test that required environment variables are set"""
        try:
            # Check if we can read the .env file to verify keys are set
            env_file = "/home/vmuser/GENAI-113-DED/GERNAI-100-test456/.env"
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    env_content = f.read()
                
                has_groq = 'GROQ_API_KEY=' in env_content and 'gsk_' in env_content
                has_openrouter = 'OPENROUTER_API_KEY=' in env_content and 'sk-or-v1-' in env_content
                has_openai = 'OPENAI_API_KEY=' in env_content and 'sk-proj-' in env_content
                
                keys_found = []
                if has_groq: keys_found.append('Groq')
                if has_openrouter: keys_found.append('OpenRouter')
                if has_openai: keys_found.append('OpenAI')
                
                if keys_found:
                    self.log_test("Environment Variables", True, f"API keys found: {', '.join(keys_found)}")
                    return True
                else:
                    self.log_test("Environment Variables", False, "No valid API keys found in .env")
                    return False
            else:
                self.log_test("Environment Variables", False, ".env file not found")
                return False
        except Exception as e:
            self.log_test("Environment Variables", False, "Error reading .env file", str(e))
            return False
    
    def test_api_cors(self):
        """Test CORS headers are properly configured"""
        try:
            # Make an OPTIONS request to check CORS
            response = requests.options(
                f"{self.backend_url}/api/v1/chat/send",
                headers={
                    'Origin': 'http://localhost:8001',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                cors_origin = response.headers.get('Access-Control-Allow-Origin')
                cors_methods = response.headers.get('Access-Control-Allow-Methods')
                
                if cors_origin and cors_methods:
                    self.log_test("CORS Configuration", True, f"Origin: {cors_origin}")
                    return True
                else:
                    self.log_test("CORS Configuration", False, "CORS headers missing")
                    return False
            else:
                self.log_test("CORS Configuration", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("CORS Configuration", False, "Request failed", str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests and generate summary"""
        print("🚀 Starting Comprehensive Test Suite...")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_backend_health,
            self.test_backend_api_root,
            self.test_chat_status,
            self.test_environment_variables,
            self.test_api_cors,
            self.test_frontend_chat_page,
            self.test_frontend_settings_page,
            self.test_chat_send,  # Run this last as it takes the longest
        ]
        
        for test_func in tests:
            test_func()
            time.sleep(0.5)  # Brief pause between tests
        
        # Generate summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        pass_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({pass_rate:.1f}%)")
        
        if passed == total:
            print("🎉 All tests PASSED! The application is working correctly.")
            return True
        else:
            print("⚠️  Some tests FAILED. Please review the issues above.")
            failed_tests = [r for r in self.test_results if not r['success']]
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
            return False

if __name__ == "__main__":
    tester = NetworkAutomationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
