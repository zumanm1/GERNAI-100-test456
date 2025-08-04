#!/usr/bin/env python3
"""
Simple FastAPI server for testing purposes - Port 5000
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(
    title="Network Automation Test Backend",
    description="Simple test backend for URL testing",
    version="1.0.0"
)

# Basic HTML template for pages
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    <p>This is the {page} page running on port 5000</p>
    <p>Timestamp: {timestamp}</p>
</body>
</html>
'''

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    from datetime import datetime
    return HTML_TEMPLATE.format(
        title="Network Automation Dashboard", 
        page="dashboard",
        timestamp=datetime.now().isoformat()
    )

@app.get("/login", response_class=HTMLResponse)
async def login():
    from datetime import datetime
    return HTML_TEMPLATE.format(
        title="Login", 
        page="login",
        timestamp=datetime.now().isoformat()
    )

@app.get("/devices", response_class=HTMLResponse)
async def devices():
    from datetime import datetime
    return HTML_TEMPLATE.format(
        title="Devices", 
        page="devices",
        timestamp=datetime.now().isoformat()
    )

@app.get("/automation", response_class=HTMLResponse)
async def automation():
    from datetime import datetime
    return HTML_TEMPLATE.format(
        title="Automation", 
        page="automation",
        timestamp=datetime.now().isoformat()
    )

@app.get("/operations", response_class=HTMLResponse)
async def operations():
    from datetime import datetime
    return HTML_TEMPLATE.format(
        title="Operations", 
        page="operations",
        timestamp=datetime.now().isoformat()
    )

@app.get("/settings", response_class=HTMLResponse)
async def settings():
    from datetime import datetime
    return HTML_TEMPLATE.format(
        title="Settings", 
        page="settings",
        timestamp=datetime.now().isoformat()
    )

@app.get("/chat", response_class=HTMLResponse)
async def chat():
    from datetime import datetime
    return HTML_TEMPLATE.format(
        title="Chat", 
        page="chat",
        timestamp=datetime.now().isoformat()
    )

@app.get("/genai-settings", response_class=HTMLResponse)
async def genai_settings():
    from datetime import datetime
    return HTML_TEMPLATE.format(
        title="GenAI Settings", 
        page="genai-settings",
        timestamp=datetime.now().isoformat()
    )

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "network-automation-test-backend", "port": 5000}

# Basic API endpoints for testing
@app.get("/api/stats")
def get_stats():
    return {
        "devices": {"total": 5, "online": 3, "offline": 2},
        "operations": {"total_today": 10, "successful": 8, "failed": 2},
        "system": {"cpu_usage": 25.0, "memory_usage": 40.0}
    }

@app.get("/api/v1/devices/")
def get_devices():
    return [
        {"id": "1", "name": "Switch-01", "ip": "192.168.1.1", "status": "online"},
        {"id": "2", "name": "Router-01", "ip": "192.168.1.2", "status": "online"},
        {"id": "3", "name": "Firewall-01", "ip": "192.168.1.3", "status": "offline"}
    ]

@app.get("/api/v1/operations/")
def get_operations():
    return [
        {"id": "1", "type": "backup", "status": "completed", "device": "Switch-01"},
        {"id": "2", "type": "connectivity", "status": "running", "device": "Router-01"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
