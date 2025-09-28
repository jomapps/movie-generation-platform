# Movie Generation Platform - Setup Guide

**Last Verified**: January 28, 2025  
**Platform**: Windows (PowerShell) with Docker support

This guide will help you set up the complete movie generation platform development environment on your local machine.

## 🎯 Prerequisites

### Required Software
- **Windows 10/11** with PowerShell 7+ (or Windows PowerShell)
- **Docker Desktop** - For running services in containers
- **Git** - With submodule support
- **Node.js 18+** - For frontend development  
- **Python 3.11+** - For backend services
- **Neo4j** - Can run via Docker

### Required Accounts/API Keys
⚠️ **Note**: API key configuration is being clarified. See [Clarifications Document](CLARIFICATIONS.md) for current status.

**Confirmed Requirements:**
- **Jina v4 API Key** - For text embeddings (brain service)
- **Neo4j Database** - For knowledge graph storage

**Additional API Keys** (configuration being verified):
- **OpenRouter API Key** - For LLM services  
- **FAL.ai API Key** - For media generation
- **ElevenLabs API Key** - For voice generation

## 🚀 Quick Setup (Recommended)

### 1. Clone Repository with Submodules

```bash
# Clone the main repository with all submodules
git clone --recursive https://github.com/your-org/movie-generation-platform.git
cd movie-generation-platform

# If already cloned without submodules, initialize them
git submodule update --init --recursive
```

### 2. Verify Submodule Status

```bash
# Check that all submodules are properly initialized
git submodule status

# Expected output should show commits for:
# - apps/auto-movie
# - services/mcp-brain-service  
# - services/langgraph-orchestrator
# - services/celery-redis
# - And other supporting services
```

### 3. Start Core Services (Docker)

**Start Brain Service (REQUIRED - other services depend on this):**
```bash
cd services/mcp-brain-service

# Create local env file and configure (Docker Compose reads .env.local)
cp .env .env.local  # or create .env.local from scratch
# Edit .env.local with your API keys (see Environment Configuration below)

# Start with Docker
docker compose up -d

# Verify it's running
curl http://localhost:8002/health
```

**Start Orchestrator Service:**
```bash
cd ../langgraph-orchestrator

# Configure environment
cp .env.example .env
# Edit with brain service connection details

# Start service
docker-compose up -d
```

### 4. Start Frontend Application

```bash
cd ../../apps/auto-movie

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit with your configuration

# Start development server
npm run dev

# Verify frontend is running
open http://localhost:3010
```

### 5. Verify Complete Setup

```bash
# Test brain service health
curl http://localhost:8002/health

# Test frontend
curl http://localhost:3010

# Check all containers are running
docker ps
```

## 📋 Detailed Setup Steps

### Environment Configuration

#### Brain Service (.env.local)
```bash
# services/mcp-brain-service/.env.local

# CRITICAL - Required for brain service to function
JINA_API_KEY=your_jina_api_key_here
JINA_API_URL=https://api.jina.ai/v1/embeddings
JINA_MODEL=jina-embeddings-v4

# Database configuration
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password

# Service configuration
PORT=8002
ENVIRONMENT=development

# CORS configuration for frontend
CORS_ORIGINS=http://localhost:3010,http://localhost:3000
```

#### Frontend Configuration (.env.local)
```bash
# apps/auto-movie/.env.local

# Brain service connection
NEXT_PUBLIC_BRAIN_SERVICE_URL=http://localhost:8002

# PayloadCMS configuration  
PAYLOAD_SECRET=your-payload-secret-key
MONGODB_URI=mongodb://localhost:27017/auto-movie

# Development settings
NODE_ENV=development
```

#### Orchestrator Configuration (.env)
```bash
# services/langgraph-orchestrator/.env

# Brain service connection (CRITICAL)
BRAIN_SERVICE_BASE_URL=http://localhost:8002
BRAIN_SERVICE_WS_URL=ws://localhost:8002/mcp

# LLM configuration (being clarified - see CLARIFICATIONS.md)
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Development settings
ENVIRONMENT=development
```

### Manual Service Setup (Alternative to Docker)

If you prefer to run services manually without Docker:

#### Brain Service Manual Setup
```bash
cd services/mcp-brain-service

# Create Python virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start Neo4j (requires separate installation or Docker)
# docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/your_password neo4j:latest

# Run the service
python -m src.main
```

#### Frontend Manual Setup
```bash
cd apps/auto-movie

# Install Node.js dependencies
npm install

# Start MongoDB (requires separate installation or Docker)
# docker run -d --name mongodb -p 27017:27017 mongo:latest

# Run development server
npm run dev
```

## 🧪 Testing Your Setup

### 1. Brain Service Functionality Test

```bash
# Test basic health endpoint
curl http://localhost:8002/health

# Test MCP WebSocket connection (requires wscat: npm install -g wscat)
wscat -c ws://localhost:8002/
# Then send a JSON message like:
# {"tool":"create_character","project_id":"smoke-test","name":"Alice","personality_description":"Curious and adventurous","appearance_description":"Short blonde hair"}

# You should receive a success response with a character_id
```

### 2. Frontend Integration Test

```bash
# Verify frontend loads
curl http://localhost:3010

# Check if brain service connection is working
# Look for any console errors in browser developer tools
```

### 3. End-to-End Workflow Test

1. **Open Frontend**: Navigate to http://localhost:3010
2. **Create Project**: Try creating a new movie project
3. **Test AI Chat**: Use the chat interface (if implemented)
4. **Check Logs**: Verify no errors in service logs

```bash
# Check service logs
docker logs mcp-brain-service
docker logs langgraph-orchestrator

# Or if running manually, check terminal output
```

## 🛠️ Development Tools

### Recommended IDE Setup

**Visual Studio Code Extensions:**
- Python extension (for backend services)
- TypeScript and Next.js extensions (for frontend)
- Docker extension (for container management)
- REST Client (for API testing)

### Useful Commands

```bash
# Update all submodules to latest
git submodule update --recursive --remote

# Restart all Docker services
docker compose down && docker compose up -d

# View all service logs
docker compose logs -f

# Clean up Docker resources
docker system prune
```

## 🚧 Troubleshooting

### Common Issues

#### "Brain Service Not Found" Error
**Problem**: Frontend cannot connect to brain service  
**Solution**: 
1. Verify brain service is running: `curl http://localhost:8002/health`
2. Check firewall/antivirus blocking port 8002
3. Verify CORS configuration includes frontend URL

#### "MCP Connection Failed" Error  
**Problem**: Services cannot connect via MCP WebSocket  
**Solution**:
1. Check brain service WebSocket endpoint: `wscat -c ws://localhost:8002/mcp`
2. Verify environment variables point to correct brain service URL
3. Check for port conflicts

#### "Database Connection Error" Error
**Problem**: Services cannot connect to Neo4j or MongoDB  
**Solution**:
1. Verify databases are running: `docker ps`
2. Check connection strings in .env files
3. Verify database credentials

#### Submodule Issues
**Problem**: Empty submodule directories or missing code  
**Solution**:
```bash
# Re-initialize submodules
git submodule deinit --all
git submodule update --init --recursive

# If still having issues, check submodule URLs
cat .gitmodules
```

### Getting Help

1. **Check Logs**: Always start by checking service logs for error details
2. **Verify Configuration**: Double-check all .env files have correct values
3. **Test Components**: Isolate issues by testing each service individually  
4. **Documentation**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed issue resolution
5. **Clarifications**: Check [CLARIFICATIONS.md](CLARIFICATIONS.md) for known configuration issues

## 🎯 Next Steps After Setup

Once your environment is running:

1. **Read Documentation**: Review [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) to understand current project state
2. **Explore Architecture**: Study [ARCHITECTURE.md](ARCHITECTURE.md) to understand the MCP brain service pattern  
3. **Check APIs**: Review [API_REFERENCE.md](API_REFERENCE.md) for available tools and endpoints
4. **Start Contributing**: Follow [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) for contribution guidelines

## 📝 Environment Verification Checklist

Use this checklist to verify your setup is complete:

- [ ] **Git Repository**: Cloned with all submodules initialized
- [ ] **Brain Service**: Running on port 8002, health endpoint responding
- [ ] **Neo4j Database**: Running and accessible to brain service
- [ ] **Frontend**: Running on port 3010, loads without errors
- [ ] **MongoDB**: Running and accessible to frontend (PayloadCMS)
- [ ] **Orchestrator**: Running and connected to brain service via MCP
- [ ] **Docker**: All containers running without errors
- [ ] **API Keys**: All required API keys configured (see CLARIFICATIONS.md)
- [ ] **Network**: No firewall issues blocking required ports
- [ ] **Testing**: Basic functionality tests passing

---

**Need more help?** 
- 🔧 [Troubleshooting Guide](TROUBLESHOOTING.md) - Detailed problem resolution
- ❓ [Clarifications](CLARIFICATIONS.md) - Known configuration issues  
- 📊 [Development Status](DEVELOPMENT_STATUS.md) - What's implemented vs planned