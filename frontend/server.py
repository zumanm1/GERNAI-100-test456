from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocketDisconnect
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the directory of the current script
frontend_dir = os.path.dirname(__file__)

# Initialize the FastAPI app
app = FastAPI(
    title="Network Automation Frontend",
    description="Frontend server for serving static files and real-time updates",
    version="1.0.0"
)

# Mount static files
static_files_path = os.path.join(frontend_dir, "static")
app.mount("/static", StaticFiles(directory=static_files_path), name="static")

# Setup templating
templates_path = os.path.join(frontend_dir, "templates")
templates = Jinja2Templates(directory=templates_path)


@app.get("/")
async def read_root():
    return FileResponse(os.path.join(frontend_dir, 'templates/auth/login.html'))

@app.get("/devices")
async def read_devices(request: Request):
    return templates.TemplateResponse("devices/index.html", {"request": request})

@app.get("/genai")
async def read_genai(request: Request):
    return templates.TemplateResponse("genai-settings/index.html", {"request": request})

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        pass

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Dashboard page rendering"""
    return templates.TemplateResponse("dashboard/index.html", {"request": request})

@app.get("/automation", response_class=HTMLResponse)
async def get_automation(request: Request):
    """Automation page rendering"""
    return templates.TemplateResponse("automation/index.html", {"request": request})

@app.get("/device-management", response_class=HTMLResponse)
async def get_device_management(request: Request):
    """Device management page"""
    return templates.TemplateResponse("devices/index.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def get_chat(request: Request):
    """Chat page rendering"""
    return templates.TemplateResponse("chat/index.html", {"request": request})

@app.get("/operations", response_class=HTMLResponse)
async def get_operations(request: Request):
    """Operations page rendering"""
    return templates.TemplateResponse("operations/index.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def get_settings(request: Request):
    """Settings page rendering"""
    return templates.TemplateResponse("settings/index.html", {"request": request})


if __name__ == "__main__":
    # Run the server using FRONTEND_PORT from .env, default to 8001
    port = int(os.getenv("FRONTEND_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
