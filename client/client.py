"""
Legal Mind AI Chatbot
Pure chatbot UI that sends requests to MCP server
"""

import requests
import json


def ask_question_server(question: str, server_url: str = "https://a9b58c306cc2.ngrok-free.app") -> str:
    """Send question to MCP server and return answer"""
    try:
        response = requests.post(
            f"{server_url}/query",
            json={"question": question},
            headers={"ngrok-skip-browser-warning": "true"},
            timeout=10  # Add timeout to prevent hanging
        )
        response.raise_for_status()
        result = response.json()
        
        # Safe access to result with proper error handling
        if result and isinstance(result, dict):
            answer = result.get('answer', 'No answer received')
            return f"🤖 AI Response: {answer}"
        else:
            return f"Invalid response from server: {result}"
            
    except requests.exceptions.Timeout:
        return "Error: Server request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to server. Server may be offline."
    except requests.exceptions.RequestException as e:
        return f"Error: Server request failed - {str(e)}"
    except json.JSONDecodeError:
        return "Error: Invalid response format from server."
    except Exception as e:
        return f"Error: Unexpected error - {str(e)}"


def ask_question(question: str, server_url: str = "https://a9b58c306cc2.ngrok-free.app") -> str:
    """Ask question using MCP server"""
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