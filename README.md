# Intervia — AI-Powered Adaptive Interview Platform

> **Interview smarter. Improve faster.**

Intervia is a production-grade AI platform that conducts personalized adaptive interviews for students and job seekers. It analyzes your resume and job description, interviews you with a 3D AI avatar, evaluates your answers across multiple dimensions, and coaches you with evidence-based, personalized improvement plans.

---

## ✨ Features

| Feature | Description | Phase |
|---------|-------------|-------|
| 🧠 Resume Intelligence | AI-powered PDF parsing + structured candidate profile extraction | 2 |
| 🎯 Job Matching | Resume vs. Job skill gap analysis | 3 |
| 🔍 RAG System | Resume-grounded semantic retrieval for interview context | 4 |
| 🤖 Adaptive Interview Agent | LangGraph-powered stateful interview with dynamic difficulty | 7 |
| 🎭 Interview Modes | HR, Technical, Behavioral, Mixed, Pressure, Job-Specific | 8 |
| ✅ Skill Verification | Tests claimed resume skills through targeted questions | 10 |
| 🗣️ Voice Interaction | STT → AI → TTS real-time pipeline | 11 |
| 🎬 3D AI Interviewer | Three.js avatar with lip-sync and state animations | 12 |
| 📊 Communication Analytics | WPM, pauses, filler words, response duration | 13 |
| 🏆 Readiness Score | Multi-dimensional interview readiness indicator | 14 |
| 💡 AI Career Coach | Evidence-based personalized improvement plan | 15 |
| 📈 Progress Tracking | Interview history, skill trends, improvement over time | 16 |
| 🎞️ Interview Replay | Annotated transcript timeline with audio | 17 |
| 🖥️ Dashboard | Overview, score charts, skill radar, weak areas | 18 |

---

## 🏗️ Architecture

```
                    ┌───────────────────┐
                    │      USER         │
                    └─────────┬─────────┘
                              │ Resume + Job
                              ▼
                 ┌──────────────────────────┐
                 │   Candidate Intelligence  │
                 └──────────┬───────────────┘
                            ▼
                 ┌──────────────────────────┐
                 │   LangGraph Orchestrator  │
                 └──────────┬───────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
       Resume Agent    Technical Agent  Behavioral Agent
                            │
                            ▼
                   ┌─────────────────┐
                   │  Interview Agent │
                   └────────┬────────┘
                            │
                     STT ←──┴──→ TTS
                            │
                       3D INTERVIEWER
                            │
                   Answer Evaluation
                            │
                   Readiness Score → AI Coach
```

See [`docs/architecture.md`](docs/architecture.md) for the full diagram.

---

## 🛠️ Tech Stack

### Frontend
- **React 18** + **TypeScript** + **Vite**
- **Tailwind CSS v4** — utility-first design system
- **React Router v6** — client-side routing
- **Three.js** + **React Three Fiber** — 3D avatar (Phase 12)
- **Zustand** — lightweight state management
- **Axios** — HTTP client

### Backend
- **Python 3.11** + **FastAPI** — async API framework
- **Pydantic v2** + **pydantic-settings** — typed config & schemas
- **LangGraph** — stateful AI agent orchestration (Phase 7)
- **Gemini 2.0 Flash** / **OpenAI** — LLM
- **SQLAlchemy 2.0** + **asyncpg** — async database ORM
- **Alembic** — database migrations
- **structlog** — structured logging

### Database
- **PostgreSQL 16** + **pgvector** — unified relational + vector store
- **Supabase** — auth, realtime, and managed hosting option

### Voice
- **Google Speech-to-Text** / **Deepgram** — STT
- **Google TTS** / **ElevenLabs** — TTS
- **Web Audio API** — browser audio handling

### DevOps
- **Docker** + **docker-compose** — containerized development
- **GitHub Actions** — CI/CD

---

## 🚀 Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 16+ with pgvector (or use Docker)
- Git

### 1. Clone the repository

```bash
git clone https://github.com/your-username/intervia.git
cd intervia
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

### 3. Start with Docker (recommended)

```bash
docker-compose up --build
```

This starts:
- PostgreSQL with pgvector on port 5432
- FastAPI backend on port 8000
- Vite frontend on port 5173

### 4. Or run locally

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

### 5. Verify

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Health: http://localhost:8000/api/v1/health
- API Docs: http://localhost:8000/docs

---

## 🧪 Running Tests

### Backend

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### Frontend (type-check)

```bash
cd frontend
npm run build
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in every value before running the app.
**Never commit `.env` to version control** — it is listed in `.gitignore`.

```bash
cp .env.example .env
```

---

### 🖥️ Application

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Runtime environment: `development` \| `staging` \| `production` |
| `APP_VERSION` | `0.1.0` | Displayed in API responses and logs |
| `DEBUG` | `true` | Enables FastAPI debug mode and verbose logging. **Set `false` in production.** |

---

### 🌐 Backend Server

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_HOST` | `0.0.0.0` | Host to bind the FastAPI server |
| `BACKEND_PORT` | `8000` | Port for the FastAPI server |
| `BACKEND_RELOAD` | `true` | Hot-reload on code changes (dev only) |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | Comma-separated list of allowed CORS origins |

---

### 🗄️ Database

| Variable | Example | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:password@localhost:5432/intervia` | Async PostgreSQL connection string used by SQLAlchemy. Requires `asyncpg` driver prefix. |
| `PGVECTOR_CONNECTION_URL` | `postgresql://postgres:password@localhost:5432/intervia` | Sync connection used by pgvector for raw SQL operations. |

> **How to get it:** Run PostgreSQL locally or use the connection string from your Supabase project under  
> **Project Settings → Database → Connection string → URI**.

> **pgvector:** The `CREATE EXTENSION IF NOT EXISTS vector;` migration runs automatically via Alembic. Ensure your PostgreSQL 16+ instance has pgvector installed.

---

### 🔐 Supabase (Auth + Managed Database)

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your project URL — `https://<project-id>.supabase.co` |
| `SUPABASE_ANON_KEY` | Public anon key — safe to use in the browser |
| `SUPABASE_SERVICE_ROLE_KEY` | Secret service role key — **backend only, never expose to the browser** |

> **How to get it:**  
> 1. Go to [supabase.com](https://supabase.com) → New Project  
> 2. **Project Settings → API** — copy `URL`, `anon public`, and `service_role` keys

---

### 🤖 AI / LLM

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `gemini` | Which LLM to use: `gemini` \| `openai` |
| `LLM_MODEL` | `gemini-2.0-flash-exp` | Model name passed to the LLM client |
| `GEMINI_API_KEY` | — | Google Gemini API key (used when `LLM_PROVIDER=gemini`) |
| `OPENAI_API_KEY` | — | OpenAI API key (used when `LLM_PROVIDER=openai`) |

> **How to get Gemini API key:**  
> Go to [aistudio.google.com](https://aistudio.google.com) → **Get API Key** → Create key in a project

> **How to get OpenAI API key:**  
> Go to [platform.openai.com](https://platform.openai.com) → **API keys** → Create new secret key

---

### 🧮 Embeddings

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL` | `models/text-embedding-004` | Google embedding model (or `text-embedding-ada-002` for OpenAI) |
| `EMBEDDING_DIMENSION` | `768` | Dimension of the embedding vectors. Must match the pgvector column size. |

> **Note:** If you switch embedding models, the `EMBEDDING_DIMENSION` must be updated and a new Alembic migration must be created to resize the pgvector column.

---

### 🗣️ Voice / Speech

| Variable | Default | Description |
|----------|---------|-------------|
| `STT_PROVIDER` | `google` | Speech-to-Text provider: `google` \| `deepgram` \| `openai-whisper` |
| `GOOGLE_STT_API_KEY` | — | API key for Google Cloud Speech-to-Text |
| `TTS_PROVIDER` | `google` | Text-to-Speech provider: `google` \| `elevenlabs` \| `openai` |
| `GOOGLE_TTS_API_KEY` | — | API key for Google Cloud Text-to-Speech |
| `ELEVENLABS_API_KEY` | — | ElevenLabs API key (optional premium TTS) |

> **How to get Google STT/TTS keys:**  
> Go to [console.cloud.google.com](https://console.cloud.google.com) → Enable **Speech-to-Text API** and **Text-to-Speech API** → Create a service account → Download JSON key or copy the API key.

> **How to get ElevenLabs key:**  
> Go to [elevenlabs.io](https://elevenlabs.io) → Profile → API Keys

---

### 🔑 Auth / JWT

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | *(must set)* | Secret used to sign JWT tokens. Generate with: `openssl rand -hex 32` |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime in days |

> ⚠️ **Security:** Change `JWT_SECRET_KEY` before deploying. Use a randomly generated 256-bit key.  
> ```bash
> openssl rand -hex 32
> ```

---

### 📁 File Storage

| Variable | Default | Description |
|----------|---------|-------------|
| `STORAGE_PROVIDER` | `local` | Where to store uploaded files: `local` \| `s3` \| `supabase-storage` |
| `LOCAL_STORAGE_PATH` | `./uploads` | Local directory for file storage (development only) |
| `MAX_UPLOAD_SIZE_MB` | `10` | Maximum allowed upload size in megabytes |
| `AWS_ACCESS_KEY_ID` | — | AWS access key (required when `STORAGE_PROVIDER=s3`) |
| `AWS_SECRET_ACCESS_KEY` | — | AWS secret key |
| `AWS_REGION` | `us-east-1` | AWS region for the S3 bucket |
| `S3_BUCKET_NAME` | — | Name of the S3 bucket for uploads |

---

### 🖼️ Frontend (Vite)

These variables are exposed to the browser via Vite's `import.meta.env`. They **must** be prefixed with `VITE_`.

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend base URL. In production, set to your deployed API URL. |
| `VITE_SUPABASE_URL` | — | Supabase project URL (same as `SUPABASE_URL`) |
| `VITE_SUPABASE_ANON_KEY` | — | Supabase anon key (same as `SUPABASE_ANON_KEY`) |
| `VITE_APP_ENV` | `development` | Frontend environment label |

> ⚠️ **Never put `SUPABASE_SERVICE_ROLE_KEY`, `JWT_SECRET_KEY`, or any LLM API key in a `VITE_` variable** — they will be bundled into the public JavaScript and visible to anyone.

---

### Minimum Viable `.env` (to run locally)

To get the app running for the first time, you only need these:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/intervia
PGVECTOR_CONNECTION_URL=postgresql://postgres:password@localhost:5432/intervia

# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# AI
GEMINI_API_KEY=your-gemini-api-key
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash-exp

# Auth
JWT_SECRET_KEY=change-me-use-openssl-rand-hex-32

# Frontend
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

Voice (`GOOGLE_STT_API_KEY`, `GOOGLE_TTS_API_KEY`) and storage (`AWS_*`) settings are only required in Phase 11+ and Phase 22+ respectively.

---

## 📁 Project Structure

```
intervia/
├── frontend/               # React + TypeScript + Vite
│   └── src/
│       ├── components/     # Shared UI components
│       ├── pages/          # Route-level pages
│       ├── features/       # Feature modules
│       ├── services/       # API client
│       ├── store/          # Zustand state
│       └── types/          # TypeScript types
│
├── backend/                # FastAPI + Python
│   └── app/
│       ├── api/v1/         # HTTP route handlers
│       ├── agents/         # LangGraph AI agents
│       ├── rag/            # Retrieval-augmented generation
│       ├── speech/         # STT / TTS services
│       ├── evaluation/     # Scoring engine
│       ├── models/         # SQLAlchemy ORM models
│       ├── schemas/        # Pydantic schemas
│       ├── services/       # Business logic
│       └── core/           # Config, logging
│
├── docs/                   # Documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 📊 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/resumes` | Upload resume |
| GET | `/api/v1/resumes` | List resumes |
| POST | `/api/v1/jobs/analyze` | Analyze job description |
| POST | `/api/v1/interviews` | Create interview |
| WS | `/ws/interview/{id}` | Real-time interview |

Full API reference: [`docs/api.md`](docs/api.md)

---

## 🗺️ Development Roadmap

```
Phase 0  ✅  Project Foundation
Phase 1  🔲  Authentication
Phase 2  🔲  Resume Intelligence
Phase 3  🔲  Job Description Intelligence
Phase 4  🔲  RAG System
Phase 5  🔲  Interview Database
Phase 6  🔲  Interview Planner Agent
Phase 7  🔲  Adaptive Interview Agent
Phase 8  🔲  Interview Modes
Phase 9  🔲  Evaluation Engine
Phase 10 🔲  Skill Verification
Phase 11 🔲  Voice Interaction
Phase 12 🔲  3D AI Interviewer
Phase 13 🔲  Communication Analytics
Phase 14 🔲  Readiness Engine
Phase 15 🔲  AI Coach
Phase 16 🔲  Interview Memory
Phase 17 🔲  Interview Replay
Phase 18 🔲  Dashboard
Phase 19 🔲  UI Polish
Phase 20 🔲  Testing
Phase 21 🔲  Security
Phase 22 🔲  Deployment
Phase 23 🔲  Evaluation Experiment
Phase 24 🔲  Final Documentation
```

---

## 🔒 Security

- No API keys or credentials committed to source control
- CORS restricted to configured origins
- File uploads validated for type (PDF only) and size (max 10MB)
- All user data isolated by user ID
- Evaluation scores described as **interview-readiness indicators only**
- Audio recording requires explicit user consent
- See [`docs/security.md`](docs/security.md) (Phase 21)

---

## 🤝 Contributing

This is a structured 24-phase project. Each phase is independently reviewable.

- **Architecture:** [`docs/architecture.md`](docs/architecture.md)
- **Git & GitHub Workflow:** [`docs/contribution.md`](docs/contribution.md) — **read this before starting any work**
- **AI Agent Design:** [`docs/ai-agents.md`](docs/ai-agents.md)
- **API Reference:** [`docs/api.md`](docs/api.md)

---

## 📄 License

MIT License — see `LICENSE` for details.

---

*Intervia — Built with React, FastAPI, LangGraph, and Gemini AI*