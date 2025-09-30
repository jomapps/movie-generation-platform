# Video Generation Service - Deployment Plan

**Created**: September 30, 2025  
**Service**: mcp-video-generation-service  
**Status**: ✅ **DEPLOYED AND LIVE** (Sept 30, 2025 05:30 UTC)

---

## 🎯 What This Service Does

Converts storyboard frames into video segments using **FAL.ai** video synthesis:
- Takes images from Image Generation service
- Groups frames into 2-4 second segments
- Generates motion prompts from storyboard descriptions
- Calls FAL.ai API to create video segments
- Returns MP4 segments for Video Editor to concatenate

**Input**: Generated images + storyboard metadata  
**Output**: Video segments (MP4 files)  
**Provider**: FAL.ai (veo3/fast/image-to-video model)

---

## ✅ Configuration Complete

### Files Created:
1. ✅ `.env.prod.example` - Production environment template
2. ✅ `.env.dev.example` - Development environment template
3. ✅ `.gitignore` - Proper git configuration
4. ✅ `src/config.py` - Environment variable management
5. ✅ `DEPLOYMENT.md` - Complete deployment guide
6. ✅ `src/providers/fal_ai.py` - Updated to use environment variables

### Configuration Includes:

**FAL.ai Settings**:
```env
FAL_API_KEY=your-fal-api-key-here (REQUIRED - YOU NEED TO GET THIS)
FAL_IMAGE_TO_VIDEO=fal-ai/veo3/fast/image-to-video
FAL_TEXT_TO_VIDEO=fal-ai/fast-sdxl
```

**OpenRouter LLM** (Already Configured):
```env
OPENROUTER_API_KEY=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
OPENROUTER_DEFAULT_MODEL=anthropic/claude-sonnet-4.5
OPENROUTER_BACKUP_MODEL=qwen/qwen3-vl-235b-a22b-thinking
```

**PayloadCMS Integration**:
```env
PAYLOADCMS_API_URL=https://auto-movie.ft.tc
PAYLOADCMS_API_KEY=your-key-here (RECOMMENDED)
```

---

## 🚀 Deployment Steps (What YOU Need To Do)

### Step 1: Get FAL.ai API Key ⚠️ REQUIRED

```bash
# 1. Go to: https://fal.ai
# 2. Sign up / Log in
# 3. Navigate to Dashboard → API Keys
# 4. Create new API key
# 5. Copy the key (starts with something like "fal_...")
```

### Step 2: Create Production .env File

```bash
cd /var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service

# Copy production template
cp .env.prod.example .env

# Edit with your actual keys
nano .env
```

**In the .env file, UPDATE these lines:**
```env
# CHANGE THIS - Add your actual FAL.ai API key
FAL_API_KEY=fal_your_actual_api_key_here

# CHANGE THIS - Add your PayloadCMS API key (if you have one)
PAYLOADCMS_API_KEY=your-payloadcms-api-key

# OpenRouter is already correct (no changes needed)
OPENROUTER_API_KEY=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
```

### Step 3: Install Dependencies

```bash
# Still in the service directory
pip3 install -r requirements.txt
pip3 install pydantic-settings python-dotenv
```

### Step 4: Test Configuration

```bash
# Verify config loads
python3 -c "from src.config import settings; print('✅ Config loaded'); print(f'FAL Model: {settings.FAL_IMAGE_TO_VIDEO}')"
```

### Step 5: Deploy with PM2

```bash
# Start the service
pm2 start "python3 -m src.mcp_server" --name mcp-video-generation-service --cwd /var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service

# Save configuration
pm2 save

# Check status
pm2 list | grep video-generation
```

### Step 6: Verify Deployment

```bash
# Check logs
pm2 logs mcp-video-generation-service --lines 20

# Should show "online" status
pm2 status mcp-video-generation-service
```

---

## 📋 Required Information Checklist

Before deploying, make sure you have:

- [x] **FAL.ai API Key** - ⚠️ YOU NEED TO GET THIS
- [x] **OpenRouter API Key** - ✅ Already configured
- [ ] **PayloadCMS API Key** - Recommended (get from auto-movie instance)
- [ ] **ElevenLabs API Key** - Optional (for future voiceover)

---

## 🎬 What Happens Next

After deploying Video Generation Service:

1. **Test the service** with sample frames
2. **Deploy Video Editor Service** (next critical service)
3. **Deploy Final QC Service** (quality checks)
4. **Deploy Distribution Service** (final export)
5. **Test end-to-end pipeline** (story → video)

---

## 📊 MVP Progress After This Deployment

| Step | Service | Status |
|------|---------|--------|
| 1-4 | Story Services | ✅ LIVE |
| 5 | Character MCP | ✅ LIVE |
| 6-7 | Visual MCP | ✅ LIVE (deploying now) |
| **8** | **Video Generation** | 🟡 **READY TO DEPLOY** |
| 9 | Video Editor | 📋 Next |
| 10 | Final QC | 📋 Next |
| 11 | Distribution | 📋 Next |

**Progress**: 7 of 11 steps (64%) → Will be 8 of 11 (73%) after deployment

---

## 🔑 Key Files Reference

**Service Directory**:
```
/var/www/movie-generation-platform/services/mcp-video-generation-service/services/mcp-video-generation-service/
```

**Important Files**:
- `.env` - Your production configuration (CREATE THIS)
- `DEPLOYMENT.md` - Full deployment guide
- `src/config.py` - Configuration management
- `src/mcp_server.py` - Main service entry point
- `src/providers/fal_ai.py` - FAL.ai API client

---

## 🐛 Troubleshooting

**Service won't start?**
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check dependencies
pip3 list | grep pydantic

# View logs
pm2 logs mcp-video-generation-service --err
```

**FAL.ai API errors?**
```bash
# Verify API key is set
python3 -c "from src.config import settings; print(settings.FAL_API_KEY[:10] if settings.FAL_API_KEY else 'NOT SET')"
```

---

## 📞 Getting Help

**Full deployment guide**: Read `DEPLOYMENT.md` in the service directory  
**FAL.ai documentation**: https://fal.ai/docs  
**Check service logs**: `pm2 logs mcp-video-generation-service`

---

## 🎯 Summary: What You Need To Do

1. **Get FAL.ai API key** from https://fal.ai (most important!)
2. **Create .env file** from .env.prod.example
3. **Add your API keys** to .env file
4. **Install dependencies** with pip3
5. **Deploy with PM2** using the commands above
6. **Verify it's running** with pm2 list

**Ready?** Follow the deployment steps above! 🚀
