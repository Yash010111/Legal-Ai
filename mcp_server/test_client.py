#!/usr/bin/env python3
"""
Test script to verify MCP communication between server and client
"""

import requests
import json
import time

def test_mcp_initialization():
    """Test MCP initialization"""
    print("🔧 Testing MCP Initialization...")
    
    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        #Enter the custom ngrok url if you are using ngrok
        #Otherwise, use the localhost url
        url_of_the_server = "http://localhost:8000/mcp"
        response = requests.post(
            url_of_the_server,
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Initialization successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

def test_mcp_tools_list():
    """Test MCP tools list"""
    print("\n🛠️ Testing MCP Tools List...")
    
    request_data = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/mcp",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Tools list retrieved: {len(result['result']['tools'])} tools available")
        for tool in result['result']['tools']:
            print(f"  - {tool['name']}: {tool['description']}")
        return True
    except Exception as e:
        print(f"❌ Tools list failed: {e}")
        return False

def test_mcp_ask_question():
    """Test MCP ask question tool"""
    print("\n❓ Testing MCP Ask Question...")
    
    request_data = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "ask_legal_question",
            "arguments": {
                "question": "What is contract law?",
                "context": "General legal question"
            }
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/mcp",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            print(f"❌ Ask question failed: {result['error']}")
            return False
        
        print(f"✅ Ask question successful:")
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"][0]["text"]
            print(f"  Answer: {content}")
        return True
    except Exception as e:
        print(f"❌ Ask question failed: {e}")
        return False

def test_server_health():
    """Test server health endpoint"""
    print("🏥 Testing Server Health...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Server is healthy: {result}")
        return True
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False

def main():
    """Run all MCP communication tests"""
    print("🧪 Legal Mind AI MCP Communication Test")
    print("=" * 50)
    
    # Test server health first
    if not test_server_health():
        print("\n❌ Server is not running. Please start the server first:")
        print("   python -m mcp_server.server")
        return
    
    # Run MCP tests
    tests = [
        test_mcp_initialization,
        test_mcp_tools_list,
        test_mcp_ask_question
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All MCP communication tests passed!")
        print("✅ Your server is ready to work with MCP clients.")
    else:
        print("⚠️ Some tests failed. Check the server logs for details.")

if __name__ == "__main__":
    main()
