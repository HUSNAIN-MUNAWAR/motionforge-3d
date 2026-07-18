# API Guide

The versioned base path is `/api/v1`. Authenticate with `Authorization: Bearer <token>`. Tenant-owned routes also require `X-Organization-ID`.

Core groups are authentication, organizations, subjects, sessions, media upload, jobs, analysis, reviews, reports, and calibrations. OpenAPI is exposed at `/api/v1/openapi.json` and interactive docs at `/api/docs`.

Errors use standard HTTP status codes. Processing failure responses include a stable job reference, failed stage, and human-readable reason while server stack traces remain hidden.
