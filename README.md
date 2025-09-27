Movie Generation Platform Monorepo

This repository aggregates multiple standalone services and apps into a single monorepo while keeping each as its own Git repository via submodules. This preserves clean separation and ownership while enabling end-to-end workflows, shared docs, and cross-repo coordination.

Structure

```
.
├── apps/
│   └── auto-movie/                # submodule
├── services/
│   ├── mcp-story-service/         # submodule
│   ├── mcp-character-service/     # submodule
│   ├── mcp-brain-service/         # submodule
│   ├── langgraph-orchestrator/    # submodule
│   └── celery-redis/              # submodule
├── docs/
│   └── thoughts/
├── scripts/
│   ├── add-submodules.ps1         # PowerShell helper (Windows recommended)
│   └── add-submodules.sh          # Bash helper (requires jq)
└── repo-map.json                  # Configure submodule URLs and paths
```

Add the external repositories

Option A — PowerShell (recommended on Windows):

```powershell
# 1) Edit repo-map.json and fill in each "url"
# 2) Run the helper script (PowerShell 7+ or Windows PowerShell)
powershell -ExecutionPolicy Bypass -File scripts/add-submodules.ps1
# or
pwsh scripts/add-submodules.ps1
```

Option B — Bash (requires jq):

```bash
# 1) Edit repo-map.json and fill in each "url"
# 2) Run the helper script
bash scripts/add-submodules.sh
```

Option C — Manual (one-by-one):

```bash
git submodule add -b main <URL_FOR_mcp-story-service> services/mcp-story-service
git submodule add -b main <URL_FOR_mcp-character-service> services/mcp-character-service
git submodule add -b main <URL_FOR_mcp-brain-service> services/mcp-brain-service
git submodule add -b main <URL_FOR_langgraph-orchestrator> services/langgraph-orchestrator
git submodule add -b main <URL_FOR_celery-redis> services/celery-redis
git submodule add -b main <URL_FOR_auto-movie> apps/auto-movie

git submodule update --init --recursive
```

Working with submodules

```bash
# Clone this monorepo and initialize submodules
git clone <this-mono-repo-url>
cd movie-generation-platform
git submodule update --init --recursive

# Pull latest changes across all submodules
git submodule foreach --recursive git pull origin $(git rev-parse --abbrev-ref HEAD)

# If you switch branches in the monorepo and want submodules aligned
git submodule sync --recursive
git submodule update --init --recursive
```

Notes

- Each service/app remains a separate Git repository. Commits to submodules should be done inside the submodule directory and pushed to its own origin.
- This monorepo tracks submodule SHAs. Update the SHA by committing submodule pointer changes in the monorepo after pulling in the submodule.
- If you do not have `jq` installed on your Bash environment, prefer the PowerShell script on Windows.


