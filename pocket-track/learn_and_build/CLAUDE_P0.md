# Complete Claude Code Learning Curriculum
**Progressive Learning Path from 101 to Certification**

---

## 📚 Learning Progression Overview

- **Level 1**: Claude Code 101 - Fundamentals (Weeks 1-2)
- **Level 2**: Claude Code Basics - Core Features (Weeks 3-4)
- **Level 3**: Claude Code 201 - Power User (Weeks 5-7)
- **Level 4**: Advanced Multi-Agent Systems (Weeks 8-10)
- **Level 5**: Production & Certification Prep (Weeks 11-14)

---

═══════════════════════════════════════════════════════════════════
## LEVEL 1: CLAUDE CODE 101 - FUNDAMENTALS (WEEKS 1-2)
═══════════════════════════════════════════════════════════════════

### 1.1 Basic Claude Code Usage & Model Selection
**Learn First**: Core interaction patterns and model selection

**Text Interaction:**
- Model selection for different tasks
- Model switching strategies
- Writing effective prompts
- Conversational context
- Code generation requests
- Code explanation requests
- Debugging assistance
- Refactoring suggestions

---

### 1.2 Session Control & Housekeeping
**Learn Second**: Driving, inspecting, and recovering a session

**Context Inspection & Reclamation:**
- `/context` — inspect what occupies the context window
- `/compact` — summarize and continue in a reclaimed window
- `/clear` — drop all context and start fresh
- Compact vs. clear decision rule
- Auto-compact behavior at the context ceiling
- Scratch-file offloading before the window fills

**Session Navigation:**
- `/resume` — pick up a previous session
- Session renaming and discoverability
- `/fork` — clone full context into a new window
- `/rewind` — time-travel to an earlier state
- `/cd` — change working directory, preserve cache
- Session recovery by metadata identifier

**Diagnostics & Accounting:**
- `/doctor` — dependency and environment diagnostics
- `/usage` — consumption breakdown by session and workflow
- `/powerup` — capability discovery
- Safe mode

---

═══════════════════════════════════════════════════════════════════
## LEVEL 2: CLAUDE CODE BASICS - CORE FEATURES (WEEKS 3-4)
═══════════════════════════════════════════════════════════════════

### 2.1 Claude API & SDK Fundamentals
**Learn Fourth**: Programmatic access

**Claude API Basics:**
- API authentication and keys
- API endpoint structure
- Message format
- Request/response cycle
- Rate limits and quotas
- Error handling basics

**Claude Agent SDK:**
- SDK installation
- Basic agent creation
- API client configuration
- Synchronous vs asynchronous calls
- Response handling
- Token counting

**Cost Management:**
- Token-based pricing model
- Input vs output tokens
- Cached tokens (cheaper)
- Cost estimation techniques
- Budget controls
- Cost optimization basics

---

═══════════════════════════════════════════════════════════════════
## LEVEL 3: CLAUDE CODE 201 - POWER USER (WEEKS 5-7)
═══════════════════════════════════════════════════════════════════

### 3.1 Configuration & Customization
**Learn Eighth**: CLAUDE.md and project setup

**CLAUDE.md Hierarchy:**
- Project-level architecture rulebook
- User-level vs project-level config
- .claude/ directory structure
- Configuration inheritance
- Override patterns

**.claude/rules/ System:**
- Glob patterns for rule matching
- Rule enforcement
- Custom coding standards
- Team conventions
- Project-specific guidelines

**Settings Configuration:**
- settings.json structure
- settings.local.json (gitignored)
- Permission configuration
- Hook configuration
- Environment variables

---

### 3.2 Memory System (Advanced)
**Learn Ninth**: Persistent context and learning

**Memory Types:**
- **User memory**: Role, goals, responsibilities, knowledge
- **Feedback memory**: Guidance on approach (what to avoid/keep)
- **Project memory**: Ongoing work, goals, context
- **Reference memory**: External system pointers

**Memory Operations:**
- Auto memory system
- Memory indexing with MEMORY.md
- Memory versioning and updates
- Memory file structure (frontmatter)
- When to save vs recall memory
- Memory staleness handling

**Context Management:**
- Context preservation across sessions
- Context compression strategies
- Long-context preservation strategies
- Context window optimization
- Information provenance tracking

---

### 3.3 Skills, Commands & Plugins
**Learn Tenth**: Extensibility and customization

**Skills (model-invoked):**
- Skill as a folder: instructions plus bundled assets (scripts, reference docs, templates)
- The "bookshelf" model — front matter as book bindings
- Progressive disclosure: only front matter loads up front
- Front-matter `description` quality as the discovery signal
- Disambiguating skills with similar names or descriptions
- Writing scope and trigger conditions ("use when", "do not use for")
- Skill frontmatter options
  - `context: fork` (isolation)
  - `model:` override
  - `run_in_background:`
- Skills instead of context-dumping into CLAUDE.md
- Codifying repeated work into skills
- Skill creation and management
- Built-in vs custom skills
- Skill parameters and arguments

**Commands (user-invoked):**
- Explicit `/` invocation
- One-off, transactional scope
- Not autonomously reached for by Claude

**Skills vs. Commands:**
- Invocation: autonomous vs. explicit
- Discovery: front-matter description vs. user recall
- Complexity: multi-step with assets vs. one-shot
- Choosing between them
- Preference for stacking behavior into skills

**Plugins:**
- Plugin as a bundle: commands + sub-agents + skills + hooks + MCP servers
- Version-controlled, managed as code
- Distribution across repos and teams
- Centralizing team standards via plugins
- `/plugins` — discovery, installation, management
- Anthropic-verified marketplace vs. third-party sources
- Vetting third-party plugins before install
- Preferring org-approved bundles
- Plugin vs. Skill: delivery mechanism vs. single capability
- Custom plugin development

**Common Commands:**
- `/help` - Get help
- `/init` - Initialize CLAUDE.md
- `/code-review` - Correctness review; `--fix` applies findings
- `/security-review` - Security review
- `/plugins`, `/context`, `/usage`
- Custom domain-specific skills and commands

---

### 3.4 Agent Management & Execution Modes
**Learn Eleventh**: Multi-agent workflows

**Agent Types:**
- general-purpose (default)
- Explore (codebase exploration)
- Plan (architecture design)
- code-reviewer
- Specialized subagents (domain-specific)

**Sub-Agent Configuration:**
- Agent definition and front matter in `.claude/agents/`
- `model:` per agent — right-sizing capability to task complexity
- Tool allow/deny scoping per agent
- MCP scoping per agent
- Runaway guard — max turn limits
- Per-agent hooks and memory
- `description` front matter for parent-session discovery
- Execution location and working directory

**Execution Modes:**
- Foreground execution (blocking, default)
- Background execution (run_in_background parameter)
- Parallel agent spawning
- Agent resumption and continuation
- Agent memory and context handoff

**Sub-Agent Execution Semantics:**
- Independent context window per sub-agent
- Task-in / response-out interaction model
- Background execution by default when delegated
- Permission mode inheritance from the parent session
- Nesting depth limit of 3 (reduced from 5)
- Agent View as a monitoring cockpit

**Explore Subagent:**
- Explore subagent specialization
- Codebase exploration workflows
- Fast search and discovery
- Pattern-based file finding
- Keyword searching in code
- Thoroughness levels: quick, medium, very thorough
- Explore vs. direct grep/find usage
- Parallel exploration capabilities

---

### 3.5 Advanced Tool Usage
**Learn Twelfth**: Tool mastery and MCP

**Tool Execution:**
- Read, Edit, Write, Bash tools (mastery)
- Tool permission management
- Tool result handling
- Parallel tool execution
- Sequential vs parallel tool calls
- Tool search and discovery
- Tool error handling

**Model Context Protocol (MCP):**
- MCP fundamentals
- Three core MCP primitives: tools, resources, prompts
- Tool description optimization for Claude selection
- .mcp.json configuration (project vs. user-level)
- MCP server setup
- Tool scoping per agent role
- MCP server implementation (Python/TypeScript)
- Resource definition and access patterns
- Prompt template distribution via MCP

**Error Response Structure:**
- isError field
- isRetryable field
- errorCategory field
- Structured error handling
- Retry strategies

---

### 3.6 Automation & Workflows
**Learn Thirteenth**: Event-driven automation

**Hook System:**
- Hook system architecture
- Event-driven workflows
- Hook configuration in settings.json
- Hook execution context

**Hook Events:**
- `SessionStart` — cache warming, environment loading
- `UserPromptSubmit` — inspect or augment the prompt
- `PreToolUse` — fires before a tool call
- `PostToolUse` — fires after a tool call
- `Stop` / `SubagentStop` — control returns to the user
- `PreCompact`, `Notification`
- Distinguishing Claude Code hook events from git hooks (pre-commit is git, not Claude Code)

**Hook Matchers & Binding:**
- Binding hooks in settings.json by event
- Matcher patterns — scoping to specific tools (e.g. `Edit|Write`) or MCP servers
- Hooks as shell scripts
- Returning a system message into the loop
- Chaining multiple hooks on one event

**Common Hook Patterns:**
- Auto-format and type-check on edit/write
- Secret scanning before egress
- MCP activity logging
- Stop-event notification hooks
- Deterministic layer vs. model judgment

**Workflow Patterns:**
- Plan mode vs. direct execution workflows
- Research workflows
- Code generation workflows
- Testing workflows
- Documentation workflows

---

### 3.7 Permission & Security
**Learn Fourteenth**: Safe and controlled execution

**Permission System:**
- Permission modes and settings
- Permission prompts
- Allowlist configuration
- Permission levels (auto-allow, prompt, deny)
- Per-tool permissions
- Per-directory permissions

**Security:**
- Sandbox mode
- Dangerous operation handling
- User approval gates
- Least-privilege principle
- Security vulnerability prevention (XSS, SQL injection, etc.)
- Credential handling
- Secret detection

---

═══════════════════════════════════════════════════════════════════
## LEVEL 4: ADVANCED MULTI-AGENT SYSTEMS (WEEKS 8-10)
═══════════════════════════════════════════════════════════════════

### 4.1 Agentic Architecture & Orchestration
**Learn Sixteenth**: Multi-agent system design (27% of certification)

**Agentic Loop Pattern:**
- send request → check stop_reason → execute tool → return result → repeat
- Stop reason evaluation and branching logic
- Tool delegation and execution flow
- Loop termination conditions
- Iteration limits

**Multi-Agent Patterns:**
- Hub-and-Spoke Orchestration with central coordinator
- Coordinator-Subagent Patterns and task delegation
- Multi-Agent System Design and communication topology
- Task Decomposition Strategies
- Flat vs hierarchical topologies

**Agent Isolation:**
- Filesystem isolation with work trees
- Context isolation with `context: fork`
- Context window forking for subagent isolation
- Token consumption isolation per subagent
- Independent agent execution
- Resource isolation

**Agent Communication:**
- Session state management across agent interactions
- Agent-to-agent handoff patterns
- Typed inter-agent messages
- Context sharing strategies
- Data flow between agents

**Error Handling:**
- Subagent error handling and propagation
- Error propagation across multi-agent systems
- Silent failure prevention
- Graceful degradation
- Recovery strategies

---

### 4.2 Parallelization Patterns
**Learn Seventeenth**: Running agents in parallel

**Pattern 1 — Sub-Agents:**
- Fan-out from a single session
- Fresh context window per delegated task
- Results returned to the parent; parent context stays lean
- Scoped, independent subtasks

**Pattern 2 — Agent View:**
- Launching parallel sessions with `claude agents`
- Cockpit view of session state (working / awaiting input / complete)
- Classifier-generated session headlines
- Starting new sessions from within the view
- Bouncing between parallel threads

**Pattern 3 — Agent Teams:**
- Lead agent with decision authority
- Shared task list
- Messaging queue for worker coordination
- Conflict resolution across workers
- Convergence and unification by the lead

**Pattern 4 — Dynamic Workflows:**
- Plan expressed as a repeatable runtime script
- Script-orchestrated sub-agent fan-out
- Unification of results at the end
- Resumability after interruption
- Scale to hundreds of agents per run
- Workflow size guideline (default 15, tunable)
- Token cost awareness

**Decision Matrix:**

| | Sub-Agents | Agent View | Agent Teams | Dynamic Workflows |
|---|---|---|---|---|
| Orchestrated by | Parent session | You | Lead agent | The script |
| Coordination | Fan-out / return | Manual switching | Messaging queue | Defined in plan |
| Repeatable | No | No | No | Yes |
| Resumable | No | Per-session | Partial | Yes |
| Scale | Few–dozens | Handful | Team-sized | Hundreds |
| Token cost | Low–moderate | Moderate | Moderate–high | High |
| Use when | Scoped independent tasks | Multitasking threads | One task, tight sync | Repeatable large-scale work |

**Underpinning Techniques:**
- Work trees — filesystem isolation per agent
- Collision avoidance as the prerequisite for higher parallelism
- Work trees vs. `context: fork` — filesystem vs. context isolation
- Cross-session messaging
- Batching worktree-isolated agents at scale

**Scope Note:**
- Loop engineering / goal-driven autonomous loops as a 301 topic

---

### 4.3 Advanced Prompt Engineering
**Learn Eighteenth**: Production prompt patterns (20% of certification)

**Advanced Techniques:**
- Few-shot prompting (advanced)
- Multi-pass review systems
- Task Decomposition Strategies
- Evidence-Citation Rules
- Confidence-Threshold Instructions

**Agent Profiles:**
- Profile-versus-Prompt Separation
- Agent Behavior Equation
- Capability-versus-Behavior Separation
- Deterministic Profile Selection
- Profile versioning

**Validation & Retry:**
- Validation-retry loop architecture
- Programmatic validation layering
- Schema versioning
- Retry policies
- Fallback strategies

**Cost Optimization:**
- Cost optimization through prompt caching
- Message Batches API (50% cost savings, 24-hour processing)
- Tradeoffs: real-time vs. batch processing
- Prompt caching for production optimization
- Token consumption monitoring

---

### 4.4 Context Management & Reliability
**Learn Nineteenth**: Production reliability (15% of certification)

**Context Strategies:**
- Long-context preservation strategies
- Context compression strategies
- Anti-pattern: Larger context windows for attention problems (use focused passes)
- Context budget management
- Context prioritization

**Reliability Patterns:**
- Confidence calibration in agentic systems
- Deterministic escalation logic (non-confidence-based)
- Information provenance tracking
- Silent failure prevention
- Edge case routing and human escalation

**Error Handling:**
- Error response structure (isError, isRetryable, errorCategory)
- Error propagation patterns
- Retry logic and graceful degradation
- Circuit breakers
- Fallback strategies

---

═══════════════════════════════════════════════════════════════════
## LEVEL 5: PRODUCTION & CERTIFICATION PREP (WEEKS 11-14)
═══════════════════════════════════════════════════════════════════

### 5.1 CI/CD Integration & Deployment
**Learn Twentieth**: Production deployment (20% of certification)

**CI/CD Patterns:**
- CI/CD integration patterns
- -p flag for non-interactive CI/CD pipelines
- Non-interactive mode
- Automated testing integration
- Continuous deployment

**Automation:**
- Hook system and automation (advanced)
- Event-driven workflows (production)
- Automated quality gates
- Deployment pipelines
- Rollback strategies

**Configuration Management:**
- Environment-specific configuration
- Secret management
- Configuration validation
- Version control for configs
- Multi-environment setup

---

### 5.2 Production Reliability & Monitoring
**Learn Twenty-First**: Production operations

**Reliability:**
- Production reliability patterns
- SLA management
- Failure recovery strategies
- Health checks
- Availability monitoring

**Cost Optimization:**
- Cost vs. latency tradeoffs
- Token consumption monitoring
- Resource optimization
- Budget alerts
- Usage analytics

**Monitoring:**
- Logging and observability
- Error tracking
- Performance metrics
- Usage analytics
- Alert configuration

---

### 5.3 Seven Anti-Patterns to Avoid
**Learn Twenty-Second**: Common mistakes (critical for certification)

**Anti-Pattern 1: Prompt-based enforcement**
- ❌ Problem: Using prompts to enforce rules
- ✅ Solution: Use programmatic validation instead
- Why: Prompts are non-deterministic, validation is deterministic

**Anti-Pattern 2: Self-reported confidence for routing**
- ❌ Problem: Asking LLM how confident it is
- ✅ Solution: Use deterministic thresholds
- Why: LLMs are poorly calibrated on confidence

**Anti-Pattern 3: Batch API for blocking workflows**
- ❌ Problem: Using batch API when you need real-time
- ✅ Solution: Proper workflow selection
- Why: Batch has 24-hour latency, incompatible with real-time

**Anti-Pattern 4: Larger context windows for attention problems**
- ❌ Problem: Increasing context to solve focus issues
- ✅ Solution: Use focused passes instead
- Why: Larger context degrades attention, costs more

**Anti-Pattern 5: Silent failures on subagent errors**
- ❌ Problem: Ignoring subagent errors
- ✅ Solution: Return structured error context
- Why: Silent failures cascade, hard to debug

**Anti-Pattern 6: Universal tool availability**
- ❌ Problem: Giving all tools to all agents
- ✅ Solution: Scope tools to agent roles
- Why: Security, cost, and error reduction

**Anti-Pattern 7: Flat multi-agent topology**
- ❌ Problem: Mesh network of agents
- ✅ Solution: Implement hub-and-spoke pattern
- Why: Easier debugging, clearer data flow

---

═══════════════════════════════════════════════════════════════════
## DOCUMENT METADATA
═══════════════════════════════════════════════════════════════════

**Document Version**: 1.1  
**Last Updated**: 2026-08-24  
**Status**: Complete - Restructured Learning Path  
**Coverage**: Claude Code 101 to Certification Topics