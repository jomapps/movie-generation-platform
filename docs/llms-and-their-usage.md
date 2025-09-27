# LLMs and Their Usage in Movie Generation Platform

This document outlines all the Large Language Models (LLMs) and AI services used throughout the movie generation platform, their specific purposes, and where they are implemented.

***CORRECTIONS IMPLEMENTED***
The codebase has been updated to use the correct LLM configurations as specified below.

RULE 1: We only use env variables for llm keys. Here are all the key names that we put in the corresponding `.env` file.

### 🔑 **ACTUAL API KEYS TO USE:**
```bash
# OpenRouter (LLM operations)
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=anthropic/claude-sonnet-4
OPENROUTER_BACKUP_MODEL=qwen/qwen3-vl-235b-a22b-thinking

# Fal.ai (Media generation)
FAL_KEY=1c65271b-e758-4e19-9eea-3f4f79dc5edd:86e949180e8c80822ab57d386e4e19ce
FAL_TEXT_TO_IMAGE_MODEL=fal-ai/nano-banana
FAL_IMAGE_TO_IMAGE_MODEL=fal-ai/nano-banana/edit

# Embeddings (Brain Service Only)
JINA_API_KEY=jina_bafa0ee92bea44198004e4ca0c9d517coCaPnnZjX0bUmXU8WnfR3NE3YcpK

# Voice generation
ELEVENLABS_API_KEY=sk_1709b158c06739d22eb0573eb4ba410d04ac0e8d7a01c414
```

RULE 2: We do not use llms used other than the ones defined in RULE 1 above.

***STATUS: CORRECTED*** - The codebase now uses the correct configurations above instead of the old patterns listed below for reference.

## Primary LLM Services

### 1. **Novel LLM Service** (Priority 1)
- **Model**: `gpt-4-turbo-preview`
- **Base URL**: `https://api.novellm.com/v1` (configurable via `NOVEL_LLM_BASE_URL`)
- **API Key**: `NOVEL_LLM_API_KEY`
- **Usage**: Primary AI service for all movie production assistance
- **Location**: `apps/auto-movie/src/services/aiErrorHandling.ts` & `apps/auto-movie/src/services/novelLLM.ts`
- **Features**:
  - Chat message processing
  - Project context understanding
  - Multi-step movie production guidance
  - Function calling capabilities
  - Fallback handling with circuit breakers

### 2. **OpenAI GPT-4** (Priority 2 - Fallback)
- **Model**: `gpt-4-turbo-preview`
- **Base URL**: `https://api.openai.com/v1`
- **API Key**: `OPENAI_API_KEY`
- **Usage**: Fallback service when Novel LLM is unavailable
- **Location**: `apps/auto-movie/src/services/aiErrorHandling.ts`
- **Features**:
  - Same capabilities as Novel LLM
  - Function calling support
  - Circuit breaker protection

### 3. **Anthropic Claude** (Priority 3 - Fallback)
- **Model**: `claude-3-sonnet-20240229`
- **Base URL**: `https://api.anthropic.com/v1`
- **API Key**: `ANTHROPIC_API_KEY`
- **Usage**: Secondary fallback service
- **Location**: `apps/auto-movie/src/services/aiErrorHandling.ts`
- **Features**:
  - System prompt support
  - Different request format than OpenAI-compatible services

## Alternative LLM Configurations

### 4. **Qwen3-VL Model** (Multimodal)
- **Model**: `qwen/qwen3-vl-235b-a22b-thinking` (default) or `qwen3-vl-72b`
- **Base URL**: Configurable via `QWEN3VL_BASE_URL` or `LLM_BASE_URL`
- **API Key**: `QWEN3VL_API_KEY` or `LLM_API_KEY`
- **Usage**: Multimodal processing (text + images)
- **Location**: `apps/auto-movie/src/services/novelLLM.ts` & documentation
- **Features**:
  - Vision capabilities for image analysis
  - Multimodal input processing
  - Used in chat message processing

### 5. **OpenRouter Integration**
- **Base URL**: `https://openrouter.ai/api/v1` (fallback)
- **API Key**: `OPENROUTER_API_KEY`
- **Model**: `OPENROUTER_DEFAULT_MODEL`
- **Usage**: Alternative routing service for various models
- **Location**: `apps/auto-movie/src/services/novelLLM.ts`

## Specialized AI Services

### 6. **LangGraph Orchestrator Models**
- **Models**: `o3`, `gpt-3.5-turbo`, `gpt-5-codex`
- **Usage**: Workflow orchestration and agent coordination
- **Location**: `services/langgraph-orchestrator/docs_config_raw.md`
- **Features**:
  - Multiple model provider support
  - Profile-based configuration
  - Reasoning effort control

### 7. **Jina Embeddings v4**
- **Model**: `jina-embeddings-v2-base-en`
- **Base URL**: `https://api.jina.ai/v1/embeddings`
- **API Key**: `JINA_API_KEY`
- **Usage**: Text embeddings for semantic search and knowledge graph
- **Location**: `services/mcp-brain-service/src/lib/embeddings.py`
- **Features**:
  - Character similarity search
  - Semantic content matching
  - Batch processing capabilities

## Specific Use Cases by Component

### Auto-Movie App (`apps/auto-movie/`)
- **Chat Interface**: Novel LLM → OpenAI → Anthropic (fallback chain)
- **Project Guidance**: Context-aware prompts for movie production steps
- **Content Generation**: Script writing, character development, story planning
- **File Processing**: Multimodal analysis with Qwen3-VL

### Celery Task Service (`services/celery-redis/`)
- **Task Types**: Video generation, image generation, audio processing
- **AI Integration**: Connects to Auto-Movie's LLM services for content generation
- **GPU Processing**: Heavy AI tasks offloaded from main application

### MCP Brain Service (`services/mcp-brain-service/`)
- **Embeddings**: Jina v4 for character and content embeddings
- **Knowledge Graph**: Neo4j with semantic search capabilities
- **Character Management**: AI-powered character similarity and relationships

### LangGraph Orchestrator (`services/langgraph-orchestrator/`)
- **Workflow AI**: Script generation, voice generation, visual content creation
- **Agent Coordination**: Multi-agent workflows for complex movie production tasks
- **Model Selection**: Dynamic model selection based on task requirements

## 🚀 DEPLOYMENT ENVIRONMENT VARIABLES CHECKLIST

**Use this checklist when deploying or updating services to ensure correct LLM configuration.**

### Required Environment Variables by Service

#### **1. Auto-Movie App (apps/auto-movie) - Port 3010**
```bash
# LLM Services
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=anthropic/claude-sonnet-4
OPENROUTER_BACKUP_MODEL=qwen/qwen3-vl-235b-a22b-thinking

# Media Generation
FAL_KEY=1c65271b-e758-4e19-9eea-3f4f79dc5edd:86e949180e8c80822ab57d386e4e19ce
FAL_TEXT_TO_IMAGE_MODEL=fal-ai/nano-banana
FAL_IMAGE_TO_IMAGE_MODEL=fal-ai/nano-banana/edit

# Voice Generation
ELEVENLABS_API_KEY=sk_1709b158c06739d22eb0573eb4ba410d04ac0e8d7a01c414

# Service URLs (keep existing)
NEXT_PUBLIC_BRAIN_SERVICE_URL=https://brain.ft.tc
NEXT_PUBLIC_TASK_SERVICE_URL=http://localhost:8001
NEXT_PUBLIC_AGENTS_SERVICE_URL=http://localhost:8003
```

#### **2. MCP Brain Service (services/mcp-brain-service) - Port 8002**
```bash
# Embeddings (PRIMARY - DO NOT CHANGE)
JINA_API_KEY=jina_bafa0ee92bea44198004e4ca0c9d517coCaPnnZjX0bUmXU8WnfR3NE3YcpK

# Database (keep existing)
NEO4J_URI=neo4j://neo4j.ft.tc:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_existing_neo4j_password

# Service Config (keep existing)
PORT=8002
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3010,https://auto-movie.ngrok.pro,https://auto-movie.ft.tc
```

#### **3. LangGraph Orchestrator (services/langgraph-orchestrator) - Port 8003**
```bash
# LLM Configuration (ADD THESE)
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=anthropic/claude-sonnet-4
OPENROUTER_BACKUP_MODEL=qwen/qwen3-vl-235b-a22b-thinking

# Brain Service Communication (ADD THIS)
BRAIN_SERVICE_WS_URL=wss://brain.ft.tc/mcp

# Keep existing service URLs
BRAIN_SERVICE_BASE_URL=https://brain.ft.tc
AUTO_MOVIE_BASE_URL=https://auto-movie.ft.tc
TASK_SERVICE_BASE_URL=https://tasks.ft.tc
```

#### **4. Celery Task Service (services/celery-redis) - Port 8001**
```bash
# LLM Configuration (ADD THESE)
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=anthropic/claude-sonnet-4
OPENROUTER_BACKUP_MODEL=qwen/qwen3-vl-235b-a22b-thinking

# Media Generation (ADD THESE)
FAL_KEY=1c65271b-e758-4e19-9eea-3f4f79dc5edd:86e949180e8c80822ab57d386e4e19ce
FAL_TEXT_TO_IMAGE_MODEL=fal-ai/nano-banana
FAL_IMAGE_TO_IMAGE_MODEL=fal-ai/nano-banana/edit

# Voice Generation (ADD THIS)
ELEVENLABS_API_KEY=sk_1709b158c06739d22eb0573eb4ba410d04ac0e8d7a01c414

# Brain Service Communication (ADD THIS)
BRAIN_SERVICE_WS_URL=wss://brain.ft.tc/mcp

# Keep existing configurations
BRAIN_SERVICE_BASE_URL=https://brain.ft.tc
```

### 🗑️ **Environment Variables to REMOVE**

**Delete these from ALL services if they exist:**
```bash
# ❌ REMOVE - Old incorrect LLM configs
NOVEL_LLM_API_KEY=*
NOVEL_LLM_BASE_URL=*
OPENAI_API_KEY=*
ANTHROPIC_API_KEY=*
QWEN3VL_API_KEY=*
QWEN3VL_BASE_URL=*
LLM_API_KEY=*
LLM_BASE_URL=*
LLM_DEFAULT_MODEL=*
```

### 📋 **Deployment Verification Checklist**

**After updating environment variables:**

1. **✅ Test OpenRouter Connection:**
   ```powershell
   curl -H "Authorization: Bearer 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" https://openrouter.ai/api/v1/models
   ```

2. **✅ Test Fal.ai Connection:**
   ```powershell
   curl -H "Authorization: Key 1c65271b-e758-4e19-9eea-3f4f79dc5edd:86e949180e8c80822ab57d386e4e19ce" https://fal.run/fal-ai/models
   ```

3. **✅ Test ElevenLabs Connection:**
   ```powershell
   curl -H "xi-api-key: sk_1709b158c06739d22eb0573eb4ba410d04ac0e8d7a01c414" https://api.elevenlabs.io/v1/voices
   ```

4. **✅ Test Brain Service Health:**
   ```powershell
   curl https://brain.ft.tc/health
   ```

5. **✅ Restart Services:**
   ```powershell
   # Restart in this order:
   # 1. Brain Service (Port 8002)
   # 2. LangGraph Orchestrator (Port 8003) 
   # 3. Celery Tasks (Port 8001)
   # 4. Auto-Movie App (Port 3010)
   ```

### 🔄 **Service-Specific Update Commands**

**For Coolify deployments:**
```bash
# Update environment variables in Coolify dashboard:
# 1. Go to Application → Environment Variables
# 2. Add/Update the variables listed above for each service
# 3. Click "Save" and "Deploy"
```

**For Docker deployments:**
```bash
# Update .env files and restart containers:
docker-compose down
docker-compose up -d
```

**For manual deployments:**
```powershell
# Update environment files in each service directory
# Restart the service processes
```

## AI Service Architecture

### Failover Strategy
1. **Primary**: Novel LLM (highest priority)
2. **Fallback 1**: OpenAI GPT-4
3. **Fallback 2**: Anthropic Claude
4. **Emergency**: Predefined responses when all services fail

### Circuit Breaker Protection
- **Failure Threshold**: 5 failures before circuit opens
- **Reset Timeout**: 60 seconds
- **Monitoring Period**: 30 seconds
- **Automatic Recovery**: Services automatically retry when available

### Request Configuration
- **Timeout**: 30 seconds default
- **Max Tokens**: 2000 default
- **Temperature**: 0.7 default
- **Retry Logic**: Exponential backoff with jitter

## Content Generation Workflows

### Story Development
- **Primary LLM**: Novel LLM for narrative structure
- **Fallbacks**: OpenAI/Anthropic for continuity
- **Prompts**: Specialized templates in `apps/auto-movie/src/utils/prompts.ts`

### Character Creation
- **LLM**: Novel LLM for personality and traits
- **Embeddings**: Jina v4 for similarity matching
- **Storage**: Neo4j knowledge graph via MCP Brain Service

### Script Generation
- **Orchestration**: LangGraph with multiple model support
- **Context**: Brain service for similar content retrieval
- **Output**: Structured scripts with scene breakdowns

### Visual Content
- **Planning**: LLM-generated storyboards and shot descriptions
- **Processing**: Celery tasks for actual image/video generation
- **Coordination**: Multi-agent workflows via LangGraph

This architecture provides robust, scalable AI capabilities with proper fallback mechanisms and specialized services for different aspects of movie production.
