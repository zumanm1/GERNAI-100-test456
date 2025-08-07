document.addEventListener('DOMContentLoaded', function () {
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');

    let sessionId = generateSessionId();
    const backendPort = 8002; // Match the .env FASTAPI_PORT
    let isConnected = true;

    function initializeChat() {
        console.log('Initializing chat with session ID:', sessionId);
        updateConnectionStatus('Connected to AI chat', 'success');
        loadChatHistory();
    }


    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // Display user message immediately
        displayMessage({
            role: 'user',
            content: message,
            timestamp: new Date().toISOString()
        });
        
        messageInput.value = '';
        showTypingIndicator();

        try {
            const response = await fetch(`http://localhost:${backendPort}/api/v1/chat/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            });

            if (response.ok) {
                const data = await response.json();
                removeTypingIndicator();
                displayMessage({
                    role: 'assistant',
                    content: data.response,
                    timestamp: new Date().toISOString()
                });
                updateConnectionStatus('Connected', 'success');
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            removeTypingIndicator();
            displayMessage({
                role: 'assistant',
                content: `Error: ${error.message}. Please check your connection and try again.`,
                timestamp: new Date().toISOString()
            });
            updateConnectionStatus('Connection Error', 'error');
        }
    }

    function generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    function showTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.classList.add('chat-message', 'chat-message-assistant', 'typing-indicator');
        typingElement.innerHTML = `
            <div class="message-avatar"></div>
            <div class="message-content">
                <div class="message-author">AI Assistant</div>
                <div class="message-text">AI is thinking...</div>
            </div>
        `;
        chatMessages.appendChild(typingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Remove typing indicator when response comes (handled in onmessage)
        setTimeout(() => {
            const indicators = document.querySelectorAll('.typing-indicator');
            indicators.forEach(indicator => indicator.remove());
        }, 30000); // Remove after 30 seconds max
    }

    function removeTypingIndicator() {
        const indicators = document.querySelectorAll('.typing-indicator');
        indicators.forEach(indicator => indicator.remove());
    }

    // Display message function to handle both user and AI responses
    function displayMessage(message) {
        removeTypingIndicator(); // Remove any typing indicators
        
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', `chat-message-${message.role}`);
        
        const avatarClass = message.role === 'user' ? 'user-avatar' : 'ai-avatar';
        const authorName = message.role === 'user' ? 'You' : 'AI Assistant';
        
        messageElement.innerHTML = `
            <div class="message-avatar ${avatarClass}"></div>
            <div class="message-content">
                <div class="message-author">${authorName}</div>
                <div class="message-text">${formatMessageContent(message.content)}</div>
                <div class="message-timestamp">${formatTimestamp(message.timestamp)}</div>
            </div>
        `;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function formatMessageContent(content) {
        // Basic formatting for code blocks and line breaks
        return content
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    function formatTimestamp(timestamp) {
        if (!timestamp) return '';
        return new Date(timestamp).toLocaleTimeString();
    }

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    // Load current AI model from settings and display it
    async function loadCurrentModel() {
        try {
            const response = await fetch('/api/v1/genai-settings/genai/core');
            if (response.ok) {
                const settings = await response.json();
                const modelDisplay = document.querySelector('.badge.bg-success-soft');
                if (modelDisplay) {
                    const provider = settings.default_chat_provider || 'openai';
                    modelDisplay.innerHTML = `<i data-lucide="cpu" class="me-1"></i>Model: ${provider.toUpperCase()}`;
                }
            }
        } catch (error) {
            console.error('Failed to load current model settings:', error);
        }
    }

    // Initialize chat functions
    function updateConnectionStatus(message, type) {
        if (typeof showToast === 'function') {
            showToast(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    async function loadChatHistory() {
        try {
            const response = await fetch(`http://localhost:${backendPort}/api/v1/chat/history/${sessionId}`);
            if (response.ok) {
                const history = await response.json();
                chatMessages.innerHTML = ''; // Clear existing messages
                history.forEach(msg => {
                    displayMessage({
                        role: msg.role,
                        content: msg.content,
                        timestamp: msg.timestamp
                    });
                });
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }

    initializeChat();
    loadCurrentModel();
});

