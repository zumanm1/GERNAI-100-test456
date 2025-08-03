"""
WebSocket Manager for Chat
Handles WebSocket connections, message broadcasting, and chat message history
"""
import json
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ChatWebSocketManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        # Store active connections by session ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Track connection metadata
        self.connection_metadata: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.connection_metadata[session_id] = {
            'connected_at': datetime.now().isoformat(),
            'message_count': 0
        }
        logger.info(f"Session {session_id} connected")
        
        # Send connection confirmation with unified schema
        await self.send_personal_message({
            'type': 'connection_confirmed',
            'session_id': session_id,
            'role': 'system',
            'content': 'Connected to chat',
            'timestamp': datetime.now().isoformat()
        }, session_id)
        
    def disconnect(self, session_id: str):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.connection_metadata:
            del self.connection_metadata[session_id]
        logger.info(f"Session {session_id} disconnected")
        
    async def send_personal_message(self, message: dict, session_id: str):
        """Send message to specific session"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
                # Update message count
                if session_id in self.connection_metadata:
                    self.connection_metadata[session_id]['message_count'] += 1
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        disconnected_sessions = []
        for session_id in list(self.active_connections.keys()):
            try:
                await self.send_personal_message(message, session_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {session_id}: {e}")
                disconnected_sessions.append(session_id)
                
        for session_id in disconnected_sessions:
            self.disconnect(session_id)
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_info(self, session_id: str) -> dict:
        """Get connection metadata for a session"""
        return self.connection_metadata.get(session_id, {})

chat_manager = ChatWebSocketManager()
