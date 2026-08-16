# Atiya - AI Revenue Management System (Learn & Build Project)

**Mission:** Build a production-quality agentic AI pricing system for small-medium motels while learning 510+ AI/agentic engineering skills.

---

## Quick Start

```bash
# Resume from where you left off
/go-atiya
```

### Running the code (from learn-and-build/)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# Run the test suite
python -m pytest -q

# Configure LLM provider keys (see .env.example)
cp .env.example .env   # then fill in GEMINI_API_KEY / GROQ_API_KEY
```

---

## What Makes This Agentic (Not Just Automation)

```
Traditional RMS:  Data → Algorithm → Price → Dashboard
Atiya:            Goal → Hypothesize → Investigate → Reason → Act/Escalate → Learn
```

The agent:
- Forms and tests hypotheses ("Why is demand low?")
- Investigates using tools (competitors, events, weather)
- Reasons about evidence with confidence scoring
- Decides: act autonomously OR ask owner
- Learns from outcomes and owner feedback

---

## Project Structure

```
learn-and-build/
├── README.md               # This file - project overview
├── REQUIREMENTS.md         # Complete product requirements
├── DESIGN.md              # Complete agent architecture
├── STATE.md               # Current Atiya implementation progress
├── DECISIONS.md           # Architecture decisions (ADRs)
│
├── AI Bible/              # Master reference documents
│   ├── AI_Learning_v2.md      # Original curriculum (28 skills, 545 subskills)
│   └── CLAUDE_LEARNING.md     # Claude Code topics reference
│
├── learning-docs/         # Learning artifacts
│   ├── plan_and_progress/     # Learning tracking
│   │   ├── LEARNING_PLAN.md   # Skill-level progress (28 skills)
│   │   └── LEARNING_PROGRESS.md  # Subskill-level tracking (545 subskills)
│   ├── all-topics/           # Learning documents (created as you progress)
│   ├── phase-1/              # (deprecated structure)
│   └── ...
│
├── src/                   # Implementation (created as you build)
│   ├── llm/              # LLM gateway (done), prompts, caching
│   ├── agent/            # Agent orchestration
│   ├── database/         # PostgreSQL models
│   ├── ui/               # Streamlit interface
│   └── ...
│
├── tests/                 # Test suites (mirrors src/ layout)
├── evals/                 # Evaluation datasets
└── .claude/
    └── skills/
        ├── go-atiya/              # Track progress, guide what's next
        └── learn-and-implement/   # Deep-learn a concept
```

---

## Essential Documents

| File | Purpose |
|------|---------|
| **REQUIREMENTS.md** | Product vision, user workflows, features, API specs |
| **DESIGN.md** | Agent architecture, agentic patterns, implementation design |
| **STATE.md** | Atiya implementation progress, next tasks, blockers |
| **DECISIONS.md** | Architecture decisions with rationale |
| **learning-docs/plan_and_progress/LEARNING_PLAN.md** | 28 skills, skill-level progress tracking |
| **learning-docs/plan_and_progress/LEARNING_PROGRESS.md** | 545 subskills, detailed progress tracking |
| **AI Bible/AI_Learning_v2.md** | Master curriculum reference (all skills & subskills) |

---

## Learning Journey

**Timeline:** 28 weeks (~10 hrs/week)  
**Framework:** 23-aspect deep learning per skill  
**Output:** Production-ready system + mastery of AI/agentic engineering

### Phases

| Phase | Weeks | Focus | Milestone |
|-------|-------|-------|-----------|
| 1 | 1-5 | Foundations | Basic single-agent pricing system |
| 2 | 6-10 | Core Patterns | Stateful agent with approval gates |
| 3 | 11-16 | **Multi-Agent** | CrewAI + LangGraph implementations |
| 4 | 17-21 | Advanced | RAG + diagnostic loops |
| 5 | 22-24 | Production | Deployed system with monitoring |
| 6 | 25-28 | Quality | **Production ready** ✅ |

**Phase 3 Highlight:** Implement pricing pipeline in BOTH CrewAI and LangGraph, then choose which fits better.

---

## Technology Stack

- **Server:** Oracle Cloud Free Tier (4 OCPUs, 24GB RAM, $0)
- **Orchestration:** n8n (self-hosted)
- **Database:** PostgreSQL
- **LLM:** Gemini 2.0 Flash (free) + Groq (fallback)
- **UI:** Streamlit
- **Integration:** Beds24 API (optional) or manual

---

## Key Constraints

1. **$0 Infrastructure** - Stay within free tiers
2. **Contribution Profit** - Optimize profit, not ADR/RevPAR
3. **Legal Compliance** - Built-in tax, fee, price gouging constraints
4. **Owner Control** - Confidence-based escalation, never black-box

---

## Development Principles

### Before Implementing
1. Read **STATE.md** to understand current progress
2. Check **DESIGN.md** for architecture decisions
3. Verify functionality isn't already implemented
4. Map task to learning concept in **LEARNING_PLAN.md**

### During Implementation
- Prefer incremental changes over large rewrites
- Never duplicate existing functionality
- Add/update tests for behavioral changes
- Don't introduce AI concepts only for learning if they make the agent worse

### After Implementation
- Run relevant tests/evaluations
- Update **STATE.md** with progress
- Update **LEARNING_PLAN.md** skill status
- Document decisions in **DECISIONS.md** if architecture changed

---

## Available Skills

### `/go-atiya`
Track progress through 510+ AI concepts - Shows where you are, what's next, guides your learning journey

### `/learn-and-implement [concept]`
Master a concept in depth - Teaches through conversation, creates learning doc + slides

---

## Current Status

See **STATE.md** for:
- Current phase and week
- Skills completed vs remaining
- Next tasks
- Recent progress
- Known issues

---

## Learning Framework: 23 Aspects Per Skill

For each of 30 skills, create a deep learning document covering:

1. Problem & Purpose
2. When to Use / Not Use
3. Core Mechanics
4. Inputs / Outputs / Contracts
5. Architecture Placement
6. Implementation Patterns
7. Configuration & Tuning
8. Trade-offs
9. Failure Modes
10. Error Handling & Recovery
11. Testing Strategy
12. Evaluation & Metrics
13. Observability
14. Performance & Scalability
15. Cost
16. Security & Safety
17. Reliability
18. Production Deployment
19. Versioning & Change Management
20. CI/CD Integration
21. Debugging / Troubleshooting
22. Real-World Design Decisions
23. Production Anti-Patterns
24. **Hands-on Implementation** (build in Atiya)
25. **Production Scenario Testing** (test with failures, load, bad inputs)


---

## Production Readiness Goals (Week 28)

- [ ] RevPAR improvement: >10%
- [ ] Recommendation acceptance: >70%
- [ ] Confidence calibration: 85% conf = 85% correct (±5%)
- [ ] Cost per recommendation: <$0.10
- [ ] Latency: <30s end-to-end
- [ ] Uptime: 99%+
- [ ] Test coverage: >80%
- [ ] Security: OWASP Top 10 mitigated
- [ ] All 30 skills documented with 23 aspects

---

## Next Steps

1. Run `/continue` to resume from current state
2. Or start Phase 1, Week 1: Skill 1 (Model/Provider Abstraction)
3. Create learning doc, implement, test, document

**Good luck on your 28-week journey to production! 🚀**
