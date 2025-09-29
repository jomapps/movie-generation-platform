# Clarification Questions

1. How should we determine the number of shots per scene—do we have pacing heuristics (e.g., max 2 shots per scene) or should the agent infer based on goal complexity and runtime targets? agent infers. we have max 7s video segments. keep that in mind.
2. Are there standardized vocabularies for `camera_notes`, `lighting_mood`, and `prompt_seed` formatting that upstream/downstream systems expect?
none. you can create a library in the payloadcms. But do not restrict new entries.
3. When character profiles and scene descriptions conflict (e.g., wardrobe or props), which source of truth should the agent follow, and should discrepancies be surfaced via `continuity_notes`? scene description takes precedence.
4. Do we need to support genre-specific style presets (anime, live-action) at MVP, and how are those presets defined and delivered to the agent? no
5. What is the desired fallback when the agent cannot confidently describe a frame—return fewer frames, insert placeholder text, or flag the scene for manual review? stop. give error with reason and wait for the user to fix.
6. Should the agent output any timing metadata (approximate frame duration) to help Video Generation with pacing, or is textual sequencing sufficient?
yes
7. How are storyboard outputs stored or versioned—does the orchestrator handle persistence, or must the agent write artifacts to a shared repository/storage location?
no version handling required. it happens in the payloadcms automatically. use the latest.

