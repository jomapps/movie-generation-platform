# Clarification Questions

1. What infrastructure will the agent run on—do we have guaranteed access to FFmpeg/FFprobe binaries with GPU support, or must we bundle lightweight alternatives?
you can list waht you want but both ffmpeg and ffprobe are available.
2. How are MP4 assets authenticated before download—should we verify checksums pre-download or rely on signed URLs alone? just rely on urls. no need to verify checksums.
3. Are the threshold defaults for brightness, freeze detection, and duration validation already defined, and where should we store configurable overrides? create a collection in payloadcms for the thresholds. all data is in payloadcms. create all fields you require in the colleciton if not present.
4. Should detected issues block the pipeline automatically, or can the orchestrator override failures via a flag in the request payload? issue block pipeline with flag and message to user.
5. Where are QC reports and preview images expected to live (storage bucket path conventions), and what retention policy hooks do we need to integrate with ops systems? pdf media in the media collection and a description of the image in the media collection. always all data in auto-movie > payloadcms.
6. How detailed should `recommended_actions` be—are we expected to provide canned remediation instructions or reference documentation links maintained elsewhere? provide remediation instructions.
7. Do we need to integrate with any alerting or ticketing systems when QC fails, or is returning structured errors back to the orchestrator sufficient for MVP? create a system in auto-movie to handle alerts and ticketing. use paylaodcms as the storage. 
