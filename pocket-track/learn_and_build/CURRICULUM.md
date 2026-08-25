# Curriculum — CLAUDE_P0 through PocketTrack

26 modules. Each teaches specific `CLAUDE_P0.md` topics and leaves a committed
artifact behind. Sequenced so every module's output is used by a later one — the
two enhancements in `DESIGN.md` fall out of the path rather than being bolted on.

**Source:** `ld-atiya/learn-and-build/AI Bible/CLAUDE_P0.md`

## Module contract

Every module has four fields. A module is complete only when **Done when** is
objectively true and the artifact exists in the repo.

```
Topics    → the CLAUDE_P0 sections it covers
Artifact  → the file / config / commit it produces
Done when → a check someone else could verify without asking you
```

---

## Phase 0 — Ground rules

*Configure the harness before writing anything it will govern.*

| # | Module | Topics | Artifact | Done when |
|---|---|---|---|---|
| M01 | Project rulebook | §3.1 CLAUDE.md hierarchy, `.claude/rules/`, inheritance, overrides | `.claude/rules/*.md` for agents + templates | A rule visibly changes Claude's behaviour on a test edit |
| M02 | Permissions & settings | §3.1 settings, §3.7 permission modes, allowlists, sandbox, least-privilege | `.claude/settings.json`, `settings.local.json` | Read-only commands stop prompting; a denied tool stays denied |
| M03 | Memory | §3.2 four memory types, MEMORY.md, frontmatter, staleness | Memory entries for this project | A fresh session recalls a project decision unprompted |

## Phase 1 — Foundations

*Decide what the model can do, then give it tools and a loop.*

| # | Module | Topics | Artifact | Done when |
|---|---|---|---|---|
| M04 | **Model capability probe** | §1.1 model selection & switching, §2.1 message format, request/response, error handling, token counting | `probe_tool_calling.py` results recorded as **D1** | Verdict GO / MARGINAL / NO-GO written into `STATE.md` |
| M05 | Skills | §3.3 custom commands, frontmatter (`context: fork`, `model:`, `run_in_background:`), skills vs plugins | `/lab-resume`, `/lab-status` | `/lab-resume` restores context with no other prompt |
| M06 | Subagents | §3.4 agent types, foreground vs background, parallel spawning, Explore thoroughness levels | A written codebase map produced by Explore | You can name when Explore beats direct grep, from experience |
| M07 | Tool design & registry | §3.5 tool execution, parallel vs sequential, scoping. **AP6** | `agents/registry.py`, `agents/tools.py` | Copilot scope *cannot* express a WRITE tool — proved by a test |
| M08 | **The agentic loop** | §4.1 loop, stop_reason branching, delegation, termination, iteration limits | `agents/runtime.py` | A 3-step chain completes; the cap is provably hit on a runaway goal |

## Phase 2 — Enhancement 1: Copilot

| # | Module | Topics | Artifact | Done when |
|---|---|---|---|---|
| M09 | Driver prompt & profiles | §4.2 few-shot, decomposition, evidence-citation, profile-vs-prompt separation, versioning | `agents/copilot.py` + versioned profile | Profile swaps without touching runtime code |
| M10 | Validation & retry | §4.2 validation-retry architecture, programmatic layering, schema versioning, fallback | Validation layer + retry policy | A deliberately malformed response recovers without user impact |
| M11 | Error contract | §3.5 `isError`/`isRetryable`/`errorCategory`, §4.3 propagation. **AP5** | `ToolResult` type | A failing tool never silently yields an empty answer |
| M12 | Context management | §4.3 long-context, compression, budget, prioritisation. **AP4** | Conversation trimming strategy | A long session stays under budget without losing the goal |
| M13 | Hooks | §3.6 hook architecture, pre-commit / post-command / user-prompt-submit, workflow patterns | Pre-commit hook blocking new network destinations | Adding a stray `httpx.get("https://…")` fails the commit |
| M14 | **Ship E1** | §3.7 CSRF, CSP; integration | Dashboard panel + route + tests | You ask a real question of your real data and get a grounded answer |

## Phase 3 — Enhancement 2: Sentinel

| # | Module | Topics | Artifact | Done when |
|---|---|---|---|---|
| M15 | Deterministic detection | **AP1** programmatic validation over prompt enforcement | Stage-1 scan in `agents/sentinel.py` | Recurring charges are found with the LLM switched off |
| M16 | Escalation & calibration | **AP2** deterministic thresholds, §4.3 confidence calibration, edge-case routing | Numeric escalation rules | No routing decision anywhere reads a model's self-reported confidence |
| M17 | WRITE tools & approval gates | §3.7 approval gates, dangerous-operation handling, least-privilege | `create_finding`, `propose_merchant_rule` | No agent path mutates a transaction, bucket, or budget |
| M18 | Provenance | §4.3 information provenance, evidence-citation | `evidence` JSON on every finding | A finding with empty evidence is rejected at insert |
| M19 | Autonomy & degradation | §4.3 silent-failure prevention, graceful degradation, circuit breakers | Scheduler wiring + fallbacks | With Ollama stopped, `daily-sync` still completes and still finds things |
| M20 | **Ship E2** | integration | Review queue UI + tests | An overnight run surfaces a real finding about your real spending |

## Phase 4 — Production

| # | Module | Topics | Artifact | Done when |
|---|---|---|---|---|
| M21 | MCP | §3.5 MCP fundamentals, tools/resources/prompts, `.mcp.json`, server implementation | Local MCP server exposing probe + eval | Claude Code calls your MCP tool from a fresh session |
| M22 | CI/CD | §5.1 CI patterns, `-p` non-interactive, quality gates, config validation | GitHub Actions workflow | A PR is auto-reviewed by `claude -p` and gated on pytest |
| M23 | Observability | §5.2 logging, error tracking, performance metrics, usage analytics, alerts | `agent_runs` dashboard | You can answer "how often does the loop hit the cap?" with data |

## Phase 5 — Gap closure

*These close what E1 and E2 structurally cannot reach.*

| # | Module | Topics | Artifact | Done when |
|---|---|---|---|---|
| M24 | Multi-agent | §4.1 hub-and-spoke, coordinator-subagent, decomposition, isolation & context forking, typed handoff, error propagation. **AP7** | Minimal Month-End Analyst | A coordinator fans out to ≥2 specialists and synthesises typed results |
| M25 | Claude API & cost | §2.1 auth, endpoints, rate limits, **Agent SDK**, sync vs async; §4.2 prompt caching, **Message Batches**, cost optimisation. **AP3** | Throwaway project **outside** pocket-track | You have measured a real cache hit and a real batch job |
| M26 | Anti-pattern audit | §5.3 all seven | Written audit against your own code | Each anti-pattern cites a line of yours that avoids it |

---

## Traceability — every CLAUDE_P0 section

| CLAUDE_P0 § | Module(s) |
|---|---|
| 1.1 Usage & model selection | M04 (+ practised throughout) |
| 2.1 Claude API basics | **M25** (M04 partial: message format, req/resp, errors, tokens) |
| 2.1 Claude Agent SDK | **M25** |
| 2.1 Cost management | **M25** |
| 3.1 CLAUDE.md hierarchy & rules | M01 |
| 3.1 Settings configuration | M02 |
| 3.2 Memory system | M03 |
| 3.3 Skills & plugins | M05 |
| 3.4 Agents & execution modes | M06 |
| 3.5 Tool execution | M07 |
| 3.5 MCP | M21 |
| 3.5 Error response structure | M11 |
| 3.6 Hooks & workflows | M13 |
| 3.7 Permissions | M02 |
| 3.7 Security & approval gates | M02, M17 |
| 4.1 Agentic loop | M08 |
| 4.1 Multi-agent & isolation & handoff | **M24** |
| 4.2 Advanced techniques & profiles | M09 |
| 4.2 Validation & retry | M10 |
| 4.2 Caching & batch | **M25** |
| 4.3 Context strategies | M12 |
| 4.3 Reliability & calibration | M16, M19 |
| 4.3 Provenance | M18 |
| 4.3 Error handling | M11 |
| 5.1 CI/CD | M22 |
| 5.2 Reliability & monitoring | M23 |
| 5.3 Seven anti-patterns | M26 (audit); individually M07·AP6, M11·AP5, M12·AP4, M15·AP1, M16·AP2, M24·AP7, M25·AP3 |

## Coverage honesty

| | Coverage | Note |
|---|---|---|
| M01–M20 (E1 + E2) | ~83% | The two enhancements plus deliberate harness work |
| + M21–M23 | ~88% | Production topics |
| + M24 | ~93% | Multi-agent — the largest single gap |
| + M25 | ~100% | **Cannot live in pocket-track.** Local-only is a hard invariant; the Claude API topics need a separate throwaway project |

M25 is deliberately outside this repo. Do not weaken the privacy invariant to
satisfy a syllabus.

## Rules of engagement

1. **Evidence or it didn't happen.** No `[x]` without an artifact path.
2. **One module at a time.** Finish and record before starting the next.
3. **Blocked ≠ skipped.** Record the blocker in `STATE.md`; move to the next
   unblocked module rather than leaving a false gap.
4. **Design drift gets logged.** If the build contradicts `DESIGN.md`, update the
   design and add a decision entry saying why.
5. **D1 gates Phase 2.** Do not write runtime code before the probe verdict.
