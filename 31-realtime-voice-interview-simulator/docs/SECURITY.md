# Security, Privacy and Threat Model

## Trust boundaries

Browser audio, SDP, transcript and filters are untrusted. The backend owns provider credentials, system instructions, reference answers, authorization, budgets and retention. The provider is an external processor. SQLite is a local learning store, not a multi-tenant production database.

## Implemented controls

- The standard API key exists only in the server environment.
- Reference answers are omitted from `/api/questions`.
- Length/type validation and NUL removal precede scoring.
- Email, phone, key-shaped values and private-key headers are redacted before persistence.
- Prompt-injection patterns create telemetry but never grant capability.
- Realtime errors exclude provider response bodies.
- HTTP rate limiting and security response headers are enabled.
- Raw audio is not recorded by the application.
- Transcript retention can be disabled and sessions can be deleted.
- Container runs non-root, drops capabilities and uses a read-only filesystem.

## Production additions

OIDC authentication, tenant-scoped authorization, CSRF/origin enforcement, distributed quotas, encrypted managed storage, regional residency, KMS rotation, immutable audit export, consent receipts, backup deletion, CSP, dependency/image signing and independent penetration testing.
