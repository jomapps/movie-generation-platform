# Clarification Questions

1. Which storage backends must the MVP support out of the box (e.g., S3-compatible only, Azure Blob, local disk), and how are credentials supplied to the agent?
All storage is via payloadcms. it has the media collection, the media collection saves to cloudflare r2. Should you need to bypass the media collection, you can use cloudflare r2 directly. always have public urls.
2. Where exactly should the metadata record be persisted—do we have an existing Story MCP endpoint or ops database contract, and what schema/versioning should we respect?
all of database related stuff is in payloadcms via collecitons. if something is missing, add it. we are developing and there is nothing that needs to stay the way it is.
3. What format and transport are expected for the emitted audit log event so we can align with existing observability pipelines? json
4. Should the agent automatically handle re-publish/versioning scenarios, or is duplicate detection via `audit_log_id` sufficient with manual remediation? overwrite
5. Are there strict naming conventions for the deterministic storage path (e.g., include concept ID, timestamp) that we must follow for downstream discovery? paylaodcms takes care of timestamps. follow the collections. do not create data models any where else.
6. How should we handle signed URL generation when the target storage lacks native support—do we proxy through another service or fall back to time-limited auth tokens?
you use of media collection will generate signed urls (or use the public url of the media)
7. What retry/backoff policies are acceptable for upload failures, and do we need to emit metrics or alerts to a specific monitoring system when retries exhaust? no retries. stop operations. inform user.
