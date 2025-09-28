# mcp-audio-service

## Service overview and purpose
Manages audio generation and processing: music bed selection, SFX cataloging, TTS/voiceover generation, and basic mixing to accompany scenes and previews.

## Technical requirements and dependencies
- Language: Python 3.11+
- FastAPI + MCP adapter
- Providers: TTS (e.g., ElevenLabs/PlayHT) where permitted; music/SFX catalogs
- DSP: FFmpeg/SoX for mixdown/normalization
- Storage: PayloadCMS Media
- Queue: Optional Celery for long jobs

## API endpoints and interfaces
- HTTP:
  - POST `/tts` { scriptText, voice, format } → mediaId
  - POST `/mix` { stems[], targetLoudness } → mediaId
  - GET `/health` → { ok: true }
- MCP tools:
  - `audio.generate_tts`
  - `audio.mixdown`

## Database schema (if applicable)
Use Media metadata to store audio descriptors:
- media.audio: { type: "tts|mix|music|sfx", loudnessLUFS, duration, bpm?, key? }

## Integration points with PayloadCMS
- Pull script text from project/script documents
- Upload rendered audio; link to scenes
- Expose lightweight search over catalog via CMS

## Step-by-step implementation guide
1. Implement TTS adapter behind a common interface
2. Add mixdown pipeline with FFmpeg filters; validate loudness
3. Create MCP tools; wire uploads to CMS
4. Add Celery tasks for long renders

## Testing strategy
- Unit: adapter mocks, parameter validation
- Integration: TTS happy path; loudness normalization check

## Deployment considerations
- Container with FFmpeg/SoX; license compliance for providers
- Secrets via environment; network to CMS and providers

