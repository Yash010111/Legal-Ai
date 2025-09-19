# 🏗️ Legal Mind AI - Client & Server Guide

## 📁 Project Structure

```
Legal-Ai/
├── mcp_server/                 # MCP Server Files
│   ├── __init__.py
│   ├── server.py              # Main MCP server
│   ├── routes.py              # API routes
│   └── test_mcp_communication.py  # Server tests
├── client/                     # Client Files
│   ├── __init__.py
│   ├── client.py              # Local client
│   ├── ngrok_client.py        # Remote client (ngrok)
│   └── remote_client.py       # Remote client (network)
├── src/                       # Core AI Engine
│   ├── ai_engine.py
│   ├── text_utils.py
│   └── pdf_converter.py
└── dat/                       # Data Files
    └── sample_docs/
        └── constitution_qa.json
```

## 🚀 Quick Start

### 1. Start the Server
```bash
# From project root
python -m mcp_server.server
```

### 2. Run Local Client
```bash
# From project root
python client/client.py
```

### 3. Run Remote Client (Ngrok)
```bash
# From project root
python client/ngrok_client.py
```

### 4. Run Remote Client (Network)
```bash
# From project root
python client/remote_client.py
```

## 🔧 Configuration

### Server Configuration
- **Port**: 8000 (default)
- **Host**: 0.0.0.0 (all interfaces)
- **MCP Endpoint**: `/mcp`
- **Health Check**: `/health`

### Client Configuration

#### Local Client (`client/client.py`)
- Connects to `http://localhost:8000`
- Uses MCP protocol
- No configuration needed

#### Ngrok Client (`client/ngrok_client.py`)
- Update `NGROK_URL` variable with your ngrok URL
- Example: `NGROK_URL = "https://abc123.ngrok.io"`

#### Network Client (`client/remote_client.py`)
- Update `SERVER_IP` variable with server's IP address
- Example: `SERVER_IP = "192.168.1.100"`

## 🧪 Testing

### Test Server Communication
```bash
python mcp_server/test_mcp_communication.py
```

### Test Individual Components
```bash
# Test AI engine
python -m pytest tests/test_ai_engine.py

# Test server health
curl http://localhost:8000/health
```

## 📋 Available Commands

### All Clients Support:
- **Ask questions**: "What is contract law?"
- **Analyze documents**: "analyze This is a legal contract..."
- **Search database**: "search contract terms"
- **Exit**: "quit"

## 🌐 Network Setup

### For Local Network:
1. Start server: `python -m mcp_server.server`
2. Find server IP: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
3. Update `client/remote_client.py` with server IP
4. Run client: `python client/remote_client.py`

### For Internet Access (Ngrok):
1. Install ngrok: https://ngrok.com/download
2. Start server: `python -m mcp_server.server`
3. Start ngrok: `ngrok http 8000`
4. Copy ngrok URL (e.g., `https://abc123.ngrok.io`)
5. Update `client/ngrok_client.py` with ngrok URL
6. Run client: `python client/ngrok_client.py`

## 🔍 Troubleshooting

### Common Issues:

1. **"Cannot connect to server"**
   - Check if server is running
   - Verify IP address/URL is correct
   - Check firewall settings

2. **"Request timed out"**
   - Check network connection
   - Try increasing timeout values
   - For ngrok: free tier can be slow

3. **"Module not found"**
   - Install dependencies: `uv sync`
   - Check Python path
   - Run from project root directory

### Debug Commands:

```bash
# Check server status
curl http://localhost:8000/health

# Test MCP endpoint
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'

# Check ngrok status (if using ngrok)
curl http://localhost:4040/api/tunnels
```

## 📚 API Reference

### MCP Endpoints:
- `POST /mcp` - MCP protocol endpoint
- `GET /health` - Health check
- `GET /` - Server info

### MCP Tools:
- `ask_legal_question` - Ask legal questions
- `analyze_legal_document` - Analyze documents
- `search_legal_database` - Search database

## 🛠️ Development

### Adding New Features:
1. Add routes in `mcp_server/routes.py`
2. Add MCP tools in `mcp_server/server.py`
3. Update clients as needed
4. Add tests in `tests/` folder

### Code Style:
- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests for new features

---

**Happy Legal AI Development! 🤖⚖️**
