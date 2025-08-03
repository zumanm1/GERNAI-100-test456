from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.ai.ai_service import ai_service
from backend.database.models import AIConversation, User
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
import json
import logging
from .websocket_manager import chat_manager
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str


@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_message: ChatMessage,
    user_id: str = "default_user",  # TODO: Implement proper authentication
    db: Session = Depends(get_db)
):
    """Send message to AI and get response"""
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Save user message to database
        user_conversation = ai_service.save_conversation(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=chat_message.message,
            db=db
        )
        
        # Get AI response
        ai_response = ai_service.get_response(
            user_message=chat_message.message,
            session_id=session_id,
            user_id=user_id,
            db=db
        )
        
        # Save AI response to database
        ai_conversation = ai_service.save_conversation(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=ai_response,
            db=db
        )
        
        # Broadcast to WebSocket connections using unified schema
        await broadcast_message({
            'type': 'chat_response',
            'session_id': session_id,
            'role': 'assistant',
            'content': ai_response,
            'timestamp': ai_conversation.created_at.isoformat()
        })
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            message_id=ai_conversation.id
        )
        
    except Exception as e:
        logger.error(f"Error in chat send: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    user_id: str = "default_user",  # TODO: Implement proper authentication
    db: Session = Depends(get_db)
):
    """Get chat history for a session"""
    try:
        conversations = db.query(AIConversation).filter(
            AIConversation.session_id == session_id,
            AIConversation.user_id == user_id
        ).order_by(AIConversation.created_at.asc()).limit(limit).all()
        
        return [
            {
                'id': conv.id,
                'role': conv.message_role,
                'content': conv.message_content,
                'timestamp': conv.created_at.isoformat(),
                'metadata': conv.metadata
            }
            for conv in conversations
        ]
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_chat_sessions(
    user_id: str = "default_user",  # TODO: Implement proper authentication
    db: Session = Depends(get_db)
):
    """Get all chat sessions for a user"""
    try:
        # Get unique session IDs for the user
        sessions = db.query(AIConversation.session_id).filter(
            AIConversation.user_id == user_id
        ).distinct().all()
        
        session_info = []
        for session in sessions:
            # Get the latest message for each session
            latest_message = db.query(AIConversation).filter(
                AIConversation.session_id == session.session_id,
                AIConversation.user_id == user_id
            ).order_by(AIConversation.created_at.desc()).first()
            
            if latest_message:
                session_info.append({
                    'session_id': session.session_id,
                    'last_message': latest_message.message_content[:100] + "..." if len(latest_message.message_content) > 100 else latest_message.message_content,
                    'last_updated': latest_message.created_at.isoformat(),
                    'message_count': db.query(AIConversation).filter(
                        AIConversation.session_id == session.session_id,
                        AIConversation.user_id == user_id
                    ).count()
                })
        
        return sorted(session_info, key=lambda x: x['last_updated'], reverse=True)
        
    except Exception as e:
        logger.error(f"Error getting chat sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    user_id: str = "default_user",  # TODO: Implement proper authentication
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    try:
        # Delete all conversations in the session
        deleted_count = db.query(AIConversation).filter(
            AIConversation.session_id == session_id,
            AIConversation.user_id == user_id
        ).delete()
        
        db.commit()
        
        return {
            'message': f'Deleted {deleted_count} messages from session {session_id}',
            'session_id': session_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-config")
async def generate_configuration(
    config_type: str,
    parameters: dict,
    user_id: str = "default_user",  # TODO: Implement proper authentication
    db: Session = Depends(get_db)
):
    """Generate network configuration using AI"""
    try:
        config = ai_service.generate_configuration(config_type, parameters)
        
        # Log the generation as a conversation
        session_id = str(uuid.uuid4())
        ai_service.save_conversation(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=f"Generate {config_type} configuration with parameters: {json.dumps(parameters)}",
            db=db
        )
        
        ai_service.save_conversation(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=config,
            db=db,
            metadata={'config_type': config_type, 'parameters': parameters}
        )
        
        return {
            'configuration': config,
            'config_type': config_type,
            'parameters': parameters,
            'session_id': session_id
        }
        
    except Exception as e:
        logger.error(f"Error generating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-config")
async def validate_configuration(
    config_content: str,
    device_type: str = "ios",
    user_id: str = "default_user",  # TODO: Implement proper authentication
    db: Session = Depends(get_db)
):
    """Validate network configuration using AI"""
    try:
        validation_result = ai_service.validate_configuration(config_content, device_type)
        
        # Log the validation as a conversation
        session_id = str(uuid.uuid4())
        ai_service.save_conversation(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=f"Validate {device_type} configuration",
            db=db
        )
        
        ai_service.save_conversation(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=f"Configuration validation result: {json.dumps(validation_result)}",
            db=db,
            metadata={'validation_result': validation_result, 'device_type': device_type}
        )
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Error validating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time chat
@router.websocket("/chat/ws")
async def websocket_endpoint(websocket: WebSocket):
    session_id = str(uuid.uuid4())
    await chat_manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Handle different message types following unified schema
            if message_data.get('type') == 'chat_message':
                # Echo back the user message with unified schema
                user_message = {
                    'type': 'message_received',
                    'session_id': session_id,
                    'role': 'user',
                    'content': message_data.get('content', ''),
                    'timestamp': datetime.now().isoformat()
                }
                await chat_manager.send_personal_message(user_message, session_id)
                
            elif message_data.get('type') == 'join_session':
                # Handle user joining a specific chat session
                requested_session_id = message_data.get('session_id')
                if requested_session_id:
                    session_id = requested_session_id
                    
                join_message = {
                    'type': 'session_joined',
                    'session_id': session_id,
                    'role': 'system',
                    'content': f'Joined session {session_id}',
                    'timestamp': datetime.now().isoformat()
                }
                await chat_manager.send_personal_message(join_message, session_id)
                
            elif message_data.get('type') == 'ping':
                # Handle ping/pong for connection health
                pong_message = {
                    'type': 'pong',
                    'session_id': session_id,
                    'role': 'system',
                    'content': 'pong',
                    'timestamp': datetime.now().isoformat()
                }
                await chat_manager.send_personal_message(pong_message, session_id)

    except WebSocketDisconnect:
        chat_manager.disconnect(session_id)
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        chat_manager.disconnect(session_id)

async def broadcast_message(message: dict):
    """Broadcast message to all active WebSocket connections using unified schema"""
    await chat_manager.broadcast(message)
