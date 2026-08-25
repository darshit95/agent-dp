# Learn & Build — PocketTrack Agentic Layer

Learn every concept in `CLAUDE_P0.md` by building two real features into PocketTrack.
Nothing here is theory-only: each curriculum module produces a committed artifact.

## The three documents

| File | Answers |
|---|---|
| [`DESIGN.md`](DESIGN.md) | **What** we are building — Copilot + Sentinel, design only |
| [`CURRICULUM.md`](CURRICULUM.md) | **How** we learn it — 24 modules, sequenced so each one builds the next piece |
| [`STATE.md`](STATE.md) | **Where** we are — the resume point, decisions made, what's next |

## Starting a session

Paste this as your first message:

```
Read pocket-track/learn_and_build/STATE.md and resume.
```

`STATE.md` opens with a RESUME BLOCK naming the current module, the last thing
finished, and the single next action. That is enough to continue with no other context.

## Ending a session

```
Update learn_and_build/STATE.md with what we did.
```

Three things get written: module status, any decision made (with its reasoning),
and one line in the session log. If a module finished, its **evidence** — a file
path, test name, or commit — goes in the progress table. No evidence, not done.

## The loop

```
   ┌──────────────────────────────────────────────┐
   │  read STATE.md  →  next module               │
   │        │                                     │
   │        ▼                                     │
   │  learn the topics (CURRICULUM.md)            │
   │        │                                     │
   │        ▼                                     │
   │  build the artifact (DESIGN.md)              │
   │        │                                     │
   │        ▼                                     │
   │  verify "done when"  →  record evidence      │
   │        │                                     │
   │        └──────► update STATE.md ─────────────┤
   └──────────────────────────────────────────────┘
```

## Two rules that keep this honest

1. **Evidence or it didn't happen.** A module is `[x]` only when a real artifact
   exists in the repo. Reading about hooks is not learning hooks.
2. **Design is a contract, not a wish.** If the build diverges from `DESIGN.md`,
   update the design and log why. Never let the two drift silently.
