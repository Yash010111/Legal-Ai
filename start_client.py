#!/usr/bin/env python3
"""
Startup script for Legal Mind AI Client
"""

import subprocess
import sys
import os

def main():
    """Start the client with options"""
    print("🤖 Legal Mind AI Client Launcher")
    print("=" * 50)
    print("Choose client type:")
    print("1. Local client (localhost)")
    print("2. Ngrok client (remote via ngrok)")
    print("3. Network client (remote via IP)")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting local client...")
                subprocess.run([sys.executable, "client/client.py"], check=True)
                break
            elif choice == "2":
                print("\n🌐 Starting ngrok client...")
                print("Make sure to update the NGROK_URL in client/ngrok_client.py")
                subprocess.run([sys.executable, "client/ngrok_client.py"], check=True)
                break
            elif choice == "3":
                print("\n🌐 Starting network client...")
                print("Make sure to update the SERVER_IP in client/remote_client.py")
                subprocess.run([sys.executable, "client/remote_client.py"], check=True)
                break
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except subprocess.CalledProcessError as e:
            print(f"❌ Error starting client: {e}")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            break

if __name__ == "__main__":
    main()
