# Installation Guide

## Project Overview

This is a comprehensive **Network Automation Application** built with modern technologies:

- **Python 3.11** - Core programming language
- **FastAPI** - High-performance web framework for building APIs
- **PostgreSQL** - Relational database for data persistence
- **AI/ML Integration** - Multiple LLM providers (OpenAI, Groq, OpenRouter)
- **Network Automation** - Cisco device management using Netmiko and PyATS/Genie
- **Real-time Communication** - WebSocket support for live updates

The application provides a complete solution for network device management, automation tasks, and AI-powered network operations.

## Prerequisites

Before starting the installation, ensure you have:

- **Python 3.11** installed on your system
- **PostgreSQL** database server running
- **Git** for version control
- Access to network devices (Cisco routers/switches) for testing

## Virtual Environment Setup

Create and activate the Python virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment (Linux/Mac)
source venv/bin/activate

# Activate virtual environment (Windows)
# venv\\Scripts\\activate
```

## Installation of Requirements

The project uses three separate requirement files for modular dependency management:

### Core Requirements (`requirements-core.txt`)

Contains essential dependencies for the main application:
- FastAPI, Uvicorn, SQLAlchemy, Pydantic
- PostgreSQL drivers (psycopg2-binary, psycopg)
- Network automation tools (Netmiko, PyATS, Genie)
- Authentication and security (python-jose, passlib, bcrypt)

```bash
pip install -r requirements-core.txt
```

### AI Requirements (`requirements-ai.txt`)

Contains AI/ML packages that may have conflicting dependencies:
- OpenAI, Groq, OpenRouter API clients
- CrewAI for multi-agent workflows
- LangChain and LangGraph for LLM orchestration
- ChromaDB for vector storage

```bash
pip install -r requirements-ai.txt
```

⚠️ **Note**: AI packages may conflict with core dependencies. Install them in a separate environment if issues arise.

### Automation Requirements (`requirements-automation.txt`)

Contains additional automation-specific dependencies:
- Enhanced scheduling capabilities
- Additional data processing tools

```bash
pip install -r requirements-automation.txt
```

## Database Bootstrap

### PostgreSQL Setup

Ensure PostgreSQL is installed and running on your system:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS (using Homebrew)
brew install postgresql
brew services start postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE your_database;
CREATE USER your_username WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE your_database TO your_username;
\q
```

### Database Initialization

To bootstrap the database, you have two options:

**Option 1: Automated Setup (Recommended for Development)**
```bash
bash init_setup.sh
```

This script will:
- Create/activate virtual environment
- Install core and AI dependencies
- Clear network ports (8001, 8002)
- Initialize database tables
- Create sample data (admin user, test devices, LLM settings)

**Option 2: Manual Setup**
```bash
python init_db.py
```

### Environment Configuration

Create a `.env` file in the project root with your PostgreSQL connection details:

```plaintext
# PostgreSQL Database Configuration
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database

# Application Ports
FRONTEND_PORT=8001
FASTAPI_PORT=8002

# Security (for automated scripts)
SUDO_PASSWORD=your_sudo_password
```

### Database Verification

After initialization, verify the database setup:

```bash
# Check if tables were created
python scripts/verify_db.py

# Default admin credentials created:
# Email: admin@example.com
# Password: admin123
```

## Port Allocation

The application uses several ports:

- **5000** – Backend API service (`backend/app.py`)
- **8002** – Main FastAPI service (`main.py`, `FASTAPI_PORT`)

## Full Start-up Flow

Follow this step-by-step process to start the entire system:

### Step 1: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 2: Database Initialization (Development)
```bash
bash init_setup.sh  # (dev)
```

### Step 3: Start Back-end API (Port 8002)
In **Terminal 2**:
```bash
python main.py  # (port 8002)
```

### Alternative: Using Service Scripts

You can also use the provided service management scripts:

```bash
# Start all services
bash start_services.sh

# Stop all services
bash stop_services.sh
```

### Verification

Once both services are running, verify the setup:

```bash
# Check backend health
curl http://localhost:8002/health

# Check frontend
curl http://localhost:8001

# Check alternative backend (port 5000)
curl http://localhost:5000/health
```

## Environment Variables Configuration

### Complete .env Example

Create a `.env` file with the following configuration:

```plaintext
# PostgreSQL Database Configuration
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database

# Application Ports
FRONTEND_PORT=8001
FASTAPI_PORT=8002

# Security
SUDO_PASSWORD=your_sudo_password

# LLM Provider API Keys (Optional)
OPENAI_API_KEY="your_openai_api_key"
GROQ_API_KEY="your_groq_api_key"
OPENROUTER_API_KEY="your_openrouter_api_key"

# Network Device Credentials (Optional)
DEVICE_USERNAME=your_network_device_username
DEVICE_PASSWORD=your_network_device_password
```

### API Key Configuration

To enable AI features, configure at least one LLM provider:

- **OpenAI**: Get API key from [platform.openai.com](https://platform.openai.com)
- **Groq**: Get API key from [console.groq.com](https://console.groq.com)
- **OpenRouter**: Get API key from [openrouter.ai](https://openrouter.ai)

## Troubleshooting & Common Errors

### Database Connection Issues

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
1. Verify PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql  # Linux
   brew services list | grep postgresql  # macOS
   ```

2. Check database credentials in `.env`
3. Ensure database and user exist:
   ```bash
   sudo -u postgres psql -c "\l"  # List databases
   sudo -u postgres psql -c "\du" # List users
   ```

### Port Already in Use

**Error**: `[Errno 48] Address already in use`

**Solutions**:
1. Use the setup script to clear ports:
   ```bash
   bash init_setup.sh
   ```

2. Manual port clearing:
   ```bash
   lsof -ti:8001 | xargs kill -9
   lsof -ti:8002 | xargs kill -9
   lsof -ti:5000 | xargs kill -9
   ```

### Python Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'backend'`

**Solutions**:
1. Ensure virtual environment is activated:
   ```bash
   source venv/bin/activate
   which python  # Should point to venv/bin/python
   ```

2. Install requirements:
   ```bash
   pip install -r requirements-core.txt
   pip install -r requirements-ai.txt
   ```

3. Run from project root directory

### AI/LLM Provider Errors

**Error**: `No LLM providers configured`

**Solutions**:
1. Add API keys to `.env` file
2. Restart the application after adding keys
3. Check API key validity:
   ```bash
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

### Network Device Connection Issues

**Error**: `NetmikoTimeoutException` or `NetmikoAuthenticationException`

**Solutions**:
1. Verify device IP addresses are reachable:
   ```bash
   ping 192.168.1.15
   ```

2. Test manual connection:
   ```bash
   telnet 192.168.1.15 23  # For telnet
   ssh user@192.168.1.15   # For SSH
   ```

3. Check device credentials in database or `.env`

### Performance Issues

**Problem**: Slow application startup or response times

**Solutions**:
1. Check system resources:
   ```bash
   htop  # Monitor CPU/Memory usage
   ```

2. Review application logs:
   ```bash
   tail -f backend.log
   tail -f frontend.log
   ```

3. Optimize database queries if needed

### Log File Locations

Application logs are stored in:
- `backend.log` - Backend API logs
- `frontend.log` - Frontend server logs
- `nohup.out` - Service startup logs

### Getting Help

If you continue to experience issues:

1. Check the application logs for detailed error messages
2. Verify all prerequisites are installed correctly
3. Ensure `.env` file contains all required variables
4. Test database connectivity separately
5. Review the project documentation in the `docs/` directory

