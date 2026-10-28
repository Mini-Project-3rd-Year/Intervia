# Intervia Security Decisions

## Request protection

- Authentication endpoints are limited to 10 requests per minute per client address.
- Other HTTP endpoints use a 100 requests per minute default limit through SlowAPI.
- CORS reads only the comma-separated `ALLOWED_ORIGINS` setting; no wildcard origin is enabled.
- Every response includes `X-Request-ID`. A caller-provided ID is preserved for distributed tracing.

## Response headers

The API adds:

- `Content-Security-Policy` with same-origin defaults and no framing.
- `X-Frame-Options: DENY`.
- `X-Content-Type-Options: nosniff`.

The CSP is intentionally API-safe. Frontend asset policy belongs to the frontend server.

## Input handling

- Pydantic validates email and password constraints at the request boundary.
- User display text is stripped of HTML markup, control characters, surrounding whitespace, and bounded to its field maximum.
- File upload validation must inspect magic bytes before parsing when upload endpoints are introduced. MIME type and filename alone are not trusted.

## Database safety

The current repository has not activated its SQLAlchemy/async database layer. When it is enabled, queries must use SQLAlchemy expressions or bound parameters; string interpolation of user values is prohibited.

## Secrets and authentication

Supabase remains the credential authority. Access tokens are validated through Supabase and are never logged. Service-role credentials are backend-only and must not be exposed to the frontend.

## Testing and limits

The backend CI workflow installs pinned dependencies, runs the complete test suite, and enforces the 80% coverage target. The current repository contains only health, auth, and WebSocket endpoints; tests for future resume, jobs, evaluation, and coaching APIs should be added when those routes are implemented.
