# DEVELOPMENT NOTE: 
# During development, DO NOT use Docker or Docker Compose!
# This main.py runs the FastAPI application directly using Python/uvicorn.
# ChromaDB and Ollama services should be started locally, not via Docker.
# Docker will be used only after successful development completion.

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv
import uuid

# Import AI components
from backend.ai.llm_manager import llm_manager, LLMSettings, initialize_llm_manager
from backend.database.database import get_db

# Load environment variables from .env file
load_dotenv()

# Create the FastAPI app
app = FastAPI(
    title="Network Automation Application",
    description="A GENAI-powered network automation application for Cisco devices",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """
    Initializes LLM providers on application startup using database configuration.
    """
    print("Initializing application services...")
    
    try:
        # Get database session
        db = next(get_db())
        
        # Initialize LLM manager with database session
        print("Initializing LLM manager with database session...")
        initialize_llm_manager(db)
        
        print("✓ LLM manager initialized successfully")
        
        # Initialize AI providers from environment as fallback
        print("Setting up fallback AI providers from environment...")
        
        # Configure OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key and openai_api_key not in ["your_openai_api_key", "xxxxxxxxxxxxxxx"]:
            print("✓ OpenAI API key found in environment")
        else:
            print("⚠ OpenAI API key not found in environment")

        # Configure Anthropic
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_api_key and anthropic_api_key not in ["your_anthropic_api_key", "xxxxxxxxxxxxxxx"]:
            print("✓ Anthropic API key found in environment")
        else:
            print("⚠ Anthropic API key not found in environment")

        # Configure Groq
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key and groq_api_key not in ["your_groq_api_key", "xxxxxxxxxxxxxxx"]:
            print("✓ Groq API key found in environment")
        else:
            print("⚠ Groq API key not found in environment")

        # Configure OpenRouter
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_api_key and openrouter_api_key not in ["your_openrouter_api_key", "xxxxxxxxxxxxxxx"]:
            print("✓ OpenRouter API key found in environment")
        else:
            print("⚠ OpenRouter API key not found in environment")
        
        print("🚀 Application startup completed successfully")
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        print("⚠ Application will continue with limited functionality")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8001",  # Frontend server
        "http://127.0.0.1:8001",  # Alternative frontend
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import the main API router
from backend.api.main import api_router

# Setup static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Include the main API router
app.include_router(api_router, prefix="/api")

# Add WebSocket support for operations
from backend.websocket_manager import connection_manager
from fastapi import WebSocket, WebSocketDisconnect
import json

@app.websocket("/ws/operations")
async def websocket_operations(websocket: WebSocket):
    client_id = str(uuid.uuid4())
    
    try:
        await connection_manager.connect(websocket, client_id, "command_execution")
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await connection_manager.send_personal_message({
                        "type": "pong",
                        "timestamp": str(uuid.uuid4())  # Simple timestamp
                    }, client_id)
                elif message.get("type") == "subscribe":
                    operation_type = message.get("operation_type", "command_execution")
                    if operation_type in connection_manager.operation_connections:
                        connection_manager.operation_connections[operation_type].add(client_id)
                        await connection_manager.send_personal_message({
                            "type": "subscribed",
                            "operation_type": operation_type,
                            "message": f"Subscribed to {operation_type} updates"
                        }, client_id)
                        
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        connection_manager.disconnect(client_id)

# Frontend routes
@app.get("/")
async def welcome_api():
    return {
        "message": "Welcome to the Network Automation API",
        "service": "network-automation-api",
        "version": "1.0.0",
        "description": "A GENAI-powered network automation application for Cisco devices",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "api_routes": "/api",
            "websocket": "/ws/operations"
        },
        "status": "running",
        "frontend_url": "http://localhost:8001"
    }

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.get("/devices", response_class=HTMLResponse)
async def devices(request: Request):
    return templates.TemplateResponse("devices/index.html", {"request": request})

@app.get("/automation", response_class=HTMLResponse)
async def automation(request: Request):
    return templates.TemplateResponse("automation/index.html", {"request": request})

@app.get("/operations", response_class=HTMLResponse)
async def operations(request: Request):
    return templates.TemplateResponse("operations/index.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    return templates.TemplateResponse("settings/modern.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse("chat/modern.html", {"request": request})

@app.get("/genai-settings", response_class=HTMLResponse)
async def genai_settings(request: Request):
    return templates.TemplateResponse("genai-settings/index.html", {"request": request})

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    """Handle 404 errors with custom page"""
    error_id = str(uuid.uuid4())[:8]
    return templates.TemplateResponse(
        "errors/404.html", 
        {"request": request, "error_id": error_id}, 
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle 500 errors"""
    error_id = str(uuid.uuid4())[:8]
    return templates.TemplateResponse(
        "errors/500.html", 
        {"request": request, "error_id": error_id}, 
        status_code=500
    )

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "network-automation-api"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("FASTAPI_PORT", 8002))  # Use FASTAPI_PORT from .env
    uvicorn.run(app, host="0.0.0.0", port=port)
