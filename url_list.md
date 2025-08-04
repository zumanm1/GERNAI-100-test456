# Network Automation Application - Complete URL List

## Backend API (Port 5000)

### Main Application Routes
- GET `/` - Dashboard page
- GET `/login` - Login page
- GET `/devices` - Devices page
- GET `/automation` - Automation page
- GET `/operations` - Operations page
- GET `/settings` - Settings page
- GET `/chat` - Chat page
- GET `/genai-settings` - GenAI settings page
- GET `/health` - Health check endpoint
- WebSocket `/ws/operations` - Operations WebSocket

### API Endpoints (under `/api` prefix)

#### Authentication (`/api/v1/auth`)
- POST `/api/v1/auth/login` - User login
- POST `/api/v1/auth/register` - User registration
- GET `/api/v1/auth/verify` - Token verification
- GET `/api/v1/auth/me` - Current user info

#### Dashboard (`/api/v1/dashboard`)
- GET `/api/v1/dashboard/stats` - Dashboard statistics
- GET `/api/v1/dashboard/device-status-chart` - Device status chart data
- GET `/api/v1/dashboard/operations-timeline` - Operations timeline data
- GET `/api/v1/dashboard/recent-operations` - Recent operations
- POST `/api/v1/dashboard/quick-actions/{action}` - Execute quick actions

#### Devices (`/api/v1/devices`)
- GET `/api/v1/devices/` - Get all devices
- POST `/api/v1/devices/` - Create new device
- GET `/api/v1/devices/{device_id}` - Get device by ID
- PUT `/api/v1/devices/{device_id}` - Update device
- DELETE `/api/v1/devices/{device_id}` - Delete device
- POST `/api/v1/devices/{device_id}/test-connectivity` - Test device connectivity
- POST `/api/v1/devices/{device_id}/backup-config` - Backup device config
- GET `/api/v1/devices/{device_id}/config` - Get device config
- GET `/api/v1/devices/{device_id}/operations` - Get device operations

#### Operations (`/api/v1/operations`)
- GET `/api/v1/operations/` - Get operations
- POST `/api/v1/operations/` - Create operation
- GET `/api/v1/operations/{operation_id}` - Get operation by ID
- DELETE `/api/v1/operations/{operation_id}` - Delete operation
- GET `/api/v1/operations/statistics/summary` - Operation statistics
- POST `/api/v1/operations/audit/start` - Start audit
- GET `/api/v1/operations/audit/{audit_id}/status` - Audit status
- GET `/api/v1/operations/audit/{audit_id}/results` - Audit results
- POST `/api/v1/operations/troubleshoot/start` - Start troubleshooting
- POST `/api/v1/operations/baseline/create` - Create baseline
- GET `/api/v1/operations/baseline/{baseline_id}` - Get baseline
- POST `/api/v1/operations/execute/command` - Execute command
- WebSocket `/api/v1/operations/ws/{operation_id}` - Operation WebSocket

#### GenAI Settings (`/api/v1/genai-settings`)
- GET `/api/v1/genai-settings/genai/llm` - Get LLM settings
- PUT `/api/v1/genai-settings/genai/llm` - Update LLM settings
- GET `/api/v1/genai-settings/genai/rag` - Get RAG settings
- PUT `/api/v1/genai-settings/genai/rag` - Update RAG settings
- GET `/api/v1/genai-settings/genai/agentic` - Get agentic settings
- PUT `/api/v1/genai-settings/genai/agentic` - Update agentic settings
- GET `/api/v1/genai-settings/genai/graph-rag` - Get Graph RAG settings
- PUT `/api/v1/genai-settings/genai/graph-rag` - Update Graph RAG settings
- GET `/api/v1/genai-settings/genai/embeddings` - Get embeddings settings
- PUT `/api/v1/genai-settings/genai/embeddings` - Update embeddings settings
- GET `/api/v1/genai-settings/genai/core` - Get core settings
- PUT `/api/v1/genai-settings/genai/core` - Update core settings
- GET `/api/v1/genai-settings/api-keys` - Get API keys
- POST `/api/v1/genai-settings/api-keys` - Add API key
- PUT `/api/v1/genai-settings/api-keys/{key_id}` - Update API key
- DELETE `/api/v1/genai-settings/api-keys/{key_id}` - Delete API key
- POST `/api/v1/genai-settings/api-keys/{key_id}/test` - Test API key

#### Settings (`/api/v1/settings`)
- GET `/api/v1/settings/` - Get settings
- PUT `/api/v1/settings/` - Update settings
- GET `/api/v1/settings/network` - Get network settings
- PUT `/api/v1/settings/network` - Update network settings
- GET `/api/v1/settings/backup` - Get backup settings
- PUT `/api/v1/settings/backup` - Update backup settings
- POST `/api/v1/settings/test-connection` - Test connection

#### Chat (`/api/v1/chat`)
- GET `/api/v1/chat/conversations` - Get conversations
- POST `/api/v1/chat/conversations` - Create conversation
- GET `/api/v1/chat/conversations/{conversation_id}` - Get conversation
- DELETE `/api/v1/chat/conversations/{conversation_id}` - Delete conversation
- POST `/api/v1/chat/conversations/{conversation_id}/messages` - Send message
- GET `/api/v1/chat/conversations/{conversation_id}/messages` - Get messages
- WebSocket `/api/v1/chat/ws/{conversation_id}` - Chat WebSocket

#### Automation (`/api/v1/automation`)
- GET `/api/v1/automation/playbooks` - Get playbooks
- POST `/api/v1/automation/playbooks` - Create playbook
- GET `/api/v1/automation/playbooks/{playbook_id}` - Get playbook
- PUT `/api/v1/automation/playbooks/{playbook_id}` - Update playbook
- DELETE `/api/v1/automation/playbooks/{playbook_id}` - Delete playbook
- POST `/api/v1/automation/playbooks/{playbook_id}/execute` - Execute playbook
- GET `/api/v1/automation/executions` - Get executions
- GET `/api/v1/automation/executions/{execution_id}` - Get execution
- POST `/api/v1/automation/executions/{execution_id}/cancel` - Cancel execution

#### Users (`/api/v1/users`)
- GET `/api/v1/users/` - Get users

#### Actions (`/api/v1/actions`)
- GET `/api/v1/actions/` - List actions
- POST `/api/v1/actions/` - Create action
- GET `/api/v1/actions/{action_id}` - Get action

#### GenAI (`/api/v1/genai`)
- GET `/api/v1/genai/` - GenAI endpoint

#### Compatibility Routes
- All operations routes also available under `/api/operations` prefix

#### Additional API Routes
- GET `/api/stats` - Dashboard stats (frontend compatibility)
- GET `/api/device-status-chart` - Device status chart
- GET `/api/operations-timeline` - Operations timeline
- GET `/api/network-operations/status` - Network operations status
- GET `/api/chat/status` - Chat service status

## Frontend Server (Port 8001)

### Frontend Routes
- GET `/` - Login page (redirects to login.html)
- GET `/devices` - Devices page
- GET `/genai` - GenAI settings page
- GET `/dashboard` - Dashboard page
- GET `/automation` - Automation page
- GET `/device-management` - Device management page
- GET `/chat` - Chat page
- GET `/operations` - Operations page
- GET `/settings` - Settings page
- WebSocket `/ws` - Frontend WebSocket

### Static Files
- `/static/*` - Static files (CSS, JS, images)

## WebSocket Endpoints
- `ws://localhost:5000/ws/operations` - Operations WebSocket
- `ws://localhost:8001/ws` - Frontend WebSocket
- Various API WebSocket endpoints for real-time features
