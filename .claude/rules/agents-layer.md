---
description: Invariants for the PocketTrack agentic layer (src/cardbudget/agents/**)
globs:
  - "pocket-track/src/cardbudget/agents/**/*.py"
  - "pocket-track/tests/**/test_agent*.py"
---

# Rules — agentic layer

Scope: `src/cardbudget/agents/**` and its tests. These encode `DESIGN.md` §3–§5
and the measured findings DEC-06 / REQ-1-2-3 in `STATE.md`. They are invariants,
not preferences — each one exists because violating it broke something real.

## Egress

**The only network destination this layer may reach is `127.0.0.1:11434`.**

The root `CLAUDE.md` privacy invariant outranks every other consideration here,
including curriculum coverage (DEC-01). Concretely:

- No `httpx`/`requests`/`urllib` call to any other host, in any code path,
  including retries, telemetry, error reporting, and model fallback.
- No "just for debugging" remote endpoint. There is no debug exception.
- If a task appears to require a remote LLM, stop and record it as a decision in
  `STATE.md` instead of implementing it.

## Dependencies

**No new Python dependency.** Goal G3, and DEC-03: the loop is ~120 lines, and an
agent framework would add 30–60 transitive packages to hide the exact mechanism
this project exists to learn. Standard library plus what `pyproject.toml` already
declares.

## Runtime invariants (measured — do not relitigate)

These came out of the M04 probe with numbers attached. See `STATE.md` DEC-06.

- **REQ-1 — required-arg validation in `registry.py`.** Every tool declares its
  required args. A call missing one is rejected with a message naming the missing
  arg; it is **never** executed with the arg absent. Rationale: an empty result is
  indistinguishable from "no data" and sent the model into a month-guessing
  spiral. Validation moved termination 1/4 → 5/6 at temperature 0.7.
- **REQ-2 — hard iteration cap in `runtime.py`, with explicit degradation.** On
  hitting the cap the loop returns "could not determine", never nothing and never
  a bare string.
- **Do NOT add a repeat-call guard.** Blocking duplicate `(tool, args)` was
  measured at 1/4 termination — worse than baseline. It pushes the model to
  invent fresh arguments and keep fishing.
- **REQ-3 — the agent loop runs at temperature 0.** The temp-0 vs temp-0.7
  divergence is the entire M04 finding.

## Enforcement in code, not in prompts

The M04 probe demonstrated this directly: the system prompt instructed "never
call the same tool with the same arguments twice" and the model did it anyway.

**Prompt instructions are not an enforcement mechanism.** Anything that must hold
— scope, required args, iteration caps, write protection — is enforced in Python
by the registry or the runtime. A rule that lives only in a prompt string is a
suggestion, and must be treated as one when reasoning about safety.

## Tool scope

- `capability` is `READ` or `WRITE`; the registry builds the response schema
  **per scope**, so a driver's enum contains only tools it may call.
- **Copilot is READ-only and must be structurally unable to express a WRITE
  tool** — not merely blocked at dispatch. Enforce at the schema level, then
  again at dispatch as defence in depth (anti-pattern AP6).
- No agent path mutates a transaction, bucket, or budget. Sentinel's WRITE tools
  propose (`create_finding`, `propose_merchant_rule`); a human approves.

## Data model

- The `Unknown` bucket is load-bearing (`monthly_summary` and the categorization
  fallback both resolve it by literal name). Never rename or delete it.
- New tables follow the `db/schema.py` conventions; any later column added to an
  existing table needs an entry in `schema.ADDED_COLUMNS`, because
  `CREATE TABLE IF NOT EXISTS` will not alter an existing database.
- Findings live in SQLCipher like everything else. Fail closed — never fall back
  to plaintext.

## Removability

**The app must remain fully functional with `agents/` deleted.** This is the
check that keeps the layer additive. If removing the directory breaks a route, a
template, or a test outside `agents/`, the coupling is a bug.

## Templates

Strict CSP (`style-src 'self'`) — **no inline `style` attributes** in any new
template. Use classes, or SVG presentation attributes as the donut and
`<progress>` bars already do.

## Before every commit touching this layer

- [ ] No network destination other than `127.0.0.1:11434`
- [ ] No new Python dependency
- [ ] App fully functional with `agents/` removed
- [ ] No inline `style` attributes in new templates
- [ ] New tables registered per `db/schema.py` conventions
