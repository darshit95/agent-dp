# Progress — CLAUDE_P0 × PocketTrack

Tracks learning `CLAUDE_P0.md` section by section while building the `DESIGN.md`
agentic layer. **Numbering is CLAUDE_P0's own** (1.1, 1.2, 2.1, …).

## How a section runs

1. Concept taught in detail
2. **User implements**, step by step
3. Cross-questions answered
4. Changes tested
5. **User reviews and says "done"** → only then is this file updated

## Session start facts — 2026-08-25

| | |
|---|---|
| Baseline tests | `126 passed` |
| Production LOC | 5,831 |
| `agents/` | one 8-line stub (`_rule_probe.py`) |
| Ollama | running, `qwen3.5:4b` Q4_K_M @ `127.0.0.1:11434` |

Model capability is **already settled** by a prior probe (12/15). Binding and not
to be relitigated — recorded in `.claude/rules/agents-layer.md`:

- required-arg validation in the registry
- hard iteration cap that degrades explicitly
- **no** repeat-call guard (measured *worse* than none)
- agent loop runs at temperature 0

## Deliverable per section

Sections differ in what they can produce, and the distinction is real:

- **Harness** — teaches driving Claude Code. Deliverable is config you then use
  while building (`.claude/` files, skills, settings).
- **Product** — architectural. Deliverable is PocketTrack code under `agents/`.

## Status

`[ ]` not started · `[~]` in progress · `[x]` done + evidence

### Level 1 — Fundamentals
| | § | Topic | Kind | Evidence |
|---|---|---|---|---|
| `[x]` | 1.1 | Usage & model selection | Harness | temp 0 vs 0.7 divergence reproduced on `qwen3.5:4b` |
| `[ ]` | 1.2 | Session control & housekeeping | Harness | |

### Level 2 — Core features
| | § | Topic | Kind | Evidence |
|---|---|---|---|---|
| `[ ]` | 2.1 | Claude API & SDK fundamentals | Outside repo¹ | |

### Level 3 — Power user
| | § | Topic | Kind | Evidence |
|---|---|---|---|---|
| `[ ]` | 3.1 | Configuration & customization | Harness | |
| `[ ]` | 3.2 | Memory system | Harness | |
| `[ ]` | 3.3 | Skills, commands & plugins | Harness | |
| `[ ]` | 3.4 | Agent management & execution modes | Harness | |
| `[ ]` | 3.5 | Advanced tool usage + MCP + error structure | **Product** | `agents/registry.py`, `agents/tools.py` |
| `[ ]` | 3.6 | Automation & workflows (hooks) | Harness | |
| `[ ]` | 3.7 | Permission & security | Both | |

### Level 4 — Advanced multi-agent
| | § | Topic | Kind | Evidence |
|---|---|---|---|---|
| `[ ]` | 4.1 | Agentic architecture & orchestration | **Product** | `agents/runtime.py` |
| `[ ]` | 4.2 | Parallelization patterns | Harness | |
| `[ ]` | 4.3 | Advanced prompt engineering | **Product** | `agents/copilot.py` |
| `[ ]` | 4.4 | Context management & reliability | **Product** | `agents/sentinel.py` |

### Level 5 — Production & certification
| | § | Topic | Kind | Evidence |
|---|---|---|---|---|
| `[ ]` | 5.1 | CI/CD integration & deployment | Harness | |
| `[ ]` | 5.2 | Production reliability & monitoring | **Product** | `agent_runs` |
| `[ ]` | 5.3 | Seven anti-patterns | Audit | |

¹ 2.1 covers the remote Claude API. PocketTrack's privacy invariant forbids a
remote LLM, so this one is learned in a throwaway project **outside** this repo.
The invariant is not weakened to satisfy a syllabus.

## DESIGN.md build status

| Component | § | Status |
|---|---|---|
| `agents/registry.py` | 5.2 | `[ ]` |
| `agents/tools.py` | 7 | `[ ]` |
| `agents/runtime.py` | 5.1 | `[ ]` |
| `agents/copilot.py` | 7 | `[ ]` |
| `agents/sentinel.py` | 8 | `[ ]` |
| `agent_runs` table | 6 | `[ ]` |
| `agent_findings` table | 6 | `[ ]` |
| Copilot panel | 7 | `[ ]` |
| Review queue | 8 | `[ ]` |
| `AgentService` in bootstrap | 4 | `[ ]` |

## Decisions

Append-only. Never edit a row; add a new one.

| # | Date | Decision | Reasoning |
|---|---|---|---|
| 1 | 2026-08-25 | Follow **CLAUDE_P0's own numbering**; earlier M01–M26 curriculum dropped | User references CLAUDE_P0 directly. Old docs remain in git HEAD if needed |
| 2 | 2026-08-25 | §2.1 is learned **outside** this repo | Remote Claude API vs. the local-only privacy invariant |
| 3 | 2026-08-26 | Temperature 0, required-arg validation, and the iteration cap are **empirically confirmed**, not inherited | Reproduced on this machine in §1.1: 0.7 diverged across runs and across machines; model omitted a required arg and dropped the terminator |

## Session log

| Date | Did | Left off at |
|---|---|---|
| 2026-08-25 | Read DESIGN + CLAUDE_P0; recovered prior context from git; fixed venv (package not installed), baseline `126 passed`; confirmed Ollama + `qwen3.5:4b` present; set working agreement | Starting §1.1 |
| 2026-08-26 | **§1.1 done.** Two model-selection decisions (session driver vs. product model). User reproduced temp 0 vs 0.7 divergence on own hardware — same prompt gave `list_buckets()` at temp 0 both machines, `get_total` (no arg) at 0.7. Also observed terminator-drop and silent success on a malformed request | §1.1 complete; next §1.2 |
