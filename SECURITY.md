# Security Policy

## Supported Versions

MotionForge 3D is pre-1.0 open-source software. Security fixes are applied to the default branch unless a maintained release branch is explicitly announced.

## Baseline Controls

- Argon2id password hashing with memory/time cost.
- Expiring HS256 JWT access tokens; deployment secret must be at least 32 random bytes.
- Organization membership enforcement and tenant-scoped queries.
- Generated internal filenames, extension/MIME/decode validation, upload and duration limits, SHA-256 duplicate detection.
- Protected evidence/report endpoints and no public object path authorization.
- Audit events for identity, media, analysis, review, and report actions.
- Non-root Docker users, health endpoints without secrets, CORS allow-list, safe error envelopes, and security headers.

## Threat model

Primary threats are cross-tenant IDOR, malicious media, decompression/codec abuse, credential theft, token replay, object-storage disclosure, queue duplication, report export bypass, and sensitive data leakage through logs. Controls are documented in `docs/security/THREAT_MODEL.md`.

## Known Gaps

Refresh-token rotation, CSRF protections for cookie mode, enterprise SSO, KMS-backed envelope encryption, malware scanning, fully signed MinIO URLs, and automated deletion retries are extension points rather than claimed completed capabilities.

## Reporting a Vulnerability

Please report vulnerabilities privately through GitHub Security Advisories if enabled for the repository, or contact the maintainer through the GitHub profile. Do not include private video, credentials, access tokens, or personal data in public issues.

Helpful reports include:

- Affected endpoint, workflow, or component.
- Steps to reproduce with synthetic data.
- Impact and suggested severity.
- Any relevant logs with secrets removed.
