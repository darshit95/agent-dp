# STATE — Learn & Build

> Single source of truth for progress. Read this first in any session.
> Update it at the end of every session.

---

## ▶ RESUME BLOCK

```
PHASE          0 — Ground rules
CURRENT MODULE M04 — Model capability probe
LAST DONE      Probe written and verified ready. Blocked on the corp machine (no model)
PLAN           Continue on a machine that already has an Ollama model installed

NEXT ACTION    1. ollama list                       ← note the exact model name
               2. python3 probe_tool_calling.py --reps 3 --model <name>
               3. record verdict in D1 + session log
               4. update DESIGN §10 only if verdict is MARGINAL / NO-GO
               5. start M01
```

**M04 stays first by choice.** Decision **D1** determines whether the runtime design
works on a small local model. Rule 3 (*blocked ≠ skipped*) would divert to
M01–M03/M05/M06, which need no model — but the user elected on 2026-08-24 to settle
D1 before any module, so nothing in Phase 0 is configured for an architecture that
may not be viable. **Do not start M01 until the verdict is recorded.**

### Machines

| | Machine A — corp laptop | Machine B — target |
|---|---|---|
| Ollama | installed (`/opt/homebrew/bin/ollama`) | installed, **model present** |
| Models | none, and none obtainable | yes — run `ollama list` to get the name |
| Probe | cannot run | **run here** |

**On Machine B, before running the probe:**

- [ ] `git pull` — confirm `learn_and_build/` and `probe_tool_calling.py` are present
- [ ] `ollama list` — the probe defaults to `qwen3.5:4b`; pass `--model <name>` if it differs
- [ ] If the model is a **sideloaded GGUF**, note the quantization — a MARGINAL result
      may be the quant, not the model. Record which one in D1
- [ ] No `.venv` needed — the probe is stdlib-only

**Machine A network blocker (diagnosed 2026-08-24)** — applies to Machine A only:

- Python TLS → `CERTIFICATE_VERIFY_FAILED: Missing Authority Key Identifier` (re-signed chain)
- `dd20bdkz54p7d.cloudfront.net` (Ollama blob CDN) → does not resolve
- `ollama pull` fetches the **manifest** fine, then every blob part dies with `EOF` after 5 retries
- Reproduced with `qwen3.5:4b` (3.4 GB) **and** `qwen3:0.6b` (~0.5 GB) → blanket CDN
  block, not a size or content limit
- `huggingface.co` and `cdn-lfs-us-1.hf.co` **do** resolve, so `ollama pull hf.co/<repo>:<quant>`
  or a Chrome download + `ollama create` may work if Machine A is ever needed

Do **not** disable certificate verification to get around this.

---

## Decisions

Append-only. Each entry records what was chosen **and why**, so a later session does
not relitigate it.

| # | Date | Decision | Reasoning |
|---|---|---|---|
| DEC-01 | 2026-08-24 | **Local Ollama only.** No remote LLM in pocket-track | Privacy invariant in root `CLAUDE.md` outranks curriculum coverage. Claude API topics move to M25, outside this repo |
| DEC-02 | 2026-08-24 | Build **Copilot (E1) + Sentinel (E2)** only | Two features, one shared runtime. Ideas 3–5 deferred; M24 revisits multi-agent |
| DEC-03 | 2026-08-24 | **No agent framework** | The loop is ~120 lines. LangChain et al. would add 30–60 transitive deps to hide the exact thing being learned. Also satisfies goal G3 (zero new deps) |
| DEC-04 | 2026-08-24 | **Hybrid** — deterministic scan feeds agentic investigation | Running the loop over all merchants is slower, costlier and *less reliable* than arithmetic. Loop goes where the uncertainty is |
| DEC-05 | 2026-08-24 | **Schema-constrained tool selection**, not native function calling | `ollama.py` already proves enum-constrained output works on 4B. May keep the model at +0 GB — pending D1 |

## Open questions

| # | Question | Blocks | Default if unresolved |
|---|---|---|---|
| D1 | Can `qwen3.5:4b` chain tool calls reliably? **Blocked: no model obtainable on this network — see Environment.** Probe is written and ready; needs only a model present | M07 onward | Sentinel stage 1 only; Copilot single-step |
| D2 | Conversation memory for Copilot? | M12 | Stateless per question |
| D3 | Sentinel cadence — daily or weekly? | M19 | Weekly |

---

## Curriculum progress

`[ ]` not started · `[~]` in progress · `[x]` done + evidence · `[!]` blocked

### Phase 0 — Ground rules
| | Module | Evidence |
|---|---|---|
| `[ ]` | M01 Project rulebook | |
| `[ ]` | M02 Permissions & settings | |
| `[ ]` | M03 Memory | |

### Phase 1 — Foundations
| | Module | Evidence |
|---|---|---|
| `[!]` | M04 Model capability probe | script: `probe_tool_calling.py` · **blocked: D1** |
| `[ ]` | M05 Skills | |
| `[ ]` | M06 Subagents | |
| `[ ]` | M07 Tool design & registry | |
| `[ ]` | M08 The agentic loop | |

### Phase 2 — Copilot (E1)
| | Module | Evidence |
|---|---|---|
| `[ ]` | M09 Driver prompt & profiles | |
| `[ ]` | M10 Validation & retry | |
| `[ ]` | M11 Error contract | |
| `[ ]` | M12 Context management | |
| `[ ]` | M13 Hooks | |
| `[ ]` | M14 **Ship E1** | |

### Phase 3 — Sentinel (E2)
| | Module | Evidence |
|---|---|---|
| `[ ]` | M15 Deterministic detection | |
| `[ ]` | M16 Escalation & calibration | |
| `[ ]` | M17 WRITE tools & approval gates | |
| `[ ]` | M18 Provenance | |
| `[ ]` | M19 Autonomy & degradation | |
| `[ ]` | M20 **Ship E2** | |

### Phase 4 — Production
| | Module | Evidence |
|---|---|---|
| `[ ]` | M21 MCP | |
| `[ ]` | M22 CI/CD | |
| `[ ]` | M23 Observability | |

### Phase 5 — Gap closure
| | Module | Evidence |
|---|---|---|
| `[ ]` | M24 Multi-agent | |
| `[ ]` | M25 Claude API & cost *(outside this repo)* | |
| `[ ]` | M26 Anti-pattern audit | |

**0 / 26 complete.**

---

## Design implementation

Tracks `DESIGN.md` §4–§8. Nothing is authorised until D1 resolves.

| Component | Design § | Status |
|---|---|---|
| `agents/runtime.py` | §5.1 | `[ ]` |
| `agents/registry.py` | §5.2 | `[ ]` |
| `agents/tools.py` | §7 | `[ ]` |
| `agents/copilot.py` | §7 | `[ ]` |
| `agents/sentinel.py` | §8 | `[ ]` |
| `agent_runs` table | §6 | `[ ]` |
| `agent_findings` table | §6 | `[ ]` |
| Copilot panel | §7 | `[ ]` |
| Review queue | §8 | `[ ]` |
| `AgentService` in bootstrap | §4 | `[ ]` |

**Invariant checks** — re-verify before every commit:

- [ ] No network destination other than `127.0.0.1:11434`
- [ ] No new Python dependency
- [ ] App fully functional with `agents/` removed
- [ ] No inline `style` attributes in new templates
- [ ] New tables registered per `db/schema.py` conventions

---

## Session log

One line per session. Newest last.

| Date | Did | Left off at |
|---|---|---|
| 2026-08-24 | Scoped 5 ideas → chose E1+E2; coverage audit vs CLAUDE_P0 (~58% from features alone); wrote DESIGN, CURRICULUM, STATE; authored probe | D1 blocked — model not pulled |
| 2026-08-24 | Attempted M04. Started Ollama daemon; pull fails on every model. Diagnosed TLS-intercepting proxy + blocked blob CDN; confirmed not size-related via 0.6 GB model. Probe verified working — its preflight caught both gaps correctly | D1 parked on network; proceed to M01 |
| 2026-08-24 | User chose to resolve D1 before any module rather than take the rule-3 diversion. Nothing else started | Awaiting `ollama pull` from an unrestricted network |
| 2026-08-24 | Ollama app reinstall on Machine A did not help — it installs the runtime, not a model; CDN still blocked. Found HF hosts reachable (possible sideload route). Decided to continue on Machine B, which already has a model. STATE made machine-aware | Handoff to Machine B; probe is the first action there |

---

## How to update this file

At the end of a session, change only what actually moved:

1. **RESUME BLOCK** — current module, last done, blocker, next action
2. **Progress table** — flip the marker, add the evidence path
3. **Decisions** — append if something was chosen; never edit an old row
4. **Session log** — one line

Keep the resume block honest. If a module is half-built, it is `[~]`, not `[x]`.
