/**
 * Modern Settings Interface for AI Network Assistant
 * Tesla-inspired design with clean, professional UX
 */

class ModernSettingsInterface {
    constructor() {
        this.backendPort = 8002;
        this.settings = {
            chatProvider: 'groq',
            configProvider: 'groq',
            temperature: 0.7,
            maxTokens: 2000,
            responseTimeout: 120,
            autoSave: true,
            codeHighlighting: true,
            debugMode: false
        };
        
        this.initializeElements();
        this.setupEventListeners();
        this.loadCurrentSettings();
        this.testConnection();
    }

    initializeElements() {
        // Provider selection
        this.providerOptions = document.querySelectorAll('.provider-option');
        
        // Sliders
        this.temperatureSlider = document.getElementById('temperature');
        this.maxTokensSlider = document.getElementById('max-tokens');
        this.timeoutSlider = document.getElementById('response-timeout');
        
        // Value displays
        this.tempValue = document.getElementById('temp-value');
        this.tokensValue = document.getElementById('tokens-value');
        this.timeoutValue = document.getElementById('timeout-value');
        
        // Toggles
        this.autoSaveToggle = document.getElementById('auto-save');
        this.codeHighlightingToggle = document.getElementById('code-highlighting');
        this.debugModeToggle = document.getElementById('debug-mode');
        
        // Buttons
        this.saveButton = document.getElementById('save-settings');
        
        // Status
        this.connectionStatus = document.getElementById('connection-status');
        this.loadingOverlay = document.getElementById('loading-overlay');
    }

    setupEventListeners() {
        // Provider selection
        this.providerOptions.forEach(option => {
            option.addEventListener('click', () => {
                const provider = option.dataset.provider;
                const type = option.dataset.type;
                this.selectProvider(provider, type);
            });
        });

        // Sliders
        this.temperatureSlider.addEventListener('input', (e) => {
            this.settings.temperature = parseFloat(e.target.value);
            this.tempValue.textContent = e.target.value;
        });

        this.maxTokensSlider.addEventListener('input', (e) => {
            this.settings.maxTokens = parseInt(e.target.value);
            this.tokensValue.textContent = e.target.value;
        });

        this.timeoutSlider.addEventListener('input', (e) => {
            this.settings.responseTimeout = parseInt(e.target.value);
            this.timeoutValue.textContent = e.target.value + 's';
        });

        // Toggles
        this.autoSaveToggle.addEventListener('change', (e) => {
            this.settings.autoSave = e.target.checked;
        });

        this.codeHighlightingToggle.addEventListener('change', (e) => {
            this.settings.codeHighlighting = e.target.checked;
        });

        this.debugModeToggle.addEventListener('change', (e) => {
            this.settings.debugMode = e.target.checked;
        });

        // Save button
        this.saveButton.addEventListener('click', () => {
            this.saveSettings();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveSettings();
            }
        });
    }

    async testConnection() {
        try {
            const response = await fetch(`http://localhost:${this.backendPort}/health`);
            if (response.ok) {
                this.updateConnectionStatus(true, 'Connected');
            } else {
                throw new Error('Backend not responding');
            }
        } catch (error) {
            console.error('Connection test failed:', error);
            this.updateConnectionStatus(false, 'Disconnected');
        }
    }

    async loadCurrentSettings() {
        try {
            console.log('🔄 Loading current settings from backend...');
            
            const response = await fetch(`http://localhost:${this.backendPort}/api/v1/settings/core`);
            
            if (response.ok) {
                const backendSettings = await response.json();
                console.log('✅ Backend settings loaded:', backendSettings);
                
                // Map backend settings to UI
                if (backendSettings.default_chat_provider) {
                    this.settings.chatProvider = backendSettings.default_chat_provider;
                    this.selectProvider(this.settings.chatProvider, 'chat');
                }
                
                if (backendSettings.default_config_generation_provider) {
                    this.settings.configProvider = backendSettings.default_config_generation_provider;
                    this.selectProvider(this.settings.configProvider, 'config');
                } else if (backendSettings.default_config_provider) {
                    this.settings.configProvider = backendSettings.default_config_provider;
                    this.selectProvider(this.settings.configProvider, 'config');
                }

                if (backendSettings.response_timeout) {
                    this.settings.responseTimeout = backendSettings.response_timeout;
                    this.timeoutSlider.value = this.settings.responseTimeout;
                    this.timeoutValue.textContent = this.settings.responseTimeout + 's';
                }
                
                this.showToast('Settings loaded successfully', 'success');
            } else {
                console.warn('⚠️ Failed to load settings from backend, using defaults');
                this.applyDefaultSettings();
            }
        } catch (error) {
            console.error('❌ Error loading settings:', error);
            this.applyDefaultSettings();
            this.showToast('Using default settings', 'info');
        }
    }

    applyDefaultSettings() {
        // Apply default UI state
        this.selectProvider('groq', 'chat');
        this.selectProvider('groq', 'config');
        
        this.temperatureSlider.value = this.settings.temperature;
        this.tempValue.textContent = this.settings.temperature;
        
        this.maxTokensSlider.value = this.settings.maxTokens;
        this.tokensValue.textContent = this.settings.maxTokens;
        
        this.timeoutSlider.value = this.settings.responseTimeout;
        this.timeoutValue.textContent = this.settings.responseTimeout + 's';
        
        this.autoSaveToggle.checked = this.settings.autoSave;
        this.codeHighlightingToggle.checked = this.settings.codeHighlighting;
        this.debugModeToggle.checked = this.settings.debugMode;
    }

    selectProvider(provider, type) {
        // Update internal settings
        if (type === 'chat') {
            this.settings.chatProvider = provider;
        } else if (type === 'config') {
            this.settings.configProvider = provider;
        }

        // Update UI
        const typeOptions = document.querySelectorAll(`[data-type="${type}"]`);
        typeOptions.forEach(option => {
            const radio = option.querySelector('.provider-radio');
            const isSelected = option.dataset.provider === provider;
            
            if (isSelected) {
                option.classList.add('border-tesla-red', 'bg-red-50');
                option.classList.remove('border-gray-200');
                radio.classList.add('bg-tesla-red', 'border-tesla-red');
                radio.classList.remove('border-gray-300');
                
                // Add checkmark
                radio.innerHTML = '<div class="w-2 h-2 bg-white rounded-full mx-auto mt-0.5"></div>';
            } else {
                option.classList.remove('border-tesla-red', 'bg-red-50');
                option.classList.add('border-gray-200');
                radio.classList.remove('bg-tesla-red', 'border-tesla-red');
                radio.classList.add('border-gray-300');
                radio.innerHTML = '';
            }
        });

        console.log(`Selected ${provider} for ${type}`);
    }

    async saveSettings() {
        this.showLoading(true);
        
        try {
            console.log('💾 Saving settings:', this.settings);

            // Prepare settings for backend
            const settingsPayload = {
                default_chat_provider: this.settings.chatProvider,
                default_config_provider: this.settings.configProvider,
                default_config_generation_provider: this.settings.configProvider,
                default_analysis_provider: this.settings.configProvider === 'groq' ? 'openrouter' : 'groq',
                response_timeout: this.settings.responseTimeout,
                temperature: this.settings.temperature,
                max_tokens: this.settings.maxTokens,
                auto_save: this.settings.autoSave,
                code_highlighting: this.settings.codeHighlighting,
                debug_mode: this.settings.debugMode,
                concurrent_requests: 5,
                cache_enabled: true,
                cache_duration: 3600,
                cache_size_limit: 1024,
                max_devices_per_operation: 10,
                require_approval_threshold: "10+ devices",
                safety_validation_level: "Standard",
                log_all_operations: true
            };

            // Update core settings
            const response = await fetch(`http://localhost:${this.backendPort}/api/v1/genai-settings/core`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settingsPayload)
            });

            if (response.ok) {
                console.log('✅ Settings saved successfully');
                this.showToast('Settings saved successfully!', 'success');
                
                // Update save button state
                this.saveButton.innerHTML = '<i data-lucide="check" class="w-4 h-4 inline mr-2"></i>Saved';
                this.saveButton.classList.remove('bg-green-600', 'hover:bg-green-700');
                this.saveButton.classList.add('bg-green-500');
                
                // Reset button after 2 seconds
                setTimeout(() => {
                    this.saveButton.innerHTML = '<i data-lucide="save" class="w-4 h-4 inline mr-2"></i>Save';
                    this.saveButton.classList.remove('bg-green-500');
                    this.saveButton.classList.add('bg-green-600', 'hover:bg-green-700');
                    lucide.createIcons();
                }, 2000);
                
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Error saving settings:', error);
            this.showToast(`Error saving settings: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    updateConnectionStatus(connected, message) {
        const statusElement = this.connectionStatus;
        const statusDot = statusElement.querySelector('div');
        const statusText = statusElement.querySelector('span');
        
        if (connected) {
            statusDot.className = 'w-3 h-3 bg-green-500 rounded-full animate-pulse';
            statusText.textContent = 'Connected';
            statusElement.className = 'flex items-center space-x-2 text-green-600';
        } else {
            statusDot.className = 'w-3 h-3 bg-red-500 rounded-full';
            statusText.textContent = 'Disconnected';
            statusElement.className = 'flex items-center space-x-2 text-red-600';
        }
    }

    showLoading(show) {
        if (show) {
            this.loadingOverlay.classList.remove('hidden');
        } else {
            this.loadingOverlay.classList.add('hidden');
        }
    }

    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(toastContainer);
        }

        const toast = document.createElement('div');
        const bgColor = type === 'success' ? 'bg-green-500' : 
                       type === 'error' ? 'bg-red-500' : 
                       type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500';
        
        toast.className = `${bgColor} text-white px-6 py-4 rounded-xl shadow-lg transform transition-all duration-300 translate-x-full flex items-center space-x-3`;
        
        const iconName = type === 'success' ? 'check-circle' : 
                        type === 'error' ? 'x-circle' : 
                        type === 'warning' ? 'alert-circle' : 'info';
        
        toast.innerHTML = `
            <i data-lucide="${iconName}" class="w-5 h-5"></i>
            <span class="font-medium">${message}</span>
        `;

        toastContainer.appendChild(toast);
        
        // Initialize icons
        lucide.createIcons();

        // Slide in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);

        // Remove after 4 seconds
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 4000);
    }

    // Test specific provider functionality
    async testProvider(provider) {
        try {
            const testMessage = "Hello, this is a test message.";
            
            const response = await fetch(`http://localhost:${this.backendPort}/api/v1/chat/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: testMessage,
                    session_id: `test_${Date.now()}`,
                    provider: provider
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.showToast(`${provider} provider test successful`, 'success');
                return true;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error(`Provider test failed for ${provider}:`, error);
            this.showToast(`${provider} provider test failed: ${error.message}`, 'error');
            return false;
        }
    }

    // Export settings
    exportSettings() {
        const settingsBlob = new Blob([JSON.stringify(this.settings, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(settingsBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ai-settings.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showToast('Settings exported successfully', 'success');
    }

    // Import settings
    importSettings(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const importedSettings = JSON.parse(e.target.result);
                
                // Validate and apply imported settings
                Object.keys(importedSettings).forEach(key => {
                    if (this.settings.hasOwnProperty(key)) {
                        this.settings[key] = importedSettings[key];
                    }
                });
                
                this.applySettingsToUI();
                this.showToast('Settings imported successfully', 'success');
            } catch (error) {
                this.showToast('Error importing settings file', 'error');
            }
        };
        
        reader.readAsText(file);
    }

    applySettingsToUI() {
        // Apply all settings to the UI elements
        this.selectProvider(this.settings.chatProvider, 'chat');
        this.selectProvider(this.settings.configProvider, 'config');
        
        this.temperatureSlider.value = this.settings.temperature;
        this.tempValue.textContent = this.settings.temperature;
        
        this.maxTokensSlider.value = this.settings.maxTokens;
        this.tokensValue.textContent = this.settings.maxTokens;
        
        this.timeoutSlider.value = this.settings.responseTimeout;
        this.timeoutValue.textContent = this.settings.responseTimeout + 's';
        
        this.autoSaveToggle.checked = this.settings.autoSave;
        this.codeHighlightingToggle.checked = this.settings.codeHighlighting;
        this.debugModeToggle.checked = this.settings.debugMode;
    }
}

// Initialize settings interface when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Loading Modern Settings Interface...');
    window.settingsInterface = new ModernSettingsInterface();
});

// Global functions for settings management
function testAllProviders() {
    if (window.settingsInterface) {
        ['groq', 'openrouter', 'openai', 'anthropic'].forEach(provider => {
            window.settingsInterface.testProvider(provider);
        });
    }
}

function exportSettings() {
    if (window.settingsInterface) {
        window.settingsInterface.exportSettings();
    }
}

function resetToDefaults() {
    if (window.settingsInterface && confirm('Are you sure you want to reset all settings to defaults?')) {
        window.settingsInterface.settings = {
            chatProvider: 'groq',
            configProvider: 'groq',
            temperature: 0.7,
            maxTokens: 2000,
            responseTimeout: 120,
            autoSave: true,
            codeHighlighting: true,
            debugMode: false
        };
        window.settingsInterface.applySettingsToUI();
        window.settingsInterface.showToast('Settings reset to defaults', 'info');
    }
}
