// Minimal web chat preview. Stores server URL in localStorage.
const serverUrlInput = document.getElementById('serverUrl');
const saveBtn = document.getElementById('saveUrl');
const pingBtn = document.getElementById('pingBtn');
const messagesDiv = document.getElementById('messages');
const msgInput = document.getElementById('msgInput');
const sendBtn = document.getElementById('sendBtn');

const STORAGE_KEY = 'mcp_server_url_preview';

function loadUrl(){
  const u = localStorage.getItem(STORAGE_KEY) || 'https://b68e6007292d.ngrok-free.app/query';
  serverUrlInput.value = u;
}

function addMessage(text, cls){
  const d = document.createElement('div');
  d.className = `bubble ${cls}`;
  d.textContent = text;
  messagesDiv.appendChild(d);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

saveBtn.addEventListener('click', ()=>{
  const u = serverUrlInput.value.trim();
  if(u) localStorage.setItem(STORAGE_KEY, u);
  alert('Saved URL: ' + u);
});

pingBtn && pingBtn.addEventListener('click', async ()=>{
  const url = serverUrlInput.value.trim();
  let target = url;
  try{
    const parsed = new URL(url);
    if(!parsed.pathname || parsed.pathname === '/'){
      parsed.pathname = '/query';
      target = parsed.toString();
    }
  }catch(_){
    try{ const p2 = new URL(`http://${url}`); if(!p2.pathname||p2.pathname==='/'){ p2.pathname='/query'; target = p2.toString(); } else target = p2.toString(); }catch(__){ target = url; }
  }
  addMessage('ping', 'user');
  try{
    const res = await fetch(target, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:'ping'})});
    const ct = res.headers.get('content-type')||'';
    let reply = '';
    if(ct.includes('application/json')){ const data = await res.json(); reply = data.answer || data.reply || JSON.stringify(data); } else { reply = await res.text(); }
    addMessage('Ping response: ' + reply, 'bot');
  }catch(e){ addMessage('Ping error: ' + e.message, 'bot'); console.error(e); }
});

async function send(){
  const text = msgInput.value.trim();
  if(!text) return;
  addMessage(text, 'user');
  msgInput.value = '';
  const url = serverUrlInput.value.trim();
  try{
    // If user entered a base URL (no path), default to /query endpoint
    let target = url;
    try{
      const parsed = new URL(url);
      if(!parsed.pathname || parsed.pathname === '/'){
        parsed.pathname = '/query';
        target = parsed.toString();
      }
    }catch(_){
      try{ const p2 = new URL(`http://${url}`); if(!p2.pathname||p2.pathname==='/'){ p2.pathname='/query'; target = p2.toString(); } else target = p2.toString(); }catch(__){ target = url; }
    }

    const res = await fetch(target, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:text})});
    const ct = res.headers.get('content-type')||'';
    let reply = '';
    if(ct.includes('application/json')){
      const data = await res.json();
      reply = data.answer || data.reply || data.response || JSON.stringify(data);
    } else {
      reply = await res.text();
    }
    addMessage(reply, 'bot');
  }catch(e){
    addMessage('Error: ' + e.message, 'bot');
    console.error(e);
  }
}

sendBtn.addEventListener('click', send);
msgInput.addEventListener('keydown', (e)=>{ if(e.key==='Enter') send(); });

loadUrl();
