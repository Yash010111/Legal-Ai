# React Native MCP Client (Expo)

This folder contains a minimal Expo React Native app you can use to test the MCP client chat UI.

Quick start (Windows PowerShell)

1. Install Node.js (if not installed). Check with:

```powershell
node -v
npm -v
```

2. From this folder, install dependencies and start the app in web mode:

```powershell
cd C:\PROJECT\Legal-Ai\client\react-native-app
npm install
npm run web
```

3. (Optional) Start a simple local test server that echoes messages (for end-to-end test):

```powershell
cd C:\PROJECT\Legal-Ai\client\react-native-app
node test_server.js
```

4. In the app (web), set the server URL to `http://localhost:3000` and Save. Type a message and Send — the test server returns JSON { reply: 'Echo: ...' } which the app will display.

Notes
- If `npm` or `node` are not available, install Node.js from https://nodejs.org/.
- You can use `npx expo start --web` instead of `npm run web` if you prefer not to install the global expo-cli.
