# Intervia — API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Versioning

All endpoints are prefixed with `/api/v1/`. Future breaking changes will be introduced under `/api/v2/` without removing v1.

## Authentication

From Phase 1 onwards, all protected endpoints require a Bearer token:

```http
Authorization: Bearer <access_token>
```

---

## Phase 0 Endpoints

### `GET /api/v1/health`

Returns the current health status of the API.

**Response**

```json
{
  "status": "ok",
  "service": "intervia-api",
  "version": "0.1.0",
  "environment": "development"
}
```

---

## Phase 1 Endpoints (Authentication)

### `POST /api/v1/auth/register`
### `POST /api/v1/auth/login`
### `POST /api/v1/auth/logout`
### `POST /api/v1/auth/refresh`
### `GET /api/v1/users/me`
### `PATCH /api/v1/users/me`

---

## Phase 2 Endpoints (Resume)

### `POST /api/v1/resumes`
Upload and parse a PDF or DOCX resume (maximum size is configured by
`MAX_UPLOAD_SIZE_MB`). This legacy endpoint returns the resume record and
does not grant consent for third-party AI processing.

### `POST /api/v1/resume/upload`
Upload a PDF or DOCX resume for the Resume Intelligence UI. Requires a valid
bearer token and explicit `consent_to_ai_processing=true` multipart field.
Returns `resume_id`, `filename`, processing `status`, and a user-facing message.
Daily per-user upload quotas are configured with `RESUME_DAILY_UPLOAD_LIMIT`.

### `GET /api/v1/resume/{resume_id}/profile`
Extract and return the resume owner's name, skills, and experience count using
Gemini. Configure `GEMINI_API_KEY` to enable profile extraction; results are
stored with the resume and reused on later requests. Profile extraction requires
the recorded Gemini consent and is subject to `RESUME_DAILY_PROFILE_LIMIT`.
Resume text is sent to Google's Gemini service only after the user consents in
the upload UI. Operators must disclose this processing in their privacy notice.

### `GET /api/v1/resumes`
List all resumes for the authenticated user.

### `GET /api/v1/resumes/{id}`
Get a specific resume and its parsed candidate profile.

### `DELETE /api/v1/resumes/{id}`
Delete a resume.

---

## Phase 3 Endpoints (Job Description)

### `POST /api/v1/jobs/analyze`

**Request**

```json
{
  "text": "We are looking for a Backend Engineer with 3+ years of experience...",
  "resume_id": "uuid"
}
```

**Response**

```json
{
  "role": "Backend Engineer",
  "required_skills": ["Python", "FastAPI", "PostgreSQL"],
  "preferred_skills": ["Redis", "Kubernetes"],
  "matched_skills": ["Python", "FastAPI"],
  "missing_skills": ["Redis", "Kubernetes"],
  "skill_gaps": ["Kubernetes orchestration", "Redis caching patterns"]
}
```

---

## Phase 5 Endpoints (Interviews)

### `POST /api/v1/interviews`
Create a new interview session.

### `GET /api/v1/interviews`
List all interviews for the user.

### `GET /api/v1/interviews/{id}`
Get interview details.

### `PATCH /api/v1/interviews/{id}/start`
Start the interview session.

### `PATCH /api/v1/interviews/{id}/end`
End the interview session.

### `GET /api/v1/interviews/{id}/questions`
Get all questions for an interview.

### `POST /api/v1/interviews/{id}/answers`
Submit an answer.

### `GET /api/v1/interviews/{id}/evaluation`
Get the full evaluation report.

---

## Phase 7 WebSocket (Adaptive Interview)

```
ws://localhost:8000/ws/interview/{session_id}
```

Messages flow:

```json
// Client → Server
{ "type": "answer", "transcript": "...", "audio_url": "..." }

// Server → Client
{ "type": "question", "text": "...", "category": "technical", "sequence": 3 }
{ "type": "thinking", "message": "Analyzing response..." }
{ "type": "interview_end", "reason": "completed" }
```

---

## Error Responses

All errors follow the FastAPI standard format:

```json
{
  "detail": "Human-readable error message"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request / validation error |
| 401 | Unauthorized (invalid or missing token) |
| 403 | Forbidden (accessing another user's data) |
| 404 | Resource not found |
| 422 | Unprocessable entity (schema validation failed) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
