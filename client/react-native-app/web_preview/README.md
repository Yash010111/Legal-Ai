# Web preview (no Node required)

This folder contains a minimal static web preview of the chat UI that POSTs to the server URL you enter.

How to run (requires Python 3 which is available on this machine):

```powershell
cd C:\PROJECT\Legal-Ai\client\react-native-app\web_preview
python -m http.server 8000
# Open http://localhost:8000 in your browser
```

Set server URL to `http://localhost:3000` (or your test server URL), Save, then type a message and Send.
