from fastapi import APIRouter
from fastapi.responses import HTMLResponse

HTML_CONTENT = r"""
<!DOCTYPE html>
<html>
<head>
    <title>Ginkgo Database WebSocket Tester</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: monospace; background: #1e1e1e; color: #d4d4d4; margin: 20px; }
        h1 { color: #4ec9b0; margin-bottom: 20px; }
        .container { max-width: 1000px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .panel { background: #252526; border: 1px solid #3e3e42; border-radius: 4px; padding: 15px; }
        .panel h2 { color: #4ec9b0; margin-bottom: 10px; font-size: 14px; }
        textarea { width: 100%; height: 150px; background: #1e1e1e; color: #d4d4d4; border: 1px solid #3e3e42; padding: 10px; font-family: monospace; margin: 5px 0; border-radius: 3px; }
        button { background: #0e639c; color: white; border: none; padding: 8px 15px; border-radius: 3px; cursor: pointer; margin-right: 5px; margin-top: 5px; }
        button:hover { background: #1177bb; }
        #response { background: #1e1e1e; border: 1px solid #3e3e42; padding: 10px; min-height: 200px; max-height: 300px; overflow-y: auto; border-radius: 3px; white-space: pre-wrap; word-wrap: break-word; font-size: 12px; }
        .preset { margin-top: 10px; }
        .preset button { display: block; width: 100%; text-align: left; margin-bottom: 5px; padding: 10px; }
        .status { padding: 5px; border-radius: 3px; margin-bottom: 10px; font-weight: bold; }
        .connected { background: #366e4d; color: #4ec9b0; }
        .disconnected { background: #5d3a3a; color: #f48771; }
    </style>
</head>
<body>
    <h1>🌲 Ginkgo Database WebSocket Tester</h1>
    
    <div class="container">
        <div class="panel">
            <h2>Connection Status</h2>
            <div id="status" class="status disconnected">Disconnected</div>
            <button onclick="window.testUI.connect()">Connect</button>
            <button onclick="window.testUI.disconnect()">Disconnect</button>
            
            <h2 style="margin-top: 15px;">Quick Commands</h2>
            <div class="preset">
                <button onclick="window.testUI.sendPreset('add_thought')">➕ Add Thought</button>
                <button onclick="window.testUI.sendPreset('add_prompt')">➕ Add Prompt</button>
                <button onclick="window.testUI.sendPreset('add_decree')">➕ Add Decree</button>
                <button onclick="window.testUI.sendPreset('query_all')">🔍 Query All</button>
                <button onclick="window.testUI.sendPreset('query_thoughts')">🔍 Query Thoughts</button>
                <button onclick="window.testUI.sendPreset('query_recent')">🔍 Recent (24h)</button>
            </div>
        </div>
        
        <div class="panel">
            <h2>Command Input</h2>
            <textarea id="input" placeholder="Enter JSON command or use presets...">{"action": "add", "text": "Hello, Ginkgo!", "type": "thought", "lang": "en"}</textarea>
            <button onclick="window.testUI.sendCommand()">Send</button>
            <button onclick="window.testUI.clearInput()">Clear</button>
        </div>
    </div>
    
    <div class="panel" style="margin-top: 20px;">
        <h2>Response Output</h2>
        <div id="response">Waiting for responses...</div>
        <button onclick="window.testUI.clearResponse()" style="margin-top: 10px;">Clear</button>
    </div>

    <script>
        window.testUI = {
            ws: null,
            presets: {
                add_thought: { action: "add", text: "This is a thought", type: "thought", lang: "en" },
                add_prompt: { action: "add", text: "This is a prompt", type: "prompt", lang: "en" },
                add_decree: { action: "add", text: "This is a decree", type: "decree", lang: "en" },
                query_all: { action: "query", query_type: "all", filters: { limit: 10 } },
                query_thoughts: { action: "query", query_type: "by_type", filters: { input_type: "thought", limit: 10 } },
                query_recent: { action: "query", query_type: "recent", filters: { hours: 24 } },
            },
            
            connect: function() {
                console.log('Attempting to connect...');
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const url = protocol + '//' + window.location.host + '/ws/frontend';
                console.log('WebSocket URL:', url);
                
                this.ws = new WebSocket(url);
                const self = this;
                
                this.ws.onopen = function() {
                    console.log('WebSocket opened');
                    self.updateStatus('Connected', true);
                    self.addOutput('✅ WebSocket connected');
                };
                
                this.ws.onmessage = function(event) {
                    console.log('Message received:', event.data);
                    try {
                        const data = JSON.parse(event.data);
                        self.addOutput('📥 Response: ' + JSON.stringify(data, null, 2));
                    } catch (e) {
                        self.addOutput('📥 Raw response: ' + event.data);
                    }
                };
                
                this.ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                    self.addOutput('❌ Error: ' + error);
                    self.updateStatus('Error', false);
                };
                
                this.ws.onclose = function() {
                    console.log('WebSocket closed');
                    self.updateStatus('Disconnected', false);
                    self.addOutput('❌ WebSocket disconnected');
                };
            },
            
            disconnect: function() {
                if (this.ws) {
                    this.ws.close();
                }
            },
            
            sendCommand: function() {
                if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                    this.addOutput('❌ Not connected to WebSocket');
                    return;
                }
                
                const input = document.getElementById('input').value;
                try {
                    const command = JSON.parse(input);
                    this.addOutput('📤 Sending: ' + JSON.stringify(command, null, 2));
                    this.ws.send(JSON.stringify(command));
                } catch (e) {
                    this.addOutput('❌ Invalid JSON: ' + e.message);
                }
            },
            
            sendPreset: function(name) {
                if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                    this.addOutput('❌ Not connected to WebSocket');
                    return;
                }
                
                const command = this.presets[name];
                if (!command) {
                    this.addOutput('❌ Unknown preset: ' + name);
                    return;
                }
                
                document.getElementById('input').value = JSON.stringify(command, null, 2);
                this.addOutput('📤 Sending preset "' + name + '": ' + JSON.stringify(command, null, 2));
                this.ws.send(JSON.stringify(command));
            },
            
            addOutput: function(text) {
                const responseDiv = document.getElementById('response');
                const timestamp = new Date().toLocaleTimeString();
                responseDiv.textContent += '[' + timestamp + '] ' + text + '\n\n';
                responseDiv.scrollTop = responseDiv.scrollHeight;
            },
            
            clearResponse: function() {
                document.getElementById('response').textContent = 'Cleared. Waiting for responses...';
            },
            
            clearInput: function() {
                document.getElementById('input').value = '';
            },
            
            updateStatus: function(text, connected) {
                const status = document.getElementById('status');
                status.textContent = text;
                status.className = 'status ' + (connected ? 'connected' : 'disconnected');
            }
        };

        // Auto-connect on page load
        window.addEventListener('load', function() {
            console.log('Page loaded, auto-connecting...');
            window.testUI.connect();
        });
    </script>
</body>
</html>
"""

router = APIRouter()


@router.get("/test")
async def test_ui():
    """Serve the WebSocket test UI"""
    return HTMLResponse(content=HTML_CONTENT)
