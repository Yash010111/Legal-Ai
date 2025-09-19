#!/usr/bin/env python3
"""
Ngrok client for Legal Mind AI MCP Server
Configure this for connecting via ngrok tunnel
"""

import requests
import json
from typing import Dict, Any, Optional

# CONFIGURATION - Update this with your ngrok URL
NGROK_URL = "https://your-tunnel-id.ngrok.io"  # Replace with your actual ngrok URL
SERVER_URL = NGROK_URL
MCP_ENDPOINT = f"{SERVER_URL}/mcp"
HEALTH_ENDPOINT = f"{SERVER_URL}/health"

class NgrokLegalMindClient:
    """Ngrok client for Legal Mind AI MCP Server"""
    
    def __init__(self, ngrok_url: str = NGROK_URL):
        self.server_url = ngrok_url
        self.mcp_endpoint = f"{ngrok_url}/mcp"
        self.health_endpoint = f"{ngrok_url}/health"
        self.request_id = 1
    
    def _get_next_id(self) -> int:
        """Get next request ID"""
        current_id = self.request_id
        self.request_id += 1
        return current_id
    
    def test_connection(self) -> bool:
        """Test connection to the ngrok server"""
        try:
            response = requests.get(self.health_endpoint, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def ask_question_mcp(self, question: str, context: str = "") -> str:
        """Send question using MCP protocol via ngrok"""
        try:
            request_data = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "tools/call",
                "params": {
                    "name": "ask_legal_question",
                    "arguments": {
                        "question": question,
                        "context": context
                    }
                }
            }
            
            response = requests.post(
                self.mcp_endpoint,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=15  # Longer timeout for ngrok
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                return f"Error: {result['error'].get('message', 'Unknown error')}"
            
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if content and len(content) > 0:
                    return content[0].get("text", "No answer received")
            
            return "No answer received"
            
        except requests.exceptions.Timeout:
            return "Error: Request timed out - ngrok tunnel may be slow"
        except requests.exceptions.ConnectionError:
            return f"Error: Cannot connect to ngrok tunnel at {self.server_url}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def analyze_document(self, document_text: str) -> str:
        """Analyze a legal document using MCP protocol via ngrok"""
        try:
            request_data = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "tools/call",
                "params": {
                    "name": "analyze_legal_document",
                    "arguments": {
                        "document_text": document_text
                    }
                }
            }
            
            response = requests.post(
                self.mcp_endpoint,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                return f"Error: {result['error'].get('message', 'Unknown error')}"
            
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if content and len(content) > 0:
                    return content[0].get("text", "No analysis received")
            
            return "No analysis received"
            
        except Exception as e:
            return f"Error: Cannot analyze document - {str(e)}"
    
    def search_database(self, query: str) -> str:
        """Search the legal database using MCP protocol via ngrok"""
        try:
            request_data = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "tools/call",
                "params": {
                    "name": "search_legal_database",
                    "arguments": {
                        "query": query
                    }
                }
            }
            
            response = requests.post(
                self.mcp_endpoint,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                return f"Error: {result['error'].get('message', 'Unknown error')}"
            
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if content and len(content) > 0:
                    return content[0].get("text", "No results found")
            
            return "No results found"
            
        except Exception as e:
            return f"Error: Cannot search database - {str(e)}"

def main():
    """Main ngrok client interface"""
    print("🌐 Legal Mind AI Ngrok Client")
    print("=" * 50)
    print(f"🔗 Connecting to ngrok tunnel: {NGROK_URL}")
    
    # Initialize client
    client = NgrokLegalMindClient()
    
    # Test connection
    print("🔌 Testing connection to ngrok tunnel...")
    if client.test_connection():
        print("✅ Connected to Legal Mind AI MCP Server via ngrok")
    else:
        print("❌ Cannot connect to ngrok tunnel.")
        print(f"   Please check:")
        print(f"   1. Ngrok is running: ngrok http 8000")
        print(f"   2. Server is running: python -m mcp_server.server")
        print(f"   3. Ngrok URL is correct: {NGROK_URL}")
        print(f"   4. Update NGROK_URL in this file with the correct URL")
        return
    
    print("\n📋 Available commands:")
    print("  - Ask any legal question")
    print("  - Type 'analyze <document_text>' to analyze a document")
    print("  - Type 'search <query>' to search the legal database")
    print("  - Type 'quit' to exit")
    print("\nAsk me any legal questions! Type 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.startswith('analyze '):
                document_text = user_input[8:].strip()
                if document_text:
                    print("🤖 Legal Mind AI: ", end="", flush=True)
                    result = client.analyze_document(document_text)
                    print(result)
                else:
                    print("Please provide document text to analyze.")
                print()
                continue
            
            if user_input.startswith('search '):
                query = user_input[7:].strip()
                if query:
                    print("🤖 Legal Mind AI: ", end="", flush=True)
                    result = client.search_database(query)
                    print(result)
                else:
                    print("Please provide a search query.")
                print()
                continue
            
            # Regular question
            print("🤖 Legal Mind AI: ", end="", flush=True)
            answer = client.ask_question_mcp(user_input)
            print(answer)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
