# MCP Chat Client (React Native / Expo)

This folder contains a minimal Expo React Native app that acts as an MCP chat client. It provides a simple chat UI and sends POST requests to a configurable server URL.

Quick features
- Changeable server URL (persisted locally)
- Chat interface (send message, receive server reply)
- Web preview via Expo web

Getting started (Windows / PowerShell)

1. Install expo CLI if you don't have it:

```powershell
npm install --global expo-cli
```

2. Install dependencies inside the `client` folder:

```powershell
cd c:\PROJECT\Legal-Ai\client
npm install
```

3. Start the app and open web preview:

```powershell
npm run web
```

4. To run on a physical device or simulator, use `npm start` and follow the Expo instructions.

Usage notes
- Enter the full server endpoint URL in the top input (for example: `http://localhost:8000/chat` or `http://<ngrok>.io`) and press Save.
- Type messages and press Send. The app sends a POST request with JSON body: `{ "message": "your text" }` to the saved server URL. The client expects JSON reply with `reply` or `response` fields, or plain text.

Customization
- You can adapt the request payload or response parsing in `App.js`.

Troubleshooting
- If your server runs on localhost and you test on a physical device, expose your server with ngrok or use your machine IP.
