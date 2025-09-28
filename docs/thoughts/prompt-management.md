# Prompt Management & Testing System — Implementation Spec

## 1) Overview & Goals
At almost every stage there is a prompt involved. We need a central place to manage, test, and execute those prompts across the platform.
- Scope: applies to all apps and standalone services.
- Host: primary UI and backend live in the main app (auto-movie), which already uses PayloadCMS.
- Central comms: other services (in services/ as MCP servers/services) will call REST endpoints on auto-movie.
- Out of scope (for now): auth/roles, metrics, retries/fallbacks, env-driven model discovery.

## 2) Architecture
- UI: PayloadCMS local API within auto-movie (admin-like screens following auto-movie design).
- REST API: Exposed by auto-movie for services to fetch templates and trigger executions.
- Execution: Happens in auto-movie backend. No internal workflow engine for “testing” — just prompt → LLM execution → result display.
- Future hooks: We may add PayloadCMS hooks later (e.g., for processing outputs), but not now.

## 3) Collections (Storage)
Two central collections in PayloadCMS:
- promptTemplates (versioned)
- promptsExecuted (not versioned), for audit

### 3.1 promptTemplates (versioned)
Minimum fields:
- name (string, required)
- app (string, required; e.g., "auto-movie"; supports other apps)
- feature (string, optional)
- stage (string, required)
- tags (array<string>, optional) — see Tagging rules below
- template (text, required) — the actual template with placeholders like {{variableName}}
- variableDefs (array<object>, required) — each item: { name, type, required, description, defaultValue }
  - type ∈ [string, number, boolean, json, text, url]
- outputSchema (json, optional) — documentation-only for now
- model (select with fixed options, string, required) — selected from a fixed set of seeded options (see §6)
- notes (text, optional)
- timestamps/owners (auto by PayloadCMS)
Indexes suggested: app+stage, tags, name.

### 3.2 promptsExecuted (not versioned)
Minimum fields:
- templateId (relation → promptTemplates, optional for ad-hoc tests)
- app (string, required)
- feature (string, optional)
- stage (string, required)
- projectId (string, optional)
- tagsSnapshot (array<string>, optional) — tags at the time of execution
- inputs (json, required) — variable values used for interpolation
- resolvedPrompt (text, required) — prompt after variable interpolation
- model (string, required)
- status (string enum: success | error, required)
- outputRaw (json or text, optional)
- errorMessage (text, optional)
- startedAt / finishedAt (datetime)
- notes (text, optional)
Indexes suggested: app+stage+feature, projectId, status, createdAt.

## 4) Tagging & Execution Order
- Tag format: alphabeticPrefix-numericOrder, e.g., mainReference-001, mainReference-002.
- Group tag: the alphabetic prefix before the hyphen (e.g., mainReference).
- Group execution order: sort ascending by numeric segment and execute sequentially.
- Multiple tags allowed per template.
- For now, no automatic chaining between prompts; the UI supports executing items sequentially and viewing outputs. Future hooks can enable chaining.

## 5) UI Requirements (auto-movie)
- Design/Layout: follow auto-movie; main menu + sidebar + content area.
- Screens:
  1) Templates List
     - Filters: app, stage, feature, tag group, free-text search (name, notes)
     - Actions: view, edit, duplicate, delete, Test
  2) Template Detail
     - Fields: name, app, stage, feature, tags[], model, notes, template text, variableDefs[], outputSchema
     - Tabs: Details | Test | Versions (PayloadCMS versions)
  3) Test (per-template)
     - Auto-generated form from variableDefs (required flags, basic type checks)
     - Execute button triggers prompt → model
     - Show resolved prompt and raw response
     - Actions on success: Save Execution (to promptsExecuted), optionally Save as Template (for ad-hoc tests)
  4) Executions List
     - Filters: app, stage, feature, projectId, tags, status, date range
     - Columns: status, model, createdAt, template name/id, projectId
     - Row click → Execution Detail
  5) Execution Detail
     - Show inputs, resolvedPrompt, status, outputRaw or errorMessage, timestamps, notes

## 6) LLM Models (seeded options; no env coupling)
Use a fixed set of selectable model options (can be stored as constants or a simple config):
- OPENROUTER_DEFAULT_MODEL = anthropic/claude-sonnet-4
- OPENROUTER_BACKUP_MODEL = qwen/qwen3-vl-235b-a22b-thinking
- FAL_TEXT_TO_IMAGE_MODEL = fal-ai/nano-banana
- FAL_IMAGE_TO_IMAGE_MODEL = fal-ai/nano-banana/edit

The promptTemplates.model field is a select with these values. We can expand later.

## 7) REST API (auto-movie)
- GET /api/prompt-templates
  - Query: app, stage, feature, tagGroup, search
  - Returns: list of templates (optionally ordered if tagGroup provided)
- GET /api/prompt-templates/:id
- GET /api/tags/:group/templates
  - Returns templates whose tags match group prefix, ordered by numeric suffix
- POST /api/prompts/execute
  - Body: { templateId?: string, inlineTemplate?: string, variableDefs?: [...], inputs: {...}, model?: string, app: string, stage: string, feature?: string, projectId?: string }
  - Behaviors:
    - If templateId present: load template; ignore inlineTemplate/variableDefs
    - Resolve variables → resolvedPrompt; route to provider by model; store promptsExecuted
    - No retry/fallback; on error store promptsExecuted with status=error
  - Response: promptsExecuted record
- GET /api/prompts/:id
- GET /api/prompts
  - Query: app, stage, feature, projectId, status, date range, search

Note: Services call these endpoints; execution occurs inside auto-movie backend.

## 8) Execution Engine (behavior)
- Variable interpolation: replace {{variableName}} with inputs[variableName].
- Validation: enforce required variables; simple type checks per variableDefs.type.
- Provider routing:
  - OPENROUTER_* → OpenRouter text/vl models
  - FAL_* → FAL endpoints (text-to-image / image-to-image)
- Persistence: always write a promptsExecuted record with inputs, resolvedPrompt, model, status, and output/error.
- Error handling: no retry/fallback; return the best error message and mark status=error.
- Output handling: store raw provider response in outputRaw. Any advanced processing will be added later via hooks.

## 9) Tag Group Utilities in UI
- “Run Tag Group” tool:
  - Input: tagGroup (e.g., mainReference) and optional projectId.
  - Fetch ordered templates; present a stepper UI to run one-by-one, showing outputs.
  - Allow writing notes per step; each execution saved in promptsExecuted.
  - No automatic output-to-input piping in v1.

## 10) Versioning & Notes
- promptTemplates: PayloadCMS built-in versioning enabled.
- promptsExecuted: not versioned.
- Both collections include a notes field for human annotations; no metrics/analytics yet.

## 11) Security & Access (v1)
- No auth/role system in v1. Add later as a future enhancement.

## 12) Non-Goals (explicit)
- No retries, no fallback models, no mock data, no legacy compatibility.
- No metrics/cost tracking in v1.
- No dynamic model discovery from env; use seeded list.

## 13) Minimal Schema Hints (PayloadCMS)
Variable def item shape (conceptual):
```ts
{ name: string; type: 'string'|'number'|'boolean'|'json'|'text'|'imageUrl'; required: boolean; description?: string; default?: any }
```
Tag format (regex idea):
```txt
^([A-Za-z]+)-(\d{3,})$
```

## 14) Implementation Notes & Next Steps
- Create/enable the two collections with the fields above in auto-movie PayloadCMS config. **DONE**
- Build the five UI screens and the “Run Tag Group” utility.
- Implement provider adapters for OpenRouter and FAL based on selected model.
- Expose the REST endpoints in auto-movie and wire them to the execution engine.
- Seed the model select options with the four values listed in §6.

Documentation for providers: openrouter.ai, fal.ai (refer to their SDK/REST docs for request/response shapes).