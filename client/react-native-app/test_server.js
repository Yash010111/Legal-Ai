// Minimal test server using Node's http module. Run with: node test_server.js
// Adds permissive CORS headers so the Expo web preview can POST to it.
const http = require('http');

const PORT = 3000;

function setCorsHeaders(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

const server = http.createServer((req, res) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    setCorsHeaders(res);
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method === 'POST') {
    setCorsHeaders(res);
    let body = '';
    console.log(`\n--- Incoming ${req.method} ${req.url} ---`);
    console.log('Headers:', req.headers);
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => {
      console.log('Body:', body);
      try {
        const data = JSON.parse(body || '{}');
        const msg = data.message || data.msg || '';
        const reply = `Echo: ${msg}`;
        const response = { reply };
        const out = JSON.stringify(response);
        console.log('Reply:', out);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(out);
      } catch (e) {
        console.error('JSON parse error:', e && e.message);
        res.writeHead(400, { 'Content-Type': 'text/plain' });
        res.end('Invalid JSON');
      }
    });
  } else {
    setCorsHeaders(res);
    console.log(`\n--- ${req.method} ${req.url} (non-POST) ---`);
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Test server. Send POST JSON {"message":"..."}');
  }
});

server.listen(PORT, () => {
  console.log(`Test server listening on http://localhost:${PORT}`);
});
