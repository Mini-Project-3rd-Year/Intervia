# Intervia — Database Schema

## Database

- **Engine**: PostgreSQL 16
- **Extension**: pgvector (vector similarity search)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic

---

## Setup (Phase 5)

```sql
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## Core Tables

### `users`

```sql
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email         VARCHAR(255) UNIQUE NOT NULL,
  full_name     VARCHAR(255),
  avatar_url    TEXT,
  hashed_password TEXT,      -- NULL if using Supabase Auth
  supabase_id   UUID UNIQUE, -- Supabase Auth user ID
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### `resumes`

```sql
CREATE TABLE resumes (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  filename      VARCHAR(255) NOT NULL,
  file_url      TEXT NOT NULL,
  raw_text      TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### `candidate_profiles`

```sql
CREATE TABLE candidate_profiles (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  resume_id     UUID UNIQUE REFERENCES resumes(id) ON DELETE CASCADE,
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  skills        JSONB DEFAULT '[]',
  projects      JSONB DEFAULT '[]',
  experience    JSONB DEFAULT '[]',
  education     JSONB DEFAULT '[]',
  certifications JSONB DEFAULT '[]',
  achievements  JSONB DEFAULT '[]',
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### `job_descriptions`

```sql
CREATE TABLE job_descriptions (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  role          VARCHAR(255),
  raw_text      TEXT NOT NULL,
  required_skills JSONB DEFAULT '[]',
  preferred_skills JSONB DEFAULT '[]',
  matched_skills JSONB DEFAULT '[]',
  missing_skills JSONB DEFAULT '[]',
  skill_gaps    JSONB DEFAULT '[]',
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### `interviews`

```sql
CREATE TABLE interviews (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  resume_id     UUID REFERENCES resumes(id),
  job_id        UUID REFERENCES job_descriptions(id),
  type          VARCHAR(50) NOT NULL,  -- hr | technical | behavioral | etc.
  difficulty    SMALLINT DEFAULT 5,    -- 1-10
  duration      INTEGER,              -- planned minutes
  status        VARCHAR(50) DEFAULT 'scheduled',
  strategy      JSONB,                -- interview plan from planner agent
  started_at    TIMESTAMPTZ,
  completed_at  TIMESTAMPTZ,
  overall_score NUMERIC(5,2),
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### `interview_questions`

```sql
CREATE TABLE interview_questions (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  interview_id  UUID REFERENCES interviews(id) ON DELETE CASCADE,
  question      TEXT NOT NULL,
  category      VARCHAR(100),  -- technical | behavioral | hr | etc.
  difficulty    SMALLINT,
  source        VARCHAR(100),  -- resume_based | job_based | adaptive | etc.
  sequence_number INTEGER NOT NULL,
  asked_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### `interview_answers`

```sql
CREATE TABLE interview_answers (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  question_id   UUID REFERENCES interview_questions(id) ON DELETE CASCADE,
  transcript    TEXT,
  audio_url     TEXT,         -- only if user enabled recording
  duration_seconds INTEGER,
  submitted_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### `interview_evaluations`

```sql
CREATE TABLE interview_evaluations (
  id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  answer_id        UUID UNIQUE REFERENCES interview_answers(id) ON DELETE CASCADE,
  relevance        NUMERIC(5,2),
  technical_accuracy NUMERIC(5,2),
  technical_depth  NUMERIC(5,2),
  clarity          NUMERIC(5,2),
  conciseness      NUMERIC(5,2),
  structure        NUMERIC(5,2),
  behavioral_score NUMERIC(5,2),
  feedback         TEXT,
  evidence         JSONB DEFAULT '[]',
  created_at       TIMESTAMPTZ DEFAULT NOW()
);
```

### `skill_assessments`

```sql
CREATE TABLE skill_assessments (
  id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  interview_id   UUID REFERENCES interviews(id) ON DELETE CASCADE,
  skill          VARCHAR(255) NOT NULL,
  claimed_level  VARCHAR(100),
  observed_level VARCHAR(100),
  confidence     NUMERIC(5,4),  -- 0.0 to 1.0
  evidence       JSONB DEFAULT '[]',
  created_at     TIMESTAMPTZ DEFAULT NOW()
);
```

### `communication_metrics`

```sql
CREATE TABLE communication_metrics (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  answer_id         UUID REFERENCES interview_answers(id) ON DELETE CASCADE,
  speaking_rate     NUMERIC(6,2),    -- words per minute
  response_duration INTEGER,         -- seconds
  filler_words      INTEGER,
  pause_count       INTEGER,
  repetition_count  INTEGER,
  answer_length     INTEGER,         -- word count
  created_at        TIMESTAMPTZ DEFAULT NOW()
);
```

### `resume_embeddings` (pgvector)

```sql
CREATE TABLE resume_embeddings (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  resume_id   UUID REFERENCES resumes(id) ON DELETE CASCADE,
  user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
  chunk_text  TEXT NOT NULL,
  chunk_index INTEGER,
  embedding   vector(768),           -- text-embedding-004 dimension
  metadata    JSONB DEFAULT '{}',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- IVFFlat index for fast approximate nearest-neighbor search
CREATE INDEX resume_embeddings_embedding_idx
  ON resume_embeddings
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
```

---

## Readiness Score View

```sql
CREATE VIEW interview_readiness_scores AS
SELECT
  i.id as interview_id,
  i.user_id,
  ROUND(
    AVG(ie.technical_accuracy) * 0.30 +
    AVG(ie.clarity)            * 0.20 +
    AVG(ie.behavioral_score)   * 0.15 +
    -- problem_solving derived from technical_depth
    AVG(ie.technical_depth)    * 0.15 +
    -- resume_knowledge and answer_quality
    AVG(ie.relevance)          * 0.10 +
    AVG(ie.structure)          * 0.10,
  2) AS overall_score
FROM interviews i
JOIN interview_questions q ON q.interview_id = i.id
JOIN interview_answers a ON a.question_id = q.id
JOIN interview_evaluations ie ON ie.answer_id = a.id
GROUP BY i.id, i.user_id;
```

> [!NOTE]
> Score weights are configurable via environment variables in Phase 14.
> The readiness score is an **interview-readiness indicator only** and does not predict hiring outcomes.
