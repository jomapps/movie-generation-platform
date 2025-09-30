# Video Generation Service - Quick Start Guide

**Status**: ✅ **DEPLOYED AND OPERATIONAL**  
**Deployment Date**: September 30, 2025 - 05:30 UTC

## ⚡ TL;DR - What You Need To Do

1. **Get FAL.ai API Key** → https://fal.ai (Sign up, get API key)
2. **Create .env file** → Copy from template and add your keys
3. **Deploy service** → Run PM2 commands below

---

## 🔑 Step 1: Get FAL.ai API Key

```
1. Go to: https://fal.ai
2. Sign up or log in
3. Go to Dashboard → API Keys
4. Create new API key
5. Copy it (looks like: fal_xxxxxxxxxxxxxxxx)
```

---

## 📝 Step 2: Create Production .env File

```bash
# Navigate to service
cd /var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service

# Copy template
cp .env.prod.example .env

# Edit and add your FAL.ai key
nano .env
```

**What to change in .env:**
```env
# CHANGE THIS LINE - Add your actual FAL.ai API key
FAL_API_KEY=fal_your_actual_key_here

# CHANGE THIS LINE - Add your PayloadCMS key (optional for MVP)
PAYLOADCMS_API_KEY=your-key-here

# These are already correct - DON'T CHANGE
OPENROUTER_API_KEY=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
OPENROUTER_DEFAULT_MODEL=anthropic/claude-sonnet-4.5
```

---

## 🚀 Step 3: Deploy

```bash
# Still in the service directory
cd /var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service

# Install dependencies
pip3 install -r requirements.txt
pip3 install pydantic-settings python-dotenv

# Deploy with PM2
pm2 start "python3 -m src.mcp_server" --name mcp-video-generation-service

# Save configuration
pm2 save

# Check status
pm2 list | grep video-generation
```

---

## ✅ Step 4: Verify

```bash
# Should show "online"
pm2 list | grep video-generation

# Check logs (should have no errors)
pm2 logs mcp-video-generation-service --lines 10
```

**Expected result**: Service shows "online" status with 0 restarts

---

## 🎯 What This Service Does

```
Images (from Visual MCP) 
    ↓
Video Generation Service (FAL.ai)
    ↓
Video Segments (MP4 files)
    ↓
Video Editor (next service to deploy)
```

**Key Feature**: Uses FAL.ai to animate static images into video clips

---

## 📊 Deployment Progress

**After deploying this service:**
- ✅ Story Services (3/3)
- ✅ Character MCP
- ✅ Visual MCP  
- ✅ **Video Generation** ← You are here
- ⏭️ Video Editor (next)
- ⏭️ Final QC
- ⏭️ Distribution

**MVP Completion**: 8 of 11 steps (73%)

---

## 🔄 After Deployment - What's Next?

### Immediate Next Steps:
1. **Test video generation** with sample frames
2. **Deploy Video Editor Service** to concatenate segments
3. **Test end-to-end** image → video workflow

### Next Service to Deploy:
**Video Editor Service** (mcp-video-editor-service)
- **Purpose**: Concatenates video segments into final MP4
- **Priority**: 🔴 CRITICAL (needed for complete MVP)
- **Location**: `/services/mcp-video-editor-service`

---

## 🆘 Need Help?

**Can't find FAL.ai key?**
- Check: https://fal.ai/dashboard/keys
- Need account: Sign up at https://fal.ai

**Service won't start?**
```bash
pm2 logs mcp-video-generation-service --err
```

**Wrong directory?**
```bash
cd /var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service
pwd  # Verify you're in the right place
```

---

## 📋 Commands Summary

```bash
# Navigate
cd /var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service

# Setup
cp .env.prod.example .env
nano .env  # Add FAL.ai key

# Install
pip3 install -r requirements.txt pydantic-settings python-dotenv

# Deploy
pm2 start "python3 -m src.mcp_server" --name mcp-video-generation-service
pm2 save

# Verify
pm2 list | grep video-generation
pm2 logs mcp-video-generation-service
```

---

**That's it!** Follow these steps and the Video Generation Service will be live! 🎬
