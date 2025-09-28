# mcp-3d-asset-service

## Service overview and purpose
Handles ingest, catalog, and basic conversions for 3D assets (models, textures, animations) to support concept previews and future 3D shots.

## Technical requirements and dependencies
- Language: Python 3.11+
- FastAPI service exposing HTTP + MCP tools
- Converters: Assimp/Blender CLI for format inspection/preview render (optional phase)
- Storage: PayloadCMS Media; large object store for heavy assets

## API endpoints and interfaces
- HTTP:
  - POST `/assets/ingest` { files[], tags[] } → assetIds
  - GET `/assets/{id}` → metadata
  - POST `/assets/preview` { assetId, camera?, lighting? } → image mediaId
  - GET `/health` → { ok: true }
- MCP tools:
  - `asset3d.ingest`
  - `asset3d.generate_preview`

## Database schema (if applicable)
Store in CMS Media with metadata fields:
- media.ThreeD: { formats[], polycount, materials[], previewIds[] }

## Integration points with PayloadCMS
- Write assets to Media; attach tags and technical metadata
- Link to Projects and scenes for planning

## Step-by-step implementation guide
1. Implement ingest endpoint; validate and upload
2. Optional: metadata extraction via Assimp
3. Optional: preview renders via Blender CLI
4. Expose MCP tools and wire progress events

## Testing strategy
- Unit: metadata parsing
- Integration: ingest + retrieval roundtrip

## Deployment considerations
- Large file handling and timeouts
- Optional GPU for preview renders; storage quotas

