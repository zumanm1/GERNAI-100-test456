/**
 * Modern Chat Interface for AI Network Assistant
 * Tesla-inspired design with clean, professional UX
 */

class ModernChatInterface {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.backendPort = 8002;
        this.isConnected = false;
        this.messageQueue = [];
        this.currentProvider = 'groq';
        
        this.initializeElements();
        this.setupEventListeners();
        this.initializeChat();
        this.loadSettings();
    }

    generateSessionId() {
        return `modern_session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.connectionStatus = document.getElementById('connection-status');
        this.modelStatus = document.getElementById('model-status');
        this.loadingOverlay = document.getElementById('loading-overlay');
    }

    setupEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enter key handling
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });

        // Prevent form submission
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
            }
        });
    }

    async initializeChat() {
        console.log('🚀 Initializing Modern Chat Interface');
        console.log(`Session ID: ${this.sessionId}`);
        
        // Test connection
        await this.testConnection();
        
        // Load chat history if available
        await this.loadChatHistory();
    }

    async testConnection() {
        try {
            const response = await fetch(`http://localhost:${this.backendPort}/health`);
            if (response.ok) {
                this.setConnectionStatus(true, 'Connected to AI Backend');
                this.isConnected = true;
            } else {
                throw new Error('Backend not responding');
            }
        } catch (error) {
            console.error('Connection test failed:', error);
            this.setConnectionStatus(false, 'Connection Failed');
        }
    }

    async loadSettings() {
        try {
            const response = await fetch(`http://localhost:${this.backendPort}/api/v1/settings/core`);
            if (response.ok) {
                const settings = await response.json();
                this.currentProvider = settings.default_chat_provider || 'groq';
                this.updateModelStatus();
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }

    updateModelStatus() {
        const providerNames = {
            'groq': 'Groq LLaMA 3-70B',
            'openrouter': 'OpenRouter Claude 3.5',
            'openai': 'OpenAI GPT-4',
            'anthropic': 'Anthropic Claude 3'
        };
        
        this.modelStatus.textContent = providerNames[this.currentProvider] || 'AI Model';
    }

    setConnectionStatus(connected, message) {
        const statusDiv = this.connectionStatus;
        const statusDot = statusDiv.querySelector('div');
        const statusText = statusDiv.querySelector('span');
        
        if (connected) {
            statusDot.className = 'w-2 h-2 bg-green-500 rounded-full';
            statusText.textContent = 'Connected';
            statusText.className = 'text-green-600';
        } else {
            statusDot.className = 'w-2 h-2 bg-red-500 rounded-full';
            statusText.textContent = 'Disconnected';
            statusText.className = 'text-red-600';
        }
        
        this.showToast(message, connected ? 'success' : 'error');
    }

    async loadChatHistory() {
        try {
            const response = await fetch(`http://localhost:${this.backendPort}/api/v1/chat/history/${this.sessionId}`);
            if (response.ok) {
                const history = await response.json();
                
                // Clear welcome message if we have history
                if (history.length > 0) {
                    this.clearWelcomeMessage();
                    
                    history.forEach(msg => {
                        this.displayMessage(msg.role, msg.content, msg.timestamp, false);
                    });
                }
                
                console.log(`📜 Loaded ${history.length} previous messages`);
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }

    clearWelcomeMessage() {
        const welcomeDiv = this.chatMessages.querySelector('.max-w-4xl');
        if (welcomeDiv) {
            welcomeDiv.remove();
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || !this.isConnected) return;

        // Clear input
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';

        // Clear welcome message if this is first message
        this.clearWelcomeMessage();

        // Display user message immediately
        this.displayMessage('user', message, new Date().toISOString());

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch(`http://localhost:${this.backendPort}/api/v1/chat/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.hideTypingIndicator();
                this.displayMessage('assistant', data.response, new Date().toISOString());
                this.setConnectionStatus(true, 'Connected');
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.displayMessage('assistant', `⚠️ Error: ${error.message}. Please check your connection and try again.`, new Date().toISOString());
            this.setConnectionStatus(false, 'Connection Error');
        }
    }

    displayMessage(role, content, timestamp, animate = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `max-w-4xl mx-auto ${animate ? 'message-bubble' : ''}`;
        
        const isUser = role === 'user';
        const avatarIcon = isUser ? 'user' : 'bot';
        const messageClass = isUser ? 'ml-12' : 'mr-12';
        const bgClass = isUser ? 'bg-tesla-red text-white' : 'bg-gray-50 text-gray-900';
        const alignClass = isUser ? 'flex-row-reverse' : 'flex-row';
        
        messageDiv.innerHTML = `
            <div class="flex ${alignClass} space-x-3 mb-4">
                <!-- Avatar -->
                <div class="flex-shrink-0">
                    <div class="w-10 h-10 ${isUser ? 'bg-tesla-red' : 'bg-gray-300'} rounded-full flex items-center justify-center">
                        <i data-lucide="${avatarIcon}" class="w-5 h-5 ${isUser ? 'text-white' : 'text-gray-600'}"></i>
                    </div>
                </div>
                
                <!-- Message Content -->
                <div class="flex-1 ${messageClass}">
                    <div class="${bgClass} rounded-2xl px-4 py-3 shadow-sm">
                        <div class="message-content">
                            ${this.formatMessageContent(content)}
                        </div>
                    </div>
                    
                    <!-- Timestamp -->
                    <div class="text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}">
                        ${this.formatTimestamp(timestamp)}
                    </div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        
        // Initialize icons
        lucide.createIcons();
        
        // Scroll to bottom
        this.scrollToBottom();
    }

    formatMessageContent(content) {
        // Enhanced content formatting
        return content
            // Code blocks
            .replace(/```(\w+)?\n([\s\S]*?)```/g, '<div class="code-block rounded-lg p-4 mt-2 mb-2 overflow-x-auto"><pre class="text-sm text-gray-300"><code>$2</code></pre></div>')
            // Inline code
            .replace(/`([^`]+)`/g, '<code class="bg-gray-200 text-gray-800 px-2 py-1 rounded text-sm">$1</code>')
            // Bold text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Network commands highlighting
            .replace(/^(\s*\w+#|\s*\w+\(config\)#|\s*\w+\(config-\w+\)#)/gm, '<span class="text-blue-600 font-medium">$1</span>')
            // Line breaks
            .replace(/\n/g, '<br>');
    }

    formatTimestamp(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'max-w-4xl mx-auto typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="flex flex-row space-x-3 mb-4">
                <!-- Avatar -->
                <div class="flex-shrink-0">
                    <div class="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                        <i data-lucide="bot" class="w-5 h-5 text-gray-600"></i>
                    </div>
                </div>
                
                <!-- Typing Content -->
                <div class="flex-1 mr-12">
                    <div class="bg-gray-50 text-gray-900 rounded-2xl px-4 py-3 shadow-sm">
                        <div class="flex space-x-1">
                            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        lucide.createIcons();
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTo({
            top: this.chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }

    showToast(message, type = 'info') {
        // Create toast if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(toastContainer);
        }

        const toast = document.createElement('div');
        const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';
        
        toast.className = `${bgColor} text-white px-4 py-3 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full`;
        toast.textContent = message;

        toastContainer.appendChild(toast);

        // Slide in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
}

// Global functions for quick actions
function sendQuickMessage(message) {
    if (window.chatInterface) {
        window.chatInterface.messageInput.value = message;
        window.chatInterface.sendMessage();
    }
}

// Initialize chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Loading Modern Chat Interface...');
    window.chatInterface = new ModernChatInterface();
});
