# 🌐 Ngrok Setup Guide for Legal Mind AI MCP Server

## Overview
This guide helps you set up your Legal Mind AI MCP Server to be accessible from any PC anywhere using ngrok tunneling.

## Prerequisites
- Legal Mind AI MCP Server running locally
- Ngrok account (free at https://ngrok.com)
- Python installed on both server and client PCs

## Step 1: Install and Setup Ngrok

### On Your Server PC:
1. **Download ngrok**: https://ngrok.com/download
2. **Sign up** for a free account
3. **Get your authtoken** from the dashboard
4. **Authenticate ngrok**:
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```

## Step 2: Start Your Server

### On Your Server PC:
```bash
# Start the Legal Mind AI MCP Server
python -m mcp_server.server
```

The server will start on `http://localhost:8000`

## Step 3: Start Ngrok Tunnel

### On Your Server PC (in a new terminal):
```bash
# Start ngrok tunnel
ngrok http 8000
```

You'll see output like:
```
Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the Forwarding URL** (e.g., `https://abc123.ngrok.io`)

## Step 4: Configure Client PC

### On Your Client PC:

1. **Copy the ngrok client file**:
   - Copy `ngrok_client.py` to your client PC
   - Or download it from your server

2. **Update the ngrok URL**:
   ```python
   # In ngrok_client.py, update this line:
   NGROK_URL = "https://your-actual-ngrok-url.ngrok.io"  # Replace with your ngrok URL
   ```

3. **Install required packages**:
   ```bash
   pip install requests
   ```

4. **Run the client**:
   ```bash
   python ngrok_client.py
   ```

## Step 5: Test the Connection

### On Your Client PC:
The client will automatically test the connection. You should see:
```
🌐 Legal Mind AI Ngrok Client
==================================================
🔗 Connecting to ngrok tunnel: https://abc123.ngrok.io
🔌 Testing connection to ngrok tunnel...
✅ Connected to Legal Mind AI MCP Server via ngrok
```

## Usage Examples

### Ask Legal Questions:
```
👤 You: What is contract law?
🤖 Legal Mind AI: [AI response about contract law]
```

### Analyze Documents:
```
👤 You: analyze This is a legal contract between...
🤖 Legal Mind AI: [Document analysis results]
```

### Search Database:
```
👤 You: search contract terms
🤖 Legal Mind AI: [Search results from legal database]
```

## Troubleshooting

### Common Issues:

1. **"Cannot connect to ngrok tunnel"**
   - Check if ngrok is running: `ngrok http 8000`
   - Verify the URL is correct in your client
   - Ensure your server is running: `python -m mcp_server.server`

2. **"Request timed out"**
   - Ngrok free tier has slower connections
   - Try again, or consider upgrading to paid tier

3. **"Connection refused"**
   - Check if your server is running on port 8000
   - Verify ngrok is forwarding to the correct port

4. **"Invalid ngrok URL"**
   - Make sure you copied the full URL including `https://`
   - Check that ngrok is still running (URLs change when ngrok restarts)

### Debug Commands:

**On Server PC:**
```bash
# Check if server is running
curl http://localhost:8000/health

# Check ngrok status
curl http://localhost:4040/api/tunnels
```

**On Client PC:**
```bash
# Test ngrok URL directly
curl https://your-ngrok-url.ngrok.io/health
```

## Security Notes

- **Ngrok URLs are public** - anyone with the URL can access your server
- **Use ngrok authentication** to prevent unauthorized access
- **Consider using ngrok's password protection** for additional security
- **Free ngrok URLs change** when you restart ngrok

## Advanced Configuration

### Custom Subdomain (Paid Feature):
```bash
ngrok http 8000 --subdomain=your-custom-name
```

### Password Protection:
```bash
ngrok http 8000 --basic-auth="username:password"
```

### Region Selection:
```bash
ngrok http 8000 --region=us  # or eu, ap, au, sa, jp, in
```

## File Structure

```
Legal-Ai/
├── mcp_server/
│   └── server.py          # MCP Server
├── client/
│   └── client.py          # Local client
├── ngrok_client.py        # Remote client for ngrok
├── ngrok_setup.py         # Setup helper
└── NGROK_SETUP_GUIDE.md   # This guide
```

## Support

If you encounter issues:
1. Check the ngrok web interface: http://localhost:4040
2. Review server logs for errors
3. Test with a simple HTTP request first
4. Verify all URLs and ports are correct

---

**Happy Legal AI-ing! 🤖⚖️**
