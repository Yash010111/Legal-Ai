"""
Legal Mind AI Chatbot
Enhanced client that supports both HTTP API and MCP protocol
"""

import requests
import json
import asyncio
from typing import Dict, Any, Optional


class LegalMindClient:
    """Client for Legal Mind AI MCP Server"""
    
    def __init__(self, server_url: str = "https://a9b58c306cc2.ngrok-free.app", use_mcp: bool = True):
        self.server_url = server_url
        self.use_mcp = use_mcp
        self.request_id = 1
    
    def _get_next_id(self) -> int:
        """Get next request ID"""
        current_id = self.request_id
        self.request_id += 1
        return current_id
    
    def ask_question_http(self, question: str, context: str = "") -> str:
        """Send question using HTTP API"""
        try:
            response = requests.post(
                f"{self.server_url}/query",
                json={"question": question, "context": context}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("answer", "No answer received")
        except Exception as e:
            return f"Error: Cannot connect to server - {str(e)}"
    
    def ask_question_mcp(self, question: str, context: str = "") -> str:
        """Send question using MCP protocol"""
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
                f"{self.server_url}/mcp",
                json=request_data,
                headers={"Content-Type": "application/json"}
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
            
        except Exception as e:
            return f"Error: Cannot connect to MCP server - {str(e)}"
    
    def ask_question(self, question: str, context: str = "") -> str:
        """Ask a legal question using the configured protocol"""
        if self.use_mcp:
            return self.ask_question_mcp(question, context)
        else:
            return self.ask_question_http(question, context)
    
    def analyze_document(self, document_text: str) -> str:
        """Analyze a legal document using MCP protocol"""
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
                f"{self.server_url}/mcp",
                json=request_data,
                headers={"Content-Type": "application/json"}
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
        """Search the legal database using MCP protocol"""
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
                f"{self.server_url}/mcp",
                json=request_data,
                headers={"Content-Type": "application/json"}
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
    
    def test_connection(self) -> bool:
        """Test connection to the server"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


def main():
    """Enhanced chatbot UI with MCP support"""
    print("🤖 Legal Mind AI Chatbot (MCP Enhanced)")
    print("=" * 50)
    
    # Initialize client
    client = LegalMindClient(use_mcp=True)
    
    # Test connection
    print("🔌 Testing connection to server...")
    if client.test_connection():
        print("✅ Connected to Legal Mind AI MCP Server")
    else:
        print("❌ Cannot connect to server. Please ensure the server is running.")
        print("   Run: python -m mcp_server.server")
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
            answer = client.ask_question(user_input)
            print(answer)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
