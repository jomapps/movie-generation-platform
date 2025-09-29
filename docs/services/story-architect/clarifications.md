# Clarification Questions

1. Are there predefined guardrails for mapping `tone_keywords` and `genre_tags` into different prompt templates, or do we need to design a selection heuristic from scratch? no
2. How strictly must the agent adhere to the 80-word limits—should we enforce hard truncation, apply soft validation with retries, or allow slightly longer sections when necessary? no hard limits or truncation. allow when necessary
3. What validation rules exist to ensure new characters aren’t introduced—do we compare against a shared character roster, or only the concept brief contents? character roster  in characters collection in payloadcms
4. Should `continuity_flags` include machine-readable codes in addition to human-readable notes to support downstream automation? machine readable codes are necessary. turn human codes into machine codes with llm assistance if required.
5. How do we propagate trace IDs and request metadata through the LLM calls—does the orchestrator supply context headers or logging APIs we must integrate with?
orchestrator supplies context headers in conjunction with the brain service.
6. Is there a requirement to support multi-language concept briefs, and if so should the arc outputs mirror the input language or default to English?
Only English for now.
7. How is prompt versioning handled between Series Creator and Story Architect so both agents stay in sync when templates change? Payloadcms does versioning. you just use what is there now.

