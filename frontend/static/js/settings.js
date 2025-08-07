document.addEventListener('DOMContentLoaded', function () {
    const settingsForm = document.getElementById('genai-settings-form');

    // Fetch and display the current settings
    async function loadSettings() {
        try {
            // Load each settings section separately using the v1 API endpoints
            const settingsSections = {
                core: await apiCall('/api/v1/genai-settings/genai/core'),
                llm: await apiCall('/api/v1/genai-settings/genai/llm'),
                rag: await apiCall('/api/v1/genai-settings/genai/rag'),
                agentic: await apiCall('/api/v1/genai-settings/genai/agentic'),
                embeddings: await apiCall('/api/v1/genai-settings/genai/embeddings'),
                api_keys: await apiCall('/api/v1/genai-settings/genai/api-keys')
            };
            
            console.log('Loaded settings:', settingsSections);
            
            // Populate the form with the current settings
            for (const section in settingsSections) {
                const sectionData = settingsSections[section];
                if (sectionData) {
                    for (const key in sectionData) {
                        const input = document.querySelector(`[name="${section}.${key}"]`);
                        if (input) {
                            if (input.type === 'checkbox') {
                                input.checked = sectionData[key];
                            } else {
                                input.value = sectionData[key];
                            }
                        }
                    }
                }
            }
            
            // Handle API keys specially
            if (settingsSections.api_keys && settingsSections.api_keys.keys) {
                displayApiKeys(settingsSections.api_keys.keys);
            }
            
            showToast('Settings loaded successfully', 'success');
        } catch (error) {
            console.error('Error loading settings:', error);
            showToast('Error loading settings', 'error');
        }
    }

    // Save the updated settings
    settingsForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const formData = new FormData(settingsForm);
        const settings = {};

        for (const [key, value] of formData.entries()) {
            if (key.startsWith('api_keys')) {
                if (!settings.api_keys) {
                    settings.api_keys = {keys: []};
                }
                const match = key.match(/api_keys\[(\d+)\]\[(\w+)\]/);
                if (match) {
                    const [, index, field] = match;
                    if (!settings.api_keys.keys[index]) {
                        settings.api_keys.keys[index] = {};
                    }
                    settings.api_keys.keys[index][field] = value;
                }
            } else {
                const [section, field] = key.split('.');
                if (!settings[section]) {
                    settings[section] = {};
                }
                settings[section][field] = value;
            }
        }

        try {
            // Save each section separately using the correct API endpoints
            const savePromises = [];
            
            if (settings.core) {
                savePromises.push(apiCall('/api/v1/genai-settings/genai/core', {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(settings.core)
                }));
            }
            
            if (settings.llm) {
                savePromises.push(apiCall('/api/v1/genai-settings/genai/llm', {
                    method: 'PUT', 
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(settings.llm)
                }));
            }
            
            if (settings.rag) {
                savePromises.push(apiCall('/api/v1/genai-settings/genai/rag', {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(settings.rag)
                }));
            }
            
            if (settings.agentic) {
                savePromises.push(apiCall('/api/v1/genai-settings/genai/agentic', {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(settings.agentic)
                }));
            }
            
            if (settings.embeddings) {
                savePromises.push(apiCall('/api/v1/genai-settings/genai/embeddings', {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(settings.embeddings)
                }));
            }
            
            // Wait for all save operations to complete
            await Promise.all(savePromises);
            
            showToast('Settings saved successfully', 'success');
            
            // Reload the chat page model display if it exists
            if (window.parent && window.parent.loadCurrentModel) {
                window.parent.loadCurrentModel();
            }
            
        } catch (error) {
            console.error('Error saving settings:', error);
            showToast('Error saving settings', 'error');
        }
    });

    // Function to display API keys
    function displayApiKeys(keys) {
        const apiKeysContainer = document.getElementById('api-keys-container');
        if (!apiKeysContainer) return;
        
        apiKeysContainer.innerHTML = '';
        
        keys.forEach((keyData, index) => {
            const keyElement = document.createElement('div');
            keyElement.className = 'api-key-item mb-3 p-3 border rounded';
            keyElement.innerHTML = `
                <div class="row">
                    <div class="col-md-3">
                        <label class="form-label">Service</label>
                        <input type="text" class="form-control" name="api_keys[${index}][service]" value="${keyData.service || ''}" readonly>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Name</label>
                        <input type="text" class="form-control" name="api_keys[${index}][name]" value="${keyData.name || ''}" readonly>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">API Key</label>
                        <input type="password" class="form-control" name="api_keys[${index}][key]" value="${keyData.key || ''}" readonly>
                    </div>
                    <div class="col-md-2 d-flex align-items-end">
                        <button type="button" class="btn btn-danger" onclick="removeApiKey(${keyData.id})">
                            <i data-lucide="trash-2"></i>
                        </button>
                    </div>
                </div>
            `;
            apiKeysContainer.appendChild(keyElement);
        });
    }
    
    // Function to add new API key
    window.addApiKey = function() {
        const service = document.getElementById('new-api-service').value;
        const name = document.getElementById('new-api-name').value;
        const key = document.getElementById('new-api-key').value;
        
        if (!service || !name || !key) {
            showToast('Please fill in all API key fields', 'error');
            return;
        }
        
        apiCall('/api/v1/genai-settings/genai/api-keys', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ service, name, key })
        }).then(() => {
            showToast('API key added successfully', 'success');
            document.getElementById('new-api-service').value = '';
            document.getElementById('new-api-name').value = '';
            document.getElementById('new-api-key').value = '';
            loadSettings(); // Reload to show the new key
        }).catch(error => {
            console.error('Error adding API key:', error);
            showToast('Error adding API key', 'error');
        });
    };
    
    // Function to remove API key
    window.removeApiKey = function(keyId) {
        if (!confirm('Are you sure you want to remove this API key?')) return;
        
        apiCall(`/api/v1/genai-settings/genai/api-keys/${keyId}`, {
            method: 'DELETE'
        }).then(() => {
            showToast('API key removed successfully', 'success');
            loadSettings(); // Reload to update the display
        }).catch(error => {
            console.error('Error removing API key:', error);
            showToast('Error removing API key', 'error');
        });
    };
    
    // Function to test API connection
    window.testApiConnection = function() {
        const service = document.getElementById('new-api-service').value;
        const key = document.getElementById('new-api-key').value;
        
        if (!service || !key) {
            showToast('Please select service and enter API key', 'error');
            return;
        }
        
        apiCall('/api/v1/genai-settings/genai/test-connection', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ provider: service, api_key: key })
        }).then(result => {
            if (result.status === 'success') {
                showToast('API connection successful!', 'success');
            } else {
                showToast(`API connection failed: ${result.message}`, 'error');
            }
        }).catch(error => {
            console.error('Error testing API connection:', error);
            showToast('Error testing API connection', 'error');
        });
    };

    loadSettings();
});

