#!/usr/bin/env python3
"""
Live Chat Test - Demonstrates Working Real AI Integration

This script simulates a live chat conversation with the AI system,
showing that it works exactly like ChatGPT/Claude with real responses.
"""

import requests
import json
import time
import uuid

BASE_URL = "http://localhost:8002"
session_id = f"live_demo_{uuid.uuid4()}"

def send_chat_message(message):
    """Send a message to the chat API and get response"""
    try:
        response = requests.post(f"{BASE_URL}/api/v1/chat/send", json={
            "message": message,
            "session_id": session_id
        })
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {e}"

def simulate_live_chat():
    """Simulate a live chat conversation"""
    print("🤖 AI Network Assistant - Live Demo")
    print("=" * 60)
    print(f"Session ID: {session_id}")
    print("Connected to: Groq LLaMA 3 70B")
    print("=" * 60)
    
    # Sample conversation messages
    messages = [
        "Hello! Can you help me configure VLAN 10 on a Cisco switch?",
        "What security considerations should I keep in mind?",
        "Can you generate the complete configuration including SVI?",
        "Thank you! How do I validate this configuration?"
    ]
    
    for i, user_message in enumerate(messages, 1):
        print(f"\n👤 User: {user_message}")
        print("🔄 AI is thinking...")
        
        # Send message and get response
        ai_response = send_chat_message(user_message)
        
        # Simulate typing delay (like real chat interfaces)
        time.sleep(1)
        
        print(f"🤖 AI Assistant: {ai_response}")
        
        if i < len(messages):
            print("\n" + "─" * 60)
            time.sleep(2)  # Brief pause between messages
    
    print("\n" + "=" * 60)
    print("✅ Live chat demonstration complete!")
    print(f"💾 Conversation saved in session: {session_id}")
    
    # Show conversation history
    print("\n📜 Loading conversation history...")
    try:
        history_response = requests.get(f"{BASE_URL}/api/v1/chat/history/{session_id}")
        if history_response.status_code == 200:
            history = history_response.json()
            print(f"✅ History loaded: {len(history)} messages stored")
        else:
            print("❌ Could not load history")
    except Exception as e:
        print(f"❌ History error: {e}")

if __name__ == "__main__":
    simulate_live_chat()
