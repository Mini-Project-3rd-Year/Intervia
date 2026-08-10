# Intervia — System Architecture

## Overview

Intervia is an AI-powered adaptive interview and career coaching platform built as a modular, full-stack application. The system uses a multi-agent AI architecture, retrieval-augmented generation (RAG), and a 3D conversational interface to deliver personalized interview preparation.

---

## High-Level Architecture

```
                    ┌───────────────────┐
                    │      USER         │
                    └─────────┬─────────┘
                              │
                     Resume + Job Description
                              │
                              ▼
                 ┌──────────────────────────┐
                 │   Candidate Intelligence  │
                 │   (Resume + Job Agents)   │
                 └──────────┬───────────────┘
                            │
                            ▼
                 ┌──────────────────────────┐
                 │    Interview Planner      │
                 │    (LangGraph Agent)      │
                 └──────────┬───────────────┘
                            │
                            ▼
                 ┌──────────────────────────┐
                 │  LangGraph Orchestrator   │
                 └──────────┬───────────────┘
                            │
            ┌───────────────┼────────────────┐
            │               │                │
            ▼               ▼                ▼
       Resume Agent    Technical Agent   Behavioral Agent
            │               │                │
            └───────────────┼────────────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │   Interview Agent   │
                  └────────┬────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                   STT           LLM
                    │             │
                    └──────┬──────┘
                           ▼
                          TTS
                           │
                           ▼
                     3D INTERVIEWER
                     (Three.js / R3F)
                           │
                           ▼
                   ANSWER ANALYSIS
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      Technical       Communication      Behavioral
      Evaluation        Analysis          Evaluation
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                   Skill Verification
                           │
                           ▼
                 Interview Readiness Score
                           │
                           ▼
                     AI COACH
                           │
                           ▼
                  PROGRESS TRACKING
```

---

## Component Architecture

### Frontend (React + TypeScript + Vite)

```
frontend/src/
├── components/         # Shared, reusable UI components
│   ├── layout/         # Navbar, Sidebar, Footer, PageWrapper
│   └── ui/             # Button, Card, Badge, Input, Modal, etc.
├── pages/              # Route-level page components
├── features/           # Feature-scoped modules
│   ├── auth/           # Login, Register, AuthGuard
│   ├── resume/         # Upload, Parser, Profile viewer
│   ├── interview/      # Session, Question, Answer, Controls
│   ├── avatar/         # 3D avatar, animation, lip-sync
│   ├── dashboard/      # Overview, charts, history
│   └── coaching/       # Feedback, Coach, Practice plan
├── hooks/              # Custom React hooks
├── services/           # API clients (Axios + WebSocket)
├── store/              # Zustand global state
├── types/              # TypeScript interfaces and types
└── utils/              # Helper functions
```

### Backend (Python + FastAPI)

```
backend/app/
├── api/v1/             # HTTP route handlers (thin controllers)
├── agents/             # LangGraph AI agents
│   ├── resume_agent/
│   ├── job_agent/
│   ├── planner_agent/
│   ├── interviewer_agent/
│   ├── technical_agent/
│   ├── behavioral_agent/
│   ├── communication_agent/
│   ├── verification_agent/
│   ├── evaluation_agent/
│   └── coach_agent/
├── rag/                # RAG pipeline (chunking, embedding, retrieval)
├── speech/             # STT and TTS integrations
├── evaluation/         # Scoring and readiness engine
├── models/             # SQLAlchemy ORM models
├── schemas/            # Pydantic request/response schemas
├── services/           # Business logic services
├── db/                 # Database session, migrations
└── core/               # Config, logging, middleware
```

---

## Data Flow — Interview Session

```
1. User uploads Resume (PDF)
2. Resume Agent extracts structured Candidate Profile
3. User pastes Job Description
4. Job Agent extracts Job Requirements
5. RAG system embeds resume into pgvector
6. Interview Planner creates Interview Strategy
7. LangGraph Orchestrator manages interview state
8. For each turn:
   a. Interviewer Agent generates next question
   b. TTS converts question to audio
   c. 3D Avatar speaks (lip-sync)
   d. User responds via microphone
   e. STT transcribes response
   f. Answer Evaluation Agent evaluates response
   g. Skill Verification Agent updates skill estimates
   h. Interviewer Agent decides next action
9. Interview ends → Readiness Score computed
10. AI Coach generates personalized improvement plan
11. Progress tracked across sessions
```

---

## Agent Architecture (Phase 6+)

Each agent follows a consistent pattern:

```python
class BaseAgent:
    system_prompt: str      # Loaded from prompts/ file
    llm: BaseChatModel
    tools: list[BaseTool]
    state_schema: BaseModel

    async def run(self, state: InterviewState) -> AgentOutput:
        ...
```

The `InterviewerAgent` uses **LangGraph** for stateful orchestration with explicit decision nodes:

```
START
  │
  ▼
[analyze_state]
  │
  ├─→ [generate_follow_up]  (weak answer detected)
  ├─→ [increase_difficulty]  (strong answer detected)
  ├─→ [change_topic]         (topic exhausted)
  ├─→ [generate_question]    (normal flow)
  └─→ [end_interview]        (duration/section complete)
```

---

## Database Architecture

See [database.md](./database.md) for full schema.

**Primary Database**: PostgreSQL 16 with pgvector extension  
**Auth Provider**: Supabase Auth (or JWT)  
**Vector Store**: pgvector (same database)

Core tables (Phase 5+):
- `users`
- `resumes`
- `candidate_profiles`
- `job_descriptions`
- `interviews`
- `interview_questions`
- `interview_answers`
- `interview_evaluations`
- `skill_assessments`
- `resume_embeddings` (pgvector)

---

## API Design

See [api.md](./api.md) for full specification.

- Base path: `/api/v1/`
- Versioned for future compatibility
- JSON request/response bodies
- Bearer token authentication (Phase 1+)
- WebSocket connections for real-time interview (Phase 7+)

---

## Technology Decisions

| Concern | Technology | Rationale |
|---|---|---|
| Frontend framework | React + TypeScript + Vite | Fast dev, strong types, large ecosystem |
| CSS | Tailwind CSS | Utility-first, consistent design tokens |
| State management | Zustand | Lightweight, no boilerplate |
| 3D rendering | Three.js + React Three Fiber | Declarative 3D for React |
| Backend framework | FastAPI | Async, typed, auto-docs |
| AI orchestration | LangGraph | Stateful agent graphs |
| LLM | Gemini 2.0 Flash | Fast, cost-effective, multimodal |
| Database | PostgreSQL + pgvector | Unified relational + vector store |
| Auth | Supabase Auth / JWT | Managed or self-hosted options |
| Speech-to-Text | Google STT / Deepgram | High accuracy, low latency |
| Text-to-Speech | Google TTS / ElevenLabs | Natural voice synthesis |
| Deployment | Docker + docker-compose | Reproducible environments |

---

## Security Principles

- All API endpoints require authentication (Phase 1+)
- CORS restricted to known origins
- File uploads validated for type and size
- No API keys or secrets committed to source control
- Row-level security on all user data
- Candidate data never exposed across user boundaries
- Audio recordings require explicit user consent
- Evaluation scores described as interview-readiness indicators only

---

## Development Phases

| Phase | Feature |
|---|---|
| 0 | Project Foundation (current) |
| 1 | Authentication |
| 2 | Resume Intelligence |
| 3 | Job Description Intelligence |
| 4 | RAG System |
| 5 | Interview Database |
| 6 | Interview Planner Agent |
| 7 | Adaptive Interview Agent |
| 8 | Interview Modes |
| 9 | Answer Evaluation Engine |
| 10 | Skill Verification |
| 11 | Voice Interaction |
| 12 | 3D AI Interviewer |
| 13 | Communication Analytics |
| 14 | Interview Readiness Engine |
| 15 | AI Coach |
| 16 | Interview Memory |
| 17 | Interview Replay |
| 18 | Dashboard |
| 19 | UI Polish |
| 20 | Testing |
| 21 | Security |
| 22 | Docker & Deployment |
| 23 | Evaluation Experiment |
| 24 | Final Documentation |
