# Clarification Questions

1. Which LLM providers/models must the agent support at launch, and how are credentials plus model selection configured per environment?
for image generation
FAL_TEXT_TO_IMAGE_MODEL=fal-ai/nano-banana
FAL_IMAGE_TO_IMAGE_MODEL=fal-ai/nano-banana/edit
for voice generation
ELEVENLABS_API_KEY
for video generation
FAL_IMAGE_TO_VIDEO=fal-ai/veo3/fast/image-to-video
FAL_TEXT_TO_VIDEO=fal-ai/veo3/fast

2. Do we have canonical taxonomies for `genre_tags` and `tone_keywords`, or should the agent generate free-form strings validated only by length/count constraints?
add the taxonomie if not present and then use.
3. How should the agent handle privacy-sensitive user inputs—do we need to redact or hash certain fields before logging or storing in telemetry systems?
NO. we do not need a system for this.
4. What is the UX expectation when critical fields (e.g., `core_conflict`) cannot be inferred—should the agent return partial briefs with `validation_notes`, or fail the request outright? fail outright
5. Are there reuse requirements (e.g., storing the concept brief for future iterations) despite the MVP statement about no persistence, and if so which service owns that storage?
ALL data is in payloadcms. create appropriate collections if not present.
6. Should we support localization/multi-language inputs from day one, or is MVP limited to English-only prompts and outputs?
English only at this time.
7. How are prompt templates versioned and deployed—do we read them from a config service, bundled JSON files, or environment-provided overrides? You do not need to worry about this. payloadcms is the source of truth and it versions itself. you can jsut use the latest.

