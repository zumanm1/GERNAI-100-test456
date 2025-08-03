"""
Simple test to verify ChatWebSocketManager functionality
"""
import pytest
import asyncio
from unittest.mock import AsyncMock
from backend.chat.websocket_manager import ChatWebSocketManager


def test_chat_websocket_manager_initialization():
    """Test that ChatWebSocketManager initializes correctly"""
    manager = ChatWebSocketManager()
    assert manager.active_connections == {}
    assert manager.connection_metadata == {}


@pytest.mark.asyncio
async def test_connect_and_disconnect():
    """Test WebSocket connection and disconnection"""
    manager = ChatWebSocketManager()
    mock_websocket = AsyncMock()
    session_id = "test-session-123"
    
    # Test connection
    await manager.connect(mock_websocket, session_id)
    
    # Verify connection was established
    assert session_id in manager.active_connections
    assert session_id in manager.connection_metadata
    assert manager.connection_metadata[session_id]['message_count'] == 1  # Connection confirmation message
    
    # Test disconnection
    manager.disconnect(session_id)
    
    # Verify connection was removed
    assert session_id not in manager.active_connections
    assert session_id not in manager.connection_metadata


@pytest.mark.asyncio 
async def test_message_schema():
    """Test that messages follow the unified schema"""
    manager = ChatWebSocketManager()
    mock_websocket = AsyncMock()
    session_id = "test-session-456"
    
    await manager.connect(mock_websocket, session_id)
    
    # Check that connection confirmation message follows schema
    sent_calls = mock_websocket.send_text.call_args_list
    assert len(sent_calls) > 0
    
    # Parse the sent message to verify schema
    import json
    sent_message = json.loads(sent_calls[0][0][0])
    
    # Verify unified schema: {type, session_id, role, content, timestamp}
    required_fields = ['type', 'session_id', 'role', 'content', 'timestamp']
    for field in required_fields:
        assert field in sent_message, f"Missing required field: {field}"
    
    assert sent_message['type'] == 'connection_confirmed'
    assert sent_message['session_id'] == session_id
    assert sent_message['role'] == 'system'
    assert sent_message['content'] == 'Connected to chat'


def test_active_sessions():
    """Test getting active sessions"""
    manager = ChatWebSocketManager()
    
    # Initially no sessions
    assert manager.get_active_sessions() == []
    
    # Add some mock sessions
    manager.active_connections['session1'] = AsyncMock()
    manager.active_connections['session2'] = AsyncMock()
    
    active_sessions = manager.get_active_sessions()
    assert len(active_sessions) == 2
    assert 'session1' in active_sessions
    assert 'session2' in active_sessions


if __name__ == "__main__":
    print("Running basic tests for ChatWebSocketManager...")
    
    # Test initialization
    test_chat_websocket_manager_initialization()
    print("✓ Initialization test passed")
    
    # Test active sessions
    test_active_sessions()
    print("✓ Active sessions test passed")
    
    print("All basic tests passed!")
