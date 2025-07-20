#!/usr/bin/env python3
"""
🤖 MCP AI System Test
Tests MCP AI integration endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8002/api/v1"
TEST_USER_ID = "11111111-1111-1111-1111-111111111111"

def test_mcp_ai_health():
    """Test MCP AI health endpoint"""
    print("\n🏥 Testing MCP AI Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/mcp-ai/health")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ MCP AI Health Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Check readiness
            if data.get('mcp_ready', False):
                print("🟢 MCP AI System READY!")
            else:
                print("🟡 MCP AI System NOT READY")
                print(f"   - Gemini API: {'✅' if data.get('gemini_api_configured') else '❌'}")
                print(f"   - Prompt File: {'✅' if data.get('prompt_file_exists') else '❌'}")
        else:
            print(f"❌ Health check failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_prompt_status():
    """Test prompt file status"""
    print("\n📄 Testing Prompt File Status...")
    
    try:
        response = requests.get(f"{BASE_URL}/mcp-ai/prompt/status")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Prompt Status Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('exists', False):
                print(f"📝 Prompt file ready: {data.get('content_length', 0)} characters")
            else:
                print("📝 Prompt file NOT FOUND")
        else:
            print(f"❌ Prompt status failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Prompt status error: {e}")

def test_create_prompt():
    """Test creating default prompt"""
    print("\n📝 Testing Create Default Prompt...")
    
    try:
        response = requests.post(f"{BASE_URL}/mcp-ai/prompt/create")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Prompt Creation Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Prompt creation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Prompt creation error: {e}")

def test_generate_ai_suggestion():
    """Test AI suggestion generation"""
    print(f"\n🤖 Testing AI Suggestion Generation for user: {TEST_USER_ID}")
    
    try:
        response = requests.post(f"{BASE_URL}/mcp-ai/{TEST_USER_ID}/generate")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ AI Generation Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success', False):
                print(f"🎯 Suggestion ID: {data.get('suggestion_id')}")
                print(f"💬 Suggestion: {data.get('suggestion_text', '')[:100]}...")
                print(f"📊 MCP Status: {data.get('mcp_status')}")
            else:
                print(f"❌ Generation failed: {data.get('error')}")
        else:
            print(f"❌ AI generation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ AI generation error: {e}")

def test_get_suggestions():
    """Test getting AI suggestions"""
    print(f"\n📋 Testing Get AI Suggestions for user: {TEST_USER_ID}")
    
    try:
        response = requests.get(f"{BASE_URL}/mcp-ai/{TEST_USER_ID}/suggestions")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Get Suggestions Response:")
            print(f"📊 Total Count: {data.get('total_count', 0)}")
            print(f"📊 MCP Status: {data.get('mcp_status')}")
            
            suggestions = data.get('suggestions', [])
            for i, suggestion in enumerate(suggestions[:3], 1):  # Show first 3
                print(f"\n{i}. 💬 {suggestion.get('text', '')[:80]}...")
                print(f"   📅 {suggestion.get('date')} | 👁️ {'Read' if suggestion.get('is_read') else 'Unread'}")
                
        else:
            print(f"❌ Get suggestions failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Get suggestions error: {e}")

def main():
    """Run all MCP AI tests"""
    print("🌳 MCP AI System Test Suite")
    print("=" * 50)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"👤 Test User: {TEST_USER_ID}")
    
    # Run tests in sequence
    test_mcp_ai_health()
    test_prompt_status()
    
    # Create prompt if needed
    response = requests.get(f"{BASE_URL}/mcp-ai/prompt/status")
    if response.status_code == 200 and not response.json().get('exists', False):
        test_create_prompt()
    
    test_generate_ai_suggestion()
    test_get_suggestions()
    
    print("\n" + "=" * 50)
    print("🎉 MCP AI Test Suite Completed!")
    print("\n💡 Next Steps:")
    print("1. Update prompts/ai_prompt.txt with your custom prompt")
    print("2. Set GEMINI_API_KEY environment variable")
    print("3. Start MCP server integration")
    print("4. Test with frontend calls")

if __name__ == "__main__":
    main() 