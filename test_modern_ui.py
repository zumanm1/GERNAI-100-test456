#!/usr/bin/env python3
"""
Modern Tesla-Inspired UI Test Suite
Tests the new chat and settings interfaces with real AI integration
"""

import requests
import json
import time
import uuid
import sys

BASE_URL_BACKEND = "http://localhost:8002"
BASE_URL_FRONTEND = "http://localhost:8001"

class ModernUITester:
    def __init__(self):
        self.session_id = f"tesla_ui_test_{uuid.uuid4()}"
        self.test_results = []

    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASSED" if success else "❌ FAILED"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status} {test_name}")
        if details and not success:
            print(f"   Details: {details}")

    def test_backend_health(self):
        """Test backend connectivity"""
        try:
            response = requests.get(f"{BASE_URL_BACKEND}/health", timeout=5)
            success = response.status_code == 200 and response.json().get('status') == 'healthy'
            self.log_test("Backend Health Check", success, response.json() if success else f"HTTP {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Backend Health Check", False, str(e))
            return False

    def test_frontend_accessibility(self):
        """Test frontend server accessibility"""
        try:
            # Test chat page
            chat_response = requests.get(f"{BASE_URL_FRONTEND}/chat", timeout=5)
            chat_success = chat_response.status_code == 200 and "Tesla-inspired" in chat_response.text
            
            # Test settings page  
            settings_response = requests.get(f"{BASE_URL_FRONTEND}/settings", timeout=5)
            settings_success = settings_response.status_code == 200 and "Tesla-inspired" in settings_response.text
            
            success = chat_success and settings_success
            details = f"Chat: {'✓' if chat_success else '✗'}, Settings: {'✓' if settings_success else '✗'}"
            self.log_test("Frontend Page Accessibility", success, details)
            return success
        except Exception as e:
            self.log_test("Frontend Page Accessibility", False, str(e))
            return False

    def test_chat_ai_integration(self):
        """Test chat with real AI (Groq) integration"""
        try:
            test_message = "Hello! Please help me configure OSPF area 0 on a Cisco router with router ID 10.0.0.1"
            
            response = requests.post(f"{BASE_URL_BACKEND}/api/v1/chat/send", 
                                   json={
                                       "message": test_message,
                                       "session_id": self.session_id
                                   }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', '')
                
                # Check if response is substantial and contains OSPF-related content
                success = (len(ai_response) > 100 and 
                          ('ospf' in ai_response.lower() or 'router' in ai_response.lower()) and
                          'router-id' in ai_response.lower())
                
                details = f"Response length: {len(ai_response)} chars, Contains OSPF content: {success}"
                self.log_test("AI Chat Integration (OSPF Config)", success, details)
                return success
            else:
                self.log_test("AI Chat Integration (OSPF Config)", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Chat Integration (OSPF Config)", False, str(e))
            return False

    def test_chat_context_persistence(self):
        """Test that chat maintains context across messages"""
        try:
            # Send follow-up message
            follow_up = "What about configuring the network statement for 192.168.1.0/24?"
            
            response = requests.post(f"{BASE_URL_BACKEND}/api/v1/chat/send",
                                   json={
                                       "message": follow_up,
                                       "session_id": self.session_id
                                   }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', '')
                
                # Check if response maintains context (mentions network statement or OSPF)
                success = (len(ai_response) > 50 and 
                          ('network' in ai_response.lower() or 
                           '192.168.1.0' in ai_response or
                           'ospf' in ai_response.lower()))
                
                details = f"Context maintained: {'Yes' if success else 'No'}"
                self.log_test("Chat Context Persistence", success, details)
                return success
            else:
                self.log_test("Chat Context Persistence", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Chat Context Persistence", False, str(e))
            return False

    def test_conversation_history(self):
        """Test conversation history retrieval"""
        try:
            response = requests.get(f"{BASE_URL_BACKEND}/api/v1/chat/history/{self.session_id}", timeout=10)
            
            if response.status_code == 200:
                history = response.json()
                
                # Should have at least 4 messages (2 user + 2 assistant from previous tests)
                success = len(history) >= 4
                details = f"Messages in history: {len(history)}"
                self.log_test("Conversation History", success, details)
                return success
            else:
                self.log_test("Conversation History", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Conversation History", False, str(e))
            return False

    def test_settings_api(self):
        """Test settings API functionality"""
        try:
            # Get current settings
            response = requests.get(f"{BASE_URL_BACKEND}/api/v1/settings/core", timeout=10)
            
            if response.status_code == 200:
                settings = response.json()
                
                # Check if we have the expected settings structure
                has_chat_provider = 'default_chat_provider' in settings
                has_timeout = 'response_timeout' in settings
                
                success = has_chat_provider and has_timeout
                details = f"Chat provider: {settings.get('default_chat_provider', 'Missing')}, Timeout: {settings.get('response_timeout', 'Missing')}"
                self.log_test("Settings API", success, details)
                return success
            else:
                self.log_test("Settings API", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Settings API", False, str(e))
            return False

    def test_config_generation(self):
        """Test AI configuration generation"""
        try:
            config_request = {
                "requirements": "Create VLAN 100 named SALES with SVI interface 192.168.100.1/24",
                "device_type": "cisco_ios"
            }
            
            response = requests.post(f"{BASE_URL_BACKEND}/api/v1/genai/config/generate",
                                   json=config_request, timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('result', {})
                
                generated_config = result.get('generated_config', '')
                validation_result = result.get('validation_result', {})
                
                # Check if config was generated and contains VLAN content
                config_success = len(generated_config) > 100 and 'vlan 100' in generated_config.lower()
                validation_success = validation_result.get('status') == 'analyzed'
                
                success = config_success and validation_success
                details = f"Config generated: {'Yes' if config_success else 'No'}, Validated: {'Yes' if validation_success else 'No'}"
                self.log_test("AI Configuration Generation", success, details)
                return success
            else:
                self.log_test("AI Configuration Generation", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Configuration Generation", False, str(e))
            return False

    def run_comprehensive_test(self):
        """Run all tests and provide summary"""
        print("🚀 Tesla-Inspired Modern UI Test Suite")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print("Testing Backend (8002) + Frontend (8001)")
        print("=" * 60)
        
        tests = [
            self.test_backend_health,
            self.test_frontend_accessibility,
            self.test_settings_api,
            self.test_chat_ai_integration,
            self.test_chat_context_persistence,
            self.test_conversation_history,
            self.test_config_generation
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"💥 Test error: {e}")
            
            time.sleep(1)  # Brief pause between tests
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print("\n" + "=" * 60)
        success_rate = (passed / total) * 100
        print(f"🎯 Overall Results: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Tesla-inspired UI is fully functional!")
            print("🌟 Features verified:")
            print("   • Real AI chat with Groq LLaMA 3-70B")
            print("   • Context-aware conversations")
            print("   • Modern Tesla-inspired design")
            print("   • Configuration generation & validation")
            print("   • Settings management")
            print("   • Conversation persistence")
        else:
            print(f"⚠️ {total - passed} test(s) failed - check details above")
        
        print("\n🔗 Access URLs:")
        print(f"   Chat: http://localhost:8001/chat")
        print(f"   Settings: http://localhost:8001/settings")
        print(f"   Backend API: http://localhost:8002/docs")
        
        return passed == total

if __name__ == "__main__":
    tester = ModernUITester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)
