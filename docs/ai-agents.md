# Intervia — AI Agent Architecture

## Overview

Intervia uses a **multi-agent architecture** built on [LangGraph](https://github.com/langchain-ai/langgraph) for stateful, adaptive interview orchestration. Each agent is a focused module responsible for a specific aspect of the interview pipeline.

---

## Agent Inventory

| Agent | Phase | Responsibility |
|-------|-------|---------------|
| `ResumeAgent` | 2 | Parse resume and extract structured candidate profile |
| `JobAgent` | 3 | Parse job description and extract requirements |
| `PlannerAgent` | 6 | Create interview strategy from candidate + job profiles |
| `InterviewerAgent` | 7 | Orchestrate adaptive interview (LangGraph graph) |
| `TechnicalAgent` | 7 | Generate technical questions and follow-ups |
| `BehavioralAgent` | 7 | Generate behavioral / STAR-method questions |
| `EvaluationAgent` | 9 | Evaluate each answer with structured scores |
| `VerificationAgent` | 10 | Verify skills claimed on the resume |
| `CommunicationAgent` | 13 | Analyze communication patterns from transcripts |
| `CoachAgent` | 15 | Generate personalized improvement plan |

---

## Interview Orchestration Graph (Phase 7)

The `InterviewerAgent` uses a LangGraph `StateGraph` with the following nodes:

```
START
  │
  ▼
[initialize_interview]
  │
  ▼
[analyze_state]  ←──────────────────────────────────┐
  │                                                  │
  ├─→ [generate_question] ─────────────────────────→ [record_answer]
  │        │                                         │
  │        ▼                                         ▼
  │   [deliver_question]               [evaluate_answer]
  │                                         │
  ├─→ [generate_follow_up]            [update_skill_estimates]
  │                                         │
  ├─→ [increase_difficulty]           [update_state]
  │                                         │
  ├─→ [decrease_difficulty]           ──────┘
  │
  ├─→ [change_topic]
  │
  └─→ [end_interview]
           │
           ▼
        [FINISH]
```

### State Schema

```python
class InterviewState(TypedDict):
    # Candidate context
    candidate_profile: CandidateProfile
    job_profile: Optional[JobProfile]

    # Interview configuration
    interview_type: InterviewType
    difficulty: int           # 1-10
    target_duration: int      # minutes
    elapsed_time: int         # seconds

    # Current state
    current_section: str
    current_question: Optional[str]
    question_count: int
    section_question_count: int

    # History
    previous_questions: List[str]
    previous_answers: List[str]
    previous_evaluations: List[AnswerEvaluation]

    # Adaptive tracking
    skill_estimates: Dict[str, SkillEstimate]
    weak_areas: List[str]
    strong_areas: List[str]

    # Decision
    next_action: Literal[
        "ask_question",
        "ask_follow_up",
        "increase_difficulty",
        "decrease_difficulty",
        "change_topic",
        "end_interview",
    ]
```

---

## Agent Base Pattern

All agents follow this interface:

```python
# backend/app/agents/base.py

class BaseAgent:
    """Base class for all Intervia agents."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = self._init_llm()
        self.system_prompt = self._load_system_prompt()

    def _init_llm(self) -> BaseChatModel:
        if self.settings.LLM_PROVIDER == "gemini":
            return ChatGoogleGenerativeAI(model=self.settings.LLM_MODEL)
        return ChatOpenAI(model=self.settings.LLM_MODEL)

    def _load_system_prompt(self) -> str:
        """Load prompt from dedicated prompts/ file."""
        raise NotImplementedError

    async def run(self, input: BaseModel) -> BaseModel:
        raise NotImplementedError
```

---

## Prompt Management

All system prompts are stored in dedicated files under `backend/app/agents/<agent_name>/prompts/`:

```
backend/app/agents/
├── interviewer_agent/
│   └── prompts/
│       ├── system.txt
│       ├── question_generation.txt
│       └── follow_up.txt
├── evaluation_agent/
│   └── prompts/
│       ├── system.txt
│       └── evaluation.txt
└── coach_agent/
    └── prompts/
        ├── system.txt
        └── coaching_plan.txt
```

This keeps prompts version-controlled and easy to iterate on without touching Python code.

---

## Structured Outputs

All agents use Pydantic structured outputs via `with_structured_output()`:

```python
# Ensures LLM responses are always valid Pydantic models
result = llm.with_structured_output(AnswerEvaluation).invoke(prompt)
```

This prevents hallucinated or malformed evaluation data.

---

## RAG Integration

The `InterviewerAgent` and `TechnicalAgent` retrieve relevant resume context before generating questions:

```python
# Phase 4 RAG service call
context = await rag_service.retrieve_resume_context(
    user_id=state["candidate_profile"].user_id,
    query=f"questions about {current_skill}",
    top_k=5,
)
```

This grounds questions in the actual resume content rather than generating generic questions.

---

## Evaluation Dimensions

The `EvaluationAgent` produces structured per-answer scores:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Technical Accuracy | 30% | Correctness of technical claims |
| Communication | 20% | Clarity, conciseness, structure |
| Behavioral | 15% | STAR method, examples, context |
| Problem Solving | 15% | Reasoning process, approach |
| Resume Knowledge | 10% | Awareness of own experience |
| Answer Quality | 10% | Relevance, depth |

> [!NOTE]
> Weights are configurable in Phase 14. Scores are **interview-readiness indicators** only.

---

## Skill Verification Logic

```
Resume: "Advanced Kubernetes"
        ↓
VerificationAgent generates 3 targeted questions:
  1. "Explain the difference between a Deployment and StatefulSet."
  2. "How does Kubernetes handle pod scheduling?"
  3. "Describe a production issue you debugged in a Kubernetes cluster."
        ↓
Answers evaluated against expected Advanced-level responses
        ↓
Output:
{
  "skill": "Kubernetes",
  "claimed_level": "Advanced",
  "observed_level": "Intermediate",
  "confidence": 0.78,
  "evidence": [
    "Correctly explained Deployment vs StatefulSet.",
    "Could not describe advanced scheduling scenarios.",
    "Lacked production debugging examples."
  ]
}
```

> [!IMPORTANT]
> The system uses language like "Observed proficiency appears below claimed level" rather than making judgments about candidate honesty.
