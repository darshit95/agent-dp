# Loop Engineering: Iterative Refinement in AI Agents

**Complete Production Guide**

---

## Table of Contents

1. [Problem and Overview](#problem-and-overview)
2. [What is Loop Engineering?](#what-is-loop-engineering)
3. [Architecture and Flow Diagram](#architecture-and-flow-diagram)
4. [Use Cases](#use-cases)
5. [Design Methodologies](#design-methodologies)
6. [Core Mechanics](#core-mechanics)
7. [Issues and Solutions](#issues-and-solutions)
8. [Production Considerations](#production-considerations)
9. [Atiya Lens](#atiya-lens)
10. [Summary](#summary)

---

## Problem and Overview

### The Single-Shot Limitation

Traditional AI interactions follow a simple pattern:

```
User Input → LLM Processing → Single Response → Done
```

This works well for:
- Simple questions with definitive answers
- Tasks with clear constraints
- Scenarios where first attempt is sufficient

But fails for:
- Complex problem-solving requiring trial and error
- Tasks needing incremental refinement
- Scenarios where validation reveals issues
- Research requiring exploration

### Example: Diagnosis Without Loops

```
User: "My app crashes on startup"

Agent: "Try reinstalling dependencies"

[User tries, still crashes]

User: "Still crashing"

Agent: "Check your config file"

[User tries, still crashes]

User: "Still crashing"

Agent: "Look at logs for errors"
```

Each interaction is isolated. The agent doesn't build on previous attempts. Manual intervention required between steps.

### Example: Diagnosis With Loops

```
User: "My app crashes on startup"

Agent enters diagnostic loop:
  Iteration 1: Check logs → Found error "Module X not found"
  Iteration 2: Check dependencies → Found X installed but wrong version
  Iteration 3: Reinstall X with correct version → Test startup → Success

Agent: "Fixed. Issue was Module X version mismatch. Reinstalled v2.1.0."
```

Autonomous, iterative, builds on previous findings, terminates on success.

### Why Agents Need Loops

**Autonomy**: Agents should solve problems without constant human intervention

**Resilience**: First attempts often fail. Loops enable recovery.

**Quality**: Iteration produces better results than single-shot attempts

**Discovery**: Complex problems require exploration, not just execution

**Validation**: Many tasks need check-fix-recheck cycles

### Single-Shot vs Iterative Reasoning

| Aspect | Single-Shot | Iterative (Loop) |
|--------|-------------|------------------|
| **Attempts** | One | Multiple until success/limit |
| **Feedback** | None | Each iteration informs next |
| **State** | Stateless | Accumulates learnings |
| **Cost** | Low (1 call) | Higher (N calls) |
| **Quality** | Variable | Improves over iterations |
| **Use Cases** | Simple queries | Complex problem-solving |
| **Failure Mode** | Returns poor result | Retries or refines |
| **User Burden** | High (manual retry) | Low (autonomous) |

---

## What is Loop Engineering?

### Definition

**Loop Engineering** is the design and implementation of iterative processes where an AI agent repeatedly attempts a task, incorporating feedback from each iteration until:
- The task succeeds
- Quality threshold is met
- Resource limits are reached
- No further improvement is possible

### Core Concept

```
┌─────────────────────────────────────────────────┐
│  Loop Engineering = Iteration + State + Exit    │
│                                                  │
│  • Iteration: What happens each cycle            │
│  • State: What we remember from previous cycles  │
│  • Exit: When to stop looping                    │
└─────────────────────────────────────────────────┘
```

### Loop Types

#### 1. Retry Loop

**Purpose**: Keep trying until success

**Pattern**: Same action repeated with slight variations

**Exit**: Success or max attempts

```
┌──────────────┐
│   Try Task   │
└──────┬───────┘
       │
       ▼
   ┌───────┐
   │Success?│─── Yes ──► Done
   └───┬───┘
       │ No
       ▼
   ┌────────────┐
   │Max Attempts?│─── Yes ──► Fail
   └───┬────────┘
       │ No
       ▼
   ┌──────────┐
   │Wait/Adjust│
   └─────┬────┘
         │
         └──► Try Task (loop back)
```

**Example**: API call fails due to rate limit, retry with exponential backoff

#### 2. Refinement Loop

**Purpose**: Improve quality iteratively

**Pattern**: Each iteration builds on and improves previous

**Exit**: Quality threshold met or max iterations

```
┌────────────────┐
│Generate Version│
└───────┬────────┘
        │
        ▼
   ┌──────────┐
   │ Evaluate │
   │  Quality │
   └─────┬────┘
         │
         ▼
    ┌─────────┐
    │Good     │─── Yes ──► Done
    │Enough?  │
    └────┬────┘
         │ No
         ▼
    ┌────────────┐
    │Identify    │
    │Improvements│
    └─────┬──────┘
          │
          ▼
    ┌─────────────┐
    │Apply Fixes  │
    │& Regenerate │
    └──────┬──────┘
           │
           └──► Evaluate Quality (loop back)
```

**Example**: Generate code, check for bugs, fix bugs, regenerate until tests pass

#### 3. Search Loop

**Purpose**: Explore solution space to find best option

**Pattern**: Generate candidates, evaluate, explore promising directions

**Exit**: Best candidate found or search space exhausted

```
┌─────────────────┐
│Generate         │
│Candidates       │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │Evaluate│
    │  Each  │
    └────┬───┘
         │
         ▼
    ┌─────────────┐
    │Found Good   │─── Yes ──► Return Best
    │Solution?    │
    └──────┬──────┘
           │ No
           ▼
    ┌──────────────┐
    │More Space    │─── No ──► Return Best So Far
    │to Explore?   │
    └──────┬───────┘
           │ Yes
           ▼
    ┌──────────────┐
    │Select Next   │
    │Direction     │
    └──────┬───────┘
           │
           └──► Generate Candidates (loop back)
```

**Example**: Research assistant explores different sources, evaluates relevance, follows most promising leads

#### 4. Validation Loop

**Purpose**: Check, fix, recheck until valid

**Pattern**: Validate → Identify issues → Fix → Validate again

**Exit**: Validation passes or unfixable

```
┌──────────┐
│ Validate │
└─────┬────┘
      │
      ▼
  ┌───────┐
  │ Valid?│─── Yes ──► Done
  └───┬───┘
      │ No
      ▼
  ┌──────────────┐
  │Identify      │
  │Violations    │
  └──────┬───────┘
         │
         ▼
    ┌────────┐
    │Fixable?│─── No ──► Fail with Details
    └────┬───┘
         │ Yes
         ▼
    ┌─────────┐
    │Apply Fix│
    └────┬────┘
         │
         └──► Validate (loop back)
```

**Example**: Code linting loop - lint, find errors, fix, lint again until clean

### When to Use Loops vs Single-Shot

#### Use Single-Shot When:

- Task is simple and well-defined
- First attempt usually succeeds
- Cost of retry exceeds benefit
- Real-time response required
- No validation needed

**Examples**:
- "What's the capital of France?"
- "Translate this sentence"
- "Format this JSON"

#### Use Loops When:

- Task complexity means first attempt often fails
- Quality improves with iteration
- Validation/testing is required
- Exploration is needed
- Autonomy is valuable

**Examples**:
- "Debug why my app crashes"
- "Generate production-ready code with tests"
- "Research the best approach for X"
- "Create a detailed plan for Y"

#### Hybrid Approach

Many systems use single-shot for initial attempt, escalating to loop if it fails:

```
┌─────────────────────────────────────────────────────────┐
│              SMART TASK HANDLER FLOW                    │
└─────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  Receive Task    │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────────┐
    │ Single-Shot Attempt  │  ◄─── Fast, low-cost first try
    └──────────┬───────────┘
               │
               ▼
         ┌──────────┐
         │ Good      │
         │ Enough?   │
         └─────┬────┘
               │
       ┌───────┴────────┐
       │                │
      Yes              No
       │                │
       ▼                ▼
  ┌─────────┐   ┌───────────────────┐
  │ Return  │   │ Refinement Loop   │  ◄─── Escalate to iteration
  │ Result  │   │ (with initial     │
  └─────────┘   │  result as seed)  │
                └────────┬──────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Return      │
                  │ Improved    │
                  │ Result      │
                  └─────────────┘

Strategy: Try fast path first, escalate to expensive iteration only when needed


---

## Architecture and Flow Diagram

### Complete Loop Architecture

**Flow Overview:**

1. **LOOP CONTROLLER** → Starts and manages the entire loop process
2. **ITERATION EXECUTOR** → Executes each loop iteration (5 steps)
3. **STATE ACCUMULATOR** → Collects insights across iterations
4. **TERMINATION CHECKER** → Decides whether to continue or stop
5. **Decision Point** → Continue looping or return final result

**Component Breakdown:**

**[1] LOOP CONTROLLER**
- Orchestrates iterations
- Manages budget (tokens, cost, time)
- Enforces termination conditions
- Logs metrics and performance

**[2] ITERATION EXECUTOR** (5-Step Process)
- **Step 1:** Load State (read findings, review attempts/errors)
- **Step 2:** Build Prompt (incorporate state, add learnings)
- **Step 3:** Call LLM (execute query, track usage)
- **Step 4:** Parse Response (extract data, validate format)
- **Step 5:** Execute Actions (run commands, collect evidence)

**[3] STATE ACCUMULATOR** (Tracks Across Iterations)
- **Findings:** Insights discovered
- **Attempts:** History of what was tried
- **Errors:** Failed paths to avoid
- **Learnings:** Refined understanding
- **Metrics:** Performance data (tokens, time, cost)

**[4] TERMINATION CHECKER** (Evaluates 4 Conditions)
- **Success:** Has the goal been achieved?
- **Quality:** Does output meet quality thresholds?
- **Budget:** Are we within token/cost/time limits?
- **Convergence:** Are we making meaningful progress?

**[5] DECISION POINT**
- **IF any termination condition met** → Return final result (findings, state, metrics)
- **IF all conditions unmet** → Next iteration (loop back to Step 1)

### Component Details

#### 1. Loop Controller

**Responsibilities**:
- Start loop with initial state
- Track iterations count
- Monitor resource consumption
- Enforce hard limits
- Collect metrics
- Handle errors

**Key Data**:
```
┌──────────────────────────────────────────────────────────────┐
│                    LOOP CONTROLLER DATA                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Configuration:                                              │
│  ├─ max_iterations: int                                      │
│  │    └─ Maximum cycles before forced stop                  │
│  │                                                           │
│  └─ budget: Budget                                           │
│       ├─ tokens: Maximum tokens to consume                   │
│       ├─ cost: Maximum dollar amount                         │
│       └─ time: Maximum wall-clock time                       │
│                                                              │
│  Runtime State:                                              │
│  ├─ current_iteration: int                                   │
│  │    └─ Which cycle we're in (1-based)                     │
│  │                                                           │
│  ├─ total_cost: float                                        │
│  │    └─ Accumulated cost across iterations                 │
│  │                                                           │
│  └─ start_time: datetime                                     │
│       └─ When loop began (for timeout checks)               │
│                                                              │
│  Metrics:                                                    │
│  └─ metrics: List[IterationMetrics]                          │
│       └─ Per-iteration performance/outcome data             │
│            ├─ tokens_used                                    │
│            ├─ cost                                           │
│            ├─ duration                                       │
│            └─ outcome                                        │
└──────────────────────────────────────────────────────────────┘
```

#### 2. Iteration Executor

**Responsibilities**:
- Construct prompt for current iteration
- Include state from previous iterations
- Call LLM
- Parse and validate response
- Execute any actions
- Return results to controller

**Prompt Structure**:
```
System: You are in iteration {N} of {MAX}. Previous attempts:
{STATE_SUMMARY}

User: {ORIGINAL_TASK}

Focus this iteration on: {ITERATION_FOCUS}

Previous errors: {ERRORS_FROM_LAST_ITERATION}
```

#### 3. State Accumulator

**Responsibilities**:
- Store results from each iteration
- Maintain history of attempts
- Track what's been tried
- Record learnings/insights
- Manage memory (summarize old iterations if needed)

**Example State**:
```
┌──────────────────────────────────────────────────────────────┐
│              STATE ACCUMULATOR STRUCTURE                     │
└──────────────────────────────────────────────────────────────┘

attempts: List of iteration records
┌─────────────────────────────────────────────────────┐
│ Iteration 1                                         │
│  ├─ action: "checked logs"                          │
│  ├─ result: "found error X"                         │
│  └─ cost: $0.02                                     │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ Iteration 2                                         │
│  ├─ action: "checked config"                        │
│  ├─ result: "config valid"                          │
│  └─ cost: $0.015                                    │
└─────────────────────────────────────────────────────┘

findings: Cumulative discoveries
├─ "error X present"
└─ "config valid"

hypotheses: Current theories about root cause
└─ "error X from missing dependency"

tried: Actions already attempted (prevents duplicates)
├─ "check_logs"
└─ "check_config"

┌──────────────────────────────────────────────────┐
│  This state grows with each iteration,           │
│  informing the next attempt and preventing       │
│  redundant work                                  │
└──────────────────────────────────────────────────┘
```

#### 4. Termination Checker

**Responsibilities**:
- Evaluate exit conditions after each iteration
- Determine if loop should continue
- Return reason for termination

**Exit Conditions**:
```
┌─────────────────────────────────────────────────────────────┐
│           TERMINATION DECISION TREE                         │
└─────────────────────────────────────────────────────────────┘

               ┌──────────────────┐
               │ should_terminate │
               │  (state, iter,   │
               │    budget)       │
               └────────┬─────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   ┌─────────┐   ┌──────────┐   ┌──────────────┐
   │ Success?│   │ Iter >=  │   │  Budget      │
   │         │   │  MAX?    │   │  Exhausted?  │
   └────┬────┘   └─────┬────┘   └──────┬───────┘
        │              │               │
       Yes            Yes             Yes
        │              │               │
        ▼              ▼               ▼
   ┌──────────┐  ┌──────────┐   ┌──────────┐
   │  STOP:   │  │  STOP:   │   │  STOP:   │
   │ "task_   │  │ "max_    │   │ "budget_ │
   │completed"│  │iterations"│   │exceeded" │
   └──────────┘  └──────────┘   └──────────┘
   
        │              │               │
        └──────────────┴───────────────┘
                       │
                      No to all above
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
   ┌──────────┐               ┌──────────────┐
   │ Quality  │               │ No Progress  │
   │Threshold │               │ Last N=3     │
   │   Met?   │               │ Iterations?  │
   └─────┬────┘               └──────┬───────┘
         │                           │
        Yes                         Yes
         │                           │
         ▼                           ▼
   ┌──────────┐               ┌──────────┐
   │  STOP:   │               │  STOP:   │
   │ "quality_│               │ "no_     │
   │sufficient"│              │progress" │
   └──────────┘               └──────────┘
   
         │                           │
         └───────────────┬───────────┘
                         │
                        No to all
                         │
                         ▼
                  ┌─────────────┐
                  │  CONTINUE   │
                  │  (return    │
                  │ False, None)│
                  └─────────────┘
```

### Flow Diagram with State Transitions

```
START
  │
  ▼
┌────────────────┐
│ Initialize     │
│ • Set max iter │
│ • Set budget   │
│ • Initial state│
└───────┬────────┘
        │
        ▼
┌────────────────────────────────────────────────┐
│         ITERATION LOOP (i = 1 to MAX)          │
│                                                │
│   ┌──────────────────────────────────────┐    │
│   │ Build Prompt with State              │    │
│   └─────────┬────────────────────────────┘    │
│             ▼                                  │
│   ┌──────────────────────────────────────┐    │
│   │ Call LLM                             │    │
│   └─────────┬────────────────────────────┘    │
│             ▼                                  │
│   ┌──────────────────────────────────────┐    │
│   │ Execute Actions                      │    │
│   └─────────┬────────────────────────────┘    │
│             ▼                                  │
│   ┌──────────────────────────────────────┐    │
│   │ Update State                         │    │
│   │ • Add attempt record                 │    │
│   │ • Update findings                    │    │
│   │ • Increment cost                     │    │
│   └─────────┬────────────────────────────┘    │
│             ▼                                  │
│   ┌──────────────────────────────────────┐    │
│   │ Check Termination Conditions         │    │
│   └─────────┬────────────────────────────┘    │
│             │                                  │
│        ┌────┴────┐                             │
│        │         │                             │
│     Continue   Stop                            │
│        │         │                             │
│        ▼         ▼                             │
│    (loop)    (exit)                            │
└────────────────────────────────────────────────┘
        │
        ▼
┌────────────────┐
│ Return Results │
│ • Final state  │
│ • Metrics      │
│ • Success flag │
└────────────────┘
        │
        ▼
      END
```

### State Transition Example

```
Iteration 1:
  State: {}
  Action: Check logs
  Result: Found "Connection timeout"
  State: {findings: ["timeout error"]}
  Continue: True

Iteration 2:
  State: {findings: ["timeout error"]}
  Action: Check network config
  Result: Found "wrong endpoint URL"
  State: {findings: ["timeout error", "wrong URL"], hypothesis: "URL misconfigured"}
  Continue: True

Iteration 3:
  State: {findings: ["timeout error", "wrong URL"], hypothesis: "URL misconfigured"}
  Action: Fix URL in config
  Result: Test connection → Success
  State: {findings: [...], hypothesis: [...], solution: "fixed URL", success: True}
  Continue: False (success)

Return: {
  success: True,
  solution: "Fixed endpoint URL in config",
  iterations: 3,
  cost: 0.045
}
```

---

## Use Cases

### 1. Atiya: Diagnosis Refinement Loop

**Scenario**: User reports "Tests failing in CI"

**Without Loop** (single-shot):
```
User: "Tests failing in CI"
Agent: "Check your test configuration"
[Doesn't solve it]
```

**With Loop**:
```
Iteration 1: Analyze CI logs
  Finding: 3 tests fail with "Module not found"
  
Iteration 2: Check dependencies
  Finding: requirements.txt missing package X
  
Iteration 3: Check recent changes
  Finding: Commit ABC removed package X accidentally
  
Iteration 4: Propose fix
  Action: Add package X back to requirements.txt
  Validation: Run tests locally → Pass
  
Result: Root cause found, fix validated, ready to apply
```

**Loop Type**: Diagnostic refinement with validation

**Exit Condition**: Fix validated or max iterations

### 2. Code Generation with Validation Loop

**Scenario**: Generate production-ready function with tests

**Flow**:
```
Iteration 1: Generate initial code
  Output: Basic function implementation
  
Iteration 2: Generate tests
  Output: Test cases
  Run: 2 tests fail
  
Iteration 3: Fix failing tests
  Output: Updated function
  Run: All tests pass, but linter errors
  
Iteration 4: Fix linting
  Output: Formatted code
  Run: Tests pass, linter clean, type checker passes
  
Result: Production-ready code with tests
```

**Loop Type**: Validation loop (generate → test → fix → validate)

**Exit Condition**: All validation passes

**Architecture**:
```
┌──────────────┐
│  Generate    │
│  Code        │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Run Validators:      │
│ • Unit tests         │
│ • Linter (flake8)    │
│ • Type checker(mypy) │
│ • Security scan      │
└──────┬───────────────┘
       │
       ▼
   ┌────────┐
   │All Pass?│── Yes ──► Return Code
   └───┬────┘
       │ No
       ▼
┌──────────────────┐
│ Parse Failures   │
│ • Which tests    │
│ • Which rules    │
│ • Error messages │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ Generate Fix     │
│ (with context)   │
└────┬─────────────┘
     │
     └──► Run Validators (loop)
```

### 3. Research Loops: Iterative Search

**Scenario**: "What's the best framework for building AI agents?"

**Flow**:
```
Iteration 1: Broad search
  Action: Search for "AI agent frameworks"
  Finding: LangChain, AutoGPT, AgentGPT, others
  Score relevance: Mixed results
  
Iteration 2: Refine search based on criteria
  Action: Search "production AI agent frameworks comparison"
  Finding: Detailed comparisons, benchmarks
  Extract: Pros/cons of top 3
  
Iteration 3: Deep dive on top candidates
  Action: Search each for "production case studies"
  Finding: Real-world usage patterns
  
Iteration 4: Synthesis
  Action: Compare findings
  Result: Recommendation with justification
```

**Loop Type**: Search loop (breadth-first initial, depth-first refinement)

**Exit Condition**: Sufficient evidence or search exhausted

**Search Tree**:
```
                     Start Query
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Framework A      Framework B      Framework C
        │                │                │
    ┌───┴───┐        ┌───┴───┐        ┌───┴───┐
    │       │        │       │        │       │
  Docs  Cases    Docs  Cases    Docs  Cases
    │       │        │       │        │       │
    └───┬───┘        └───┬───┘        └───┬───┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                   Synthesize
```

### 4. Planning Loops: Progressive Refinement

**Scenario**: "Create a deployment plan for microservices migration"

**Flow**:
```
Iteration 1: High-level plan
  Output: 
    1. Analyze current system
    2. Design microservices
    3. Implement
    4. Deploy
    
Iteration 2: Refine with constraints
  Input: "Must have zero downtime"
  Output: Added blue-green deployment, rollback steps
  
Iteration 3: Add risk mitigation
  Input: "What could go wrong?"
  Output: Added monitoring, feature flags, canary releases
  
Iteration 4: Resource estimation
  Output: Timeline, team size, cost projections
  
Iteration 5: Validation
  Action: Check against best practices
  Output: Adjusted based on patterns
  
Result: Detailed, validated deployment plan
```

**Loop Type**: Refinement loop with progressive detail

**Exit Condition**: Plan complete and validated

**Refinement Stages**:
```
Draft Plan (sparse)
     │
     ▼
Add Constraints
     │
     ▼
Add Risk Mitigation
     │
     ▼
Add Resources
     │
     ▼
Validate & Adjust
     │
     ▼
Final Plan (detailed)
```

---

## Design Methodologies

### 1. Retry Loop: Keep Trying Until Success

**Purpose**: Handle transient failures through repeated attempts

**When to Use**:
- API calls that may fail due to rate limits/network
- File operations that may have temporary locks
- External service calls with intermittent issues

**Architecture**:
```
┌─────────────────────────────────────────────┐
│           RETRY LOOP PATTERN                │
│                                             │
│   attempt = 0                               │
│   max_attempts = 5                          │
│   base_delay = 1                            │
│                                             │
│   while attempt < max_attempts:             │
│       try:                                  │
│           result = execute_task()           │
│           return result  # Success          │
│       except RetriableError as e:           │
│           attempt += 1                      │
│           if attempt >= max_attempts:       │
│               raise MaxRetriesExceeded      │
│           delay = base_delay * (2 ** attempt)│
│           wait(delay)                       │
└─────────────────────────────────────────────┘
```

**Flow Diagram**:
```
START
  │
  ▼
┌─────────────┐
│ attempt = 0 │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Execute Task     │
└────┬─────────────┘
     │
     ▼
 ┌─────────┐
 │Success? │─── Yes ──► Return Result
 └────┬────┘
      │ No (error)
      ▼
 ┌──────────────┐
 │ Retriable    │─── No ──► Raise Error
 │ Error?       │
 └──────┬───────┘
        │ Yes
        ▼
 ┌──────────────────┐
 │ attempt += 1     │
 └────┬─────────────┘
      │
      ▼
 ┌──────────────────┐
 │ attempt >=       │─── Yes ──► Raise MaxRetries
 │ max_attempts?    │
 └────┬─────────────┘
      │ No
      ▼
 ┌──────────────────────┐
 │ Wait (exponential    │
 │ backoff)             │
 └────┬─────────────────┘
      │
      └──► Execute Task (loop)
```

**Exponential Backoff**:

```
Attempt 1: Immediate
Attempt 2: Wait 1 second
Attempt 3: Wait 2 seconds
Attempt 4: Wait 4 seconds
Attempt 5: Wait 8 seconds

Formula: delay = base_delay * (2 ^ (attempt - 1))
```

**Visual Timeline**:
```
Time:    0s    1s    3s         7s              15s
         │     │     │          │               │
Attempt: 1     2     3          4               5
         │     │     │          │               │
Result:  Fail  Fail  Fail       Fail            Success
         │     │     │          │               │
Wait:    →1s→  →2s→  →4s→       →8s→
```

**Decision Tree**:
```
                    Execute
                       │
        ┌──────────────┴──────────────┐
        │                             │
     Success                        Fail
        │                             │
    Return                    ┌───────┴───────┐
                              │               │
                         Retriable?      Non-Retriable
                              │               │
                    ┌─────────┴────────┐   Raise
                    │                  │
              Under Limit         At Limit
                    │                  │
              Wait & Retry         Raise
```

**Production Example**:

```
┌─────────────────────────────────────────────────────────────┐
│                   RETRY LOOP CLASS                          │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │ RetryLoop    │
                    │ Constructor  │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌─────────┐    ┌──────────┐    ┌──────────┐
    │max_     │    │base_     │    │backoff   │
    │attempts │    │delay     │    │factor    │
    │= 5      │    │= 1       │    │= 2       │
    └─────────┘    └──────────┘    └──────────┘

┌─────────────────────────────────────────────────────────────┐
│              execute(task, retriable_exceptions)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Initialize:                                                │
│  ├─ attempt = 0                                             │
│  └─ last_error = None                                       │
│                                                             │
│  ┌──────────────────────────────────────────┐              │
│  │  LOOP while attempt < max_attempts        │              │
│  │  ┌────────────────────────────────────┐  │              │
│  │  │  Try:                              │  │              │
│  │  │    result = task()                 │  │              │
│  │  │    ┌──────────────────────┐        │  │              │
│  │  │    │ Return Success Dict: │        │  │              │
│  │  │    │ • success: True      │        │  │              │
│  │  │    │ • result: result     │        │  │              │
│  │  │    │ • attempts: N        │        │  │              │
│  │  │    └──────────────────────┘        │  │              │
│  │  │                                    │  │              │
│  │  │  Except retriable_exceptions:      │  │              │
│  │  │    last_error = e                  │  │              │
│  │  │    attempt += 1                    │  │              │
│  │  │    │                                │  │              │
│  │  │    ├─► If attempt >= max_attempts: │  │              │
│  │  │    │     Raise MaxRetriesExceeded  │  │              │
│  │  │    │                                │  │              │
│  │  │    └─► delay = base_delay *        │  │              │
│  │  │              (backoff ^ (attempt-1))│  │              │
│  │  │        sleep(delay)                 │  │              │
│  │  └────────────────────────────────────┘  │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
│  If loop exits without return:                              │
│  └─► Raise RuntimeError                                     │
└─────────────────────────────────────────────────────────────┘

Usage Pattern:
┌─────────────────────────────────────────────────────────────┐
│  retry = RetryLoop(max_attempts=3)                          │
│                                                             │
│  result = retry.execute(                                    │
│      task = lambda: api.call(),                             │
│      retriable_exceptions = (RateLimitError, NetworkError)  │
│  )                                                          │
│                                                             │
│  # Returns: {"success": True, "result": ..., "attempts": N} │
└─────────────────────────────────────────────────────────────┘
```

**Issues & Solutions**:

| Issue | Solution |
|-------|----------|
| Infinite retry on persistent error | Max attempts limit |
| Same error every time | Classify errors (retriable vs not) |
| Long waits blocking other work | Async retry with background tasks |
| Exponential backoff too aggressive | Add jitter, cap max delay |
| Logs spammed with retry messages | Log only final success/failure |

---

### 2. Refinement Loop: Improve Quality Each Iteration

**Purpose**: Incrementally improve output quality through feedback

**When to Use**:
- Code generation requiring validation
- Content creation needing quality checks
- Planning tasks benefiting from iteration

**Architecture**:
```
┌────────────────────────────────────────────────┐
│         REFINEMENT LOOP PATTERN                │
│                                                │
│   current = generate_initial()                 │
│   iteration = 1                                │
│                                                │
│   while iteration <= max_iterations:           │
│       quality = evaluate(current)              │
│       if quality >= threshold:                 │
│           return current                       │
│                                                │
│       feedback = get_feedback(current, quality)│
│       current = refine(current, feedback)      │
│       iteration += 1                           │
│                                                │
│   return current  # Best effort                │
└────────────────────────────────────────────────┘
```

**Flow Diagram**:
```
START
  │
  ▼
┌────────────────────┐
│ Generate Initial   │
│ Version            │
└─────────┬──────────┘
          │
          ▼
┌─────────────────────────────────────┐
│    REFINEMENT LOOP (i=1 to MAX)     │
│                                     │
│  ┌──────────────────────┐           │
│  │ Evaluate Quality     │           │
│  │ • Run tests          │           │
│  │ • Check metrics      │           │
│  │ • Compare to goals   │           │
│  └─────────┬────────────┘           │
│            ▼                        │
│      ┌─────────┐                    │
│      │Quality  │─── Yes ──► Exit    │
│      │Met?     │                    │
│      └────┬────┘                    │
│           │ No                      │
│           ▼                         │
│  ┌────────────────────┐             │
│  │ Analyze Gaps       │             │
│  │ • What's wrong?    │             │
│  │ • How to fix?      │             │
│  └─────────┬──────────┘             │
│            ▼                        │
│  ┌────────────────────┐             │
│  │ Refine Version     │             │
│  │ (incorporate fixes)│             │
│  └─────────┬──────────┘             │
│            │                        │
│            └──► Next Iteration      │
└─────────────────────────────────────┘
          │
          ▼
     Return Best Version
```

**Quality Metrics**:

```
┌─────────────────────────────────────┐
│        Quality Dimensions           │
│                                     │
│  • Correctness (tests pass)         │
│  • Completeness (all requirements)  │
│  • Performance (meets benchmarks)   │
│  • Style (linting, formatting)      │
│  • Security (no vulnerabilities)    │
│  • Maintainability (complexity)     │
└─────────────────────────────────────┘

Each dimension scored 0-100
Overall quality = weighted average
Threshold = 80 (configurable)
```

**Refinement Flow Visualization**:

```
Version 1 (Quality: 40)
├─ Tests: 2/5 pass
├─ Linting: 10 errors
└─ Coverage: 30%
        │
        ▼ Feedback: Fix failing tests, resolve lint errors
        │
Version 2 (Quality: 65)
├─ Tests: 4/5 pass
├─ Linting: 2 errors
└─ Coverage: 60%
        │
        ▼ Feedback: Fix last test, clean remaining lint
        │
Version 3 (Quality: 85) ✓
├─ Tests: 5/5 pass
├─ Linting: 0 errors
└─ Coverage: 75%
```

**Production Example**:

```
┌─────────────────────────────────────────────────────────────┐
│              REFINEMENT LOOP CLASS                          │
└─────────────────────────────────────────────────────────────┘

Configuration:
├─ quality_threshold: 0.8
└─ max_iterations: 5

┌─────────────────────────────────────────────────────────────┐
│      execute(generator, evaluator, refiner) → result        │
├─────────────────────────────────────────────────────────────┤
│  Parameters:                                                │
│  • generator: () → Output                                   │
│  • evaluator: (Output) → (Quality, Feedback)                │
│  • refiner: (Output, Feedback) → Improved_Output            │
│                                                             │
│  Initialize:                                                │
│  ├─ current = generator()  (initial output)                 │
│  └─ history = []                                            │
│                                                             │
│  ┌─────────────────────────────────────────┐               │
│  │ FOR iteration in 1 to max_iterations:   │               │
│  │  ┌───────────────────────────────────┐  │               │
│  │  │ 1. Evaluate current output        │  │               │
│  │  │    quality, feedback =            │  │               │
│  │  │        evaluator(current)         │  │               │
│  │  └───────────────────────────────────┘  │               │
│  │  ┌───────────────────────────────────┐  │               │
│  │  │ 2. Record in history              │  │               │
│  │  │    history.append({               │  │               │
│  │  │      iteration, quality, feedback │  │               │
│  │  │    })                             │  │               │
│  │  └───────────────────────────────────┘  │               │
│  │  ┌───────────────────────────────────┐  │               │
│  │  │ 3. Check threshold                │  │               │
│  │  │    if quality >= threshold:       │  │               │
│  │  │      RETURN SUCCESS:              │  │               │
│  │  │      {                            │  │               │
│  │  │        "success": True,           │  │               │
│  │  │        "output": current,         │  │               │
│  │  │        "quality": quality,        │  │               │
│  │  │        "iterations": N,           │  │               │
│  │  │        "history": history         │  │               │
│  │  │      }                            │  │               │
│  │  └───────────────────────────────────┘  │               │
│  │  ┌───────────────────────────────────┐  │               │
│  │  │ 4. Refine for next iteration      │  │               │
│  │  │    current = refiner(current,     │  │               │
│  │  │                     feedback)     │  │               │
│  │  └───────────────────────────────────┘  │               │
│  └─────────────────────────────────────────┘               │
│                                                             │
│  If loop completes without reaching threshold:              │
│  RETURN BEST EFFORT:                                        │
│  {                                                          │
│    "success": False,                                        │
│    "output": current,                                       │
│    "quality": quality (last),                               │
│    "iterations": max_iterations,                            │
│    "history": history,                                      │
│    "reason": "max_iterations"                               │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘

Usage Example: Code Generation with Test Validation
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  generate_code():                                           │
│    return llm.generate("Write function to parse JSON")     │
│                                                             │
│  evaluate_code(code) → (score, feedback):                   │
│    score = 0, feedback = []                                 │
│    ┌────────────────────────────────────┐                  │
│    │ Test Validation (50% weight):     │                  │
│    │   tests_passed = run_tests(code)  │                  │
│    │   score += tests_passed × 0.5     │                  │
│    │   if failed: feedback.append(...) │                  │
│    └────────────────────────────────────┘                  │
│    ┌────────────────────────────────────┐                  │
│    │ Linting (30% weight):             │                  │
│    │   if no errors: score += 0.3      │                  │
│    │   else: feedback.append(errors)   │                  │
│    └────────────────────────────────────┘                  │
│    ┌────────────────────────────────────┐                  │
│    │ Coverage (20% weight):            │                  │
│    │   score += (coverage/100) × 0.2   │                  │
│    │   if <80%: feedback.append(...)   │                  │
│    └────────────────────────────────────┘                  │
│    return score, feedback                                   │
│                                                             │
│  refine_code(code, feedback):                               │
│    prompt = """                                             │
│      Current code has issues:                               │
│      {feedback}                                             │
│      Fix these issues: {code}                               │
│    """                                                      │
│    return llm.generate(prompt)                              │
│                                                             │
│  loop = RefinementLoop(quality_threshold=0.8,               │
│                        max_iterations=3)                    │
│  result = loop.execute(generate_code,                       │
│                        evaluate_code,                       │
│                        refine_code)                         │
└─────────────────────────────────────────────────────────────┘
```

**Convergence Patterns**:

```
Quality Over Iterations:

100% │                              ─────  Threshold
     │                         ────
     │                    ────
 80% │               ────          ← Meets threshold
     │          ────
     │     ────
     │ ────
   0%└────────────────────────────────────
      1    2    3    4    5    6

Good: Steady improvement, reaches threshold


100% │  ────────────────────────────────  Threshold
     │ 
 80% │ ───────
     │       └──────                      ← Plateau
     │             └─────
     │
   0%└────────────────────────────────────
      1    2    3    4    5    6

Bad: Early plateau, not improving


100% │
     │     ╱╲      ╱╲
     │    ╱  ╲    ╱  ╲                    ← Oscillation
 50% │   ╱    ╲  ╱    ╲
     │  ╱      ╲╱      ╲
   0%└────────────────────────────────────
      1    2    3    4    5    6

Bad: Oscillating, unstable
```

---

### 3. Search Loop: Explore Solution Space

**Purpose**: Find best solution through exploration

**When to Use**:
- Multiple possible approaches
- Need to compare options
- Solution space is large
- Best approach unknown upfront

**Strategies**:

#### Breadth-First Search

Explore all options at current depth before going deeper

```
                    Root Question
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Option A         Option B         Option C
        │                │                │
    Evaluate         Evaluate         Evaluate
        │                │                │
    ┌───┴───┐        ┌───┴───┐        ┌───┴───┐
    │       │        │       │        │       │
   A.1     A.2      B.1     B.2      C.1     C.2

Level 1: Explore A, B, C
Level 2: Explore A.1, A.2, B.1, B.2, C.1, C.2
```

**Best For**: When you need comprehensive coverage, early options might be best

#### Depth-First Search

Explore one path fully before trying others

```
                    Root Question
                         │
                    Option A
                         │
                    Evaluate
                         │
                    ┌────┴────┐
                   A.1       A.2
                    │
               Evaluate A.1
                    │
              ┌─────┴─────┐
            A.1.1       A.1.2

Level 1: A
Level 2: A.1
Level 3: A.1.1
Level 4: A.1.2
...then backtrack to A.2, then try B, etc.
```

**Best For**: When depth matters, solution likely down one path

#### Best-First Search

Always explore most promising option next

```
                    Root
                     │
        ┌────────────┼────────────┐
        │            │            │
    A (score=7)  B (score=9)  C (score=4)
                     │
              Explore B first
                     │
            ┌────────┴────────┐
        B.1 (score=8)     B.2 (score=6)
            │
     Explore B.1 next
     
Priority queue: [B:9, B.1:8, A:7, B.2:6, C:4]
```

**Best For**: When scoring is reliable, want best solution fast

**Architecture**:

```
┌────────────────────────────────────────┐
│         SEARCH LOOP PATTERN            │
│                                        │
│  frontier = [initial_state]            │
│  explored = set()                      │
│  best = None                           │
│                                        │
│  while frontier and not exhausted:     │
│      current = frontier.pop()          │
│      explored.add(current)             │
│                                        │
│      if is_solution(current):          │
│          if better_than(current, best):│
│              best = current            │
│          if good_enough(best):         │
│              return best               │
│                                        │
│      for neighbor in expand(current):  │
│          if neighbor not in explored:  │
│              frontier.add(neighbor)    │
│                                        │
│  return best                           │
└────────────────────────────────────────┘
```

**Flow Diagram**:

```
START
  │
  ▼
┌─────────────────────┐
│ Initialize:         │
│ • Frontier = [root] │
│ • Explored = {}     │
│ • Best = None       │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────────┐
│ While frontier not empty:        │
│                                  │
│  ┌────────────────────┐          │
│  │ Pop next from      │          │
│  │ frontier           │          │
│  └─────────┬──────────┘          │
│            ▼                     │
│  ┌────────────────────┐          │
│  │ Evaluate           │          │
│  └─────────┬──────────┘          │
│            │                     │
│     ┌──────┴──────┐              │
│     │             │              │
│  Solution?    Not Solution       │
│     │             │              │
│     ▼             ▼              │
│  ┌──────┐   ┌──────────┐        │
│  │Update│   │ Expand   │        │
│  │Best  │   │ Neighbors│        │
│  └──┬───┘   └────┬─────┘        │
│     │            │              │
│     ▼            ▼              │
│  Good       Add to Frontier     │
│  Enough?         │              │
│     │            │              │
│  Yes└────────────┘              │
│     │         No                │
│     ▼         (loop)            │
│  Return                         │
└──────────────────────────────────┘
```

**Pruning Strategies**:

Avoid exploring unpromising paths

```
┌────────────────────────────────┐
│     PRUNING RULES              │
│                                │
│  1. Score Threshold            │
│     if score(node) < min:      │
│         skip                   │
│                                │
│  2. Similarity Pruning         │
│     if too_similar(node, seen):│
│         skip                   │
│                                │
│  3. Cost Limit                 │
│     if cost(node) > budget:    │
│         skip                   │
│                                │
│  4. Depth Limit                │
│     if depth(node) > max:      │
│         skip                   │
└────────────────────────────────┘
```

**Pruning Visualization**:

```
                    Root
                     │
        ┌────────────┼────────────┐
        │            │            │
    A (score=7)  B (score=9)  C (score=2) ← PRUNED (score < 5)
        │            │
    ┌───┴───┐    ┌───┴───┐
   A.1     A.2  B.1     B.2 (similar to A.1) ← PRUNED
  (score=6)(score=9)(score=8)
    │        │      │
   KEEP    KEEP   KEEP

Final frontier: [A.2, B.1, A.1]
```

**Production Example**:

```
┌─────────────────────────────────────────────────────────────┐
│                   SEARCH LOOP CLASS                         │
└─────────────────────────────────────────────────────────────┘

Constructor:
├─ max_iterations: 20
└─ strategy: 'best_first' | 'breadth_first' | 'depth_first'

┌─────────────────────────────────────────────────────────────┐
│  execute(initial, expander, evaluator, is_solution)         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Parameters:                                                │
│  ├─ initial: starting state                                 │
│  ├─ expander: (state) -> [new_states]                       │
│  ├─ evaluator: (state) -> score (higher = better)           │
│  └─ is_solution: (state) -> bool                            │
│                                                             │
│  Initialize Data Structures:                                │
│  ┌─────────────────────────────────────────┐               │
│  │ Strategy-specific frontier:              │               │
│  │ • breadth_first → deque([initial])       │               │
│  │ • depth_first → [initial]                │               │
│  │ • best_first → PriorityQueue with        │               │
│  │                (-score, initial)         │               │
│  └─────────────────────────────────────────┘               │
│  ├─ explored = set()                                        │
│  ├─ best = None                                             │
│  ├─ best_score = -∞                                         │
│  └─ iterations = 0                                          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │ MAIN LOOP: while frontier and i < max_iter   │          │
│  │  ┌────────────────────────────────────────┐ │          │
│  │  │ 1. Get next from frontier:             │ │          │
│  │  │    • depth_first: pop()                │ │          │
│  │  │    • breadth_first: popleft()          │ │          │
│  │  │    • best_first: get highest score     │ │          │
│  │  └────────────────────────────────────────┘ │          │
│  │  ┌────────────────────────────────────────┐ │          │
│  │  │ 2. Skip if already explored            │ │          │
│  │  │    state_hash = hash(str(current))     │ │          │
│  │  │    if in explored: continue            │ │          │
│  │  │    explored.add(state_hash)            │ │          │
│  │  └────────────────────────────────────────┘ │          │
│  │  ┌────────────────────────────────────────┐ │          │
│  │  │ 3. Evaluate current state              │ │          │
│  │  │    score = evaluator(current)          │ │          │
│  │  └────────────────────────────────────────┘ │          │
│  │  ┌────────────────────────────────────────┐ │          │
│  │  │ 4. Check if solution & update best     │ │          │
│  │  │    if is_solution(current) and         │ │          │
│  │  │       score > best_score:              │ │          │
│  │  │       best = current                   │ │          │
│  │  │       best_score = score               │ │          │
│  │  │       if score >= 0.9: break ◄──┐      │ │          │
│  │  │                     Early exit  │      │ │          │
│  │  └────────────────────────────────────────┘ │          │
│  │  ┌────────────────────────────────────────┐ │          │
│  │  │ 5. Expand to neighbors                 │ │          │
│  │  │    neighbors = expander(current)       │ │          │
│  │  │    for each neighbor:                  │ │          │
│  │  │      if not explored:                  │ │          │
│  │  │        add to frontier (strategy-based)│ │          │
│  │  └────────────────────────────────────────┘ │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  Return:                                                    │
│  └─ {"best": best, "score": best_score,                    │
│      "iterations": N, "explored": M}                        │
└─────────────────────────────────────────────────────────────┘

Usage Example: Finding Best Implementation Approach
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  expand_approaches(current):                                │
│    ├─ current + " with caching"                             │
│    ├─ current + " with parallelization"                     │
│    └─ "different algorithm: " + alternative_algo()          │
│                                                             │
│  evaluate_approach(approach):                               │
│    └─ speed_score × 0.4                                     │
│       + memory_score × 0.3                                  │
│       + simplicity_score × 0.3                              │
│                                                             │
│  is_good_solution(approach):                                │
│    └─ evaluate_approach(approach) > 0.7                     │
│                                                             │
│  search = SearchLoop(max_iterations=15,                     │
│                      strategy='best_first')                 │
│                                                             │
│  result = search.execute(                                   │
│      initial = "basic implementation",                      │
│      expander = expand_approaches,                          │
│      evaluator = evaluate_approach,                         │
│      is_solution = is_good_solution                         │
│  )                                                          │
└─────────────────────────────────────────────────────────────┘
```

**Search Tree Visualization**:

```
                        "basic implementation" (0.5)
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
          "with caching"   "with parallel"  "different algo"
              (0.7)            (0.6)            (0.8) ← Best so far
                │                                 │
        ┌───────┴───────┐                  ┌──────┴──────┐
        │               │                  │             │
   "cache+index"  "cache+compress"  "algo+optimize" "algo+distribute"
      (0.75)          (0.72)             (0.85) ✓       (0.82)
                                            │
                                      SOLUTION FOUND
                                      Score: 0.85
                                      Depth: 2
                                      Iterations: 8
```

---

### 4. Validation Loop: Check → Fix → Check Again

**Purpose**: Ensure output meets all requirements through iterative validation

**When to Use**:
- Output must pass specific criteria
- Multiple validation rules
- Fixes can be automated
- Quality gates required

**Architecture**:

```
┌───────────────────────────────────────┐
│      VALIDATION LOOP PATTERN          │
│                                       │
│  output = generate()                  │
│  iteration = 1                        │
│                                       │
│  while iteration <= max_iterations:   │
│      violations = validate(output)    │
│                                       │
│      if not violations:               │
│          return output  # Valid       │
│                                       │
│      if not fixable(violations):      │
│          raise ValidationError        │
│                                       │
│      output = fix(output, violations) │
│      iteration += 1                   │
│                                       │
│  raise MaxIterationsExceeded          │
└───────────────────────────────────────┘
```

**Flow Diagram**:

```
START
  │
  ▼
┌────────────────┐
│ Generate       │
│ Initial Output │
└───────┬────────┘
        │
        ▼
┌───────────────────────────────────┐
│  VALIDATION LOOP (i=1 to MAX)     │
│                                   │
│  ┌─────────────────────┐          │
│  │ Run All Validators: │          │
│  │ • Syntax check      │          │
│  │ • Style check       │          │
│  │ • Tests             │          │
│  │ • Security scan     │          │
│  └──────────┬──────────┘          │
│             ▼                     │
│       ┌──────────┐                │
│       │ All Pass?│─── Yes ──► Return Output
│       └─────┬────┘                │
│             │ No                  │
│             ▼                     │
│  ┌────────────────────┐           │
│  │ Collect Violations │           │
│  └──────────┬─────────┘           │
│             ▼                     │
│       ┌──────────┐                │
│       │ Fixable? │─── No ──► Raise Error
│       └─────┬────┘                │
│             │ Yes                 │
│             ▼                     │
│  ┌────────────────────┐           │
│  │ Generate Fixes     │           │
│  └──────────┬─────────┘           │
│             ▼                     │
│  ┌────────────────────┐           │
│  │ Apply Fixes        │           │
│  └──────────┬─────────┘           │
│             │                     │
│             └──► Run Validators (loop)
└───────────────────────────────────┘
```

**Validation Categories**:

```
┌─────────────────────────────────────────────┐
│           VALIDATION TYPES                  │
│                                             │
│  1. SYNTAX                                  │
│     • Parsing succeeds                      │
│     • No syntax errors                      │
│     Fixable: Often yes                      │
│                                             │
│  2. STYLE                                   │
│     • Linting rules (flake8, eslint)        │
│     • Formatting (black, prettier)          │
│     Fixable: Yes (auto-format)              │
│                                             │
│  3. TYPE CHECKING                           │
│     • Type annotations correct              │
│     • No type mismatches                    │
│     Fixable: Sometimes                      │
│                                             │
│  4. TESTS                                   │
│     • Unit tests pass                       │
│     • Integration tests pass                │
│     Fixable: Yes (fix implementation)       │
│                                             │
│  5. SECURITY                                │
│     • No known vulnerabilities              │
│     • No hardcoded secrets                  │
│     Fixable: Yes (remove/fix issues)        │
│                                             │
│  6. BUSINESS LOGIC                          │
│     • Meets requirements                    │
│     • Edge cases handled                    │
│     Fixable: Yes (add logic)                │
└─────────────────────────────────────────────┘
```

**Convergence Detection**:

Detect when fixes aren't helping

```
┌─────────────────────────────────────┐
│      CONVERGENCE DETECTION          │
│                                     │
│  Track violations over iterations:  │
│                                     │
│  Iteration 1: [E1, E2, E3, E4]      │
│  Iteration 2: [E2, E4, E5]          │
│  Iteration 3: [E4, E5, E6]          │
│                                     │
│  Analysis:                          │
│  • Fixed: E1, E3                    │
│  • Persist: E2, E4                  │
│  • New: E5, E6                      │
│                                     │
│  If new >= fixed for 2 iterations:  │
│      → Not converging               │
│      → Abort or escalate            │
└─────────────────────────────────────┘
```

**Validation Decision Tree**:

```
                  Validate
                     │
        ┌────────────┴────────────┐
        │                         │
    All Pass                 Violations
        │                         │
    Return                  ┌─────┴─────┐
                            │           │
                     Syntax Errors   Logic Errors
                            │           │
                     ┌──────┴────┐      │
                     │           │      │
                 Fixable    Not Fixable │
                     │           │      │
                  Fix & Retry  Fail     │
                                    ┌───┴────┐
                                    │        │
                              Auto-Fixable  Manual
                                    │        │
                              Fix & Retry  Fail
```

**Production Example**:

```
┌─────────────────────────────────────────────────────────────┐
│              VALIDATION LOOP CLASS                          │
└─────────────────────────────────────────────────────────────┘

Configuration:
├─ max_iterations: 5
├─ validators: []
└─ fixers: {}

┌─────────────────────────────────────────────────────────────┐
│   add_validator(name, validator_func, fixer_func)           │
├─────────────────────────────────────────────────────────────┤
│  Parameters:                                                │
│  • validator_func: (output) → [violations]                  │
│  • fixer_func: (output, violations) → fixed_output          │
│                                                             │
│  Action:                                                    │
│  validators.append({                                        │
│    "name": name,                                            │
│    "validator": validator_func,                             │
│    "fixer": fixer_func                                      │
│  })                                                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              execute(output) → result                       │
├─────────────────────────────────────────────────────────────┤
│  history = []                                               │
│                                                             │
│  ┌──────────────────────────────────────────┐              │
│  │ FOR iteration in 1 to max_iterations:    │              │
│  │  ┌────────────────────────────────────┐  │              │
│  │  │ 1. Run All Validators              │  │              │
│  │  │    all_violations = []             │  │              │
│  │  │    for each validator:             │  │              │
│  │  │      violations = validator(output)│  │              │
│  │  │      if violations:                │  │              │
│  │  │        append to all_violations    │  │              │
│  │  └────────────────────────────────────┘  │              │
│  │  ┌────────────────────────────────────┐  │              │
│  │  │ 2. Track History                   │  │              │
│  │  │    history.append({                │  │              │
│  │  │      iteration: N,                 │  │              │
│  │  │      violations_count: X,          │  │              │
│  │  │      validators_failed: [...]      │  │              │
│  │  │    })                              │  │              │
│  │  └────────────────────────────────────┘  │              │
│  │  ┌────────────────────────────────────┐  │              │
│  │  │ 3. Check if Valid (no violations)  │  │              │
│  │  │    if not all_violations:          │  │              │
│  │  │      RETURN SUCCESS:               │  │              │
│  │  │      {                             │  │              │
│  │  │        "valid": True,              │  │              │
│  │  │        "output": output,           │  │              │
│  │  │        "iterations": N,            │  │              │
│  │  │        "history": history          │  │              │
│  │  │      }                             │  │              │
│  │  └────────────────────────────────────┘  │              │
│  │  ┌────────────────────────────────────┐  │              │
│  │  │ 4. Check if Fixable                │  │              │
│  │  │    unfixable = violations with     │  │              │
│  │  │                no fixer            │  │              │
│  │  │    if unfixable exists:            │  │              │
│  │  │      RETURN FAILURE:               │  │              │
│  │  │      {                             │  │              │
│  │  │        "valid": False,             │  │              │
│  │  │        "output": output,           │  │              │
│  │  │        "unfixable": unfixable,     │  │              │
│  │  │        "history": history          │  │              │
│  │  │      }                             │  │              │
│  │  └────────────────────────────────────┘  │              │
│  │  ┌────────────────────────────────────┐  │              │
│  │  │ 5. Check Convergence               │  │              │
│  │  │    if iter > 2 and                 │  │              │
│  │  │       not _is_improving():         │  │              │
│  │  │      RETURN FAILURE:               │  │              │
│  │  │      {                             │  │              │
│  │  │        "valid": False,             │  │              │
│  │  │        "output": output,           │  │              │
│  │  │        "reason": "not_converging", │  │              │
│  │  │        "history": history          │  │              │
│  │  │      }                             │  │              │
│  │  └────────────────────────────────────┘  │              │
│  │  ┌────────────────────────────────────┐  │              │
│  │  │ 6. Apply All Fixes                 │  │              │
│  │  │    for each violation_set:         │  │              │
│  │  │      output = fixer(output,        │  │              │
│  │  │                     violations)    │  │              │
│  │  └────────────────────────────────────┘  │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
│  If loop completes without validation:                      │
│  RETURN FAILURE:                                            │
│  {                                                          │
│    "valid": False,                                          │
│    "output": output,                                        │
│    "reason": "max_iterations",                              │
│    "history": history                                       │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│           _is_improving(history) → bool                     │
├─────────────────────────────────────────────────────────────┤
│  Check if violations decreasing                             │
│                                                             │
│  If len(history) < 3: return True (too early to judge)      │
│                                                             │
│  recent = last 3 violation counts                           │
│  return recent[-1] < recent[0]                              │
│         (latest < oldest = improving)                       │
└─────────────────────────────────────────────────────────────┘

Usage Example: Code Validation Pipeline
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  loop = ValidationLoop(max_iterations=3)                    │
│                                                             │
│  ┌──────────────────────────────────────────┐              │
│  │ VALIDATOR 1: Syntax                      │              │
│  │ validate_syntax(code):                   │              │
│  │   try:                                   │              │
│  │     compile(code, '<string>', 'exec')    │              │
│  │     return []  # No violations           │              │
│  │   except SyntaxError as e:               │              │
│  │     return [str(e)]                      │              │
│  │                                          │              │
│  │ fix_syntax(code, violations):            │              │
│  │   llm.generate("Fix syntax errors...")   │              │
│  │                                          │              │
│  │ loop.add_validator("syntax",             │              │
│  │                    validate_syntax,      │              │
│  │                    fix_syntax)           │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
│  ┌──────────────────────────────────────────┐              │
│  │ VALIDATOR 2: Linting                     │              │
│  │ validate_lint(code):                     │              │
│  │   result = subprocess.run(['flake8',...])│              │
│  │   return result.stdout.split('\n')       │              │
│  │                                          │              │
│  │ fix_lint(code, violations):              │              │
│  │   llm.generate("Fix lint errors...")     │              │
│  │                                          │              │
│  │ loop.add_validator("lint",               │              │
│  │                    validate_lint,        │              │
│  │                    fix_lint)             │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
│  ┌──────────────────────────────────────────┐              │
│  │ VALIDATOR 3: Tests                       │              │
│  │ validate_tests(code):                    │              │
│  │   result = run_tests(code)               │              │
│  │   return result.failures                 │              │
│  │                                          │              │
│  │ fix_tests(code, violations):             │              │
│  │   llm.generate("Fix failing tests...")   │              │
│  │                                          │              │
│  │ loop.add_validator("tests",              │              │
│  │                    validate_tests,       │              │
│  │                    fix_tests)            │              │
│  └──────────────────────────────────────────┘              │
│                                                             │

loop.add_validator("tests", validate_tests, fix_tests)

# Execute validation loop
code = generate_code()
result = loop.execute(code)

if result["valid"]:
    print(f"Valid after {result['iterations']} iterations")
    deploy(result["output"])
else:
    print(f"Failed: {result.get('reason', 'unfixable')}")
```

**Validation Flow Visualization**:

```
Iteration 1:
  Output: [Generated Code]
  Validation Results:
    ✗ Syntax: Missing colon on line 5
    ✗ Lint: E501 line too long (3 violations)
    ✗ Tests: test_edge_case failed
  Fixes Applied: Add colon, break lines, fix logic

Iteration 2:
  Output: [Fixed Code]
  Validation Results:
    ✓ Syntax: Pass
    ✗ Lint: E501 line too long (1 violation)
    ✗ Tests: test_edge_case failed
  Fixes Applied: Break line, adjust edge case

Iteration 3:
  Output: [Re-fixed Code]
  Validation Results:
    ✓ Syntax: Pass
    ✓ Lint: Pass
    ✓ Tests: Pass
  Result: VALID ✓
```

---

## Core Mechanics

### Loop Termination Conditions

**Critical Question**: When should a loop stop?

**Answer**: When continuing provides no value or exceeds costs

#### Termination Condition Types

```
┌─────────────────────────────────────────────────────┐
│              TERMINATION CONDITIONS                 │
│                                                     │
│  1. SUCCESS                                         │
│     Task completed, goal achieved                   │
│     Priority: Highest (desired outcome)             │
│                                                     │
│  2. QUALITY THRESHOLD                               │
│     Output good enough, further improvement minimal │
│     Priority: High (acceptable outcome)             │
│                                                     │
│  3. MAX ITERATIONS                                  │
│     Hit iteration limit                             │
│     Priority: Medium (safety limit)                 │
│                                                     │
│  4. BUDGET EXHAUSTED                                │
│     Cost/time limit reached                         │
│     Priority: High (prevent overruns)               │
│                                                     │
│  5. NO PROGRESS                                     │
│     Not improving for N iterations                  │
│     Priority: Medium (prevent waste)                │
│                                                     │
│  6. CONVERGENCE DETECTED                            │
│     Output stable, no meaningful changes            │
│     Priority: Medium (diminishing returns)          │
│                                                     │
│  7. ERROR UNRECOVERABLE                             │
│     Hit error that can't be fixed                   │
│     Priority: High (fail fast)                      │
└─────────────────────────────────────────────────────┘
```

#### Termination Decision Tree

```
                   After Iteration
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     Success?        Error?          In Progress
        │                │                │
    Return            ┌──┴──┐             │
    Success           │     │             │
                 Retriable  Fatal         │
                      │     │             │
                   Continue Fail          │
                            │             │
                    ┌───────────────┬─────┴─────┬──────────┐
                    │               │           │          │
             Budget         Max          Quality      Progress
             Exceeded?    Iterations?   Threshold?  Declining?
                    │               │           │          │
               ┌────┴───┐      ┌────┴───┐  ┌────┴───┐  ┌──┴────┐
               │        │      │        │  │        │  │       │
              Yes      No     Yes      No Yes      No Yes     No
               │        │      │        │  │        │  │       │
              Fail   Continue Fail   Continue Return Continue Continue
                                           Success  (for N?)
                                                       │
                                                   ┌───┴───┐
                                                  Yes      No
                                                   │        │
                                                  Fail   Continue
```

#### Implementation

```
┌─────────────────────────────────────────────────────────────┐
│              TERMINATION CHECKER CLASS                      │
└─────────────────────────────────────────────────────────────┘

Constructor Configuration:
├─ max_iterations: 10
├─ max_cost: $1.0
├─ quality_threshold: 0.8
└─ no_progress_limit: 3

┌─────────────────────────────────────────────────────────────┐
│        should_terminate(state) → (bool, str, bool)          │
│                    (stop?, reason, success?)                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CHECK SEQUENCE (priority order):                           │
│                                                             │
│  1. ┌──────────────────────────────┐                       │
│     │ state.success?                │                       │
│     └───────┬──────────────────────┘                       │
│            Yes → (True, 'task_completed', True)             │
│                                                             │
│  2. ┌──────────────────────────────────────┐               │
│     │ state.quality >= threshold (0.8)?    │               │
│     └───────┬──────────────────────────────┘               │
│            Yes → (True, 'quality_threshold_met', True)      │
│                                                             │
│  3. ┌──────────────────────────────────────┐               │
│     │ state.total_cost >= max_cost?        │               │
│     └───────┬──────────────────────────────┘               │
│            Yes → (True, 'budget_exhausted', False)          │
│                                                             │
│  4. ┌──────────────────────────────────────┐               │
│     │ state.iteration >= max_iterations?   │               │
│     └───────┬──────────────────────────────┘               │
│            Yes → (True, 'max_iterations', False)            │
│                                                             │
│  5. ┌──────────────────────────────────────┐               │
│     │ _no_progress(state)?                 │               │
│     └───────┬──────────────────────────────┘               │
│            Yes → (True, 'no_progress', False)               │
│                                                             │
│  6. ┌──────────────────────────────────────┐               │
│     │ _converged(state)?                   │               │
│     └───────┬──────────────────────────────┘               │
│            Yes → (True, 'converged', quality >= 0.5)        │
│                                                             │
│  7. ┌──────────────────────────────────────┐               │
│     │ state.unrecoverable_error?           │               │
│     └───────┬──────────────────────────────┘               │
│            Yes → (True, 'unrecoverable_error', False)       │
│                                                             │
│  All checks passed:                                         │
│  └─► (False, None, None) ◄─── Continue looping             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              _no_progress(state) → bool                     │
├─────────────────────────────────────────────────────────────┤
│  Purpose: Detect stagnation (no improvement in N iterations)│
│                                                             │
│  quality_history: [0.4, 0.5, 0.6, 0.62, 0.62, 0.61]        │
│                              ▲                              │
│                           baseline                          │
│                                    └─────┬─────┘            │
│                                    recent 3 values          │
│                                                             │
│  Logic:                                                     │
│  ├─ If len(history) < no_progress_limit + 1: False         │
│  ├─ baseline = history[-no_progress_limit - 1]             │
│  ├─ recent = history[-no_progress_limit:]                  │
│  └─ Return: all(score <= baseline for score in recent)     │
│                                                             │
│  Example: recent=[0.62, 0.62, 0.61], baseline=0.6          │
│  → NOT all <= baseline → False (some progress)              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              _converged(state) → bool                       │
├─────────────────────────────────────────────────────────────┤
│  Purpose: Detect convergence (output no longer changing)    │
│                                                             │
│  output_history: [out1, out2, out3, out4, out5]            │
│                                    └────┬────┘              │
│                                   last 3 outputs            │
│                                                             │
│  Logic:                                                     │
│  ├─ If len(history) < 3: False                             │
│  ├─ last_three = history[-3:]                              │
│  ├─ similarity = calculate_similarity(last_three)          │
│  └─ Return: similarity > 0.95 (95% identical)              │
│                                                             │
│  Example: Last 3 outputs very similar (95%+ match)          │
│  → True → Stop (diminishing returns)                        │
└─────────────────────────────────────────────────────────────┘
```

**Visual Termination Flow**:

```
Iteration 1: Quality=0.4, Cost=$0.10, Progress=N/A
    ↓ Continue

Iteration 2: Quality=0.5, Cost=$0.18, Progress=+0.1
    ↓ Continue

Iteration 3: Quality=0.65, Cost=$0.25, Progress=+0.15
    ↓ Continue

Iteration 4: Quality=0.75, Cost=$0.32, Progress=+0.1
    ↓ Continue

Iteration 5: Quality=0.82, Cost=$0.40, Progress=+0.07
    ↓ STOP: Quality threshold (0.8) met ✓

Result: Success after 5 iterations
```

---

### State Accumulation

**Purpose**: Remember what's been learned across iterations

**Challenge**: LLMs are stateless - each call is independent

**Solution**: Explicitly pass state in each iteration's prompt

#### What to Keep

```
┌──────────────────────────────────────────────┐
│           STATE COMPONENTS                   │
│                                              │
│  1. ATTEMPTS                                 │
│     What: Actions tried each iteration       │
│     Why: Avoid repeating same failures       │
│     Example: ["checked logs", "tested API"]  │
│                                              │
│  2. FINDINGS                                 │
│     What: Discoveries made                   │
│     Why: Build on learnings                  │
│     Example: ["error in line 50", "API OK"]  │
│                                              │
│  3. HYPOTHESES                               │
│     What: Working theories                   │
│     Why: Guide next steps                    │
│     Example: ["may be config issue"]         │
│                                              │
│  4. ERRORS                                   │
│     What: Failures encountered               │
│     Why: Inform fixes                        │
│     Example: [{"iter": 2, "error": "..."}]   │
│                                              │
│  5. METRICS                                  │
│     What: Quality/cost over time             │
│     Why: Track progress, detect convergence  │
│     Example: [{"iter": 1, "quality": 0.5}]   │
│                                              │
│  6. CONTEXT                                  │
│     What: Relevant background info           │
│     Why: Maintain continuity                 │
│     Example: {"user_goal": "...", "..."}     │
└──────────────────────────────────────────────┘
```

#### What to Discard

**Problem**: State grows unbounded → context window overflow

**Solutions**:

1. **Rolling Window**: Keep only last N iterations
2. **Summarization**: Compress old iterations
3. **Relevance Filtering**: Drop low-value info
4. **Hierarchical**: Detailed recent + summarized old

```
┌────────────────────────────────────────┐
│      STATE MANAGEMENT STRATEGIES       │
│                                        │
│  FULL STATE (all iterations)           │
│  ├─ Iteration 1: {...}                 │
│  ├─ Iteration 2: {...}                 │
│  ├─ Iteration 3: {...}                 │
│  └─ Iteration 4: {...}                 │
│  Problem: Grows unbounded              │
│                                        │
│  ROLLING WINDOW (last 3)               │
│  ├─ Iteration 1: [discarded]           │
│  ├─ Iteration 2: {...}                 │
│  ├─ Iteration 3: {...}                 │
│  └─ Iteration 4: {...}                 │
│  Benefit: Fixed size                   │
│  Tradeoff: Lose old context            │
│                                        │
│  HIERARCHICAL (summary + recent)       │
│  ├─ Iterations 1-2: [summarized]       │
│  ├─ Iteration 3: {...}                 │
│  └─ Iteration 4: {...}                 │
│  Benefit: Keep essence, detail recent  │
│  Tradeoff: Summarization cost          │
└────────────────────────────────────────┘
```

#### Memory Management

```
┌─────────────────────────────────────────────────────────────┐
│              STATE ACCUMULATOR CLASS                        │
└─────────────────────────────────────────────────────────────┘

Configuration:
├─ strategy: 'full' | 'rolling' | 'hierarchical'
├─ window_size: 3 (for rolling/hierarchical)
└─ full_history: [] (internal storage)

┌─────────────────────────────────────────────────────────────┐
│                     PUBLIC METHODS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  add_iteration(iteration_data):                             │
│  └─► full_history.append(iteration_data)                    │
│                                                             │
│  get_state_for_next_iteration():                            │
│  └─► Dispatch based on strategy:                            │
│       ├─ 'full' → _full_state()                             │
│       ├─ 'rolling' → _rolling_window()                      │
│       └─ 'hierarchical' → _hierarchical()                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              STRATEGY IMPLEMENTATIONS                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  _full_state():                                             │
│  ┌────────────────────────────────────────┐                │
│  │ Return ALL iterations                  │                │
│  │ {                                      │                │
│  │   "iterations": full_history,          │                │
│  │   "count": len(full_history)           │                │
│  │ }                                      │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  _rolling_window():                                         │
│  ┌────────────────────────────────────────┐                │
│  │ Return LAST N iterations only          │                │
│  │ recent = full_history[-window_size:]   │                │
│  │ {                                      │                │
│  │   "recent_iterations": recent,         │                │
│  │   "total_count": len(full_history)     │                │
│  │ }                                      │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  _hierarchical():                                           │
│  ┌────────────────────────────────────────┐                │
│  │ If total <= window_size:               │                │
│  │   → Use _full_state()                  │                │
│  │                                        │                │
│  │ Otherwise:                             │                │
│  │   old = full_history[:-window_size]    │                │
│  │   recent = full_history[-window_size:] │                │
│  │   summary = _summarize_iterations(old) │                │
│  │                                        │                │
│  │   Return:                              │                │
│  │   {                                    │                │
│  │     "summary": summary,                │                │
│  │     "recent_iterations": recent,       │                │
│  │     "total_count": len(full_history)   │                │
│  │   }                                    │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  _summarize_iterations(iterations):                         │
│  ┌────────────────────────────────────────┐                │
│  │ Extract key info from old iterations:  │                │
│  │ • Collect all actions                  │                │
│  │ • Collect all findings                 │
│  │ • Deduplicate both                     │                │
│  │                                        │                │
│  │ Return:                                │                │
│  │ {                                      │                │
│  │   "iterations_summarized": N,          │                │
│  │   "unique_attempts": [dedupe actions], │                │
│  │   "key_findings": [dedupe findings]    │                │
│  │ }                                      │                │
│  └────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘

Usage Example with Hierarchical Strategy:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  accumulator = StateAccumulator(strategy='hierarchical',    │
│                                 window_size=2)              │
│                                                             │
│  Iteration 1: add_iteration({                               │
│    "iteration": 1,                                          │
│    "actions": ["check logs"],                               │
│    "findings": ["error on line 50"],                        │
│    "quality": 0.3                                           │
│  })                                                         │
│                                                             │
│  Iteration 2: add_iteration({                               │
│    "iteration": 2,                                          │
│    "actions": ["check config"],                             │
│    "findings": ["config valid"],                            │
│    "quality": 0.4                                           │
│  })                                                         │
│                                                             │
│  Iteration 3: add_iteration({                               │
│    "iteration": 3,                                          │
│    "actions": ["check dependencies"],                       │
│    "findings": ["missing package X"],                       │
│    "quality": 0.6                                           │
│  })                                                         │
│                                                             │
│  ┌───────────────────────────────────────────────┐         │
│  │ For Iteration 4, get_state_for_next_iteration │         │
│  └─────────────────┬─────────────────────────────┘         │
│                    │                                        │
│                    ▼                                        │
│  {                                                          │
│    "summary": {                      ◄─── Iteration 1       │
│      "iterations_summarized": 1,         summarized        │
│      "unique_attempts": ["check logs"],                     │
│      "key_findings": ["error on line 50"]                   │
│    },                                                       │
│    "recent_iterations": [            ◄─── Iterations 2-3    │
│      {iteration: 2, ...},                  in full detail   │
│      {iteration: 3, ...}                                    │
│    ],                                                       │
│    "total_count": 3                                         │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘

Memory Management Trade-offs:
┌─────────────┬──────────────┬───────────────┬──────────────┐
│  Strategy   │ Memory Usage │  Context Loss │   Best For   │
├─────────────┼──────────────┼───────────────┼──────────────┤
│ Full        │ Grows O(N)   │ None          │ Short loops  │
│ Rolling     │ Fixed O(W)   │ Old iterations│ Long loops   │
│ Hierarchical│ O(W) + small │ Some detail   │ Most cases   │
└─────────────┴──────────────┴───────────────┴──────────────┘
```

**State in Prompt**:

```
System: You are diagnosing a test failure. This is iteration 4.

Previous attempts summary:
- Checked logs, config, dependencies
- Found: error on line 50, missing package X

Recent iterations detail:

Iteration 2:
  Action: check config
  Result: config valid
  
Iteration 3:
  Action: check dependencies
  Result: missing package X

User: Continue diagnosis. Focus on the missing package X finding.
```

---

### Iteration Design

**Goal**: Each iteration should be focused and productive

#### Iteration Prompt Structure

```
┌──────────────────────────────────────┐
│      ITERATION PROMPT TEMPLATE       │
│                                      │
│  [SYSTEM CONTEXT]                    │
│  • Role/task description             │
│  • Current iteration number          │
│  • Total iterations allowed          │
│                                      │
│  [STATE FROM PREVIOUS ITERATIONS]    │
│  • What's been tried                 │
│  • What's been learned               │
│  • Current hypotheses                │
│                                      │
│  [CURRENT FOCUS]                     │
│  • What to focus on this iteration   │
│  • Why (based on previous results)   │
│                                      │
│  [CONSTRAINTS]                       │
│  • What not to repeat                │
│  • Budget remaining                  │
│  • Time remaining                    │
│                                      │
│  [OUTPUT FORMAT]                     │
│  • Expected response structure       │
│  • Actions to take                   │
│  • Findings to report                │
└──────────────────────────────────────┘
```

#### Incorporating Feedback

**Pattern**: Analyze previous iteration → Adjust next iteration

```
┌─────────────────────────────────────────────────────────────┐
│           build_iteration_prompt(state, iteration)          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: Base Context                                       │
│  ┌───────────────────────────────────────┐                 │
│  │ You are in iteration N of MAX.        │                 │
│  │ Task: {original_task}                 │                 │
│  └───────────────────────────────────────┘                 │
│                                                             │
│  STEP 2: Previous State (if iteration > 1)                  │
│  ┌───────────────────────────────────────┐                 │
│  │ Previous iterations:                  │                 │
│  │ ┌───────────────────────────────────┐ │                 │
│  │ │ For each in recent_iterations():  │ │                 │
│  │ │   Iteration X:                    │ │                 │
│  │ │     Attempted: {action}           │ │                 │
│  │ │     Result: {result}              │ │                 │
│  │ │     Quality: {quality}            │ │                 │
│  │ └───────────────────────────────────┘ │                 │
│  └───────────────────────────────────────┘                 │
│                                                             │
│  STEP 3: Adaptive Focus (based on feedback)                 │
│  ┌───────────────────────────────────────┐                 │
│  │ If last_iteration_failed():           │                 │
│  │   → "Last iteration failed. Error: X" │                 │
│  │   → "Try a different approach"        │                 │
│  │                                       │                 │
│  │ Elif making_progress():               │                 │
│  │   → "Progress is good. Continue in    │                 │
│  │      this direction."                 │                 │
│  │                                       │                 │
│  │ Else:                                 │                 │
│  │   → "Progress has stalled. Consider   │                 │
│  │      alternative approach."           │                 │
│  └───────────────────────────────────────┘                 │
│                                                             │
│  STEP 4: Current Focus                                      │
│  ┌───────────────────────────────────────┐                 │
│  │ focus = determine_focus(state)        │                 │
│  │ "This iteration, focus on: {focus}"   │                 │
│  └───────────────────────────────────────┘                 │
│                                                             │
│  STEP 5: Constraints                                        │
│  ┌───────────────────────────────────────┐                 │
│  │ "Do not repeat: {tried_actions()}"    │                 │
│  │ "Budget remaining: ${budget_rem()}"   │                 │
│  └───────────────────────────────────────┘                 │
│                                                             │
│  Return: Complete prompt string                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│               determine_focus(state) → str                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Decision Tree:                                             │
│                                                             │
│       ┌────────────────┐                                    │
│       │ Has iterations?│                                    │
│       └───────┬────────┘                                    │
│               │                                             │
│        ┌──────┴──────┐                                      │
│        │             │                                      │
│       No            Yes                                     │
│        │             │                                      │
│        ▼             ▼                                      │
│   ┌─────────┐   ┌──────────────┐                          │
│   │"Initial │   │ Get last_it  │                          │
│   │explore" │   └──────┬───────┘                          │
│   └─────────┘          │                                   │
│                        │                                   │
│           ┌────────────┼────────────┐                      │
│           │            │            │                      │
│           ▼            ▼            ▼                      │
│      ┌────────┐  ┌─────────┐  ┌──────────┐               │
│      │found_  │  │hit_     │  │no_prog   │               │
│      │clue?   │  │error?   │  │>= 2?     │               │
│      └───┬────┘  └────┬────┘  └─────┬────┘               │
│         Yes          Yes            Yes                    │
│          │            │              │                     │
│          ▼            ▼              ▼                     │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│   │"Follow up│  │"Resolve  │  │"Try      │               │
│   │on: {clue}"│ │error: X" │  │completely│               │
│   └──────────┘  └──────────┘  │different"│               │
│                                └──────────┘               │
│           │            │            │                      │
│           └────────────┴────────────┘                      │
│                        │                                   │
│                       All No                               │
│                        │                                   │
│                        ▼                                   │
│                ┌───────────────┐                          │
│                │"Continue      │                          │
│                │ current       │                          │
│                │ investigation"│                          │
│                └───────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

**Visual Iteration Flow**:

```
Iteration 1: Explore
    ↓
  Result: Found clue X
    ↓
Iteration 2: Follow up on clue X
    ↓
  Result: Clue X leads to finding Y
    ↓
Iteration 3: Investigate finding Y
    ↓
  Result: Finding Y is root cause
    ↓
Iteration 4: Fix root cause
    ↓
  Result: Fix applied, test passes
    ↓
  Success
```

---

### Cost Control

**Problem**: Loops can be expensive (multiple LLM calls)

**Solution**: Budget tracking and optimization

#### Budget Tracking

```
┌─────────────────────────────────────────────────────────────┐
│                  BUDGET TRACKER CLASS                       │
└─────────────────────────────────────────────────────────────┘

Configuration:
├─ max_cost: $1.0 (dollar limit)
├─ max_time: 300 seconds (5 minutes)
├─ spent: $0 (accumulator)
└─ start_time: time.time() (for timeout checks)

┌─────────────────────────────────────────────────────────────┐
│                      METHODS                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  record_call(cost, tokens):                                 │
│  ┌────────────────────────────────┐                        │
│  │ spent += cost                  │                        │
│  │ Track usage for this iteration │                        │
│  └────────────────────────────────┘                        │
│                                                             │
│  remaining_cost():                                          │
│  ┌────────────────────────────────┐                        │
│  │ return max_cost - spent        │                        │
│  └────────────────────────────────┘                        │
│                                                             │
│  remaining_time():                                          │
│  ┌────────────────────────────────┐                        │
│  │ elapsed = time.time() -        │                        │
│  │           start_time           │                        │
│  │ return max_time - elapsed      │                        │
│  └────────────────────────────────┘                        │
│                                                             │
│  can_continue():                                            │
│  ┌────────────────────────────────┐                        │
│  │ Check both constraints:        │                        │
│  │ return (spent < max_cost AND   │                        │
│  │         elapsed < max_time)    │                        │
│  └────────────────────────────────┘                        │
│                                                             │
│  summary():                                                 │
│  ┌────────────────────────────────┐                        │
│  │ elapsed = time.time() -        │                        │
│  │           start_time           │                        │
│  │ return {                       │                        │
│  │   "cost": spent,               │                        │
│  │   "time": elapsed,             │                        │
│  │   "cost_remaining": remaining, │                        │
│  │   "time_remaining": remaining  │                        │
│  │ }                              │                        │
│  └────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

#### Cost Optimization Strategies

```
┌─────────────────────────────────────────────┐
│       COST OPTIMIZATION TECHNIQUES          │
│                                             │
│  1. EARLY TERMINATION                       │
│     Stop as soon as good enough             │
│     Benefit: Avoid unnecessary iterations   │
│                                             │
│  2. SMALLER MODELS FOR SIMPLE STEPS         │
│     Use Claude Haiku for validation         │
│     Use Claude Sonnet for complex reasoning │
│     Benefit: 10x cost reduction on simple   │
│                                             │
│  3. BATCH OPERATIONS                        │
│     Combine multiple checks in one call     │
│     Benefit: Reduce call overhead           │
│                                             │
│  4. CACHING                                 │
│     Cache results of expensive operations   │
│     Benefit: Avoid redundant work           │
│                                             │
│  5. PROGRESSIVE DEPTH                       │
│     Start shallow, go deep only if needed   │
│     Benefit: Pay for depth only when worth  │
│                                             │
│  6. STATE SUMMARIZATION                     │
│     Compress old state to reduce tokens     │
│     Benefit: Smaller context = lower cost   │
└─────────────────────────────────────────────┘
```

**Cost Over Iterations**:

```
Cost Per Iteration:

Iteration 1: $0.15 (full context, complex)
Iteration 2: $0.12 (cached system, medium)
Iteration 3: $0.08 (smaller model, simple validation)
Iteration 4: $0.05 (quick check)

Total: $0.40

With optimization:
Iteration 1: $0.15 (necessary)
Iteration 2: $0.06 (smaller model)
Iteration 3: TERMINATED EARLY (quality met)

Total: $0.21 (47% savings)
```

---

## Issues and Solutions

### Issue 1: Infinite Loops (Runaway Costs)

**Symptom**: Loop never terminates, costs escalate

**Causes**:
- No max iterations set
- Termination conditions never met
- Bug in termination logic

**Example**:

```
┌─────────────────────────────────────────────────────────────┐
│                    BAD: No Termination                      │
└─────────────────────────────────────────────────────────────┘

    ┌────────────────┐
    │ while True:    │  ◄──── DANGER: Infinite loop potential
    └────────┬───────┘
             │
             ▼
    ┌────────────────┐
    │ result =       │
    │ try_task()     │
    └────────┬───────┘
             │
             ▼
         ┌───────┐
         │Success?│
         └───┬───┘
             │
         ┌───┴───┐
        Yes      No
         │        │
         ▼        └──► Loop back (forever if never succeeds!)
       break
         │
         ▼
       Done

Problem: What if task never succeeds? Infinite cost!
```

**Solutions**:

1. **Always set max iterations**

```
┌─────────────────────────────────────────────────────────────┐
│                  GOOD: Hard Limit                           │
└─────────────────────────────────────────────────────────────┘

    max_iterations = 10
    
    ┌─────────────────────────────┐
    │ for i in range(max_iter):   │  ◄──── SAFE: Guaranteed stop
    └────────────┬────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ result =       │
        │ try_task()     │
        └────────┬───────┘
                 │
                 ▼
             ┌───────┐
             │Success?│
             └───┬───┘
                 │
             ┌───┴───┐
            Yes      No
             │        │
             ▼        └──► Continue to i+1 (max 10 iterations)
           break
             │
             ▼
           Done

Guarantee: Loop terminates after max 10 iterations
```

2. **Multiple exit conditions**

```
┌─────────────────────────────────────────────────────────────┐
│            BETTER: Multiple Exit Conditions                 │
└─────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────┐
    │ for i in range(max_iter):   │
    └────────────┬────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ result =       │
        │ try_task()     │
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │ Check exits:   │
        ├────────────────┤
        │ 1. Success?    │──► Yes ──► break (Success exit)
        │ 2. Budget      │
        │    exhausted?  │──► Yes ──► break (Cost limit)
        │ 3. No progress │
        │    (last 3)?   │──► Yes ──► break (Stalled)
        └────────┬───────┘
                 │
                All No
                 │
                 └──► Continue to next iteration
```

3. **Timeout as failsafe**

```
┌─────────────────────────────────────────────────────────────┐
│              BEST: Time Limit Failsafe                      │
└─────────────────────────────────────────────────────────────┘

Setup:
┌──────────────────────────────────────┐
│ import signal                        │
│                                      │
│ def timeout_handler(signum, frame):  │
│     raise TimeoutError               │
│                                      │
│ signal.signal(SIGALRM, handler)      │
│ signal.alarm(300)  # 5 min max       │
└──────────────────────────────────────┘
        │
        ▼
    ┌───────┐
    │ try:  │
    └───┬───┘
        │
        ▼
┌───────────────────────────────┐
│ for i in range(max_iter):     │  ◄──── Protected by timeout
│     result = try_task()       │
│     if should_terminate():    │
│         break                 │
└───────────────────────────────┘
        │
        ▼
    ┌──────────┐
    │ finally: │
    └─────┬────┘
          │
          ▼
┌──────────────────────┐
│ signal.alarm(0)      │  ◄──── Cancel timeout
│ (cleanup)            │
└──────────────────────┘

Safety: Even if loop logic fails, timeout kills it at 5 min
```

**Monitoring**:

```
┌─────────────────────────────────────────────────────────────┐
│                 LOOP MONITOR CLASS                          │
└─────────────────────────────────────────────────────────────┘

alert_threshold: 0.5

┌─────────────────────────────────────────────────────────────┐
│   check_iteration(iteration, max_iter, cost, max_cost)      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Calculate progress ratios:                                 │
│  ┌────────────────────────────────────┐                    │
│  │ progress = iteration / max_iter    │                    │
│  │            (how far through loop)  │                    │
│  │                                    │                    │
│  │ cost_progress = cost / max_cost    │                    │
│  │                (how much spent)    │                    │
│  └────────────────────────────────────┘                    │
│                                                             │
│  Burn rate check:                                           │
│  ┌────────────────────────────────────────┐                │
│  │ if cost_progress > progress × 1.5:     │                │
│  │   ┌──────────────────────────────────┐ │                │
│  │   │ ALERT: "Cost burn rate high"     │ │                │
│  │   │ • iteration: N                   │ │                │
│  │   │ • cost: $X                       │ │                │
│  │   │ • burn_rate: cost_progress /     │ │                │
│  │   │              progress            │ │                │
│  │   └──────────────────────────────────┘ │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  Example:                                                   │
│  Iteration 2/10 (20% progress)                              │
│  Cost $0.40/$1.00 (40% spent)                               │
│  → 40% > 20% × 1.5 (30%) → ALERT!                           │
│  → Spending too fast, may run out before completion         │
└─────────────────────────────────────────────────────────────┘
```

**Diagram**:

```
Without Safeguards:
    Try → Fail → Try → Fail → Try → Fail → ... → $$$$$

With Safeguards:
    Try → Fail → Try → Fail → Try → MAX ITERATIONS → Stop
                                                       ↓
                                                   Return Best
```

---

### Issue 2: Oscillation (Never Converging)

**Symptom**: Quality fluctuates, never stabilizes

**Causes**:
- Fixes introduce new problems
- Conflicting requirements
- Non-deterministic operations

**Example**:

```
Iteration 1: Quality = 0.6
  Fix: Improve feature A

Iteration 2: Quality = 0.5
  Fix: Broke feature B, fix B

Iteration 3: Quality = 0.6
  Fix: Broke feature A again, fix A

Iteration 4: Quality = 0.5
  Fix: Broke feature B again...

Oscillates between 0.5 and 0.6, never improving
```

**Visual**:

```
Quality Over Time (Oscillation):

100% │
     │
     │        ╱╲      ╱╲      ╱╲
 60% │       ╱  ╲    ╱  ╲    ╱  ╲
     │      ╱    ╲  ╱    ╲  ╱
 50% │     ╱      ╲╱      ╲╱
     │
   0%└──────────────────────────────
      1    2    3    4    5    6

Should detect and terminate
```

**Solutions**:

1. **Oscillation Detection**

```
┌─────────────────────────────────────────────────────────────┐
│         detect_oscillation(history, window=4)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Purpose: Detect alternating pattern in quality scores      │
│                                                             │
│  ┌──────────────────────────────────────────┐              │
│  │ If len(history) < window: return False   │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
│  Extract recent scores:                                     │
│  ┌──────────────────────────────────────────┐              │
│  │ recent = history[-window:]               │              │
│  │ scores = [h['quality'] for h in recent]  │              │
│  │                                          │              │
│  │ Example: [0.6, 0.5, 0.6, 0.5]           │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
│  Count transitions:                                         │
│  ┌──────────────────────────────────────────────┐          │
│  │ increases = count(scores[i+1] > scores[i])   │          │
│  │ decreases = count(scores[i+1] < scores[i])   │          │
│  │                                              │          │
│  │ Example: [0.6→0.5, 0.5→0.6, 0.6→0.5]        │          │
│  │ increases = 1, decreases = 2                │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  Oscillation test:                                          │
│  ┌──────────────────────────────────────────────┐          │
│  │ if abs(increases - decreases) <= 1:          │          │
│  │     return True  # Oscillating               │          │
│  │ else:                                        │          │
│  │     return False # Trending                  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  Logic: If roughly equal ups and downs, no net progress     │
└─────────────────────────────────────────────────────────────┘
```

2. **Ensemble Approach**

Instead of fixing each issue independently, accumulate all issues and fix together:

```
┌─────────────────────────────────────────────────────────────┐
│                  BAD: Sequential Fixes                      │
└─────────────────────────────────────────────────────────────┘

    issues = [issue1, issue2, issue3]
    
    ┌───────────────────────┐
    │ for issue in issues:  │
    │     output =          │
    │     fix(output, issue)│  ◄─ Each fix may break others!
    └───────────────────────┘
    
    Problem: Fix for issue1 might break issue2's fix
    Result: Oscillation between conflicting states

┌─────────────────────────────────────────────────────────────┐
│                  GOOD: Batch Fixes                          │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────┐
    │ all_issues =                 │
    │   collect_all_issues(output) │  ◄─ Gather all problems
    └──────────────┬───────────────┘
                   │
                   ▼
    ┌──────────────────────────────┐
    │ output =                     │
    │   fix_all(output, all_issues)│  ◄─ One comprehensive fix
    └──────────────────────────────┘      that resolves conflicts
    
    Benefit: Considers all issues together, avoids conflicts
```

3. **Require Consistent Improvement**

```
┌─────────────────────────────────────────────────────────────┐
│         should_continue(history, min_streak=2)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Purpose: Only continue if consistently improving           │
│                                                             │
│  ┌───────────────────────────────────────────┐             │
│  │ If len(history) < min_streak + 1:         │             │
│  │     return True  # Too early to judge     │             │
│  └───────────────────────────────────────────┘             │
│                                                             │
│  Extract recent scores:                                     │
│  ┌───────────────────────────────────────────┐             │
│  │ recent = history[-(min_streak+1):]        │             │
│  │ scores = [h['quality'] for h in recent]   │             │
│  │                                           │             │
│  │ Example (min_streak=2):                   │             │
│  │ recent = last 3 iterations                │             │
│  │ scores = [0.5, 0.6, 0.7]                  │             │
│  └───────────────────────────────────────────┘             │
│                                                             │
│  Check all transitions improving:                           │
│  ┌───────────────────────────────────────────┐             │
│  │ for i in range(len(scores)-1):            │             │
│  │     if scores[i+1] <= scores[i]:          │             │
│  │         return False  # Not improving     │             │
│  │                                           │             │
│  │ return True  # All transitions improved   │             │
│  └───────────────────────────────────────────┘             │
│                                                             │
│  Examples:                                                  │
│  [0.5, 0.6, 0.7] → True (consistent improvement)            │
│  [0.5, 0.6, 0.5] → False (declined in last step)            │
│  [0.5, 0.5, 0.6] → False (stalled in middle)                │
└─────────────────────────────────────────────────────────────┘
```

**Diagram**:

```
Oscillation Detection:

┌──────────────────────┐
│ After Each Iteration │
└──────────┬───────────┘
           │
           ▼
    ┌──────────────┐
    │ Check Last 4 │
    │ Iterations   │
    └──────┬───────┘
           │
           ▼
    ┌────────────────────────┐
    │ Quality Pattern?       │
    └──┬──────────────────┬──┘
       │                  │
  Improving          Oscillating
       │                  │
    Continue            Terminate
                          │
                    Return Best
                    of Last 4
```

---

### Issue 3: Premature Termination

**Symptom**: Loop stops before finding solution

**Causes**:
- Termination conditions too aggressive
- Max iterations too low
- Quality threshold too high
- Incorrect success detection

**Example**:

```
┌─────────────────────────────────────────────────────────────┐
│              BAD: Premature Termination                     │
└─────────────────────────────────────────────────────────────┘

Configuration:
├─ max_iterations = 2        ◄─── Too few!
└─ quality_threshold = 0.95  ◄─── Too high!

    ┌──────────────────────────┐
    │ for i in range(2):       │  ◄─── Only 2 attempts
    └─────────┬────────────────┘
              │
              ▼
    ┌───────────────────┐
    │ result = refine() │
    └─────────┬─────────┘
              │
              ▼
        ┌──────────────┐
        │ quality >=   │
        │ 0.95?        │  ◄─── Very hard to reach
        └──────┬───────┘
               │
          ┌────┴────┐
         Yes       No
          │         │
        return    continue
                    │
                    └─► Only 1 more try!

Result: Often fails to reach 0.95 in just 2 iterations
        Terminates with suboptimal result
```

**Solutions**:

1. **Calibrate Thresholds**

```
┌─────────────────────────────────────────────────────────────┐
│              GOOD: Reasonable Limits                        │
└─────────────────────────────────────────────────────────────┘

Configuration:
├─ max_iterations = 10       ◄─── Enough attempts
└─ quality_threshold = 0.8   ◄─── Achievable target

BETTER: Adaptive thresholds based on task complexity

┌─────────────────────────────────────────────────────────────┐
│        get_quality_threshold(task_complexity)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│              ┌──────────────────┐                          │
│              │ task_complexity? │                          │
│              └────────┬─────────┘                          │
│                       │                                     │
│         ┌─────────────┼─────────────┐                      │
│         │             │             │                      │
│      'simple'     'medium'      'complex'                   │
│         │             │             │                      │
│         ▼             ▼             ▼                      │
│    return 0.9   return 0.8   return 0.7                    │
│    (Higher)     (Moderate)   (Lower)                       │
│                                                             │
│  Logic: Harder tasks need lower thresholds                  │
└─────────────────────────────────────────────────────────────┘
```

2. **Graceful Degradation**

```
┌─────────────────────────────────────────────────────────────┐
│       Return best effort if perfect not achieved            │
└─────────────────────────────────────────────────────────────┘

Initialize:
├─ best = None
└─ best_quality = 0

    ┌─────────────────────────────┐
    │ for i in range(max_iter):   │
    └────────────┬────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ result =       │
        │ refine(output) │
        └────────┬───────┘
                 │
                 ▼
        ┌──────────────────┐
        │ quality better   │
        │ than best?       │
        └────┬───────┬─────┘
            Yes     No
             │       │
             ▼       └──► Skip update
        ┌─────────┐
        │ best =  │
        │ result  │
        └────┬────┘
             │
             ▼
        ┌──────────────────┐
        │ quality >=       │
        │ threshold?       │
        └────┬───────┬─────┘
            Yes     No
             │       │
             ▼       └──► Continue loop
        return result
           (Perfect!)

After loop completes:
└─► return best  (Best effort, even if < threshold)

Benefit: Always returns something useful
```

3. **User Override Option**

```
┌─────────────────────────────────────────────────────────────┐
│         Allow user to request more iterations               │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────────────┐
    │ result =             │
    │ loop.execute(task)   │
    └──────────┬───────────┘
               │
               ▼
          ┌────────┐
          │Success?│
          └───┬────┘
              │
         ┌────┴────┐
        Yes       No
         │         │
         ▼         ▼
    return    ┌────────────────────┐
    result    │ user_wants_more =  │
              │ ask_user("Quality  │
              │ not met. Continue?")│
              └─────────┬──────────┘
                        │
                   ┌────┴────┐
                  Yes       No
                   │         │
                   ▼         ▼
          ┌──────────────┐  return
          │ result =     │  result
          │ loop.execute │  (as-is)
          │ (max_iter=20)│
          └──────┬───────┘
                 │
                 ▼
              return
              result

Benefit: User controls cost/quality trade-off
```

**Comparison Table**:

| Configuration | Success Rate | Avg Iterations | Avg Cost |
|---------------|--------------|----------------|----------|
| max=2, thresh=0.95 | 30% | 2 | $0.20 |
| max=5, thresh=0.90 | 60% | 3.5 | $0.35 |
| max=10, thresh=0.80 | 85% | 5.2 | $0.52 |
| max=20, thresh=0.70 | 95% | 7.8 | $0.78 |

**Recommendation**: max=10, thresh=0.80 (sweet spot)

---

### Solutions Summary Table

| Issue | Detection | Prevention | Recovery |
|-------|-----------|------------|----------|
| **Infinite Loop** | Cost/time tracking | Max iterations, timeout | Force terminate, return best |
| **Oscillation** | Quality fluctuation pattern | Batch fixes, consistency check | Terminate, return highest quality |
| **Premature Term** | Success rate monitoring | Calibrate thresholds | Allow continuation, graceful degradation |
| **Cost Overrun** | Budget tracker | Early termination, model selection | Alert, hard stop |
| **No Progress** | Quality history | Focus adjustment | Alternative approach, escalate |

---

## Production Considerations

### ROI: When Loops Save Money vs Waste Money

#### Loop ROI Formula

```
ROI = (Value of Solution) - (Cost of Loop)

Where:
  Value of Solution = Human time saved * Hourly rate
  Cost of Loop = LLM costs + Compute costs + Developer time

Positive ROI: Value > Cost (use loop)
Negative ROI: Value < Cost (use single-shot or manual)
```

#### When Loops Save Money

**Scenario 1: Repetitive Debug Tasks**

```
Manual approach:
  Developer debugging: 2 hours @ $100/hr = $200
  
Loop approach:
  Loop cost: $2 (10 iterations @ $0.20)
  Developer review: 0.5 hours @ $100/hr = $50
  Total: $52
  
Savings: $148 (74% reduction)
```

**Scenario 2: Code Review Iterations**

```
Manual approach:
  3 review rounds, 1 hour each = 3 hours @ $100/hr = $300
  
Loop approach:
  Automated validation loop: $5
  Final human review: 0.5 hours @ $100/hr = $50
  Total: $55
  
Savings: $245 (82% reduction)
```

#### When Loops Waste Money

**Scenario 1: Simple Tasks**

```
Single-shot approach:
  One LLM call: $0.05
  
Loop approach:
  5 iterations averaging $0.10 each = $0.50
  
Waste: $0.45 (10x cost for same result)
```

**Scenario 2: Unsolvable Problems**

```
Manual approach:
  Developer identifies problem unsolvable: 0.5 hours @ $100/hr = $50
  
Loop approach:
  Loop runs to max iterations (20): $10
  Developer still has to manually solve: 1 hour @ $100/hr = $100
  Total: $110
  
Waste: $60 (120% of manual cost)
```

#### ROI Decision Matrix

```
                    Task Complexity
                Simple    Medium    Complex
              ┌─────────┬─────────┬─────────┐
   Success    │ Single  │  Loop   │  Loop   │
   Rate High  │  Shot   │  (5-10) │ (10-20) │
              ├─────────┼─────────┼─────────┤
   Success    │ Single  │ Manual  │  Loop   │
   Rate Med   │  Shot   │  or     │ (15-30) │
              │         │ Loop    │ +Manual │
              ├─────────┼─────────┼─────────┤
   Success    │ Manual  │ Manual  │ Manual  │
   Rate Low   │         │         │         │
              └─────────┴─────────┴─────────┘
```

### Monitoring Loop Behavior

**Key Metrics**:

```
┌─────────────────────────────────────────┐
│         LOOP MONITORING METRICS         │
│                                         │
│  1. Completion Rate                     │
│     % of loops that succeed             │
│     Target: >80%                        │
│                                         │
│  2. Average Iterations                  │
│     Mean iterations to completion       │
│     Track over time for degradation     │
│                                         │
│  3. Cost Per Loop                       │
│     Average $ spent per loop            │
│     Alert if spikes                     │
│                                         │
│  4. Termination Reasons                 │
│     Distribution of why loops end       │
│     Goal: Most are "success"            │
│                                         │
│  5. Quality Distribution                │
│     Final quality scores                │
│     Ensure meeting thresholds           │
│                                         │
│  6. Time to Completion                  │
│     How long loops take                 │
│     Detect slowdowns                    │
└─────────────────────────────────────────┘
```

**Monitoring Dashboard**:

```
┌────────────────── LOOP METRICS ──────────────────┐
│                                                  │
│  Last 24 Hours:                                  │
│    Total Loops: 150                              │
│    Successful: 127 (85%)                         │
│    Failed: 23 (15%)                              │
│                                                  │
│  Avg Iterations: 5.2 (↓ from 6.1 yesterday)      │
│  Avg Cost: $0.42 (↑ from $0.38 yesterday)        │
│  Avg Time: 45s                                   │
│                                                  │
│  Termination Reasons:                            │
│    Success: 127 (85%)                            │
│    Max Iterations: 15 (10%)                      │
│    Budget: 5 (3%)                                │
│    No Progress: 3 (2%)                           │
│                                                  │
│  Quality Distribution:                           │
│    >0.9: 80 (63%)                                │
│    0.8-0.9: 35 (28%)                             │
│    0.7-0.8: 12 (9%)                              │
│    <0.7: 0 (0%)                                  │
└──────────────────────────────────────────────────┘
```

**Implementation**:

```
┌─────────────────────────────────────────────────────────────┐
│                  LOOP MONITOR CLASS                         │
└─────────────────────────────────────────────────────────────┘

Data: metrics = []  (list of loop results)

┌─────────────────────────────────────────────────────────────┐
│               record_loop(loop_result)                      │
├─────────────────────────────────────────────────────────────┤
│  Append to metrics:                                         │
│  {                                                          │
│    "timestamp": time.time(),                                │
│    "success": loop_result["success"],                       │
│    "iterations": loop_result["iterations"],                 │
│    "cost": loop_result["cost"],                             │
│    "time": loop_result["time"],                             │
│    "quality": loop_result["quality"],                       │
│    "termination_reason": loop_result["reason"]              │
│  }                                                          │
│                                                             │
│  Then: _check_anomalies(loop_result)                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              _check_anomalies(result)                       │
├─────────────────────────────────────────────────────────────┤
│  recent = last 100 loops                                    │
│                                                             │
│  Check 1: High cost                                         │
│  ┌────────────────────────────────────┐                    │
│  │ if result["cost"] >                │                    │
│  │    2 × mean(recent costs):         │                    │
│  │    alert("High cost loop", result) │                    │
│  └────────────────────────────────────┘                    │
│                                                             │
│  Check 2: Nearly hit max iterations                         │
│  ┌────────────────────────────────────┐                    │
│  │ if result["iterations"] >=         │                    │
│  │    90% of max_iterations:          │                    │
│  │    alert("Nearly maxed", result)   │                    │
│  └────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│            get_dashboard(hours=24)                          │
├─────────────────────────────────────────────────────────────┤
│  Filter: recent = metrics within last N hours               │
│                                                             │
│  Calculate:                                                 │
│  ┌────────────────────────────────────────┐                │
│  │ total: count(recent)                   │                │
│  │ success_rate: count(success) / total   │                │
│  │ avg_iterations: mean(iterations)       │                │
│  │ avg_cost: mean(cost)                   │                │
│  │ avg_time: mean(time)                   │                │
│  │ termination_reasons:                   │                │
│  │   Counter of why loops ended           │                │
│  │ quality_buckets:                       │                │
│  │   _bucket_quality(recent)              │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  Return: dashboard dictionary                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│            _bucket_quality(metrics)                         │
├─────────────────────────────────────────────────────────────┤
│  buckets = {"<0.7": 0, "0.7-0.8": 0,                       │
│             "0.8-0.9": 0, ">0.9": 0}                        │
│                                                             │
│  For each metric:                                           │
│    q = metric["quality"]                                    │
│    ┌────────────────────────────┐                          │
│    │ if q < 0.7:   buckets["<0.7"] += 1                    │
│    │ elif q < 0.8: buckets["0.7-0.8"] += 1                 │
│    │ elif q < 0.9: buckets["0.8-0.9"] += 1                 │
│    │ else:         buckets[">0.9"] += 1                    │
│    └────────────────────────────┘                          │
│                                                             │
│  Return: buckets                                            │
└─────────────────────────────────────────────────────────────┘

Visual Flow:
Loop completes → record_loop() → check_anomalies() → alert if needed
                            ↓
                        metrics.append()
                            ↓
          Later: get_dashboard() → aggregate & visualize
```

### Alerting on Runaway Loops

**Alert Triggers**:

```
┌────────────────────────────────────────┐
│         ALERT CONDITIONS               │
│                                        │
│  CRITICAL                              │
│  • Loop cost > $5                      │
│  • Loop time > 10 minutes              │
│  • Infinite loop detected              │
│    Action: Force terminate             │
│                                        │
│  WARNING                               │
│  • Iteration > 80% of max              │
│  • Cost > 2x average                   │
│  • No progress for 5 iterations        │
│    Action: Consider terminating        │
│                                        │
│  INFO                                  │
│  • Quality oscillating                 │
│  • Slow convergence                    │
│    Action: Log for analysis            │
└────────────────────────────────────────┘
```

**Implementation**:

```
┌─────────────────────────────────────────────────────────────┐
│                  LOOP ALERTER CLASS                         │
└─────────────────────────────────────────────────────────────┘

Thresholds:
├─ max_cost: $5.0
├─ max_time: 600s (10 minutes)
├─ cost_multiplier: 2.0
├─ max_iteration_percent: 0.8 (80%)
└─ no_progress_limit: 5

┌─────────────────────────────────────────────────────────────┐
│              check_iteration(state) → alerts[]              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  alerts = []                                                │
│                                                             │
│  CHECK 1: Critical - High Cost                              │
│  ┌──────────────────────────────────────┐                  │
│  │ if state["cost"] > max_cost ($5):    │                  │
│  │   alerts.append({                    │                  │
│  │     "level": "CRITICAL",             │                  │
│  │     "message": "Cost $X exceeds $5", │                  │
│  │     "action": "TERMINATE"            │                  │
│  │   })                                 │                  │
│  └──────────────────────────────────────┘                  │
│                                                             │
│  CHECK 2: Critical - High Time                              │
│  ┌──────────────────────────────────────┐                  │
│  │ if state["time"] > max_time (600s):  │                  │
│  │   alerts.append({                    │                  │
│  │     "level": "CRITICAL",             │                  │
│  │     "message": "Time Xs exceeds 600s"│                  │
│  │     "action": "TERMINATE"            │                  │
│  │   })                                 │                  │
│  └──────────────────────────────────────┘                  │
│                                                             │
│  CHECK 3: Warning - Near Max Iterations                     │
│  ┌──────────────────────────────────────┐                  │
│  │ iter_percent = iteration / max       │                  │
│  │ if iter_percent > 80%:               │                  │
│  │   alerts.append({                    │                  │
│  │     "level": "WARNING",              │                  │
│  │     "message": "At X% of max iters", │                  │
│  │     "action": "MONITOR"              │                  │
│  │   })                                 │                  │
│  └──────────────────────────────────────┘                  │
│                                                             │
│  CHECK 4: Warning - No Progress                             │
│  ┌──────────────────────────────────────┐                  │
│  │ if _no_progress(state, limit=5):     │                  │
│  │   alerts.append({                    │                  │
│  │     "level": "WARNING",              │                  │
│  │     "message": "No improvement in    │                  │
│  │                 last 5 iterations",  │                  │
│  │     "action": "CONSIDER_TERMINATING" │                  │
│  │   })                                 │                  │
│  └──────────────────────────────────────┘                  │
│                                                             │
│  Send all alerts:                                           │
│  ┌──────────────────────────────────────┐                  │
│  │ for alert in alerts:                 │                  │
│  │     _send_alert(alert)               │                  │
│  └──────────────────────────────────────┘                  │
│                                                             │
│  Return: True if any alert action is "TERMINATE"            │
│         (force stop loop)                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              _send_alert(alert)                             │
├─────────────────────────────────────────────────────────────┤
│  Print: [LEVEL] message                                     │
│                                                             │
│  Production: Send to monitoring systems                      │
│  • Slack notifications                                      │
│  • PagerDuty alerts                                         │
│  • Email                                                    │
│  • Logging system                                           │
└─────────────────────────────────────────────────────────────┘
```

### Cost Optimization

**Strategies**:

1. **Model Selection**

```
┌─────────────────────────────────────────────────────────────┐
│      select_model(task_complexity, iteration)               │
├─────────────────────────────────────────────────────────────┤
│  Purpose: Choose cheapest model that can handle task        │
│                                                             │
│              ┌─────────────────┐                           │
│              │ task_complexity │                           │
│              │ or iteration?   │                           │
│              └────────┬────────┘                           │
│                       │                                     │
│         ┌─────────────┼─────────────┐                      │
│         │             │             │                      │
│      "simple"     "medium"      "complex"                   │
│    or iter>5                                                │
│         │             │             │                      │
│         ▼             ▼             ▼                      │
│   ┌─────────┐   ┌──────────┐  ┌──────────┐               │
│   │ Haiku   │   │ Sonnet   │  │  Opus    │               │
│   │$0.01/1K │   │$0.03/1K  │  │$0.15/1K  │               │
│   └─────────┘   └──────────┘  └──────────┘               │
│                                                             │
│  Strategy: Start with powerful model, switch to cheap       │
│            for later iterations (simple validation)         │
└─────────────────────────────────────────────────────────────┘
```

2. **Prompt Optimization**

```
┌─────────────────────────────────────────────────────────────┐
│                  BAD: Full State Every Time                 │
└─────────────────────────────────────────────────────────────┘
prompt = "Previous iterations:\n" +
         json.dumps(all_history, indent=2) + "\n..."

Cost: High token count (grows with each iteration)
Example: Iteration 10 includes all 10 previous iterations
         = 5000+ tokens = $0.15+

┌─────────────────────────────────────────────────────────────┐
│               GOOD: Summarize Old, Detail Recent            │
└─────────────────────────────────────────────────────────────┘
prompt = "Summary of iterations 1-5: {summary}\n" +
         "Recent iterations:\n" +
         json.dumps(recent_history) + "\n..."

Cost: Much lower token count (fixed size)
Example: Iteration 10 includes summary + last 3 iterations
         = 1500 tokens = $0.045
Savings: 70%
```

3. **Early Termination**

```
┌─────────────────────────────────────────────────────────────┐
│          Terminate as soon as good enough                   │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │ quality >=       │
    │ threshold?       │
    └────┬───────┬─────┘
        Yes     No
         │       │
         ▼       └──► Continue iterating
    ┌─────────┐
    │ return  │  ◄─── Don't waste iterations improving
    │ result  │       from 0.82 to 0.84 (diminishing returns)
    └─────────┘

Example: Threshold = 0.8
  Iteration 3: quality = 0.82 → STOP (good enough!)
  Don't run iterations 4-10 just for marginal improvement
```

4. **Caching**

```
┌─────────────────────────────────────────────────────────────┐
│              Cache expensive operations                     │
└─────────────────────────────────────────────────────────────┘

@lru_cache(maxsize=100)
def validate_code(code_hash):
    # Expensive operations:
    # • Run test suite
    # • Run linters
    # • Security scan
    return validation_results

Benefits:
┌──────────────────────────────────────────┐
│ First call for code_hash_X:   $0.05     │
│ Subsequent calls:              $0.00     │
│   (cache hit, instant return)            │
└──────────────────────────────────────────┘

Savings: 100% on repeated validations
```

**Cost Comparison**:

```
Without Optimization:
  Iteration 1: Claude Opus, full state: $0.50
  Iteration 2: Claude Opus, full state: $0.50
  Iteration 3: Claude Opus, full state: $0.50
  Iteration 4: Claude Opus, full state: $0.50
  Total: $2.00

With Optimization:
  Iteration 1: Claude Sonnet, full state: $0.10
  Iteration 2: Claude Haiku, summary: $0.03
  Iteration 3: Claude Haiku, summary: $0.03
  TERMINATE EARLY (quality met)
  Total: $0.16

Savings: $1.84 (92% reduction)
```

---

## Atiya Lens

### Atiya's Loop Implementation

**Context**: Atiya is an AI agent for diagnosing developer environment issues

**Challenge**: Diagnosis often requires multiple investigation steps, each building on previous findings

**Solution**: Diagnosis refinement loop

### Architecture

```
┌─────────────────────────────────────────────────┐
│             ATIYA DIAGNOSTIC LOOP               │
│                                                 │
│  User Issue Report                              │
│         │                                       │
│         ▼                                       │
│  ┌─────────────────┐                            │
│  │ Initial Triage  │                            │
│  │ • Parse issue   │                            │
│  │ • Classify type │                            │
│  └────────┬────────┘                            │
│           │                                     │
│           ▼                                     │
│  ┌──────────────────────────────────────┐      │
│  │    DIAGNOSTIC LOOP (max 8 iters)     │      │
│  │                                      │      │
│  │  ┌────────────────────┐              │      │
│  │  │ Generate Hypothesis│              │      │
│  │  └─────────┬──────────┘              │      │
│  │            ▼                         │      │
│  │  ┌────────────────────┐              │      │
│  │  │ Execute Tests      │              │      │
│  │  │ • Check logs       │              │      │
│  │  │ • Run commands     │              │      │
│  │  │ • Inspect config   │              │      │
│  │  └─────────┬──────────┘              │      │
│  │            ▼                         │      │
│  │  ┌────────────────────┐              │      │
│  │  │ Analyze Results    │              │      │
│  │  └─────────┬──────────┘              │      │
│  │            │                         │      │
│  │     ┌──────┴──────┐                  │      │
│  │     │             │                  │      │
│  │  Root Cause    More Data Needed      │      │
│  │  Found?        │                     │      │
│  │     │          └──► Next Iteration   │      │
│  │     ▼                                │      │
│  │  Exit Loop                           │      │
│  └──────────────────────────────────────┘      │
│           │                                     │
│           ▼                                     │
│  ┌─────────────────┐                            │
│  │ Generate Fix    │                            │
│  └────────┬────────┘                            │
│           │                                     │
│           ▼                                     │
│  ┌─────────────────┐                            │
│  │ Validate Fix    │                            │
│  └────────┬────────┘                            │
│           │                                     │
│           ▼                                     │
│  Return Solution                                │
└─────────────────────────────────────────────────┘
```

### Diagnosis Refinement Workflow

**Example Issue**: "npm install fails"

```
ITERATION 1: Initial Investigation
  Hypothesis: Missing dependencies or network issue
  Action: Check npm logs
  Result: Found "EACCES: permission denied"
  Progress: 40% (identified error type)
  Continue: Yes (need to find why permission denied)

ITERATION 2: Permission Investigation
  Hypothesis: Wrong directory ownership
  Action: Check directory permissions
  Result: Directory owned by root
  Progress: 70% (found root cause)
  Continue: Yes (need to determine fix approach)

ITERATION 3: Fix Determination
  Hypothesis: Need to change ownership or use sudo
  Action: Check if user should own directory
  Result: Yes, this is user's project directory
  Progress: 90% (know what to fix)
  Continue: Yes (need to validate fix)

ITERATION 4: Fix Validation
  Action: Propose "chown -R user:user /path"
  Validation: Safe, correct approach
  Progress: 100% (root cause found, fix validated)
  Continue: No (success)

RESULT:
  Root Cause: Directory owned by root, should be owned by user
  Fix: chown -R user:user /path/to/project
  Confidence: High
  Iterations: 4
```

### Implementation Details

```
┌─────────────────────────────────────────────────────────────┐
│            ATIYA DIAGNOSTIC LOOP CLASS                      │
└─────────────────────────────────────────────────────────────┘

Configuration:
├─ max_iterations: 8
└─ confidence_threshold: 0.85

┌─────────────────────────────────────────────────────────────┐
│               diagnose(issue_report) → result               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INITIALIZE STATE:                                          │
│  ┌────────────────────────────────────┐                    │
│  │ state = {                          │                    │
│  │   "issue": issue_report,           │                    │
│  │   "hypotheses": [],                │                    │
│  │   "findings": [],                  │                    │
│  │   "tested": [],                    │                    │
│  │   "iteration": 0                   │                    │
│  │ }                                  │                    │
│  └────────────────────────────────────┘                    │
│                                                             │
│  INITIAL TRIAGE:                                            │
│  ┌────────────────────────────────────┐                    │
│  │ triage = triage_issue(issue)       │                    │
│  │ state["category"] = triage[...]    │                    │
│  │ state["initial_hypotheses"] = [...] │                   │
│  └────────────────────────────────────┘                    │
│                                                             │
│  ┌─────────────────────────────────────────────┐           │
│  │ DIAGNOSTIC LOOP (while iter < max_iter=8)   │           │
│  │  ┌───────────────────────────────────────┐  │           │
│  │  │ iteration += 1                        │  │           │
│  │  └───────────────────────────────────────┘  │           │
│  │  ┌───────────────────────────────────────┐  │           │
│  │  │ 1. Generate Hypothesis                │  │           │
│  │  │    hypothesis = generate_hypothesis() │  │           │
│  │  │    (based on state, findings, tested) │  │           │
│  │  └───────────────────────────────────────┘  │           │
│  │  ┌───────────────────────────────────────┐  │           │
│  │  │ 2. Design & Execute Tests             │  │           │
│  │  │    tests = design_tests(hypothesis)   │  │           │
│  │  │    results = execute_tests(tests)     │  │           │
│  │  └───────────────────────────────────────┘  │           │
│  │  ┌───────────────────────────────────────┐  │           │
│  │  │ 3. Analyze Results                    │  │           │
│  │  │    analysis = analyze_results()       │  │           │
│  │  └───────────────────────────────────────┘  │           │
│  │  ┌───────────────────────────────────────┐  │           │
│  │  │ 4. Update State                       │  │           │
│  │  │    findings.extend(analysis[...])     │  │           │
│  │  │    tested.append(hypothesis)          │  │           │
│  │  └───────────────────────────────────────┘  │           │
│  │  ┌───────────────────────────────────────┐  │           │
│  │  │ 5. Check Root Cause Found?            │  │           │
│  │  └────────┬──────────────────────────────┘  │           │
│  │          Yes                                │           │
│  │           │                                 │           │
│  │           ▼                                 │           │
│  │  ┌───────────────────────────────────────┐  │           │
│  │  │ Generate & Validate Fix               │  │           │
│  │  │ fix = generate_fix(root_cause)        │  │           │
│  │  │ validation = validate_fix(fix)        │  │           │
│  │  └───────────────────────────────────────┘  │           │
│  │           │                                 │           │
│  │           ▼                                 │           │
│  │  ┌───────────────────────────────────────┐  │           │
│  │  │ RETURN SUCCESS:                       │  │           │
│  │  │ {                                     │  │           │
│  │  │   "success": True,                    │  │           │
│  │  │   "root_cause": ...,                  │  │           │
│  │  │   "fix": fix,                         │  │           │
│  │  │   "confidence": ...,                  │  │           │
│  │  │   "iterations": N,                    │  │           │
│  │  │   "diagnostic_path": findings         │  │           │
│  │  │ }                                     │  │           │
│  │  └───────────────────────────────────────┘  │           │
│  │                                             │           │
│  │          No (root cause not found)          │           │
│  │           │                                 │           │
│  │           ▼                                 │           │
│  │  ┌───────────────────────────────────────┐  │           │
│  │  │ should_continue(state)?               │  │           │
│  │  └────────┬──────────────────────────────┘  │           │
│  │          Yes                                │           │
│  │           │                                 │           │
│  │           └──► Next Iteration               │           │
│  │                                             │           │
│  │          No (or max iterations)             │           │
│  │           │                                 │           │
│  │           ▼ Break loop                      │           │
│  └─────────────────────────────────────────────┘           │
│                                                             │
│  RETURN FAILURE:                                            │
│  ┌────────────────────────────────────┐                    │
│  │ {                                  │                    │
│  │   "success": False,                │                    │
│  │   "findings": state["findings"],   │                    │
│  │   "iterations": N,                 │                    │
│  │   "reason": "max_iterations" or    │                    │
│  │             "low_confidence"       │                    │
│  │ }                                  │                    │
│  └────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│           HELPER METHODS (LLM-powered)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  generate_hypothesis(state):                                │
│  ┌────────────────────────────────────────┐                │
│  │ Prompt LLM with:                       │                │
│  │ • Issue description                    │                │
│  │ • Category                             │                │
│  │ • Previous findings                    │                │
│  │ • Already tested hypotheses            │                │
│  │ → Returns: Next hypothesis to test     │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  design_tests(hypothesis):                                  │
│  ┌────────────────────────────────────────┐                │
│  │ Prompt LLM with hypothesis             │                │
│  │ → Returns: List of tests:              │                │
│  │   • Commands to run                    │                │
│  │   • Files to check                     │                │
│  │   • Logs to examine                    │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  execute_tests(tests):                                      │
│  ┌────────────────────────────────────────┐                │
│  │ For each test:                         │                │
│  │   If type=="command":                  │                │
│  │     subprocess.run(command)            │                │
│  │     collect stdout, stderr, returncode │                │
│  │   If type=="file_check":               │                │
│  │     read_file(path)                    │                │
│  │     collect content                    │                │
│  │ → Returns: All test results            │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  analyze_results(results, state):                           │
│  ┌────────────────────────────────────────┐                │
│  │ Prompt LLM with:                       │                │
│  │ • Test results                         │                │
│  │ • Previous findings                    │                │
│  │ Questions:                             │                │
│  │ 1. What do results tell us?            │                │
│  │ 2. Found root cause?                   │                │
│  │ 3. What to investigate next?           │                │
│  │ 4. Confidence level (0-1)?             │                │
│  │ → Returns: Analysis with confidence    │                │
│  └────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### Results and Metrics

**Production Metrics** (based on 1000 diagnoses):

```
┌───────────────────────────────────────────┐
│      ATIYA DIAGNOSTIC LOOP METRICS        │
│                                           │
│  Success Rate: 87%                        │
│    • Root cause found: 870/1000           │
│    • Partial diagnosis: 95/1000           │
│    • No diagnosis: 35/1000                │
│                                           │
│  Average Iterations: 3.8                  │
│    • Single iteration: 15%                │
│    • 2-3 iterations: 45%                  │
│    • 4-6 iterations: 30%                  │
│    • 7-8 iterations: 10%                  │
│                                           │
│  Average Time: 45 seconds                 │
│  Average Cost: $0.32                      │
│                                           │
│  Top Issue Categories:                    │
│    • Permission errors: 25%               │
│    • Dependency issues: 20%               │
│    • Configuration errors: 18%            │
│    • Network issues: 15%                  │
│    • Other: 22%                           │
│                                           │
│  User Satisfaction: 4.3/5                 │
└───────────────────────────────────────────┘
```

**Iteration Distribution**:

```
Number of Cases:
300 │     ███
    │     ███
250 │     ███
    │     ███     ███
200 │     ███     ███
    │     ███     ███
150 │ ███ ███     ███ ███
    │ ███ ███     ███ ███
100 │ ███ ███     ███ ███ ███
    │ ███ ███     ███ ███ ███
 50 │ ███ ███     ███ ███ ███ ███
    │ ███ ███     ███ ███ ███ ███ ███
  0 └─────────────────────────────────
      1   2-3     4-6     7-8    Max
           Iterations to Solution
```

**ROI Analysis**:

```
Without Atiya (Manual Debug):
  Average developer time: 30 minutes
  Developer rate: $100/hr
  Cost per issue: $50

With Atiya Loop:
  Average Atiya time: 45 seconds
  Average cost: $0.32
  Developer review: 5 minutes @ $100/hr = $8.33
  Total: $8.65

Savings per Issue: $41.35 (83% reduction)
Annual Savings (1000 issues): $41,350
```

### Lessons Learned

**What Works**:
1. Iterative investigation finds root causes manual debugging might miss
2. State accumulation prevents re-checking same things
3. Hypothesis-driven testing is more efficient than random exploration
4. 8 iteration limit is sweet spot (rarely need more, prevents runaway)

**What Doesn't**:
1. Trying to solve in one iteration (too complex)
2. Not tracking what's been tested (wastes iterations)
3. Continuing past 8 iterations (diminishing returns)
4. Skipping fix validation (leads to ineffective solutions)

**Optimizations Applied**:
1. Use cheaper model (Haiku) for test execution, Sonnet for analysis
2. Cache common diagnoses to avoid full loop
3. Early termination when high confidence reached (don't waste iterations)
4. Parallel test execution when tests are independent

---

## Summary

### Key Takeaways

```
┌─────────────────────────────────────────────────────────┐
│                  LOOP ENGINEERING ESSENCE               │
│                                                         │
│  1. LOOPS ENABLE ITERATION                              │
│     Single-shot fails on complex tasks                  │
│     Loops allow refinement and exploration              │
│                                                         │
│  2. FOUR CORE PATTERNS                                  │
│     • Retry: Keep trying until success                  │
│     • Refinement: Improve quality each iteration        │
│     • Search: Explore to find best option               │
│     • Validation: Check-fix-check cycle                 │
│                                                         │
│  3. THREE CRITICAL COMPONENTS                           │
│     • Iteration: What happens each cycle                │
│     • State: What we remember                           │
│     • Termination: When to stop                         │
│                                                         │
│  4. MUST HAVE SAFEGUARDS                                │
│     • Max iterations (prevent infinite loops)           │
│     • Budget limits (prevent cost overruns)             │
│     • Progress detection (stop if not improving)        │
│     • Oscillation detection (stop if fluctuating)       │
│                                                         │
│  5. PRODUCTION ESSENTIALS                               │
│     • Monitor metrics (success rate, cost, time)        │
│     • Alert on anomalies (runaway loops, high cost)     │
│     • Optimize costs (model selection, early term)      │
│     • Measure ROI (ensure loops add value)              │
└─────────────────────────────────────────────────────────┘
```

### When to Use Loops

```
USE LOOPS WHEN:
✓ Task is complex (multi-step reasoning required)
✓ First attempt often fails (validation catches issues)
✓ Quality improves with iteration (refinement possible)
✓ Exploration needed (solution not obvious)
✓ Autonomy valuable (reduce human intervention)

DON'T USE LOOPS WHEN:
✗ Task is simple (single-shot works)
✗ First attempt usually succeeds (loop overhead not worth it)
✗ Iteration doesn't help (quality doesn't improve)
✗ Solution is deterministic (no exploration needed)
✗ Real-time response required (latency too high)
```

### Loop Engineering Checklist

```
□ Define clear success criteria
□ Set max iterations (typically 5-10)
□ Implement budget tracking
□ Design state accumulation strategy
□ Build multiple termination conditions
□ Add progress monitoring
□ Implement oscillation detection
□ Add cost optimization
□ Set up metrics collection
□ Configure alerts for anomalies
□ Test with edge cases
□ Measure ROI
```

### Anti-Patterns to Avoid

```
❌ No max iterations (infinite loop risk)
❌ Only one exit condition (no safety net)
❌ Not tracking state (repeat same actions)
❌ No cost monitoring (surprise bills)
❌ Ignoring no-progress (wasting iterations)
❌ Too aggressive thresholds (premature termination)
❌ Using expensive model for everything (cost overrun)
❌ Not monitoring metrics (blind to issues)
```

### Further Reading

- **Retry Patterns**: Exponential backoff, circuit breakers, bulkheads
- **Search Algorithms**: A*, beam search, Monte Carlo tree search
- **Reinforcement Learning**: Loop as RL problem (state, action, reward)
- **Prompt Engineering**: Chain-of-thought, tree-of-thought, self-consistency
- **Production AI**: Observability, cost management, failure handling

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-20  
**Author**: AI Learning System  
**Target**: Production AI Engineers  

**Lines**: ~2,800

---
