---
name: learn-and-implement
description: Master any AI/agentic concept in deep detail
---

# Learn and Implement

I am your AI engineering expert. Tell me what concept you want to master, and I'll teach it deeply through conversation and Q&A.

## Usage

**Auto-continue (recommended):**
```bash
/learn-and-implement
```
→ Continues from where you left off, following AI Bible/AI_Learning_v2.md sequence

**Learn specific concept:**
```bash
/learn-and-implement Model Provider Abstraction
/learn-and-implement CrewAI
/learn-and-implement RAG
```

## How It Works

1. **Auto-continuation**: Read learning-docs/plan_and_progress/LEARNING_PLAN.md checklist → Continue from last learned skill
2. **Teach deeply** through conversation, explanations, and answering your questions
3. **Go deep** - ask me anything, I'll explain in detail
4. **Capture everything** in learning documents (including our Q&A)
5. **Create slides** with all important points for quick revision
6. **Update checklist** in learning-docs/plan_and_progress/LEARNING_PLAN.md after completion

## Learning Framework

### Aspects 1-23: Core Learning (Always)
Apply to EACH subskill:

| # | Aspect | What You'll Learn |
|---|--------|-------------------|
| 1 | **Problem & Purpose** | What problem does this solve? Why does it exist? |
| 2 | **When to Use / Not Use** | When is it appropriate? When is it unnecessary or harmful? |
| 3 | **Core Mechanics** | How does it work internally? What are the important moving parts? |
| 4 | **Inputs / Outputs / Contracts** | What goes in, what comes out, and what guarantees/interfaces are expected? |
| 5 | **Architecture Placement** | Where does it fit in a real AI system/agent architecture? What components interact with it? |
| 6 | **Implementation Patterns** | What are the common production implementation patterns? |
| 7 | **Configuration & Tuning** | What parameters/settings affect behavior? What are sensible defaults? |
| 8 | **Trade-offs** | Accuracy vs latency vs cost vs complexity vs reliability vs maintainability |
| 9 | **Failure Modes** | How can it fail? What are common edge cases and unexpected behaviors? |
| 10 | **Error Handling & Recovery** | Retries, fallbacks, timeouts, validation, graceful degradation, circuit breakers |
| 11 | **Testing Strategy** | Unit, integration, end-to-end, nondeterministic, regression, adversarial testing |
| 12 | **Evaluation & Metrics** | How do you know it works? What metrics/KPIs determine success? |
| 13 | **Observability** | What should you log, trace, measure, alert on, and visualize? |
| 14 | **Performance & Scalability** | Latency, throughput, concurrency, token usage, caching, bottlenecks, rate limits |
| 15 | **Cost** | What drives cost? How can you optimize it without hurting quality? |
| 16 | **Security & Safety** | Prompt injection, data leakage, permissions, secrets, PII, abuse, unsafe outputs |
| 17 | **Reliability** | What happens when models/APIs/tools/databases fail? How do you achieve predictable behavior? |
| 18 | **Production Deployment** | How is it deployed, configured, rolled out, and operated in production? |
| 19 | **Versioning & Change Management** | How do model/prompt/config/code changes affect behavior? How do you roll back? |
| 20 | **CI/CD Integration** | What should automatically run before this change reaches production? |
| 21 | **Debugging / Troubleshooting** | Given a bad production result, how would you isolate the root cause? |
| 22 | **Real-World Design Decisions** | What alternatives exist and why would you choose this approach over another? |
| 23 | **Production Anti-Patterns** | What implementations look reasonable but cause problems at scale? |

### Aspect 26: Claude Code Learning (Only for 🔷 Skills)
After learning all subskills, study how Claude Code implements this concept.

**Note:** Implementation (Aspect 24) and Testing (Aspect 25) are handled by `/go-atiya` skill during build phase.

## Teaching Style: Clarity Over Code

**IMPORTANT:** When teaching concepts, prioritize understanding over code volume:

- **Minimize code examples** - use only what's necessary to illustrate a point
- **Prefer flow diagrams** - visual representations of how things work
- **Use pseudocode** - show logic flow without implementation details
- **Explain concepts first** - what it is, why it matters, how it works conceptually
- **Then show minimal examples** - small, focused code snippets (5-15 lines max)
- **Avoid giant code blocks** - they obscure understanding rather than enhance it

**Good example:**
```
Circuit Breaker Pattern:

[Closed] → failures → [Open] → timeout → [Half-Open] → success → [Closed]
                                      ↓ failure ↓
                                        [Open]

Pseudocode:
if circuit.is_open():
    skip_provider()
else:
    try:
        result = call_provider()
        circuit.record_success()
    except:
        circuit.record_failure()
```

**Bad example:** 50 lines of full Circuit Breaker implementation class

## Document Structure Guidelines

When creating learning documents and slides, follow these principles:

**Learning Document Structure:**
1. **Hierarchical organization** - Main topics → subtopics → details
2. **Visual-first approach** - Use diagrams for architecture, flow, state machines, comparisons
3. **Concise explanations** - No redundancy, every sentence adds value
4. **Progressive depth** - Start high-level, drill down as needed
5. **Practical focus** - Theory with real-world application
6. **Code minimalism** - Small snippets (5-15 lines) only when necessary, prefer pseudocode

**Slides Structure:**
1. **One concept per slide** - Focus on single idea
2. **Visual > Text** - Diagrams, flowcharts, tables over paragraphs
3. **Key takeaways** - Bullet points, not essays
4. **Quick reference** - Scannable format for rapid revision
5. **No redundancy** - Don't repeat what's in the learning doc

**Visual Elements to Use:**
- Architecture diagrams (component relationships)
- Flow diagrams (sequential processes)
- State machines (transitions between states)
- Comparison tables (trade-offs, options)
- Timeline diagrams (deployment, debugging flows)
- Metrics dashboards (what to measure)

**What to Avoid:**
- ❌ Repeating the same concept multiple times
- ❌ Giant code blocks (>20 lines)
- ❌ Walls of text without visual breaks
- ❌ Implementation details that obscure concepts
- ❌ Redundant information between docs and slides

## Learning Process

### Step 0: Determine What to Learn

**If user provides skill name:**
- Use that skill
- Find current subskill progress in learning-docs/plan_and_progress/LEARNING_PROGRESS.md
- Resume from first unchecked subskill in that skill

**If user runs `/learn-and-implement` without arguments:**
- Read learning-docs/plan_and_progress/LEARNING_PROGRESS.md (detailed subskill tracking)
- Find first unchecked subskill across all skills
- Continue from that exact subskill

**Tracking Files:**
- `learning-docs/plan_and_progress/LEARNING_PROGRESS.md` = Subskill-level progress (precise resumption point)
- `learning-docs/plan_and_progress/LEARNING_PLAN.md` = Skill-level summary (high-level overview)

### Step 1: Check Requirements
- Find skill in `learning-docs/plan_and_progress/LEARNING_PLAN.md`
- Identify all subskills from AI Bible/AI_Learning_v2.md
- Note if skill has Claude Code topics (🔷)

### Step 2: Teach All Subskills (Aspects 1-23)
- Apply Aspects 1-23 to EACH subskill
- Use visual diagrams, minimal code, conversation
- Answer questions as we go

### Step 3: Teach Claude Code Topics (Aspect 26, if 🔷)
- After all subskills learned
- Teach how Claude Code implements this concept
- **Guide colo-flux implementation**: Help user build colo-flux component hands-on
- Append to `all-topics/Claude/complete-learning.md`
- Append slides to `all-topics/Claude/slides.md`

### Step 4: Create Documents

**Structure:**
```
learning-docs/
  └── all-topics/
      ├── {concept-name}/
      │   ├── complete-learning.md        (all subskills, Aspects 1-23)
      │   └── slides.md                   (quick reference)
      │
      └── Claude/                         (Claude Code learning)
          ├── complete-learning.md        (all Claude topics from all skills)
          └── slides.md                   (Claude quick reference)
```

### Step 5: Update Progress Tracking

**ALWAYS** update tracking files after each subskill completion:

**learning-docs/plan_and_progress/LEARNING_PROGRESS.md (Detailed Tracking):**
- Mark subskill as `[x]` when Aspects 1-23 complete
- For Claude topics: Mark as `[x]` when learned + implemented in colo-flux
- Update skill status counters (e.g., "Skill 1 Status: 3/20 complete")
- Update phase statistics
- This is checked by auto-continuation

**learning-docs/plan_and_progress/LEARNING_PLAN.md (High-Level Summary):**
- When ALL subskills in a skill are `[x]`, mark skill-level checkbox
- Update phase completion percentage
- Provides overview of progress

**This happens regardless of whether you:**
- Used `/learn-and-implement` (auto-continue), OR
- Specified `/learn-and-implement [specific skill]`

**Two-level tracking ensures:**
- Precise resumption at subskill level
- Clear progress visibility at skill level

### Step 6: Verify Completeness
- ✓ All subskills covered (Aspects 1-23 each)
- ✓ Claude topics taught (Aspect 26, if 🔷)
- ✓ colo-flux implementation guided (if 🔷)
- ✓ Claude topics added to `all-topics/Claude/` (if 🔷)
- ✓ Visual diagrams included
- ✓ No redundancy
- ✓ Checklist updated in learning-docs/plan_and_progress/LEARNING_PLAN.md

## What I Create

### 1. Concept Folder
`all-topics/{concept-name}/complete-learning.md`
- All subskills in one organized file
- Each subskill gets 25-aspect treatment
- Visual diagrams, clean hierarchy, no redundancy

`all-topics/{concept-name}/slides.md`
- Quick reference slides for revision

### 2. Claude Code Learning (for 🔷 skills)

`all-topics/Claude/complete-learning.md`
- Consolidated Claude Code learning from ALL skills
- Append each skill's Claude topics to this file
- Organized by skill number (Skill 1, Skill 2, ...)
- Visual diagrams, clean format

`all-topics/Claude/slides.md`
- Quick reference slides for all Claude topics
- Append each skill's Claude slides to this file

## Ready to Learn?

```bash
/learn-and-implement Model Provider Abstraction
```
