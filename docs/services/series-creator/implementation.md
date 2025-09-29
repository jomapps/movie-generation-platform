# Series Creator Agent Implementation

**Last Updated**: 2025-09-29  
**Status**: Draft Implementation Plan

## Overview
- Implements the Story MCP tool responsible for transforming user-submitted ideas into structured concept briefs consumed by downstream narrative services.
- Generates concise briefs (<250 words) capturing title, logline, genre/tone taxonomies, core conflict, and optional positioning notes.
- Stores canonical data (prompt templates, taxonomy definitions, generated briefs) in PayloadCMS collections to ensure consistency and auditability.

## System Responsibilities
1. Accept raw `user_idea` text plus optional `context`, validate inputs, and normalize whitespace for prompt assembly.
2. Retrieve prompt templates, taxonomy vocabularies, and model credentials from PayloadCMS-managed configuration.
3. Invoke configured LLM provider (default GPT-4o mini or environment override) using structured prompts seeded for deterministic behavior.
4. Parse LLM responses into strict JSON schema; retry once on validation failure before surfacing a descriptive error.
5. Persist generated brief, validation notes, and associated metadata in PayloadCMS collections for downstream reference.
6. Return `concept_brief` (or error) to orchestrator; reject requests lacking critical fields (e.g., core conflict) with failure status.

## Data Contracts
### Request Payload
```json
{
  "user_idea": "string",
  "context": {
    "franchise": "string",
    "creative_constraints": ["string"],
    "target_rating": "string",
    "prior_iterations": ["string"]
  }
}
```

### Response Payload
```json
{
  "concept_brief": {
    "title": "string",
    "logline": "string",
    "genre_tags": ["string"],
    "tone_keywords": ["string"],
    "core_conflict": "string",
    "audience_promise": "string",
    "success_criteria": ["string"]
  },
  "validation_notes": ["string"],
  "taxonomy_refs": {
    "genre_tags_collection_id": "string",
    "tone_keywords_collection_id": "string"
  }
}
```

### PayloadCMS Collections
- `seriesPromptTemplates`: `{ id, name, version, template_text, model_hint, updated_at }`
- `seriesTaxonomies`: `{ id, type, values[], locale, updated_at }`
- `seriesConceptBriefs`: `{ id, project_id, user_idea, context, concept_brief, validation_notes[], model_used, seed, created_at }`
- `seriesLLMConfigs`: `{ id, provider, model, credentials_ref, rate_limit, enabled }`

## Processing Pipeline
1. **Input Validation**
   - Verify `user_idea` non-empty; ensure context fields conform to schema.
   - Reject requests with missing critical context required by guardrails (none in MVP).
2. **Configuration Fetch**
   - Load active prompt template (`seriesPromptTemplates` latest version tagged `primary`).
   - Fetch taxonomy sets for `genre_tags` and `tone_keywords`; create baseline entries if absent.
   - Determine LLM provider/model from `seriesLLMConfigs` (fallback to env defaults) and fetch credentials.
3. **Prompt Assembly**
   - Construct prompt with sections: user idea, context details, required output schema, taxonomy guidance, length constraints.
   - Inject deterministic seed (e.g., hashed combination of `user_idea` + project ID) for reproducibility.
4. **LLM Invocation**
   - Call configured provider with JSON schema enforcement (e.g., OpenAI response format) and 12s timeout.
   - On validation failure, retry once with augmented instructions referencing failure reason.
5. **Schema Validation**
   - Parse returned JSON via Pydantic (or equivalent) ensuring required fields present and taxonomy values exist in registered lists.
   - If core conflict missing or empty, treat as fatal error and return failure response.
6. **Persistence**
   - Store finalized concept brief, validation notes, seed, and prompt reference in `seriesConceptBriefs` collection.
   - Optionally record LLM usage metrics (token counts) for observability.
7. **Response Assembly**
   - Return normalized brief with taxonomy references, trimmed strings, and arrays limited to 3 entries.
   - Include `validation_notes` when optional fields omitted or heuristics triggered (e.g., short logline).

## Taxonomy Management
- `seriesTaxonomies` collection supports types `genre_tags` and `tone_keywords` with curated values.
- During generation, map LLM outputs to nearest taxonomy entries (case-insensitive); if missing, append new entries only when aligned with editorial policy.
- Provide references (IDs) in response to help downstream services maintain canonical mapping.

## LLM Provider Configuration
- Default environment variables:
  - `FAL_TEXT_TO_IMAGE_MODEL`, `FAL_IMAGE_TO_IMAGE_MODEL` for future multimodal prompts (document for completeness).
  - `FAL_IMAGE_TO_VIDEO`, `FAL_TEXT_TO_VIDEO`, `ELEVENLABS_API_KEY` stored in PayloadCMS if needed by series-level planning (not used in MVP text generation but documented for future expansion).
- `seriesLLMConfigs` defines provider credentials (OpenAI API key, model names). Credentials referenced via secrets manager integration or PayloadCMS secure fields.
- Support English-only outputs in MVP; enforce via prompt instructions.

## Error Handling & Validation Notes
- Fatal errors (missing core conflict, schema parse failure after retry) return MCP error with `validation_notes` describing cause.
- Non-fatal notes (e.g., inability to infer audience promise) appear in `validation_notes` array and output still marked successful.
- Ensure logs omit sensitive user context; store raw idea only within PayloadCMS secured collection.

## Observability & Metrics
- Emit counters:
  - `series_creator.success_rate`
  - `series_creator.validation_failures`
  - `series_creator.latency_ms` (P50/P95)
- Capture model usage metrics (tokens, retries) for ops dashboards.
- Persist deterministic seed usage to aid replication of briefs.

## Testing Strategy
- **Unit Tests**: Prompt assembly, taxonomy mapping, schema validation, deterministic seed hashing.
- **Integration Tests**: LLM call plumbing, PayloadCMS config retrieval, persistence of concept briefs.
- **Smoke Tests**: Daily run against curated set of sample ideas to ensure prompt stability.

## Future Enhancements
- Introduce multi-language support by extending taxonomy collections with locale metadata.
- Add revision management (versioning briefs per idea) and tie into UI workflows.
- Integrate with Brain/Story Bible services for canonical franchise constraints.
- Support alternative LLM providers (Anthropic, local models) through additional config entries.
