# Complete Claude Code Learning Curriculum
**Progressive Learning Path from 101 to Certification**

Total Topics: 156 discrete learning items organized in incremental difficulty

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

### 1.1 What is Claude Code?
**Learn First**: Understanding the platform and mental model

**Core Concepts:**
- Claude Code as AI-powered coding assistant
- Multi-modal LLM capabilities (text + code + images)
- Autonomous agentic behavior
- Tool-calling and execution model
- Where Claude Code fits in the AI ecosystem

**Platforms & Access:**
- CLI tool (terminal-based)
- Desktop app (Mac/Windows)
- Web app (claude.ai/code)
- VS Code extension
- JetBrains extension
- Platform selection criteria

**Claude Models:**
- Claude 4.X model family overview
- Opus 4.7 (claude-opus-4-7) - Most capable, slower, expensive
- Sonnet 4.6 (claude-sonnet-4-6) - Balanced performance/cost
- Sonnet 4.5 - Previous generation
- Haiku 4.5 (claude-haiku-4-5) - Fastest, cheapest
- Fast mode with Opus 4.6
- Model selection for different tasks
- Model switching strategies

---

### 1.2 Basic Claude Code Usage
**Learn Second**: Core interaction patterns

**Text Interaction:**
- Writing effective prompts
- Conversational context
- Code generation requests
- Code explanation requests
- Debugging assistance
- Refactoring suggestions

**Core Workflows:**
- Interactive mode (default)
- Direct execution mode
- Question answering
- Code modification
- File reading and editing
- Multi-file operations

**Best Practices - Basics:**
- Be specific in requests
- Provide context
- Ask for explanations when unclear
- Review changes before accepting
- Use incremental changes
- Test as you go

---

### 1.3 Basic Tools & Commands
**Learn Third**: Essential tool usage

**Core Tools:**
- Read tool (view file contents)
- Edit tool (precise modifications)
- Write tool (create new files)
- Bash tool (shell commands)
- When to use each tool

**Tool Basics:**
- Read before edit principle
- Prefer Edit over Write for existing files
- Use dedicated tools over Bash (Read vs cat, Edit vs sed)
- Tool permission prompts
- Understanding tool results

**Output & Formatting:**
- Markdown rendering
- Code block formatting
- Clickable file references `[file.ts](path/file.ts)`
- Line number linking `[file.ts:42](path/file.ts#L42)`
- Structured output basics

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

### 2.2 Prompt Engineering Fundamentals
**Learn Fifth**: Crafting effective prompts

**Prompt Engineering Basics:**
- System-Prompt Design
- User-Prompt Design
- System/User Prompt Separation
- Explicit Output-Format Instructions
- Clear task definition
- Providing sufficient context

**Few-Shot Learning:**
- What is few-shot prompting
- When to use examples
- Structuring examples effectively
- Example quality vs quantity
- Domain-specific examples

**Constraints & Instructions:**
- Explicit Constraints
- Evidence-Only Instructions
- Hallucination Prevention techniques
- Insufficient-Data Handling
- Error guidance

---

### 2.3 Structured Output & Validation
**Learn Sixth**: Controlling output format

**JSON Schema Enforcement:**
- JSON schema basics
- Schema design principles
- --output-format json flag
- --json-schema flag
- Schema validation

**Validation Patterns:**
- Validation-retry loop architecture
- Semantic vs. syntax validation
- Programmatic validation layering
- Type checking
- Runtime validation
- Error recovery

**Structured Data:**
- Pydantic models integration
- Type safety
- Field validation
- Nested structures
- Optional vs required fields

---

### 2.4 Basic Git Integration
**Learn Seventh**: Version control workflows

**Git Workflows:**
- Git commit workflows
- Commit message generation
- Co-authored commits with Claude
- Diff review
- Branch awareness

**Git Safety:**
- Git safety protocols
- No force push to main/master
- No --no-verify flag
- Pre-commit hook compliance
- Reviewing changes before commit
- Understanding destructive operations

**Pull Requests:**
- Pull request creation
- PR description generation
- Branch management
- Review request formatting
- Using gh CLI integration

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

### 3.3 Skills & Plugins System
**Learn Tenth**: Extensibility and customization

**Skills:**
- Custom slash command development
- Skill creation and management
- Skill frontmatter options
  - `context: fork` (isolation)
  - `model:` override
  - `run_in_background:`
- Skill invocation and execution
- Built-in vs custom skills
- Skill parameters and arguments

**Plugins:**
- Plugin architecture
- Plugin installation and configuration
- Plugin vs. Skills differences
- Custom plugin development
- Plugin ecosystem
- Plugin discovery and management

**Common Skills:**
- `/help` - Get help
- `/init` - Initialize CLAUDE.md
- `/review` - Review pull request
- `/security-review` - Security review
- Custom domain-specific skills

---

### 3.4 Agent Management & Execution Modes
**Learn Eleventh**: Multi-agent workflows

**Agent Types:**
- general-purpose (default)
- Explore (codebase exploration)
- Plan (architecture design)
- code-reviewer
- Specialized subagents (domain-specific)

**Execution Modes:**
- Foreground execution (blocking, default)
- Background execution (run_in_background parameter)
- Parallel agent spawning
- Agent resumption and continuation
- Agent memory and context handoff

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

### 3.6 IDE Integration (Advanced)
**Learn Thirteenth**: IDE-specific features

**VS Code Extension:**
- VS Code extension features
- IDE selection context
- Selection-based actions
- Inline suggestions
- Multi-file editing

**General IDE Features:**
- Clickable code references
- File path navigation
- Line number linking
- Status line configuration
- Keyboard shortcuts and keybindings
- Custom keybindings.json

---

### 3.7 Automation & Workflows
**Learn Fourteenth**: Event-driven automation

**Hook System:**
- Hook system architecture
- Event-driven workflows
- Hook configuration in settings.json
- Hook execution context

**Hook Types:**
- Pre-commit hooks
- Post-command hooks
- User-prompt-submit hooks
- Custom event hooks
- Automated behaviors via hooks

**Workflow Patterns:**
- Plan mode vs. direct execution workflows
- Research workflows
- Code generation workflows
- Testing workflows
- Documentation workflows

---

### 3.8 Permission & Security
**Learn Fifteenth**: Safe and controlled execution

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
- Agent isolation with worktrees (context: fork)
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

### 4.2 Advanced Prompt Engineering
**Learn Seventeenth**: Production prompt patterns (20% of certification)

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

### 4.3 Context Management & Reliability
**Learn Eighteenth**: Production reliability (15% of certification)

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
**Learn Nineteenth**: Production deployment (20% of certification)

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
**Learn Twentieth**: Production operations

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
**Learn Twenty-First**: Common mistakes (critical for certification)

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

### 5.4 Certification Domain Coverage
**Learn Twenty-Second**: Exam preparation

**Domain 1: Agentic Architecture & Orchestration (27%)**
- Agentic Loop Pattern mastery
- Hub-and-Spoke Orchestration
- Multi-Agent System Design
- All topics from section 4.1

**Domain 2: Tool Design & MCP Integration (18%)**
- MCP fundamentals
- Tool design best practices
- Error handling patterns
- All topics from section 3.5

**Domain 3: Claude Code Configuration & Workflows (20%)**
- CLAUDE.md expertise
- Workflow patterns
- CI/CD integration
- All topics from sections 3.1 and 5.1

**Domain 4: Prompt Engineering & Structured Output (20%)**
- Advanced prompting
- Validation patterns
- Cost optimization
- All topics from sections 2.2, 2.3, and 4.2

**Domain 5: Context Management & Reliability (15%)**
- Context strategies
- Reliability patterns
- Production deployment
- All topics from sections 3.2, 4.3, and 5.2

**Hands-On Skills Required:**
- Building end-to-end agentic loops with tool calling
- Structured error handling in distributed systems
- CLAUDE.md project governance design
- MCP server implementation from scratch
- Multi-pass validation pipelines with JSON schema
- Hub-and-spoke system architecture
- CI/CD integration with Claude Code
- Prompt caching for production optimization

---

═══════════════════════════════════════════════════════════════════
## SUPPORTING TOPICS & REFERENCE
═══════════════════════════════════════════════════════════════════

### Supporting Technologies

**Claude Agent SDK:**
- Core framework for agent development
- Python SDK
- TypeScript SDK
- API client libraries
- Tool integration patterns

**JSON Schema Validation:**
- Schema design
- Validation libraries
- Type generation
- Error messages
- Schema evolution

**Production Infrastructure:**
- Cost optimization tools
- Failure recovery systems
- Monitoring and alerting
- SLA management
- Deployment automation

---

## 📊 Learning Statistics

**Total Learning Items: 156+**

**By Level:**
- Level 1 (101 Basics): 26 topics
- Level 2 (Core Features): 28 topics  
- Level 3 (201 Power User): 52 topics
- Level 4 (Multi-Agent): 30 topics
- Level 5 (Production): 20+ topics

**By Certification Domain:**
- Domain 1 (Orchestration): ~30 topics (27%)
- Domain 2 (Tools/MCP): ~28 topics (18%)
- Domain 3 (Config/Workflows): ~31 topics (20%)
- Domain 4 (Prompting): ~31 topics (20%)
- Domain 5 (Context/Reliability): ~23 topics (15%)
- Supporting/Anti-patterns: ~13 topics

---

## 🎯 Study Recommendations

### Week-by-Week Plan

**Weeks 1-2: Level 1 (Claude 101)**
- Day 1-2: Install and basic usage
- Day 3-5: Core tools mastery
- Day 6-7: Model selection and basic prompting
- Weekend: Practice project #1 (simple code generation)

**Weeks 3-4: Level 2 (Core Features)**
- Day 8-10: API/SDK basics
- Day 11-13: Prompt engineering
- Day 14-16: Structured output
- Day 17-21: Git integration
- Weekend: Practice project #2 (automated PR workflow)

**Weeks 5-7: Level 3 (Claude 201)**
- Day 22-24: Configuration systems
- Day 25-28: Memory system
- Day 29-31: Skills and plugins
- Day 32-35: Agent management
- Day 36-42: Advanced tools and MCP
- Weekends: Practice projects #3-4 (custom skills, MCP integration)

**Weeks 8-10: Level 4 (Multi-Agent)**
- Day 43-49: Agentic architecture
- Day 50-56: Advanced prompting
- Day 57-63: Context and reliability
- Weekends: Practice projects #5-6 (multi-agent systems)

**Weeks 11-14: Level 5 (Production & Cert Prep)**
- Day 64-70: CI/CD integration
- Day 71-77: Production reliability
- Day 78-84: Anti-patterns study
- Day 85-98: Certification domain review
- Final weekend: Mock exam and review

### Daily Practice (2 hours/day)
- 45 min: Study new topics
- 45 min: Hands-on practice
- 30 min: Review and note-taking

### Practice Projects Suggested
1. Code generator with validation
2. Automated PR review bot
3. Custom skill for domain workflow
4. MCP server for internal API
5. Multi-agent incident response system
6. Production deployment pipeline

---

## ✅ Checklist: Am I Ready for Certification?

**Domain 1: Agentic Architecture (27%)**
- [ ] Can implement agentic loop from scratch
- [ ] Can design hub-and-spoke topology
- [ ] Understand all 7 multi-agent patterns
- [ ] Can handle agent errors properly
- [ ] Can isolate agent context and tokens

**Domain 2: Tool Design & MCP (18%)**
- [ ] Can build custom MCP server
- [ ] Understand all 3 MCP primitives
- [ ] Can optimize tool descriptions
- [ ] Can handle error responses correctly
- [ ] Can scope tools per agent role

**Domain 3: Configuration & Workflows (20%)**
- [ ] Can write effective CLAUDE.md
- [ ] Understand .claude/rules/ patterns
- [ ] Can implement CI/CD integration
- [ ] Know when to use plan vs direct mode
- [ ] Can configure hooks properly

**Domain 4: Prompt Engineering (20%)**
- [ ] Can write few-shot prompts
- [ ] Can implement validation-retry loops
- [ ] Understand batch vs real-time tradeoffs
- [ ] Can optimize costs with caching
- [ ] Can enforce JSON schema output

**Domain 5: Context & Reliability (15%)**
- [ ] Can implement long-context strategies
- [ ] Can handle agent-to-agent handoffs
- [ ] Know deterministic escalation patterns
- [ ] Can track information provenance
- [ ] Can prevent silent failures

**Anti-Patterns:**
- [ ] Can identify and fix all 7 anti-patterns
- [ ] Understand why each anti-pattern is bad
- [ ] Know the correct alternative for each

---

**Document Version: 1.0**  
**Last Updated: 2026-08-14**  
**Status: Complete - No content lost from original**  
**New: Fully restructured in progressive learning order**  
**Coverage: Claude 101, 201, and Certification topics**
