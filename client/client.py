"""
Legal Mind AI Chatbot
Pure chatbot UI that sends requests to MCP server
"""

import requests


def ask_question(question: str, server_url: str = "http://localhost:8000") -> str:
    """Send question to MCP server and return answer"""
    try:
        response = requests.post(
            f"{server_url}/query",
            json={"question": question}
        )
        response.raise_for_status()
        result = response.json()
        return result.get("answer", "No answer received")
    except:
        return "Error: Cannot connect to server"


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
