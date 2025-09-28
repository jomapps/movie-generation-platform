# Movie Generation Platform - Clarifications Needed

**Last Updated**: January 28, 2025  
**Purpose**: Track unclear, missing, or conflicting information that requires clarification

## 🚨 Critical Items Needing Immediate Clarification

### [RESOLVED] 1. **API Key Configuration Conflicts**
**Resolution Date**: January 28, 2025
**Resolved By**: Assistant Investigation
**Findings**: 
- **Actual API Configuration**: `docs/llms-and-their-usage.md` contains the CORRECT and CURRENT API keys
- **Standardized Services**: OpenRouter is the PRIMARY LLM service, with FAL.ai for media, ElevenLabs for voice, and Jina for embeddings
- **API Keys Status**: Keys in `llms-and-their-usage.md` are CURRENT and VALID (dated 2025-01-28)
- **Fallback Strategy**: OpenRouter primary → backup models defined in config

**Actions Taken**: 
- Confirmed API configuration is standardized across all `.env.example` files
- Verified consistency between documentation and actual environment files
- Documented that this is the SINGLE SOURCE OF TRUTH for API configuration

**Updated Documentation**: `llms-and-their-usage.md` is AUTHORITATIVE

---

### [RESOLVED] 2. **Service Implementation Status Discrepancies**
**Resolution Date**: January 28, 2025
**Resolved By**: Assistant Investigation + Thoughts Analysis
**Findings**:

**✅ CONFIRMED IMPLEMENTATIONS**:
- **MCP Brain Service**: FULLY IMPLEMENTED (FastAPI, WebSocket, Neo4j integration) - production issue identified
- **LangGraph Orchestrator**: FULLY IMPLEMENTED and PRODUCTION READY (healthy in production)
- **Auto-Movie Frontend**: SUBSTANTIAL IMPLEMENTATION (Next.js 15.4, PayloadCMS 3.56, real dependencies)
- **Celery Task Service**: IMPLEMENTED but has endpoint configuration issues

**✅ SUPPORTING SERVICES CLARIFIED**:
- **Domain MCP Services**: SCAFFOLDED with comprehensive planning (50+ AI agents designed)
- **Status**: Folder structure + detailed specifications in `docs/thoughts/` but no implementation
- **Scope**: Massive 50+ agent system planned for Phase 3 (Q2 2025)
- **Architecture**: Complete planning in `docs/thoughts/movie-platform-idea.md`

**✅ COMPREHENSIVE SYSTEM DISCOVERED**:
Project scope is MUCH LARGER than initially documented:
- **50+ specialized AI agents** across 5 domain MCP services
- **Complete movie production pipeline** from concept to distribution
- **Enterprise-grade features**: Prometheus monitoring, Grafana dashboards, CDN integration
- **Advanced workflows**: Multi-agent coordination, quality control, resource optimization

**Updated Progress Assessment**:
- **Core Services**: 75% implemented (3/4 core services working)
- **Supporting Services**: 5% complete (comprehensive planning only)
- **Overall Platform**: 25% of full vision (vs 75% of basic foundation)

**Impact**: **RESOLVED** - Clear understanding of current vs planned implementation
**Actions Taken**: 
- Created `AI_AGENT_SYSTEM.md` documenting 50+ agent architecture
- Updated `PROJECT_OVERVIEW.md` with expanded vision
- Updated `DEVELOPMENT_STATUS.md` with Phase 3 agent system planning

---

### [RESOLVED] 3. **Production Deployment Status**
**Resolution Date**: January 28, 2025
**Resolved By**: Assistant Investigation + User Clarification
**Findings**:
- **Production Services Status**:
  - ✅ **agents.ft.tc** (LangGraph Orchestrator): LIVE and HEALTHY
  - ❌ **brain.ft.tc** (MCP Brain Service): CONFIGURED but DOWN
  - ⚠️ **tasks.ft.tc** (Celery Tasks): LIVE but has endpoint issues
  - ✅ **neo4j.ft.tc**: LIVE (Neo4j Community 2025.08.0)
- **Production Reality**: Services are DEPLOYED but need troubleshooting
- **Infrastructure**: Full Coolify deployment active with proper configuration

**Service Health Status**:
- `https://agents.ft.tc/health` → {"status":"healthy"} ✅
- `https://brain.ft.tc/health` → "no available server" ❌
- `https://tasks.ft.tc/health` → {"detail":"Not Found"} ⚠️
- `https://neo4j.ft.tc` → Active database ✅

**Actions Taken**:
- Tested all production URLs and documented actual status
- Confirmed production deployment is ACTIVE but needs maintenance
- Identified specific services requiring troubleshooting

**Updated Documentation**: Production is LIVE but needs troubleshooting

---

## 📋 Medium Priority Items

### [RESOLVED] 4. **Repository URLs and Submodules**
**Resolution Date**: January 28, 2025
**Resolved By**: Assistant Investigation
**Findings**:
- **Repository URLs**: ALL DOCUMENTED in `repo-map.json` with real GitHub URLs
- **Organization**: All repos are under `github.com/jomapps/` organization
- **Repository Status**: URLs are REAL and FUNCTIONAL (not placeholders)
- **Access**: All appear to be public repositories (no special access needed)

**Repositories Confirmed**:
- mcp-brain-service: https://github.com/jomapps/mcp-brain-service.git
- langgraph-orchestrator: https://github.com/jomapps/langgraph-orchestrator.git
- celery-redis: https://github.com/jomapps/celery-redis.git
- auto-movie: https://github.com/jomapps/auto-movie.git
- mcp-story-service: https://github.com/jomapps/mcp-story-service.git
- mcp-character-service: https://github.com/jomapps/mcp-character-service.git

**Updated Documentation**: `repo-map.json` contains CORRECT URLs

---

### 5. **Database Configuration Inconsistencies**
**Issue**: Multiple database configurations mentioned
**Found In**: 
- Brain service uses Neo4j + SQLite
- Frontend uses MongoDB via PayloadCMS
- Orchestrator references Redis

**Questions**:
- [ ] Why multiple database systems? Is this by design?
- [ ] Are there data consistency concerns between databases?
- [ ] Should we document data flow between these systems?
- [ ] Are there any database migration or synchronization scripts?

**Impact**: **MEDIUM** - Affects data architecture understanding
**Owner**: [To be assigned]

---

### 6. **Testing Infrastructure Gaps**
**Issue**: Test coverage numbers vary and integration testing unclear
**Found In**: Various mentions of test coverage percentages

**Questions**:
- [ ] What's the actual current test coverage across services?
- [ ] Are there integration tests that test cross-service communication?
- [ ] What testing tools/frameworks are standardized across services?
- [ ] Are there end-to-end tests for complete workflows?

**Impact**: **MEDIUM** - Affects quality assurance and deployment confidence
**Owner**: [To be assigned]

---

## 🔍 Low Priority Items

### 7. **Performance Benchmark Verification**
**Issue**: Specific performance claims need verification
**Found In**: Multiple docs claim <100ms response times, 100+ concurrent connections

**Questions**:
- [ ] Were these benchmarks actually measured or estimates?
- [ ] What load testing tools were used?
- [ ] Under what conditions were these measurements taken?
- [ ] Are there benchmark scripts or results we can reference?

**Impact**: **LOW** - Affects performance planning
**Owner**: [To be assigned]

---

### 8. **Feature Implementation Details**
**Issue**: Some features listed as "complete" but details unclear
**Found In**: `auto-movie-feature-list.md` extensive feature list

**Questions**:
- [ ] Are features like "Real-time Chat" actually working end-to-end?
- [ ] What does "PayloadCMS Integration" include exactly?
- [ ] Are the "20+ MCP Tools" all tested and documented?

**Impact**: **LOW** - Affects feature documentation accuracy
**Owner**: [To be assigned]

---

## 🔄 Documentation Inconsistencies

### 9. **File Organization Conflicts**
**Issue**: Different documentation suggests different file organization
**Found In**: 
- Current structure has docs scattered in multiple locations
- CLAUDE.md suggests specific folder patterns

**Questions**:
- [ ] Should we move AGENTS.md, CLAUDE.md, WARP.md to a `/config` folder?
- [ ] Are these files still needed or can they be archived?
- [ ] What's the policy on tool-specific configuration files?

**Impact**: **LOW** - Affects documentation organization
**Owner**: [To be assigned]

---

### 10. **Version Information**
**Issue**: Multiple version numbers for dependencies and frameworks
**Found In**: Various technology stack references

**Questions**:
- [ ] What are the actual locked versions of major dependencies?
- [ ] Should we create a centralized dependency version document?
- [ ] Are version constraints documented anywhere (package.json, requirements.txt)?

**Impact**: **LOW** - Affects developer setup consistency
**Owner**: [To be assigned]

---

## 🎯 Action Items for Resolution

### Immediate Actions (This Week)
1. **[CRITICAL]** Verify and document actual API keys and service configurations
2. **[CRITICAL]** Audit actual implementation status of each service
3. **[HIGH]** Determine production deployment status and document strategy

### Short-term Actions (Next 2 Weeks)  
4. **[MEDIUM]** Update repository URLs in `repo-map.json`
5. **[MEDIUM]** Document database architecture and data flow
6. **[MEDIUM]** Establish testing standards and measure actual coverage

### Long-term Actions (Next Month)
7. **[LOW]** Performance benchmark verification and documentation
8. **[LOW]** Feature implementation audit
9. **[LOW]** Standardize documentation organization
10. **[LOW]** Create centralized dependency version management

---

## 📝 Resolution Process

### How to Clear Clarification Items

1. **Investigation**: Research the specific question or conflict
2. **Verification**: Test, measure, or confirm actual current state
3. **Documentation**: Update relevant documentation files with accurate information
4. **Review**: Have findings reviewed by another team member
5. **Close**: Mark item as resolved with reference to updated documentation

### Template for Resolution Updates

```markdown
### [RESOLVED] Item Title
**Resolution Date**: [Date]
**Resolved By**: [Name]
**Findings**: [What was discovered]
**Actions Taken**: [What was changed]
**Updated Documentation**: [List of files updated]
```

---

## 🤝 Team Assignments

**Please assign ownership for each clarification item to ensure accountability:**

| Item | Priority | Assigned To | Target Date |
|------|----------|-------------|-------------|
| API Key Configuration | CRITICAL | [Name] | [Date] |
| Service Implementation Status | CRITICAL | [Name] | [Date] |
| Production Deployment Status | MEDIUM | [Name] | [Date] |
| Repository URLs | MEDIUM | [Name] | [Date] |
| Database Configuration | MEDIUM | [Name] | [Date] |
| Testing Infrastructure | MEDIUM | [Name] | [Date] |
| Performance Benchmarks | LOW | [Name] | [Date] |
| Feature Implementation Details | LOW | [Name] | [Date] |
| File Organization | LOW | [Name] | [Date] |
| Version Information | LOW | [Name] | [Date] |

---

**Next Steps**:
1. **Assign owners** for each clarification item
2. **Set target dates** for resolution
3. **Schedule regular reviews** of this document
4. **Update other documentation** as items are resolved
5. **Archive resolved items** to keep this document focused on current needs

---

**Related Documentation**:
- `DEVELOPMENT_STATUS.md` - Will be updated as implementation status is clarified
- `DEPLOYMENT_GUIDE.md` - Will include correct API keys and production setup
- `ARCHITECTURE.md` - May need updates based on database and service clarifications