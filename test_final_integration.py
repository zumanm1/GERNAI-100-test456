#!/usr/bin/env python3
"""
Final Integration Test - Complete AI System with Real APIs

This test verifies:
1. Chat functionality with Groq API
2. Config generation with Groq API 
3. Config validation with Groq API
4. Conversation persistence
5. All API endpoints working correctly

Run with: python test_final_integration.py
"""

import requests
import json
import time
import sys
import uuid

BASE_URL = "http://localhost:8002"

def test_health_check():
    """Test backend health endpoint"""
    print("\n🏥 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health check passed: {data}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_chat_functionality():
    """Test AI chat with Groq"""
    print("\n💬 Testing Chat Functionality...")
    
    session_id = f"integration_test_{uuid.uuid4()}"
    
    # Test chat message
    chat_data = {
        "message": "Hello! Can you help me configure OSPF on a Cisco router?",
        "session_id": session_id
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/chat/send", json=chat_data)
    
    if response.status_code == 200:
        data = response.json()
        ai_response = data.get('response', '')
        print(f"✅ Chat response received ({len(ai_response)} chars): {ai_response[:200]}...")
        
        # Test follow-up question
        follow_up_data = {
            "message": "What about OSPF areas and their benefits?",
            "session_id": session_id
        }
        
        follow_up_response = requests.post(f"{BASE_URL}/api/v1/chat/send", json=follow_up_data)
        if follow_up_response.status_code == 200:
            follow_up_ai = follow_up_response.json().get('response', '')
            print(f"✅ Follow-up response received ({len(follow_up_ai)} chars): {follow_up_ai[:200]}...")
            
            # Test conversation history
            history_response = requests.get(f"{BASE_URL}/api/v1/chat/history/{session_id}")
            if history_response.status_code == 200:
                history = history_response.json()
                print(f"✅ Conversation history retrieved: {len(history)} messages")
                return True
        
    print(f"❌ Chat test failed: {response.status_code}")
    return False

def test_config_generation():
    """Test AI config generation with Groq"""
    print("\n⚙️ Testing Configuration Generation...")
    
    config_data = {
        "requirements": "Configure OSPF area 0 with router ID 10.0.0.1, advertise network 192.168.1.0/24 and 10.0.0.0/8, and set hello interval to 5 seconds",
        "device_type": "cisco_ios"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/genai/config/generate", json=config_data)
    
    if response.status_code == 200:
        data = response.json()
        result = data.get('result', {})
        generated_config = result.get('generated_config', '')
        validation_result = result.get('validation_result', {})
        
        print(f"✅ Configuration generated ({len(generated_config)} chars)")
        print(f"📋 Config preview: {generated_config[:300]}...")
        
        if validation_result.get('status') == 'analyzed':
            analysis = validation_result.get('analysis', '')
            print(f"✅ Validation completed ({len(analysis)} chars)")
            print(f"🔍 Analysis preview: {analysis[:200]}...")
            return True
        else:
            print(f"⚠️ Validation status: {validation_result.get('status')}")
            return False
    
    print(f"❌ Config generation failed: {response.status_code}")
    return False

def test_backend_settings():
    """Test backend AI settings"""
    print("\n⚙️ Testing Backend Settings...")
    
    # Get current settings
    response = requests.get(f"{BASE_URL}/api/v1/settings/core")
    if response.status_code == 200:
        settings = response.json()
        chat_provider = settings.get('default_chat_provider', 'unknown')
        config_provider = settings.get('default_config_provider', 'unknown')
        print(f"✅ Current settings - Chat: {chat_provider}, Config: {config_provider}")
        return True
    else:
        print(f"❌ Settings retrieval failed: {response.status_code}")
        return False

def run_comprehensive_test():
    """Run all integration tests"""
    print("🚀 Starting Comprehensive AI Integration Test")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Backend Settings", test_backend_settings),
        ("Chat Functionality", test_chat_functionality),
        ("Config Generation", test_config_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
        
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! AI integration is fully functional!")
        return True
    else:
        print(f"❌ {total - passed} test(s) failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
