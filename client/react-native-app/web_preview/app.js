// Minimal web chat preview. Stores server URL in localStorage.
const serverUrlInput = document.getElementById('serverUrl');
const saveBtn = document.getElementById('saveUrl');
const messagesDiv = document.getElementById('messages');
const msgInput = document.getElementById('msgInput');
const sendBtn = document.getElementById('sendBtn');

const STORAGE_KEY = 'mcp_server_url_preview';

function loadUrl(){
  const u = localStorage.getItem(STORAGE_KEY) || 'http://localhost:3000';
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

async function send(){
  const text = msgInput.value.trim();
  if(!text) return;
  addMessage(text, 'user');
  msgInput.value = '';
  const url = serverUrlInput.value.trim();
  try{
    const res = await fetch(url, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
    const ct = res.headers.get('content-type')||'';
    let reply = '';
    if(ct.includes('application/json')){
      const data = await res.json();
      reply = data.reply || data.response || JSON.stringify(data);
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
