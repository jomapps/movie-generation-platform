# Video Services - Correct Directory Paths

## 🔍 Understanding the Structure

The video services are **git submodules** with a nested structure. This is intentional for repository organization.

---

## ✅ CORRECT Paths for Each Service

### Video Generation Service

**Full Path (USE THIS)**:
```bash
cd /var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service
```

**Why nested?** 
- `services/mcp-video-generation-service/` = Git submodule (repository root)
- `services/mcp-video-generation-service/services/mcp-video-generation-service/` = Actual service code

**Files Location**:
- `.env` → Create here
- `src/mcp_server.py` → Main entry point
- `src/config.py` → Configuration ✅ Already created
- `requirements.txt` → Dependencies

---

### Video Editor Service

**Full Path (USE THIS)**:
```bash
cd /var/www/movie-generation-platform/services/mcp-video-editor-service/services/mcp-video-editor-service
```

**Files Location**:
- `.env.example` → Already exists
- `src/` → Service code
- `requirements.txt` → Dependencies

---

## 📋 Quick Navigation Commands

```bash
# Video Generation Service
export VIDEO_GEN_PATH="/var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service"
cd $VIDEO_GEN_PATH

# Video Editor Service  
export VIDEO_EDIT_PATH="/var/www/movie-generation-platform/services/mcp-video-editor-service/services/mcp-video-editor-service"
cd $VIDEO_EDIT_PATH

# Or create aliases (add to ~/.bashrc)
alias cdvideogen="cd /var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service"
alias cdvideoeditor="cd /var/www/movie-generation-platform/services/mcp-video-editor-service/services/mcp-video-editor-service"
```

---

## 🚀 Deployment Commands (Copy-Paste Ready)

### Video Generation Service

```bash
# Navigate to correct directory
cd /var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service

# Create .env from template
cp .env.prod.example .env

# Edit with your FAL.ai API key
nano .env
# UPDATE: FAL_API_KEY=your-fal-key-here

# Install dependencies
pip3 install -r requirements.txt

# Deploy with PM2 (use full path for --cwd)
pm2 start "python3 -m src.mcp_server" \
  --name mcp-video-generation-service \
  --cwd /var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service

# Save
pm2 save

# Verify
pm2 list | grep video-generation
```

### Video Editor Service (When Ready)

```bash
# Navigate to correct directory
cd /var/www/movie-generation-platform/services/mcp-video-editor-service/services/mcp-video-editor-service

# Create .env from template
cp .env.example .env

# Edit with your keys
nano .env

# Install dependencies
pip3 install -r requirements.txt

# Deploy with PM2
pm2 start "python3 -m src.main" \
  --name mcp-video-editor-service \
  --cwd /var/www/movie-generation-platform/services/mcp-video-editor-service/services/mcp-video-editor-service

# Save
pm2 save
```

---

## 🗂️ Service Organization Summary

```
services/
├── mcp-video-generation-service/        ← Git submodule root
│   ├── services/
│   │   └── mcp-video-generation-service/ ← ACTUAL SERVICE CODE HERE
│   │       ├── .env                      ← CREATE THIS
│   │       ├── .env.prod.example         ← Template (already created)
│   │       ├── src/
│   │       │   ├── mcp_server.py        ← Entry point
│   │       │   └── config.py            ← Config (already created)
│   │       └── requirements.txt
│   └── (other nested services from submodule repo)
│
└── mcp-video-editor-service/            ← Git submodule root
    ├── services/
    │   └── mcp-video-editor-service/    ← ACTUAL SERVICE CODE HERE
    │       ├── .env.example
    │       ├── src/
    │       └── requirements.txt
    └── (other nested services from submodule repo)
```

---

## ⚠️ Important Notes

1. **Always use the FULL nested path** when deploying
2. **The outer directory is the git submodule** (contains .git file pointing to parent)
3. **The inner directory has the actual service code** (has src/, requirements.txt)
4. **PM2 --cwd flag MUST use the full nested path**

---

## 🎯 Quick Reference

**Video Generation Service Path**:
```
/var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service
```

**Video Editor Service Path**:
```
/var/www/movie-generation-platform/services/mcp-video-editor-service/services/mcp-video-editor-service
```

**Pro Tip**: Save these paths as environment variables or shell aliases!

---

## ✅ Configuration Status

### Video Generation Service
- ✅ `.env.prod.example` created
- ✅ `.env.dev.example` created
- ✅ `.gitignore` created
- ✅ `src/config.py` created
- ✅ `DEPLOYMENT.md` created
- ✅ OpenRouter LLM configured
- ⚠️ **Need**: FAL.ai API key

### Video Editor Service
- 📋 To be configured next
- ✅ Service code exists
- 📋 Need production .env files

---

**Use this document as reference for all video service deployments!**
