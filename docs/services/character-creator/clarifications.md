# Clarification Questions

1. What is the authoritative source for the canonical character list—should the agent rely solely on the `scene_list` input or is there a shared registry we need to query/update during deduplication?
Good question. Create an extensive character collection in the auto-menu > payloadcms which is hte holder of all data. make only name and project id as required. this way we can query the character, expand the character object as we go.
2. When duplicate or conflicting character names are detected, do we auto-resolve (e.g., append descriptors) or surface a blocking error back to the orchestrator for manual intervention? Yes pls. auto resolve using descriptor. normally between a-z e,g, Eugene, then duplicate will be Eugene A, Eugene B, etc.
3. How should `relationships` and `continuity_notes` be populated when the upstream data lacks explicit guidance—are we expected to infer minimal entries or leave fields empty by default? Create relational fields only if necessary. if lacking guidance write "lacking_guidance" and we will pick this up in ui. we have to stop processing when we meet with "lacking_guidance"
4. Should unresolved or ambiguously named characters halt downstream agents, or simply appear in the `unresolved_references` array for human follow-up? yes. same as lacking_guidance
5. Are there standard prompt templates or tone/style presets we must use when generating visual signatures and motivations, or will these be developed as part of implementation?
Create seed of min prompt templates. You can require certain prompt template names e.g. master_reference
6. How is `context.overrides` expected to arrive (schema, transport, priority rules) so we can design the deferred override hook without rework later? we will rework, since there is no current mechanism for this.
7. Do we need to version the archetype dictionary used for genre-specific prompts, and if so where will that configuration live (code repo vs. external config service)? Not necessary.
