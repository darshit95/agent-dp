---
name: any-learn
description: Deep production-grade learning of any AI/tech concept with Atiya context and complete documentation
---

# Any-Learn: Production-Grade Deep Dive Learning

Master any AI/Agentic/Technical concept in production-grade depth with complete documentation and diagrams.

## Usage

**General AI/Agentic topics:**
```bash
/any-learn Prompt Caching
/any-learn Circuit Breaker Pattern
/any-learn [highlighted topics]
```

**Claude Code topics** (prefix with "claude"):
```bash
/any-learn claude MCP fundamentals
/any-learn claude Tool Design
/any-learn claude [highlighted topics from 🔷 sections]
```

**Entire file:**
```bash
/any-learn file:AI_Learning_v2.md
```

---

## Context: Atiya

Atiya is a production AI agent for diagnosing PARTS test failures.

**Goals**: 90%+ accuracy, <$0.50/diagnosis, <60s latency, 99.9% uptime, 1000 failures/day

**Use Atiya as reference context**: Every concept learned should be evaluated through the lens of "how would this apply to building Atiya?" - but no actual implementation required, just learning and design thinking.

---

## What We Need

For each topic, provide **production-grade depth** covering:

1. **Foundation**: What problem this solves (with metrics), how it works, math/stats if applicable
2. **Architecture**: System diagrams (ASCII/Mermaid), design patterns, data flows, state machines
3. **Implementation**: Complete code examples, edge cases, configuration, dependencies
4. **Production**: Performance, cost, reliability, scale, observability, security (ALL with real numbers)
5. **Trade-offs**: When to use, when NOT, complexity cost, ROI, alternatives
6. **Atiya Lens**: How this applies to Atiya (use case, where it fits, decision: implement/defer/skip with ROI)
7. **Monitoring**: Metrics, dashboards, alerts, debugging

---

## How We Learn

**Approach**: Deep, visual, production-focused
- Diagrams everywhere (ASCII, Mermaid, sequence, state)
- Real metrics (not "fast" - "10ms overhead")
- Complete runnable code
- Explicit decisions for Atiya (with ROI justification)
- Connect to PARTS test diagnosis domain

**Flow**:
1. Understand problem (why exists)
2. Learn mechanics (architecture, patterns)
3. Production considerations (cost, scale, reliability)
4. Atiya evaluation (how it fits, implement/defer/skip)
5. Document all

---

## Documentation Output

Generate **3 files** per session:

**Location structure:**

- **General AI/Agentic topics** (organized hierarchically):
  - `learning-docs/all-topics/[X. Main Skill Name]/[concept-name]/`
  - Where `[X. Main Skill Name]` is from AI_Learning_v2.md (e.g., "1. Model Provider Abstraction and Fallback")
  - Determine the main skill by reading AI_Learning_v2.md and matching the concept to the appropriate skill section

- **Claude Code topics** (separate folder):
  - `learning-docs/all-topics/Claude/[concept-name]/`

**How to determine main skill folder:**
1. Read `/home/test/reg/agent-dp/ld-atiya/learn-and-build/AI Bible/AI_Learning_v2.md`
2. Find which main skill (1-28, 12A, 12B) the concept belongs to
3. Use that skill's title as the parent folder (e.g., "2. LLM Integration Prompt Engineering and Agent Profiles")
4. If concept is from 🔷 CLAUDE CODE section → use `Claude/` folder instead

**Files to create:**

### 1. `complete-learning.md`
Full reference doc - follow `model-provider-abstraction` example structure:
- Overview (Problem → Solution → Result)
- Architecture diagrams
- Core mechanics
- Implementation patterns
- Production considerations (perf, cost, reliability, scale, observability, security)
- Atiya lens (use case, fit, decision with ROI)
- Trade-offs & alternatives
- Monitoring
- Real-world examples

**Requirements**: ASCII/Mermaid diagrams, concrete numbers, complete code, ROI justification

### 2. `enhanced-slides.md`
Marp presentation (8-12 slides) with rich speaker notes - follow `model-provider-abstraction` example:
- Each slide: content + detailed `<!--speaker notes-->`
- Diagrams in Mermaid
- Real metrics
- Atiya application in speaker notes

### 3. `[concept-name]-presentation.html`
Interactive HTML presentation:
- Renders slides + speaker notes
- Keyboard navigation
- Mermaid rendering
- Use `model-provider-abstraction-presentation.html` as template

---

## Quality Standards

- ✅ Concrete metrics everywhere ($X, Yms, Z%)
- ✅ Clear diagrams
- ✅ Complete runnable code
- ✅ ROI justification for Atiya decisions
- ✅ Production focus (not academic)

---

## Success Criteria

After learning, user can:
- Explain to senior engineer
- Draw architecture from memory
- Know production trade-offs
- Justify Atiya decision with ROI
- Know what to monitor

---

## Topic Type Detection & Routing

**Step 1: Determine if Claude topic or General AI topic**

**Claude Code topics** identified by:
- User explicitly says "claude [topic]" (e.g., `/any-learn claude MCP fundamentals`)
- Topics from 🔷 CLAUDE CODE sections in AI_Learning_v2.md
- Topics mentioning: MCP, Claude API, Claude Code, Skills, Plugins, Memory system, CLAUDE.md, etc.

**Step 2: Route to correct folder**

**If Claude topic:**
- `learning-docs/all-topics/Claude/[concept-name]/`

**If General AI topic:**
1. Read AI_Learning_v2.md
2. Find which main skill (1-28, 12A, 12B) contains this concept
3. Create folder: `learning-docs/all-topics/[X. Main Skill Name]/[concept-name]/`
4. Example: "Prompt Caching" → found under "Skill 7: Prompt Caching and Token/Context Optimization" → folder is `7. Prompt Caching and Token Context Optimization/prompt-caching/`

---

**Begin deep production-grade learning with complete documentation.**
