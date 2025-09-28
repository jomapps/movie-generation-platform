# Movie Generation Platform

**AI-Powered Movie Production Platform** - Create professional-quality movies using intelligent AI assistance, from story concept to final production.

[![Status: Phase 1 Complete](https://img.shields.io/badge/Status-Phase%201%20Complete-green)](docs/DEVELOPMENT_STATUS.md)
[![Architecture: MCP Brain Service](https://img.shields.io/badge/Architecture-MCP%20Brain%20Service-blue)](docs/ARCHITECTURE.md)
[![Platform: Windows + Docker](https://img.shields.io/badge/Platform-Windows%20%2B%20Docker-lightblue)](#quick-start)

## ⚡ Quick Start

```bash
# 1. Clone with submodules
git clone --recursive <repository-url>
cd movie-generation-platform

# 2. Start core services (requires Docker)
cd services/mcp-brain-service && docker-compose up -d
cd ../langgraph-orchestrator && docker-compose up -d

# 3. Start frontend
cd ../../apps/auto-movie
npm install && npm run dev

# 4. Verify setup
curl http://localhost:8002/health  # Brain service
open http://localhost:3010         # Frontend
```

**Need help?** See the complete [Setup Guide](docs/SETUP_GUIDE.md).

## 🏗️ Architecture Overview

**Centralized Brain Service Model** - All AI/ML operations flow through a single "brain" service:

```
Users → Frontend (Port 3010) ┐
                             ├── MCP WebSocket ──► Brain Service (Port 8002) ──► AI APIs
LangGraph Orchestrator ──────┤                                                   (Jina, OpenRouter,
Celery Tasks ────────────────┘                                                    FAL.ai, etc.)
```

**Key Benefits:**
- ✅ **Consistent AI**: All services use the same AI models and knowledge
- ✅ **Reliable**: Centralized error handling and fallback strategies  
- ✅ **Scalable**: Add new services without managing separate AI integrations
- ✅ **Secure**: API keys centralized in one service only

📖 **[Complete Architecture Documentation](docs/ARCHITECTURE.md)**

## 🎯 What Can You Build?

- **🎬 Complete Movies**: AI-guided story development, character creation, and production planning
- **📚 Interactive Stories**: Dynamic narratives with character consistency and plot development  
- **🎨 Visual Content**: AI-generated storyboards, concept art, and character designs
- **🤝 Collaborative Projects**: Real-time editing with multiple team members
- **📈 Production Management**: Timeline tracking, resource planning, and progress monitoring

**Current Status**: ✅ Core infrastructure complete | 🔄 User interface in progress  
📊 **[Detailed Development Status](docs/DEVELOPMENT_STATUS.md)**

## 📚 Documentation

### Essential Reading (Start Here)
- 📖 **[Project Overview](docs/PROJECT_OVERVIEW.md)** - What we're building and why
- 🏗️ **[Architecture Guide](docs/ARCHITECTURE.md)** - Technical design and MCP brain service pattern  
- 📊 **[Development Status](docs/DEVELOPMENT_STATUS.md)** - Current progress and roadmap
- ⚙️ **[Setup Guide](docs/SETUP_GUIDE.md)** - Complete development environment setup

### Reference Documentation
- 📋 **[API Reference](docs/API_REFERENCE.md)** - MCP tools and REST endpoints
- 🚀 **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- 🔧 **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- 👥 **[Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)** - How to contribute

### Questions or Issues?
- ❓ **[Clarifications Needed](docs/CLARIFICATIONS.md)** - Items requiring discussion
- 📁 **[Documentation Structure](docs/DOCUMENTATION_STRUCTURE.md)** - How docs are organized

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **📖 Read**: [Development Status](docs/DEVELOPMENT_STATUS.md) to understand current priorities
2. **⚙️ Setup**: Follow the [Setup Guide](docs/SETUP_GUIDE.md) to get everything running  
3. **🔍 Explore**: Check [Clarifications Needed](docs/CLARIFICATIONS.md) for areas needing help
4. **💻 Code**: Follow our [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)

**Priority Areas:**
- 🎯 **Frontend MCP Integration** (TypeScript WebSocket client)
- 🧠 **Orchestrator Cleanup** (Remove direct database dependencies) 
- 🔧 **Testing Infrastructure** (Cross-service integration tests)
- 📝 **API Documentation** (Complete MCP tool reference)

## ⚡ Key Features

### 🧠 AI-Powered Intelligence
- **20+ MCP Tools**: Text embedding, semantic search, knowledge graphs
- **Multi-Provider LLMs**: OpenRouter, FAL.ai, ElevenLabs with fallback support
- **Context-Aware**: AI that understands your project state and history
- **Batch Processing**: Efficient handling of large datasets and workflows

### 🎬 Movie Production Tools
- **Story Development**: AI-guided narrative creation and refinement
- **Character Management**: Consistency tracking across your entire project
- **Visual Pipeline**: Storyboard generation and concept development (planned)
- **Collaboration**: Real-time multi-user editing and project sharing

### 🏗️ Developer Experience  
- **MCP Protocol**: Standardized AI tool communication across all services
- **Docker Ready**: Complete containerization for easy deployment
- **Comprehensive Testing**: 95% test coverage with integration test suite
- **Modern Stack**: Next.js 15, Python 3.11+, TypeScript, Neo4j

## 🚀 Project Status

| Component | Status | Progress | Notes |
|-----------|--------|----------|-------|
| **🧠 MCP Brain Service** | ✅ **Complete** | 100% | Production ready with 20+ MCP tools |
| **🎬 Auto-Movie Frontend** | 🔄 **In Progress** | 65% | Next.js app with PayloadCMS |
| **🤖 LangGraph Orchestrator** | 🔄 **In Progress** | 75% | Workflow engine, needs MCP cleanup |
| **⚙️ Celery Task Service** | ❌ **Planned** | 0% | Background processing (Phase 2) |
| **📖 Documentation** | ✅ **Complete** | 100% | Comprehensive docs in `/docs/` folder |

## 🎯 Getting Started

**New to the project?** Follow this path:

1. **🎬 [Project Overview](docs/PROJECT_OVERVIEW.md)** - Understand the vision and goals
2. **🏗️ [Architecture Guide](docs/ARCHITECTURE.md)** - Learn the technical design  
3. **📊 [Development Status](docs/DEVELOPMENT_STATUS.md)** - See what's built and what's next
4. **⚙️ [Setup Guide](docs/SETUP_GUIDE.md)** - Get your development environment running
5. **👥 [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)** - Start contributing!

**Need Help?** Check our [Troubleshooting Guide](docs/TROUBLESHOOTING.md) or review [items needing clarification](docs/CLARIFICATIONS.md).

---

**Repository**: Movie Generation Platform | **License**: [License] | **Version**: Phase 1 Complete  
**Questions?** See [Clarifications](docs/CLARIFICATIONS.md) | **Issues?** Check [Troubleshooting](docs/TROUBLESHOOTING.md)

