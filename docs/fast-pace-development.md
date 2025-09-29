# Fast‑Pace Development Plan — First Movie Generation (MVP v0)

Last updated: 2025-09-29
Source of truth: docs/AI_AGENT_SYSTEM.md (Primary Production Pipeline, Critical Path) and current docs/ directory.

## Goal
Reach the first end‑to‑end movie generation as fast as possible. We implement only the minimum set of agents strictly required to output a short video (MP4) from a high‑level idea, accepting quality trade‑offs (reduced polish, simplified visuals/audio, minimal QC).

## Principles
- Implement only critical‑path agents; defer everything that mainly improves quality.
- Prefer simple prompts and defaults; avoid complex cross‑agent coordination at v0.
- Produce a single short clip (e.g., 10–30s) as the first milestone.

## Minimal Agent Order (Strict MVP Sequence)
Derived from AI_AGENT_SYSTEM.md → Primary Production Pipeline. Each item shows: Agent (MCP) — Purpose — Key input/output.

1) Series Creator (Story MCP) — Seed concept — input: user idea; output: concept brief
2) Story Architect (Story MCP) — Story arc — input: concept; output: high‑level arc
3) Episode Breakdown (Story MCP) — Beats/scenes — input: arc; output: scene list with 1–3 key beats
4) Character Creator (Character MCP) — Core characters — input: arc + beats; output: minimal character profiles (2–4)
5) Storyboard Artist (Visual MCP) — Rough boards — input: beats + characters; output: 6–12 frame descriptions with camera notes
6) Image Generation (Visual MCP) — Key frames — input: storyboard frames; output: images per frame (use FAL.ai integration)
7) Video Generation (Production) — Short segments — input: images/frames; output: 7–10s video segments (concatenate if needed)
8) Video Editor (Post) — Assembly — input: segments; output: single MP4 clip
9) Final QC (Post) — Basic checks — input: MP4; output: pass/fail + minimal fixes (e.g., black frames)
10) Distribution (Post) — Export — input: final MP4; output: downloadable/rendered artifact

Notes:
- Audio is optional for MVP. If time allows, add simple background music via “Audio Mixer” later (see Next‑Upgrades). Voice/dialogue is deferred.
- Character Designer can be skipped initially by letting prompts describe visuals inline in the storyboard and image prompts.

## Deferred (Quality‑Only) Agents — Not Required for First Output
These improve quality but are not needed to get a first video. Implement after MVP:
- Dialogue Writer, Voice Creator, Voice Director, Audio Mixer, Music Composer, Foley, Voice Matching
- Character Designer, Concept Artist, Environment Designer, Costume Designer, Props Master, Shot Designer
- Compositor, Color Grader, VFX Supervisor, Continuity, Quality Controller, Subtitle/Caption, Marketing Asset
- Script Supervisor, Location Scout, Research, Legal Compliance, Render Farm Coordinator, Version Control, Performance Monitor, Cost Optimizer

## Minimal MCP Services Needed for MVP
- Story MCP (hosts: Series Creator, Story Architect, Episode Breakdown)
- Character MCP (hosts: Character Creator)
- Visual MCP (hosts: Storyboard Artist, Image Generation)
- Video generation step can be a simple utility/integration rather than a full MCP at v0; promote to its own agent/service later.
- Post (Video Editor, Final QC, Distribution) can initially be simple scripts/utilities called by the UI.

## Hand‑offs (I/O Contracts)
- Concept brief → Story arc → Episode beats → Character profiles → Storyboard frames → Images → Video segments → Edited MP4 → QC pass → Distribution
- Keep outputs as plain JSON/Markdown objects so UI can show each stage without extra transformation.

## Next‑Upgrades (Fast Follow)
Add in this order to improve perceived quality without large complexity jumps:
1) Character Designer (Character MCP) — better visual consistency
2) Color Grader (Post) — quick film look and tone consistency
3) Audio Mixer (Audio MCP) — add simple background track
4) Compositor (Post) — basic overlays/transitions
5) Quality Controller (Production Planning) — automated basic checks before Final QC

## References
- docs/AI_AGENT_SYSTEM.md — “Primary Production Pipeline” and “Critical Path Agents”
- docs/DEVELOPMENT_STATUS.md — overall status/phasing
- docs/ARCHITECTURE.md — service layout and MCP domains

