# Design — PocketTrack Agentic Layer

**Status:** Design. No implementation authorised yet.
**Scope:** Two enhancements — Copilot (E1) and Sentinel (E2).
**Last updated:** 2026-08-24

---

## 1. Goals

| # | Goal |
|---|---|
| G1 | Let the user ask open-ended questions of their own financial data |
| G2 | Autonomously surface recurring-charge money leaks without being asked |
| G3 | Add **zero** new Python dependencies |
| G4 | Keep the app fully functional when the agent layer is unavailable |
| G5 | Exercise the agentic patterns in `CLAUDE_P0.md` on real, non-toy code |

## 2. Non-goals

- Multi-agent orchestration (deferred — see §11)
- Any remote LLM provider
- Automatic mutation of budgets, buckets, or transactions
- An agent framework of any kind

## 3. Inherited constraints

These come from the root `CLAUDE.md` and are non-negotiable.

| Constraint | Consequence for this design |
|---|---|
| Server binds `127.0.0.1` only | No new listeners, no callbacks |
| No financial data leaves the machine | Only permitted egress is `127.0.0.1:11434` (Ollama) |
| Secrets live in the OS keychain | Agent layer stores no secrets at all |
| Fail closed on encryption | Findings live in SQLCipher like everything else |
| `Unknown` bucket is load-bearing | Agent must never rename or delete it |
| Strict CSP, `style-src 'self'` | No inline styles in new templates |
| Schema changes need `ADDED_COLUMNS` | New tables + any later columns follow the existing pattern |

**Privacy assertion.** The agent layer introduces exactly one network destination:
the local Ollama daemon, already used by `categorization/ollama.py`. Enforced by a
pre-commit hook (curriculum M12), not by convention.

---

## 4. Architecture

One runtime, one tool registry, two drivers that differ only in **trigger** and
**tool scope**.

```
      HUMAN                                 SCHEDULER (launchd)
        │                                          │
        ▼                                          ▼
  ┌───────────────┐                        ┌──────────────────┐
  │  Copilot      │                        │  Sentinel        │
  │  reactive     │                        │  autonomous      │
  │  READ scope   │                        │  READ+WRITE      │
  └───────┬───────┘                        └────────┬─────────┘
          │                                         │
          │        ┌────────────────────┐           │
          └───────►│   AgentRuntime     │◄──────────┘
                   │  loop · cap · retry│
                   │  error contract    │
                   └─────────┬──────────┘
                             ▼
                   ┌────────────────────┐
                   │   ToolRegistry     │
                   │  scope enforcement │
                   └─────────┬──────────┘
                             ▼
        ┌────────────────────────────────────────┐
        │  EXISTING: repositories.py · SQLCipher │
        └────────────────────────────────────────┘
```

### Package layout

```
src/cardbudget/agents/
├── __init__.py
├── runtime.py      ~120  loop, iteration cap, error handling
├── registry.py      ~80  tool definitions, scope enforcement
├── tools.py        ~150  thin adapters over existing repositories
├── copilot.py       ~60  E1 driver
└── sentinel.py     ~110  E2 driver (deterministic scan + agentic investigation)
```

Wired into `services.py::bootstrap_services()` as a single `AgentService`,
constructed **last** so it can depend on every other repository.

---

## 5. Core components

### 5.1 AgentRuntime

```
run(goal: str,
    scope: ToolScope,
    max_iterations: int = 8) -> AgentResult
```

The loop:

1. Send messages to Ollama with a **schema-constrained** response format
2. Parse `{tool, args}` — the `tool` field is an `enum`, so the model cannot
   invent a tool name
3. `tool == "done"` → terminate, return the answer
4. Otherwise dispatch through the registry (scope-checked) and append the result
5. Repeat until `done`, cap reached, or unrecoverable error

`AgentResult` carries `steps`, `answer`, `error`, `hit_cap`, and `iterations` —
never a bare string, so callers can distinguish "no findings" from "failed".

**Why schema-constrained rather than native function calling:** the codebase already
proves this pattern works on a 4B model (`ollama.py` uses an `enum` on `bucket`).
Picking one item from a short enum is far more reliable on small models than
free-form tool calls. This choice is what may keep the model at 4B — see §10.

### 5.2 Tool contract

```
Tool = name | description | args_schema | capability | handler
capability ∈ { READ, WRITE }
```

The registry builds the response schema **per scope**, so a driver's enum contains
only the tools it is allowed to call. A Copilot attempt to call `create_finding`
is impossible at the schema level and rejected at dispatch as defence in depth.

> Covers anti-pattern 6 (universal tool availability), enforced in code rather
> than in a prompt.

### 5.3 Error contract

Every tool returns a `ToolResult`, never a raw value or an exception:

```
ToolResult = value | isError | isRetryable | errorCategory
errorCategory ∈ { not_found, bad_args, unavailable, permission, internal }
```

Errors are fed **back into the loop** as observations so the model can correct
course — a wrong merchant name should produce a retry with a better name, not a
crashed run. Unretryable errors terminate with the reason preserved in
`AgentResult.error`.

> Covers anti-pattern 5 (silent failures) and §4.3's error-structure requirement.

---

## 6. Data model

Two new tables, following existing `db/schema.py` conventions.

### `agent_runs` — observability

| column | notes |
|---|---|
| `id` | pk |
| `driver` | `copilot` \| `sentinel` |
| `started_at`, `ended_at` | |
| `iterations` | how many loop turns |
| `status` | `ok` \| `capped` \| `error` |
| `error` | nullable |

### `agent_findings` — Sentinel output

| column | notes |
|---|---|
| `id` | pk |
| `run_id` | fk → `agent_runs` |
| `kind` | `price_increase` \| `trial_converted` \| `duplicate` \| `zombie` |
| `merchant` | |
| `evidence` | JSON — the transactions that justify the claim |
| `impact_annual_cents` | integer, never a float |
| `status` | `new` \| `reviewed` \| `dismissed` \| `actioned` |

`evidence` is mandatory and non-empty. A finding that cannot cite the rows
supporting it is rejected before insert.

> Covers §4.3 information provenance and evidence-citation rules.

---

## 7. Enhancement 1 — Copilot

**Trigger:** user, from a panel on the dashboard.
**Scope:** READ only.
**Cap:** 8 iterations.

### Tools

| Tool | Returns |
|---|---|
| `list_buckets()` | bucket names |
| `bucket_summary(bucket, period)` | total spend |
| `query_transactions(bucket?, merchant?, period, limit)` | rows |
| `merchant_history(merchant, months)` | dated amounts |
| `detect_recurring(merchant)` | periodicity + amount stats (deterministic) |
| `net_worth_series(months)` | balances over time |
| `done(answer)` | terminates |

### Flow

```
"Am I spending more on food than last quarter?"
   → bucket_summary(Food, Q2)      $1,240
   → bucket_summary(Food, Q3)      $1,690
   → query_transactions(Food, Q3)  DOORDASH ×23     ← model chose to dig
   → done("Up 36%, almost all DoorDash")
```

Step 3 exists because of step 2's result. No code path encodes "if spike, drill down".

### Interface

A panel on the dashboard, not a new page. Tool calls are shown as they happen —
the user sees *how* the answer was reached, which is both a trust feature and the
provenance requirement made visible.

### Degradation

| Condition | Behaviour |
|---|---|
| Ollama down | Panel shows "Copilot unavailable", rest of app normal |
| Cap reached | Partial answer + "stopped after 8 steps" |
| Tool error | Fed back to the model; if fatal, plain error, no crash |

---

## 8. Enhancement 2 — Sentinel

**Trigger:** `daily-sync`, via existing launchd scheduler. No human present.
**Scope:** READ + WRITE.
**Cap:** 12 iterations.

### Two-stage design

```
┌─────────────────────────────────────────────────┐
│ STAGE 1 — DETERMINISTIC       cheap, exhaustive │
│ · interval variance     · amount clustering     │
│ · first-charge detection                        │
│                                                 │
│   47 merchants ──► 5 the math cannot classify   │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│ STAGE 2 — AGENTIC            costly, flexible   │
│ · investigates each candidate its own way       │
│ · chooses depth per candidate                   │
│ · writes findings, terminates itself            │
└──────────────────────┬──────────────────────────┘
                       ▼
              review queue (human, next login)
```

Stage 1 is plain Python and never calls the model. Stage 2 receives only the
ambiguous residue. Running the loop over all 47 merchants would be slower,
costlier, **and less reliable** than the arithmetic.

> Covers anti-pattern 1 (programmatic validation, not prompt enforcement) and
> anti-pattern 2 (numeric thresholds, never self-reported confidence).

### Additional WRITE tools

| Tool | Effect |
|---|---|
| `create_finding(kind, merchant, evidence, impact)` | Insert — rejected if `evidence` empty |
| `propose_merchant_rule(merchant, bucket)` | Creates a **proposal**, never applies a rule |
| `done(summary)` | Terminates |

No Sentinel tool mutates a transaction, bucket, or budget. Every write lands in a
queue a human approves. The agent's autonomy is over *investigation*, not over the
user's money.

> Covers §3.7 approval gates and least-privilege.

### Escalation

Deterministic and numeric — never "how confident are you?":

| Rule | Action |
|---|---|
| `impact_annual < $12` | recorded, not surfaced |
| `kind == trial_converted` | always `needs_review` |
| `evidence rows < 2` | discarded |
| stage 1 flags, stage 2 finds nothing | logged as a near-miss, not a finding |

### Degradation

| Condition | Behaviour |
|---|---|
| Ollama down | Stage 1 still runs; deterministic findings only |
| Cap reached | Findings so far are kept; run marked `capped` |
| Model too weak (probe fails) | Stage 2 disabled by config; app unaffected |

That last row matters: **Sentinel is useful even with the LLM entirely removed.**

---

## 9. Weight budget

| | Cost |
|---|---|
| New dependencies | **0** |
| Production code | ~520 lines (+9% of 5,548) |
| New tables | 2 |
| New templates | 2 (copilot panel, review queue) |
| New services | 1 (`AgentService`) |
| Model disk | 0 GB if the 4B probe passes, else ~9 GB |

Guard rails that keep it there:

1. Tools are adapters — business logic stays in existing services
2. Deterministic work never becomes an LLM call
3. One runtime, two drivers; a third agent costs ~60 lines
4. Strictly additive — no existing code path calls into `agents/`

---

## 10. Open decisions

| # | Question | Blocked on | Default if unresolved |
|---|---|---|---|
| D1 | Can `qwen3.5:4b` chain tool calls? | `probe_tool_calling.py` — model not yet pulled | Ship Sentinel stage 1 only; Copilot single-step |
| D2 | Conversation memory for Copilot? | D1 | Stateless per question |
| D3 | Sentinel cadence — daily or weekly? | Real finding volume | Weekly, to avoid noise |

**D1 gates everything.** Run the probe before writing runtime code.

---

## 11. Deferred

| Idea | Why deferred | Would unlock |
|---|---|---|
| Month-End Analyst (multi-agent) | Needs the runtime first | §4.1 orchestration, anti-pattern 7 |
| Goal Planner | Needs approval-gate infra from E2 | Deeper §3.7 |
| Statement Reconciler | Needs a vision model (heavy) | §4.3 provenance depth |
