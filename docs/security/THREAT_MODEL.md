# Threat Model

| Asset | Threat | Control | Residual risk |
|---|---|---|---|
| Tenant video | IDOR / cross-tenant download | Membership check plus tenant-scoped DB lookup before FileResponse | A future direct-to-object-store path must preserve this check |
| Credentials | Offline cracking | Argon2id and minimum password length | Password policy and MFA are deployment decisions |
| JWT | Replay or leaked secret | Short expiry, secret from environment, no token logging | Refresh rotation is not yet implemented |
| Upload pipeline | Path traversal | Generated internal filenames; original name used only as metadata | Codec vulnerabilities depend on patched FFmpeg/OpenCV |
| Worker | Duplicate execution | Persistent terminal state and idempotent result replacement | Distributed locks should be added for high scale |
| Reports | Unauthorized export | Tenant-scoped report record lookup | Browser cache policy depends on deployment proxy |
| Logs | Sensitive notes/tokens | Structured logging contract excludes tokens and subject notes | Operators must preserve redaction in external sinks |
| Object storage | Public bucket | Local protected path by default; MinIO intended as private | Signed URL adapter is an extension point |
