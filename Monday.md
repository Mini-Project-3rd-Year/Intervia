# 📋 Intervia — Weekend Delivery Guide
### Deliver by: **Monday 9:00 AM IST**
### Team: Tanushri · Shri · Upasna · Sansriti

> Read your own section fully before writing a single line of code.  
> The **API Contract** section at the bottom is mandatory reading for everyone.

---

## ⚙️ First — Everyone Does This Once

```bash
# 1. Clone / pull latest code
git checkout main
git pull origin main

# 2. Create your branch (use exact branch name below)
# 3. Work only in your branch
# 4. Open a PR to → develop (not main)
```

> If `develop` branch doesn't exist yet, **Sansriti creates it first:**
> ```bash
> git checkout -b develop
> git push origin develop
> ```

---
---

# 🛠️ SANSRITI — DevOps + Critical Bug Fixes
### Branch: `fix/critical-bugs-and-devops`

```bash
git checkout main
git pull origin main
git checkout -b fix/critical-bugs-and-devops
```

---

## Task 1: Fix Duplicate Functions in `embedder.py` ⚠️ CRITICAL

**File:** `backend/app/rag/embedder.py`

The file currently has `embed_text`, `embed_batch`, `_embed_openai_sync` defined **twice**. Delete lines 161–239 (the second copy). The file should end at line 157.

After deleting, the file ends with:
```python
    all_embeddings.extend(batch_embeddings)

return all_embeddings
```

**Verify fix:**
```bash
cd backend
python -c "from app.rag.embedder import embed_text, embed_batch; print('OK')"
```
Expected output: `OK` (no `SyntaxError` or `ImportError`)

---

## Task 2: Fix `asyncio.get_event_loop()` in `embedder.py`

In `backend/app/rag/embedder.py`, find **both occurrences** of:
```python
loop = asyncio.get_event_loop()
```
Replace both with:
```python
loop = asyncio.get_running_loop()
```

---

## Task 3: Fix Hardcoded JWT Secret in `config.py`

**File:** `backend/app/core/config.py`

Find:
```python
JWT_SECRET_KEY: str = "changeme-in-production"
```

Replace with:
```python
JWT_SECRET_KEY: str = ""

@model_validator(mode="after")
def _validate_production_secrets(self) -> "Settings":
    if self.APP_ENV == "production":
        if not self.JWT_SECRET_KEY:
            raise ValueError(
                "JWT_SECRET_KEY must be set in production. "
                "Generate one with: openssl rand -hex 32"
            )
    return self
```

Also add this import at the top of `config.py` if not already there:
```python
from pydantic import AnyHttpUrl, field_validator, model_validator
```

---

## Task 4: Fix `DEBUG` and `RELOAD` Defaults

**File:** `backend/app/core/config.py`

Change:
```python
DEBUG: bool = True
BACKEND_RELOAD: bool = True
```
To:
```python
DEBUG: bool = False
BACKEND_RELOAD: bool = False
```

> The `.env` file in dev overrides this. Production is now safe by default.

---

## Task 5: Fix RAG Debug Router — Conditional Registration

**File:** `backend/app/api/v1/__init__.py`

Replace:
```python
# Phase 4: RAG debug endpoint (dev only — guarded by DEBUG check inside the route)
from app.api.v1.rag import router as rag_router  # noqa: E402

api_v1_router.include_router(rag_router)
```

With:
```python
# Phase 4: RAG debug endpoint — only registered in DEBUG mode
if _settings.DEBUG:
    from app.api.v1.rag import router as rag_router  # noqa: E402
    api_v1_router.include_router(rag_router)
```

---

## Task 6: Create `docker-compose.prod.yml`

**File:** `docker-compose.prod.yml` (project root — next to `docker-compose.yml`)

```yaml
version: "3.9"

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: intervia-postgres-prod
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: intervia-backend-prod
    restart: always
    env_file:
      - .env.prod
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      APP_ENV: production
      DEBUG: "false"
    ports:
      - "8000:8000"
    volumes:
      - uploads_data:/app/uploads
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: intervia-frontend-prod
    restart: always
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend

volumes:
  postgres_data:
  uploads_data:
```

---

## Task 7: Create `frontend/Dockerfile.prod`

**File:** `frontend/Dockerfile.prod`

```dockerfile
# ── Stage 1: Build ──────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ── Stage 2: Serve with Nginx ───────────────────────────────
FROM nginx:alpine AS runtime
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Task 8: Create `nginx.conf`

**File:** `nginx.conf` (project root)

```nginx
events { worker_connections 1024; }

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    server {
        listen 80;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;

        # Backend API proxy
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # WebSocket proxy
        location /ws/ {
            proxy_pass http://backend:8000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # React SPA — all other routes go to index.html
        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
```

---

## Task 9: Create GitHub Actions CI

**File:** `.github/workflows/ci.yml` (create the folders too)

```yaml
name: CI

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  backend-test:
    name: Backend — Lint & Test
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v --tb=short
        env:
          APP_ENV: development
          DEBUG: "true"
          SUPABASE_URL: "http://localhost"
          SUPABASE_ANON_KEY: "test"
          SUPABASE_SERVICE_ROLE_KEY: "test"
          GEMINI_API_KEY: "test"
          DATABASE_URL: "postgresql+asyncpg://postgres:password@localhost:5432/intervia"

  frontend-check:
    name: Frontend — Type Check & Lint
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - name: TypeScript check
        run: npx tsc --noEmit
      - name: Lint
        run: npm run lint
```

---

## Task 10: Update `.env.example`

**File:** `.env.example` (project root — already exists, update it)

Add these missing required vars:
```bash
# ── Production Required ─────────────────────────
APP_ENV=production
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-strong-password-here
POSTGRES_DB=intervia
JWT_SECRET_KEY=generate-with-openssl-rand-hex-32

# ── Backend ─────────────────────────────────────
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
GEMINI_API_KEY=your-gemini-api-key
ALLOWED_ORIGINS=https://yourdomain.com

# ── Frontend ─────────────────────────────────────
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## ✅ How to Test Your Work

```bash
# Test 1: No import errors
cd backend
python -c "from app.main import app; print('App loads OK')"

# Test 2: Existing tests still pass
pytest tests/ -v

# Test 3: Docker prod build works
docker build -f frontend/Dockerfile.prod ./frontend
```

---

## 📤 How to Create Your PR

```bash
# Commit everything
git add .
git commit -m "fix: critical bugs, security hardening, prod docker setup"
git push origin fix/critical-bugs-and-devops
```

Then go to GitHub → **New Pull Request**:
- **Base branch:** `develop`
- **Compare branch:** `fix/critical-bugs-and-devops`
- **Title:** `fix: critical bugs + security + prod docker`
- **Description:**
  ```
  ## What's in this PR
  - Fixed duplicate functions in embedder.py
  - Fixed asyncio.get_event_loop() deprecation
  - Removed hardcoded JWT_SECRET_KEY default
  - Set DEBUG=False as production default
  - RAG debug router now conditionally registered
  - Added docker-compose.prod.yml
  - Added frontend/Dockerfile.prod + nginx.conf
  - Added GitHub Actions CI pipeline
  - Updated .env.example

  ## Testing
  - [ ] `python -c "from app.main import app"` passes
  - [ ] `pytest tests/` passes
  - [ ] Docker build succeeds
  ```
- Tag **Tanushri** as reviewer

---
---

# 🤖 SHRI — AI Backend (Interview Engine + TTS)
### Branch: `feat/interview-api`

```bash
git checkout main
git pull origin main
git checkout -b feat/interview-api
```

---

## Task 1: Add Dependencies

**File:** `backend/requirements.txt`

Add these lines:
```
# Resume parsing
pypdf==5.0.1
python-docx==1.1.2

# AI agents
langchain-google-genai==2.0.7

# Rate limiting
slowapi==0.1.9
```

Then install:
```bash
cd backend
pip install -r requirements.txt
```

---

## Task 2: Create Interview SQLAlchemy Models

**File:** `backend/app/models/interview.py` (create new file)

```python
"""
backend/app/models/interview.py
Interview session, question, answer, and evaluation ORM models.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    resume_id = Column(UUID(as_uuid=True), nullable=True)  # optional
    role = Column(String(255), nullable=False)
    mode = Column(String(50), nullable=False)  # technical | hr | mixed | pressure
    status = Column(String(50), nullable=False, default="active")  # active | completed
    overall_score = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    questions = relationship("InterviewQuestion", back_populates="interview",
                             order_by="InterviewQuestion.order_index")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("interviews.id"), nullable=False)
    text = Column(Text, nullable=False)
    question_type = Column(String(100), nullable=False, default="general")
    difficulty = Column(String(50), nullable=False, default="medium")
    order_index = Column(Integer, nullable=False, default=0)
    audio_url = Column(String(500), nullable=True)  # TTS generated audio

    interview = relationship("Interview", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False)


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("interview_questions.id"),
                         nullable=False, unique=True)
    answer_text = Column(Text, nullable=False)
    score = Column(Integer, nullable=True)          # 0–100
    feedback = Column(Text, nullable=True)
    strengths = Column(JSONB, nullable=False, server_default="[]")
    improvements = Column(JSONB, nullable=False, server_default="[]")
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    question = relationship("InterviewQuestion", back_populates="answer")
```

---

## Task 3: Register Models in `__init__.py`

**File:** `backend/app/models/__init__.py`

```python
"""
backend/app/models/__init__.py
SQLAlchemy ORM model registry.
"""

from app.models.resume_chunk import ResumeChunk
from app.models.interview import Interview, InterviewQuestion, InterviewAnswer

__all__ = [
    "ResumeChunk",
    "Interview",
    "InterviewQuestion",
    "InterviewAnswer",
]
```

---

## Task 4: Create Alembic Migration for Interview Tables

```bash
cd backend
alembic revision --autogenerate -m "add_interview_tables"
```

> ⚠️ **Coordinate with Upasna first!** Only one person should run `alembic revision` at a time.  
> Run yours AFTER Upasna runs hers, or flip a coin and go first — just don't run simultaneously.

Check the generated file in `alembic/versions/` — make sure it includes `interviews`, `interview_questions`, `interview_answers` tables.

Apply it:
```bash
alembic upgrade head
```

---

## Task 5: Create Interview API Router

**File:** `backend/app/api/v1/interview.py` (create new file)

```python
"""
backend/app/api/v1/interview.py
Interview session API — start session, submit answer, get results.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.logging import get_logger
from app.db.session import get_db
from app.schemas.user import UserRead
from app.services.interview_service import InterviewService

logger = get_logger()
router = APIRouter(prefix="/interview", tags=["interview"])


# ── Request / Response schemas ────────────────────────────────────────────────

class StartInterviewRequest(BaseModel):
    role: str
    mode: str          # technical | hr | mixed | pressure
    resume_id: Optional[str] = None

class QuestionOut(BaseModel):
    id: str
    text: str
    question_type: str
    difficulty: str
    audio_url: Optional[str] = None

class StartInterviewResponse(BaseModel):
    session_id: str
    role: str
    mode: str
    total_questions: int
    first_question: QuestionOut

class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer_text: str

class SubmitAnswerResponse(BaseModel):
    score: int
    feedback: str
    strengths: list[str]
    improvements: list[str]
    next_question: Optional[QuestionOut] = None
    session_complete: bool

class ResultsResponse(BaseModel):
    session_id: str
    role: str
    mode: str
    overall_score: int
    total_questions: int
    questions: list[dict]
    coaching_tips: list[str]


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/start", response_model=StartInterviewResponse,
             status_code=status.HTTP_201_CREATED)
async def start_interview(
    payload: StartInterviewRequest,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StartInterviewResponse:
    """
    Start a new interview session.
    Calls Gemini to generate questions, stores them, returns first question.
    """
    service = InterviewService(db)
    result = await service.start_interview(
        user_id=current_user.id,
        role=payload.role,
        mode=payload.mode,
        resume_id=payload.resume_id,
    )
    return result


@router.post("/answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    payload: SubmitAnswerRequest,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SubmitAnswerResponse:
    """
    Submit an answer to the current question.
    Gemini evaluates it and returns score + feedback + next question.
    """
    service = InterviewService(db)
    result = await service.submit_answer(
        session_id=payload.session_id,
        question_id=payload.question_id,
        answer_text=payload.answer_text,
        user_id=current_user.id,
    )
    return result


@router.get("/{session_id}/results", response_model=ResultsResponse)
async def get_results(
    session_id: str,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResultsResponse:
    """Get the full interview results and AI coaching tips."""
    service = InterviewService(db)
    return await service.get_results(session_id=session_id, user_id=current_user.id)
```

---

## Task 6: Create Interview Service (Gemini Logic)

**File:** `backend/app/services/interview_service.py` (create new file)

```python
"""
backend/app/services/interview_service.py
Core interview business logic — Gemini question generation + evaluation.
"""

import json
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.interview import Interview, InterviewAnswer, InterviewQuestion

logger = get_logger()
settings = get_settings()

QUESTION_COUNT = 6  # Questions per session


def _get_gemini_client():
    from google import genai
    return genai.Client(api_key=settings.GEMINI_API_KEY)


async def _call_gemini(prompt: str) -> str:
    """Call Gemini in a thread pool (blocking call → async)."""
    import asyncio, functools
    client = _get_gemini_client()

    def _sync_call():
        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
        )
        return response.text

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_call)


class InterviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_interview(
        self, user_id: str, role: str, mode: str, resume_id: Optional[str] = None
    ) -> dict:
        # ── 1. Generate questions via Gemini ──────────────────────────────────
        mode_desc = {
            "technical": "technical coding, system design, and framework questions",
            "hr": "behavioral STAR-method HR questions about teamwork, leadership, challenges",
            "mixed": "a mix of 3 technical and 3 behavioral questions",
            "pressure": "rapid-fire, challenging, slightly intimidating questions",
        }.get(mode, "general interview questions")

        prompt = f"""Generate exactly {QUESTION_COUNT} interview questions for a {role} position.
Focus on: {mode_desc}

Return ONLY a valid JSON array, no markdown, no explanation:
[
  {{"text": "question text here", "type": "Technical|Behavioral|System Design|HR", "difficulty": "easy|medium|hard"}},
  ...
]"""

        raw = await _call_gemini(prompt)
        # Strip markdown code fences if Gemini wraps in ```json
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        questions_data = json.loads(raw)

        # ── 2. Create Interview record ────────────────────────────────────────
        interview = Interview(
            user_id=uuid.UUID(user_id),
            resume_id=uuid.UUID(resume_id) if resume_id else None,
            role=role,
            mode=mode,
            status="active",
        )
        self.db.add(interview)
        await self.db.flush()  # get interview.id

        # ── 3. Create question records ────────────────────────────────────────
        db_questions = []
        for i, q in enumerate(questions_data[:QUESTION_COUNT]):
            question = InterviewQuestion(
                interview_id=interview.id,
                text=q["text"],
                question_type=q.get("type", "general"),
                difficulty=q.get("difficulty", "medium"),
                order_index=i,
            )
            self.db.add(question)
            db_questions.append(question)

        await self.db.commit()
        await self.db.refresh(interview)
        for q in db_questions:
            await self.db.refresh(q)

        first_q = db_questions[0]
        return {
            "session_id": str(interview.id),
            "role": role,
            "mode": mode,
            "total_questions": len(db_questions),
            "first_question": {
                "id": str(first_q.id),
                "text": first_q.text,
                "question_type": first_q.question_type,
                "difficulty": first_q.difficulty,
                "audio_url": None,
            },
        }

    async def submit_answer(
        self, session_id: str, question_id: str, answer_text: str, user_id: str
    ) -> dict:
        # ── 1. Load question ──────────────────────────────────────────────────
        result = await self.db.execute(
            select(InterviewQuestion).where(
                InterviewQuestion.id == uuid.UUID(question_id)
            )
        )
        question = result.scalar_one_or_none()
        if not question:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Question not found")

        # ── 2. Evaluate answer via Gemini ─────────────────────────────────────
        eval_prompt = f"""You are a strict but fair interview evaluator.

Question: {question.text}
Question Type: {question.question_type}
Candidate Answer: {answer_text}

Score the answer out of 100 and provide feedback.
Return ONLY valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "feedback": "<2-3 sentence summary>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "improvements": ["<improvement 1>", "<improvement 2>"]
}}"""

        raw = await _call_gemini(eval_prompt)
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        eval_data = json.loads(raw)

        # ── 3. Save answer ────────────────────────────────────────────────────
        answer = InterviewAnswer(
            question_id=uuid.UUID(question_id),
            answer_text=answer_text,
            score=eval_data["score"],
            feedback=eval_data["feedback"],
            strengths=eval_data.get("strengths", []),
            improvements=eval_data.get("improvements", []),
        )
        self.db.add(answer)
        await self.db.flush()

        # ── 4. Find next question ─────────────────────────────────────────────
        next_q_result = await self.db.execute(
            select(InterviewQuestion)
            .where(InterviewQuestion.interview_id == question.interview_id)
            .where(InterviewQuestion.order_index == question.order_index + 1)
        )
        next_question = next_q_result.scalar_one_or_none()

        # ── 5. Complete interview if no more questions ─────────────────────────
        if not next_question:
            interview_result = await self.db.execute(
                select(Interview).where(Interview.id == question.interview_id)
            )
            interview = interview_result.scalar_one()
            interview.status = "completed"

        await self.db.commit()

        return {
            "score": eval_data["score"],
            "feedback": eval_data["feedback"],
            "strengths": eval_data.get("strengths", []),
            "improvements": eval_data.get("improvements", []),
            "next_question": {
                "id": str(next_question.id),
                "text": next_question.text,
                "question_type": next_question.question_type,
                "difficulty": next_question.difficulty,
                "audio_url": None,
            } if next_question else None,
            "session_complete": next_question is None,
        }

    async def get_results(self, session_id: str, user_id: str) -> dict:
        result = await self.db.execute(
            select(Interview).where(Interview.id == uuid.UUID(session_id))
        )
        interview = result.scalar_one_or_none()
        if not interview:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Session not found")

        questions_result = await self.db.execute(
            select(InterviewQuestion)
            .where(InterviewQuestion.interview_id == interview.id)
            .order_by(InterviewQuestion.order_index)
        )
        questions = questions_result.scalars().all()

        qa_list = []
        total_score = 0
        answered = 0

        for q in questions:
            if q.answer:
                total_score += q.answer.score
                answered += 1
                qa_list.append({
                    "question": q.text,
                    "type": q.question_type,
                    "answer": q.answer.answer_text,
                    "score": q.answer.score,
                    "feedback": q.answer.feedback,
                    "strengths": q.answer.strengths,
                    "improvements": q.answer.improvements,
                })

        overall = total_score // answered if answered > 0 else 0

        # Generate coaching tips
        tips_prompt = f"""Based on an interview for {interview.role}, overall score {overall}/100.
Give exactly 3 short, actionable improvement tips as a JSON array of strings.
Return ONLY the JSON array, no markdown."""
        raw_tips = await _call_gemini(tips_prompt)
        raw_tips = raw_tips.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        coaching_tips = json.loads(raw_tips)

        return {
            "session_id": session_id,
            "role": interview.role,
            "mode": interview.mode,
            "overall_score": overall,
            "total_questions": len(questions),
            "questions": qa_list,
            "coaching_tips": coaching_tips,
        }
```

---

## Task 7: Register Interview Router

**File:** `backend/app/api/v1/__init__.py`

Add after the health router lines:
```python
from app.api.v1.interview import router as interview_router  # noqa: E402
api_v1_router.include_router(interview_router)
```

---

## Task 8: TTS Stub Endpoint

**File:** `backend/app/speech/tts.py` (create new file)

```python
"""
backend/app/speech/tts.py
Text-to-Speech — Google TTS stub.
Returns a URL to a generated audio file.
Upgrade to ElevenLabs for higher quality in Week 2.
"""

import asyncio
import functools
import os
import uuid

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger()
settings = get_settings()


async def text_to_speech(text: str) -> str:
    """
    Convert text to audio using Google Cloud TTS.
    Returns a URL path to the saved audio file.
    
    For now: uses gTTS (free, no API key needed).
    Install: pip install gtts
    """
    try:
        from gtts import gTTS  # type: ignore
    except ImportError:
        logger.warning("gTTS not installed — returning empty audio URL")
        return ""

    audio_id = str(uuid.uuid4())
    filename = f"{audio_id}.mp3"
    filepath = os.path.join(settings.LOCAL_STORAGE_PATH, "tts", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    def _generate():
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(filepath)

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _generate)

    return f"/uploads/tts/{filename}"
```

Add `gtts==2.5.1` to `requirements.txt`.

---

## ✅ How to Test

```bash
cd backend
# Start the server
uvicorn app.main:app --reload

# Test start interview (in another terminal)
curl -X POST http://localhost:8000/api/v1/interview/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"role": "Frontend Developer", "mode": "technical"}'
```

---

## 📤 How to Create Your PR

```bash
git add .
git commit -m "feat: interview API with Gemini question generation + evaluation"
git push origin feat/interview-api
```

GitHub → New PR:
- **Base:** `develop` | **Compare:** `feat/interview-api`
- **Title:** `feat: interview session API (start, answer, results)`
- **Description:** List the endpoints you added, confirm Alembic migration is included
- Tag **Tanushri** as reviewer (she needs these endpoints)

---
---

# 📄 UPASNA — Resume Intelligence + Evaluation UI
### Branch: `feat/resume-and-evaluation`

```bash
git checkout main
git pull origin main
git checkout -b feat/resume-and-evaluation
```

---

## Task 1: Add Resume Dependencies

**File:** `backend/requirements.txt` — add (coordinate with Shri, one person edits):
```
pypdf==5.0.1
python-docx==1.1.2
```

```bash
pip install pypdf python-docx
```

---

## Task 2: Create Resume Model

**File:** `backend/app/models/resume.py` (create new file)

```python
"""backend/app/models/resume.py — Resume ORM model."""

import uuid
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    raw_text = Column(Text, nullable=True)          # Extracted text
    parsed_profile = Column(Text, nullable=True)    # JSON string of CandidateProfile
    status = Column(String(50), nullable=False, default="processing")
    # status: processing | ready | error
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
```

---

## Task 3: Register Resume Model

**File:** `backend/app/models/__init__.py` — add:
```python
from app.models.resume import Resume

__all__ = [
    "ResumeChunk",
    "Resume",
    # Shri adds: Interview, InterviewQuestion, InterviewAnswer
]
```

---

## Task 4: Create Alembic Migration

> ⚠️ Coordinate with Shri — only one person runs `alembic revision` at a time!

```bash
cd backend
alembic revision --autogenerate -m "add_resumes_table"
alembic upgrade head
```

---

## Task 5: Create Resume Parser Service

**File:** `backend/app/services/resume_parser.py` (create new file)

```python
"""
backend/app/services/resume_parser.py
Extracts raw text from PDF and DOCX resume files.
"""

import os
from app.core.logging import get_logger

logger = get_logger()


def extract_text_from_file(file_path: str, mime_type: str) -> str:
    """
    Extract plain text from a resume file.
    Supports PDF and DOCX formats.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if mime_type == "application/pdf":
        return _extract_pdf(file_path)
    elif mime_type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ):
        return _extract_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {mime_type}")


def _extract_pdf(path: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages)
    return text.strip()


def _extract_docx(path: str) -> str:
    from docx import Document
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)
```

---

## Task 6: Create Resume API Router

**File:** `backend/app/api/v1/resume.py` (create new file)

```python
"""
backend/app/api/v1/resume.py
Resume upload, parsing, and profile endpoints.
"""

import json
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.resume import Resume
from app.schemas.user import UserRead
from app.services.resume_parser import extract_text_from_file

logger = get_logger()
settings = get_settings()
router = APIRouter(prefix="/resume", tags=["resume"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


class ResumeProfileResponse(BaseModel):
    resume_id: str
    name: str | None
    skills: list[str]
    experience_count: int
    status: str


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # ── Validate file ──────────────────────────────────────────────────────────
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF and DOCX files are accepted.",
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB.",
        )

    # ── Save file ──────────────────────────────────────────────────────────────
    resume_id = uuid.uuid4()
    upload_dir = os.path.join(settings.LOCAL_STORAGE_PATH, "resumes")
    os.makedirs(upload_dir, exist_ok=True)

    ext = ".pdf" if file.content_type == "application/pdf" else ".docx"
    filename = f"{resume_id}{ext}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    # ── Extract text ───────────────────────────────────────────────────────────
    try:
        raw_text = extract_text_from_file(file_path, file.content_type)
    except Exception as e:
        logger.error("Resume text extraction failed", error=str(e))
        raw_text = ""

    # ── Save to DB ─────────────────────────────────────────────────────────────
    resume = Resume(
        id=resume_id,
        user_id=uuid.UUID(current_user.id),
        filename=file.filename or filename,
        file_path=file_path,
        mime_type=file.content_type,
        raw_text=raw_text,
        status="ready" if raw_text else "error",
    )
    db.add(resume)
    await db.commit()

    logger.info("Resume uploaded", resume_id=str(resume_id), user_id=current_user.id)

    return {
        "resume_id": str(resume_id),
        "filename": file.filename,
        "status": resume.status,
        "message": "Resume uploaded and processed successfully." if raw_text
                   else "Upload saved but text extraction failed.",
    }


@router.get("/{resume_id}/profile", response_model=ResumeProfileResponse)
async def get_resume_profile(
    resume_id: str,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeProfileResponse:
    """Return parsed profile from a resume. Calls Gemini to extract skills + name."""
    result = await db.execute(
        select(Resume).where(Resume.id == uuid.UUID(resume_id))
    )
    resume = result.scalar_one_or_none()

    if not resume or str(resume.user_id) != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found.")

    if not resume.raw_text:
        raise HTTPException(status_code=422, detail="Resume text could not be extracted.")

    # ── Quick Gemini extraction ────────────────────────────────────────────────
    import asyncio, functools
    from google import genai

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = f"""Extract key information from this resume text.
Return ONLY valid JSON, no markdown:
{{
  "name": "<full name or null>",
  "skills": ["skill1", "skill2", ...],
  "experience_count": <number of distinct jobs>
}}

Resume:
{resume.raw_text[:3000]}"""

    def _call():
        response = client.models.generate_content(model=settings.LLM_MODEL, contents=prompt)
        return response.text

    loop = asyncio.get_running_loop()
    raw = await loop.run_in_executor(None, _call)
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()

    try:
        profile_data = json.loads(raw)
    except Exception:
        profile_data = {"name": None, "skills": [], "experience_count": 0}

    return ResumeProfileResponse(
        resume_id=resume_id,
        name=profile_data.get("name"),
        skills=profile_data.get("skills", [])[:20],
        experience_count=profile_data.get("experience_count", 0),
        status=resume.status,
    )
```

---

## Task 7: Register Resume Router

**File:** `backend/app/api/v1/__init__.py` — add:
```python
from app.api.v1.resume import router as resume_router  # noqa: E402
api_v1_router.include_router(resume_router)
```

---

## Task 8: Build Resume Upload Frontend

**File:** `frontend/src/features/resume/ResumeUpload.tsx` (create new file + folder)

```tsx
import { useState, useRef } from "react";
import apiClient from "../../services/api";

interface Props {
  onUploadComplete: (resumeId: string) => void;
}

export default function ResumeUpload({ onUploadComplete }: Props) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    if (!["application/pdf",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
          .includes(file.type)) {
      setError("Only PDF or DOCX files accepted.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError("File must be under 10MB.");
      return;
    }

    setError(null);
    setUploading(true);
    const form = new FormData();
    form.append("file", file);

    try {
      const { data } = await apiClient.post("/resume/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onUploadComplete(data.resume_id);
    } catch (e: any) {
      setError(e.response?.data?.detail || "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault(); setDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
      }}
      onClick={() => inputRef.current?.click()}
      style={{
        border: `2px dashed ${dragging ? "var(--blue)" : "var(--border)"}`,
        borderRadius: 12, padding: "3rem", textAlign: "center",
        cursor: "pointer", background: dragging ? "rgba(99,102,241,0.05)" : "transparent",
        transition: "all 0.2s",
      }}
    >
      <input ref={inputRef} type="file" accept=".pdf,.docx" hidden
        onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }} />
      {uploading ? (
        <p style={{ color: "var(--text-muted)" }}>⏳ Processing resume…</p>
      ) : (
        <>
          <p style={{ fontSize: "2rem", marginBottom: 8 }}>📄</p>
          <p style={{ fontWeight: 600 }}>Drop your resume here</p>
          <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>
            PDF or DOCX · Max 10MB
          </p>
        </>
      )}
      {error && <p style={{ color: "var(--red)", marginTop: 12, fontSize: "0.875rem" }}>{error}</p>}
    </div>
  );
}
```

Also create `frontend/src/features/resume/index.ts`:
```ts
export { default as ResumeUpload } from "./ResumeUpload";
```

---

## Task 9: Wire Resume Page

**File:** `frontend/src/pages/` — update the `/resume` route in `App.tsx`.

Replace `PlaceholderPage` for `/resume` with an actual page (create `ResumePage.tsx`):

```tsx
// frontend/src/pages/ResumePage.tsx
import { useState } from "react";
import AppShell from "../components/layout/AppShell";
import { ResumeUpload } from "../features/resume";
import apiClient from "../services/api";

export default function ResumePage() {
  const [resumeId, setResumeId] = useState<string | null>(null);
  const [profile, setProfile] = useState<any>(null);

  const handleUpload = async (id: string) => {
    setResumeId(id);
    try {
      const { data } = await apiClient.get(`/resume/${id}/profile`);
      setProfile(data);
    } catch { /* profile unavailable */ }
  };

  return (
    <AppShell pageTitle="Resume Intelligence">
      <div className="page-content" style={{ maxWidth: 720 }}>
        <h1 style={{ marginBottom: "1.5rem" }}>Your Resume</h1>
        {!resumeId ? (
          <ResumeUpload onUploadComplete={handleUpload} />
        ) : profile ? (
          <div>
            <h2>{profile.name || "Your Profile"}</h2>
            <p>{profile.experience_count} positions · {profile.skills.length} skills</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 12 }}>
              {profile.skills.map((s: string) => (
                <span key={s} className="badge">{s}</span>
              ))}
            </div>
            <button style={{ marginTop: "1.5rem" }} onClick={() => setResumeId(null)}>
              Upload Different Resume
            </button>
          </div>
        ) : (
          <p>Processing your resume…</p>
        )}
      </div>
    </AppShell>
  );
}
```

Update `App.tsx` — replace the `/resume` `PlaceholderPage` with:
```tsx
import ResumePage from "./pages/ResumePage.tsx";
// ...
<Route path="/resume" element={<ProtectedRoute><ResumePage /></ProtectedRoute>} />
```

---

## ✅ How to Test

```bash
# Backend test
cd backend
uvicorn app.main:app --reload

# In another terminal — upload a real PDF
curl -X POST http://localhost:8000/api/v1/resume/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/resume.pdf"

# Frontend test
cd frontend && npm run dev
# Navigate to /resume — drag and drop a PDF
```

---

## 📤 How to Create Your PR

```bash
git add .
git commit -m "feat: resume upload, parsing, profile extraction + resume UI"
git push origin feat/resume-and-evaluation
```

GitHub → New PR:
- **Base:** `develop` | **Compare:** `feat/resume-and-evaluation`
- **Title:** `feat: resume upload + parsing + profile UI`
- Tag **Tanushri** as reviewer

---
---

# 👩‍💻 TANUSHRI — 3D AI Interviewer + Interview Frontend
### Branch: `feat/3d-avatar-interview-ui`

```bash
git checkout main
git pull origin main
git checkout -b feat/3d-avatar-interview-ui
```

---

## Task 1: Install R3F Packages

```bash
cd frontend
npm install @react-three/fiber @react-three/drei three @types/three
npm install @react-spring/three
```

Verify install: `node -e "require('@react-three/fiber'); console.log('R3F OK')"`

---

## Task 2: Get a Free Avatar Model

1. Go to **readyplayer.me**
2. Create a free account → build avatar → export as **GLB**
3. Save to `frontend/public/avatar.glb`

**Backup option** (if ReadyPlayerMe is slow): Download a free `.glb` from:
https://sketchfab.com/3d-models/categories/characters?features=downloadable&sort_by=-likeCount

---

## Task 3: Create Avatar Feature Module

Create folder `frontend/src/features/avatar/` and these files:

**`frontend/src/features/avatar/useAvatarStore.ts`**
```ts
import { create } from "zustand";

export type AvatarState = "IDLE" | "SPEAKING" | "LISTENING" | "THINKING";

interface AvatarStore {
  state: AvatarState;
  setState: (s: AvatarState) => void;
}

export const useAvatarStore = create<AvatarStore>((set) => ({
  state: "IDLE",
  setState: (state) => set({ state }),
}));
```

**`frontend/src/features/avatar/AvatarModel.tsx`**
```tsx
import { useRef, useEffect } from "react";
import { useGLTF, useAnimations } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { useAvatarStore } from "./useAvatarStore";

export function AvatarModel({ url = "/avatar.glb" }: { url?: string }) {
  const group = useRef<THREE.Group>(null!);
  const { scene, animations } = useGLTF(url);
  const { actions } = useAnimations(animations, group);
  const avatarState = useAvatarStore((s) => s.state);

  // Idle head bob
  useFrame((_, delta) => {
    if (group.current) {
      group.current.rotation.y = Math.sin(Date.now() * 0.0005) * 0.05;
    }
  });

  // Play animations based on state
  useEffect(() => {
    const actionName = Object.keys(actions)[0]; // use first available animation
    if (actionName && actions[actionName]) {
      actions[actionName]?.reset().fadeIn(0.3).play();
    }
  }, [avatarState, actions]);

  return (
    <group ref={group}>
      <primitive object={scene} scale={1.8} position={[0, -1.6, 0]} />
    </group>
  );
}
```

**`frontend/src/features/avatar/AvatarScene.tsx`**
```tsx
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, ContactShadows } from "@react-three/drei";
import { Suspense } from "react";
import { AvatarModel } from "./AvatarModel";
import { useAvatarStore } from "./useAvatarStore";

const STATE_COLORS: Record<string, string> = {
  IDLE: "#6366f1",
  SPEAKING: "#10b981",
  LISTENING: "#3b82f6",
  THINKING: "#f59e0b",
};

export default function AvatarScene() {
  const avatarState = useAvatarStore((s) => s.state);

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      {/* State indicator */}
      <div style={{
        position: "absolute", top: 12, left: "50%", transform: "translateX(-50%)",
        background: STATE_COLORS[avatarState] + "33",
        border: `1px solid ${STATE_COLORS[avatarState]}`,
        color: STATE_COLORS[avatarState],
        borderRadius: 20, padding: "4px 14px",
        fontSize: "0.75rem", fontWeight: 600, zIndex: 10,
        textTransform: "uppercase", letterSpacing: "0.05em",
      }}>
        {avatarState}
      </div>

      <Canvas
        camera={{ position: [0, 0.2, 2.5], fov: 40 }}
        style={{ background: "radial-gradient(ellipse at center, #1e1b4b 0%, #0f0f1a 100%)" }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[2, 4, 2]} intensity={1.5} />
        <pointLight position={[-2, 2, -2]} intensity={0.5} color="#6366f1" />

        <Suspense fallback={null}>
          <AvatarModel />
          <ContactShadows position={[0, -1.6, 0]} opacity={0.4} scale={3} blur={2} />
          <Environment preset="studio" />
        </Suspense>

        <OrbitControls
          enablePan={false}
          enableZoom={false}
          minPolarAngle={Math.PI / 3}
          maxPolarAngle={Math.PI / 1.8}
        />
      </Canvas>
    </div>
  );
}
```

**`frontend/src/features/avatar/index.ts`**
```ts
export { default as AvatarScene } from "./AvatarScene";
export { useAvatarStore } from "./useAvatarStore";
export type { AvatarState } from "./useAvatarStore";
```

---

## Task 4: Create Interview Service

**File:** `frontend/src/services/interviewService.ts` (create new file)

```ts
import apiClient from "./api";

export interface Question {
  id: string;
  text: string;
  question_type: string;
  difficulty: string;
  audio_url?: string;
}

export interface StartInterviewResponse {
  session_id: string;
  role: string;
  mode: string;
  total_questions: number;
  first_question: Question;
}

export interface AnswerResponse {
  score: number;
  feedback: string;
  strengths: string[];
  improvements: string[];
  next_question: Question | null;
  session_complete: boolean;
}

export interface ResultsResponse {
  session_id: string;
  role: string;
  mode: string;
  overall_score: number;
  total_questions: number;
  questions: Array<{
    question: string;
    answer: string;
    score: number;
    feedback: string;
    strengths: string[];
    improvements: string[];
  }>;
  coaching_tips: string[];
}

export const interviewService = {
  start: (role: string, mode: string, resume_id?: string) =>
    apiClient.post<StartInterviewResponse>("/interview/start", { role, mode, resume_id })
      .then(r => r.data),

  answer: (session_id: string, question_id: string, answer_text: string) =>
    apiClient.post<AnswerResponse>("/interview/answer", { session_id, question_id, answer_text })
      .then(r => r.data),

  results: (session_id: string) =>
    apiClient.get<ResultsResponse>(`/interview/${session_id}/results`)
      .then(r => r.data),
};
```

---

## Task 5: Update `InterviewPage.tsx` — Wire to Real API

Replace the hardcoded `sampleQuestions` and stage logic with real API calls. The key changes are in the `SetupStage` and session logic.

Find in `InterviewPage.tsx`:
```tsx
function SetupStage({ onStart }: { onStart: (mode: Mode, role: string) => void }) {
```

Change `onStart` call inside to use the real service. Add to the top of `InterviewPage.tsx`:
```tsx
import { interviewService, type Question } from "../services/interviewService";
import { AvatarScene, useAvatarStore } from "../features/avatar";
```

Add state in `InterviewPage` component (where the stage is managed):
```tsx
const [sessionId, setSessionId] = useState<string | null>(null);
const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
const [totalQuestions, setTotalQuestions] = useState(0);
const [questionIndex, setQuestionIndex] = useState(0);
const [isLoading, setIsLoading] = useState(false);
const setAvatarState = useAvatarStore((s) => s.setState);

const handleStart = async (mode: Mode, role: string) => {
  setIsLoading(true);
  try {
    const data = await interviewService.start(role, mode);
    setSessionId(data.session_id);
    setCurrentQuestion(data.first_question);
    setTotalQuestions(data.total_questions);
    setAvatarState("SPEAKING");
    setStage("session");
  } catch (e) {
    console.error("Failed to start interview", e);
  } finally {
    setIsLoading(false);
  }
};

const handleAnswer = async (answerText: string) => {
  if (!sessionId || !currentQuestion) return;
  setIsLoading(true);
  setAvatarState("THINKING");
  try {
    const data = await interviewService.answer(sessionId, currentQuestion.id, answerText);
    setQuestionIndex(i => i + 1);
    if (data.session_complete || !data.next_question) {
      setStage("completed");
      setAvatarState("IDLE");
    } else {
      setCurrentQuestion(data.next_question);
      setAvatarState("SPEAKING");
    }
  } finally {
    setIsLoading(false);
  }
};
```

---

## Task 6: Add Avatar to Interview Session Stage

In the session stage JSX of `InterviewPage.tsx`, add the avatar panel:

```tsx
{/* Avatar panel — add this above the question card */}
<div style={{ height: 300, borderRadius: 16, overflow: "hidden", marginBottom: "1.5rem" }}>
  <AvatarScene />
</div>
```

---

## ✅ How to Test

```bash
cd frontend
npm run dev
# Navigate to /interview
# You should see the avatar rendered in the setup and session stages
```

---

## 📤 How to Create Your PR

```bash
git add .
git commit -m "feat: 3D avatar scene + interview API integration"
git push origin feat/3d-avatar-interview-ui
```

GitHub → New PR:
- **Base:** `develop` | **Compare:** `feat/3d-avatar-interview-ui`
- **Title:** `feat: 3D AI interviewer + real interview session API`
- Tag **Shri** as reviewer (she built the API you're consuming)

---
---

## 🔗 Shared API Contract (ALL TEAMMATES READ)

```
POST /api/v1/resume/upload          → Upasna builds
GET  /api/v1/resume/:id/profile     → Upasna builds

POST /api/v1/interview/start        → Shri builds
POST /api/v1/interview/answer       → Shri builds
GET  /api/v1/interview/:id/results  → Shri builds

frontend/src/services/interviewService.ts → Tanushri builds
frontend/src/features/avatar/             → Tanushri builds
frontend/src/features/resume/             → Upasna builds
```

> ⛔ **No one changes these endpoint URLs or response shapes without a group message first.**

---

## 🚦 Migration Coordination

Only one Alembic migration at a time:
```
Order: Upasna first → Shri second
Upasna: alembic revision --autogenerate -m "add_resumes_table"
Shri:   alembic revision --autogenerate -m "add_interview_tables"
```
Message the group when you're done so the next person can run theirs.

---

## 📅 Monday Delivery Checklist

| | Tanushri | Shri | Upasna | Sansriti |
|---|---|---|---|---|
| Branch created | ☐ | ☐ | ☐ | ☐ |
| Code written + tested locally | ☐ | ☐ | ☐ | ☐ |
| PR opened to `develop` | ☐ | ☐ | ☐ | ☐ |
| Teammate tagged as reviewer | ☐ | ☐ | ☐ | ☐ |

> **Message the group when your PR is open** so we can review before Monday standup!
