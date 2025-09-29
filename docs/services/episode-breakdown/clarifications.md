# Clarification Questions

1. When expanding the story arc into scenes, do we have prescribed heuristics for mapping each arc section to scene counts, or should the agent dynamically decide based on text length and pacing cues? dynamically decide
2. How should the agent validate characters referenced in `scene_list`—is there a shared canonical character registry available at runtime, or must we only rely on names present in the `story_arc` and `concept_brief` payloads? character colleciton in payloadcms, which is the holder of all data. Please ensure that the collection has the fields that you need
3. Are there guardrails for locations (e.g., whitelist, production budget constraints) that we should enforce programmatically when applying the “1–2 locations” heuristic? No
4. What should happen when more than five scenes are required to cover all beats—do we merge beats, drop lower-priority beats, or return a warning for human intervention? human intervention
5. Do we need to track rationale for each `visual_hook` so downstream agents understand why a particular motif was chosen, or is the short string sufficient? yes
6. How deterministic should the output be—do we have a shared seeding strategy with other agents to guarantee reproducibility across retries? yes. appropriate field in a colleciton in payloadcms. create if not present
7. Where should `continuity_flags` be logged or surfaced so that subsequent agents (and the UI) can react appropriately—does the orchestrator already have a workflow for them? yes. appropriate field in a colleciton in payloadcms. create if not present
