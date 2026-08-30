---
description: Context-window discipline — measured rules for reading and searching files
globs:
  - "**/*"
---

# Rules — context discipline

From **M27**, measured on this repo's own transcripts. Full evidence and method:
`pocket-track/learn_and_build/SESSION-PLAYBOOK.md`. Decision: `STATE.md` DEC-08.

The finding these rest on: in session `d57f8449` (707 turns, peak 520,040 input
tokens) **tool output was ~86% of accumulated context and conversation only
~14%**. Sessions get expensive from reading, not from talking.

## Never `Read` a file to search it

Use `grep`, `rg`, or `sed -n` to return the matching lines. `Read` pulls the
whole file into context permanently.

Measured cost of ignoring this: `repositories.py` was read 6× for 14,935 tokens
when the answers wanted were a few lines each.

## Never `Read` a large or generated file

Logs, `.jsonl` transcripts, lockfiles, build output, anything over a few hundred
lines: aggregate it in Bash (`python3 -c`, `awk`, `jq`, `wc`) and return the
summary. One `Read` of a large file can consume the window and still answer less
than a five-line aggregation.

Measured: 19 MB of JSONL analyzed via Bash aggregation cost 13,833 tokens. The
same content via `Read` would have been ~5,000,000 tokens — 25× the window, i.e.
impossible. **Ratio ≈ 360:1.**

## Read a file at most once per session

A second read of an unchanged file is a signal to compact, or to write the
relevant extract to a scratch file — not to read it again.

Measured: 13 files were re-read in one session, costing **41,145 tokens, 63% of
all Read spend.**

## Offload before the window fills

Long analysis output belongs in a file, referenced by path. A path costs ~10
tokens; the content it points at cost thousands. Do this *before* the window is
tight, not after — auto-compact fires on token count, not at a task boundary, so
it can summarize away something load-bearing mid-thought.

## Fan out when the search is large and the answer is small

A subagent's exploration stays in its own context window; only its report enters
yours. The single `Agent` call in `d57f8449` returned 3,142 tokens for work that
would have cost far more inline.

## Clear between curriculum modules

Each `learn_and_build` module ends with a written artifact and a `STATE.md`
update, so the transcript has no residual value. The RESUME BLOCK makes a
cleared session free to restart: ~26,700 tokens fresh, versus 300K+ carrying a
finished module forward.
