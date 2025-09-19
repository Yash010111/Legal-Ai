#!/usr/bin/env python3
"""
Startup script for Legal Mind AI MCP Server
"""

import subprocess
import sys
import os

def main():
    """Start the MCP server"""
    print("🚀 Starting Legal Mind AI MCP Server...")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Start the server
        subprocess.run([sys.executable, "-m", "mcp_server.server"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
