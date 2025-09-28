# Movie Generation Platform - Documentation Structure

**SINGLE SOURCE OF TRUTH** - This document defines the complete documentation organization for the platform.

## 🎯 Documentation Philosophy

- **ONE PLACE FOR EVERYTHING**: All authoritative information lives in `/docs/` folder
- **SMALL, TARGETED FILES**: Each file serves a specific purpose and audience
- **NO DUPLICATION**: Information appears in only one place
- **CLEAR HIERARCHY**: Logical organization from overview to implementation details
- **ALWAYS CURRENT**: Documentation maintained with code changes

## 📁 Documentation Hierarchy

```
docs/
├── PROJECT_OVERVIEW.md          ← What is this project? Goals? Current status?
├── ARCHITECTURE.md              ← Technical architecture and design decisions
├── AI_AGENT_SYSTEM.md          ← 50+ AI agents and production workflows
├── DEVELOPMENT_STATUS.md        ← What's built, what's in progress, what's next
├── SETUP_GUIDE.md              ← How to get everything running locally
├── PRODUCTION_ENDPOINTS.md      ← **NEW** ✅ Live production services and endpoints
├── JINA_V4_INTEGRATION.md      ← **NEW** ✅ Complete Jina v4 architecture transformation
├── API_REFERENCE.md            ← Complete API and MCP tools documentation
├── DEPLOYMENT_GUIDE.md         ← Production deployment and configuration
├── TROUBLESHOOTING.md          ← Common problems and solutions
├── DEVELOPMENT_WORKFLOW.md     ← Development processes and standards
├── CLARIFICATIONS.md           ← Items needing clarification
├── thoughts/                   ← Design specifications and planning
│   ├── movie-platform-idea.md ← Complete 50+ agent system specification
│   ├── prompt-management.md   ← AI prompt system implementation spec
│   ├── Domain-configs.md      ← Service ports and domain configuration
│   ├── system-architecture-diagram.md ← Visual system architecture
│   └── mono-repo-structure.md ← Pattern library and tooling recommendations
└── legacy/                     ← Archive of old docs (to be deleted)
    ├── auto-movie-feature-list.md
    ├── generic-to-be-done.md
    ├── llms-and-their-usage.md
    └── monorepo-reference.md
```

## 📋 File Purposes

### Core Documentation (Essential Reading)

| File | Audience | Purpose | Contents |
|------|----------|---------|-----------|
| `PROJECT_OVERVIEW.md` | Everyone | Project understanding | 50+ AI agent system vision, goals, current status |
| `ARCHITECTURE.md` | Developers | Technical design | MCP brain service pattern, service connections, data flow |
| `AI_AGENT_SYSTEM.md` | Developers/Stakeholders | Agent system design | 50+ specialized AI agents, workflows, coordination |
| `DEVELOPMENT_STATUS.md` | All stakeholders | Progress tracking | Implementation status, roadmap, Phase 3 agent system |
| `SETUP_GUIDE.md` | Developers | Getting started | Step-by-step local development setup |
| `PRODUCTION_ENDPOINTS.md` | All users | Production services | Live endpoints, status, configuration examples |
| `JINA_V4_INTEGRATION.md` | Developers/Stakeholders | Architecture status | Complete transformation documentation, all phases |

### Reference Documentation (As-Needed)

| File | Audience | Purpose | Contents |
|------|----------|---------|-----------|
| `API_REFERENCE.md` | Developers | API usage | MCP tools, REST endpoints, request/response formats |
| `DEPLOYMENT_GUIDE.md` | DevOps/Admins | Production setup | Environment variables, service configuration, deployment |
| `TROUBLESHOOTING.md` | All users | Problem solving | Common issues, error messages, solutions |
| `DEVELOPMENT_WORKFLOW.md` | Contributors | Process guidance | Testing, coding standards, contribution process |

### Administrative

| File | Audience | Purpose | Contents |
|------|----------|---------|-----------|
| `CLARIFICATIONS.md` | Project team | Gap identification | Missing/unclear information that needs resolution |

## 🎯 Information Flow

```
ROOT README.md
    ↓ (Brief overview + navigation)
PROJECT_OVERVIEW.md
    ↓ (What & why)
ARCHITECTURE.md
    ↓ (How it's built)
DEVELOPMENT_STATUS.md
    ↓ (Current state)
SETUP_GUIDE.md
    ↓ (How to start)
[Other reference docs as needed]
```

## ✅ Content Verification Rules

Each documentation file must:

1. **Have a single, clear purpose** - No overlap with other files
2. **Be maintained with code** - Updated when implementations change
3. **Include verification date** - "Last verified: [date]" at top
4. **Link to related docs** - Clear navigation between files
5. **Use consistent format** - Follow established patterns

## 🗑️ Files to Archive/Delete

Once new structure is complete, these will be moved to `docs/legacy/` and then deleted:

- `docs/auto-movie-feature-list.md` → Information moved to DEVELOPMENT_STATUS.md
- `docs/generic-to-be-done.md` → Implementation plan moved to DEVELOPMENT_STATUS.md  
- `docs/llms-and-their-usage.md` → LLM configuration moved to DEPLOYMENT_GUIDE.md
- `docs/monorepo-reference.md` → Information distributed across new structure
- Root level: `AGENTS.md`, `CLAUDE.md`, `WARP.md` → Tool-specific, move to separate config folder

## 📝 Maintenance Process

1. **Before any code changes**: Check if documentation needs updates
2. **After implementation**: Update relevant documentation files
3. **Monthly review**: Verify all information is current and accurate
4. **Version control**: Document changes in git commits

## 🚀 Implementation Status

- [x] Documentation structure defined
- [x] Core files created (PROJECT_OVERVIEW, ARCHITECTURE, AI_AGENT_SYSTEM, DEVELOPMENT_STATUS, SETUP_GUIDE, CLARIFICATIONS)
- [x] Information integrated from thoughts/ folder (50+ agent system discovered)
- [x] Root README updated with new vision
- [x] Comprehensive system architecture documented
- [ ] API_REFERENCE.md created
- [ ] DEPLOYMENT_GUIDE.md created
- [ ] TROUBLESHOOTING.md created
- [ ] DEVELOPMENT_WORKFLOW.md created
- [ ] Legacy files archived
- [ ] Team review completed
- [ ] Old documentation deleted

---

**Last Updated**: 2025-01-28
**Maintained By**: Project team
**Review Cycle**: Monthly or when major changes occur