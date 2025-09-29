# Clarification Questions

1. Which video synthesis providers must the agent integrate with at MVP launch, and how are API credentials plus model presets configured per environment? fal.ai and fixed models and credentials in env. fixed system wide.
2. How should we determine the grouping of frames into segments—are there explicit orchestration rules, or should the agent infer from storyboard pacing and scene numbers? best to incremental scene numbers.
3. Do we need to support asynchronous job polling with callbacks/webhooks, or is synchronous blocking acceptable given provider SLAs? at present syncronous is fine.
4. What is the expected behavior when provider runtimes exceed the 90s target—should we cancel the job, continue polling, or hand control back to the orchestrator with a pending status? all our systems and all fal.ai support webhooks.. they should integrate with that. some tasks can take very very long time.
5. Are there required motion style controls (pan, zoom, action verbs) that must map directly from storyboard metadata, and how granular should those mappings be? jsut use teh workds as they are . prompts will be precise nad understood.
6. How do we enforce consistent resolution and frame rate—should the agent post-process outputs with FFmpeg or rely on provider guarantees? rely on provider guarantees.
7. What failure handling and retry policies are acceptable for `failed_segments`, and should we attempt to regenerate using alternate prompts or simply report the failure upstream? no retyr. if it fails report and stop.
