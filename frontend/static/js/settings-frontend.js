/**
 * AI Network Assistant - Frontend Settings Interface
 * Modern JavaScript for settings management with backend API communication
 */

class SettingsInterface {
    constructor() {
        // Configuration
        this.config = {
            backendUrl: 'http://localhost:8002',
            endpoints: {
                settings: '/api/v1/settings',
                status: '/api/chat/status',
                models: '/api/v1/models'
            },
            requestTimeout: 10000
        };

        // Default settings
        this.defaultSettings = {
            // AI Model Settings
            modelProvider: 'groq',
            groqModel: 'llama3-70b-8192',
            openaiModel: 'gpt-4o',
            claudeModel: 'claude-3.5-sonnet',
            openrouterModel: 'anthropic/claude-3.5-sonnet',
            geminiModel: 'gemini-1.5-pro',
            temperature: 0.7,
            maxTokens: 4096,
            
            // Interface Settings
            darkMode: false,
            autoScroll: true,
            soundEffects: false,
            messageStyle: 'bubbles',
            
            // Network Settings
            backendUrl: 'http://localhost:8002',
            requestTimeout: 30
        };

        // Current settings (will be loaded from backend or localStorage)
        this.currentSettings = { ...this.defaultSettings };

        // DOM Elements
        this.elements = {
            // AI Model Settings
            modelProvider: document.getElementById('model-provider'),
            groqModel: document.getElementById('groq-model'),
            temperatureSlider: document.getElementById('temperature-slider'),
            temperatureValue: document.getElementById('temperature-value'),
            maxTokensSlider: document.getElementById('max-tokens-slider'),
            maxTokensValue: document.getElementById('max-tokens-value'),
            
            // Interface Settings
            darkMode: document.getElementById('dark-mode'),
            autoScroll: document.getElementById('auto-scroll'),
            soundEffects: document.getElementById('sound-effects'),
            messageStyle: document.getElementById('message-style'),
            
            // Network Settings
            backendUrl: document.getElementById('backend-url'),
            timeoutSlider: document.getElementById('timeout-slider'),
            timeoutValue: document.getElementById('timeout-value'),
            
            // Status & Actions
            connectionIndicator: document.getElementById('connection-indicator'),
            connectionText: document.getElementById('connection-text'),
            backendStatus: document.getElementById('backend-status'),
            currentModel: document.getElementById('current-model'),
            lastUpdated: document.getElementById('last-updated'),
            
            // Buttons
            saveButton: document.getElementById('save-settings'),
            resetButton: document.getElementById('reset-settings'),
            exportButton: document.getElementById('export-settings'),
            testConnectionButton: document.getElementById('test-connection'),
            
            // Toast
            successToast: document.getElementById('success-toast')
        };

        // Initialize
        this.init();
    }

    async init() {
        try {
            console.log('🚀 Initializing Settings Interface...');
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load settings
            await this.loadSettings();
            
            // Update UI with loaded settings
            this.updateUI();
            
            // Test backend connection
            await this.testConnection();
            
            console.log('✅ Settings Interface initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize settings interface:', error);
            this.showError('Failed to initialize settings interface');
        }
    }

    setupEventListeners() {
        // Model provider change
        this.elements.modelProvider?.addEventListener('change', (e) => {
            this.currentSettings.modelProvider = e.target.value;
            this.updateModelSpecificSettings();
        });

        // Groq model change
        this.elements.groqModel?.addEventListener('change', (e) => {
            this.currentSettings.groqModel = e.target.value;
        });

        // Temperature slider
        this.elements.temperatureSlider?.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            this.currentSettings.temperature = value;
            if (this.elements.temperatureValue) {
                this.elements.temperatureValue.textContent = value.toFixed(1);
            }
        });

        // Max tokens slider
        this.elements.maxTokensSlider?.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.currentSettings.maxTokens = value;
            if (this.elements.maxTokensValue) {
                this.elements.maxTokensValue.textContent = value;
            }
        });

        // Interface toggles
        this.elements.darkMode?.addEventListener('change', (e) => {
            this.currentSettings.darkMode = e.target.checked;
        });

        this.elements.autoScroll?.addEventListener('change', (e) => {
            this.currentSettings.autoScroll = e.target.checked;
        });

        this.elements.soundEffects?.addEventListener('change', (e) => {
            this.currentSettings.soundEffects = e.target.checked;
        });

        this.elements.messageStyle?.addEventListener('change', (e) => {
            this.currentSettings.messageStyle = e.target.value;
        });

        // Network settings
        this.elements.backendUrl?.addEventListener('change', (e) => {
            this.currentSettings.backendUrl = e.target.value;
        });

        this.elements.timeoutSlider?.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.currentSettings.requestTimeout = value;
            if (this.elements.timeoutValue) {
                this.elements.timeoutValue.textContent = value;
            }
        });

        // Action buttons
        this.elements.saveButton?.addEventListener('click', () => this.saveSettings());
        this.elements.resetButton?.addEventListener('click', () => this.resetSettings());
        this.elements.exportButton?.addEventListener('click', () => this.exportSettings());
        this.elements.testConnectionButton?.addEventListener('click', () => this.testConnection());
    }

    updateModelSpecificSettings() {
        // Hide all provider-specific settings first
        const providerSettings = [
            'groq-settings',
            'openai-settings', 
            'claude-settings',
            'openrouter-settings',
            'gemini-settings'
        ];
        
        providerSettings.forEach(settingsId => {
            const element = document.getElementById(settingsId);
            if (element) {
                element.style.display = 'none';
            }
        });
        
        // Show the current provider's settings
        const currentProviderSettings = document.getElementById(`${this.currentSettings.modelProvider}-settings`);
        if (currentProviderSettings) {
            currentProviderSettings.style.display = 'block';
        }
        
        // Set up event listeners for model-specific dropdowns
        this.setupModelSpecificListeners();
    }
    
    setupModelSpecificListeners() {
        // OpenAI model change
        const openaiModel = document.getElementById('openai-model');
        if (openaiModel) {
            openaiModel.addEventListener('change', (e) => {
                this.currentSettings.openaiModel = e.target.value;
            });
        }
        
        // Claude model change  
        const claudeModel = document.getElementById('claude-model');
        if (claudeModel) {
            claudeModel.addEventListener('change', (e) => {
                this.currentSettings.claudeModel = e.target.value;
            });
        }
        
        // OpenRouter model change
        const openrouterModel = document.getElementById('openrouter-model');
        if (openrouterModel) {
            openrouterModel.addEventListener('change', (e) => {
                this.currentSettings.openrouterModel = e.target.value;
            });
        }
        
        // Gemini model change
        const geminiModel = document.getElementById('gemini-model');
        if (geminiModel) {
            geminiModel.addEventListener('change', (e) => {
                this.currentSettings.geminiModel = e.target.value;
            });
        }
    }

    async loadSettings() {
        try {
            // Try to load from backend first
            const response = await fetch(`${this.config.backendUrl}${this.config.endpoints.settings}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                signal: AbortSignal.timeout(this.config.requestTimeout)
            });

            if (response.ok) {
                const backendSettings = await response.json();
                this.currentSettings = { ...this.defaultSettings, ...backendSettings };
                console.log('✅ Settings loaded from backend');
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.warn('Failed to load from backend, trying localStorage:', error.message);
            
            // Fallback to localStorage
            try {
                const saved = localStorage.getItem('settings');
                if (saved) {
                    const localSettings = JSON.parse(saved);
                    this.currentSettings = { ...this.defaultSettings, ...localSettings };
                    console.log('✅ Settings loaded from localStorage');
                } else {
                    console.log('📝 Using default settings');
                }
            } catch (localError) {
                console.warn('Failed to load from localStorage:', localError);
                console.log('📝 Using default settings');
            }
        }
    }

    updateUI() {
        // Model settings
        if (this.elements.modelProvider) {
            this.elements.modelProvider.value = this.currentSettings.modelProvider;
        }
        
        if (this.elements.groqModel) {
            this.elements.groqModel.value = this.currentSettings.groqModel;
        }
        
        if (this.elements.temperatureSlider) {
            this.elements.temperatureSlider.value = this.currentSettings.temperature;
        }
        
        if (this.elements.temperatureValue) {
            this.elements.temperatureValue.textContent = this.currentSettings.temperature.toFixed(1);
        }
        
        if (this.elements.maxTokensSlider) {
            this.elements.maxTokensSlider.value = this.currentSettings.maxTokens;
        }
        
        if (this.elements.maxTokensValue) {
            this.elements.maxTokensValue.textContent = this.currentSettings.maxTokens;
        }

        // Interface settings
        if (this.elements.darkMode) {
            this.elements.darkMode.checked = this.currentSettings.darkMode;
        }
        
        if (this.elements.autoScroll) {
            this.elements.autoScroll.checked = this.currentSettings.autoScroll;
        }
        
        if (this.elements.soundEffects) {
            this.elements.soundEffects.checked = this.currentSettings.soundEffects;
        }
        
        if (this.elements.messageStyle) {
            this.elements.messageStyle.value = this.currentSettings.messageStyle;
        }

        // Network settings
        if (this.elements.backendUrl) {
            this.elements.backendUrl.value = this.currentSettings.backendUrl;
        }
        
        if (this.elements.timeoutSlider) {
            this.elements.timeoutSlider.value = this.currentSettings.requestTimeout;
        }
        
        if (this.elements.timeoutValue) {
            this.elements.timeoutValue.textContent = this.currentSettings.requestTimeout;
        }

        // Update model-specific settings visibility
        this.updateModelSpecificSettings();
        
        // Update last updated time
        if (this.elements.lastUpdated) {
            this.elements.lastUpdated.textContent = new Date().toLocaleTimeString();
        }
    }

    async saveSettings() {
        try {
            console.log('💾 Saving settings...', this.currentSettings);
            
            // Show loading state
            this.setButtonLoading(this.elements.saveButton, true);

            // Try to save to backend first
            try {
                const response = await fetch(`${this.config.backendUrl}${this.config.endpoints.settings}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.currentSettings),
                    signal: AbortSignal.timeout(this.config.requestTimeout)
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                console.log('✅ Settings saved to backend');
            } catch (backendError) {
                console.warn('Failed to save to backend:', backendError.message);
            }

            // Always save to localStorage as backup
            localStorage.setItem('settings', JSON.stringify(this.currentSettings));
            console.log('✅ Settings saved to localStorage');

            // Show success
            this.showSuccess('Settings saved successfully!');
            
            // Update UI
            this.updateUI();
            
        } catch (error) {
            console.error('❌ Failed to save settings:', error);
            this.showError('Failed to save settings');
        } finally {
            this.setButtonLoading(this.elements.saveButton, false);
        }
    }

    async resetSettings() {
        if (confirm('Are you sure you want to reset all settings to defaults?')) {
            try {
                this.currentSettings = { ...this.defaultSettings };
                this.updateUI();
                
                // Clear localStorage
                localStorage.removeItem('settings');
                
                // Try to reset on backend too
                try {
                    await fetch(`${this.config.backendUrl}${this.config.endpoints.settings}`, {
                        method: 'DELETE',
                        signal: AbortSignal.timeout(this.config.requestTimeout)
                    });
                } catch (backendError) {
                    console.warn('Failed to reset on backend:', backendError.message);
                }
                
                this.showSuccess('Settings reset to defaults');
                console.log('✅ Settings reset to defaults');
            } catch (error) {
                console.error('❌ Failed to reset settings:', error);
                this.showError('Failed to reset settings');
            }
        }
    }

    exportSettings() {
        try {
            const exportData = {
                settings: this.currentSettings,
                exportedAt: new Date().toISOString(),
                version: '1.0.0'
            };

            const blob = new Blob([JSON.stringify(exportData, null, 2)], {
                type: 'application/json'
            });

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ai-assistant-settings-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            this.showSuccess('Settings exported successfully');
            console.log('✅ Settings exported');
        } catch (error) {
            console.error('❌ Failed to export settings:', error);
            this.showError('Failed to export settings');
        }
    }

    async testConnection() {
        try {
            console.log('🔗 Testing backend connection...');
            
            // Show testing state
            this.updateConnectionStatus('testing', 'Testing connection...');
            this.setButtonLoading(this.elements.testConnectionButton, true);

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000);

            const response = await fetch(`${this.currentSettings.backendUrl}${this.config.endpoints.status}`, {
                method: 'GET',
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                const data = await response.json();
                this.updateConnectionStatus('connected', 'Connected successfully');
                this.updateBackendStatus('Online');
                this.updateCurrentModel(data.model || 'Unknown');
                console.log('✅ Backend connection successful', data);
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.warn('❌ Backend connection failed:', error.message);
            this.updateConnectionStatus('error', `Connection failed: ${error.message}`);
            this.updateBackendStatus('Offline');
        } finally {
            this.setButtonLoading(this.elements.testConnectionButton, false);
        }
    }

    updateConnectionStatus(status, text) {
        const indicator = this.elements.connectionIndicator;
        const textEl = this.elements.connectionText;

        if (indicator) {
            indicator.className = 'w-3 h-3 rounded-full ' + {
                'connected': 'bg-green-500',
                'error': 'bg-red-500',
                'testing': 'bg-yellow-400 animate-pulse'
            }[status];
        }

        if (textEl) {
            textEl.textContent = text;
        }
    }

    updateBackendStatus(status) {
        const statusEl = this.elements.backendStatus;
        if (statusEl) {
            statusEl.textContent = status;
            statusEl.className = 'font-medium ' + {
                'Online': 'text-green-600',
                'Offline': 'text-red-600',
                'Connecting...': 'text-yellow-600'
            }[status] || 'text-gray-600';
        }
    }

    updateCurrentModel(model) {
        const modelEl = this.elements.currentModel;
        if (modelEl) {
            modelEl.textContent = model;
        }
    }

    setButtonLoading(button, loading) {
        if (!button) return;

        if (loading) {
            button.disabled = true;
            button.classList.add('opacity-50');
            const originalText = button.textContent;
            button.dataset.originalText = originalText;
            button.innerHTML = '<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>';
        } else {
            button.disabled = false;
            button.classList.remove('opacity-50');
            button.textContent = button.dataset.originalText || 'Save Settings';
        }
    }

    showSuccess(message) {
        const toast = this.elements.successToast;
        if (toast) {
            const messageSpan = toast.querySelector('span');
            if (messageSpan) {
                messageSpan.textContent = message;
            }
            
            toast.classList.remove('hidden');
            
            setTimeout(() => {
                toast.classList.add('hidden');
            }, 3000);
        }
        
        console.log('✅', message);
    }

    showError(message) {
        // Create error toast if it doesn't exist
        let errorToast = document.getElementById('error-toast');
        if (!errorToast) {
            errorToast = document.createElement('div');
            errorToast.id = 'error-toast';
            errorToast.className = 'hidden fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-xl shadow-lg z-50';
            errorToast.innerHTML = `
                <div class="flex items-center space-x-2">
                    <i data-lucide="alert-circle" class="w-5 h-5"></i>
                    <span>${message}</span>
                </div>
            `;
            document.body.appendChild(errorToast);
            
            // Re-initialize Lucide icons
            if (window.lucide) {
                lucide.createIcons();
            }
        } else {
            const messageSpan = errorToast.querySelector('span');
            if (messageSpan) {
                messageSpan.textContent = message;
            }
        }
        
        errorToast.classList.remove('hidden');
        
        setTimeout(() => {
            errorToast.classList.add('hidden');
        }, 5000);
        
        console.error('❌', message);
    }

    // Public methods for external access
    getSettings() {
        return { ...this.currentSettings };
    }

    updateSetting(key, value) {
        this.currentSettings[key] = value;
        this.updateUI();
    }
}

// Initialize settings when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 DOM loaded, initializing settings interface...');
    window.settingsInterface = new SettingsInterface();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SettingsInterface;
}
