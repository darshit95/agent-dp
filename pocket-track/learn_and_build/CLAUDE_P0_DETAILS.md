##1.1 — Basic Claude Code Usage & Model Selection

Kind: Harness. This produces no agents/ code. It changes how you drive the tool for every section after it — including the ones that do build Copilot.

The concept
The core idea in §1.1 is right-sizing capability to task complexity. There are two model-selection decisions in this project, and conflating them is the most common mistake:

Decision 1 — which Claude model drives your Claude Code session. You're on Opus 5 now. The tradeoff:

Model	Use for	Why
Opus	Architecture, design review, debugging a subtle failure, writing the agentic loop	Deepest reasoning; you're paying for judgment
Sonnet	Bulk edits, applying a pattern you already decided, test scaffolding	Much faster/cheaper; the thinking is already done
Haiku	Mechanical transforms, formatting, simple lookups	Cheapest; no judgment required
The rule: use the expensive model to decide, the cheap model to execute. Deciding registry.py's scope-enforcement design is Opus work. Writing the twelfth similar tool adapter afterward is not.

/model switches mid-session. Context carries over — you don't lose the conversation.