---
name: go-atiya
description: Build production-grade AI agent for Atiya
---

# Go Atiya - Production AI Implementation

I implement production-grade Atiya pricing agent. Simple and focused.

## Usage

```bash
/go-atiya
```

## What I Do

1. **Track implementation progress** - Read STATE.md to see what's implemented
2. **Determine next task** - Based on LEARNING_PLAN and DESIGN
3. **Suggest learning** - Throw learning command for required concept
4. **Trust you** - When you say "done learning", I implement
5. **Build production code** - Focus on perfect implementation

## How It Works

```
Read STATE.md + DESIGN.md
  ↓
Identify next Atiya implementation task
  ↓
Suggest: /learn-and-implement [concept]
  ↓
User learns (tracked separately in learn-and-build/learning-docs/plan_and_progress/LEARNING_PLAN.md)
  ↓
User says: "done" or "learned" or "ready"
  ↓
I implement production code for Atiya
  ↓
Update STATE.md with Atiya code progress
```

---

## Instructions

When user invokes `/go-atiya`:

### 1. Read Current State

Read:
- **STATE.md** - Atiya implementation progress (ONLY source of truth)
- **DESIGN.md** - Atiya architecture and design decisions
- **REQUIREMENTS.md** - Product requirements (if exists)

**Do NOT read learn-and-build/learning-docs/plan_and_progress/LEARNING_PLAN.md** - Learning tracking is separate, managed by `/learn-and-implement`

### 2. Determine Next Implementation Task

Based on STATE.md "Next Atiya Implementation Tasks" section:
- Read what's already implemented
- Read what's next to build
- Identify required concept to learn

**Implementation sequence** (from STATE.md):
- Phase 1: LLM Gateway → Prompt System → Structured Outputs → Observability
- Phase 2: State Management → Evidence Synthesis → Caching → Human-in-Loop → Error Handling
- Phase 3: Multi-Agent Orchestration (using chosen framework)
- Phase 4-6: RAG, testing, production deployment

### 3. Present to User

**Simple format:**

```
📍 Current Status
Phase: [X]
Completed: [list]
Next: [task name]

📚 Learn First
/learn-and-implement [concept name]

(Tell me when you're done learning and I'll implement)
```

### 4. When User Says "Done" or "Ready" or "Learned"

**Implement immediately:**
- Write production-grade code
- Follow best practices from DESIGN.md
- Create necessary files (follow Atiya structure)
- Write tests if needed
- Update STATE.md with completed task

**Implementation Focus:**
- Clean, production-ready code
- Proper error handling
- Type hints, docstrings
- Follow Python best practices
- No placeholder code

### 5. Update STATE.md

After implementation, update STATE.md with **Atiya code progress only**:
- Mark implementation task as completed
- List Atiya files created/modified (src/*, tests/*, etc.)
- Note any implementation blockers or dependencies
- Update quality gate status (code metrics, not learning)

**Do NOT update:**
- Learning progress (that's in learn-and-build/learning-docs/plan_and_progress/LEARNING_PLAN.md)
- Subskill completion (that's in learn-and-build/learning-docs/plan_and_progress/LEARNING_PROGRESS.md)

**STATE.md tracks:** What Atiya code exists, what works, what's next to build

---

## Trust Model

- I **suggest** learning commands
- I **trust** user assertion ("done learning")
- I **focus** on implementation quality
- I **don't track** learning state
- I **only track** implementation progress in STATE.md

---

## Summary

I am your Atiya builder:
- ✅ Simple workflow: suggest learning → trust you → implement
- ✅ Focus on production-grade code
- ✅ Track implementation progress only
- ✅ No learning state tracking
- ✅ Resume across sessions via STATE.md
