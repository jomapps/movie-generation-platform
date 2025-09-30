# Domain-configs.md Update Summary

**Date:** January 30, 2025  
**Updated File:** `/docs/Domain-configs.md`

## Changes Made

### 1. Added Protocol Classification Section

**New Section:** "Service Communication Protocols"

Clarifies two types of services:
- **HTTP/WebSocket Services** - Have public URLs, listen on ports
- **stdio-based MCP Services** - No public URLs, spawned processes only

### 2. Updated All Service Entries with Status

Every service now shows:
- ✅ **LIVE** - Currently running in production
- 📋 **PLANNED** - Not yet deployed

### 3. Added Protocol Information

Each service entry now includes:
- **Protocol type** (HTTP, WebSocket, stdio MCP)
- **Current status** (Running/Not deployed)
- **PM2 process name** (for running services)

### 4. Story Service Entry - Major Update

**Before:**
```markdown
#### Story MCP Server
- **Local**: `localhost:8010`
- **Dev**: `story.ngrok.pro`
- **Prod**: `story.ft.tc`
- **Purpose**: Create the story related agent
```

**After:**
```markdown
#### Story MCP Server ✅ LIVE
- **Protocol**: ⚠️ stdio-based MCP (NO public URL/port)
- **Local**: Spawned via `python -m src.mcp.server` (no port)
- **Dev**: N/A (stdio only)
- **Prod**: N/A (stdio only)
- **Status**: ✅ Running (PM2: mcp-story-service)
- **Purpose**: Story structure analysis, plot thread tracking, consistency validation
- **Access**: Via MCP stdio protocol (spawned by orchestrator)
- **Note**: This service does NOT listen on port 8010. Port reserved for future HTTP wrapper if needed.
```

### 5. Updated Port Allocation Summary

**Before:** Simple list of ports
**After:** Two categories with status indicators

```bash
✅ Currently Running Services
- Includes actual port usage
- Shows stdio services with "N/A" for port

📋 Reserved Ports (Not Yet Deployed)
- Shows planned services
- Clarifies which are optional
```

**Added Important Notes:**
- Port 8010 reserved but unused (Story Service uses stdio)
- Redis DB allocation (db 0: brain, db 1: story)
- stdio services don't need ports

### 6. Added Current Platform Status Section

New comprehensive status table:

| Service | Type | Port | Protocol | PM2 Name | Status |
|---------|------|------|----------|----------|--------|
| Auto-Movie App | Frontend | 3010 | HTTP/WebSocket | auto-movie | ✅ Online |
| Celery API | Task Queue | 8001 | HTTP REST | celery-api | ✅ Online |
| Celery Worker | Background | - | Internal | celery-worker | ✅ Online |
| Brain Service | Knowledge | 8002 | HTTP + WS | brain-api | ✅ Online |
| Orchestrator | Coordination | 8003 | HTTP REST | agents-api | ✅ Online |
| Story Service | Story Analysis | N/A | stdio MCP | mcp-story-service | ✅ Online |

### 7. Added Deployment Progress Tracking

Shows current completion status:
- **Core Platform:** ✅ 100% Complete
- **MCP Services:** 🔄 20% Complete (1 of 5)
- **MVP Pipeline:** 🔄 30% Complete

### 8. Added Next Priority Services

Clear list of what should be deployed next:
1. Character Service (port 8011)
2. Visual Service (port 8012)
3. Story Bible Service (port 8015)

### 9. Fixed Domain Conflicts

**Audio Service domain corrected:**
- Old: `story-architect.ft.tc` (conflicted)
- New: `audio.ft.tc` with warning note

### 10. Added Related Documentation Links

Links to:
- Fast-Pace Development guide
- Story Service deployment guide
- Platform secrets documentation

## Key Takeaways

### For Developers

1. **Check Protocol First** - Know if service uses HTTP or stdio
2. **Port 8010 is Reserved** - Story Service doesn't actually use it
3. **stdio Services** - Cannot be accessed via curl/browser
4. **PM2 Names** - Use correct names for service management

### For Deployment

1. **5 HTTP Services** - Have public URLs, need nginx/domain setup
2. **1 stdio Service** - Runs via PM2, no URL needed
3. **Next Priority** - Character → Visual → Story Bible

### For Integration

1. **Story Service** - Access via MCP protocol (spawn process)
2. **Other Services** - Access via HTTP/WebSocket
3. **Redis DBs** - Separate databases for different services

## Documentation Consistency

This update ensures:
- ✅ Accurate reflection of deployed services
- ✅ Clear distinction between protocols
- ✅ Correct port usage information
- ✅ Deployment status transparency
- ✅ Priority guidance for next steps

## Files That Reference This

These files should be consistent with Domain-configs.md:
- ✅ `/docs/fast-pace-development.md` - Already consistent
- ✅ `/services/mcp-story-service/DEPLOY.md` - Already explains stdio
- ⚠️ `/docs/platform-secrets-and-startup.md` - May need review for stdio services
- ⚠️ Service-specific READMEs - Should reference stdio where applicable

## Future Considerations

### If Deciding to Add HTTP Wrapper to Story Service

Current setup allows flexibility:
1. **Port 8010 is reserved** - Can add HTTP server later
2. **stdio still works** - No breaking changes needed
3. **Both protocols possible** - Could support both simultaneously

### Pattern for Future MCP Services

This update establishes a pattern for documenting:
- Protocol type clearly stated
- No misleading port/URL info for stdio services
- Clear access method documentation
- Status indicators for deployment tracking

---

**Updated by:** Droid AI Agent  
**Date:** January 30, 2025  
**Version:** 2.0 (stdio-aware)
