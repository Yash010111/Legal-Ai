"""
Lightweight Python test server to accept POST requests on / and respond
with QueryResponse JSON (answer, confidence, sources). Adds CORS headers.
Run with: python py_test_server.py
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

PORT = 3000

class Handler(BaseHTTPRequestHandler):
    def _set_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        print('\n--- Incoming POST', self.path)
        print('Headers:', dict(self.headers))
        print('Body:', body)
        try:
            data = json.loads(body or '{}')
        except Exception as e:
            self.send_response(400)
            self._set_cors()
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Invalid JSON')
            return

        q = data.get('question') or data.get('message') or ''
        resp = {
            'answer': f'Echo: {q}',
            'confidence': 0.9,
            'sources': []
        }
        out = json.dumps(resp).encode('utf-8')
        self.send_response(200)
        self._set_cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)
        print('Replied:', resp)

    def do_GET(self):
        # simple health
        self.send_response(200)
        self._set_cors()
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'py_test_server OK')


if __name__ == '__main__':
    print(f'Listening on http://localhost:{PORT}')
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down')
        server.server_close()
