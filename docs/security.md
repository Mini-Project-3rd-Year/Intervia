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
- Resume upload validation checks signatures and archive structure, limits size, DOCX archive entries and expanded size, and PDF page count. MIME type and filename alone are not trusted.
- Resume content is sent to Google Gemini only after the user explicitly consents. Consent is persisted with the resume and required by the profile endpoint. The application owner must clearly disclose Google's processing in its privacy notice and verify that the provider configuration satisfies applicable privacy obligations.
- Resume uploads and Gemini profile extractions have configurable per-user daily quotas. The counters are persisted in PostgreSQL so they apply across application workers.

## Database safety

The async SQLAlchemy database layer is active. Queries must use SQLAlchemy expressions or bound parameters; string interpolation of user values is prohibited.

## Secrets and authentication

Supabase remains the credential authority. Access tokens are validated through Supabase and are never logged. Service-role credentials are backend-only and must not be exposed to the frontend.

## Testing and limits

The backend CI workflow installs pinned dependencies, runs the complete test suite, and enforces the 80% coverage target. Resume parsing, profile extraction, upload cleanup, and quota behavior are covered by backend tests.
