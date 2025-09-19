"""
Legal Mind AI Chatbot
Pure chatbot UI that sends requests to MCP server and uses local retrieval
"""

import requests
import sys
import os

# Add helpers to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'helpers'))

from retrieval import answer_legal_question, search_legal_database


def ask_question_local(question: str) -> str:
    """Try to answer question using local JSON data first"""
    try:
        answer = answer_legal_question(question)
        if answer and "don't have specific information" not in answer:
            return f"📚 Local Knowledge: {answer}"
        return None
    except Exception as e:
        return None


def ask_question_server(question: str, server_url: str = "https://a9b58c306cc2.ngrok-free.app") -> str:
    """Send question to MCP server and return answer"""
    try:
        response = requests.post(
            f"{server_url}/query",
            json={"question": question},
            headers={"ngrok-skip-browser-warning": "true"}
        )
        response.raise_for_status()
        result = response.json()
        
        # Safe access to result with proper error handling
        if result and isinstance(result, dict):
            return f"🤖 AI Response: {result.get('answer', 'No answer received')}"
        else:
            return f"Invalid response from server: {result}"
            
    except requests.exceptions.RequestException as e:
        return f"Error: Cannot connect to server - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


def ask_question(question: str, server_url: str = "https://a9b58c306cc2.ngrok-free.app") -> str:
    """Ask question using local data first, then server as fallback"""
    # Try local retrieval first
    local_answer = ask_question_local(question)
    if local_answer:
        return local_answer
    
    # Fallback to server
    return ask_question_server(question, server_url)


def main():
    """Pure chatbot UI"""
    print("🤖 Legal Mind AI Chatbot")
    print("Ask me any legal questions! Type 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("🤖 Legal Mind AI: ", end="", flush=True)
            answer = ask_question(user_input)
            print(answer)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()