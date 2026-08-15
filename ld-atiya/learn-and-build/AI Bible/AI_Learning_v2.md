# AI/Agentic Systems & Claude Code - Complete Learning Path

**Systematically Organized for Progressive Learning**

Total Content: 28 Broad Skills | 400+ AI/Agentic Subskills | 103 Claude Code Topics

---

## 📚 Learning Path Overview

This curriculum is designed for **14-week progressive mastery**, moving from fundamentals to production deployment.

### Learning Phases:
- **Phase 1** (Weeks 1-2): Foundations - LLMs, Prompts, Basic Agents
- **Phase 2** (Weeks 3-4): Core Agent Patterns - Integration, State, Profiles
- **Phase 3** (Weeks 5-6): Multi-Agent Systems - Orchestration, Routing
- **Phase 4** (Weeks 7-8): Advanced Features - RAG, Embeddings, Diagnostic Loops
- **Phase 5** (Weeks 9-10): Production & Optimization - Caching, Cost, Observability
- **Phase 6** (Weeks 11-12): Quality & Safety - Testing, Evaluation, Security
- **Phase 7** (Weeks 13-14): Deployment & Scale - Backend, CI/CD, Automation

🔷 = Claude Code practical implementation topics

---

═══════════════════════════════════════════════════════════════════
## PHASE 1: FOUNDATIONS (WEEKS 1-2)
═══════════════════════════════════════════════════════════════════

**Goal**: Understand LLMs, prompts, structured outputs, and basic agent interaction

---

### 1. Model/Provider Abstraction and Fallback
**Learn First**: Understand what models are, how to select them, and handle failures

Required Technical Subskills:
- Unified Model Gateway
- Provider Adapter Pattern
- Capability-Aware Model Routing
- Cost- and Latency-Aware Routing
- Retry, Backoff, and Circuit Breaking
- Rate-Limit and Quota Management
- Fallback Policies and Graceful Degradation
- Model and Configuration Versioning
- Multi-Model Routing
- Task-Specific Model Selection
- Embedding/Judge/Synthesis Model Separation
- Partial-Result Preservation
- Optional-Dependency Failure Isolation

🔷 CLAUDE CODE: Model Selection & API Fundamentals
- Claude 4.X model family (Opus 4.7, Sonnet 4.6, Haiku 4.5)
- Model selection for different tasks
- Fast mode with Opus 4.6
- Claude API fundamentals and SDK usage
- Message Batches API (50% cost savings, 24-hour processing)
- Tradeoffs: real-time vs. batch processing
- Claude Code platforms (CLI, Desktop, Web, IDE extensions)

---

### 2. LLM Integration, Prompt Engineering, and Agent Profiles
**Learn Second**: Master how to communicate with LLMs effectively

Required Technical Subskills:
- LLM API Integration
- System-Prompt Design
- User-Prompt Design
- System/User Prompt Separation
- Explicit Output-Format Instructions
- Few-Shot Learning
- Explicit Constraints
- Evidence-Only Instructions
- Hallucination Prevention
- Insufficient-Data Handling
- Evidence-Citation Rules
- Confidence-Threshold Instructions
- Agent Profiles
- Profile-versus-Prompt Separation
- Agent Behavior Equation
- Capability-versus-Behavior Separation
- Deterministic Profile Selection
- Profile Identity
- Profile Objective
- Profile Scope
- Profile Inputs
- Evidence Policy
- Reasoning Procedure
- Output Contract
- Profile Guardrails
- Profile Confidence Rubric
- Profile Examples
- Profiles as Policies
- Version-Controlled Profiles
- Profile Loading
- Profile Caching
- Profile Restart Behavior
- Per-Step Prompt Templates

🔷 CLAUDE CODE: Prompt Engineering & Best Practices
- Few-shot prompting techniques
- Multi-pass review systems
- Task Decomposition Strategies
- Plan mode vs. direct execution workflows
- Plan mode for implementation planning
- Custom slash command development (Skills)
- Skill creation, management, and frontmatter
- Skill parameters and arguments
- Plugins: architecture, installation, development
- Confidence calibration in agentic systems
- Anti-pattern: Prompt-based enforcement (use programmatic validation)
- Anti-pattern: Self-reported confidence for routing (use deterministic thresholds)

---

### 3. Structured LLM Outputs and Validation
**Learn Third**: Control LLM responses with schemas and validation

Required Technical Subskills:
- JSON Schema Design
- Typed Models with Pydantic
- Strict Schema-Constrained Generation
- Tool-Call Argument Validation
- Semantic Output Validation
- Retry and Repair Loops
- Schema Versioning
- Evidence and Provenance Fields
- Typed Findings
- Typed Agent Handoffs
- Runtime Type Validation
- JSON Serialization and Deserialization
- Structured FORM Outputs
- Structured ANALYZE Outputs
- Structured SYNTHESIZE Outputs

🔷 CLAUDE CODE: Structured Output & Validation
- JSON schema enforcement for structured output
- --output-format json and --json-schema flags
- Validation-retry loop architecture
- Semantic vs. syntax validation
- Programmatic validation layering
- Agentic Loop Pattern: send request → check stop_reason → execute tool → return result → repeat
- Stop reason evaluation and branching logic

---

### 4. Agent Observability and Experiment Tracking
**Learn Fourth**: Monitor and understand agent behavior from the start

Required Technical Subskills:
- End-to-End Trace Instrumentation
- Prompt and Model Version Tracking
- Tool-Call and Handoff Tracing
- Token, Cost, and Latency Telemetry
- Error, Retry, and Fallback Classification
- Session and State Inspection
- Experiment Run Comparison
- Evaluation Dashboards
- Decision-Level Logging
- Audit Trail
- Actor and Timestamp Attribution
- Introspection APIs
- RAG Usage Telemetry
- Progress Visibility
- Triage History

🔷 CLAUDE CODE: Tool Design & Execution Tracking
- Model Context Protocol (MCP) fundamentals
- Three core MCP primitives: tools, resources, and prompts
- Tool description optimization for Claude selection
- .mcp.json configuration and server setup
- MCP server implementation (Python/TypeScript)
- Tool scoping per agent role
- Read, Edit, Write, Bash tools in Claude Code
- Tool permission management
- Parallel vs sequential tool execution
- Tool result handling and error responses

---

═══════════════════════════════════════════════════════════════════
## PHASE 2: CORE AGENT PATTERNS (WEEKS 3-4)
═══════════════════════════════════════════════════════════════════

**Goal**: Build stateful, reliable agents with proper lifecycle management

---

### 5. Agent State Management and Lifecycle
**Learn Fifth**: Manage agent state across interactions

Required Technical Subskills:
- Persistent State Management
- Centralized Database State
- Intermediate-Result Persistence
- Restart-Safe Pending Work
- Status Transitions
- State-Machine Design
- Resume Capability
- Approval-State Persistence
- Agentic State Across Iterations
- Iteration History
- Evidence-Chain State
- Confidence-State Tracking
- Best-Hypothesis State
- Run-to-Triage Relationships

🔷 CLAUDE CODE: Context & Session Management
- Session state management across agent interactions
- Long-context preservation strategies
- Memory system: user, feedback, project, reference types
- Memory indexing with MEMORY.md
- Memory versioning and updates
- Context preservation across sessions
- Context compression strategies
- Information provenance tracking
- Auto memory for persistent learning
- CLAUDE.md hierarchy (project-level architecture rulebook)
- .claude/rules/ glob patterns and rule enforcement
- Anti-pattern: Larger context windows for attention problems (use focused passes)

---

### 6. Evidence Synthesis and Confidence Reasoning
**Learn Sixth**: Make decisions based on evidence

Required Technical Subskills:
- Multi-Source Evidence Synthesis
- colo-auto Evidence Integration
- Infra Pulse Evidence Integration
- colo-diag Evidence Integration
- RAG Evidence Integration
- Conflicting-Evidence Handling
- Evidence Prioritization
- Evidence-Chain Construction
- Grounded Root-Cause Analysis
- Confidence Scoring
- Confidence Calibration
- Best-Hypothesis Selection
- Strongest-Evidence Tracking
- Capability-Gap Acknowledgment
- Actionable Recommendation Generation
- Per-Hypothesis Analysis
- Final Cross-Iteration Synthesis
- ANALYZE-versus-SYNTHESIZE Separation

---

### 7. Prompt Caching and Token/Context Optimization
**Learn Seventh**: Optimize cost and performance early

Required Technical Subskills:
- Prompt Caching
- Cacheable System-Prompt Blocks
- Cacheable Agent Profiles
- Prompt-Cache Expiration
- Prompt-Cache TTL
- Cache-Hit Tracking
- Cache-Miss Tracking
- Sequential Cache Priming
- Periodic Cache Warming
- Cache-Hit-Rate Optimization
- Input-Token Tracking
- Output-Token Tracking
- Cached-Token Tracking
- Per-Request Cost Attribution
- Response Truncation
- Token-Budget Control
- Context-Budget Management
- Tiered Context Extraction
- Full Evidence Storage
- Summarized Evidence Storage
- Context Compression
- Bounded Iteration Cost
- Parallelism-versus-Cache Trade-Off

🔷 CLAUDE CODE: Cost Optimization & Caching
- Cost optimization through prompt caching
- Prompt caching for production optimization
- Token consumption monitoring
- Cost vs. latency tradeoffs
- Production reliability and SLA management
- Resource definition and access patterns (MCP)
- Prompt template distribution via MCP

---

### 8. Human-in-the-Loop and Controlled Execution
**Learn Eighth**: Add safety gates and human oversight

Required Technical Subskills:
- Human-in-the-Loop
- Human Approval Gates
- Awaiting-Approval State
- Approve and Reject Workflow
- Guarded Execution
- Defense-in-Depth Checks
- Execution Preconditions
- Duplicate Execution Prevention
- Classification Guards
- State Guards
- Fix-Prompt Validation
- Side-Effect Authorization
- Human Accountability

🔷 CLAUDE CODE: Permission & Safety Controls
- Permission modes and settings
- Permission prompts and user approval
- Allowlist configuration for common operations
- Sandbox mode for safe execution
- Dangerous operation handling
- Git safety protocols (no force push, no --no-verify)
- Pre-commit hook compliance
- Security vulnerability prevention (XSS, SQL injection, etc.)
- Deterministic escalation logic (non-confidence-based)
- Edge case routing and human escalation

---

### 9. Error Normalization, Deduplication, and Analysis Caching
**Learn Ninth**: Handle errors intelligently

Required Technical Subskills:
- Hash Matching
- Error Deduplication
- Error Normalization
- Timestamp Masking
- Dynamic ID Masking
- Line-Number Masking
- Error Fingerprinting
- SHA-256 Error Hashing
- Folder-and-Testcase Cache
- Error-Hash Cache
- Cached Analysis Reuse
- Duplicate-Triage Detection
- Stable Cache-Key Design

---

═══════════════════════════════════════════════════════════════════
## PHASE 3: MULTI-AGENT SYSTEMS (WEEKS 5-6)
═══════════════════════════════════════════════════════════════════

**Goal**: Design systems with multiple specialized agents working together

---

### 10. Deterministic-First Agent Architecture
**Learn Tenth**: Optimize with rules before using LLMs

Required Technical Subskills:
- Deterministic-First Architecture
- Rule-Based Preprocessing
- LLM-as-Last-Resort Gating
- Regex-Based Classification
- Regex and YAML Bucket Detection
- No-LLM Skill Execution
- No-LLM API Execution
- Deterministic Profile Selection
- Pre-LLM Cost Optimization
- Pre-LLM Latency Optimization
- Deterministic Cache Checks
- Deterministic Workflow Control

---

### 11. Classification-Aware Routing
**Learn Eleventh**: Route requests intelligently based on classification

Required Technical Subskills:
- Classification-Aware Routing
- Route-Before-Analyze
- Bucket-Aware Routing
- Classification-Specific Workflows
- Evidence-Source Routing
- Conditional Tool Invocation
- Approval-Path Routing
- No-LLM versus LLM Path Selection
- RAG Eligibility Gating
- SAAS_INFRA Routing
- SAAS_INFRA_DEEP Routing
- CLEANUP Routing
- OTHER-Bucket Routing

---

### 12. Sub-Agent Architecture and Orchestration
**Learn Twelfth**: Build multi-agent systems with orchestration

Required Technical Subskills:
- Specialized Sub-Agent Architecture
- Lightweight Orchestrator Pattern
- Orchestrator-versus-Specialist Responsibility Separation
- Tool-Scoped Specialists
- Context and Tool Minimization
- Conditional Sub-Agent Invocation
- Typed Inter-Agent Communication
- Multi-Service Evidence Gathering
- Skill Invocation
- API-Based Agent Invocation
- Monolith Decomposition

🔷 CLAUDE CODE: Multi-Agent Orchestration
- Hub-and-Spoke Orchestration with central coordinator
- Coordinator-Subagent Patterns and task delegation
- Multi-Agent System Design and communication topology
- Agent types: general-purpose, Explore, Plan, code-reviewer
- Explore subagent: quick, medium, very thorough modes
- Background agent execution and parallel spawning
- Agent isolation with worktrees (context: fork)
- Foreground vs background agent execution
- Agent resumption and continuation
- Subagent error handling and propagation
- Context window forking for subagent isolation
- Token consumption isolation per subagent
- Agent-to-agent handoff patterns
- Anti-pattern: Flat multi-agent topology (use hub-and-spoke instead)
- Anti-pattern: Universal tool availability (scope tools to agent roles)

---

### 12A. CrewAI Multi-Agent Framework
**Learn After Sub-Agent Architecture**: Role-based multi-agent orchestration

**Core Concepts:**
- Mental model: Film crew with specialized roles
- Agent = specialist (role, goal, backstory)
- Task = unit of work (description, expected_output, agent)
- Crew = orchestrator (agents + tasks + process)
- Architecture layer: Orchestration (between LLM and Tools)

**Agent Design:**
- Role, goal, backstory (persona-driven)
- Tools assignment (list of @tool or BaseTool)
- Verbose mode for debugging
- Memory enablement (short-term, long-term, entity)
- Delegation capability (allow_delegation)
- Max iterations and retry limits
- Rate limiting (max_rpm)
- Cache control for tool results
- Custom system/prompt templates

**Task Configuration:**
- Description with placeholders ({variable})
- Expected output specification
- Agent assignment
- Context chaining (context=[prior_tasks])
- Structured output (output_pydantic, output_json)
- Output file writing
- Human-in-the-loop (human_input=True)
- Async execution
- Task-specific tools override
- Callbacks on completion

**Crew Orchestration:**
- Process types: Sequential, Hierarchical, Consensual
- kickoff() method and inputs
- CrewOutput handling (raw, pydantic, json_dict, tasks_output, token_usage)
- Memory system (crew-level)
- Planning mode
- Manager LLM/agent for hierarchical
- Global rate limiting
- Output logging
- Telemetry sharing

**LLM Integration:**
- LiteLLM wrapper (100+ providers)
- Configuration patterns (direct, proxy, env vars)
- Model selection (temperature, max_tokens, top_p)
- Timeout and retry configuration
- Provider adapter pattern

**Process Types:**
- Sequential: Linear pipeline (default)
- Hierarchical: Manager delegates dynamically
- Consensual: Multi-agent review and discussion
- Trade-offs: predictability vs adaptability vs cost

**Tools:**
- @tool decorator for simple functions
- BaseTool class for complex tools
- Built-in tools (SerperDev, ScrapeWebsite, FileRead, etc.)
- MCP integration (Model Context Protocol)
- Tool description optimization
- Error response structure

**Memory System:**
- Short-term memory (working memory within run)
- Long-term memory (lessons across runs)
- Entity memory (tracking people, systems, projects)
- Unified Memory API
- When to use memory (repeated executions vs one-shot)

**Advanced Features:**
- Agent delegation patterns
- Task callbacks
- Human input gates
- Structured output with Pydantic
- Async task execution
- Context chaining best practices

**Common Patterns:**
- Linear pipeline (analyze → investigate → remediate → communicate)
- Fan-out/fan-in (parallel work, then synthesize)
- Review chain (author → reviewer → revise)
- Escalation (junior → senior routing)

**Production Considerations:**
- Token cost estimation (~15-25K tokens for 4-agent pipeline)
- Error handling and retries
- Debugging with verbose mode
- Security and tool scoping
- Rate limiting strategies
- Production maturity (12M+ daily executions)

---

### 12B. LangGraph State Machine Framework
**Learn After CrewAI**: Graph-based multi-actor orchestration

**Core Concepts:**
- Mental model: Flowchart with functions and typed state
- State = TypedDict (shared whiteboard)
- Node = function (takes state, returns updates)
- Edge = connection (unconditional or conditional)
- Compile = validates graph, produces runnable

**State Management:**
- Typed state with TypedDict
- Explicit state fields (all data visible)
- State updates via node return values
- Partial updates (only changed fields)
- State persistence with checkpointers
- SQLite/Postgres backends
- Time-travel debugging capability

**Node Functions:**
- Plain Python functions
- Takes state as input
- Returns dict of updates
- LLM calls within nodes
- Manual prompt construction
- More control, more responsibility

**Edge Types:**
- Regular edges (always execute next)
- Conditional edges (routing function decides)
- Entry point (first node)
- Finish point (terminal nodes)
- Loops and cycles (with termination conditions)

**Graph Building:**
- StateGraph(StateClass) initialization
- add_node(name, function)
- add_edge(source, destination)
- add_conditional_edges(source, router_fn, mapping)
- set_entry_point(node)
- set_finish_point(node)
- compile() validation

**Execution:**
- invoke(initial_state) to run
- Returns final state dict
- Interrupt patterns (interrupt_before, interrupt_after)
- Stream mode for real-time updates
- Checkpointing for resumability

**LLM Integration:**
- ChatOpenAI with LiteLLM proxy
- OpenAI-compatible API
- Model configuration (temperature, tokens)
- Direct LLM invocation in nodes
- Tool binding patterns

**Patterns:**
- Linear pipeline (sequential nodes)
- Conditional routing (severity-based branching)
- Human-in-the-loop (input() in nodes or interrupts)
- Loops/retry (cycle back to previous nodes)
- Parallel branches (fan-out execution)
- Subgraphs (nested workflows)

**Advanced Features:**
- Conditional routing based on state
- Loop detection and max iterations
- Human approval gates
- State persistence for long-running tasks
- Multi-step resumption
- Parallel node execution
- Error propagation patterns

**Debugging:**
- LangSmith traces
- State inspection at any point
- Time-travel debugging
- Graph visualization
- Explicit data flow

**Production Considerations:**
- State management overhead
- Checkpointer configuration
- Error handling strategies
- Graph validation at compile time
- Integration with LangChain ecosystem
- Battle-tested at LangChain scale

**CrewAI vs LangGraph Comparison:**
- Mental model: Roles/personas vs Functions/state
- Learning curve: Easy vs Moderate
- Data flow: Context parameter vs Typed state
- Conditional logic: Limited vs First-class
- State management: Implicit vs Explicit
- Use CrewAI for: 3-5 agents, linear pipelines, quick prototypes
- Use LangGraph for: Complex branching, loops, approval gates, explicit state

---

### 13. Evidence Classification and Loop Termination
**Learn Thirteenth**: Know when to stop iterating

Required Technical Subskills:
- EVIDENCE_FOUND Classification
- CONFIRMED Classification
- REFUTED Classification
- INCONCLUSIVE Classification
- CAPABILITY_GAP Classification
- Confidence Updates from Evidence
- High-Confidence Termination
- Maximum-Iteration Termination
- Hypotheses-Exhausted Termination
- All-Paths-Blocked Termination
- Termination-Reason Tracking
- Termination-Aware Final Synthesis
- Bounded-Cost Termination
- Infinite-Loop Prevention

🔷 CLAUDE CODE: Error Handling & Reliability
- Error response structure (isError, isRetryable, errorCategory)
- Error propagation across multi-agent systems
- Silent failure prevention
- Anti-pattern: Silent failures on subagent errors (return structured error context)
- Tool delegation and execution flow
- Git commit workflows and pull request creation
- Pre-commit hook failure handling
- Retry logic and graceful degradation

---

═══════════════════════════════════════════════════════════════════
## PHASE 4: ADVANCED FEATURES (WEEKS 7-8)
═══════════════════════════════════════════════════════════════════

**Goal**: Implement RAG, embeddings, and sophisticated diagnostic patterns

---

### 14. Retrieval-Augmented Generation and Knowledge Grounding
**Learn Fourteenth**: Enhance agents with external knowledge

Required Technical Subskills:
- Retrieval-Augmented Generation
- Grounded Generation
- Optional RAG
- Additive RAG
- Classification-Based RAG Enablement
- Context Injection
- Reference Documentation Injection
- Retrieval-Context Assembly
- Source Attribution
- Direct-Relevance Citation
- No-Relevant-Context Abstention
- Skip-RAG Fallback
- RAG-Augmented Chat Interface
- RAG Usage Tracking
- Retrieved-Chunk Citation Tracking

---

### 15. Embeddings, Vector Databases, and Semantic Retrieval
**Learn Fifteenth**: Build the foundation for semantic search

Required Technical Subskills:
- Embedding Generation
- Query Embeddings
- Document Embeddings
- Dense Vector Representations
- Semantic Similarity
- Embedding-Model Selection
- Batch Embedding
- Vector Database Design
- PostgreSQL pgvector
- Vector Schema Design
- Vector Indexing
- Cosine Similarity
- Top-K Retrieval
- Approximate Nearest-Neighbor Search
- Metadata Filtering
- Semantic Search
- Keyword-versus-Semantic Search
- Vector-Distance Ranking

---

### 16. RAG Relevance Gating and Retrieval-Quality Control
**Learn Sixteenth**: Ensure retrieved content is actually relevant

Required Technical Subskills:
- Gated RAG
- Two-Stage Retrieval
- Cosine Candidate Retrieval
- Soft Similarity Thresholds
- LLM Relevance Judge
- Per-Chunk Binary Relevance Classification
- Topic-Similarity-versus-Task-Relevance Detection
- Early Stopping after Sufficient Relevant Chunks
- Skip-RAG Decision
- Irrelevant-Context Rejection
- Retrieval Precision Control
- Retrieval Cost Control
- Retrieval Latency Control

---

### 17. Knowledge Ingestion, Chunking, Indexing, and Freshness
**Learn Seventeenth**: Build and maintain knowledge bases

Required Technical Subskills:
- Model Context Protocol
- Smart MCP
- MCP-versus-Per-Query Access
- Offline Indexing
- Scheduled Knowledge Ingestion
- Local Hot-Path Retrieval
- Confluence Document Ingestion
- Document Chunking
- Fixed-Size Chunking
- Sentence-Based Chunking
- Paragraph-Based Chunking
- Recursive Chunking
- Chunk Overlap
- Chunk-Size Optimization
- Indexing Pipelines
- Incremental Indexing
- Content Hashing
- Staleness Detection
- Document Change Detection
- Selective Re-Chunking
- Selective Re-Embedding
- Source Metadata
- Document Provenance
- Scheduled Re-Indexing

---

### 18. Agentic Diagnostic Loops
**Learn Eighteenth**: Build agents that investigate iteratively

Required Technical Subskills:
- Agentic Loops
- FORM-Hypothesis Step
- Diagnostic Query Generation
- Diagnostic Tool Execution
- ANALYZE Step
- DECIDE Step
- Loop-or-Conclude Decision
- SYNTHESIZE Step
- Progressive Refinement
- Adaptive Investigation
- Controlled Exploration
- Evidence Accumulation
- Multi-Iteration Reasoning
- Bounded Maximum Iterations
- Single-Pass-versus-Iterative Diagnosis
- Multi-Root-Cause Exploration
- Loop State Machine
- Deterministic Loop Control from Structured Decisions

---

### 19. Hypothesis-Driven Diagnosis and Targeted Tool Use
**Learn Nineteenth**: Apply scientific method to agent investigations

Required Technical Subskills:
- Hypothesis-Driven Diagnosis
- Hypothesis Formation
- Hypothesis Prioritization
- Specific Testable Hypotheses
- Most-Likely-First Investigation
- Simple-to-Complex Hypothesis Ordering
- Targeted Diagnostic Queries
- Query Rationale Generation
- Non-Repetition of Tested Hypotheses
- Hypothesis Confirmation
- Hypothesis Refutation
- Next-Best-Hypothesis Generation
- Best-Hypothesis Selection
- Strongest-Evidence Iteration Tracking
- FORM-versus-ANALYZE Separation

---

### 20. Capability-Gap Tracking and User Progress
**Learn Twentieth**: Communicate limitations and progress

Required Technical Subskills:
- Capability-Gap Tracking
- Missing-Tool Detection
- Missing-Data Detection
- Missing-Access Detection
- Blocker Telemetry
- Capability-Roadmap Feedback
- Tool-Prioritization Feedback
- User-Visible Capability Limits
- Progress Visibility
- Current-Iteration Display
- Maximum-Iteration Display
- Current-Hypothesis Display
- Running-versus-Stuck Transparency
- Manual-Investigation Handoff
- Capability-Gap Reporting in Final RCA

🔷 CLAUDE CODE: CI/CD Integration & Automation
- CI/CD integration patterns
- -p flag for non-interactive CI/CD pipelines
- Hook system and automation
- Event-driven workflows (pre-commit, post-command, user-prompt-submit)
- Automated behaviors via hooks configuration
- Git integration and branch management
- Co-authored commits with Claude
- Status line configuration
- Keyboard shortcuts and keybindings customization
- IDE integration: VS Code, JetBrains
- Clickable code references and file navigation
- Read before edit workflow
- Prefer Edit over Write for existing files
- Clean diffs without cosmetic changes
- Interactive vs. non-interactive modes

---

═══════════════════════════════════════════════════════════════════
## PHASE 5: PRODUCTION & OPTIMIZATION (WEEKS 9-10)
═══════════════════════════════════════════════════════════════════

**Goal**: Deploy agents at scale with monitoring and optimization

---

### 21. LLM-as-Judge Design and Calibration
**Learn Twenty-First**: Use LLMs to evaluate outputs

Required Technical Subskills:
- Evaluation Rubric Design
- Point-Based Grading
- Pairwise Comparison
- Reference-Based Grading
- Human-Judge Agreement
- Position and Length Bias Testing
- Judge Consistency and Variance
- Multi-Grader Ensembles
- Binary Retrieved-Chunk Relevance Judging
- Two-Stage RAG Judge Gating
- Early-Stopping Judge Policies

---

### 22. LLM Evaluation Metrics
**Learn Twenty-Second**: Measure what matters

Required Technical Subskills:
- Task Success and Solve Rate
- Precision, Recall, and F1
- Tool-Call Accuracy
- Groundedness and Faithfulness
- Pairwise Win Rate
- Safety Violation Rate
- Latency, Cost, and Reliability Metrics
- Confidence Calibration

---

### 23. Backend Product Engineering
**Learn Twenty-Third**: Build production-grade systems

Required Technical Subskills:
- Python and FastAPI Service Design
- REST and Streaming APIs
- Asynchronous I/O and Background Workers
- PostgreSQL and Schema Migrations
- Queue-Based Workflow Orchestration
- Idempotency and Retry Semantics
- Authentication and Authorization
- Caching and Rate Limiting
- Distributed Systems Fundamentals
- CI/CD and Production Observability
- Async API Pattern
- Job and Run Status Polling
- Batch Processing
- Parallel Worker Execution
- Run Grouping and Entity Relationships
- Cross-Service Integration
- Dashboard Deep Linking
- Health Checks and Alerting
- systemd Service Deployment
- Data Retention and TTL Policies

---

═══════════════════════════════════════════════════════════════════
## PHASE 6: QUALITY & SAFETY (WEEKS 11-12)
═══════════════════════════════════════════════════════════════════

**Goal**: Ensure reliability, safety, and quality through rigorous testing

---

### 24. Golden Dataset Creation
**Learn Twenty-Fourth**: Build high-quality evaluation datasets

Required Technical Subskills:
- Production Trace Sampling
- Task and Failure Taxonomy
- Edge-Case and Hard-Negative Curation
- Ground-Truth Annotation Guidelines
- Inter-Annotator Agreement
- Dataset Versioning and Provenance
- Held-Out Regression Sets
- Synthetic Data Validation

---

### 25. Nondeterministic AI Testing
**Learn Twenty-Fifth**: Test systems with inherent randomness

Required Technical Subskills:
- Repeated-Trial Evaluation
- Sampling Parameter Control
- Pass@k and Success Distributions
- Variance and Flakiness Analysis
- Statistical Confidence Intervals
- Reproducible Evaluation Configuration
- Tail and Worst-Case Analysis
- Baseline-versus-Candidate Comparison

---

### 26. Metamorphic Testing for LLMs
**Learn Twenty-Sixth**: Test invariants and robustness

Required Technical Subskills:
- Paraphrase Invariance Testing
- Context-Order Invariance
- Irrelevant-Context Robustness
- Distractor and Noise Injection
- Counterfactual Sensitivity Testing
- Prompt and Context Ablation
- Tool and Environment Perturbation
- Long-Context Robustness

---

### 27. Prompt and Agent Regression Testing in CI
**Learn Twenty-Seventh**: Prevent regressions automatically

Required Technical Subskills:
- Versioned Evaluation Suites
- Baseline-versus-Candidate Gates
- Prompt and Model Regression Thresholds
- Repeated-Run Stability Gates
- Dataset and Schema Versioning
- Failure Triage Reports
- Canary and Shadow Evaluation
- Automated Rollback Criteria

---

### 28. AI Safety and Adversarial Evaluation
**Learn Twenty-Eighth**: Protect against attacks and misuse

Required Technical Subskills:
- Prompt-Injection Testing
- Tool-Use Escalation Testing
- Data-Exfiltration Testing
- RAG-Poisoning Evaluation
- Jailbreak and Policy-Evasion Testing
- Sandboxing and Runtime Isolation
- Least-Privilege Tool Authorization
- Safety Regression Suites
- Red-Team Scenario Design

---

═══════════════════════════════════════════════════════════════════
## SUMMARY & LEARNING METRICS
═══════════════════════════════════════════════════════════════════

### Complete Topic Inventory

| Phase | Week | Skill # | Skill Name | AI Subskills | Claude Topics |
|-------|------|---------|------------|--------------|---------------|
| 1 | 1-2 | 1 | Model/Provider Abstraction and Fallback | 13 | 7 |
| 1 | 1-2 | 2 | LLM Integration, Prompt Engineering, and Agent Profiles | 32 | 12 |
| 1 | 1-2 | 3 | Structured LLM Outputs and Validation | 15 | 7 |
| 1 | 1-2 | 4 | Agent Observability and Experiment Tracking | 15 | 10 |
| 2 | 3-4 | 5 | Agent State Management and Lifecycle | 14 | 12 |
| 2 | 3-4 | 6 | Evidence Synthesis and Confidence Reasoning | 18 | 0 |
| 2 | 3-4 | 7 | Prompt Caching and Token/Context Optimization | 23 | 7 |
| 2 | 3-4 | 8 | Human-in-the-Loop and Controlled Execution | 13 | 10 |
| 2 | 3-4 | 9 | Error Normalization, Deduplication, and Analysis Caching | 13 | 0 |
| 3 | 5-6 | 10 | Deterministic-First Agent Architecture | 12 | 0 |
| 3 | 5-6 | 11 | Classification-Aware Routing | 13 | 0 |
| 3 | 5-6 | 12 | Sub-Agent Architecture and Orchestration | 11 | 15 |
| 3 | 5-6 | 12A | **CrewAI Multi-Agent Framework** | **~60** | **0** |
| 3 | 5-6 | 12B | **LangGraph State Machine Framework** | **~50** | **0** |
| 3 | 5-6 | 13 | Evidence Classification and Loop Termination | 14 | 8 |
| 4 | 7-8 | 14 | Retrieval-Augmented Generation and Knowledge Grounding | 15 | 0 |
| 4 | 7-8 | 15 | Embeddings, Vector Databases, and Semantic Retrieval | 18 | 0 |
| 4 | 7-8 | 16 | RAG Relevance Gating and Retrieval-Quality Control | 13 | 0 |
| 4 | 7-8 | 17 | Knowledge Ingestion, Chunking, Indexing, and Freshness | 24 | 0 |
| 4 | 7-8 | 18 | Agentic Diagnostic Loops | 18 | 0 |
| 4 | 7-8 | 19 | Hypothesis-Driven Diagnosis and Targeted Tool Use | 15 | 0 |
| 4 | 7-8 | 20 | Capability-Gap Tracking and User Progress | 15 | 15 |
| 5 | 9-10 | 21 | LLM-as-Judge Design and Calibration | 11 | 0 |
| 5 | 9-10 | 22 | LLM Evaluation Metrics | 8 | 0 |
| 5 | 9-10 | 23 | Backend Product Engineering | 20 | 0 |
| 6 | 11-12 | 24 | Golden Dataset Creation | 8 | 0 |
| 6 | 11-12 | 25 | Nondeterministic AI Testing | 8 | 0 |
| 6 | 11-12 | 26 | Metamorphic Testing for LLMs | 8 | 0 |
| 6 | 11-12 | 27 | Prompt and Agent Regression Testing in CI | 8 | 0 |
| 6 | 11-12 | 28 | AI Safety and Adversarial Evaluation | 9 | 0 |

---

### Learning Statistics

**Total Content - UPDATED:**
- ✅ 28 Broad Skills (original)
- ✅ 400+ AI/Agentic Subskills (original)
- ✅ 103 Claude Code Topics (original)
- ✅ **2 New Orchestration Frameworks: CrewAI + LangGraph**
- ✅ **~110 New Framework-Specific Topics**

**GRAND TOTAL: 30 Skills | 510+ Subskills | 103 Claude Topics | 2 Frameworks**

**Phase Breakdown - UPDATED:**
- Phase 1 (Foundations): 4 skills, 75 AI subskills, 36 Claude topics
- Phase 2 (Core Patterns): 5 skills, 81 AI subskills, 29 Claude topics
- Phase 3 (Multi-Agent): **6 skills** (added CrewAI + LangGraph), **160 AI subskills**, 23 Claude topics
- Phase 4 (Advanced): 7 skills, 118 AI subskills, 15 Claude topics
- Phase 5 (Production): 3 skills, 39 AI subskills, 0 Claude topics
- Phase 6 (Quality & Safety): 5 skills, 41 AI subskills, 0 Claude topics

**Learning Dependencies Respected:**
✅ Fundamentals before advanced topics
✅ Single-agent before multi-agent
✅ Basic prompting before RAG
✅ Core concepts before testing
✅ Theory before production deployment

---

### Recommended Study Approach

**Daily Practice (2 hours/day):**
- 45 min: Theory (read AI subskills)
- 45 min: Practice (implement Claude Code topics)
- 30 min: Build small projects applying concepts

**Weekly Milestones:**
- Week 1: Build your first Claude agent
- Week 2: Implement structured outputs with validation
- Week 3: Create stateful agent with memory
- Week 4: Add human-in-the-loop controls
- Week 5: **Build CrewAI multi-agent system (incident response pipeline)**
- Week 6: **Build same system with LangGraph (conditional routing + state management)**
- Week 7: Add RAG to your agent
- Week 8: Build diagnostic loop system
- Week 9: Optimize for production cost/latency
- Week 10: Deploy with observability
- Week 11: Implement comprehensive testing
- Week 12: Complete security hardening
- Week 13-14: Capstone project integrating all skills (CrewAI or LangGraph)


### Next Steps

1. **Start with Phase 1, Week 1**: Model selection and basic prompting
2. **Build as you learn**: Create small projects after each skill
3. **Track progress**: Check off subskills as you master them
4. **Practice Claude Code**: Use the CLI/IDE daily
6. **Join community**: Engage with other learners (CrewAI: 45K+ stars, LangGraph: 15K+ stars)
7. **Take certification**: After Phase 5 completion

**Good luck on your AI/Agentic learning journey! 🚀**

---

*Document Version: 2.1*
*Last Updated: 2026-08-14*
*Content: 28 Original Skills + CrewAI + LangGraph | 510+ Subskills | 103 Claude Topics*
*New: Multi-agent orchestration frameworks (CrewAI & LangGraph) integrated in Phase 3*
