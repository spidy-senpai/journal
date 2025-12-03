#!/usr/bin/env python3
"""
Fumiko AI Integration Test Script
Tests all Fumiko API endpoints and functionality
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
SESSION_COOKIE = None  # Set this after login

def log_test(test_name, passed, message=""):
    """Log test results"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"   → {message}")

def login_user(email, password):
    """Log in and get session cookie"""
    global SESSION_COOKIE
    try:
        response = requests.post(f"{BASE_URL}/login", data={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            SESSION_COOKIE = response.cookies.get('session')
            log_test("User Login", True, "Session obtained")
            return True
        else:
            log_test("User Login", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("User Login", False, str(e))
        return False

def get_headers():
    """Get request headers with session"""
    return {
        'Content-Type': 'application/json',
        'Cookie': f'session={SESSION_COOKIE}' if SESSION_COOKIE else ''
    }

def test_fumiko_context():
    """Test GET /api/fumiko-context"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/fumiko-context",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            passed = data.get('success', False)
            
            log_test("GET /api/fumiko-context", passed)
            if passed:
                print(f"   → Past entries: {data['past_entries_count']}")
                print(f"   → Has profile: {data['virtual_profile']['has_profile']}")
                print(f"   → Chat history: {data['chat_history_count']}")
            
            return passed, data if passed else None
        else:
            log_test("GET /api/fumiko-context", False, f"Status: {response.status_code}")
            return False, None
    except Exception as e:
        log_test("GET /api/fumiko-context", False, str(e))
        return False, None

def test_fumiko_chat(message):
    """Test POST /api/fumiko-chat"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/fumiko-chat",
            headers=get_headers(),
            json={
                "message": message,
                "chat_id": "test"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            passed = data.get('success', False)
            
            log_test(f"POST /api/fumiko-chat - '{message[:30]}...'", passed)
            if passed:
                print(f"   → Response: {data['response'][:100]}...")
                print(f"   → Context provided: {data['context_provided']}")
            
            return passed, data if passed else None
        else:
            log_test(f"POST /api/fumiko-chat", False, f"Status: {response.status_code}")
            print(f"   → Response: {response.text[:200]}")
            return False, None
    except Exception as e:
        log_test(f"POST /api/fumiko-chat", False, str(e))
        return False, None

def test_fumiko_history(limit=10):
    """Test GET /api/fumiko-history"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/fumiko-history?limit={limit}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            passed = data.get('success', False)
            
            log_test("GET /api/fumiko-history", passed)
            if passed:
                print(f"   → Messages retrieved: {len(data['messages'])}")
                if data['messages']:
                    latest = data['messages'][-1]
                    print(f"   → Latest: {latest['message'][:50]}...")
            
            return passed, data if passed else None
        else:
            log_test("GET /api/fumiko-history", False, f"Status: {response.status_code}")
            return False, None
    except Exception as e:
        log_test("GET /api/fumiko-history", False, str(e))
        return False, None

def test_context_requirements():
    """Test what's needed for good Fumiko responses"""
    print("\n📋 Checking Requirements:")
    
    success, context = test_fumiko_context()
    
    if not success:
        print("❌ Cannot fetch context")
        return False
    
    checks = {
        "Has current entry": context['current_entry'] != 'No current entry',
        "Has past entries": context['past_entries_count'] > 0,
        "Has virtual profile": context['virtual_profile']['has_profile'],
        "Has chat history": context['chat_history_count'] > 0
    }
    
    for check, result in checks.items():
        status = "✅" if result else "⚠️"
        print(f"{status} {check}")
    
    return all(checks.values())

def test_conversation_flow():
    """Test a complete conversation flow"""
    print("\n💬 Testing Conversation Flow:")
    
    messages = [
        "I've been feeling stressed lately",
        "Can you help me understand why?",
        "What should I do about it?"
    ]
    
    all_passed = True
    for msg in messages:
        passed, response = test_fumiko_chat(msg)
        all_passed = all_passed and passed
        
        if passed:
            print(f"   Response received successfully")
        else:
            print(f"   ❌ Failed to get response")
    
    return all_passed

def test_api_error_handling():
    """Test error handling"""
    print("\n🛡️ Testing Error Handling:")
    
    # Test with empty message
    try:
        response = requests.post(
            f"{BASE_URL}/api/fumiko-chat",
            headers=get_headers(),
            json={"message": "", "chat_id": "test"}
        )
        log_test("Empty message handling", response.status_code == 400)
    except Exception as e:
        log_test("Empty message handling", False, str(e))
    
    # Test without authentication (requires fixing)
    try:
        response = requests.get(f"{BASE_URL}/api/fumiko-context")
        log_test("Auth protection", response.status_code != 200)
    except Exception as e:
        log_test("Auth protection", False, str(e))

def test_firestore_storage():
    """Test that messages are saved to Firestore"""
    print("\n💾 Testing Firestore Storage:")
    
    # Get initial history count
    _, history1 = test_fumiko_history(limit=100)
    count1 = len(history1['messages']) if history1 else 0
    
    # Send a message
    test_fumiko_chat("Test message for storage verification")
    
    # Wait a moment for database write
    import time
    time.sleep(1)
    
    # Get updated history count
    _, history2 = test_fumiko_history(limit=100)
    count2 = len(history2['messages']) if history2 else 0
    
    passed = count2 > count1
    log_test("Message saved to Firestore", passed, 
             f"Before: {count1}, After: {count2}")

def run_all_tests():
    """Run complete test suite"""
    print("=" * 60)
    print("🤖 FUMIKO AI INTEGRATION TEST SUITE")
    print("=" * 60)
    
    # Note: Update these credentials
    print("\n📝 Setup:")
    print("⚠️  Update test_email and test_password below before running")
    
    test_email = "test@example.com"  # UPDATE THIS
    test_password = "password"  # UPDATE THIS
    
    if not login_user(test_email, test_password):
        print("\n❌ Cannot proceed without login")
        return
    
    print("\n" + "=" * 60)
    print("🔍 Testing API Endpoints")
    print("=" * 60)
    
    # Test individual endpoints
    print("\n1️⃣ Context Endpoint:")
    test_fumiko_context()
    
    print("\n2️⃣ Chat Endpoint:")
    test_fumiko_chat("Hello Fumiko, how are you?")
    
    print("\n3️⃣ History Endpoint:")
    test_fumiko_history(limit=5)
    
    # Test requirements
    print("\n" + "=" * 60)
    print("📋 Checking Context Requirements")
    print("=" * 60)
    test_context_requirements()
    
    # Test conversation flow
    print("\n" + "=" * 60)
    print("💬 Conversation Flow")
    print("=" * 60)
    test_conversation_flow()
    
    # Test error handling
    print("\n" + "=" * 60)
    print("🛡️ Error Handling")
    print("=" * 60)
    test_api_error_handling()
    
    # Test storage
    print("\n" + "=" * 60)
    print("💾 Data Persistence")
    print("=" * 60)
    test_firestore_storage()
    
    print("\n" + "=" * 60)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
