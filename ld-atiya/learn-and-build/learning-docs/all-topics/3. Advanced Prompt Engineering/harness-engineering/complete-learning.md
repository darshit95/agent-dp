# Harness Engineering: Orchestrating Multi-Agent AI Workflows

## Table of Contents

1. [Problem and Overview](#problem-and-overview)
2. [What is Harness Engineering?](#what-is-harness-engineering)
3. [How is this Different from Prompt and Context Engineering?](#how-is-this-different-from-prompt-and-context-engineering)
4. [Architecture and Flow Diagram](#architecture-and-flow-diagram)
5. [Use Cases](#use-cases)
6. [Design Methodologies](#design-methodologies)
7. [Issues](#issues)
8. [Core Mechanics](#core-mechanics)
9. [Production Considerations](#production-considerations)
10. [Atiya Lens](#atiya-lens)
11. [Summary](#summary)

---

## Problem and Overview

### What is Harness Engineering?

**Harness Engineering** is the discipline of designing, implementing, and managing **orchestration systems** that coordinate multiple AI agents, tools, and execution steps to solve complex problems that cannot be addressed by a single prompt-response cycle.

```
┌─────────────────────────────────────────────────────────────────────┐
│                      THE ORCHESTRATION GAP                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Single LLM Call:                                                   │
│  ┌──────────┐      ┌─────────────┐      ┌──────────┐              │
│  │  Prompt  │─────▶│  LLM Model  │─────▶│ Response │              │
│  └──────────┘      └─────────────┘      └──────────┘              │
│                                                                     │
│  ✗ Limited context window                                          │
│  ✗ Single reasoning path                                           │
│  ✗ No tool chaining                                                │
│  ✗ No error recovery                                               │
│  ✗ No state management                                             │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Harness-Orchestrated Workflow:                                    │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐           │
│  │ Agent 1 │──▶│ Agent 2 │──▶│ Agent 3 │──▶│  Final  │           │
│  │ Network │   │ Config  │   │ Timing  │   │ Result  │           │
│  └────┬────┘   └────┬────┘   └────┬────┘   └─────────┘           │
│       │             │             │                                │
│       ▼             ▼             ▼                                │
│  ┌────────────────────────────────────┐                            │
│  │     Orchestrator / Harness         │                            │
│  │  • State Management                │                            │
│  │  • Error Recovery                  │                            │
│  │  • Context Passing                 │                            │
│  │  • Tool Execution                  │                            │
│  └────────────────────────────────────┘                            │
│                                                                     │
│  ✓ Multi-step reasoning                                            │
│  ✓ Specialist collaboration                                        │
│  ✓ Tool chaining                                                   │
│  ✓ Error recovery & retry                                          │
│  ✓ State persistence across steps                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Why Isn't Prompt + Context Enough?

While **Prompt Engineering** (what to ask) and **Context Engineering** (what evidence to provide) are foundational, they are **insufficient for complex, multi-step workflows**:

| Limitation | Why Prompt/Context Fails | Harness Engineering Solution |
|------------|-------------------------|------------------------------|
| **Context Window Limits** | Single prompt cannot contain all diagnostic data for complex problems | Split into multiple specialist agents, each with focused context |
| **Multi-Step Reasoning** | LLM cannot reliably chain 10+ steps in one response | Explicit orchestration with state management between steps |
| **Tool Execution** | Prompt cannot execute code, query databases, or call APIs | Harness provides execution environment and tool interfaces |
| **Error Recovery** | Single-shot response cannot retry on failure | Harness implements retry logic, fallback paths, and error handling |
| **Specialist Knowledge** | General-purpose prompt dilutes expertise | Multiple specialized agents (network, config, timing, security) |
| **State Management** | No mechanism to preserve intermediate results | Harness maintains shared state across agent invocations |
| **Quality Control** | No validation of intermediate outputs | Harness enforces validation gates between steps |

### The Orchestration Gap

```
Problem Complexity
      ▲
      │                                    ┌──────────────────────┐
      │                                    │  Harness Engineering │
      │                                    │      Required        │
  High│                         ┌──────────┼──────────────────────┤
      │                         │          │                      │
      │                         │ Multi-   │  • Multi-agent       │
      │              ┌──────────┤ Step     │  • State management  │
      │              │          │ Tasks    │  • Error recovery    │
      │              │ Complex  │          │  • Tool orchestration│
      │    ┌─────────┤ Prompts  └──────────┘                      │
      │    │         │                                            │
      │    │ Simple  │                                            │
      │    │ Prompts │                                            │
  Low │────┴─────────┴──────────────────────────────────────────▶
      │                                               Orchestration
      │    Prompt + Context        Context +          Needs
      │    Sufficient              Orchestration
```

**The Gap:** When task complexity exceeds what a single LLM call can handle, you need **orchestration infrastructure** — the harness.

---

## What is Harness Engineering?

### Definition: Harness = Context + Orchestration + Execution

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HARNESS ENGINEERING EQUATION                     │
└─────────────────────────────────────────────────────────────────────┘

    ┌────────────┐       ┌──────────────┐       ┌───────────┐
    │            │       │              │       │           │
    │  CONTEXT   │   +   │ ORCHESTRATION│   +   │ EXECUTION │
    │            │       │              │       │           │
    └──────┬─────┘       └──────┬───────┘       └─────┬─────┘
           │                    │                     │
           │                    │                     │
           ▼                    ▼                     ▼
    ┌────────────┐       ┌──────────────┐       ┌───────────┐
    │ • Problem  │       │ • Agent      │       │ • Tool    │
    │   data     │       │   sequencing │       │   calling │
    │ • System   │       │ • State      │       │ • Code    │
    │   logs     │       │   passing    │       │   running │
    │ • Configs  │       │ • Routing    │       │ • API     │
    │ • History  │       │   logic      │       │   access  │
    │ • Domain   │       │ • Error      │       │ • Database│
    │   knowledge│       │   handling   │       │   queries │
    └────────────┘       └──────────────┘       └───────────┘
           │                    │                     │
           └────────────────────┼─────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │                       │
                    │   HARNESS SYSTEM      │
                    │                       │
                    │  Coordinates agents,  │
                    │  manages state, and   │
                    │  executes tools to    │
                    │  solve complex tasks  │
                    │                       │
                    └───────────────────────┘
```

### Core Components

1. **Context Management**
   - Gather relevant data for each agent
   - Filter and prioritize information
   - Maintain context window budget
   - Version and track context evolution

2. **Orchestration**
   - Define agent execution sequence
   - Implement routing logic (sequential, parallel, conditional)
   - Pass state between agents
   - Coordinate tool access
   - Handle errors and retries

3. **Execution Environment**
   - Provide tool interfaces (API clients, CLI wrappers)
   - Sandbox code execution
   - Manage credentials and permissions
   - Enforce timeouts and resource limits
   - Log all actions for auditability

### Scope and Boundaries

```
┌─────────────────────────────────────────────────────────────────────┐
│                     HARNESS ENGINEERING SCOPE                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  IN SCOPE:                                                          │
│  ✓ Multi-agent coordination                                        │
│  ✓ State management across steps                                   │
│  ✓ Tool orchestration and execution                                │
│  ✓ Error handling and retry logic                                  │
│  ✓ Workflow design patterns (sequential, parallel, conditional)    │
│  ✓ Quality gates and validation                                    │
│  ✓ Observability and logging                                       │
│  ✓ Cost control and budget management                              │
│                                                                     │
│  OUT OF SCOPE:                                                      │
│  ✗ Training LLM models (that's ML Engineering)                     │
│  ✗ Designing prompts for single-shot tasks (Prompt Engineering)    │
│  ✗ RAG implementation (that's Context Engineering)                 │
│  ✗ Fine-tuning models for domain adaptation                        │
│  ✗ Infrastructure provisioning (that's DevOps)                     │
│                                                                     │
│  GRAY AREA (overlaps):                                              │
│  ~ Agent profile design (intersects with Prompt Engineering)       │
│  ~ Context retrieval strategy (intersects with Context Eng)        │
│  ~ Model selection (intersects with ML Engineering)                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## How is this Different from Prompt and Context Engineering?

### Comparison Table

| Aspect | Prompt Engineering | Context Engineering | Harness Engineering |
|--------|-------------------|---------------------|---------------------|
| **Focus** | What to ask | What evidence to provide | How to orchestrate workflow |
| **Scope** | Single LLM call | Single LLM call with enriched context | Multiple coordinated LLM calls |
| **Primary Artifact** | System prompt, user prompt | RAG pipeline, context retrieval | Orchestration graph, state machine |
| **Key Challenge** | Clarity, specificity, constraints | Relevance, recency, ranking | Coordination, state, error handling |
| **Failure Mode** | Ambiguous output, hallucination | Irrelevant context, information overload | Agent deadlock, state corruption, cascading failures |
| **Optimization Target** | Response quality per token | Context relevance and density | Workflow efficiency and reliability |
| **Tooling** | Prompt templates, few-shot examples | Vector DB, embeddings, retrieval | Workflow engines, state managers, orchestrators |
| **Metrics** | Accuracy, coherence, compliance | Precision@K, recall, context utilization | Task completion rate, latency, cost per workflow |
| **Example Output** | "Analyze this log file" | "Here are the 10 most relevant error patterns from 1M logs" | "Step 1: Network agent → Step 2: Config agent → Step 3: Timing agent → Final diagnosis" |

### Visual Venn Diagram

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    │    HARNESS ENGINEERING              │
                    │                                     │
                    │  ┌────────────────────────────┐     │
                    │  │                            │     │
                    │  │  Orchestration             │     │
   ┌────────────────┼──┤  • Agent sequencing        │     │
   │                │  │  • State management        │     │
   │  PROMPT        │  │  • Error recovery          │     │
   │  ENGINEERING   │  │  • Tool execution          │─────┼──────┐
   │                │  │                            │     │      │
   │  • Clarity     │  └──────────┬─────────────────┘     │      │
   │  • Constraints │             │                       │      │
   │  • Role def    │    ┌────────┴────────┐              │      │
   │                │    │                 │              │      │
   └────────┬───────┘    │  INTEGRATION    │              │      │
            │            │    ZONE         │              │      │
            │    ┌───────┤                 ├─────────┐    │      │
            │    │       │ • Agent profiles│         │    │      │
            │    │       │ • Context       │         │    │      │
            └────┤       │   routing       │         ├────┘      │
                 │       │ • Prompt        │         │           │
                 │       │   templates     │         │           │
                 │       │   per agent     │         │           │
                 │       └─────────────────┘         │           │
                 │                                   │           │
                 │  CONTEXT ENGINEERING              │           │
                 │                                   │           │
                 │  • RAG pipelines                  │           │
                 │  • Vector search                  │           │
                 │  • Context ranking                │           │
                 └───────────────────────────────────┘           │
                                                                 │
                                                                 │
                         ┌───────────────────────────────────────┘
                         │
                         │  UNIQUE TO HARNESS:
                         │  • Multi-step workflows
                         │  • State persistence
                         │  • Error recovery
                         │  • Tool orchestration
                         └─────────────────────────
```

### The Three-Layer Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LAYER 3: HARNESS                             │
│  "How do we coordinate multiple agents to solve this?"             │
├─────────────────────────────────────────────────────────────────────┤
│  • Atiya: Network Agent → Config Agent → Timing Agent              │
│  • State: Pass network findings to config analysis                 │
│  • Error: If timing agent fails, retry with expanded context       │
│  • Validation: Ensure each agent produces structured output        │
└─────────────────────────────────────────────────────────────────────┘
                                   ▲
                                   │
┌─────────────────────────────────────────────────────────────────────┐
│                       LAYER 2: CONTEXT                              │
│  "What evidence does each agent need?"                             │
├─────────────────────────────────────────────────────────────────────┤
│  • Network Agent: Interface stats, routing tables, ARP cache       │
│  • Config Agent: Device configs, change history, compliance rules  │
│  • Timing Agent: NTP logs, clock drift metrics, sync status        │
│  • Retrieved via RAG from testbed logs, configs, telemetry         │
└─────────────────────────────────────────────────────────────────────┘
                                   ▲
                                   │
┌─────────────────────────────────────────────────────────────────────┐
│                       LAYER 1: PROMPT                               │
│  "What should each agent do?"                                      │
├─────────────────────────────────────────────────────────────────────┤
│  • Network Agent: "You are a network diagnostics expert..."        │
│  • Config Agent: "You are a configuration auditor..."              │
│  • Timing Agent: "You are a timing/sync specialist..."             │
│  • Constraints: Output format, reasoning style, error handling     │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Insight:** Harness Engineering doesn't replace the other two — it **builds on top of them** to enable workflows that exceed single-call capabilities.

---

## Architecture and Flow Diagram

### Complete Harness Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HARNESS SYSTEM ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │                  │
                              │  User / Trigger  │
                              │                  │
                              └────────┬─────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────┐
                    │                                  │
                    │      ORCHESTRATOR / HARNESS      │
                    │                                  │
                    │  • Workflow definition           │
                    │  • Agent routing logic           │
                    │  • State coordination            │
                    │  • Error handling                │
                    │                                  │
                    └──────────┬───────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │ Context   │  │   State   │  │ Execution │
        │ Manager   │  │  Manager  │  │  Engine   │
        └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
              │              │              │
              │              │              │
┌─────────────┼──────────────┼──────────────┼─────────────┐
│             │              │              │             │
│  ┌──────────▼─────┐  ┌─────▼──────┐  ┌───▼──────────┐  │
│  │  RAG Pipeline  │  │ Shared     │  │ Tool         │  │
│  │  • Retrieval   │  │ State      │  │ Registry     │  │
│  │  • Ranking     │  │ • Workflow │  │ • API calls  │  │
│  │  • Filtering   │  │   vars     │  │ • Code exec  │  │
│  └────────────────┘  │ • Agent    │  │ • DB queries │  │
│                      │   outputs  │  └──────────────┘  │
│                      │ • Metadata │                    │
│                      └────────────┘                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │  Agent 1  │  │  Agent 2  │  │  Agent N  │
        │ (Network) │  │ (Config)  │  │ (Timing)  │
        └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
              │              │              │
              │              │              │
              └──────────────┼──────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Error Handler   │
                    │ • Retry logic   │
                    │ • Fallback path │
                    │ • Escalation    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Observability   │
                    │ • Logging       │
                    │ • Metrics       │
                    │ • Tracing       │
                    └─────────────────┘
```

### Component Details

#### 1. Context Manager

**Responsibility:** Gather and filter relevant information for each agent.

```
┌──────────────────────────────────────────────────────────┐
│              CONTEXT MANAGER                             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  INPUT: Agent ID, Task, Current State                   │
│                                                          │
│  PROCESS:                                                │
│  1. Identify required context types                     │
│     (logs, configs, metrics, history)                   │
│  2. Retrieve from storage (vector DB, file system, DB)  │
│  3. Rank by relevance to current task                   │
│  4. Filter to fit context window budget                 │
│  5. Format for agent consumption                        │
│                                                          │
│  OUTPUT: Contextual data package for agent              │
│                                                          │
│  CHALLENGES:                                             │
│  • Context window limits (4K-200K tokens)               │
│  • Relevance ranking accuracy                           │
│  • Stale data detection                                 │
│  • Cross-domain context fusion                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

#### 2. Orchestrator

**Responsibility:** Define and execute the workflow logic.

```
┌──────────────────────────────────────────────────────────┐
│                 ORCHESTRATOR                             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  WORKFLOW DEFINITION:                                    │
│  • Agent execution graph (DAG or state machine)         │
│  • Routing rules (sequential, parallel, conditional)    │
│  • Termination conditions                               │
│                                                          │
│  RUNTIME EXECUTION:                                      │
│  1. Initialize workflow state                           │
│  2. Determine next agent to invoke                      │
│  3. Prepare context via Context Manager                 │
│  4. Call agent via Execution Engine                     │
│  5. Update state via State Manager                      │
│  6. Check termination conditions                        │
│  7. Handle errors via Error Handler                     │
│  8. Loop until completion or failure                    │
│                                                          │
│  PATTERNS:                                               │
│  • Sequential: A → B → C                                │
│  • Parallel: A || B || C → D                            │
│  • Conditional: if (A.result) then B else C             │
│  • Loop: while (not done) repeat A                      │
│  • Cascade: A → B(A.output) → C(B.output)              │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

#### 3. State Manager

**Responsibility:** Persist and share state across agent invocations.

```
┌──────────────────────────────────────────────────────────┐
│                   STATE MANAGER                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  STATE SCHEMA:                                           │
│  {                                                       │
│    "workflow_id": "atiya-001",                           │
│    "current_step": 2,                                    │
│    "agent_outputs": {                                    │
│      "network_agent": {...},                            │
│      "config_agent": {...}                              │
│    },                                                    │
│    "metadata": {                                         │
│      "start_time": "2026-08-20T10:00:00Z",              │
│      "total_cost": 0.35,                                │
│      "retry_count": 1                                   │
│    }                                                     │
│  }                                                       │
│                                                          │
│  OPERATIONS:                                             │
│  • get(key): Retrieve value from shared state           │
│  • set(key, value): Update state                        │
│  • append(key, value): Add to list                      │
│  • checkpoint(): Create state snapshot for rollback     │
│  • restore(checkpoint_id): Rollback to prior state      │
│                                                          │
│  PERSISTENCE:                                            │
│  • In-memory (fast, lost on crash)                      │
│  • Redis (durable, distributed)                         │
│  • Database (auditable, queryable)                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

#### 4. Execution Engine

**Responsibility:** Execute agent calls and tool invocations.

```
┌──────────────────────────────────────────────────────────┐
│                EXECUTION ENGINE                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  AGENT INVOCATION:                                       │
│  1. Load agent profile (system prompt, model, params)   │
│  2. Inject context from Context Manager                 │
│  3. Call LLM API (OpenAI, Anthropic, etc.)              │
│  4. Parse and validate response                         │
│  5. Return structured output                            │
│                                                          │
│  TOOL EXECUTION:                                         │
│  1. Receive tool call request from agent                │
│  2. Validate permissions and parameters                 │
│  3. Execute tool (API call, code run, DB query)         │
│  4. Capture output and errors                           │
│  5. Return result to agent                              │
│                                                          │
│  SAFETY MEASURES:                                        │
│  • Timeout enforcement (30s default)                    │
│  • Sandbox for code execution                           │
│  • Rate limiting per agent                              │
│  • Credential management (API keys, tokens)             │
│  • Audit logging of all executions                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

#### 5. Error Handler

**Responsibility:** Detect, classify, and recover from failures.

```
┌──────────────────────────────────────────────────────────┐
│                  ERROR HANDLER                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ERROR TAXONOMY:                                         │
│  • Transient: API rate limit, timeout (RETRY)           │
│  • Semantic: Invalid agent output (REPROMPT)            │
│  • Structural: Missing required field (VALIDATE+RETRY)  │
│  • Fatal: Auth failure, quota exceeded (ABORT)          │
│                                                          │
│  RECOVERY STRATEGIES:                                    │
│  1. Retry with exponential backoff                      │
│     • Max retries: 3                                    │
│     • Backoff: 2^n seconds                              │
│  2. Fallback to alternate agent/model                   │
│     • GPT-4 → GPT-3.5 on cost limit                     │
│  3. Partial result return                               │
│     • Return best-effort output with warning            │
│  4. Human escalation                                     │
│     • Queue for manual review                           │
│                                                          │
│  CIRCUIT BREAKER:                                        │
│  • If agent fails 5 times in 10 minutes, disable agent  │
│  • Alert on-call engineer                               │
│  • Route to fallback workflow                           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Multi-Agent Workflow Diagram

Example: **Atiya's Test Failure Diagnostic Workflow**

```
┌───────────────────────────────────────────────────────────────────────┐
│                  ATIYA DIAGNOSTIC WORKFLOW                            │
└───────────────────────────────────────────────────────────────────────┘

   Start
     │
     ▼
┌─────────────────┐
│ Intake & Triage │  Classify failure type
│     Agent       │  Extract metadata (test name, env, timestamp)
└────────┬────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────┐
│                        SPECIALIST CASCADE                      │
└────────────────────────────────────────────────────────────────┘

         ▼
    ┌─────────────────┐
    │ Network Agent   │  Analyze: connectivity, routing, latency
    │                 │  Context: interface stats, ping logs, traceroute
    │ Output:         │
    │ • network_ok: bool
    │ • findings: [...]
    │ • confidence: 0.85
    └────────┬────────┘
             │
             ▼
    State.set("network", output)
             │
             ▼
    ┌─────────────────┐
    │  Config Agent   │  Analyze: device configs, compliance, changes
    │                 │  Context: startup-config, running-config, diffs
    │ Input:          │
    │ • State.get("network")  (uses network findings)
    │                 │
    │ Output:         │
    │ • config_issues: [...]
    │ • recent_changes: [...]
    │ • confidence: 0.92
    └────────┬────────┘
             │
             ▼
    State.set("config", output)
             │
             ▼
    ┌─────────────────┐
    │  Timing Agent   │  Analyze: NTP sync, clock drift, timing errors
    │                 │  Context: NTP logs, system time, drift metrics
    │ Input:          │
    │ • State.get("network")
    │ • State.get("config")
    │                 │
    │ Output:         │
    │ • timing_issues: [...]
    │ • root_cause: "..."
    │ • confidence: 0.78
    └────────┬────────┘
             │
             ▼
    State.set("timing", output)
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                    SYNTHESIS & REPORTING                       │
└────────────────────────────────────────────────────────────────┘
             │
             ▼
    ┌─────────────────┐
    │ Synthesis Agent │  Combine findings from all specialists
    │                 │  Generate final diagnosis
    │ Input:          │
    │ • State.get("network")
    │ • State.get("config")
    │ • State.get("timing")
    │                 │
    │ Output:         │
    │ • root_cause: "NTP server unreachable due to firewall rule"
    │ • evidence: [...]
    │ • remediation: "Update ACL to allow NTP traffic"
    │ • confidence: 0.88
    └────────┬────────┘
             │
             ▼
      ┌─────────────┐
      │   Report    │
      │  to User    │
      └─────────────┘
```

**Key Features:**
- **Cascade pattern:** Each agent builds on prior findings
- **State passing:** Network findings inform config analysis, both inform timing analysis
- **Synthesis:** Final agent aggregates all specialist outputs
- **Confidence tracking:** Each step reports certainty, final synthesis weighs evidence

---

## Use Cases

### 1. Atiya: Multi-Specialist Cascade for Test Failure Diagnosis

**Problem:** A network test fails. Root cause could be:
- Network issues (connectivity, routing, latency)
- Configuration problems (device config, compliance violations)
- Timing/sync issues (NTP failures, clock drift)
- Code bugs, environment issues, data corruption, etc.

**Why Single Prompt Fails:**
- Too much context (all logs, configs, metrics exceed context window)
- Too many domains (network, config, timing expertise diluted)
- Unreliable multi-step reasoning (LLM skips steps or hallucinates)

**Harness Solution:**

```
┌──────────────────────────────────────────────────────────────────┐
│            ATIYA HARNESS: SPECIALIST CASCADE                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Agent 1: Network Specialist                                    │
│  ├─ Context: Interface stats, ping logs, routing tables         │
│  ├─ Expertise: Network diagnostics, connectivity analysis       │
│  └─ Output: network_ok=True, latency_spike detected on eth0     │
│                                                                  │
│  Agent 2: Config Specialist                                     │
│  ├─ Context: Device configs, change history, ACLs               │
│  ├─ Expertise: Configuration audit, compliance checks           │
│  ├─ Input: Network agent findings (latency on eth0)             │
│  └─ Output: Recent ACL change blocked NTP traffic               │
│                                                                  │
│  Agent 3: Timing Specialist                                     │
│  ├─ Context: NTP logs, clock drift metrics, sync status         │
│  ├─ Expertise: Timing analysis, NTP troubleshooting             │
│  ├─ Input: Network + config findings (ACL blocked NTP)          │
│  └─ Output: Clock drift 15s, NTP unreachable, causing test fail │
│                                                                  │
│  Synthesis Agent:                                                │
│  ├─ Input: All specialist findings                              │
│  └─ Output: "Root cause: ACL change on 2026-08-19 blocked NTP,  │
│             causing clock drift and test timeout. Remediation:   │
│             Revert ACL change or add NTP exception."             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Results:**
- **Accuracy improvement:** 73% → 91% (single-shot vs. harness)
- **Context efficiency:** Each agent sees only relevant domain data (3K tokens vs. 50K)
- **Explainability:** Clear chain of reasoning from each specialist

### 2. Complex Diagnostic Workflow: Database Performance Issue

**Problem:** Application latency increased by 300%. Potential causes:
- Database query performance (slow queries, missing indexes)
- Network latency (cloud region issues, DNS)
- Application code (N+1 queries, memory leaks)
- Infrastructure (CPU/memory exhaustion, disk I/O)

**Harness Workflow:**

```
                           ┌──────────────┐
                           │ Triage Agent │
                           │ Classify:    │
                           │ "DB-related" │
                           └──────┬───────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
            ┌───────────┐ ┌───────────┐ ┌───────────┐
            │   Query   │ │ Network   │ │Infra Agent│
            │   Agent   │ │   Agent   │ │           │
            └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
                  │             │             │
                  │(parallel)   │(parallel)   │(parallel)
                  │             │             │
                  └─────────────┼─────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │ Synthesis     │
                        │ Agent         │
                        │ Root cause:   │
                        │ "Missing index│
                        │ on user_id    │
                        │ causing full  │
                        │ table scans"  │
                        └───────────────┘
```

**Key Pattern:** **Parallel investigation** — three specialists run simultaneously, synthesis agent waits for all, then aggregates findings.

### 3. Multi-Step Reasoning Chain: Security Incident Response

**Problem:** Suspicious login detected. Investigate and respond.

**Harness Workflow:**

```
Step 1: Detection Agent
└─ Output: Suspicious login from new IP in foreign country

Step 2: Enrichment Agent
├─ Input: IP address
├─ Tools: GeoIP lookup, threat intel API
└─ Output: IP is known VPN exit node, no prior threat reports

Step 3: Behavioral Analysis Agent
├─ Input: User ID, login history
├─ Tools: Query user database, session logs
└─ Output: User recently traveled to that country (calendar check)

Step 4: Risk Scoring Agent
├─ Input: All prior findings
└─ Output: Risk score 3/10 (low), likely legitimate

Step 5: Response Agent
├─ Input: Risk score
└─ Output: Log event, no action required
```

**Key Pattern:** **Sequential reasoning** with **tool execution** at each step.

---

## Design Methodologies

### 1. Sequential Harness

**Pattern:** Steps execute in strict order: A → B → C

**When to Use:**
- Each step depends on prior outputs
- Linear reasoning chain
- No parallelization benefit

**Visual Flow:**

```
┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│ Step 1  │─────▶│ Step 2  │─────▶│ Step 3  │─────▶│ Final   │
│ Agent A │      │ Agent B │      │ Agent C │      │ Output  │
└─────────┘      └─────────┘      └─────────┘      └─────────┘
     │                │                │
     ▼                ▼                ▼
  Output A        Output B        Output C
     │                │                │
     └────────────────┴────────────────┘
                      │
                      ▼
                State.get("A", "B", "C")
```

**Visual Implementation Flow:**

```
┌────────────────────────────────────────────────────────────────────┐
│          SEQUENTIAL HARNESS: Step-by-Step Execution                │
└────────────────────────────────────────────────────────────────────┘

Initialize:
  state = {} (empty dictionary)

┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Agent A                                                │
├─────────────────────────────────────────────────────────────────┤
│  1. Get context for Agent A                                     │
│     context_a = context_manager.get_context(task, agent="A")    │
│                                                                 │
│  2. Run Agent A with context                                    │
│     output_a = agent_a.run(context_a)                           │
│                                                                 │
│  3. Store result in state                                       │
│     state["agent_a"] = output_a                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Agent B (uses Step 1 output)                           │
├─────────────────────────────────────────────────────────────────┤
│  1. Get context with prior state                                │
│     context_b = context_manager.get_context(                    │
│         task, agent="B", prior_state=state)                     │
│                                                                 │
│  2. Run Agent B with context + Agent A output                   │
│     output_b = agent_b.run(context_b, input=output_a)           │
│                                                                 │
│  3. Store result in state                                       │
│     state["agent_b"] = output_b                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Agent C (uses Step 1 + 2 outputs)                      │
├─────────────────────────────────────────────────────────────────┤
│  1. Get context with full prior state                           │
│     context_c = context_manager.get_context(                    │
│         task, agent="C", prior_state=state)                     │
│                                                                 │
│  2. Run Agent C with context + both prior outputs               │
│     output_c = agent_c.run(                                     │
│         context_c, input=[output_a, output_b])                  │
│                                                                 │
│  3. Store result in state                                       │
│     state["agent_c"] = output_c                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                      Return complete state
                      {
                        "agent_a": output_a,
                        "agent_b": output_b,
                        "agent_c": output_c
                      }
```

**Advantages:**
- Simple to reason about
- Easy to debug (linear execution trace)
- Clear dependencies

**Disadvantages:**
- No parallelization (slow for independent tasks)
- Any step failure blocks entire workflow

---

### 2. Parallel Harness

**Pattern:** Multiple agents run simultaneously, results aggregated

**When to Use:**
- Steps are independent (no dependencies)
- Latency-critical workflows
- Redundancy needed (multiple agents vote)

**Visual Flow:**

```
                        ┌─────────┐
                        │ Task    │
                        │ Input   │
                        └────┬────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │ Agent A │         │ Agent B │         │ Agent C │
    │(Network)│         │(Config) │         │(Timing) │
    └────┬────┘         └────┬────┘         └────┬────┘
         │                   │                   │
         │  (concurrent)     │  (concurrent)     │  (concurrent)
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                     ┌───────────────┐
                     │ Aggregation   │
                     │ Agent         │
                     │ Combine all   │
                     │ outputs       │
                     └───────┬───────┘
                             │
                             ▼
                       Final Result
```

**Visual Implementation Flow:**

```
┌────────────────────────────────────────────────────────────────────┐
│             PARALLEL HARNESS: Concurrent Execution                 │
└────────────────────────────────────────────────────────────────────┘

Step 1: Launch all agents concurrently using asyncio.gather
        (return_exceptions=True prevents one failure from killing all)

                          ┌─────────────┐
                          │    Task     │
                          └──────┬──────┘
                                 │
                   ┌─────────────┼─────────────┐
                   │             │             │
                   ▼             ▼             ▼
           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
           │  Agent A     │ │  Agent B     │ │  Agent C     │
           │  run_async() │ │  run_async() │ │  run_async() │
           └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
                  │                │                │
            (concurrent)     (concurrent)     (concurrent)
                  │                │                │
                  ▼                ▼                ▼
            ┌─────────┐      ┌─────────┐      ┌─────────┐
            │ Result A│      │ Result B│      │ Result C│
            │ or Error│      │ or Error│      │ or Error│
            └─────────┘      └─────────┘      └─────────┘
                  │                │                │
                  └────────────────┼────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Filter out errors                                      │
├─────────────────────────────────────────────────────────────────┤
│  For each result in results:                                    │
│    If result is NOT an Exception:                               │
│      Add to valid_results list                                  │
│                                                                 │
│  Example:                                                       │
│    results = [Result_A, Error, Result_C]                        │
│    valid_results = [Result_A, Result_C]                         │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Aggregate valid results                                │
├─────────────────────────────────────────────────────────────────┤
│  Run aggregation_agent with valid_results                       │
│  aggregated = aggregation_agent.run(valid_results)              │
│                                                                 │
│  Aggregation agent synthesizes:                                 │
│  • Common findings across agents                                │
│  • Weighted confidence scores                                   │
│  • Final combined diagnosis                                     │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                          Return aggregated result
```

**Advantages:**
- Fast (parallelization reduces latency)
- Fault-tolerant (one failure doesn't block others)

**Disadvantages:**
- Complex error handling (partial failures)
- Higher cost (all agents run, even if one suffices)
- Can't pass intermediate results between agents

---

### 3. Conditional Harness

**Pattern:** Routing decisions based on intermediate results

**When to Use:**
- Different execution paths for different scenarios
- Cost optimization (skip unnecessary steps)
- Adaptive workflows

**Visual Flow:**

```
                        ┌─────────┐
                        │ Step 1  │
                        │ Triage  │
                        └────┬────┘
                             │
                        Output: Issue Type
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         if "network"   if "config"    if "timing"
              │              │              │
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │ Network │    │ Config  │    │ Timing  │
        │ Agent   │    │ Agent   │    │ Agent   │
        └────┬────┘    └────┬────┘    └────┬────┘
             │              │              │
             └──────────────┼──────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │ Synthesis   │
                     └─────────────┘
```

**Visual Implementation Flow:**

```
┌────────────────────────────────────────────────────────────────────┐
│           CONDITIONAL HARNESS: Decision-Based Routing              │
└────────────────────────────────────────────────────────────────────┘

Step 1: Triage Classification
┌─────────────────────────────────────────────────────────────────┐
│  Run triage agent to classify issue type                        │
│  issue_type = triage_agent.run(task)                            │
│                                                                 │
│  Possible outputs: "network", "config", "timing", "other"       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
Step 2: Route to Appropriate Specialist
┌─────────────────────────────────────────────────────────────────┐
│                  Decision Tree Routing                          │
└─────────────────────────────────────────────────────────────────┘

              What is issue_type?
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
        ▼            ▼            ▼            ▼
   "network"    "config"     "timing"      "other"
        │            │            │            │
        ▼            ▼            ▼            ▼
 ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
 │ Network    │ │ Config     │ │ Timing     │ │ General    │
 │ Agent      │ │ Agent      │ │ Agent      │ │ Agent      │
 │ run(task)  │ │ run(task)  │ │ run(task)  │ │ run(task)  │
 └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
       │              │              │              │
       └──────────────┼──────────────┼──────────────┘
                      │
                      ▼
         specialist_output (from chosen agent)
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Synthesis                                              │
├─────────────────────────────────────────────────────────────────┤
│  Run synthesis agent with specialist output                     │
│  final_result = synthesis_agent.run(specialist_output)          │
│                                                                 │
│  Synthesis produces:                                            │
│  • Validated diagnosis                                          │
│  • Confidence score                                             │
│  • Remediation steps                                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
                   Return final_result

Key Benefit: Only 2 agents called (triage + specialist + synthesis)
            vs 4+ agents in sequential cascade
            Cost savings: ~50% fewer LLM calls
```

**Advantages:**
- Cost-efficient (only run necessary agents)
- Adaptive (handles different scenarios)

**Disadvantages:**
- Requires accurate triage/classification
- More complex to maintain (many code paths)

---

### 4. Cascade Harness (Atiya Pattern)

**Pattern:** Each agent builds on prior outputs, context accumulates

**When to Use:**
- Multi-domain expertise needed
- Each step narrows the investigation
- Context grows incrementally

**Visual Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     CASCADE HARNESS                             │
└─────────────────────────────────────────────────────────────────┘

Step 1: Network Agent
├─ Context: Interface stats, ping logs
└─ Output: "Latency spike on eth0"

          │
          ▼ (pass output to next agent)

Step 2: Config Agent
├─ Context: Device configs, change history
├─ Input: "Latency spike on eth0" (from Step 1)
└─ Output: "ACL change blocked NTP traffic on eth0"

          │
          ▼ (accumulate context)

Step 3: Timing Agent
├─ Context: NTP logs, clock drift
├─ Input: "Latency spike" + "ACL blocked NTP" (from Steps 1-2)
└─ Output: "Clock drift 15s, causing test timeout"

          │
          ▼ (all evidence accumulated)

Step 4: Synthesis Agent
├─ Input: Network + Config + Timing findings
└─ Output: "Root cause: ACL change blocked NTP → clock drift → test fail"
```

**Visual Implementation Flow:**

```
┌────────────────────────────────────────────────────────────────────┐
│     CASCADE HARNESS: Incremental Context Accumulation             │
└────────────────────────────────────────────────────────────────────┘

Initialize:
  accumulated_context = [] (empty list)

┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Network Agent                                          │
├─────────────────────────────────────────────────────────────────┤
│  Input context: [] (empty - first agent)                        │
│                                                                 │
│  network_output = network_agent.run(                            │
│      task, context=accumulated_context)                         │
│                                                                 │
│  Append to context:                                             │
│  accumulated_context.append(network_output)                     │
│                                                                 │
│  Context now: [network_output]                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Config Agent (sees network findings)                   │
├─────────────────────────────────────────────────────────────────┤
│  Input context: [network_output]                                │
│  ↑ Config agent can reference network findings                  │
│                                                                 │
│  config_output = config_agent.run(                              │
│      task, context=accumulated_context)                         │
│                                                                 │
│  Append to context:                                             │
│  accumulated_context.append(config_output)                      │
│                                                                 │
│  Context now: [network_output, config_output]                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Timing Agent (sees network + config findings)          │
├─────────────────────────────────────────────────────────────────┤
│  Input context: [network_output, config_output]                 │
│  ↑ Timing agent has full history                                │
│                                                                 │
│  timing_output = timing_agent.run(                              │
│      task, context=accumulated_context)                         │
│                                                                 │
│  Append to context:                                             │
│  accumulated_context.append(timing_output)                      │
│                                                                 │
│  Context now: [network_output, config_output, timing_output]    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Synthesis Agent (sees all specialist findings)         │
├─────────────────────────────────────────────────────────────────┤
│  Input context: [network_output, config_output, timing_output]  │
│  ↑ Complete evidence chain                                      │
│                                                                 │
│  final_diagnosis = synthesis_agent.run(                         │
│      task, context=accumulated_context)                         │
│                                                                 │
│  Synthesizes all findings into coherent diagnosis               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    Return final_diagnosis

Context Growth Pattern:
  Step 1: []                                              (0 items)
  Step 2: [network]                                       (1 item)
  Step 3: [network, config]                               (2 items)
  Step 4: [network, config, timing]                       (3 items)
  
Key: Each agent builds on ALL prior findings, creating a
     progressive chain of evidence and reasoning.
```

**Advantages:**
- Deep expertise per domain
- Context efficiency (each agent sees only relevant prior findings)
- Explainable (clear chain of reasoning)

**Disadvantages:**
- Sequential (can't parallelize)
- Error propagation (early mistake affects all downstream agents)

---

### 5. Retry Harness (Error Recovery)

**Pattern:** Automatically retry failed steps with modifications

**When to Use:**
- Transient failures expected (API rate limits, timeouts)
- LLM output validation failures
- Non-deterministic tasks

**Visual Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                      RETRY HARNESS                              │
└─────────────────────────────────────────────────────────────────┘

Attempt 1:
┌─────────┐
│ Agent A │─────▶ ERROR: Timeout
└─────────┘
     │
     ▼ (wait 2s)

Attempt 2:
┌─────────┐
│ Agent A │─────▶ ERROR: Invalid output format
└─────────┘
     │
     ▼ (wait 4s, add validation prompt)

Attempt 3:
┌─────────┐
│ Agent A │─────▶ SUCCESS
└─────────┘
     │
     ▼
  Continue workflow
```

**Visual Implementation Flow:**

```
┌────────────────────────────────────────────────────────────────────┐
│           RETRY HARNESS: Error Recovery with Backoff               │
└────────────────────────────────────────────────────────────────────┘

Input: agent, task, max_retries=3

For attempt = 0, 1, 2 (range 0 to max_retries):

  ┌─────────────────────────────────────────────────────────────┐
  │  Try: Run agent and validate                                │
  └─────────────────────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  output = agent.run(task)                                   │
  └────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Check: Is output valid?                                    │
  │  if validate(output):                                       │
  └────────┬────────────────────────────┬───────────────────────┘
           │ YES                        │ NO
           ▼                            ▼
    ┌───────────┐              ┌─────────────────────┐
    │  Return   │              │ Raise               │
    │  output   │              │ ValidationError     │
    └───────────┘              └──────────┬──────────┘
                                          │
                                          ▼
                               Go to exception handling

  ┌─────────────────────────────────────────────────────────────┐
  │  Exception Handling                                         │
  └─────────────────────────────────────────────────────────────┘

       Exception Type?
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
  TimeoutError  ValidationError
  RateLimitError
       │             │
       ▼             ▼
  ┌──────────┐  ┌──────────────────────────────────────────┐
  │ Transient│  │ Semantic Error (invalid format)          │
  │ Error    │  │                                          │
  └─────┬────┘  └────────┬─────────────────────────────────┘
        │                │
        ▼                ▼
  Is this last      Is this last
  attempt?          attempt?
  (attempt < 2)     (attempt < 2)
        │                │
    ┌───┴───┐        ┌───┴───┐
   YES     NO       YES     NO
    │       │        │       │
    ▼       ▼        ▼       ▼
  Retry   Raise    Retry   Raise
  with    error    with    error
  backoff          enhanced
    │               prompt
    │                │
    ▼                ▼
  Wait time =     Append to task prompt:
  2^attempt       "\n\nIMPORTANT: Output must be valid JSON."
  (1s, 2s, 4s)
    │                │
    └────────────────┴──────▶ Continue to next iteration

After max_retries exhausted with no success:
  ┌─────────────────────────────────────────────────────────────┐
  │  Raise MaxRetriesExceeded                                   │
  │  "Agent failed after 3 attempts"                            │
  └─────────────────────────────────────────────────────────────┘

Backoff Pattern:
  Attempt 0: Wait 2^0 = 1 second
  Attempt 1: Wait 2^1 = 2 seconds
  Attempt 2: Wait 2^2 = 4 seconds
  Attempt 3: Raise (exhausted)
```

**Advantages:**
- Resilient to transient failures
- Automatic recovery from semantic errors
- Reduces manual intervention

**Disadvantages:**
- Increases latency (retries take time)
- Higher cost (multiple LLM calls)
- Can mask underlying issues

---

### Summary: When to Use Each Pattern

| Pattern | Best For | Latency | Cost | Complexity |
|---------|----------|---------|------|------------|
| **Sequential** | Linear dependencies, simple workflows | Medium | Low | Low |
| **Parallel** | Independent tasks, speed-critical | Low | High | Medium |
| **Conditional** | Different scenarios, cost optimization | Medium | Medium | High |
| **Cascade** | Multi-domain expertise, incremental reasoning | High | Medium | Medium |
| **Retry** | Error recovery, validation | High | High | Medium |

**Pro Tip:** Most production harnesses **combine patterns**:
- Cascade + Retry (Atiya: each specialist retries on failure)
- Conditional + Parallel (triage decides which parallel batch to run)
- Sequential + Retry (linear workflow with per-step retries)

---

## Issues

### 1. Complexity Management

**Problem:** Harnesses with many agents, conditional paths, and error handlers become difficult to understand and maintain.

```
┌──────────────────────────────────────────────────────────────────┐
│               COMPLEXITY EXPLOSION                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Simple Workflow (2 agents):                                    │
│  • 2 execution paths                                            │
│  • 4 potential error states                                     │
│  • 1 state schema                                               │
│                                                                  │
│  Complex Workflow (10 agents, conditional routing):             │
│  • 50+ execution paths                                          │
│  • 200+ potential error states                                  │
│  • 10 state schemas                                             │
│  • Debugging a failure requires tracing through multiple agents │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Mitigation Strategies:**

1. **Workflow Visualization Tools**
   - Generate DAG diagrams from harness code
   - Live execution tracing in UI
   - State snapshots at each step

2. **Modular Design**
   - Break large harnesses into sub-workflows
   - Reusable agent profiles
   - Clear interfaces between components

3. **Testing**
   - Unit test each agent independently
   - Integration test full workflow with fixtures
   - Chaos testing (inject random failures)

**Example: Testing Strategy**

```
┌────────────────────────────────────────────────────────────────────┐
│                THREE-TIER TESTING APPROACH                         │
└────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TIER 1: Unit Test (Single Agent)                              │
├─────────────────────────────────────────────────────────────────┤
│  Test: test_network_agent()                                     │
│                                                                 │
│  Setup:                                                         │
│    task = {"logs": "..."}                                       │
│                                                                 │
│  Execute:                                                       │
│    output = network_agent.run(task)                             │
│                                                                 │
│  Assert:                                                        │
│    output["network_ok"] == True                                 │
│                                                                 │
│  Purpose: Verify individual agent produces expected output      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TIER 2: Integration Test (Full Workflow)                      │
├─────────────────────────────────────────────────────────────────┤
│  Test: test_atiya_workflow()                                    │
│                                                                 │
│  Setup:                                                         │
│    task = load_fixture("test_failure_001")                      │
│    ↑ Known test case with expected root cause                   │
│                                                                 │
│  Execute:                                                       │
│    result = atiya_harness.run(task)                             │
│    ↑ Run full cascade: Network → Config → Timing → Synthesis   │
│                                                                 │
│  Assert:                                                        │
│    result["root_cause"] == "NTP server unreachable"             │
│                                                                 │
│  Purpose: Verify end-to-end workflow produces correct diagnosis │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TIER 3: Chaos Test (Resilience Under Failure)                 │
├─────────────────────────────────────────────────────────────────┤
│  Test: test_workflow_resilience()                               │
│                                                                 │
│  Setup:                                                         │
│    Enable failure injection at 20% rate                         │
│    with inject_random_failures(rate=0.2):                       │
│      ↑ Randomly fail agent calls, timeouts, etc.                │
│                                                                 │
│  Execute:                                                       │
│    result = atiya_harness.run(task)                             │
│    ↑ Harness should retry and recover                           │
│                                                                 │
│  Assert:                                                        │
│    result is not None                                           │
│    ↑ Workflow completed despite 20% failure rate                │
│                                                                 │
│  Purpose: Verify error recovery mechanisms work under stress    │
└─────────────────────────────────────────────────────────────────┘

Test Coverage Matrix:
┌──────────────┬─────────┬──────────────┬─────────────────┐
│ Test Type    │ Scope   │ What It Tests│ Example         │
├──────────────┼─────────┼──────────────┼─────────────────┤
│ Unit         │ Agent   │ Logic        │ Network agent   │
│              │         │ correctness  │ detects latency │
├──────────────┼─────────┼──────────────┼─────────────────┤
│ Integration  │ Workflow│ End-to-end   │ Full cascade    │
│              │         │ accuracy     │ finds root cause│
├──────────────┼─────────┼──────────────┼─────────────────┤
│ Chaos        │ System  │ Resilience   │ Recovers from   │
│              │         │ under failure│ 20% error rate  │
└──────────────┴─────────┴──────────────┴─────────────────┘
```

---

### 2. State Propagation Errors

**Problem:** Incorrect or missing state passed between agents leads to cascading failures.

```
┌──────────────────────────────────────────────────────────────────┐
│              STATE PROPAGATION FAILURE                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: Network Agent                                          │
│  └─ Output: {"network_ok": true, "latency_ms": 50}              │
│                                                                  │
│  Step 2: Config Agent                                           │
│  └─ EXPECTED INPUT: network_ok, latency_ms                      │
│  └─ ACTUAL INPUT: {} (state not passed!)                        │
│  └─ ERROR: KeyError("network_ok")                               │
│                                                                  │
│  Result: Workflow aborted, no diagnosis                         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Root Causes:**
- State manager bug (key typo, serialization failure)
- Agent didn't write output to state
- Schema mismatch between agents

**Mitigation Strategies:**

1. **Schema Validation**
   - Define expected state schema per agent
   - Validate state at each step
   - Fail fast on schema violations

```
┌────────────────────────────────────────────────────────────────────┐
│              SCHEMA VALIDATION WITH PYDANTIC                       │
└────────────────────────────────────────────────────────────────────┘

Step 1: Define Expected Schema
┌─────────────────────────────────────────────────────────────────┐
│  NetworkAgentOutput Schema:                                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Field         │ Type        │ Required │ Description      │  │
│  ├───────────────┼─────────────┼──────────┼──────────────────┤  │
│  │ network_ok    │ bool        │ Yes      │ Network status   │  │
│  │ latency_ms    │ int         │ Yes      │ Latency in ms    │  │
│  │ findings      │ list[str]   │ Yes      │ Issues found     │  │
│  └───────────────┴─────────────┴──────────┴──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

Step 2: Validation Wrapper
┌─────────────────────────────────────────────────────────────────┐
│  network_agent_wrapper(task, state):                            │
│                                                                 │
│    1. Run agent to get raw output                              │
│       output = network_agent.run(task)                          │
│       ↓                                                         │
│       output = {                                                │
│         "network_ok": true,                                     │
│         "latency_ms": 50,                                       │
│         "findings": ["Latency spike on eth0"]                   │
│       }                                                         │
│                                                                 │
│    2. Validate against schema                                  │
│       validated = NetworkAgentOutput(**output)                  │
│       ↓                                                         │
│       If output matches schema: Continue                        │
│       If output invalid: Raise ValidationError                  │
│                                                                 │
│    3. Store validated output in state                          │
│       state["network"] = validated.dict()                       │
│                                                                 │
│    4. Return validated object                                  │
│       return validated                                          │
└─────────────────────────────────────────────────────────────────┘

Validation Outcomes:
┌──────────────┬──────────────────────────────────────────────────┐
│ Scenario     │ Result                                           │
├──────────────┼──────────────────────────────────────────────────┤
│ Valid output │ Passes validation, stored in state               │
├──────────────┼──────────────────────────────────────────────────┤
│ Missing field│ ValidationError: "network_ok is required"        │
├──────────────┼──────────────────────────────────────────────────┤
│ Wrong type   │ ValidationError: "latency_ms must be int"        │
├──────────────┼──────────────────────────────────────────────────┤
│ Extra field  │ Ignored (unless strict mode enabled)             │
└──────────────┴──────────────────────────────────────────────────┘

Key Benefit: Fail fast at agent boundary, not deep in workflow
```

2. **Immutable State**
   - Prevent agents from overwriting each other's state
   - Use namespaced keys (agent_name.field)

```
┌────────────────────────────────────────────────────────────────────┐
│              STATE NAMESPACING: AVOID KEY COLLISIONS               │
└────────────────────────────────────────────────────────────────────┘

BAD PATTERN: Global Namespace (Collision Risk)
┌─────────────────────────────────────────────────────────────────┐
│  Agent A executes:                                              │
│    state["result"] = "Network latency detected"                 │
│                                                                 │
│  State after Agent A:                                           │
│    {"result": "Network latency detected"}                       │
│                                                                 │
│  Agent B executes:                                              │
│    state["result"] = "Config error found"  ← OVERWRITES Agent A │
│                                                                 │
│  State after Agent B:                                           │
│    {"result": "Config error found"}  ✗ Agent A result lost!     │
└─────────────────────────────────────────────────────────────────┘

GOOD PATTERN: Namespaced Keys (Isolated)
┌─────────────────────────────────────────────────────────────────┐
│  Agent A executes:                                              │
│    state["agent_a.result"] = "Network latency detected"         │
│                                                                 │
│  State after Agent A:                                           │
│    {"agent_a.result": "Network latency detected"}               │
│                                                                 │
│  Agent B executes:                                              │
│    state["agent_b.result"] = "Config error found"               │
│                                                                 │
│  State after Agent B:                                           │
│    {                                                            │
│      "agent_a.result": "Network latency detected",              │
│      "agent_b.result": "Config error found"                     │
│    }  ✓ Both results preserved!                                 │
└─────────────────────────────────────────────────────────────────┘

BETTER PATTERN: Nested Structure (Hierarchical)
┌─────────────────────────────────────────────────────────────────┐
│  state = {                                                      │
│    "network": {                                                 │
│      "result": "Latency detected",                              │
│      "confidence": 0.9                                          │
│    },                                                           │
│    "config": {                                                  │
│      "result": "Config error found",                            │
│      "confidence": 0.85                                         │
│    }                                                            │
│  }                                                              │
│                                                                 │
│  Access pattern:                                                │
│    network_confidence = state["network"]["confidence"]          │
│    config_result = state["config"]["result"]                    │
└─────────────────────────────────────────────────────────────────┘

Key Benefit: Each agent has isolated namespace, preventing
             accidental overwrites and data corruption
```

3. **Checkpointing**
   - Save state snapshots after each step
   - Enable rollback on error

```
┌────────────────────────────────────────────────────────────────────┐
│         CHECKPOINTING: State Snapshots for Rollback               │
└────────────────────────────────────────────────────────────────────┘

Flow: harness_with_checkpoints(task)

┌─────────────────────────────────────────────────────────────────┐
│  Initialize                                                     │
│  state = {}                                                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Run Agent A                                            │
├─────────────────────────────────────────────────────────────────┤
│  output_a = agent_a.run(task)                                   │
│  state["agent_a"] = output_a                                    │
│                                                                 │
│  State: {"agent_a": output_a}                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  CREATE CHECKPOINT 1                                            │
│  checkpoint_1 = state.copy()                                    │
│                                                                 │
│  Checkpoint saved: {"agent_a": output_a}                        │
│  ↑ Immutable snapshot for potential rollback                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Run Agent B (with error handling)                      │
└─────────────────────────────────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │ Try block   │
                    └──────┬──────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ output_b = agent_b.run │
              │   (task, input=output_a)│
              └────────┬───────────────┘
                       │
                       ▼
                   Success?
                       │
              ┌────────┴────────┐
             YES               NO
              │                 │
              ▼                 ▼
    ┌──────────────────┐  ┌──────────────────────────┐
    │ Update state     │  │ Exception caught         │
    │ state["agent_b"] │  │                          │
    │ = output_b       │  │ 1. Rollback to checkpoint│
    │                  │  │    state = checkpoint_1  │
    │ Continue workflow│  │                          │
    └──────────────────┘  │ 2. Re-raise exception    │
                          │    raise                 │
                          └──────────────────────────┘

Checkpoint Timeline:
┌─────────────────────────────────────────────────────────────────┐
│ Time │ Event            │ State              │ Checkpoint       │
├──────┼──────────────────┼────────────────────┼──────────────────┤
│ T0   │ Initialize       │ {}                 │ None             │
│ T1   │ Agent A completes│ {agent_a: ...}     │ None             │
│ T2   │ Checkpoint saved │ {agent_a: ...}     │ checkpoint_1: {} │
│ T3a  │ Agent B succeeds │ {agent_a, agent_b} │ checkpoint_1     │
│ T3b  │ Agent B FAILS    │ ROLLBACK→{agent_a} │ checkpoint_1     │
└──────┴──────────────────┴────────────────────┴──────────────────┘

Key Benefit: On failure, state reverts to last known good state,
             preventing corruption from partial updates
```

---

### 3. Cost Explosion (Multiple LLM Calls)

**Problem:** Each agent invokes an LLM, costs multiply quickly.

```
┌──────────────────────────────────────────────────────────────────┐
│                    COST EXPLOSION                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Single LLM Call:                                                │
│  • GPT-4: $0.03 / 1K input tokens, $0.06 / 1K output tokens     │
│  • Input: 5K tokens, Output: 500 tokens                         │
│  • Cost: (5 * 0.03) + (0.5 * 0.06) = $0.18                      │
│                                                                  │
│  Atiya Harness (4 agents):                                      │
│  • Network Agent: 3K in, 500 out = $0.12                        │
│  • Config Agent: 3K in, 500 out = $0.12                         │
│  • Timing Agent: 3K in, 500 out = $0.12                         │
│  • Synthesis Agent: 5K in, 1K out = $0.21                       │
│  • TOTAL: $0.57 per workflow (3x single call)                   │
│                                                                  │
│  At scale (1,000 workflows/day):                                │
│  • Single call: $180/day, $5,400/month                          │
│  • Harness: $570/day, $17,100/month                             │
│  • DIFFERENCE: $11,700/month                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Mitigation Strategies:**

1. **Model Selection Per Agent**
   - Use cheaper models (GPT-3.5) for simple tasks
   - Reserve GPT-4 for complex reasoning

```
┌────────────────────────────────────────────────────────────────────┐
│          MODEL SELECTION: Right Model for Right Task               │
└────────────────────────────────────────────────────────────────────┘

Agent Configuration by Complexity:

┌─────────────────────────────────────────────────────────────────┐
│  Agent: Triage                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Model: GPT-3.5-turbo                                           │
│  Task Complexity: Simple (classification)                       │
│  Reasoning: "Is this network, config, or timing issue?"         │
│  Cost: $0.001 per 1K tokens (input)                             │
│  Justification: Classification task, simple pattern matching    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Agent: Network Specialist                                      │
├─────────────────────────────────────────────────────────────────┤
│  Model: GPT-4                                                   │
│  Task Complexity: High (complex diagnostics)                    │
│  Reasoning: Multi-step analysis of network logs, routing        │
│  Cost: $0.03 per 1K tokens (input)                              │
│  Justification: Requires deep reasoning about network behavior  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Agent: Synthesis                                               │
├─────────────────────────────────────────────────────────────────┤
│  Model: GPT-4                                                   │
│  Task Complexity: High (integration of evidence)                │
│  Reasoning: Combine network + config + timing findings          │
│  Cost: $0.03 per 1K tokens (input)                              │
│  Justification: Critical final diagnosis, accuracy paramount    │
└─────────────────────────────────────────────────────────────────┘

Cost Comparison:
┌──────────────┬─────────────┬──────────────┬──────────────────┐
│ Agent        │ Model       │ Input Tokens │ Cost             │
├──────────────┼─────────────┼──────────────┼──────────────────┤
│ Triage       │ GPT-3.5     │ 1,000        │ $0.001           │
│ Network      │ GPT-4       │ 3,000        │ $0.09            │
│ Synthesis    │ GPT-4       │ 5,000        │ $0.15            │
├──────────────┼─────────────┼──────────────┼──────────────────┤
│ TOTAL        │ Mixed       │ 9,000        │ $0.241           │
└──────────────┴─────────────┴──────────────┴──────────────────┘

vs All GPT-4:
┌──────────────┬─────────────┬──────────────┬──────────────────┐
│ Agent        │ Model       │ Input Tokens │ Cost             │
├──────────────┼─────────────┼──────────────┼──────────────────┤
│ Triage       │ GPT-4       │ 1,000        │ $0.03            │
│ Network      │ GPT-4       │ 3,000        │ $0.09            │
│ Synthesis    │ GPT-4       │ 5,000        │ $0.15            │
├──────────────┼─────────────┼──────────────┼──────────────────┤
│ TOTAL        │ GPT-4       │ 9,000        │ $0.27            │
└──────────────┴─────────────┴──────────────┴──────────────────┘

Savings: $0.27 - $0.241 = $0.029 per workflow (10.7% reduction)
At 1,000 workflows/day: $29/day, $870/month savings
```

2. **Conditional Execution**
   - Skip agents if prior steps already found root cause
   - Early termination when confidence threshold met

```
┌────────────────────────────────────────────────────────────────────┐
│        EARLY TERMINATION: Skip Unnecessary Agent Calls             │
└────────────────────────────────────────────────────────────────────┘

Flow: optimized_harness(task)

┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Network Agent                                          │
├─────────────────────────────────────────────────────────────────┤
│  network_output = network_agent.run(task)                       │
│                                                                 │
│  Example output:                                                │
│  {                                                              │
│    "diagnosis": "Connectivity issue on eth0",                   │
│    "confidence": 0.97                                           │
│  }                                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Check confidence threshold                                     │
│  Is network_output["confidence"] > 0.95?                        │
└─────────────────────────────────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                   YES            NO
                    │              │
                    ▼              ▼
            ┌──────────────┐  ┌──────────────────────────────────┐
            │ RETURN       │  │ Continue to Config Agent         │
            │ network_     │  │                                  │
            │ output       │  │ STEP 2: Config Agent             │
            │              │  │ config_output =                  │
            │ Skip Config  │  │   config_agent.run(task)         │
            │ Skip Timing  │  │                                  │
            │              │  │ Example output:                  │
            │ Cost saved:  │  │ {"diagnosis": "...",             │
            │ 2 agents     │  │  "confidence": 0.88}             │
            └──────────────┘  └─────────┬────────────────────────┘
                                        │
                                        ▼
                              Is config_output["confidence"] > 0.95?
                                        │
                                 ┌──────┴──────┐
                                YES            NO
                                 │              │
                                 ▼              ▼
                         ┌──────────────┐  ┌──────────────────┐
                         │ RETURN       │  │ Continue to      │
                         │ config_      │  │ Timing Agent     │
                         │ output       │  │                  │
                         │              │  │ STEP 3:          │
                         │ Skip Timing  │  │ timing_output =  │
                         │              │  │  timing_agent.   │
                         │ Cost saved:  │  │  run(task)       │
                         │ 1 agent      │  │                  │
                         └──────────────┘  │ RETURN           │
                                           │ timing_output    │
                                           │                  │
                                           │ (no more agents) │
                                           └──────────────────┘

Cost Comparison:
┌──────────────────────────┬──────────────┬──────────────────────┐
│ Scenario                 │ Agents Run   │ Cost                 │
├──────────────────────────┼──────────────┼──────────────────────┤
│ Network confident (0.97) │ 1 (Network)  │ $0.12                │
│ Config confident (0.96)  │ 2 (Net+Cfg)  │ $0.24                │
│ Low confidence all       │ 3 (all)      │ $0.36                │
├──────────────────────────┼──────────────┼──────────────────────┤
│ Average (40% early term) │ 1.6 agents   │ $0.19 (47% savings)  │
└──────────────────────────┴──────────────┴──────────────────────┘

Key Benefit: Pay only for agents that add value
             High-confidence early findings save ~50% cost
```

3. **Caching**
   - Cache agent outputs for identical inputs
   - Reuse prior diagnoses for similar failures

```
┌────────────────────────────────────────────────────────────────────┐
│           CACHING: Reuse Results for Identical Inputs              │
└────────────────────────────────────────────────────────────────────┘

Flow: cached_agent_run(agent, task)

┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Generate Cache Key                                     │
├─────────────────────────────────────────────────────────────────┤
│  1. Serialize task to JSON (sorted keys for consistency)        │
│     json_str = json.dumps(task, sort_keys=True)                 │
│                                                                 │
│  2. Hash JSON to create unique identifier                       │
│     task_hash = hashlib.md5(json_str.encode()).hexdigest()      │
│                                                                 │
│  3. Combine agent name + hash for namespaced key                │
│     cache_key = f"{agent.name}:{task_hash}"                     │
│                                                                 │
│  Example:                                                       │
│    task = {"test": "ntp_sync", "env": "testbed-007"}            │
│    task_hash = "a3f8b2c1..."                                    │
│    cache_key = "network_agent:a3f8b2c1..."                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Check Cache                                            │
├─────────────────────────────────────────────────────────────────┤
│  Is cache_key in cache?                                         │
└─────────────────────────────────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                   YES            NO
                    │              │
                    ▼              ▼
         ┌────────────────────┐  ┌──────────────────────────────┐
         │ CACHE HIT          │  │ CACHE MISS                   │
         │                    │  │                              │
         │ Return cached      │  │ STEP 3: Run Agent            │
         │ result immediately │  │ output = agent.run(task)     │
         │                    │  │                              │
         │ Cost: $0           │  │ Cost: $0.12 (LLM call)       │
         │ Latency: <1ms      │  │ Latency: 3.2s (LLM latency)  │
         │                    │  │                              │
         │ return cache[      │  │ STEP 4: Store in Cache       │
         │   cache_key]       │  │ cache[cache_key] = output    │
         │                    │  │                              │
         │                    │  │ STEP 5: Return Output        │
         │                    │  │ return output                │
         └────────────────────┘  └──────────────────────────────┘

Cache Data Structure:
┌─────────────────────────────────────────────────────────────────┐
│ cache = {                                                       │
│   "network_agent:a3f8b2c1...": {                                │
│     "network_ok": true,                                         │
│     "findings": ["Latency on eth0"],                            │
│     "confidence": 0.85                                          │
│   },                                                            │
│   "config_agent:7d9e1f4a...": {                                 │
│     "config_issues": ["ACL blocked NTP"],                       │
│     "confidence": 0.92                                          │
│   }                                                             │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘

Performance Impact:
┌──────────────┬─────────────┬──────────────┬─────────────────┐
│ Scenario     │ Cache Hit % │ Avg Cost     │ Savings         │
├──────────────┼─────────────┼──────────────┼─────────────────┤
│ No caching   │ 0%          │ $0.36        │ Baseline        │
│ 30% hit rate │ 30%         │ $0.25        │ 30% ($0.11)     │
│ 60% hit rate │ 60%         │ $0.14        │ 61% ($0.22)     │
└──────────────┴─────────────┴──────────────┴─────────────────┘

Cache Invalidation: Expire entries after 24 hours or on
                     configuration changes to avoid stale data
```

4. **Budget Limits**
   - Set max cost per workflow
   - Abort if budget exceeded

```
┌────────────────────────────────────────────────────────────────────┐
│         BUDGET CONTROL: Enforce Cost Limits Per Workflow           │
└────────────────────────────────────────────────────────────────────┘

Flow: budget_controlled_harness(task, max_cost_usd=1.00)

Initialize:
  total_cost = 0.0
  state = {}
  max_cost_usd = 1.00

For each agent in [network_agent, config_agent, timing_agent]:

  ┌─────────────────────────────────────────────────────────────┐
  │ Run agent with cost tracking                                │
  │ output, cost = agent.run_with_cost_tracking(task)           │
  │                                                             │
  │ Example:                                                    │
  │   output = {"network_ok": true, ...}                        │
  │   cost = 0.12  (based on tokens used)                       │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Update total cost                                           │
  │ total_cost += cost                                          │
  │                                                             │
  │ Example progression:                                        │
  │   After Network: total_cost = 0.12                          │
  │   After Config:  total_cost = 0.24                          │
  │   After Timing:  total_cost = 0.36                          │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Check budget limit                                          │
  │ Is total_cost > max_cost_usd?                               │
  └─────────────────────────────────────────────────────────────┘
                             │
                      ┌──────┴──────┐
                     YES            NO
                      │              │
                      ▼              ▼
         ┌──────────────────────┐  ┌────────────────────────┐
         │ BUDGET EXCEEDED      │  │ Continue workflow      │
         │                      │  │                        │
         │ Raise                │  │ Store output in state  │
         │ BudgetExceededError  │  │ state[agent.name] =    │
         │                      │  │   output               │
         │ Message:             │  │                        │
         │ "Workflow cost $1.25 │  │ Proceed to next agent  │
         │  exceeds budget      │  └────────────────────────┘
         │  $1.00"              │
         │                      │
         │ Workflow ABORTED     │
         └──────────────────────┘

After all agents (if budget not exceeded):
  ┌─────────────────────────────────────────────────────────────┐
  │ Return complete state                                       │
  │ state = {                                                   │
  │   "network_agent": network_output,                          │
  │   "config_agent": config_output,                            │
  │   "timing_agent": timing_output                             │
  │ }                                                           │
  │                                                             │
  │ Total cost: $0.36 (within $1.00 budget)                     │
  └─────────────────────────────────────────────────────────────┘

Budget Enforcement Example:
┌────────────┬──────────────┬──────────────┬─────────────────┐
│ Agent      │ Cost         │ Total Cost   │ Status          │
├────────────┼──────────────┼──────────────┼─────────────────┤
│ Network    │ $0.12        │ $0.12        │ ✓ Continue      │
│ Config     │ $0.12        │ $0.24        │ ✓ Continue      │
│ Timing     │ $0.12        │ $0.36        │ ✓ Continue      │
│ (Synthesis)│ $0.75        │ $1.11        │ ✗ ABORT (>$1.00)│
└────────────┴──────────────┴──────────────┴─────────────────┘

Key Benefit: Prevents runaway costs, especially in loops or
             when agents retry multiple times
```

---

### 4. Debugging Multi-Step Failures

**Problem:** When a workflow fails, it's unclear which agent caused the issue and why.

```
┌──────────────────────────────────────────────────────────────────┐
│              DEBUGGING MULTI-STEP FAILURE                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Error Log:                                                      │
│  "WorkflowError: Atiya harness failed to diagnose test failure" │
│                                                                  │
│  Questions:                                                      │
│  • Which agent failed? Network? Config? Timing?                 │
│  • What was the error? Timeout? Invalid output? Logic error?    │
│  • What state was passed to the failing agent?                  │
│  • Can we reproduce the failure?                                │
│                                                                  │
│  Challenge: 4 agents, each made 1-2 LLM calls, total 6 calls.  │
│  Need to trace through entire execution to find root cause.     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Mitigation Strategies:**

1. **Structured Logging**
   - Log every agent invocation with inputs, outputs, errors
   - Include timestamps, agent names, state snapshots

```
┌────────────────────────────────────────────────────────────────────┐
│         STRUCTURED LOGGING: Complete Execution Trace               │
└────────────────────────────────────────────────────────────────────┘

Flow: instrumented_agent_run(agent, task, state)

┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Log Agent Start                                        │
├─────────────────────────────────────────────────────────────────┤
│  logger.info("Starting {agent.name}", extra={...})              │
│                                                                 │
│  Log entry:                                                     │
│  {                                                              │
│    "level": "INFO",                                             │
│    "message": "Starting network_agent",                         │
│    "timestamp": "2026-08-20T10:00:00Z",                         │
│    "agent": "network_agent",                                    │
│    "task_id": "test-failure-001",                               │
│    "state": {"prior_findings": [...]}                           │
│  }                                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Execute Agent (with exception handling)                │
└─────────────────────────────────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │ Try block   │
                    └──────┬──────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ output = agent.run(    │
              │   task, state=state)   │
              └────────┬───────────────┘
                       │
                   Success?
                       │
              ┌────────┴────────┐
             YES               NO
              │                 │
              ▼                 ▼
┌──────────────────────────┐  ┌──────────────────────────────────┐
│ STEP 3a: Log Success     │  │ STEP 3b: Log Error               │
├──────────────────────────┤  ├──────────────────────────────────┤
│ logger.info(             │  │ logger.error(                    │
│   "Completed...",        │  │   "Failed...",                   │
│   extra={...})           │  │   extra={...},                   │
│                          │  │   exc_info=True)                 │
│ Log entry:               │  │                                  │
│ {                        │  │ Log entry:                       │
│   "level": "INFO",       │  │ {                                │
│   "message":             │  │   "level": "ERROR",              │
│     "Completed           │  │   "message":                     │
│      network_agent",     │  │     "Failed network_agent",      │
│   "timestamp":           │  │   "timestamp":                   │
│     "2026-08-20T10:00:03"│  │     "2026-08-20T10:00:02Z",      │
│   "agent":               │  │   "agent": "network_agent",      │
│     "network_agent",     │  │   "error": "TimeoutError: ...",  │
│   "output": {            │  │   "state": {...},                │
│     "network_ok": true,  │  │   "stack_trace": "..."           │
│     "confidence": 0.85   │  │ }                                │
│   }                      │  │                                  │
│ }                        │  │ Re-raise exception               │
│                          │  └──────────────────────────────────┘
│ Return output            │
└──────────────────────────┘

Log Output Timeline:
┌─────────────────────────────────────────────────────────────────┐
│ T0: INFO  - Starting network_agent (task-001, state={})         │
│ T3: INFO  - Completed network_agent (confidence=0.85)           │
│ T3: INFO  - Starting config_agent (task-001, state={net...})    │
│ T6: ERROR - Failed config_agent (TimeoutError: ...)             │
│ T8: INFO  - Starting config_agent [RETRY 1]                     │
│ T11: INFO - Completed config_agent (confidence=0.92)            │
└─────────────────────────────────────────────────────────────────┘

Key Benefits:
  • Complete audit trail of all agent executions
  • Searchable by task_id, agent name, timestamp
  • Error context preserved with stack traces
  • State snapshots enable debugging failed workflows
```

2. **Distributed Tracing**
   - Use OpenTelemetry or similar to trace requests across agents
   - Visualize execution flow in tools like Jaeger

```
┌────────────────────────────────────────────────────────────────────┐
│        DISTRIBUTED TRACING: Visualize Multi-Agent Flow             │
└────────────────────────────────────────────────────────────────────┘

Implementation: traced_harness(task)

┌─────────────────────────────────────────────────────────────────┐
│  Root Span: atiya_harness                                       │
├─────────────────────────────────────────────────────────────────┤
│  with tracer.start_as_current_span("atiya_harness") as span:    │
│    span.set_attribute("task.id", task["id"])                    │
│                                                                 │
│    Span attributes:                                             │
│      - name: "atiya_harness"                                    │
│      - task.id: "test-failure-001"                              │
│      - start_time: 2026-08-20T10:00:00Z                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Child Span 1│     │ Child Span 2│     │ Child Span 3│
├─────────────┤     ├─────────────┤     ├─────────────┤
│ network_    │     │ config_     │     │ timing_     │
│ agent       │     │ agent       │     │ agent       │
│             │     │             │     │             │
│ start: T0   │     │ start: T3   │     │ start: T7   │
│ end: T3     │     │ end: T7     │     │ end: T11    │
│ duration:   │     │ duration:   │     │ duration:   │
│ 3.2s        │     │ 3.8s        │     │ 4.1s        │
└─────────────┘     └─────────────┘     └─────────────┘

Jaeger UI Visualization:
┌─────────────────────────────────────────────────────────────────┐
│ Trace: atiya_harness (11.1s total)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ atiya_harness                    |████████████████████████| 11.1s
│   network_agent                  |█████|                    3.2s
│   config_agent                        |██████|              3.8s
│   timing_agent                             |███████|        4.1s
│                                                                 │
│ 0s        2s        4s        6s        8s       10s      12s  │
└─────────────────────────────────────────────────────────────────┘

Span Nesting Structure:
┌─────────────────────────────────────────────────────────────────┐
│ atiya_harness (root span)                                       │
│ ├── network_agent (child span)                                  │
│ │   ├── context_retrieval (nested child)                        │
│ │   ├── llm_call (nested child)                                 │
│ │   └── validation (nested child)                               │
│ ├── config_agent (child span)                                   │
│ │   ├── context_retrieval                                       │
│ │   ├── llm_call                                                │
│ │   └── validation                                              │
│ └── timing_agent (child span)                                   │
│     ├── context_retrieval                                       │
│     ├── llm_call                                                │
│     └── validation                                              │
└─────────────────────────────────────────────────────────────────┘

Attributes Captured Per Span:
┌──────────────────┬──────────────────────────────────────────────┐
│ Attribute        │ Example Value                                │
├──────────────────┼──────────────────────────────────────────────┤
│ span.name        │ "network_agent"                              │
│ agent.model      │ "gpt-4"                                      │
│ agent.confidence │ 0.85                                         │
│ tokens.input     │ 3000                                         │
│ tokens.output    │ 500                                          │
│ cost.usd         │ 0.12                                         │
│ error.occurred   │ false                                        │
└──────────────────┴──────────────────────────────────────────────┘

Key Benefits:
  • Visual timeline of agent execution
  • Identify bottlenecks (which agent is slow?)
  • Debug cascading failures (which span errored?)
  • Performance optimization (can we parallelize?)
```

3. **State Snapshots**
   - Save full state after each step for post-mortem analysis

```
┌────────────────────────────────────────────────────────────────────┐
│         STATE SNAPSHOTS: Capture Workflow History                  │
└────────────────────────────────────────────────────────────────────┘

Flow: harness_with_snapshots(task)

Initialize:
  state = {}
  snapshots = []

For each agent in [network_agent, config_agent, timing_agent]:

  ┌─────────────────────────────────────────────────────────────┐
  │ Execute agent                                               │
  │ output = agent.run(task, state=state)                       │
  │ state[agent.name] = output                                  │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Create snapshot                                             │
  │ snapshot = {                                                │
  │   "step": i,                                                │
  │   "agent": agent.name,                                      │
  │   "state": state.copy(),  ← Full state at this point        │
  │   "timestamp": time.time()                                  │
  │ }                                                           │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Append to snapshots list                                    │
  │ snapshots.append(snapshot)                                  │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             └──▶ Continue to next agent

After all agents:
  ┌─────────────────────────────────────────────────────────────┐
  │ Return state and snapshots                                  │
  │ return state, snapshots                                     │
  └─────────────────────────────────────────────────────────────┘

Snapshot Timeline Example:
┌─────────────────────────────────────────────────────────────────┐
│ Snapshot 0: After network_agent                                 │
│ {                                                               │
│   "step": 0,                                                    │
│   "agent": "network_agent",                                     │
│   "timestamp": 1692534003.2,                                    │
│   "state": {                                                    │
│     "network_agent": {                                          │
│       "network_ok": true,                                       │
│       "findings": ["Latency spike on eth0"],                    │
│       "confidence": 0.85                                        │
│     }                                                           │
│   }                                                             │
│ }                                                               │
├─────────────────────────────────────────────────────────────────┤
│ Snapshot 1: After config_agent                                  │
│ {                                                               │
│   "step": 1,                                                    │
│   "agent": "config_agent",                                      │
│   "timestamp": 1692534007.0,                                    │
│   "state": {                                                    │
│     "network_agent": {...},  ← Preserved from Snapshot 0        │
│     "config_agent": {                                           │
│       "config_issues": ["ACL blocked NTP"],                     │
│       "confidence": 0.92                                        │
│     }                                                           │
│   }                                                             │
│ }                                                               │
├─────────────────────────────────────────────────────────────────┤
│ Snapshot 2: After timing_agent                                  │
│ {                                                               │
│   "step": 2,                                                    │
│   "agent": "timing_agent",                                      │
│   "timestamp": 1692534011.1,                                    │
│   "state": {                                                    │
│     "network_agent": {...},                                     │
│     "config_agent": {...},                                      │
│     "timing_agent": {                                           │
│       "timing_issues": ["Clock drift 15s"],                     │
│       "root_cause": "NTP unreachable",                          │
│       "confidence": 0.78                                        │
│     }                                                           │
│   }                                                             │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘

Post-Mortem Debugging:
  If workflow fails at config_agent, inspect:
    - Snapshot 0: What did network_agent produce?
    - Snapshot 1 (partial): What input did config_agent receive?
  
  Enables time-travel debugging without re-running entire workflow

Storage Options:
  • In-memory: Fast, lost on process exit
  • JSON file: Persistent, human-readable
  • Database: Queryable, long-term retention
```

4. **Replay Capability**
   - Save all inputs/outputs to enable exact replay of failed workflows

```
┌────────────────────────────────────────────────────────────────────┐
│           REPLAY CAPABILITY: Record and Replay Workflows           │
└────────────────────────────────────────────────────────────────────┘

PART 1: Recording Execution
────────────────────────────

Flow: replayable_harness(task)

Initialize:
  execution_log = []

For each agent in agents:

  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 1: Log input                                           │
  │ execution_log.append({                                      │
  │   "type": "input",                                          │
  │   "agent": agent.name,                                      │
  │   "data": task                                              │
  │ })                                                          │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 2: Run agent                                           │
  │ output = agent.run(task)                                    │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 3: Log output                                          │
  │ execution_log.append({                                      │
  │   "type": "output",                                         │
  │   "agent": agent.name,                                      │
  │   "data": output                                            │
  │ })                                                          │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             └──▶ Continue to next agent

After all agents:
  ┌─────────────────────────────────────────────────────────────┐
  │ Save execution log to file                                  │
  │ save_execution_log(execution_log)                           │
  │                                                             │
  │ Filename: "workflow_test-failure-001_20260820.json"         │
  └─────────────────────────────────────────────────────────────┘

Execution Log Structure:
┌─────────────────────────────────────────────────────────────────┐
│ [                                                               │
│   {"type": "input", "agent": "network_agent",                   │
│    "data": {"test": "ntp_sync", "logs": "..."}},                │
│   {"type": "output", "agent": "network_agent",                  │
│    "data": {"network_ok": true, "confidence": 0.85}},           │
│   {"type": "input", "agent": "config_agent",                    │
│    "data": {"test": "ntp_sync", "logs": "..."}},                │
│   {"type": "output", "agent": "config_agent",                   │
│    "data": {"config_issues": [...], "confidence": 0.92}},       │
│   ...                                                           │
│ ]                                                               │
└─────────────────────────────────────────────────────────────────┘

PART 2: Replaying Execution
────────────────────────────

Flow: replay_from_log(log_file)

┌─────────────────────────────────────────────────────────────────┐
│ Load execution log                                              │
│ execution_log = load_execution_log(log_file)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
For each entry in execution_log:

  ┌─────────────────────────────────────────────────────────────┐
  │ Check entry type                                            │
  └─────────────────────────────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
            entry["type"] == ?
                    │             │
             ┌──────┴──┐      ┌───┴──────┐
            "input"   "output"            
             │              │
             ▼              ▼
  ┌───────────────┐  ┌───────────────────────┐
  │ Print input   │  │ Print output          │
  │ "Agent X      │  │ "Agent X produced:    │
  │  received:    │  │  {network_ok: true,   │
  │  {test:...}"  │  │   confidence: 0.85}"  │
  └───────────────┘  └───────────────────────┘

Replay Output:
┌─────────────────────────────────────────────────────────────────┐
│ Agent network_agent received: {"test": "ntp_sync", ...}         │
│ Agent network_agent produced: {"network_ok": true, ...}         │
│ Agent config_agent received: {"test": "ntp_sync", ...}          │
│ Agent config_agent produced: {"config_issues": [...], ...}      │
│ Agent timing_agent received: {"test": "ntp_sync", ...}          │
│ Agent timing_agent produced: {"timing_issues": [...], ...}      │
└─────────────────────────────────────────────────────────────────┘

Use Cases:
  • Debug failures without re-running expensive LLM calls
  • Reproduce exact agent behavior for testing
  • Audit trail for compliance/security review
  • Performance analysis of historical executions
```

---

## Core Mechanics

### Loops: Each Iteration Until Task Finished

**Concept:** Many harnesses implement **iterative refinement**: repeat agent calls until task is complete or max iterations reached.

```
┌──────────────────────────────────────────────────────────────────┐
│                    ITERATIVE LOOP HARNESS                        │
└──────────────────────────────────────────────────────────────────┘

Initialize:
  iteration = 0
  max_iterations = 5
  done = False
  state = {}

Loop:
  while not done and iteration < max_iterations:
      iteration += 1
      
      # Agent call
      output = agent.run(task, state=state)
      state.update(output)
      
      # Check termination condition
      done = output.get("task_complete", False)
      
      # Update task for next iteration
      task["feedback"] = output.get("feedback", "")
  
  if done:
      return state
  else:
      raise MaxIterationsExceeded("Task not completed in 5 iterations")
```

**Visual Flow:**

```
    Start
      │
      ▼
┌─────────────┐
│ Initialize  │
│ state = {}  │
│ iteration=0 │
└──────┬──────┘
       │
       ▼
 ┌─────────────────────────┐
 │ iteration < max?        │
 │ AND not done?           │
 └──┬───────────────────┬──┘
    │ Yes               │ No
    │                   │
    ▼                   ▼
┌─────────┐        ┌─────────┐
│ Run     │        │ Return  │
│ Agent   │        │ state   │
└────┬────┘        └─────────┘
     │
     ▼
┌─────────────┐
│ Update      │
│ state       │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Check done? │
└──────┬──────┘
       │
       └──(loop back)
```

#### Use Case: Code Generation with Validation

```
┌────────────────────────────────────────────────────────────────────┐
│       CODE GENERATION WITH ITERATIVE VALIDATION                    │
└────────────────────────────────────────────────────────────────────┘

Flow: code_generation_harness(spec, max_iterations=3)

Initialize:
  state = {"code": "", "errors": []}

For iteration in range(0, 3):  # Max 3 attempts

  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 1: Generate code                                       │
  │ code = code_agent.run(spec, prior_code=state["code"])       │
  │ state["code"] = code                                        │
  │                                                             │
  │ Iteration 0: spec = "Write factorial function"             │
  │              code = "def factorial(n): return n * n-1"      │
  │ Iteration 1: spec + feedback about errors                   │
  │              code = "def factorial(n): return n * (n-1)"    │
  │ Iteration 2: spec + updated feedback                        │
  │              code = "def factorial(n): ..."  (corrected)    │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 2: Validate generated code                            │
  │ validation_result = validator.run(code)                     │
  │ state["errors"] = validation_result.get("errors", [])       │
  │                                                             │
  │ Iteration 0: errors = ["SyntaxError: missing parentheses"]  │
  │ Iteration 1: errors = ["LogicError: base case missing"]    │
  │ Iteration 2: errors = []  (valid!)                          │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 3: Check termination condition                        │
  │ if len(state["errors"]) == 0:                               │
  └─────────────────────────────────────────────────────────────┘
                             │
                      ┌──────┴──────┐
                     YES            NO
                      │              │
                      ▼              ▼
            ┌──────────────┐  ┌────────────────────────────┐
            │ SUCCESS      │  │ STEP 4: Provide feedback   │
            │ Return state │  │ spec["feedback"] =         │
            │              │  │   f"Fix errors:            │
            │ state = {    │  │    {state['errors']}"      │
            │   "code":    │  │                            │
            │   "def...",  │  │ Continue to next iteration │
            │   "errors":[]│  └────────────────────────────┘
            │ }            │
            └──────────────┘

After max_iterations exhausted with errors:
  ┌─────────────────────────────────────────────────────────────┐
  │ Raise MaxIterationsExceeded                                 │
  │ "Could not generate valid code in 3 iterations"             │
  └─────────────────────────────────────────────────────────────┘

Iteration Timeline:
┌────────┬───────────────────────┬─────────────────────┬──────────┐
│ Iter   │ Generated Code        │ Validation Errors   │ Action   │
├────────┼───────────────────────┼─────────────────────┼──────────┤
│ 0      │ def factorial(n):     │ ["SyntaxError:      │ Retry    │
│        │   return n * n-1      │  missing parens"]   │          │
├────────┼───────────────────────┼─────────────────────┼──────────┤
│ 1      │ def factorial(n):     │ ["LogicError:       │ Retry    │
│        │   return n * (n-1)    │  base case missing"]│          │
├────────┼───────────────────────┼─────────────────────┼──────────┤
│ 2      │ def factorial(n):     │ []                  │ SUCCESS  │
│        │   if n == 0: return 1 │                     │ Return   │
│        │   return n*(n-1)      │                     │          │
└────────┴───────────────────────┴─────────────────────┴──────────┘

Key Feature: Agent learns from prior mistakes through feedback loop
             Each iteration incorporates validation errors from previous
```

#### Loop Termination Conditions

| Condition | When to Use | Example |
|-----------|-------------|---------|
| **Task Complete Flag** | Agent signals completion | `output["task_complete"] == True` |
| **Validation Pass** | Output passes quality gate | `validator.check(output) == True` |
| **Confidence Threshold** | Agent is confident enough | `output["confidence"] > 0.9` |
| **Max Iterations** | Safety limit | `iteration >= max_iterations` |
| **Timeout** | Time limit | `time.time() - start > 60` |
| **Cost Limit** | Budget exhausted | `total_cost > max_cost` |

#### State Accumulation

**Pattern:** State grows with each iteration, providing history to agent.

```
Iteration 1:
state = {
  "attempts": 1,
  "code": "def foo(): pass",
  "errors": ["Missing docstring"]
}

Iteration 2:
state = {
  "attempts": 2,
  "code": "def foo():\n    \"\"\"Foo function.\"\"\"\n    pass",
  "errors": []  # Fixed
}
```

**Why This Matters:** Agent can learn from prior mistakes, leading to convergence.

---

### State Management: Passing Context Between Steps

**Core Challenge:** How to serialize, persist, and share state across agents?

#### State Schema Design

```
┌────────────────────────────────────────────────────────────────────┐
│                 STATE SCHEMA DESIGN PATTERNS                       │
└────────────────────────────────────────────────────────────────────┘

OPTION 1: Simple Dictionary (Unstructured)
──────────────────────────────────────────

state = {
  "network": {
    "network_ok": true,
    "latency_ms": 50,
    "findings": ["Latency spike on eth0"]
  },
  "config": {
    "config_issues": ["ACL blocked NTP"],
    "recent_changes": [...]
  },
  "timing": {
    "timing_issues": ["Clock drift 15s"],
    "root_cause": "NTP unreachable"
  }
}

Pros:
  • Simple to implement
  • Flexible (no schema enforcement)
  • Easy to serialize (JSON)

Cons:
  ✗ No type safety
  ✗ No validation
  ✗ Typos cause runtime errors


OPTION 2: Structured with Pydantic Model
─────────────────────────────────────────

WorkflowState Schema:
┌─────────────────────────────────────────────────────────────────┐
│ Field           │ Type              │ Required │ Description    │
├─────────────────┼───────────────────┼──────────┼────────────────┤
│ task_id         │ str               │ Yes      │ Unique task ID │
│ current_step    │ int               │ Yes      │ Workflow step  │
│ agent_outputs   │ dict[str, dict]   │ Yes      │ Agent results  │
│ metadata        │ dict              │ Yes      │ Extra info     │
│ created_at      │ str               │ Yes      │ ISO timestamp  │
└─────────────────┴───────────────────┴──────────┴────────────────┘

Configuration:
  extra = "allow"  ← Permits additional fields not in schema
                     (for extensibility without breaking changes)

Example Instance:
┌─────────────────────────────────────────────────────────────────┐
│ WorkflowState(                                                  │
│   task_id="test-failure-001",                                   │
│   current_step=2,                                               │
│   agent_outputs={                                               │
│     "network": {"network_ok": true, ...},                       │
│     "config": {"config_issues": [...], ...}                     │
│   },                                                            │
│   metadata={                                                    │
│     "start_time": "2026-08-20T10:00:00Z",                       │
│     "total_cost": 0.24,                                         │
│     "retry_count": 0                                            │
│   },                                                            │
│   created_at="2026-08-20T10:00:00Z"                             │
│ )                                                               │
└─────────────────────────────────────────────────────────────────┘

Pros:
  ✓ Type safety (catches errors at assignment)
  ✓ Automatic validation
  ✓ IDE autocomplete support
  ✓ Self-documenting schema

Cons:
  • More boilerplate code
  • Schema changes require updates


RECOMMENDATION: Use Pydantic for production harnesses
                Use dict for prototyping/experimentation
```

#### Persistence Options

| Backend | Pros | Cons | Use Case |
|---------|------|------|----------|
| **In-Memory Dict** | Fast, simple | Lost on crash | Short-lived workflows, dev/test |
| **Redis** | Fast, distributed | Requires infrastructure | Production, multi-process |
| **Database (Postgres)** | Durable, queryable | Slower | Long-running, audit requirements |
| **File System** | Simple, auditable | Not distributed | Single-machine, debugging |

#### Example: Redis State Manager

```
┌────────────────────────────────────────────────────────────────────┐
│         REDIS STATE MANAGER: Distributed State Storage             │
└────────────────────────────────────────────────────────────────────┘

Class: RedisStateManager

┌─────────────────────────────────────────────────────────────────┐
│ INITIALIZATION                                                  │
├─────────────────────────────────────────────────────────────────┤
│ __init__(redis_url="redis://localhost:6379")                    │
│   • Connect to Redis server                                     │
│   • self.client = redis.from_url(redis_url)                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD: get(workflow_id, key)                                   │
│ Purpose: Retrieve single value from workflow state             │
├─────────────────────────────────────────────────────────────────┤
│ Steps:                                                          │
│   1. Build Redis key: f"workflow:{workflow_id}:state"           │
│      Example: "workflow:workflow-123:state"                     │
│                                                                 │
│   2. Get field from hash: self.client.hget(state_key, key)      │
│      Example: hget("workflow:workflow-123:state", "network")    │
│                                                                 │
│   3. Deserialize JSON and return                                │
│      return json.loads(data) if data else None                  │
│                                                                 │
│ Example:                                                        │
│   state_mgr.get("workflow-123", "network")                      │
│   → {"network_ok": true, "confidence": 0.85}                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD: set(workflow_id, key, value)                            │
│ Purpose: Store single value in workflow state                  │
├─────────────────────────────────────────────────────────────────┤
│ Steps:                                                          │
│   1. Build Redis key: f"workflow:{workflow_id}:state"           │
│                                                                 │
│   2. Serialize value to JSON                                    │
│      json_value = json.dumps(value)                             │
│                                                                 │
│   3. Store in Redis hash                                        │
│      self.client.hset(state_key, key, json_value)               │
│                                                                 │
│ Example:                                                        │
│   state_mgr.set("workflow-123", "network",                      │
│                 {"network_ok": True})                           │
│   → Stores in Redis: workflow:workflow-123:state.network        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD: get_all(workflow_id)                                    │
│ Purpose: Retrieve entire workflow state                        │
├─────────────────────────────────────────────────────────────────┤
│ Steps:                                                          │
│   1. Build Redis key                                            │
│                                                                 │
│   2. Get all fields from hash                                   │
│      data = self.client.hgetall(state_key)                      │
│      → {b"network": b"{...}", b"config": b"{...}"}              │
│                                                                 │
│   3. Decode keys and deserialize JSON values                    │
│      return {k.decode(): json.loads(v)                          │
│              for k, v in data.items()}                          │
│                                                                 │
│ Example:                                                        │
│   state_mgr.get_all("workflow-123")                             │
│   → {                                                           │
│        "network": {"network_ok": true, ...},                    │
│        "config": {"config_issues": [...], ...}                  │
│      }                                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD: delete(workflow_id)                                     │
│ Purpose: Remove entire workflow state (cleanup)                │
├─────────────────────────────────────────────────────────────────┤
│ Steps:                                                          │
│   1. Build Redis key                                            │
│   2. Delete entire hash: self.client.delete(state_key)          │
│                                                                 │
│ Example:                                                        │
│   state_mgr.delete("workflow-123")                              │
│   → Removes all state for workflow-123                          │
└─────────────────────────────────────────────────────────────────┘

Usage Example:
┌─────────────────────────────────────────────────────────────────┐
│ # Initialize manager                                            │
│ state_mgr = RedisStateManager()                                 │
│                                                                 │
│ # Store network agent output                                    │
│ state_mgr.set("workflow-123", "network",                        │
│               {"network_ok": True})                             │
│                                                                 │
│ # Retrieve network agent output                                 │
│ network_state = state_mgr.get("workflow-123", "network")        │
│ → {"network_ok": True}                                          │
└─────────────────────────────────────────────────────────────────┘

Redis Data Structure:
  Key: "workflow:workflow-123:state"
  Type: Hash
  Fields:
    "network" → '{"network_ok": true, "confidence": 0.85}'
    "config"  → '{"config_issues": [...], "confidence": 0.92}'
    "timing"  → '{"timing_issues": [...], "confidence": 0.78}'

Benefits:
  • Distributed: Multiple processes can share state
  • Fast: In-memory storage with persistence
  • Scalable: Handles thousands of concurrent workflows
  • TTL support: Auto-expire old workflows
```

#### State Namespacing

**Problem:** Avoid key collisions between agents.

**Visual: State Namespacing Patterns**

```
┌──────────────────────────────────────────────────────────────────┐
│  State Namespacing: Avoiding Key Collisions                     │
└──────────────────────────────────────────────────────────────────┘

❌ BAD: Global Keys (Collision Risk)
────────────────────────────────
state["result"] = "..."  ← Which agent's result? Ambiguous!

Problems:
  • Key collisions between agents
  • No ownership tracking
  • Hard to debug conflicts


✓ GOOD: Namespaced Keys
────────────────────────────────
state["agent_network.result"] = "..."
state["agent_config.result"] = "..."

Benefits:
  • Clear agent ownership
  • No collisions
  • Easy to grep/filter


✓✓ BETTER: Nested Structure
────────────────────────────────
state = {
  "network": {
    "result": "...",
    "confidence": 0.9
  },
  "config": {
    "result": "...",
    "confidence": 0.85
  }
}

Benefits:
  • Hierarchical organization
  • Easy to access: state["network"]["result"]
  • Type-safe with schema validation
  • Natural grouping of related fields


Recommendation: Use nested structure for multi-agent state
```

---

### Error Handling: Retry, Fallback, Escalation

#### Error Taxonomy

```
┌──────────────────────────────────────────────────────────────────┐
│                      ERROR CLASSIFICATION                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TRANSIENT ERRORS (Retry):                                      │
│  • API rate limit (429)                                         │
│  • Timeout (network glitch)                                     │
│  • Temporary service outage (503)                               │
│  → Strategy: Exponential backoff, max 3 retries                 │
│                                                                  │
│  SEMANTIC ERRORS (Reprompt):                                    │
│  • Invalid JSON output                                          │
│  • Missing required fields                                      │
│  • Hallucinated data                                            │
│  → Strategy: Add validation constraints, retry with feedback    │
│                                                                  │
│  LOGIC ERRORS (Fallback):                                       │
│  • Agent produces incorrect diagnosis                           │
│  • Low confidence score                                         │
│  → Strategy: Route to alternate agent or model                  │
│                                                                  │
│  FATAL ERRORS (Abort):                                          │
│  • Authentication failure                                       │
│  • Quota exceeded                                               │
│  • Invalid input data (cannot be fixed)                         │
│  → Strategy: Abort workflow, alert human                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

#### Retry with Exponential Backoff

```
┌────────────────────────────────────────────────────────────────────┐
│       RETRY WITH EXPONENTIAL BACKOFF: Smart Error Recovery        │
└────────────────────────────────────────────────────────────────────┘

Function: retry_with_backoff(func, max_retries=3,
                              base_delay=1.0, max_delay=60.0)

Purpose: Retry function with increasing delays between attempts

For attempt in range(0, max_retries):

  ┌─────────────────────────────────────────────────────────────┐
  │ Try: Execute function                                       │
  │ return func()                                               │
  └─────────────────────────────────────────────────────────────┘
       │
       ▼
    Success?
       │
   ┌───┴───┐
  YES     NO
   │       │
   ▼       ▼
Return  Exception caught
result  (TimeoutError, RateLimitError)
           │
           ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Check: Is this the last attempt?                            │
  │ if attempt == max_retries - 1:                              │
  └─────────────────────────────────────────────────────────────┘
           │
       ┌───┴───┐
      YES     NO
       │       │
       ▼       ▼
   Re-raise  Calculate backoff delay
   error     │
             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 1: Calculate exponential backoff                       │
  │ delay = min(base_delay * (2 ** attempt), max_delay)         │
  │                                                             │
  │ Examples:                                                   │
  │   attempt=0: delay = 1.0 * 2^0 = 1.0s                       │
  │   attempt=1: delay = 1.0 * 2^1 = 2.0s                       │
  │   attempt=2: delay = 1.0 * 2^2 = 4.0s                       │
  │   attempt=3: delay = 1.0 * 2^3 = 8.0s                       │
  │   (capped at max_delay=60.0)                                │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 2: Add jitter (avoid thundering herd)                  │
  │ jitter = random.uniform(0, 0.1 * delay)                     │
  │ total_delay = delay + jitter                                │
  │                                                             │
  │ Example (attempt=1, delay=2.0s):                            │
  │   jitter = random in [0, 0.2]  (say 0.15)                   │
  │   total_delay = 2.0 + 0.15 = 2.15s                          │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 3: Log warning and sleep                               │
  │ logger.warning(f"Attempt {attempt+1} failed: {e}.           │
  │                 Retrying in {total_delay:.2f}s")            │
  │ time.sleep(total_delay)                                     │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             └──▶ Continue to next iteration

After max_retries exhausted:
  ┌─────────────────────────────────────────────────────────────┐
  │ Raise MaxRetriesExceeded                                    │
  │ "Failed after 3 attempts"                                   │
  └─────────────────────────────────────────────────────────────┘

Retry Timeline Example:
┌────────┬──────────┬────────────┬─────────────┬──────────────┐
│ Attempt│ Delay    │ Total Time │ Outcome     │ Action       │
├────────┼──────────┼────────────┼─────────────┼──────────────┤
│ 0      │ 0s       │ 0s         │ Timeout     │ Wait 1.0s    │
│ 1      │ 1.0s     │ 1.0s       │ Timeout     │ Wait 2.0s    │
│ 2      │ 2.0s     │ 3.0s       │ Success     │ Return       │
└────────┴──────────┴────────────┴─────────────┴──────────────┘

Total elapsed: 3.0s (without retries: would have failed at 0s)

Usage Example:
┌─────────────────────────────────────────────────────────────────┐
│ output = retry_with_backoff(lambda: agent.run(task))            │
│                                                                 │
│ Wraps agent.run(task) in retry logic:                           │
│   • Retries transient failures (timeout, rate limit)            │
│   • Uses exponential backoff (1s, 2s, 4s)                       │
│   • Adds jitter to prevent synchronized retries                 │
│   • Logs each retry attempt for observability                   │
└─────────────────────────────────────────────────────────────────┘

Key Feature: Jitter prevents thundering herd problem
             (multiple clients retrying at exact same time)
```

#### Fallback to Alternate Agent

```
┌────────────────────────────────────────────────────────────────────┐
│       FALLBACK PATTERN: Tiered Agent Strategy                      │
└────────────────────────────────────────────────────────────────────┘

Flow: fallback_harness(task)

┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: Try Primary Agent (GPT-4)                              │
│ Expensive but accurate                                         │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Try:                                                        │
  │   output = primary_agent.run(task)                          │
  │   (GPT-4, high accuracy, cost: $0.12)                       │
  └────────┬────────────────────────────────────────────────────┘
           │
       Success?
           │
       ┌───┴───┐
      YES     NO
       │       │
       ▼       ▼
   Got     Exception
   output  caught
       │       │
       ▼       └──▶ Log warning and fallback
  ┌─────────────────────────────────────────────────────────────┐
  │ Check confidence threshold                                  │
  │ Is output["confidence"] > 0.8?                              │
  └─────────────────────────────────────────────────────────────┘
           │
       ┌───┴───┐
      YES     NO
       │       │
       ▼       │
   Return      │
   output      │
   (success)   │
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│ TIER 2: Fallback to Secondary Agent (GPT-3.5)                  │
│ Cheaper but less accurate                                      │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Try:                                                        │
  │   output = secondary_agent.run(task)                        │
  │   (GPT-3.5, lower accuracy, cost: $0.02)                    │
  └────────┬────────────────────────────────────────────────────┘
           │
       Success?
           │
       ┌───┴───┐
      YES     NO
       │       │
       ▼       ▼
   Got     Exception
   output  caught
       │       │
       ▼       └──▶ Log warning and escalate
  ┌─────────────────────────────────────────────────────────────┐
  │ Check lower confidence threshold                            │
  │ Is output["confidence"] > 0.6?                              │
  │ (Accept lower confidence for cheaper model)                 │
  └─────────────────────────────────────────────────────────────┘
           │
       ┌───┴───┐
      YES     NO
       │       │
       ▼       │
   Return      │
   output      │
   (degraded)  │
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│ TIER 3: Human Escalation                                       │
│ Last resort when all agents fail                               │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ return escalate_to_human(task)                              │
  │   • Add to manual review queue                              │
  │   • Alert on-call engineer                                  │
  │   • Return placeholder response                             │
  └─────────────────────────────────────────────────────────────┘

Decision Tree:
                    ┌──────────────┐
                    │ Start        │
                    └──────┬───────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ Primary (GPT-4)        │
              │ confidence > 0.8?      │
              └────────┬───────────────┘
                       │
            ┌──────────┴──────────┐
           YES                   NO
            │                     │
            ▼                     ▼
      ┌─────────┐      ┌─────────────────────┐
      │ Return  │      │ Secondary (GPT-3.5) │
      │ primary │      │ confidence > 0.6?   │
      │ output  │      └─────────┬───────────┘
      └─────────┘                │
                      ┌──────────┴──────────┐
                     YES                   NO
                      │                     │
                      ▼                     ▼
                ┌──────────┐        ┌─────────────┐
                │ Return   │        │ Escalate to │
                │secondary │        │ human       │
                │ output   │        └─────────────┘
                └──────────┘

Execution Scenarios:
┌────────────┬──────────────┬──────────────┬──────────────┐
│ Scenario   │ Primary      │ Secondary    │ Final Action │
├────────────┼──────────────┼──────────────┼──────────────┤
│ A          │ Success      │ Not called   │ Return P     │
│            │ conf=0.92    │              │              │
├────────────┼──────────────┼──────────────┼──────────────┤
│ B          │ Success      │ Success      │ Return S     │
│            │ conf=0.65    │ conf=0.72    │              │
├────────────┼──────────────┼──────────────┼──────────────┤
│ C          │ Timeout      │ Success      │ Return S     │
│            │              │ conf=0.68    │              │
├────────────┼──────────────┼──────────────┼──────────────┤
│ D          │ Success      │ Success      │ Escalate     │
│            │ conf=0.50    │ conf=0.45    │              │
└────────────┴──────────────┴──────────────┴──────────────┘

Key Benefit: Graceful degradation from expensive/accurate
             to cheap/good-enough, with human backstop
```

#### Human Escalation

```
┌────────────────────────────────────────────────────────────────────┐
│           HUMAN ESCALATION: Queue for Manual Review                │
└────────────────────────────────────────────────────────────────────┘

Class: EscalationQueue

┌─────────────────────────────────────────────────────────────────┐
│ INITIALIZATION                                                  │
├─────────────────────────────────────────────────────────────────┤
│ __init__()                                                      │
│   self.queue = []  (empty list to hold escalated tasks)         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD: add(task, reason)                                       │
│ Purpose: Add task to escalation queue and alert engineer       │
├─────────────────────────────────────────────────────────────────┤
│ Steps:                                                          │
│   1. Create escalation entry                                    │
│      entry = {                                                  │
│        "task": task,                                            │
│        "reason": reason,                                        │
│        "timestamp": time.time()                                 │
│      }                                                          │
│                                                                 │
│   2. Append to queue                                            │
│      self.queue.append(entry)                                   │
│                                                                 │
│   3. Alert on-call engineer                                     │
│      send_alert(f"Task escalated: {reason}")                    │
│      ↑ PagerDuty, Slack, email, etc.                            │
│                                                                 │
│ Example:                                                        │
│   escalation_queue.add(                                         │
│     task={"id": "test-failure-001", ...},                       │
│     reason="All agents failed to diagnose"                      │
│   )                                                             │
│   → Queue now contains 1 item                                   │
│   → Alert sent to on-call engineer                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD: get_next()                                              │
│ Purpose: Retrieve next task for human review (FIFO)            │
├─────────────────────────────────────────────────────────────────┤
│ Steps:                                                          │
│   1. Check if queue is non-empty                                │
│   2. If queue has items: pop(0) → first item                    │
│   3. If queue empty: return None                                │
│                                                                 │
│ Example:                                                        │
│   next_task = escalation_queue.get_next()                       │
│   → {"task": {...}, "reason": "...", "timestamp": 1692534003}   │
│                                                                 │
│   (Queue is now empty if that was the only item)                │
└─────────────────────────────────────────────────────────────────┘

Function: escalate_to_human(task)
┌─────────────────────────────────────────────────────────────────┐
│ Steps:                                                          │
│   1. Add task to escalation queue                               │
│      escalation_queue.add(task, "All agents failed to diagnose")│
│                                                                 │
│   2. Return placeholder response                                │
│      return {                                                   │
│        "status": "escalated",                                   │
│        "message": "Task queued for human review"                │
│      }                                                          │
│                                                                 │
│ Calling workflow receives response indicating escalation        │
└─────────────────────────────────────────────────────────────────┘

Escalation Queue State Over Time:
┌─────────────────────────────────────────────────────────────────┐
│ T0: Queue empty []                                              │
│                                                                 │
│ T1: Agent fails, escalate task-001                              │
│     Queue: [{"task": task-001, "reason": "...", "ts": T1}]      │
│     Alert: "Task escalated: All agents failed"                  │
│                                                                 │
│ T2: Agent fails, escalate task-002                              │
│     Queue: [task-001, task-002]                                 │
│     Alert: "Task escalated: All agents failed"                  │
│                                                                 │
│ T3: Engineer calls get_next()                                   │
│     Returns: task-001                                           │
│     Queue: [task-002]                                           │
│                                                                 │
│ T4: Engineer resolves task-001 manually                         │
│     Queue: [task-002] (unchanged)                               │
└─────────────────────────────────────────────────────────────────┘

Integration with Harness:
┌─────────────────────────────────────────────────────────────────┐
│ try:                                                            │
│   output = primary_agent.run(task)                              │
│ except Exception:                                               │
│   try:                                                          │
│     output = secondary_agent.run(task)                          │
│   except Exception:                                             │
│     return escalate_to_human(task)  ← Last resort               │
└─────────────────────────────────────────────────────────────────┘

Key Benefits:
  • Graceful failure handling (no silent drops)
  • Human-in-the-loop for complex edge cases
  • Alerting ensures timely review
  • FIFO queue ensures fair processing order
```

---

### Cost Control: Budget Limits, Early Termination

#### Cost Tracking

```
┌────────────────────────────────────────────────────────────────────┐
│              COST TRACKER: Monitor and Enforce Budget              │
└────────────────────────────────────────────────────────────────────┘

Class: CostTracker

┌─────────────────────────────────────────────────────────────────┐
│ INITIALIZATION                                                  │
├─────────────────────────────────────────────────────────────────┤
│ __init__(max_cost_usd=10.0)                                     │
│   self.max_cost = 10.0                                          │
│   self.total_cost = 0.0                                         │
│   self.cost_per_agent = {}  (tracks spending per agent)         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD: add_cost(agent_name, cost_usd)                          │
│ Purpose: Record agent cost and enforce budget limit            │
├─────────────────────────────────────────────────────────────────┤
│ Steps:                                                          │
│   1. Update total cost                                          │
│      self.total_cost += cost_usd                                │
│                                                                 │
│   2. Update per-agent cost                                      │
│      current = self.cost_per_agent.get(agent_name, 0)           │
│      self.cost_per_agent[agent_name] = current + cost_usd       │
│                                                                 │
│   3. Check budget limit                                         │
│      if self.total_cost > self.max_cost:                        │
│        raise BudgetExceededError(...)                           │
│                                                                 │
│ Example:                                                        │
│   cost_tracker.add_cost("network_agent", 0.12)                  │
│   → total_cost = 0.12                                           │
│   → cost_per_agent = {"network_agent": 0.12}                    │
│   → Budget OK (0.12 < 10.0)                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD: get_remaining_budget()                                  │
│ Purpose: Calculate how much budget is left                     │
├─────────────────────────────────────────────────────────────────┤
│ Calculation:                                                    │
│   return self.max_cost - self.total_cost                        │
│                                                                 │
│ Example:                                                        │
│   max_cost = 1.00                                               │
│   total_cost = 0.36                                             │
│   remaining = 1.00 - 0.36 = 0.64                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD: get_cost_breakdown()                                    │
│ Purpose: Return detailed cost report                           │
├─────────────────────────────────────────────────────────────────┤
│ Returns:                                                        │
│   {                                                             │
│     "total": 0.36,                                              │
│     "per_agent": {                                              │
│       "network_agent": 0.12,                                    │
│       "config_agent": 0.12,                                     │
│       "timing_agent": 0.12                                      │
│     },                                                          │
│     "remaining": 0.64                                           │
│   }                                                             │
└─────────────────────────────────────────────────────────────────┘

Usage in Workflow:
┌─────────────────────────────────────────────────────────────────┐
│ # Initialize tracker with $1.00 budget                          │
│ cost_tracker = CostTracker(max_cost_usd=1.00)                   │
│                                                                 │
│ # Run agent                                                     │
│ output = agent.run(task)                                        │
│                                                                 │
│ # Calculate cost based on tokens used                           │
│ cost = calculate_cost(output)                                   │
│ # Example: 3000 input + 500 output tokens @ GPT-4 rates         │
│ # cost = (3000 * $0.03/1K) + (500 * $0.06/1K) = $0.12           │
│                                                                 │
│ # Track cost                                                    │
│ cost_tracker.add_cost(agent.name, cost)                         │
│ → If total exceeds $1.00, BudgetExceededError raised            │
└─────────────────────────────────────────────────────────────────┘

Cost Evolution Example:
┌────────────┬──────────────┬──────────────┬─────────────────┐
│ Agent      │ Cost         │ Total Cost   │ Status          │
├────────────┼──────────────┼──────────────┼─────────────────┤
│ Network    │ +$0.12       │ $0.12        │ ✓ OK (< $1.00)  │
│ Config     │ +$0.12       │ $0.24        │ ✓ OK            │
│ Timing     │ +$0.12       │ $0.36        │ ✓ OK            │
│ Synthesis  │ +$0.21       │ $0.57        │ ✓ OK            │
│ (Retry)    │ +$0.12       │ $0.69        │ ✓ OK            │
│ (Extra)    │ +$0.50       │ $1.19        │ ✗ ABORT!        │
└────────────┴──────────────┴──────────────┴─────────────────┘

Budget Exceeded Flow:
  total_cost ($1.19) > max_cost ($1.00)
    ↓
  Raise BudgetExceededError
    ↓
  "Workflow cost $1.19 exceeds budget $1.00"
    ↓
  Workflow aborted, partial results returned

Key Benefits:
  • Prevents runaway costs from infinite loops
  • Provides cost visibility per agent
  • Enforces hard budget limits
  • Useful for cost analysis and optimization
```

#### Early Termination on High Confidence

```
┌────────────────────────────────────────────────────────────────────┐
│     EARLY TERMINATION: Stop When Confidence Threshold Met          │
└────────────────────────────────────────────────────────────────────┘

Flow: cost_optimized_harness(task, confidence_threshold=0.9)

Initialize:
  cost_tracker = CostTracker(max_cost_usd=1.00)
  confidence_threshold = 0.9

For each agent in [network_agent, config_agent, timing_agent]:

  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 1: Run agent                                           │
  │ output = agent.run(task)                                    │
  │                                                             │
  │ Example:                                                    │
  │   network_agent → {"diagnosis": "...", "confidence": 0.97}  │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 2: Calculate and track cost                           │
  │ cost = calculate_cost(output)                               │
  │ cost_tracker.add_cost(agent.name, cost)                     │
  │                                                             │
  │ Example:                                                    │
  │   cost = $0.12                                              │
  │   total_cost now = $0.12                                    │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 3: Check confidence threshold                         │
  │ Is output.get("confidence", 0) > confidence_threshold?      │
  │ Is 0.97 > 0.9?                                              │
  └─────────────────────────────────────────────────────────────┘
                             │
                      ┌──────┴──────┐
                     YES            NO
                      │              │
                      ▼              ▼
         ┌──────────────────────┐  ┌────────────────────────┐
         │ EARLY TERMINATION    │  │ Continue to next agent │
         │                      │  │                        │
         │ Log:                 │  │ Run config_agent next  │
         │ "Early termination:  │  └────────────────────────┘
         │  network_agent       │
         │  achieved 0.97       │
         │  confidence"         │
         │                      │
         │ RETURN output        │
         │                      │
         │ Skip config_agent    │
         │ Skip timing_agent    │
         │                      │
         │ Cost saved:          │
         │ 2 agents × $0.12     │
         │ = $0.24 saved        │
         └──────────────────────┘

After all agents (if no early termination):
  ┌─────────────────────────────────────────────────────────────┐
  │ No agent achieved high confidence                           │
  │ Return last output (best effort)                            │
  │ return output                                               │
  └─────────────────────────────────────────────────────────────┘

Example Scenarios:
┌────────────┬─────────────┬──────────────┬──────────────────┐
│ Scenario   │ Network     │ Config       │ Timing           │
│            │ Confidence  │ Confidence   │ Confidence       │
├────────────┼─────────────┼──────────────┼──────────────────┤
│ A: Early   │ 0.97 ✓      │ Not called   │ Not called       │
│ success    │ RETURN      │              │                  │
│            │ Cost: $0.12 │              │                  │
├────────────┼─────────────┼──────────────┼──────────────────┤
│ B: Mid     │ 0.75        │ 0.94 ✓       │ Not called       │
│ success    │ Continue    │ RETURN       │                  │
│            │ Cost:       │              │                  │
│            │ $0.12+$0.12 │              │                  │
│            │ = $0.24     │              │                  │
├────────────┼─────────────┼──────────────┼──────────────────┤
│ C: All run │ 0.65        │ 0.78         │ 0.82             │
│            │ Continue    │ Continue     │ RETURN (last)    │
│            │ Cost: $0.12 │ + $0.12      │ + $0.12 = $0.36  │
└────────────┴─────────────┴──────────────┴──────────────────┘

Cost Savings Analysis:
┌──────────────────────────┬──────────────┬─────────────────┐
│ Strategy                 │ Avg Agents   │ Avg Cost        │
│                          │ Run          │                 │
├──────────────────────────┼──────────────┼─────────────────┤
│ Always run all 3 agents  │ 3.0          │ $0.36           │
├──────────────────────────┼──────────────┼─────────────────┤
│ Early term (40% at net,  │ 1.8          │ $0.22 (39%      │
│ 30% at config)           │              │ savings)        │
└──────────────────────────┴──────────────┴─────────────────┘

At 1,000 workflows/day: $140/day savings = $4,200/month

Key Benefit: Minimize cost while maintaining high accuracy
             by stopping as soon as confident diagnosis found
```

---

## Production Considerations

### ROI Analysis: Savings from Orchestration

**Question:** Does the added cost of harness orchestration justify the benefits?

#### ROI Calculation Framework

```
┌──────────────────────────────────────────────────────────────────┐
│                         ROI CALCULATION                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  COSTS:                                                          │
│  • LLM API costs (increased due to multiple agents)             │
│  • Engineering time to build harness                            │
│  • Infrastructure costs (orchestration platform)                │
│  • Operational overhead (monitoring, debugging)                 │
│                                                                  │
│  BENEFITS:                                                       │
│  • Accuracy improvement → fewer false diagnoses                 │
│  • Time savings → faster incident resolution                    │
│  • Engineer productivity → less manual debugging                │
│  • Customer satisfaction → fewer escalations                    │
│                                                                  │
│  ROI = (Benefits - Costs) / Costs                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

#### Example: Atiya ROI

**Scenario:** 100 test failures/day, each requiring diagnosis.

**Before Harness (Manual Debugging):**
- Average time per diagnosis: 30 minutes
- Engineer hourly rate: $100/hour
- Daily cost: 100 failures × 0.5 hours × $100 = **$5,000/day**
- Monthly cost: **$150,000**

**After Harness (Atiya):**
- Automated diagnosis: 91% accuracy
- Manual debugging needed: 9 failures × 0.5 hours × $100 = $450/day
- LLM costs: 100 workflows × $0.57 = $57/day
- Daily cost: $450 + $57 = **$507/day**
- Monthly cost: **$15,210**

**Savings:** $150,000 - $15,210 = **$134,790/month**

**ROI:** ($134,790 - engineering_cost) / engineering_cost

Even if harness took 2 engineer-months to build (cost: $40,000), ROI is:
- ROI = ($134,790 - $40,000) / $40,000 = **237% in first month**
- Payback period: **9 days**

#### When Harness is NOT Worth It

| Scenario | Why ROI is Negative |
|----------|---------------------|
| **Low volume tasks** | < 10 tasks/month → LLM cost exceeds manual labor |
| **Simple tasks** | Single prompt suffices → orchestration overhead not needed |
| **High variability** | Each task is unique → no reusable patterns to harness |
| **Intolerant to errors** | Safety-critical → 91% accuracy insufficient, need 99.9% |

---

### Monitoring Multi-Step Workflows

#### Key Metrics

```
┌──────────────────────────────────────────────────────────────────┐
│                   HARNESS OBSERVABILITY METRICS                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WORKFLOW-LEVEL:                                                 │
│  • Completion rate: % workflows that succeed                    │
│  • Average latency: End-to-end time                             │
│  • Cost per workflow: Total LLM spend                           │
│  • Error rate: % workflows that fail                            │
│                                                                  │
│  AGENT-LEVEL:                                                    │
│  • Invocation count: How often each agent is called            │
│  • Success rate: % successful agent calls                       │
│  • Average latency: Time per agent call                         │
│  • Cost per agent: LLM spend per agent                          │
│                                                                  │
│  STATE-LEVEL:                                                    │
│  • State size: Bytes of state per workflow                      │
│  • State growth: How state size changes over steps             │
│  • Validation failures: % state updates rejected               │
│                                                                  │
│  QUALITY-LEVEL:                                                  │
│  • Accuracy: % correct diagnoses (requires ground truth)        │
│  • Confidence: Average confidence scores                        │
│  • Human escalation rate: % workflows requiring manual review   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

#### Monitoring Dashboard (Example)

```
┌─────────────────────────────────────────────────────────────────┐
│                 ATIYA HARNESS DASHBOARD                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Today (2026-08-20):                                            │
│  ┌────────────────┬────────────────┬────────────────┐          │
│  │ Workflows      │ Success Rate   │ Avg Latency    │          │
│  ├────────────────┼────────────────┼────────────────┤          │
│  │ 342            │ 91.2%          │ 12.3s          │          │
│  └────────────────┴────────────────┴────────────────┘          │
│                                                                 │
│  Per-Agent Performance:                                         │
│  ┌──────────┬───────┬─────────┬─────────┬─────────┐           │
│  │ Agent    │ Calls │ Success │ Latency │ Cost    │           │
│  ├──────────┼───────┼─────────┼─────────┼─────────┤           │
│  │ Network  │ 342   │ 98.5%   │ 3.2s    │ $41.04  │           │
│  │ Config   │ 342   │ 97.1%   │ 3.8s    │ $41.04  │           │
│  │ Timing   │ 342   │ 96.8%   │ 4.1s    │ $41.04  │           │
│  │ Synthesis│ 312   │ 99.0%   │ 2.1s    │ $65.52  │           │
│  └──────────┴───────┴─────────┴─────────┴─────────┘           │
│                                                                 │
│  Error Breakdown:                                               │
│  • Timeout: 12 (3.5%)                                          │
│  • Validation: 8 (2.3%)                                        │
│  • LLM Error: 5 (1.5%)                                         │
│  • Other: 5 (1.5%)                                             │
│                                                                 │
│  Total Cost Today: $188.64                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Alerting Rules

```
┌────────────────────────────────────────────────────────────────────┐
│         ALERTING RULES: Prometheus-Style Alert Definitions         │
└────────────────────────────────────────────────────────────────────┘

Alert Configuration Schema:
┌─────────────────────────────────────────────────────────────────┐
│ Alert 1: HighWorkflowFailureRate                                │
├─────────────────────────────────────────────────────────────────┤
│ Name:      "HighWorkflowFailureRate"                            │
│ Condition: workflow_error_rate > 0.10                           │
│            (Error rate exceeds 10%)                             │
│ Duration:  5 minutes                                            │
│            (Sustained for 5m before firing)                     │
│ Severity:  warning                                              │
│ Message:   "Workflow error rate exceeded 10% for 5 minutes"     │
│                                                                 │
│ Trigger Example:                                                │
│   T0: error_rate = 0.08  → No alert                             │
│   T5: error_rate = 0.12  → Alert pending (start timer)          │
│   T10: error_rate = 0.13 → Alert FIRES (sustained 5m)           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Alert 2: AgentLatencySpike                                      │
├─────────────────────────────────────────────────────────────────┤
│ Name:      "AgentLatencySpike"                                  │
│ Condition: agent_latency_p95 > 15s                              │
│            (95th percentile latency exceeds 15 seconds)         │
│ Duration:  5 minutes                                            │
│ Severity:  warning                                              │
│ Message:   "Agent P95 latency exceeded 15s"                     │
│                                                                 │
│ Trigger Example:                                                │
│   Normal: P95 latency = 3.2s → No alert                         │
│   Spike:  P95 latency = 18.5s for 5m → Alert FIRES              │
│                                                                 │
│ Use Case: Detect LLM API slowdowns or network issues            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Alert 3: BudgetExceeded                                         │
├─────────────────────────────────────────────────────────────────┤
│ Name:      "BudgetExceeded"                                     │
│ Condition: daily_cost > $500                                    │
│            (Total LLM spend for day exceeds budget)             │
│ Duration:  1 minute                                             │
│            (Fast response - costs escalate quickly)             │
│ Severity:  critical                                             │
│            (Requires immediate attention)                       │
│ Message:   "Daily LLM cost exceeded $500"                       │
│                                                                 │
│ Trigger Example:                                                │
│   9 AM:  daily_cost = $200  → No alert                          │
│   2 PM:  daily_cost = $520  → Alert FIRES (critical)            │
│                                                                 │
│ Actions:                                                        │
│   • Page on-call engineer                                       │
│   • Investigate runaway costs                                   │
│   • Consider disabling harness temporarily                      │
└─────────────────────────────────────────────────────────────────┘

Alert Summary Table:
┌──────────────────────────┬─────────────┬──────────┬──────────┐
│ Alert Name               │ Condition   │ Duration │ Severity │
├──────────────────────────┼─────────────┼──────────┼──────────┤
│ HighWorkflowFailureRate  │ Error > 10% │ 5m       │ warning  │
│ AgentLatencySpike        │ P95 > 15s   │ 5m       │ warning  │
│ BudgetExceeded           │ Cost > $500 │ 1m       │ critical │
└──────────────────────────┴─────────────┴──────────┴──────────┘

Alert Lifecycle:
┌─────────────────────────────────────────────────────────────────┐
│ 1. Condition Met                                                │
│    workflow_error_rate = 0.12 (> 0.10 threshold)                │
│    ↓                                                            │
│ 2. Alert Pending                                                │
│    Start duration timer (5 minutes)                             │
│    ↓                                                            │
│ 3. Condition Sustained                                          │
│    error_rate remains > 0.10 for full 5 minutes                 │
│    ↓                                                            │
│ 4. Alert Fires                                                  │
│    Send notification to on-call engineer                        │
│    ↓                                                            │
│ 5. Resolution                                                   │
│    error_rate drops below 0.10                                  │
│    ↓                                                            │
│ 6. Alert Clears                                                 │
│    Notification sent: "Alert resolved"                          │
└─────────────────────────────────────────────────────────────────┘

Integration:
  • Prometheus: Scrape metrics, evaluate rules
  • Alertmanager: Route alerts, deduplicate
  • PagerDuty/Slack: Notify engineers
```

---

### Observability Patterns

#### 1. Distributed Tracing

**Tool:** OpenTelemetry + Jaeger

```
┌────────────────────────────────────────────────────────────────────┐
│      OPENTELEMETRY + JAEGER: Distributed Tracing Setup             │
└────────────────────────────────────────────────────────────────────┘

PART 1: Setup and Configuration
────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Initialize Tracer Provider                             │
│ trace.set_tracer_provider(TracerProvider())                     │
│ → Creates global tracing infrastructure                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Configure Jaeger Exporter                              │
│ jaeger_exporter = JaegerExporter(                               │
│   agent_host_name="localhost",                                  │
│   agent_port=6831                                               │
│ )                                                               │
│ → Connects to Jaeger agent for trace collection                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Attach Span Processor                                  │
│ trace.get_tracer_provider().add_span_processor(                 │
│   BatchSpanProcessor(jaeger_exporter)                           │
│ )                                                               │
│ → Batches spans before sending to Jaeger (performance)          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Get Tracer Instance                                    │
│ tracer = trace.get_tracer(__name__)                             │
│ → Creates tracer for current module                             │
└─────────────────────────────────────────────────────────────────┘

PART 2: Instrument Harness
───────────────────────────

Function: traced_harness(task)

┌─────────────────────────────────────────────────────────────────┐
│ ROOT SPAN: atiya_workflow                                       │
│ with tracer.start_as_current_span("atiya_workflow") as span:    │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ Set root span attributes                                        │
│ span.set_attribute("task.id", task["id"])                       │
│   Example: "test-failure-001"                                   │
│ span.set_attribute("task.type", task["type"])                   │
│   Example: "network_test_failure"                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ CHILD SPAN 1:   │ │ CHILD SPAN 2:   │ │ CHILD SPAN 3:   │
│ network_agent   │ │ config_agent    │ │ timing_agent    │
└─────────────────┘ └─────────────────┘ └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CHILD SPAN: network_agent                                       │
│ with tracer.start_as_current_span("network_agent") as          │
│      agent_span:                                                │
│                                                                 │
│   Set agent span attributes                                    │
│   agent_span.set_attribute("agent.model", "gpt-4")              │
│                                                                 │
│   Execute agent                                                 │
│   network_output = network_agent.run(task)                      │
│                                                                 │
│   Set result attributes                                        │
│   agent_span.set_attribute("agent.confidence",                  │
│                             network_output["confidence"])       │
│   Example: 0.85                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CHILD SPAN: config_agent                                        │
│ with tracer.start_as_current_span("config_agent"):              │
│   config_output = config_agent.run(task)                        │
│   (Similar attribute setting as network_agent)                  │
└─────────────────────────────────────────────────────────────────┘

Return final_output (when all spans complete)

Span Hierarchy in Jaeger:
┌─────────────────────────────────────────────────────────────────┐
│ atiya_workflow (root)                                           │
│ ├── Attributes:                                                 │
│ │   • task.id: "test-failure-001"                               │
│ │   • task.type: "network_test_failure"                         │
│ │                                                               │
│ ├── network_agent (child span)                                  │
│ │   ├── Attributes:                                             │
│ │   │   • agent.model: "gpt-4"                                  │
│ │   │   • agent.confidence: 0.85                                │
│ │   └── Duration: 3.2s                                          │
│ │                                                               │
│ ├── config_agent (child span)                                   │
│ │   ├── Attributes:                                             │
│ │   │   • agent.model: "gpt-4"                                  │
│ │   │   • agent.confidence: 0.92                                │
│ │   └── Duration: 3.8s                                          │
│ │                                                               │
│ └── timing_agent (child span)                                   │
│     └── Duration: 4.1s                                          │
│                                                                 │
│ Total Duration: 11.1s                                           │
└─────────────────────────────────────────────────────────────────┘

Data Flow:
  Application → OpenTelemetry SDK → Batch Processor
      → Jaeger Agent (port 6831) → Jaeger Collector
      → Jaeger Storage → Jaeger UI (visualization)

Key Benefits:
  • End-to-end visibility of workflow execution
  • Performance bottleneck identification
  • Error propagation tracking
  • Service dependency mapping
```

**Result:** Visualize full workflow execution in Jaeger UI:

```
Trace: atiya_workflow (12.3s)
├─ network_agent (3.2s)
│  ├─ context_retrieval (0.5s)
│  ├─ llm_call (2.5s)
│  └─ validation (0.2s)
├─ config_agent (3.8s)
│  ├─ context_retrieval (0.6s)
│  ├─ llm_call (2.9s)
│  └─ validation (0.3s)
├─ timing_agent (4.1s)
└─ synthesis_agent (2.1s)
```

#### 2. Structured Logging

```
┌────────────────────────────────────────────────────────────────────┐
│          STRUCTURED LOGGING: Machine-Parseable JSON Logs           │
└────────────────────────────────────────────────────────────────────┘

Setup:
  import structlog
  logger = structlog.get_logger()

Function: logged_harness(task)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Log workflow start                                     │
│ logger.info("workflow_started",                                 │
│             task_id=task["id"],                                 │
│             task_type=task["type"])                             │
│                                                                 │
│ JSON Output:                                                    │
│ {                                                               │
│   "event": "workflow_started",                                  │
│   "task_id": "test-failure-001",                                │
│   "task_type": "network_test_failure",                          │
│   "timestamp": "2026-08-20T10:00:00Z"                           │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘

For each agent in [network_agent, config_agent, timing_agent]:

  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 2: Log agent start                                     │
  │ logger.info("agent_started",                                 │
  │             step=step,                                       │
  │             agent=agent.name)                                │
  │                                                             │
  │ JSON Output (step=0, network_agent):                        │
  │ {                                                           │
  │   "event": "agent_started",                                 │
  │   "step": 0,                                                │
  │   "agent": "network_agent",                                 │
  │   "timestamp": "2026-08-20T10:00:01Z"                       │
  │ }                                                           │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ STEP 3: Execute agent (with error handling)                │
  └─────────────────────────────────────────────────────────────┘
                             │
                      ┌──────┴──────┐
                     Try           Except
                      │              │
                      ▼              ▼
  ┌──────────────────────────┐  ┌──────────────────────────┐
  │ SUCCESS PATH             │  │ ERROR PATH               │
  │                          │  │                          │
  │ output = agent.run(task) │  │ Exception caught         │
  │                          │  │                          │
  │ Log agent_completed:     │  │ Log agent_failed:        │
  │ logger.info(             │  │ logger.error(            │
  │   "agent_completed",     │  │   "agent_failed",        │
  │   step=step,             │  │   step=step,             │
  │   agent=agent.name,      │  │   agent=agent.name,      │
  │   confidence=output.get  │  │   error=str(e),          │
  │     ("confidence"),      │  │   exc_info=True)         │
  │   tokens_used=output.get │  │                          │
  │     ("tokens")           │  │ JSON Output:             │
  │ )                        │  │ {                        │
  │                          │  │   "event":               │
  │ JSON Output:             │  │     "agent_failed",      │
  │ {                        │  │   "step": 0,             │
  │   "event":               │  │   "agent":               │
  │     "agent_completed",   │  │     "network_agent",     │
  │   "step": 0,             │  │   "error":               │
  │   "agent":               │  │     "TimeoutError...",   │
  │     "network_agent",     │  │   "stack_trace": "...",  │
  │   "confidence": 0.85,    │  │   "timestamp":           │
  │   "tokens_used": 3500,   │  │     "2026-08-20T..."     │
  │   "timestamp":           │  │ }                        │
  │     "2026-08-20T..."     │  │                          │
  │ }                        │  │ Re-raise exception       │
  └──────────────────────────┘  └──────────────────────────┘

After all agents complete successfully:

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Log workflow completion                                │
│ logger.info("workflow_completed",                               │
│             task_id=task["id"])                                 │
│                                                                 │
│ JSON Output:                                                    │
│ {                                                               │
│   "event": "workflow_completed",                                │
│   "task_id": "test-failure-001",                                │
│   "timestamp": "2026-08-20T10:00:11Z"                           │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘

Complete Log Timeline (JSON):
┌─────────────────────────────────────────────────────────────────┐
│ {"event": "workflow_started", "task_id": "test-failure-001",    │
│  "timestamp": "2026-08-20T10:00:00Z"}                           │
│                                                                 │
│ {"event": "agent_started", "step": 0, "agent": "network_agent", │
│  "timestamp": "2026-08-20T10:00:01Z"}                           │
│                                                                 │
│ {"event": "agent_completed", "step": 0, "agent":                │
│  "network_agent", "confidence": 0.85, "tokens_used": 3500,      │
│  "timestamp": "2026-08-20T10:00:04Z"}                           │
│                                                                 │
│ {"event": "agent_started", "step": 1, "agent": "config_agent",  │
│  "timestamp": "2026-08-20T10:00:04Z"}                           │
│                                                                 │
│ {"event": "agent_completed", "step": 1, "agent":                │
│  "config_agent", "confidence": 0.92, "tokens_used": 3200,       │
│  "timestamp": "2026-08-20T10:00:08Z"}                           │
│                                                                 │
│ {"event": "workflow_completed", "task_id": "test-failure-001",  │
│  "timestamp": "2026-08-20T10:00:11Z"}                           │
└─────────────────────────────────────────────────────────────────┘

Querying Logs (Example):
  • Find all failed agents:
    jq 'select(.event == "agent_failed")' logs.jsonl

  • Calculate average agent latency:
    jq 'select(.event == "agent_completed") | .duration' logs.jsonl | avg

  • Find workflows for specific task:
    jq 'select(.task_id == "test-failure-001")' logs.jsonl

Key Benefits:
  • Structured data (not free-text)
  • Easy to query and aggregate
  • Integrates with ELK, Splunk, Datadog
  • Machine-readable for alerting
```

**Log Output (JSON):**

```json
{
  "event": "workflow_started",
  "task_id": "test-failure-001",
  "task_type": "network_test_failure",
  "timestamp": "2026-08-20T10:00:00Z"
}
{
  "event": "agent_started",
  "step": 0,
  "agent": "network_agent",
  "timestamp": "2026-08-20T10:00:01Z"
}
{
  "event": "agent_completed",
  "step": 0,
  "agent": "network_agent",
  "confidence": 0.85,
  "tokens_used": 3500,
  "timestamp": "2026-08-20T10:00:04Z"
}
```

**Benefits:**
- Easy to parse and query (JSON)
- Searchable by any field (task_id, agent, etc.)
- Integrates with log aggregation tools (ELK, Splunk)

---

## Atiya Lens

### Atiya's Harness Implementation

**Atiya** is a production harness built for diagnosing network test failures in a QA automation environment. It implements a **specialist cascade pattern** with three domain-specific agents.

#### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ATIYA ARCHITECTURE                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      INPUT: Test Failure                        │
│  • Test name: "test_ntp_sync"                                   │
│  • Environment: "testbed-007"                                   │
│  • Timestamp: "2026-08-20T10:00:00Z"                            │
│  • Logs: [device logs, system logs, test runner logs]          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              SPECIALIST CASCADE (SEQUENTIAL)                    │
└─────────────────────────────────────────────────────────────────┘

    ┌────────────────────────────────────────────────┐
    │ Specialist 1: Network Agent                    │
    │ • Model: GPT-4                                 │
    │ • System Prompt: "Network diagnostics expert" │
    │ • Context: Interface stats, routing, ARP       │
    │ • Output: network_findings + confidence        │
    └──────────────────┬─────────────────────────────┘
                       │
                       ▼ (pass findings to next agent)
                       │
    ┌────────────────────────────────────────────────┐
    │ Specialist 2: Config Agent                     │
    │ • Model: GPT-4                                 │
    │ • System Prompt: "Config audit expert"        │
    │ • Context: Device configs, change history      │
    │ • Input: Network findings                      │
    │ • Output: config_findings + confidence         │
    └──────────────────┬─────────────────────────────┘
                       │
                       ▼ (accumulate evidence)
                       │
    ┌────────────────────────────────────────────────┐
    │ Specialist 3: Timing Agent                     │
    │ • Model: GPT-4                                 │
    │ • System Prompt: "Timing/NTP expert"          │
    │ • Context: NTP logs, clock drift               │
    │ • Input: Network + Config findings             │
    │ • Output: timing_findings + confidence         │
    └──────────────────┬─────────────────────────────┘
                       │
                       ▼ (all evidence collected)
                       │
    ┌────────────────────────────────────────────────┐
    │ Synthesis Agent                                │
    │ • Model: GPT-4                                 │
    │ • Input: All specialist findings               │
    │ • Output: Root cause + remediation + confidence│
    └──────────────────┬─────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT: Diagnosis Report                     │
│  • Root Cause: "ACL change blocked NTP traffic"                 │
│  • Evidence: [network latency, ACL diff, NTP unreachable]      │
│  • Remediation: "Revert ACL or add NTP exception"              │
│  • Confidence: 0.88                                             │
└─────────────────────────────────────────────────────────────────┘
```

### Specialist Cascade Architecture

**Why Cascade Over Parallel?**

1. **Context Efficiency:** Each specialist sees only domain-relevant data (3K tokens) instead of all data (50K tokens)
2. **Expert Focus:** Network agent doesn't dilute expertise trying to understand configs
3. **Evidence Accumulation:** Later agents benefit from earlier findings (timing agent can focus on NTP since network already ruled out connectivity issues)
4. **Explainability:** Clear chain of reasoning: "Network OK → Config issue found → Timing confirms NTP blocked"

**Agent Profiles:**

```
┌────────────────────────────────────────────────────────────────────┐
│              ATIYA AGENT PROFILE SPECIFICATIONS                    │
└────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ AGENT 1: Network Specialist                                     │
├─────────────────────────────────────────────────────────────────┤
│ Configuration:                                                  │
│   name: "network_specialist"                                    │
│   model: "gpt-4"                                                │
│   temperature: 0.2  (Low for deterministic diagnostics)         │
│   max_tokens: 2000                                              │
│                                                                 │
│ System Prompt:                                                  │
│   Role: Network diagnostics expert for test automation envs    │
│   Task: Analyze network connectivity, routing, latency issues   │
│                                                                 │
│ Context Provided:                                               │
│   • Interface statistics (packet loss, errors, collisions)      │
│   • Routing tables                                              │
│   • ARP cache                                                   │
│   • Ping/traceroute logs                                        │
│   • VLAN configurations                                         │
│                                                                 │
│ Output Schema (JSON):                                           │
│   {                                                             │
│     "network_ok": bool,                                         │
│     "findings": [list of issues found],                         │
│     "confidence": float (0-1),                                  │
│     "evidence": [specific log excerpts]                         │
│   }                                                             │
│                                                                 │
│ Constraints:                                                    │
│   • Focus ONLY on network-layer issues                          │
│   • Do not speculate about config or timing                     │
│   • Provide evidence for all findings                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ AGENT 2: Config Specialist                                      │
├─────────────────────────────────────────────────────────────────┤
│ Configuration:                                                  │
│   name: "config_specialist"                                     │
│   model: "gpt-4"                                                │
│   temperature: 0.2                                              │
│   max_tokens: 2000                                              │
│                                                                 │
│ System Prompt:                                                  │
│   Role: Device configuration auditor for network equipment      │
│   Task: Identify config errors, compliance violations, changes  │
│                                                                 │
│ Context Provided:                                               │
│   • Device startup-config and running-config                    │
│   • Configuration change history (diffs)                        │
│   • Compliance rules                                            │
│   • Prior network findings (if any)                             │
│                                                                 │
│ Output Schema (JSON):                                           │
│   {                                                             │
│     "config_issues": [list of config problems],                 │
│     "recent_changes": [changes made in last 7 days],            │
│     "confidence": float (0-1),                                  │
│     "evidence": [config snippets showing issues]                │
│   }                                                             │
│                                                                 │
│ Constraints:                                                    │
│   • Focus ONLY on configuration issues                          │
│   • Do not diagnose network or timing                           │
│   • Reference network findings if provided                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ AGENT 3: Timing Specialist                                      │
├─────────────────────────────────────────────────────────────────┤
│ Configuration:                                                  │
│   name: "timing_specialist"                                     │
│   model: "gpt-4"                                                │
│   temperature: 0.2                                              │
│   max_tokens: 2000                                              │
│                                                                 │
│ System Prompt:                                                  │
│   Role: Timing and synchronization expert (NTP, PTP, drift)     │
│   Task: Diagnose timing-related test failures                   │
│                                                                 │
│ Context Provided:                                               │
│   • NTP logs and sync status                                    │
│   • System clock drift metrics                                  │
│   • Prior network and config findings (if any)                  │
│                                                                 │
│ Output Schema (JSON):                                           │
│   {                                                             │
│     "timing_issues": [list of timing problems],                 │
│     "root_cause": str (most likely cause),                      │
│     "confidence": float (0-1),                                  │
│     "evidence": [log excerpts showing issues]                   │
│   }                                                             │
│                                                                 │
│ Constraints:                                                    │
│   • Focus ONLY on timing issues                                 │
│   • Integrate prior findings if relevant                        │
│   • Explain causal chain from network/config to timing          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ AGENT 4: Synthesis Specialist                                   │
├─────────────────────────────────────────────────────────────────┤
│ Configuration:                                                  │
│   name: "synthesis_specialist"                                  │
│   model: "gpt-4"                                                │
│   temperature: 0.3  (Slightly higher for creative synthesis)    │
│   max_tokens: 1500                                              │
│                                                                 │
│ System Prompt:                                                  │
│   Role: Senior QA engineer synthesizing multi-domain diagnoses  │
│   Task: Combine all specialist findings into final root cause   │
│                                                                 │
│ Input:                                                          │
│   JSON outputs from all specialist agents                       │
│   (network, config, timing)                                     │
│                                                                 │
│ Output Schema (JSON):                                           │
│   {                                                             │
│     "root_cause": str (concise summary),                        │
│     "evidence": [key evidence from specialists],                │
│     "remediation": str (how to fix the issue),                  │
│     "confidence": float (0-1, weighted avg of specialists)      │
│   }                                                             │
│                                                                 │
│ Constraints:                                                    │
│   • Diagnosis must be coherent (no contradictions)              │
│   • All evidence must support root cause                        │
│   • Remediation must be actionable                              │
│   • Confidence reflects weakest specialist link                 │
└─────────────────────────────────────────────────────────────────┘

Agent Temperature Strategy:
┌──────────────────┬─────────────┬───────────────────────────┐
│ Agent            │ Temperature │ Reasoning                 │
├──────────────────┼─────────────┼───────────────────────────┤
│ Network          │ 0.2         │ Deterministic diagnosis   │
│ Config           │ 0.2         │ Deterministic diagnosis   │
│ Timing           │ 0.2         │ Deterministic diagnosis   │
│ Synthesis        │ 0.3         │ Creative integration      │
└──────────────────┴─────────────┴───────────────────────────┘

Key Design Principle:
  Each specialist has narrow domain expertise, preventing
  "jack of all trades, master of none" dilution. Synthesis
  agent integrates findings into coherent diagnosis.
```

### Results: Accuracy Improvement from Orchestration

**Experiment:** Compare single-shot diagnosis vs. Atiya harness on 100 test failures with known root causes.

#### Single-Shot Approach

```
Prompt: "You are a QA diagnostics expert. Analyze this test failure and determine the root cause."

Context: All logs, configs, metrics (50K tokens, truncated to fit context window)

Results:
• Correct diagnosis: 73/100 (73%)
• Incorrect diagnosis: 18/100 (18%)
• Uncertain/No diagnosis: 9/100 (9%)
```

**Failure Modes:**
- Context overload: LLM skipped critical evidence buried in 50K tokens
- Domain dilution: Tried to be expert in network + config + timing, missed nuances
- Multi-step reasoning failure: Skipped steps or hallucinated connections

#### Atiya Harness Approach

```
Workflow: Network Agent → Config Agent → Timing Agent → Synthesis

Context per agent: 3K tokens (domain-focused)

Results:
• Correct diagnosis: 91/100 (91%)
• Incorrect diagnosis: 6/100 (6%)
• Uncertain/No diagnosis: 3/100 (3%)
```

**Improvement:**
- Accuracy: **+18 percentage points** (73% → 91%)
- Incorrect diagnoses: **-12 percentage points** (18% → 6%)
- Uncertain cases: **-6 percentage points** (9% → 3%)

#### Cost-Benefit Analysis

**Single-Shot:**
- Cost per diagnosis: $0.18 (5K input tokens × $0.03 + 500 output tokens × $0.06)
- Accuracy: 73%
- False positives requiring manual review: 27

**Atiya Harness:**
- Cost per diagnosis: $0.57 (4 agents × avg $0.14)
- Accuracy: 91%
- False positives requiring manual review: 9

**ROI:**
- Additional cost: $0.39 per diagnosis
- Manual review saved: 18 failures × 30 min × $100/hour = **$900 saved**
- Net benefit per 100 failures: $900 - (100 × $0.39) = **$861**

**Conclusion:** Harness orchestration delivers **18% accuracy improvement** while remaining highly cost-effective.

---

### Key Design Decisions in Atiya

#### 1. Why Sequential (Cascade) Instead of Parallel?

**Considered Parallel:** All three specialists run simultaneously, synthesis agent aggregates.

**Rejected Because:**
- **Context inefficiency:** Each agent needs full dataset (50K tokens) since they can't assume others will find certain issues
- **Redundant work:** Network agent checks for ACL issues, config agent also checks for ACL issues (overlap)
- **No evidence accumulation:** Timing agent can't leverage network findings to focus investigation

**Cascade Benefits:**
- **Context reduction:** Each agent sees only 3K tokens
- **Expert focus:** Network agent doesn't need to understand NTP, timing agent doesn't need to understand routing
- **Guided investigation:** Early findings narrow later searches

#### 2. Why Separate Synthesis Agent?

**Could Instead:** Have timing agent (final in cascade) produce final diagnosis.

**Separate Synthesis Because:**
- **Role clarity:** Timing agent focused on timing domain, synthesis agent weighs all evidence
- **Confidence calibration:** Synthesis agent can downgrade confidence if specialist findings conflict
- **Explainability:** Explicit synthesis step makes reasoning transparent

#### 3. Why GPT-4 for All Agents?

**Considered:** Use GPT-3.5 for simple agents, GPT-4 only for synthesis.

**GPT-4 for All Because:**
- **Accuracy critical:** False diagnoses costly (engineer time wasted on wrong path)
- **Complex reasoning:** Even "simple" network diagnostics require multi-step reasoning
- **Cost acceptable:** $0.57 per diagnosis is small vs. $50 manual diagnosis cost

#### 4. Error Handling Strategy

**Implemented:**
- **Per-agent retry:** If agent times out, retry with exponential backoff (max 3 attempts)
- **Validation gates:** Each agent output validated against JSON schema before passing to next
- **Partial results:** If timing agent fails, return network + config findings with "incomplete" flag

**Not Implemented:**
- **Agent fallback:** No cheaper model fallback (prioritized accuracy over cost)
- **Human-in-the-loop:** No manual intervention during workflow (async process)

---

## Summary

### Key Takeaways

1. **Harness Engineering = Context + Orchestration + Execution**
   - Goes beyond prompt and context engineering to coordinate multi-agent workflows
   - Enables solving complex problems that exceed single LLM call capabilities

2. **Core Patterns:**
   - **Sequential:** Linear dependency chain (A → B → C)
   - **Parallel:** Independent tasks run simultaneously
   - **Conditional:** Routing based on intermediate results
   - **Cascade:** Specialist chain with evidence accumulation (Atiya pattern)
   - **Retry:** Error recovery with exponential backoff

3. **Critical Mechanics:**
   - **Loops:** Iterative refinement until task complete
   - **State Management:** Share context across agents (Redis, DB, in-memory)
   - **Error Handling:** Classify errors (transient, semantic, fatal) and recover appropriately
   - **Cost Control:** Budget limits, early termination, model selection

4. **Production Readiness:**
   - **ROI Analysis:** Harnesses justify cost when accuracy improvement × volume × manual_cost > LLM_cost
   - **Observability:** Distributed tracing, structured logging, metrics dashboards
   - **Monitoring:** Track completion rate, latency, cost, error rate per agent

5. **When to Use Harnesses:**
   - **Multi-domain expertise** needed (network + config + timing)
   - **Multi-step reasoning** required (>5 sequential steps)
   - **Tool orchestration** needed (APIs, code execution, database queries)
   - **High volume** tasks (>100/month to amortize engineering cost)
   - **Error recovery** critical (retries, fallbacks, human escalation)

6. **When NOT to Use Harnesses:**
   - **Simple tasks** solvable with single prompt
   - **Low volume** (<10/month, manual work cheaper)
   - **High variability** (each task unique, no reusable patterns)
   - **Cost-sensitive** contexts where 3x LLM cost is prohibitive

### Atiya Case Study Summary

**Problem:** Diagnose network test failures (100/day) with 73% accuracy using single-shot LLM.

**Solution:** Harness with 3 specialists (Network, Config, Timing) + Synthesis agent.

**Results:**
- **Accuracy:** 73% → 91% (+18 pp)
- **Cost:** $0.18 → $0.57 per diagnosis (+217%)
- **ROI:** $861 saved per 100 failures (manual review reduction)
- **Payback:** 9 days to recover engineering investment

**Key Success Factors:**
1. **Cascade pattern:** Each specialist builds on prior findings
2. **Context efficiency:** 3K tokens per agent vs. 50K single-shot
3. **Expert focus:** Domain-specific system prompts
4. **Validation gates:** JSON schema enforcement between steps
5. **Error recovery:** Per-agent retries with exponential backoff

---

### The Harness Engineering Mindset

**Traditional Prompt Engineering:**
> "How can I write a prompt that makes the LLM solve this problem?"

**Harness Engineering:**
> "How can I decompose this problem into orchestrated steps, each solvable by a specialized agent, with state management, error recovery, and quality gates?"

**The Shift:**
- From **single-shot optimization** to **workflow design**
- From **prompt crafting** to **system architecture**
- From **LLM output** to **orchestrated multi-agent system**

Harness Engineering is the bridge from **AI experimentation** to **AI production systems**.

---

### Further Reading

**Foundational Concepts:**
- Prompt Engineering: How to design effective prompts
- Context Engineering: RAG pipelines and context retrieval
- Model Provider Abstraction: Managing multiple LLM providers

**Advanced Topics:**
- Agent Profiles: Defining specialist agents with distinct personas
- Tool Use: Enabling LLMs to call APIs and execute code
- Observability: Tracing and monitoring multi-agent systems

**Production Systems:**
- LangChain: Popular orchestration framework
- LangGraph: Graph-based workflow engine
- Semantic Kernel: Microsoft's orchestration library
- OpenAI Assistants API: Managed agent orchestration

---

**End of Document**

Total Lines: ~2,800
