# Series Creator Agent Specification

**Last Updated**: 2025-09-29  
**Status**: Draft  
**Service Type**: Story MCP Tool (concept seeding)

## Purpose
- Convert a high-level user idea into a structured series concept brief that can seed the rest of the production pipeline.
- Capture genre, tone, primary conflict, and positioning details early to reduce iteration later in the story workflow.

## MVP Scope
- Support a single short-form production (10–30s clip) per request.
- Generate one canonical concept brief per idea; revisions handled manually in UI for v0.
- No persistence beyond returning the brief to the orchestrator/UI (Story MCP stores downstream artifacts).

## Inputs
- `user_idea` (string, required): Free-form description of the concept.
- `context` (optional object): Previous prompts, franchise constraints, or creative guardrails supplied by UI or ops.

## Outputs
- `concept_brief` (object): Structured record used by Story Architect.
  - `title` (string)
  - `logline` (string)
  - `genre_tags` (array[string], 3 max)
  - `tone_keywords` (array[string], 3 max)
  - `core_conflict` (string)
  - `audience_promise` (string, optional)
  - `success_criteria` (array[string], optional)

## Core Responsibilities
1. Normalize user input and extract the creative anchor points for downstream agents.
2. Ensure the concept brief is concise (<250 words) while covering the required output fields.
3. Flag missing information (e.g., no conflict) in a validation note for UI display.

## Workflow
1. Receive event from orchestrator with `user_idea` and optional `context`.
2. Run prompt template against LLM (OpenAI GPT-4o mini or configured default).
3. Parse LLM output into strict JSON schema; re-try once if validation fails.
4. Return structured concept brief to Story MCP orchestrator.

## Interfaces & Contracts
### MCP Tool: `generate_series_concept`
- **Purpose**: Produce the concept brief from a raw idea.
- **Request Schema**
  ```json
  {
    "user_idea": "string",
    "context": {
      "franchise": "string?",
      "creative_constraints": ["string"],
      "target_rating": "string?"
    }
  }
  ```
- **Response Schema**
  ```json
  {
    "concept_brief": {
      "title": "string",
      "logline": "string",
      "genre_tags": ["string"],
      "tone_keywords": ["string"],
      "core_conflict": "string",
      "audience_promise": "string?",
      "success_criteria": ["string"]
    },
    "validation_notes": ["string"]
  }
  ```
- **Error Handling**: Return MCP tool error with `validation_notes` if schema parsing fails twice.

## Dependencies
- **Upstream**: UI / LangGraph orchestrator providing user idea.
- **Downstream**: Story Architect agent consumes `concept_brief` JSON.
- **External Services**: OpenAI (or configured LLM provider) for generation.

## Non-Functional Requirements
- Average latency < 6s per request; hard timeout 12s.
- Ensure deterministic schema formatting with Pydantic validation before returning.
- Log request/response metadata (excluding raw user text when privacy flag set).

## Operational Considerations
- Maintain prompt templates in versioned JSON to allow quick updates.
- Feature flag to switch between different LLM providers without redeploy.
- Observability: expose counters for successful briefs, retries, validation failures.

## Risks & Open Questions
- Handling franchise-specific canon might require Brain Service context (deferred).
- Rate limits from LLM provider during high-volume ideation sessions.
- Future revisions workflow (multi-pass ideation) not covered in MVP.

## Testing Strategy
- **Unit**: Prompt assembly, schema validation, fallback logic.
- **Integration**: LLM call contract, orchestrator request/response path.
- **Smoke**: Daily generation against sample ideas to ensure prompt stability.

## Metrics
- `series_creator.success_rate`
- `series_creator.latency_ms` (P50/P95)
- `series_creator.validation_failures`
