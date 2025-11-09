"""
FastAPI server for Legal Mind AI MCP
Supports both HTTP API and MCP protocol for client communication
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
import json
import asyncio
import sys
import os
import time

# Load environment from a .env file if present and set sensible defaults.
# NOTE: Do NOT hardcode API tokens in source. If you want to run with
# the Hugging Face Inference API, set the token in the environment (recommended):
#
# PowerShell example (do NOT commit these lines to source):
# $env:HUGGINGFACE_API_TOKEN = "hf_xxxYOURTOKENxxx"
# $env:GEMMA_MODEL = "bigscience/gemma-2b"
#
# The code below will read environment variables and will default GEMMA_MODEL
# to 'bigscience/gemma-2b' if nothing is provided.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; requirements.txt already lists python-dotenv
    pass

# Default model id for Gemma 2 b (can be overridden via GEMMA_MODEL env var)
# Per user request the server should default to use google/gemma-2-2b.
# Default model id for Gemma 2 b (can be overridden via GEMMA_MODEL env var)
# Per previous user preference the server defaults were set to google/gemma-2-2b;
# add a LOCAL_ONLY flag to prefer local execution always. By default LOCAL_ONLY=1
os.environ.setdefault("GEMMA_MODEL", "google/gemma-2-2b")

# If LOCAL_ONLY is set (default '1'), the /query endpoint will always run the local
# fallback model and will NOT call the remote Hugging Face Inference API. Set
# LOCAL_ONLY='0' to allow remote calls (not recommended per user's instruction).
os.environ.setdefault("LOCAL_ONLY", "1")

# Helper accessors used elsewhere in the module
GEMMA_MODEL = os.environ.get("GEMMA_MODEL")
HUGGINGFACE_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN") or os.environ.get("HF_TOKEN") or os.environ.get("HF_API_TOKEN")

# Note: The original code imported 'router' but it wasn't used. Keeping the structure for completeness.
# from mcp_server_Doc_retreival.routes import router

app = FastAPI(
    title="Legal Mind AI MCP Server",
    description="Model Context Protocol server for Legal Mind AI",
    version="0.1.0"
)

# Server start time for uptime reporting
START_TIME = time.time()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- In-memory metrics (rolling history) ---
from collections import deque
METRICS_WINDOW = 120  # number of samples to keep (e.g., 120 * 2s = 4 minutes)
metrics_lock = asyncio.Lock()
metrics_history = deque(maxlen=METRICS_WINDOW)  # each entry: {ts, req_rate, tool_rate, ping}
_requests_since = 0
_tool_calls_since = 0


@app.middleware("http")
async def count_requests_middleware(request, call_next):
    """Increment request counter for metrics on every incoming HTTP request."""
    global _requests_since
    try:
        async with metrics_lock:
            _requests_since += 1
    except Exception:
        pass
    response = await call_next(request)
    return response


@app.on_event("startup")
async def start_metrics_sampler():
    """Background task to sample rates every 2 seconds and store in history."""
    async def sampler():
        global _requests_since, _tool_calls_since
        interval = 2.0
        while True:
            await asyncio.sleep(interval)
            try:
                async with metrics_lock:
                    reqs = _requests_since
                    tools = _tool_calls_since
                    _requests_since = 0
                    _tool_calls_since = 0
                # compute per-second rates
                req_rate = round(reqs / interval, 2)
                tool_rate = round(tools / interval, 2)
                entry = {"ts": time.time(), "req_rate": req_rate, "tool_rate": tool_rate}
                metrics_history.append(entry)
            except Exception:
                # swallow errors in background sampler to keep it running
                pass

    asyncio.create_task(sampler())


@app.get("/metrics")
async def get_metrics():
    """Return the recent metrics history as JSON."""
    async with metrics_lock:
        hist = list(metrics_history)
    return {"history": hist}


# --- Minimal MCP models (used by MCP endpoint and dashboard) ---
class MCPRequest(BaseModel):
        jsonrpc: Optional[str] = None
        id: Optional[Any] = None
        method: str = ""
        params: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
        id: Optional[Any] = None
        result: Optional[Dict[str, Any]] = None
        error: Optional[Dict[str, Any]] = None


class MCPTool(BaseModel):
        name: str
        description: Optional[str] = None
        arguments: Optional[Dict[str, Any]] = None


# Advertised tools (only ask_legal_question is active)
MCP_TOOLS: List[MCPTool] = [
        MCPTool(
                name="ask_legal_question",
                description="Answer a legal question using local RAG over datasets",
                arguments={"question": {"type": "string", "description": "The legal question to answer"}}
        )
]


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
        """Futuristic dashboard with real-time ping sparkline and dataset stats"""
        datasets_dir = os.path.join(os.getcwd(), "datasets")

        txt_count = 0
        total_size = 0
        breakdown = {"cases": 0, "laws": 0, "other": 0}

        if os.path.exists(datasets_dir):
                for r, dirs, files in os.walk(datasets_dir):
                        for fn in files:
                                if fn.lower().endswith('.txt'):
                                        txt_count += 1
                                        p = os.path.join(r, fn)
                                        try:
                                                total_size += os.path.getsize(p)
                                        except Exception:
                                                pass
                                        rel = os.path.relpath(p, datasets_dir).replace('\\', '/').lower()
                                        if rel.startswith('cases/'):
                                                breakdown['cases'] += 1
                                        elif rel.startswith('laws/'):
                                                breakdown['laws'] += 1
                                        else:
                                                breakdown['other'] += 1

        # Load metadata.json if present (used to display hardcoded large counts)
        metadata_path = os.path.join(datasets_dir, 'metadata.json')
        if os.path.exists(metadata_path):
                try:
                        with open(metadata_path, 'r', encoding='utf-8') as mf:
                                meta = json.load(mf)
                                display_cases = int(meta.get('cases', breakdown['cases']))
                                display_laws = int(meta.get('law_documents', breakdown['laws']))
                                display_other = int(meta.get('other_documents', breakdown['other']))
                except Exception:
                        display_cases = breakdown['cases']; display_laws = breakdown['laws']; display_other = breakdown['other']
        else:
                display_cases = breakdown['cases']; display_laws = breakdown['laws']; display_other = breakdown['other']

        display_txt_count = display_cases + display_laws + display_other

        def human_size(n: int) -> str:
                for unit in ['B','KB','MB','GB','TB']:
                        if n < 1024.0:
                                return f"{n:3.1f}{unit}"
                        n /= 1024.0
                return f"{n:.1f}PB"

        # Build tools HTML
        tools_rows = ""
        for t in MCP_TOOLS:
                tools_rows += f"<div style='padding:10px;border-radius:8px;background:rgba(255,255,255,0.02);margin-bottom:8px'><strong>{t.name}</strong> - {t.description or ''}</div>"

        uptime = "{:.0f}s".format(time.time() - START_TIME)

        # Use r""" for the template to avoid issues with backslashes and quotes inside the large string
        html_template = r"""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>Legal Mind AI — MCP Server</title>
            <style>
                :root {--bg-a:#020617;--bg-b:#0a1630;--glow:#00fff0;--accent:#9f5cff;--muted:#9fb3d6}
                html,body{height:100%;margin:0;padding:0;font-family:Inter,system-ui,Segoe UI,Roboto,Arial}
                body{background:radial-gradient(1200px 600px at 10% 10%, rgba(63,94,251,0.06), transparent), linear-gradient(180deg,var(--bg-a),var(--bg-b));color:#dfefff;padding:24px}
                .wrap{max-width:1280px;margin:0 auto}
                .header{display:flex;align-items:center;gap:18px;margin-bottom:18px}
                .logo{width:64px;height:64px;border-radius:14px;background:linear-gradient(135deg,var(--accent),var(--glow));display:flex;align-items:center;justify-content:center;box-shadow:0 10px 40px rgba(0,255,240,0.08);border:1px solid rgba(255,255,255,0.03)}
                h1{margin:0;font-size:22px;letter-spacing:0.4px}
                .sub{color:var(--muted);font-size:13px}
                .bg-grid{position:fixed;inset:0;pointer-events:none;opacity:0.06;background-image:linear-gradient(90deg,rgba(255,255,255,0.02) 1px,transparent 1px),linear-gradient(180deg,rgba(255,255,255,0.02) 1px,transparent 1px);background-size:120px 120px,120px 120px;transform:translateZ(0)}
                .grid{display:grid;grid-template-columns:repeat(12,1fr);gap:14px;position:relative;z-index:1}
                .card{grid-column:span 6;padding:18px;border-radius:12px;background:linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0.01));border:1px solid rgba(255,255,255,0.03);box-shadow:0 6px 24px rgba(0,0,0,0.6)}
                .card.wide{grid-column:span 12}
                .muted{color:var(--muted);font-size:13px}
                .kpi{display:flex;align-items:center;gap:10px}
                .kpi .val{font-weight:800;color:var(--glow);font-size:18px}
                .endpoint{display:inline-block;background:rgba(255,255,255,0.02);padding:6px 10px;border-radius:8px;font-family:monospace;color:#cdeff6}
                .ping-box{display:flex;align-items:center;gap:12px}
                #pingCanvas{width:180px;height:48px;background:transparent;display:block}
                .ping-stats{font-size:13px;color:var(--muted)}
                .glow-line{height:3px;background:linear-gradient(90deg,transparent,var(--glow),transparent);border-radius:3px;margin:12px 0;opacity:0.9;animation:glow 3s linear infinite}
                @keyframes glow{0%{filter:blur(0px)}50%{filter:blur(6px)}100%{filter:blur(0px)}}
                @media (max-width:900px){.card{grid-column:span 12}}
            </style>
        </head>
        <body>
            <div class="bg-grid"></div>
            <div class="wrap">
                <div class="header">
                    <div class="logo" aria-hidden>
                        <svg width="38" height="38" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" fill="white" fill-opacity="0.03"/><path d="M8 12a4 4 0 0 1 8 0" stroke="white" stroke-opacity="0.6" stroke-width="0.9" stroke-linecap="round"/></svg>
                    </div>
                    <div>
                        <h1>Legal Mind AI — MCP Server</h1>
                        <div class="sub">Version: %%APP_VERSION%% • <span id="uptime">%%UPTIME%%</span></div>
                    </div>
                    <div style="margin-left:auto;display:flex;gap:10px;align-items:center">
                        <button class="endpoint" onclick="navigator.clipboard.writeText(location.href)">Copy URL</button>
                    </div>
                </div>

                <div class="grid">
                    <div class="card">
                        <div class="kpi"><div class="val">Datasets</div><div class="muted">contents & targets</div></div>
                        <div style="margin-top:8px" class="muted">Path: %%DATASETS_DIR%%</div>
                        <div style="margin-top:8px"><strong>%%DISPLAY_TXT_COUNT%%</strong> TXT files (display) • <span class="muted">Total size: %%HUMAN_SIZE%%</span></div>
                        <div style="margin-top:8px" class="muted">Breakdown (displayed): Cases: <strong>%%DISPLAY_CASES%%</strong> • Laws: <strong>%%DISPLAY_LAWS%%</strong> • Other: <strong>%%DISPLAY_OTHER%%</strong></div>
                        <div style="margin-top:6px" class="muted">(Actual scanned: Cases: <strong>%%BREAK_CASES%%</strong>, Laws: <strong>%%BREAK_LAWS%%</strong>, Other: <strong>%%BREAK_OTHER%%</strong>)</div>
                        <div class="glow-line"></div>
                        <div class="ping-box" style="margin-top:10px">
                            <canvas id="pingCanvas" width="300" height="80"></canvas>
                            <div>
                                <div class="ping-stats">Ping <span id="pingNow">-</span> ms</div>
                                <div class="ping-stats">Avg: <span id="pingAvg">-</span> ms • Min: <span id="pingMin">-</span> ms • Max: <span id="pingMax">-</span> ms</div>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="kpi"><div class="val">Endpoints</div><div class="muted">MCP & API</div></div>
                        <div style="margin-top:8px"><strong>MCP:</strong> <span class="endpoint">/mcp</span></div>
                        <div style="margin-top:6px"><strong>Health:</strong> <span class="endpoint">/health</span></div>
                        <div style="margin-top:6px"><strong>API (query):</strong> <span class="endpoint">/query</span></div>
                        <div style="margin-top:10px" class="muted">Server root: %%REQUEST_BASE_URL%%</div>
                        <div style="margin-top:12px">
                            <button class="endpoint" onclick="testTools()">List MCP Tools</button>
                        </div>
                    </div>

                    <!-- Realtime Activity card removed as requested; live metrics remain below -->

                    <div class="card wide">
                            <div class="kpi"><div class="val">Requests (recent)</div></div>
                            <div style="margin-top:10px;">
                                <!-- left margin reserved for Y-axis labels; canvas covers full width and drawing will offset accordingly -->
                                <canvas id="lineCanvas" width="1200" height="240" style="width:100%;height:240px;background:transparent"></canvas>
                            </div>
                            <div style="margin-top:8px" class="muted">This chart reflects recent requests/sec (history last %%METRICS_SECONDS%% seconds).</div>
                            <div style="display:flex;align-items:center;justify-content:space-between">
                                <div style="display:flex;gap:14px;align-items:center;font-family:monospace;color:var(--muted);font-size:13px">
                                    <div>Now: <strong id="reqNow">-</strong></div>
                                    <div>Avg: <strong id="reqAvg">-</strong></div>
                                    <div>Max: <strong id="reqMax">-</strong></div>
                                </div>
                            </div>
                    </div>

                    <div class="card wide">
                        <div class="kpi"><div class="val">MCP Tools</div><div class="muted">interactive schemas</div></div>
                        <div style="margin-top:12px" id="toolsArea">
                            %%TOOLS_ROWS%%
                        </div>
                    </div>
                </div>

                <footer style="margin-top:18px;color:var(--muted);font-size:13px">Generated by Legal Mind AI MCP Server • %%TIMESTAMP%%</footer>
            </div>

            <script>
                // Ping logic and sparkline
                const pings = [];
                const maxPoints = 40;
                const canvas = document.getElementById('pingCanvas');
                const ctx = canvas.getContext('2d');

                function drawPing() {
                    ctx.clearRect(0,0,canvas.width,canvas.height);
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = 'rgba(123,227,255,0.95)';
                    ctx.beginPath();
                    const w = canvas.width; const h = canvas.height;
                    const maxPing = Math.max(50, ...pings);
                    pings.forEach((v,i)=>{
                        const x = (i/(maxPoints-1))*w;
                        const y = h - (v/maxPing)*h;
                        if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
                    });
                    ctx.stroke();
                }

                async function pingHealth() {
                    const t0 = performance.now();
                    try {
                        const r = await fetch('/health', {cache: 'no-store'});
                        const t1 = performance.now();
                        const ms = Math.round(t1 - t0);
                        pings.push(ms);
                        if(pings.length>maxPoints) pings.shift();
                        document.getElementById('pingNow').textContent = ms;
                        const avg = Math.round(pings.reduce((a,b)=>a+b,0)/pings.length);
                        document.getElementById('pingAvg').textContent = avg;
                        document.getElementById('pingMin').textContent = Math.min(...pings);
                        document.getElementById('pingMax').textContent = Math.max(...pings);
                        drawPing();
                    } catch(e) {
                        pings.push(999); if(pings.length>maxPoints) pings.shift(); drawPing();
                        document.getElementById('pingNow').textContent = 'err';
                    }
                }

                // Replace separate warmup/intervals with a single combined poll
                // to avoid interleaved requests and reduce total polling rate.

                function testTools() {
                    fetch('/mcp', {
                        method: 'POST', headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({jsonrpc:'2.0', id:1, method:'tools/list'})
                    }).then(r=>r.json()).then(j=>alert('Tools:\n'+JSON.stringify(j.result.tools,null,2))).catch(e=>alert('Error'));
                }

                // Per-card realtime canvases removed (requests & tool-calls card); metrics still feed the flowing charts below

                // Buffers that back the visualizations; these will be populated from /metrics
                let simLine = new Array(128).fill(0);

                // Helper to take the last n values from metrics history and pad to length
                function takeLast(arr, n){
                    const res = new Array(n).fill(0);
                    const start = Math.max(0, arr.length - n);
                    for(let i = start; i < arr.length; i++){
                        res[n - (arr.length - i)] = arr[i];
                    }
                    return res;
                }

                async function updateMetrics(){
                    try{
                        const r = await fetch('/metrics', {cache:'no-store'});
                        if(!r.ok) return;
                        const j = await r.json();
                        const hist = j.history || [];
                        // map history to numeric series (older -> newer)
                        const reqs = hist.map(x=> typeof x.req_rate === 'number' ? x.req_rate : 0);
                        // feed the visualization buffer (flowing area) with the latest series
                        simLine = takeLast(reqs, simLine.length);
                        // update numeric readouts (Now/Avg/Max)
                        try{
                            const last = simLine.length? simLine[simLine.length-1] : 0;
                            const avg = simLine.length? Math.round((simLine.reduce((a,b)=>a+b,0)/simLine.length)*100)/100 : 0;
                            const max = simLine.length? Math.max(...simLine) : 0;
                            const nowEl = document.getElementById('reqNow');
                            const avgEl = document.getElementById('reqAvg');
                            const maxEl = document.getElementById('reqMax');
                            if(nowEl) nowEl.textContent = String(last);
                            if(avgEl) avgEl.textContent = String(avg);
                            if(maxEl) maxEl.textContent = String(max);
                        }catch(e){/* ignore UI update errors */}
                    }catch(e){
                        // ignore network errors silently; overlay will show unhandled errors if needed
                    }
                }

                // initial metrics load and unified polling
                // combined poll will fetch /metrics and /health together
                async function pollAll(){
                    try{
                        // run both fetches in parallel to reduce latency
                        await Promise.all([updateMetrics(), pingHealth()]);
                    }catch(e){
                        // ignore poll errors
                    }
                }

                // run initial poll immediately, then every 4s
                pollAll();
                const POLL_INTERVAL_MS = 4000;
                setInterval(pollAll, POLL_INTERVAL_MS);

                // Flowing line only (requests)
                const lineCanvas = document.getElementById('lineCanvas');
                const lineCtx = lineCanvas ? lineCanvas.getContext('2d') : null;

                // draw background grid similar to system charts (confined to plotting area)
                function drawGrid(ctx, leftMargin, stepY=20, stepX=50, color='rgba(255,255,255,0.03)'){
                    if(!ctx) return;
                    const w = ctx.canvas.width; const h = ctx.canvas.height;
                    ctx.save();
                    ctx.strokeStyle = color; ctx.lineWidth = 1;
                    ctx.beginPath();
                    // horizontal grid across plotting area
                    for(let y=0;y<=h;y+=stepY){ ctx.moveTo(leftMargin,y+0.5); ctx.lineTo(w,y+0.5); }
                    // vertical grid inside plotting area
                    for(let x=leftMargin;x<=w;x+=stepX){ ctx.moveTo(x+0.5,0); ctx.lineTo(x+0.5,h); }
                    ctx.stroke(); ctx.restore();
                }

                // Smooth flowing filled-area line chart with grid (requests) and Y-axis labels
                function drawFlowingArea(ctx, values, color) {
                    if(!ctx) return;
                    const w = ctx.canvas.width; const h = ctx.canvas.height;
                    ctx.clearRect(0,0,w,h);
                    const leftMargin = Math.max(44, Math.floor(w * 0.06)); // reserve space for Y labels
                    const plotW = w - leftMargin - 8; // small right padding
                    // draw grid within plotting area
                    drawGrid(ctx, leftMargin, 18, Math.floor(plotW/12));
                    if(!values || values.length < 2) return;
                    const maxV = Math.max(1, ...values);
                    const minV = 0;
                    // draw Y axis line
                    ctx.save();
                    ctx.strokeStyle = 'rgba(255,255,255,0.12)'; ctx.lineWidth = 1;
                    ctx.beginPath(); ctx.moveTo(leftMargin+0.5, 0); ctx.lineTo(leftMargin+0.5, h); ctx.stroke();
                    ctx.restore();

                    // draw Y ticks and labels
                    const tickCount = 4;
                    ctx.fillStyle = 'rgba(255,255,255,0.6)'; ctx.font = '12px system-ui, Arial'; ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
                    for(let t=0;t<=tickCount;t++){
                        const frac = t / tickCount;
                        const y = h - frac * h;
                        const value = (minV + (1-frac)*(maxV-minV));
                        const label = (value >= 100 ? Math.round(value) : Number(value.toFixed(2)));
                        ctx.fillText(String(label), leftMargin - 8, y);
                        // small tick mark
                        ctx.strokeStyle = 'rgba(255,255,255,0.08)'; ctx.beginPath(); ctx.moveTo(leftMargin+2, y+0.5); ctx.lineTo(leftMargin+6, y+0.5); ctx.stroke();
                    }

                    // path for line (map values into plotting area)
                    ctx.beginPath();
                    values.forEach((v,i)=>{
                        const x = leftMargin + (i/(values.length-1))*plotW;
                        const y = h - ((v - minV)/(maxV - minV))*h;
                        if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
                    });
                    // create filled area
                    const lastX = leftMargin + plotW; const baseY = h;
                    ctx.lineTo(lastX, baseY);
                    ctx.lineTo(leftMargin, baseY);
                    ctx.closePath();
                    // fill with gradient
                    const grad = ctx.createLinearGradient(0,0,0,h);
                    grad.addColorStop(0, color.replace('0.98', '0.18'));
                    grad.addColorStop(1, 'rgba(0,0,0,0.02)');
                    ctx.fillStyle = grad;
                    ctx.fill();
                    // draw line on top
                    ctx.beginPath();
                    values.forEach((v,i)=>{
                        const x = leftMargin + (i/(values.length-1))*plotW;
                        const y = h - ((v - minV)/(maxV - minV))*h;
                        if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
                    });
                    ctx.lineWidth = 2; ctx.strokeStyle = color; ctx.stroke();
                }

                // render loop: draw the flowing requests chart
                function renderLoop(){
                    drawFlowingArea(lineCtx, simLine, 'rgba(159,92,255,0.98)');
                    requestAnimationFrame(renderLoop);
                }

                requestAnimationFrame(renderLoop);
            </script>
        </body>
        </html>
        """

        html = html_template.replace('%%APP_VERSION%%', str(app.version))
        html = html.replace('%%UPTIME%%', uptime)
        html = html.replace('%%DATASETS_DIR%%', datasets_dir)
        html = html.replace('%%DISPLAY_TXT_COUNT%%', str(display_txt_count))
        html = html.replace('%%HUMAN_SIZE%%', human_size(total_size))
        html = html.replace('%%DISPLAY_CASES%%', str(display_cases))
        html = html.replace('%%DISPLAY_LAWS%%', str(display_laws))
        html = html.replace('%%DISPLAY_OTHER%%', str(display_other))
        html = html.replace('%%BREAK_CASES%%', str(breakdown['cases']))
        html = html.replace('%%BREAK_LAWS%%', str(breakdown['laws']))
        html = html.replace('%%BREAK_OTHER%%', str(breakdown['other']))
        html = html.replace('%%REQUEST_BASE_URL%%', str(request.base_url))
        html = html.replace('%%TOOLS_ROWS%%', tools_rows)
        html = html.replace('%%TIMESTAMP%%', time.strftime('%Y-%m-%d %H:%M:%S'))
        # replace metrics window seconds (METRICS_WINDOW * interval seconds)
        try:
            metrics_seconds = str(METRICS_WINDOW * 2)
        except Exception:
            metrics_seconds = 'N/A'
        html = html.replace('%%METRICS_SECONDS%%', metrics_seconds)

        return HTMLResponse(content=html, status_code=200)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "legal-mind-ai-mcp"}


# Simple /query endpoint to answer a user question using Gemma 2 b (Hugging Face)
class QueryRequest(BaseModel):
    question: str
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.0


@app.post("/query")
async def query_endpoint(qreq: QueryRequest, request: Request):
    """Answer a free-text question using Gemma 2 b from Hugging Face.

    Behavior:
    - If a Hugging Face API token is provided in env (HUGGINGFACE_API_TOKEN or HF_TOKEN),
      the endpoint will call the Hugging Face Inference API with the configured model id.
    - Otherwise it will attempt a local `transformers` pipeline for text-generation.

    Configure the model via env `GEMMA_MODEL` (default: 'bigscience/gemma-2b').
    """
    question = (qreq.question or "").strip()
    if not question:
        return {"error": "Missing question"}

    # Use the configured model (default set above to google/gemma-2-2b)
    # Use the configured model (default set above)
    model_id = os.environ.get("GEMMA_MODEL", os.environ.get("GEMMA_MODEL", "google/gemma-2-2b"))

    # Token resolution: per your instruction only HUGGINGFACE_API_TOKEN will be considered
    # and only when remote calls are allowed. Authorization header and alternate env
    # variable names (HF_TOKEN / HF_API_TOKEN) are ignored.
    hf_token = os.environ.get("HUGGINGFACE_API_TOKEN")

    # If LOCAL_ONLY is set to '1' (default), always use local fallback and ignore remote.
    local_only = os.environ.get("LOCAL_ONLY", "1").strip() in ("1", "true", "True")
    if local_only:
        hf_token = None

    try:
        # Remote (Inference API) path (only if not forced-local and hf_token present)
        if hf_token and not local_only:
            try:
                # per HF docs: use huggingface_hub.InferenceApi for hosted inference
                from huggingface_hub import InferenceApi
            except Exception as exc:
                raise HTTPException(status_code=500, detail=f"Missing dependency huggingface_hub: {exc}")

            infer = InferenceApi(repo_id=model_id, token=hf_token)
            # Call using documented signature: infer(inputs=..., parameters={...})
            try:
                # Try the modern keyword-style call
                resp = infer(inputs=question, parameters={"max_new_tokens": int(qreq.max_tokens or 256), "temperature": float(qreq.temperature or 0.0)})
            except TypeError:
                # Fallback: some versions expect a single payload dict
                try:
                    payload = {"inputs": question, "parameters": {"max_new_tokens": int(qreq.max_tokens or 256), "temperature": float(qreq.temperature or 0.0)}}
                    resp = infer(payload)
                except Exception as exc:
                    raise HTTPException(status_code=502, detail=f"Inference API error (payload call): {exc}")
            except Exception as exc:
                raise HTTPException(status_code=502, detail=f"Inference API error: {exc}")

            # Response can be a dict or list depending on model/inference type
            answer = None
            if isinstance(resp, dict):
                answer = resp.get("generated_text") or resp.get("text") or json.dumps(resp)
            elif isinstance(resp, list) and len(resp) > 0:
                first = resp[0]
                if isinstance(first, dict):
                    answer = first.get("generated_text") or first.get("text") or json.dumps(first)
                else:
                    answer = str(first)
            else:
                answer = str(resp)

            return {"model": model_id, "answer": answer}

        # Local transformers fallback (opt-in): follow standard transformers usage
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
            import torch as _torch
        except Exception:
            # If neither remote token nor local deps are available, instruct user how to proceed
            raise HTTPException(status_code=400, detail=(
                "No Hugging Face token provided and local transformers/torch not available. "
                "Install transformers and torch to enable local fallback."
            ))

        # Choose a lightweight local fallback model to avoid downloading very large Gemma weights.
        local_model = os.environ.get("LOCAL_FALLBACK_MODEL", "google/flan-t5-small")

        # Attempt to run locally (may be slow or OOM for large models)
        device = 0 if _torch.cuda.is_available() else -1
        try:
            # Use pipeline for sequence-to-sequence models like FLAN-T5
            # Load tokenizer and model explicitly to allow using use_auth_token=False when needed.
            tokenizer = AutoTokenizer.from_pretrained(local_model, use_auth_token=False)
            model = AutoModelForSeq2SeqLM.from_pretrained(local_model, use_auth_token=False)
            pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device_map=None)
            gen = pipe(question, max_new_tokens=int(qreq.max_tokens or 256), do_sample=False, temperature=float(qreq.temperature or 0.0))
            if isinstance(gen, list) and len(gen) > 0 and isinstance(gen[0], dict) and "generated_text" in gen[0]:
                answer = gen[0]["generated_text"]
            else:
                answer = str(gen)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Local model generation failed: {e}")

        return {"model": local_model, "answer": answer}
    except Exception as e:
        return {"error": "model invocation failed", "detail": str(e)}

    except Exception as e:
        return {"error": "model invocation failed", "detail": str(e)}


@app.post("/mcp", response_model=MCPResponse)
async def mcp_endpoint(request: MCPRequest):
    """
    MCP (Model Context Protocol) endpoint for client communication
    
    Args:
        request: MCP request with method and parameters
        
    Returns:
        MCP response with result or error
    """
    try:
        if request.method == "initialize":
            return MCPResponse(
                id=request.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": True
                        }
                    },
                    "serverInfo": {
                        "name": "legal-mind-ai-mcp",
                        "version": "0.1.0"
                    }
                }
            )
        elif request.method == "tools/list":
            return MCPResponse(
                id=request.id,
                result={
                    "tools": [tool.dict() for tool in MCP_TOOLS]
                }
            )
        elif request.method == "tools/call":
            if not request.params or "name" not in request.params:
                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": "Error: Invalid params: missing tool name"
                            }
                        ]
                    },
                    error={
                        "code": -32602,
                        "message": "Invalid params: missing tool name"
                    }
                )
            tool_name = request.params["name"]
            tool_args = request.params.get("arguments", {})
            # Route to appropriate tool handler
            if tool_name == "ask_legal_question":
                # record a tool call for metrics
                try:
                    async with metrics_lock:
                        global _tool_calls_since
                        _tool_calls_since += 1
                except Exception:
                    pass
                result = await handle_ask_legal_question(tool_args)
            else:
                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error: Unknown tool: {tool_name}"
                            }
                        ]
                    },
                    error={
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                )
            return MCPResponse(
                id=request.id,
                result=result
            )
        else:
            return MCPResponse(
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: Unknown method: {request.method}"
                        }
                    ]
                },
                error={
                    "code": -32601,
                    "message": f"Unknown method: {request.method}"
                }
            )
    except Exception as e:
        return MCPResponse(
            id=request.id,
            result={
                "content": [
                    {
                        "type": "text",
                        "text": f"Internal error: {str(e)}"
                    }
                ]
            },
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        )


async def handle_ask_legal_question(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle ask_legal_question tool call using RAG from helpers/retrieval.py"""
    try:
        # NOTE: You must ensure 'helpers/retrieval.py' exists and is importable.
        from helpers import retrieval 
        question = args.get("question", "")
        # context is ignored for now, but can be used for advanced retrieval
        answer = retrieval.answer_legal_question(question)
        # If answer is a fallback message, provide more guidance
        if answer.lower().startswith("no relevant information"):
            # Try to suggest related questions or provide a helpful message
            related = []
            try:
                retriever = retrieval.LegalRAGRetriever()
                related = retriever.get_related_questions(question)
            except Exception:
                pass
            if related:
                answer += "\n\nRelated questions you can try:\n" + "\n".join(f"- {q}" for q in related)
            else:
                answer += "\n\nTry rephrasing your question or ask about fundamental rights, freedoms, or constitutional remedies."
        return {
            "content": [
                {
                    "type": "text",
                    "text": answer
                }
            ]
        }
    except Exception as e:
        # A mock response if the retrieval module fails to load or run
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error processing legal question (retrieval mock): Check 'helpers/retrieval.py'. Error: {str(e)}"
                }
            ]
        }


# Removed handlers: analyze_legal_document and search_legal_database


if __name__ == "__main__":
    print("🚀 Starting Legal Mind AI MCP Server...")
    print("🌐 Server will be accessible at:")
    print("   - Local: http://localhost:8000")
    print("   - Network: http://[YOUR_IP]:8000")
    print("   - MCP Endpoint: http://[YOUR_IP]:8000/mcp")
    print("   - Health Check: http://[YOUR_IP]:8000/health")
    print("\n📋 For clients on other PCs, use your machine's IP address")
    print("   Find your IP with: ipconfig (Windows) or ifconfig (Linux/Mac)")
    print("\n🔧 Starting server...")
    
    uvicorn.run(
        app, 
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,
        log_level="info"
    )