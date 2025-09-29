# Clarification Questions

1. Which diffusion providers must the MVP support beyond FAL.ai, and how should provider credentials/secrets be injected into the runtime securely?
we will only use fal.ai since it allows us to use different models
2. Do we have a standardized prompt template library already defined, or will the implementation need to create and maintain these templates (including localization/style variants)? i dont have already defined. how ever you can seed appropriate examples for testing and we will create new ones later.
3. How should we reconcile discrepancies between storyboard descriptions and character visual signatures—does one take precedence, or should we synthesize them with explicit conflict resolution rules? no. alert the user with the issue clearly in the auto-movie app. Create a mechanism to record failures in an audit log. and flag them in the UI.
4. What is the expected behavior when the provider returns base64 payloads—do we own the upload to object storage, and what naming/retention policies apply to those assets? use most appropriate. create base64 to image conversion.
5. Are quality scores or rejection heuristics required in MVP (e.g., auto-flagging blurry outputs), or is the `failed_frames` array sufficient for error reporting? yes. Use the default llm to score the image. it has vision capabilities.
6. Should retries be handled synchronously within a single request lifecycle, or can we enqueue background jobs for long-running renders with callback notifications? no retries, fallbacks or mock data. if it fails, just report gracefully and stop operations.
7. How do we ensure consistent seeding across batches to maintain character continuity—does the orchestrator provide deterministic seeds per frame, or should the agent derive them? let orchestrator provide deterministic seeds per frame ikn conjunctiion with the brain service.

