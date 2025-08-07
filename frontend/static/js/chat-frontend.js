/**
 * AI Network Assistant - Frontend Chat Interface
 * Modern JavaScript for chat functionality with backend API communication
 */

class ChatInterface {
    constructor() {
        // Configuration
        this.config = {
            backendUrl: 'http://localhost:8002',
            endpoints: {
                chat: '/api/v1/chat/send',
                status: '/api/chat/status',
                models: '/api/v1/models'
            },
            requestTimeout: 30000,
            retryAttempts: 3
        };

        // State
        this.isConnected = false;
        this.isTyping = false;
        this.messageHistory = [];
        this.currentSessionId = this.generateSessionId();

        // DOM Elements
        this.elements = {
            chatMessages: document.getElementById('chat-messages'),
            messageInput: document.getElementById('message-input'),
            sendButton: document.getElementById('send-button'),
            connectionStatus: document.getElementById('connection-status'),
            modelStatus: document.getElementById('model-status'),
            loadingOverlay: document.getElementById('loading-overlay')
        };

        // Initialize
        this.init();
    }

    async init() {
        try {
            console.log('🚀 Initializing Chat Interface...');
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Check backend connection
            await this.checkConnection();
            
            // Load chat history from localStorage
            this.loadChatHistory();
            
            console.log('✅ Chat Interface initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize chat interface:', error);
            this.showError('Failed to initialize chat interface');
        }
    }

    setupEventListeners() {
        // Send button click
        this.elements.sendButton?.addEventListener('click', () => {
            this.handleSendMessage();
        });

        // Enter key in textarea (Shift+Enter for new line)
        this.elements.messageInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });

        // Auto-resize textarea
        this.elements.messageInput?.addEventListener('input', this.autoResizeTextarea.bind(this));

        // Connection status check interval
        setInterval(() => {
            this.checkConnection();
        }, 30000); // Check every 30 seconds
    }

    async checkConnection() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);

            const response = await fetch(`${this.config.backendUrl}${this.config.endpoints.status}`, {
                method: 'GET',
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                const data = await response.json();
                this.isConnected = true;
                this.updateConnectionStatus(true, 'Connected');
                this.updateModelStatus(data.model || 'Groq LLaMA 3-70B');
                return true;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.warn('Backend connection check failed:', error.message);
            this.isConnected = false;
            this.updateConnectionStatus(false, 'Disconnected');
            return false;
        }
    }

    updateConnectionStatus(connected, text) {
        const statusEl = this.elements.connectionStatus;
        if (!statusEl) return;

        const indicator = statusEl.querySelector('.w-2');
        const textEl = statusEl.querySelector('span');

        if (indicator && textEl) {
            indicator.className = connected 
                ? 'w-2 h-2 bg-green-500 rounded-full'
                : 'w-2 h-2 bg-red-500 rounded-full';
            textEl.textContent = text;
        }
    }

    updateModelStatus(model) {
        const modelEl = this.elements.modelStatus;
        if (modelEl) {
            modelEl.textContent = model;
        }
    }

    autoResizeTextarea() {
        const textarea = this.elements.messageInput;
        if (!textarea) return;

        textarea.style.height = 'auto';
        const newHeight = Math.min(textarea.scrollHeight, 120);
        textarea.style.height = newHeight + 'px';
    }

    async handleSendMessage() {
        const message = this.elements.messageInput?.value.trim();
        if (!message) return;

        // Disable input while processing
        this.setInputDisabled(true);

        try {
            // Add user message to chat
            this.addMessage('user', message);
            
            // Clear input
            this.elements.messageInput.value = '';
            this.autoResizeTextarea();
            
            // Save to history
            this.messageHistory.push({ role: 'user', content: message, timestamp: Date.now() });
            
            // Show typing indicator
            const typingId = this.showTypingIndicator();
            
            // Send to backend
            const response = await this.sendToBackend(message);
            
            // Remove typing indicator
            this.removeTypingIndicator(typingId);
            
            // Add AI response
            if (response && response.response) {
                this.addMessage('assistant', response.response);
                this.messageHistory.push({ 
                    role: 'assistant', 
                    content: response.response, 
                    timestamp: Date.now() 
                });
                
                // Update session ID if provided
                if (response.session_id) {
                    this.currentSessionId = response.session_id;
                }
            } else {
                throw new Error('Invalid response from backend');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.removeTypingIndicator();
            this.showError('Failed to send message. Please try again.');
        } finally {
            this.setInputDisabled(false);
            this.saveChatHistory();
            this.scrollToBottom();
        }
    }

    async sendToBackend(message) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.requestTimeout);

        try {
            const response = await fetch(`${this.config.backendUrl}${this.config.endpoints.chat}`, {
                method: 'POST',
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSessionId,
                    history: this.messageHistory.slice(-10) // Send last 10 messages for context
                })
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timed out');
            }
            throw error;
        }
    }

    addMessage(role, content) {
        const messagesContainer = this.elements.chatMessages;
        if (!messagesContainer) return;

        // Hide welcome message if it exists
        this.hideWelcomeMessage();

        const messageDiv = document.createElement('div');
        messageDiv.className = `message-bubble ${role === 'user' ? 'ml-auto' : 'mr-auto'}`;

        const isUser = role === 'user';
        const bgColor = isUser ? 'bg-tesla-red text-white' : 'bg-gray-100 text-gray-900';
        const alignment = isUser ? 'text-right' : 'text-left';

        messageDiv.innerHTML = `
            <div class="max-w-4xl mx-auto">
                <div class="flex ${isUser ? 'justify-end' : 'justify-start'} mb-4">
                    <div class="flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3 max-w-3xl">
                        <!-- Avatar -->
                        <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-tesla-red ml-3' : 'bg-gray-600 mr-3'}">
                            <i data-lucide="${isUser ? 'user' : 'bot'}" class="w-4 h-4 text-white"></i>
                        </div>
                        
                        <!-- Message Content -->
                        <div class="${bgColor} rounded-2xl px-4 py-3 ${alignment} shadow-sm">
                            <div class="prose prose-sm max-w-none ${isUser ? 'prose-invert' : ''}">
                                ${this.formatMessage(content)}
                            </div>
                            <div class="text-xs opacity-70 mt-2">
                                ${new Date().toLocaleTimeString()}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        
        // Re-initialize Lucide icons for new content
        if (window.lucide) {
            lucide.createIcons();
        }

        this.scrollToBottom();
    }

    formatMessage(content) {
        // Basic markdown-like formatting
        let formatted = content;
        
        // Code blocks
        formatted = formatted.replace(/```(\w+)?\n?([\s\S]*?)```/g, (match, lang, code) => {
            return `<pre class="code-block rounded-lg p-4 my-3 overflow-x-auto"><code class="language-${lang || 'text'}">${this.escapeHtml(code.trim())}</code></pre>`;
        });
        
        // Inline code
        formatted = formatted.replace(/`([^`]+)`/g, '<code class="bg-gray-200 px-1 py-0.5 rounded text-sm font-mono">$1</code>');
        
        // Bold text
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Convert line breaks to HTML
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showTypingIndicator() {
        const typingId = 'typing-' + Date.now();
        const messagesContainer = this.elements.chatMessages;
        if (!messagesContainer) return typingId;

        this.hideWelcomeMessage();

        const typingDiv = document.createElement('div');
        typingDiv.id = typingId;
        typingDiv.className = 'message-bubble mr-auto typing-indicator';
        typingDiv.innerHTML = `
            <div class="max-w-4xl mx-auto">
                <div class="flex justify-start mb-4">
                    <div class="flex items-start space-x-3 max-w-3xl">
                        <div class="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0">
                            <i data-lucide="bot" class="w-4 h-4 text-white"></i>
                        </div>
                        <div class="bg-gray-100 rounded-2xl px-4 py-3 shadow-sm">
                            <div class="flex space-x-1">
                                <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                                <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style="animation-delay: 0.2s"></div>
                                <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style="animation-delay: 0.4s"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        messagesContainer.appendChild(typingDiv);
        
        if (window.lucide) {
            lucide.createIcons();
        }
        
        this.scrollToBottom();
        return typingId;
    }

    removeTypingIndicator(typingId) {
        if (typingId) {
            const typingEl = document.getElementById(typingId);
            if (typingEl) {
                typingEl.remove();
            }
        }
    }

    hideWelcomeMessage() {
        const welcomeDiv = this.elements.chatMessages?.querySelector('.text-center.py-12');
        if (welcomeDiv) {
            welcomeDiv.style.display = 'none';
        }
    }

    setInputDisabled(disabled) {
        const input = this.elements.messageInput;
        const button = this.elements.sendButton;
        
        if (input) {
            input.disabled = disabled;
        }
        if (button) {
            button.disabled = disabled;
            button.classList.toggle('opacity-50', disabled);
        }
    }

    showError(message) {
        // Show error as a system message
        const messagesContainer = this.elements.chatMessages;
        if (!messagesContainer) return;

        const errorDiv = document.createElement('div');
        errorDiv.className = 'max-w-4xl mx-auto mb-4';
        errorDiv.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center space-x-3">
                <i data-lucide="alert-circle" class="w-5 h-5 text-red-500 flex-shrink-0"></i>
                <div>
                    <p class="text-red-800 font-medium">Error</p>
                    <p class="text-red-600 text-sm">${message}</p>
                </div>
            </div>
        `;

        messagesContainer.appendChild(errorDiv);
        
        if (window.lucide) {
            lucide.createIcons();
        }
        
        this.scrollToBottom();
    }

    scrollToBottom() {
        const container = this.elements.chatMessages;
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    saveChatHistory() {
        try {
            localStorage.setItem('chat_history', JSON.stringify(this.messageHistory));
        } catch (error) {
            console.warn('Failed to save chat history:', error);
        }
    }

    loadChatHistory() {
        try {
            const saved = localStorage.getItem('chat_history');
            if (saved) {
                const history = JSON.parse(saved);
                // Load recent messages (last 20)
                this.messageHistory = history.slice(-20);
                
                // Display last few messages
                this.messageHistory.slice(-5).forEach(msg => {
                    if (msg.role && msg.content) {
                        this.addMessage(msg.role, msg.content);
                    }
                });
            }
        } catch (error) {
            console.warn('Failed to load chat history:', error);
            this.messageHistory = [];
        }
    }

    clearHistory() {
        this.messageHistory = [];
        localStorage.removeItem('chat_history');
        
        // Clear messages display
        const messagesContainer = this.elements.chatMessages;
        if (messagesContainer) {
            messagesContainer.innerHTML = `
                <div class="max-w-4xl mx-auto">
                    <div class="text-center py-12">
                        <div class="w-16 h-16 bg-tesla-red rounded-full flex items-center justify-center mx-auto mb-4">
                            <i data-lucide="bot" class="w-8 h-8 text-white"></i>
                        </div>
                        <h2 class="text-2xl font-semibold text-gray-900 mb-2">Welcome to AI Network Assistant</h2>
                        <p class="text-gray-600 max-w-md mx-auto">
                            Your intelligent companion for Cisco network automation, configuration, and troubleshooting.
                        </p>
                    </div>
                </div>
            `;
            
            if (window.lucide) {
                lucide.createIcons();
            }
        }
    }
}

// Quick message function for welcome buttons
window.sendQuickMessage = function(message) {
    if (window.chatInterface && message) {
        const input = document.getElementById('message-input');
        if (input) {
            input.value = message;
            window.chatInterface.handleSendMessage();
        }
    }
};

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 DOM loaded, initializing chat interface...');
    window.chatInterface = new ChatInterface();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatInterface;
}
