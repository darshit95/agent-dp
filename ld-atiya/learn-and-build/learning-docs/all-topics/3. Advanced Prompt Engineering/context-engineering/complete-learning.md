# Context Engineering - Complete Learning

**Last Updated:** 2026-08-20  
**Purpose:** Deep production-grade learning of Context Engineering with Atiya implementation examples

This document provides comprehensive coverage of Context Engineering - the practice of intelligently selecting, structuring, and delivering relevant information to LLMs for optimal performance at minimal cost.

---

## 1. Problem and Overview

### 1.1 What is Context Engineering?

Context Engineering is the systematic practice of gathering, filtering, structuring, and delivering relevant information to Large Language Models to maximize task performance while minimizing token cost.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE CONTEXT ENGINEERING PROBLEM                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SCENARIO: Test failure diagnosis in Atiya                                  │
│                                                                             │
│  Available Evidence:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ • Test log file:           50,000 lines  (125,000 tokens)          │    │
│  │ • Test code:                1,200 lines  (3,000 tokens)             │    │
│  │ • Topology YAML:              800 lines  (2,000 tokens)             │    │
│  │ • Device config dump:      10,000 lines  (25,000 tokens)            │    │
│  │ • Previous run log:        40,000 lines  (100,000 tokens)           │    │
│  │                                                                     │    │
│  │ Total if sent raw: 255,000 tokens × $3/1M = $0.77 per diagnosis    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ❌ NAIVE APPROACH: Send everything                                         │
│     • Exceeds context window (200K limit)                                   │
│     • High cost ($0.77 per analysis)                                        │
│     • Poor signal-to-noise ratio                                            │
│     • Slow processing                                                       │
│                                                                             │
│  ✅ CONTEXT ENGINEERING: Send only what matters                             │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ SMART SELECTION:                                                    │    │
│  │                                                                     │    │
│  │ • Test log: Extract ERROR/FAILED sections only    → 500 lines      │    │
│  │ • Test code: Include test function + fixtures     → 200 lines      │    │
│  │ • Topology: Relevant device config only           → 100 lines      │    │
│  │ • Device config: Skip if not config-related       → 0 lines        │    │
│  │ • Previous run: Comparison summary only           → 50 lines       │    │
│  │                                                                     │    │
│  │ Optimized context: 850 lines = ~2,100 tokens                       │    │
│  │ Cost: 2,100 tokens × $3/1M = $0.006 per diagnosis                  │    │
│  │                                                                     │    │
│  │ 💰 SAVINGS: 99.2% cost reduction                                   │    │
│  │ ⚡ SPEED: 120× faster processing                                   │    │
│  │ 🎯 ACCURACY: Better signal-to-noise ratio                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Why Context Matters for LLM Performance

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   CONTEXT QUALITY vs LLM PERFORMANCE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                    TOO LITTLE CONTEXT                             │      │
│  │                                                                   │      │
│  │  User: "Why did my test fail?"                                    │      │
│  │  LLM:  "I need more information. Can you provide:                 │      │
│  │         - The test log                                            │      │
│  │         - The test code                                           │      │
│  │         - The error message"                                      │      │
│  │                                                                   │      │
│  │  ❌ Result: Multiple round-trips, slow diagnosis                  │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                    TOO MUCH CONTEXT                               │      │
│  │                                                                   │      │
│  │  User: "Why did my test fail?" + 200,000 tokens of logs           │      │
│  │  LLM:  "Looking through the logs... [processing]...               │      │
│  │         The error appears to be on line 45,231..."                │      │
│  │                                                                   │      │
│  │  ❌ Result: High cost, slow, buried signal                        │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                    OPTIMIZED CONTEXT                              │      │
│  │                                                                   │      │
│  │  User: "Why did my test fail?"                                    │      │
│  │                                                                   │      │
│  │  Context provided:                                                │      │
│  │  • Test function (50 lines)                                       │      │
│  │  • Error traceback (20 lines)                                     │      │
│  │  • Failed assertion section (10 lines)                            │      │
│  │  • Relevant device state (30 lines)                               │      │
│  │                                                                   │      │
│  │  LLM: "Root cause: SSL certificate mismatch.                      │      │
│  │        Expected: CN=*.prisma.local                                │      │
│  │        Actual: CN=localhost                                       │      │
│  │        Fix: Update topology.yaml cert_name parameter"             │      │
│  │                                                                   │      │
│  │  ✅ Result: Fast, accurate, actionable diagnosis                  │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              PERFORMANCE COMPARISON                               │      │
│  │                                                                   │      │
│  │  Context Type    │ Tokens │  Cost  │ Time │ Accuracy │           │      │
│  │  ───────────────┼────────┼────────┼──────┼──────────┤           │      │
│  │  Too Little      │   500  │ $0.002 │  15s │   40%    │           │      │
│  │  Too Much        │200,000 │ $0.600 │  45s │   70%    │           │      │
│  │  Optimized       │  2,500 │ $0.008 │   8s │   95%    │ ← Winner  │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Insight:** Context quality matters more than context quantity. The right 2,500 tokens outperform 200,000 irrelevant tokens.

### 1.3 Cost of Context (Tokens = Money)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TOKEN ECONOMICS IN PRODUCTION                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Claude Sonnet 4.6 Pricing (as of 2026-08):                                 │
│  • Input tokens:  $3.00 per 1M tokens                                       │
│  • Output tokens: $15.00 per 1M tokens                                      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │            ATIYA PRODUCTION SCENARIO                              │      │
│  │                                                                   │      │
│  │  Daily test failures: 500 tests                                   │      │
│  │  Diagnosis per test needed                                        │      │
│  │                                                                   │      │
│  │  ┌────────────────────────────────────────────────────────────┐   │      │
│  │  │ OPTION A: No Context Engineering                          │   │      │
│  │  │                                                            │   │      │
│  │  │ Per diagnosis:                                             │   │      │
│  │  │   Input:  50,000 tokens (full log)                         │   │      │
│  │  │   Output:  1,000 tokens (analysis)                         │   │      │
│  │  │                                                            │   │      │
│  │  │ Cost per diagnosis:                                        │   │      │
│  │  │   Input:  50,000 / 1M × $3   = $0.150                      │   │      │
│  │  │   Output:  1,000 / 1M × $15  = $0.015                      │   │      │
│  │  │   Total: $0.165                                            │   │      │
│  │  │                                                            │   │      │
│  │  │ Daily cost: 500 × $0.165 = $82.50                          │   │      │
│  │  │ Monthly cost: $82.50 × 22 = $1,815                         │   │      │
│  │  │ Annual cost: $1,815 × 12 = $21,780                         │   │      │
│  │  └────────────────────────────────────────────────────────────┘   │      │
│  │                                                                   │      │
│  │  ┌────────────────────────────────────────────────────────────┐   │      │
│  │  │ OPTION B: With Context Engineering                        │   │      │
│  │  │                                                            │   │      │
│  │  │ Per diagnosis:                                             │   │      │
│  │  │   Input:  2,500 tokens (extracted errors + context)        │   │      │
│  │  │   Output:  1,000 tokens (analysis)                         │   │      │
│  │  │                                                            │   │      │
│  │  │ Cost per diagnosis:                                        │   │      │
│  │  │   Input:  2,500 / 1M × $3   = $0.0075                      │   │      │
│  │  │   Output:  1,000 / 1M × $15 = $0.015                       │   │      │
│  │  │   Total: $0.0225                                           │   │      │
│  │  │                                                            │   │      │
│  │  │ Daily cost: 500 × $0.0225 = $11.25                         │   │      │
│  │  │ Monthly cost: $11.25 × 22 = $247.50                        │   │      │
│  │  │ Annual cost: $247.50 × 12 = $2,970                         │   │      │
│  │  └────────────────────────────────────────────────────────────┘   │      │
│  │                                                                   │      │
│  │  💰 SAVINGS:                                                      │      │
│  │     • Per diagnosis: $0.165 → $0.0225 (86% reduction)             │      │
│  │     • Daily: $71.25 saved                                         │      │
│  │     • Monthly: $1,567.50 saved                                    │      │
│  │     • Annual: $18,810 saved                                       │      │
│  │                                                                   │      │
│  │  ROI on Context Engineering Implementation:                       │      │
│  │     • Development cost: ~40 hours × $150/hr = $6,000              │      │
│  │     • Payback period: 8.4 days                                    │      │
│  │     • 1-year ROI: 314%                                            │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                    TOKEN BREAKDOWN                                │      │
│  │                                                                   │      │
│  │  1 token ≈ 4 characters or 0.75 words                             │      │
│  │                                                                   │      │
│  │  Common file sizes in tokens:                                     │      │
│  │  • 1,000 line log file:     ~2,500 tokens                         │      │
│  │  • 500 line Python file:    ~1,250 tokens                         │      │
│  │  • 200 line YAML file:        ~500 tokens                         │      │
│  │  • Error traceback (30 ln):   ~100 tokens                         │      │
│  │                                                                   │      │
│  │  Atiya test failure evidence:                                     │      │
│  │  • Full test log:           50,000 tokens ($0.15 input)           │      │
│  │  • Extracted errors:         2,000 tokens ($0.006 input)          │      │
│  │  • 25× reduction in cost                                          │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Critical Takeaway:** Context Engineering isn't optional at scale. For 500 diagnoses/day, it's the difference between $82.50/day and $11.25/day - a savings of $18,810 annually.

---

## 2. What is Context Engineering?

### 2.1 Definition

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT ENGINEERING DEFINITION                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Context Engineering is the discipline of:                                  │
│                                                                             │
│  1. GATHERING - Identifying all potentially relevant information            │
│  2. FILTERING - Selecting only what's necessary for the task                │
│  3. STRUCTURING - Organizing information for optimal comprehension          │
│  4. DELIVERING - Presenting context to maximize LLM performance             │
│                                                                             │
│  Goal: Maximum task success at minimum token cost                           │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                      THE 4 PILLARS                                │      │
│  │                                                                   │      │
│  │   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐      │      │
│  │   │GATHERING │ → │FILTERING │ → │STRUCTURING│ → │DELIVERING│      │      │
│  │   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘      │      │
│  │        │              │              │              │             │      │
│  │        ▼              ▼              ▼              ▼             │      │
│  │   Find all        Select        Organize        Present          │      │
│  │   relevant       necessary      for clarity     optimally        │      │
│  │   sources        pieces only                                     │      │
│  │                                                                   │      │
│  │   Test log       Skip debug     Add metadata   System prompt     │      │
│  │   Test code      Keep errors    Group by type  + Evidence        │      │
│  │   Topology       Skip success   Add line #s    = LLM call        │      │
│  │   Config         Keep critical  Priority order                   │      │
│  │   Prior runs     Summarize                                       │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Scope vs Prompt Engineering

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              PROMPT ENGINEERING vs CONTEXT ENGINEERING                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PROMPT ENGINEERING                               │    │
│  │                                                                     │    │
│  │  Focus: HOW you ask the LLM to perform the task                     │    │
│  │                                                                     │    │
│  │  Concerns:                                                          │    │
│  │  • System prompt design                                             │    │
│  │  • Instruction clarity                                              │    │
│  │  • Output format specification                                      │    │
│  │  • Few-shot examples                                                │    │
│  │  • Role definition                                                  │    │
│  │  • Constraint specification                                         │    │
│  │                                                                     │    │
│  │  Example:                                                           │    │
│  │  ┌────────────────────────────────────────────────────────────┐     │    │
│  │  │ System: You are a PARTS test failure expert.              │     │    │
│  │  │         Analyze the evidence and provide:                 │     │    │
│  │  │         1. Root cause                                     │     │    │
│  │  │         2. Affected component                             │     │    │
│  │  │         3. Recommended fix                                │     │    │
│  │  │                                                            │     │    │
│  │  │ Output format: JSON with fields {cause, component, fix}   │     │    │
│  │  └────────────────────────────────────────────────────────────┘     │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    CONTEXT ENGINEERING                              │    │
│  │                                                                     │    │
│  │  Focus: WHAT information you provide to the LLM                     │    │
│  │                                                                     │    │
│  │  Concerns:                                                          │    │
│  │  • Evidence selection                                               │    │
│  │  • Information density                                              │    │
│  │  • Token optimization                                               │    │
│  │  • Relevance filtering                                              │    │
│  │  • Context organization                                             │    │
│  │  • Metadata enrichment                                              │    │
│  │                                                                     │    │
│  │  Example:                                                           │    │
│  │  ┌────────────────────────────────────────────────────────────┐     │    │
│  │  │ Evidence:                                                  │     │    │
│  │  │                                                            │     │    │
│  │  │ [Test Log - Lines 4521-4548]                              │     │    │
│  │  │ ERROR: SSL handshake failed                               │     │    │
│  │  │ Expected CN: *.prisma.local                               │     │    │
│  │  │ Received CN: localhost                                    │     │    │
│  │  │                                                            │     │    │
│  │  │ [Test Code - test_ssl_connection:45-67]                   │     │    │
│  │  │ def test_ssl_connection(topology):                        │     │    │
│  │  │     client.connect(topology.gateway.ip, verify_ssl=True)  │     │    │
│  │  │                                                            │     │    │
│  │  │ [Topology - gateway.yaml:12-18]                           │     │    │
│  │  │ gateway:                                                  │     │    │
│  │  │   cert_name: localhost                                    │     │    │
│  │  │   # Should be: *.prisma.local                             │     │    │
│  │  └────────────────────────────────────────────────────────────┘     │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      THEY WORK TOGETHER                             │    │
│  │                                                                     │    │
│  │         ┌──────────────┐           ┌──────────────┐                 │    │
│  │         │   PROMPT     │     +     │   CONTEXT    │                 │    │
│  │         │ ENGINEERING  │           │ ENGINEERING  │                 │    │
│  │         └──────┬───────┘           └──────┬───────┘                 │    │
│  │                │                          │                         │    │
│  │                │   "How to ask"           │   "What to provide"     │    │
│  │                │                          │                         │    │
│  │                └─────────┬────────────────┘                         │    │
│  │                          │                                          │    │
│  │                          ▼                                          │    │
│  │                ┌──────────────────┐                                 │    │
│  │                │  COMPLETE LLM    │                                 │    │
│  │                │  REQUEST         │                                 │    │
│  │                │                  │                                 │    │
│  │                │  System: [HOW]   │                                 │    │
│  │                │  User: [WHAT]    │                                 │    │
│  │                └──────────────────┘                                 │    │
│  │                          │                                          │    │
│  │                          ▼                                          │    │
│  │                   High-quality output                               │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  KEY DISTINCTION:                                                           │
│  • Prompt Engineering: The instructions                                     │
│  • Context Engineering: The data                                            │
│  • Both essential for production AI systems                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Key Principles

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  CONTEXT ENGINEERING PRINCIPLES                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. RELEVANCE FIRST                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │  Include only information directly relevant to the task            │      │
│  │                                                                   │      │
│  │  ✅ Error traceback for debugging                                 │      │
│  │  ✅ Failed test function code                                     │      │
│  │  ✅ Related configuration                                         │      │
│  │                                                                   │      │
│  │  ❌ Full 50K line log when only errors matter                     │      │
│  │  ❌ Passing test output                                           │      │
│  │  ❌ Unrelated configuration sections                              │      │
│  │                                                                   │      │
│  │  Metric: Relevance ratio = Useful tokens / Total tokens           │      │
│  │  Target: > 80% relevance                                          │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  2. SIGNAL-TO-NOISE OPTIMIZATION                                            │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │  Maximize information density                                     │      │
│  │                                                                   │      │
│  │  BAD (low signal):                                                │      │
│  │  ┌─────────────────────────────────────────────────────────┐      │      │
│  │  │ [2026-08-20 10:23:45] INFO: Starting test                │      │      │
│  │  │ [2026-08-20 10:23:46] DEBUG: Connecting to device        │      │      │
│  │  │ [2026-08-20 10:23:47] DEBUG: Connection established      │      │      │
│  │  │ [2026-08-20 10:23:48] DEBUG: Sending command             │      │      │
│  │  │ ... 500 more DEBUG lines ...                             │      │      │
│  │  │ [2026-08-20 10:28:12] ERROR: Timeout waiting for response│      │      │
│  │  └─────────────────────────────────────────────────────────┘      │      │
│  │  Signal: 1 line out of 500 = 0.2%                                 │      │
│  │                                                                   │      │
│  │  GOOD (high signal):                                              │      │
│  │  ┌─────────────────────────────────────────────────────────┐      │      │
│  │  │ [2026-08-20 10:28:12] ERROR: Timeout waiting for response│      │      │
│  │  │ Command: show device-state                               │      │      │
│  │  │ Timeout: 30s                                             │      │      │
│  │  │ Device: 10.1.1.1 (gateway)                               │      │      │
│  │  │ Last successful: 2026-08-20 09:15:33                     │      │      │
│  │  └─────────────────────────────────────────────────────────┘      │      │
│  │  Signal: 5 lines = 100% relevant                                  │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  3. COST-PERFORMANCE BALANCE                                                │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │  Find the minimum sufficient context                              │      │
│  │                                                                   │      │
│  │      Performance ▲                                                │      │
│  │                 │     ┌─────────  Plateau                         │      │
│  │            100% │    /                                            │      │
│  │                 │   /                                             │      │
│  │             80% │  /                                              │      │
│  │                 │ /                                               │      │
│  │             60% │/                                                │      │
│  │                 ┼──────────────────────────────►                  │      │
│  │                 0    1K   2K   3K   4K   5K  Tokens               │      │
│  │                                                                   │      │
│  │  Sweet spot: ~2-3K tokens for test diagnosis                      │      │
│  │  Beyond 3K: Diminishing returns                                   │      │
│  │  Below 1K: Insufficient context                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  4. STRUCTURE FOR COMPREHENSION                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │  Organize context hierarchically                                  │      │
│  │                                                                   │      │
│  │  ✅ GOOD STRUCTURE:                                               │      │
│  │  ┌─────────────────────────────────────────────────────────┐      │      │
│  │  │ === FAILURE SUMMARY ===                                 │      │      │
│  │  │ Test: test_ssl_connection                               │      │      │
│  │  │ Error: SSL certificate mismatch                         │      │      │
│  │  │                                                         │      │      │
│  │  │ === ERROR DETAILS ===                                   │      │      │
│  │  │ [Log excerpt with line numbers]                         │      │      │
│  │  │                                                         │      │      │
│  │  │ === RELEVANT CODE ===                                   │      │      │
│  │  │ [Test function]                                         │      │      │
│  │  │                                                         │      │      │
│  │  │ === CONFIGURATION ===                                   │      │      │
│  │  │ [Topology section]                                      │      │      │
│  │  └─────────────────────────────────────────────────────────┘      │      │
│  │                                                                   │      │
│  │  ❌ BAD STRUCTURE:                                                │      │
│  │  ┌─────────────────────────────────────────────────────────┐      │      │
│  │  │ Here's everything mixed together with no organization   │      │      │
│  │  │ logs and code and config all jumbled...                 │      │      │
│  │  └─────────────────────────────────────────────────────────┘      │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  5. METADATA ENRICHMENT                                                     │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │  Add context about the context                                    │      │
│  │                                                                   │      │
│  │  Without metadata:                                                │      │
│  │    ERROR: Connection timeout                                      │      │
│  │                                                                   │      │
│  │  With metadata:                                                   │      │
│  │    [test_gpcs_connection.log:4521] 2026-08-20 10:28:12           │      │
│  │    ERROR: Connection timeout                                      │      │
│  │    Source: test_gpcs_basic/test_connection_tests.py::test_ssl    │      │
│  │    Device: gateway-1 (10.1.1.1)                                   │      │
│  │    Attempt: 3/3                                                   │      │
│  │                                                                   │      │
│  │  Metadata helps LLM understand:                                   │      │
│  │  • Where in the log                                               │      │
│  │  • What was being tested                                          │      │
│  │  • Which device failed                                            │      │
│  │  • Whether retries happened                                       │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  6. PROGRESSIVE DISCLOSURE                                                  │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │  Start minimal, add context only when needed                      │      │
│  │                                                                   │      │
│  │  Round 1: Send minimal context                                    │      │
│  │    → If LLM can diagnose: DONE (low cost)                         │      │
│  │                                                                   │      │
│  │  Round 2: LLM requests more context                               │      │
│  │    → Add specific requested evidence                              │      │
│  │    → Re-analyze                                                   │      │
│  │                                                                   │      │
│  │  Tradeoff:                                                        │      │
│  │  • Lower average cost (most cases resolve in Round 1)             │      │
│  │  • Higher latency (multi-turn conversation)                       │      │
│  │                                                                   │      │
│  │  Use when: Latency acceptable, cost critical                      │      │
│  │  Avoid when: Real-time diagnosis needed                           │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Architecture and Flow Diagram

### 3.1 Complete Context Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT ENGINEERING PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ STAGE 1: CONTEXT GATHERING                                        │      │
│  │                                                                   │      │
│  │ Input: Test failure notification                                  │      │
│  │                                                                   │      │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │      │
│  │   │Test Log  │  │Test Code │  │Topology  │  │Device    │         │      │
│  │   │File      │  │Source    │  │YAML      │  │Config    │         │      │
│  │   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │      │
│  │        │             │             │             │                │      │
│  │        └─────────────┴──────┬──────┴─────────────┘                │      │
│  │                             │                                     │      │
│  │                             ▼                                     │      │
│  │                    Evidence Collection                            │      │
│  │                    ┌─────────────────┐                            │      │
│  │                    │ GatherContext() │                            │      │
│  │                    └────────┬────────┘                            │      │
│  │                             │                                     │      │
│  │  Output: Raw evidence set (255,000 tokens)                        │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                  │                                          │
│                                  ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ STAGE 2: CONTEXT SELECTION                                        │      │
│  │                                                                   │      │
│  │ Strategy: Filter by relevance                                     │      │
│  │                                                                   │      │
│  │   Test Log (125K tokens)                                          │      │
│  │        │                                                          │      │
│  │        ├─► Extract ERROR/FAILED lines ────► 1,500 tokens          │      │
│  │        ├─► Extract WARN near errors ──────►   300 tokens          │      │
│  │        └─► Skip INFO/DEBUG ────────────────►     0 tokens          │      │
│  │                                                                   │      │
│  │   Test Code (3K tokens)                                           │      │
│  │        │                                                          │      │
│  │        ├─► Include failed test function ──►   200 tokens          │      │
│  │        ├─► Include fixtures used ─────────►   100 tokens          │      │
│  │        └─► Skip passing tests ─────────────►     0 tokens          │      │
│  │                                                                   │      │
│  │   Topology (2K tokens)                                            │      │
│  │        │                                                          │      │
│  │        ├─► Device config if config error ─►   150 tokens          │      │
│  │        └─► Skip if not config-related ─────►     0 tokens          │      │
│  │                                                                   │      │
│  │   Device Config (25K tokens)                                      │      │
│  │        │                                                          │      │
│  │        ├─► Relevant section only ─────────►   200 tokens          │      │
│  │        └─► Skip most ───────────────────────►     0 tokens          │      │
│  │                                                                   │      │
│  │                    ┌─────────────────┐                            │      │
│  │                    │ SelectContext() │                            │      │
│  │                    └────────┬────────┘                            │      │
│  │                             │                                     │      │
│  │  Output: Filtered evidence (2,450 tokens)                         │      │
│  │  Reduction: 99% (255K → 2.5K)                                     │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                  │                                          │
│                                  ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ STAGE 3: CONTEXT OPTIMIZATION                                     │      │
│  │                                                                   │      │
│  │ Enrich + Structure                                                │      │
│  │                                                                   │      │
│  │   ┌─────────────────────────────────────────────────────────┐     │      │
│  │   │ Add Metadata:                                           │     │      │
│  │   │ • Line numbers: [log.txt:4521]                          │     │      │
│  │   │ • Timestamps: 2026-08-20 10:28:12                       │     │      │
│  │   │ • Source tags: [Test Code] [Topology]                   │     │      │
│  │   │ • File paths: test_connection_tests.py                  │     │      │
│  │   └─────────────────────────────────────────────────────────┘     │      │
│  │                             │                                     │      │
│  │                             ▼                                     │      │
│  │   ┌─────────────────────────────────────────────────────────┐     │      │
│  │   │ Structure Hierarchically:                               │     │      │
│  │   │                                                         │     │      │
│  │   │ === FAILURE SUMMARY ===                                 │     │      │
│  │   │ [High-level overview]                                   │     │      │
│  │   │                                                         │     │      │
│  │   │ === ERROR DETAILS ===                                   │     │      │
│  │   │ [Log excerpts with metadata]                            │     │      │
│  │   │                                                         │     │      │
│  │   │ === TEST CODE ===                                       │     │      │
│  │   │ [Relevant functions]                                    │     │      │
│  │   │                                                         │     │      │
│  │   │ === CONFIGURATION ===                                   │     │      │
│  │   │ [Topology/device config]                                │     │      │
│  │   └─────────────────────────────────────────────────────────┘     │      │
│  │                             │                                     │      │
│  │                    ┌─────────────────┐                            │      │
│  │                    │OptimizeContext()│                            │      │
│  │                    └────────┬────────┘                            │      │
│  │                             │                                     │      │
│  │  Output: Structured evidence (2,600 tokens with metadata)         │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                  │                                          │
│                                  ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ STAGE 4: CONTEXT DELIVERY                                         │      │
│  │                                                                   │      │
│  │   ┌─────────────────────────────────────────────────────────┐     │      │
│  │   │ Compose LLM Request:                                    │     │      │
│  │   │                                                         │     │      │
│  │   │ {                                                       │     │      │
│  │   │   "model": "claude-sonnet-4-6",                         │     │      │
│  │   │   "system": "You are a PARTS test expert. Analyze...", │     │      │
│  │   │   "messages": [                                         │     │      │
│  │   │     {                                                   │     │      │
│  │   │       "role": "user",                                   │     │      │
│  │   │       "content": "[Structured evidence from Stage 3]"   │     │      │
│  │   │     }                                                   │     │      │
│  │   │   ],                                                    │     │      │
│  │   │   "max_tokens": 4096                                    │     │      │
│  │   │ }                                                       │     │      │
│  │   └─────────────────────────────────────────────────────────┘     │      │
│  │                             │                                     │      │
│  │                    ┌─────────────────┐                            │      │
│  │                    │ DeliverContext()│                            │      │
│  │                    └────────┬────────┘                            │      │
│  │                             │                                     │      │
│  │                             ▼                                     │      │
│  │                   ANTHROPIC CLAUDE API                            │      │
│  │                             │                                     │      │
│  │                             ▼                                     │      │
│  │  Output: Diagnosis with root cause + fix                          │      │
│  │  Cost: $0.008 (vs $0.77 without context engineering)              │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Interactions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT PIPELINE COMPONENTS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                    EvidenceCollector                              │      │
│  │                                                                   │      │
│  │  collect_evidence(failure_event):                                 │      │
│  │    • Locate test log file                                         │      │
│  │    • Find test source code                                        │      │
│  │    • Load topology YAML                                           │      │
│  │    • Fetch device config (if needed)                              │      │
│  │    • Get previous run logs (optional)                             │      │
│  │                                                                   │      │
│  │  Returns: EvidenceSet                                             │      │
│  │    - log_file: Path                                               │      │
│  │    - log_content: str (full 50K lines)                            │      │
│  │    - test_code: str                                               │      │
│  │    - topology: dict                                               │      │
│  │    - device_config: Optional[str]                                 │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                  │                                          │
│                                  ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                    ContextSelector                                │      │
│  │                                                                   │      │
│  │  select_relevant(evidence_set, failure_type):                     │      │
│  │                                                                   │      │
│  │    # Analyze failure type                                         │      │
│  │    if "SSL" in failure_type:                                      │      │
│  │        priority = ["SSL errors", "cert config", "handshake"]      │      │
│  │    elif "timeout" in failure_type:                                │      │
│  │        priority = ["timeout errors", "connection", "network"]     │      │
│  │                                                                   │      │
│  │    # Extract from log                                             │      │
│  │    errors = extract_errors(log_content)                           │      │
│  │    warnings = extract_warnings_near(errors)                       │      │
│  │                                                                   │      │
│  │    # Filter test code                                             │      │
│  │    relevant_code = extract_failed_test_function()                 │      │
│  │    fixtures = extract_used_fixtures()                             │      │
│  │                                                                   │      │
│  │    # Select topology sections                                     │      │
│  │    if config_related(failure_type):                               │      │
│  │        topo_excerpt = extract_device_config()                     │      │
│  │                                                                   │      │
│  │  Returns: SelectedContext                                         │      │
│  │    - errors: List[LogLine]                                        │      │
│  │    - test_function: str                                           │      │
│  │    - fixtures: List[str]                                          │      │
│  │    - topology_excerpt: Optional[str]                              │      │
│  │    - token_count: int                                             │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                  │                                          │
│                                  ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                    ContextOptimizer                               │      │
│  │                                                                   │      │
│  │  optimize(selected_context):                                      │      │
│  │                                                                   │      │
│  │    # Add metadata                                                 │      │
│  │    for error in selected_context.errors:                          │      │
│  │        error.add_metadata(                                        │      │
│  │            line_number=error.line_num,                            │      │
│  │            timestamp=error.timestamp,                             │      │
│  │            source_file=error.file                                 │      │
│  │        )                                                          │      │
│  │                                                                   │      │
│  │    # Structure hierarchically                                     │      │
│  │    structured = format_template(                                  │      │
│  │        summary=create_summary(),                                  │      │
│  │        errors=format_errors(),                                    │      │
│  │        code=format_code(),                                        │      │
│  │        config=format_config()                                     │      │
│  │    )                                                              │      │
│  │                                                                   │      │
│  │    # Validate token count                                         │      │
│  │    if count_tokens(structured) > target_max:                      │      │
│  │        structured = truncate_smart(structured)                    │      │
│  │                                                                   │      │
│  │  Returns: str (formatted context ready for LLM)                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                  │                                          │
│                                  ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                    ContextDelivery                                │      │
│  │                                                                   │      │
│  │  deliver(optimized_context, system_prompt):                       │      │
│  │                                                                   │      │
│  │    request = {                                                    │      │
│  │        "model": select_model(task_type="DEBUG"),                  │      │
│  │        "system": system_prompt,                                   │      │
│  │        "messages": [                                              │      │
│  │            {"role": "user", "content": optimized_context}         │      │
│  │        ],                                                         │      │
│  │        "max_tokens": 4096                                         │      │
│  │    }                                                              │      │
│  │                                                                   │      │
│  │    response = claude_client.messages.create(**request)            │      │
│  │                                                                   │      │
│  │    # Track metrics                                                │      │
│  │    metrics.record(                                                │      │
│  │        input_tokens=response.usage.input_tokens,                  │      │
│  │        output_tokens=response.usage.output_tokens,                │      │
│  │        cost=estimate_cost(...)                                    │      │
│  │    )                                                              │      │
│  │                                                                   │      │
│  │  Returns: Diagnosis                                               │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Use Cases

### 4.1 Atiya: Evidence Collection for Test Diagnosis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ATIYA TEST DIAGNOSIS USE CASE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SCENARIO: Overnight regression run produces 127 test failures              │
│            QA engineer needs to triage by 9am                               │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                   WITHOUT ATIYA                                   │      │
│  │                                                                   │      │
│  │  8:00am  Engineer arrives, sees 127 failures                      │      │
│  │  8:05am  Opens first log file (50K lines), searches for "ERROR"   │      │
│  │  8:15am  Finds error, opens test code to understand context       │      │
│  │  8:25am  Checks topology YAML for configuration                   │      │
│  │  8:35am  Identifies root cause: cert name mismatch                │      │
│  │  8:40am  Documents finding, moves to next failure                 │      │
│  │                                                                   │      │
│  │  Time per failure: 40 minutes                                     │      │
│  │  127 failures × 40 min = 5,080 minutes = 84.6 hours               │      │
│  │                                                                   │      │
│  │  ❌ IMPOSSIBLE: Can't triage all failures in one day              │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                    WITH ATIYA                                     │      │
│  │                                                                   │      │
│  │  8:00am  Engineer runs: atiya batch-diagnose nightly-failures/    │      │
│  │  8:01am  Atiya submits 127 diagnoses to Claude Batches API        │      │
│  │          Cost: 127 × $0.0225 = $2.86 (with 50% batch discount)    │      │
│  │  8:05am  Gets coffee while Atiya processes                        │      │
│  │  9:00am  Results ready: atiya batch-results                       │      │
│  │                                                                   │      │
│  │  Output:                                                          │      │
│  │  ┌─────────────────────────────────────────────────────────┐      │      │
│  │  │ FAILURE SUMMARY (127 tests)                             │      │      │
│  │  │                                                         │      │      │
│  │  │ Root Causes:                                            │      │      │
│  │  │  1. SSL cert mismatch (45 tests) ← SAME ROOT CAUSE      │      │      │
│  │  │     Fix: Update topology.yaml cert_name to *.prisma     │      │      │
│  │  │                                                         │      │      │
│  │  │  2. Timeout on device reboot (32 tests)                 │      │      │
│  │  │     Fix: Increase timeout in test fixtures              │      │      │
│  │  │                                                         │      │      │
│  │  │  3. API endpoint deprecated (28 tests)                  │      │      │
│  │  │     Fix: Update to /v2/config endpoint                  │      │      │
│  │  │                                                         │      │      │
│  │  │  4. Race condition in async test (15 tests)             │      │      │
│  │  │     Fix: Add await before assertion                    │      │      │
│  │  │                                                         │      │      │
│  │  │  5. Various unique issues (7 tests)                     │      │      │
│  │  │     Requires individual investigation                   │      │      │
│  │  └─────────────────────────────────────────────────────────┘      │      │
│  │                                                                   │      │
│  │  Time to triage: 1 hour (Atiya) + 15 min (engineer review)        │      │
│  │  Cost: $2.86                                                      │      │
│  │  Engineer time saved: 83.4 hours                                  │      │
│  │                                                                   │      │
│  │  ✅ IMPACT:                                                       │      │
│  │  • 4 systemic issues identified (covering 120/127 failures)       │      │
│  │  • Fixes can be prioritized by impact                             │      │
│  │  • Most failures resolved with 4 changes                          │      │
│  │  • Only 7 unique issues need deep investigation                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              ATIYA CONTEXT ENGINEERING PIPELINE                   │      │
│  │                                                                   │      │
│  │  For each test failure:                                           │      │
│  │                                                                   │      │
│  │  1. GATHER                                                        │      │
│  │     ✓ Read pytest log from ReportPortal                           │      │
│  │     ✓ Parse test file path from pytest metadata                   │      │
│  │     ✓ Load test function source                                   │      │
│  │     ✓ Load topology YAML if referenced                            │      │
│  │     ✓ Get device config if config-related failure                 │      │
│  │                                                                   │      │
│  │  2. SELECT                                                        │      │
│  │     ✓ Extract ERROR/EXCEPTION lines from log                      │      │
│  │     ✓ Extract traceback (last 20 lines before error)              │      │
│  │     ✓ Include failed test function only                           │      │
│  │     ✓ Include fixtures used by test                               │      │
│  │     ✓ Skip passing test output                                    │      │
│  │     ✓ Skip DEBUG/INFO logs unless near error                      │      │
│  │                                                                   │      │
│  │  3. OPTIMIZE                                                      │      │
│  │     ✓ Add line numbers: [pytest.log:4521]                         │      │
│  │     ✓ Add timestamps: 2026-08-20 10:28:12                         │      │
│  │     ✓ Add source tags: [Test Code] [Topology]                     │      │
│  │     ✓ Structure in sections: Summary → Errors → Code → Config     │      │
│  │     ✓ Validate token count < 3000                                 │      │
│  │                                                                   │      │
│  │  4. DELIVER                                                       │      │
│  │     ✓ System prompt: "PARTS test failure expert"                  │      │
│  │     ✓ User message: Structured evidence                           │      │
│  │     ✓ Model: Sonnet 4.6 (balanced quality/cost)                   │      │
│  │     ✓ Batch API: 50% cost savings                                 │      │
│  │     ✓ Process overnight, results by morning                       │      │
│  │                                                                   │      │
│  │  Result: High-quality diagnosis at 1/100th manual effort           │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 RAG Systems

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              CONTEXT ENGINEERING IN RAG SYSTEMS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  RAG = Retrieval-Augmented Generation                                       │
│  Context Engineering is CRITICAL for RAG performance                        │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                    RAG PIPELINE                                   │      │
│  │                                                                   │      │
│  │  User Query: "How do I configure SSL certificates in PARTS?"      │      │
│  │        │                                                          │      │
│  │        ▼                                                          │      │
│  │  ┌──────────────────────────────────────────────────────┐         │      │
│  │  │ STEP 1: RETRIEVAL (Context Gathering)               │         │      │
│  │  │                                                      │         │      │
│  │  │ Vector Search in Documentation:                     │         │      │
│  │  │                                                      │         │      │
│  │  │ Found 100 potentially relevant documents:           │         │      │
│  │  │ • topology/ssl_guide.md          (similarity: 0.92) │         │      │
│  │  │ • examples/gpcs_ssl.yaml         (similarity: 0.89) │         │      │
│  │  │ • api/partsfwk_ssl_methods.md    (similarity: 0.87) │         │      │
│  │  │ • troubleshooting/ssl_errors.md  (similarity: 0.85) │         │      │
│  │  │ • ... 96 more documents ...      (similarity: 0.45-0.84)│         │      │
│  │  │                                                      │         │      │
│  │  │ Total if included: ~200,000 tokens                   │         │      │
│  │  └──────────────────────────────────────────────────────┘         │      │
│  │        │                                                          │      │
│  │        ▼                                                          │      │
│  │  ┌──────────────────────────────────────────────────────┐         │      │
│  │  │ STEP 2: CONTEXT SELECTION                            │         │      │
│  │  │                                                      │         │      │
│  │  │ Apply thresholds:                                    │         │      │
│  │  │ • Keep only similarity > 0.85 → 4 documents          │         │      │
│  │  │ • Rank by relevance to query                         │         │      │
│  │  │                                                      │         │      │
│  │  │ Selected documents:                                  │         │      │
│  │  │ 1. topology/ssl_guide.md         (2,500 tokens)      │         │      │
│  │  │ 2. examples/gpcs_ssl.yaml        (800 tokens)        │         │      │
│  │  │ 3. api/partsfwk_ssl_methods.md   (1,200 tokens)      │         │      │
│  │  │ 4. troubleshooting/ssl_errors.md (1,000 tokens)      │         │      │
│  │  │                                                      │         │      │
│  │  │ Total: 5,500 tokens                                  │         │      │
│  │  │ Reduction: 97.25% (200K → 5.5K)                      │         │      │
│  │  └──────────────────────────────────────────────────────┘         │      │
│  │        │                                                          │      │
│  │        ▼                                                          │      │
│  │  ┌──────────────────────────────────────────────────────┐         │      │
│  │  │ STEP 3: CONTEXT OPTIMIZATION                         │         │      │
│  │  │                                                      │         │      │
│  │  │ Check token budget:                                  │         │      │
│  │  │ • Max context window: 200K tokens                    │         │      │
│  │  │ • Reserve for output: 4K tokens                      │         │      │
│  │  │ • System prompt: 500 tokens                          │         │      │
│  │  │ • Available for context: 195.5K tokens               │         │      │
│  │  │ • Current context: 5.5K tokens ✓ FITS               │         │      │
│  │  │                                                      │         │      │
│  │  │ But can we improve signal-to-noise?                  │         │      │
│  │  │                                                      │         │      │
│  │  │ Chunk relevant sections:                             │         │      │
│  │  │ • From ssl_guide.md: Extract "Configuration" section │         │      │
│  │  │   (skip "Overview" and "Troubleshooting")            │         │      │
│  │  │ • From examples: Full file (it's concise)            │         │      │
│  │  │ • From API docs: Method signatures only              │         │      │
│  │  │ • From troubleshooting: Common errors section        │         │      │
│  │  │                                                      │         │      │
│  │  │ Optimized: 3,200 tokens (42% reduction)              │         │      │
│  │  └──────────────────────────────────────────────────────┘         │      │
│  │        │                                                          │      │
│  │        ▼                                                          │      │
│  │  ┌──────────────────────────────────────────────────────┐         │      │
│  │  │ STEP 4: CONTEXT DELIVERY (Generation)               │         │      │
│  │  │                                                      │         │      │
│  │  │ Prompt:                                              │         │      │
│  │  │ ┌────────────────────────────────────────────────┐   │         │      │
│  │  │ │ System: You are a PARTS documentation expert. │   │         │      │
│  │  │ │         Answer based ONLY on the provided docs│   │         │      │
│  │  │ │                                                │   │         │      │
│  │  │ │ User: Here's relevant documentation:          │   │         │      │
│  │  │ │                                                │   │         │      │
│  │  │ │ [Document 1: topology/ssl_guide.md]            │   │         │      │
│  │  │ │ Configuration:                                │   │         │      │
│  │  │ │ To configure SSL in topology YAML:            │   │         │      │
│  │  │ │ ...                                            │   │         │      │
│  │  │ │                                                │   │         │      │
│  │  │ │ [Document 2: examples/gpcs_ssl.yaml]           │   │         │      │
│  │  │ │ gateway:                                      │   │         │      │
│  │  │ │   ssl_certificate:                            │   │         │      │
│  │  │ │     cert_name: *.prisma.local                 │   │         │      │
│  │  │ │ ...                                            │   │         │      │
│  │  │ │                                                │   │         │      │
│  │  │ │ Question: How do I configure SSL certificates │   │         │      │
│  │  │ │ in PARTS?                                     │   │         │      │
│  │  │ └────────────────────────────────────────────────┘   │         │      │
│  │  │                                                      │         │      │
│  │  │ LLM Response:                                        │         │      │
│  │  │ "To configure SSL certificates in PARTS topology:    │         │      │
│  │  │  1. Add ssl_certificate block under device          │         │      │
│  │  │  2. Set cert_name to your certificate CN            │         │      │
│  │  │  3. Example: cert_name: *.prisma.local              │         │      │
│  │  │  See topology/ssl_guide.md for full details."        │         │      │
│  │  └──────────────────────────────────────────────────────┘         │      │
│  │                                                                   │      │
│  │  ✅ RESULT: Accurate answer grounded in documentation             │      │
│  │  Cost: 3,200 input + 500 output = $0.017                          │      │
│  │  vs naive approach (200K tokens) = $0.600                         │      │
│  │  Savings: 97.2%                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              RAG CONTEXT ENGINEERING PRINCIPLES                   │      │
│  │                                                                   │      │
│  │  1. RETRIEVAL QUALITY > RETRIEVAL QUANTITY                        │      │
│  │     • Better to retrieve 5 highly relevant docs than 100 maybe    │      │
│  │     • Set high similarity thresholds (>0.85)                      │      │
│  │     • Rank and limit top-k results                                │      │
│  │                                                                   │      │
│  │  2. CHUNK WISELY                                                  │      │
│  │     • Chunk documents at section boundaries, not random sizes     │      │
│  │     • Preserve semantic coherence                                 │      │
│  │     • Add metadata: source file, section name                     │      │
│  │                                                                   │      │
│  │  3. RERANK AFTER RETRIEVAL                                        │      │
│  │     • Vector search finds candidates                              │      │
│  │     • Reranker scores relevance to specific query                 │      │
│  │     • Select top reranked results                                 │      │
│  │                                                                   │      │
│  │  4. DEDUPLICATION                                                 │      │
│  │     • Multiple chunks from same doc? Merge or pick best           │      │
│  │     • Identical content from different docs? Include once         │      │
│  │                                                                   │      │
│  │  5. CONTEXT WINDOW BUDGETING                                      │      │
│  │     • Reserve space for system prompt + output                    │      │
│  │     • Fill remaining budget with highest-value context            │      │
│  │     • Monitor actual usage vs budget                              │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Long-Context Applications

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LONG-CONTEXT APPLICATIONS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Modern LLMs support 200K+ token context windows                            │
│  BUT: Longer context ≠ Better performance                                   │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │           "LOST IN THE MIDDLE" PROBLEM                            │      │
│  │                                                                   │      │
│  │  Study: LLMs perform worse when key info is in middle of long ctx │      │
│  │                                                                   │      │
│  │      Accuracy ▲                                                   │      │
│  │              │                                                    │      │
│  │         100% │█                                     ████          │      │
│  │              │██                                  ███             │      │
│  │          80% │███                              ███                │      │
│  │              │████                          ███                   │      │
│  │          60% │█████                      ███                      │      │
│  │              │██████                  ███                         │      │
│  │          40% │███████             ████                            │      │
│  │              │████████        ████                                │      │
│  │          20% │█████████   ████                                    │      │
│  │              │──────────────────────────────────────────►         │      │
│  │              Start    25K    50K    75K   100K    End             │      │
│  │                    Position of Key Information                    │      │
│  │                                                                   │      │
│  │  Observation: Best performance when key info is at START or END   │      │
│  │               Worst performance when key info is in MIDDLE        │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │        CONTEXT ENGINEERING FOR LONG CONTEXTS                      │      │
│  │                                                                   │      │
│  │  USE CASE: Code repository analysis                               │      │
│  │  Task: "Find all SQL injection vulnerabilities"                   │      │
│  │  Codebase: 150 files, 50,000 lines, ~125,000 tokens               │      │
│  │                                                                   │      │
│  │  ❌ NAIVE: Send entire codebase                                   │      │
│  │  ┌────────────────────────────────────────────────────────┐       │      │
│  │  │ System: You are a security auditor                    │       │      │
│  │  │                                                        │       │      │
│  │  │ User: Here's the entire codebase (125K tokens)         │       │      │
│  │  │                                                        │       │      │
│  │  │ [file1.py - 500 lines]                                 │       │      │
│  │  │ [file2.py - 800 lines]                                 │       │      │
│  │  │ ... 148 more files ...                                 │       │      │
│  │  │                                                        │       │      │
│  │  │ Question: Find SQL injection vulnerabilities           │       │      │
│  │  └────────────────────────────────────────────────────────┘       │      │
│  │                                                                   │      │
│  │  Problems:                                                        │      │
│  │  • Key vulnerabilities lost in middle                             │      │
│  │  • High cost: 125K × $3/1M = $0.375 input                         │      │
│  │  • Slow processing: ~60 seconds                                   │      │
│  │  • Inconsistent results (middle info dropped)                     │      │
│  │                                                                   │      │
│  │  ✅ SMART: Extract relevant code sections                        │      │
│  │  ┌────────────────────────────────────────────────────────┐       │      │
│  │  │ STEP 1: Find files with SQL queries                    │       │      │
│  │  │ Grep for: "execute\(", "query\(", "SELECT"             │       │      │
│  │  │ Result: 12 files (not all 150)                         │       │      │
│  │  │                                                        │       │      │
│  │  │ STEP 2: Extract functions with SQL                     │       │      │
│  │  │ Parse AST, extract function bodies                     │       │      │
│  │  │ Result: 23 functions, ~1,200 lines                     │       │      │
│  │  │                                                        │       │      │
│  │  │ STEP 3: Add surrounding context                        │       │      │
│  │  │ Include 5 lines before/after each function             │       │      │
│  │  │ Add file path + line numbers                           │       │      │
│  │  │ Total: ~1,500 lines = 3,750 tokens                     │       │      │
│  │  │                                                        │       │      │
│  │  │ STEP 4: Structure by risk                              │       │      │
│  │  │ Group by pattern:                                      │       │      │
│  │  │ • User input directly in query (HIGH RISK)             │       │      │
│  │  │ • String formatting in query (MEDIUM RISK)             │       │      │
│  │  │ • Parameterized queries (LOW RISK)                     │       │      │
│  │  │                                                        │       │      │
│  │  │ Deliver to LLM:                                        │       │      │
│  │  │ ┌──────────────────────────────────────────────┐       │       │      │
│  │  │ │ === HIGH RISK: Direct User Input ===         │       │       │      │
│  │  │ │ [db/users.py:45-52]                          │       │       │      │
│  │  │ │ def find_user(username):                     │       │       │      │
│  │  │ │     query = f"SELECT * FROM users            │       │       │      │
│  │  │ │              WHERE name='{username}'"        │       │       │      │
│  │  │ │     return db.execute(query)                 │       │       │      │
│  │  │ │                                              │       │       │      │
│  │  │ │ === MEDIUM RISK: String Formatting ===       │       │       │      │
│  │  │ │ [api/search.py:78-85]                        │       │       │      │
│  │  │ │ def search(term):                            │       │       │      │
│  │  │ │     query = "SELECT * FROM posts WHERE       │       │       │      │
│  │  │ │              content LIKE '%{}%'".format(term)│       │       │      │
│  │  │ │     ...                                      │       │       │      │
│  │  │ └──────────────────────────────────────────────┘       │       │      │
│  │  └────────────────────────────────────────────────────────┘       │      │
│  │                                                                   │      │
│  │  Benefits:                                                        │      │
│  │  • Key vulnerabilities at START (high attention area)             │      │
│  │  • Reduced cost: 3,750 tokens vs 125,000 (97% savings)            │      │
│  │  • Faster: 5 seconds vs 60 seconds                                │      │
│  │  • Higher accuracy (focused context)                              │      │
│  │  • Grouped by severity (actionable output)                        │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │          STRATEGIES FOR LONG-CONTEXT SCENARIOS                    │      │
│  │                                                                   │      │
│  │  1. HIERARCHICAL PROCESSING                                       │      │
│  │     Pass 1: Summarize each file → 150 summaries (15K tokens)      │      │
│  │     Pass 2: Identify relevant files → 12 files                    │      │
│  │     Pass 3: Deep analysis of 12 files → findings                  │      │
│  │                                                                   │      │
│  │  2. MAP-REDUCE PATTERN                                            │      │
│  │     Map: Process each file individually → partial results         │      │
│  │     Reduce: Combine results → final analysis                      │      │
│  │     Benefit: Parallelizable, scalable                             │      │
│  │                                                                   │      │
│  │  3. PROGRESSIVE REFINEMENT                                        │      │
│  │     Round 1: Coarse-grained pass (all code, just signatures)      │      │
│  │     Round 2: Focus on flagged areas (full function bodies)        │      │
│  │     Round 3: Deep dive on confirmed issues                        │      │
│  │                                                                   │      │
│  │  4. STRATEGIC PLACEMENT                                           │      │
│  │     Most important info: START of context                         │      │
│  │     Supporting details: END of context                            │      │
│  │     Avoid: Key info in middle (lost in the middle problem)        │      │
│  │                                                                   │      │
│  │  5. CONTEXT WINDOW MANAGEMENT                                     │      │
│  │     Monitor: total tokens sent                                    │      │
│  │     Budget: system (500) + context (XK) + output (4K)             │      │
│  │     Validate: Don't exceed model's max context window             │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Design Methodologies

### 5.1 Evidence Prioritization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EVIDENCE PRIORITIZATION METHODOLOGY                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Principle: Not all evidence is equally valuable                            │
│  Strategy: Classify evidence by criticality and include accordingly         │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              THREE-TIER PRIORITIZATION MODEL                      │      │
│  │                                                                   │      │
│  │   ┌─────────────────────────────────────────────────────────┐     │      │
│  │   │ TIER 1: CRITICAL (Always include, first in context)    │     │      │
│  │   │                                                         │     │      │
│  │   │ • Error messages and tracebacks                         │     │      │
│  │   │ • Failed assertions                                     │     │      │
│  │   │ • Exception details                                     │     │      │
│  │   │ • Failed test function code                             │     │      │
│  │   │                                                         │     │      │
│  │   │ Placement: TOP of context (highest attention)           │     │      │
│  │   │ Token budget: Up to 40% of total                        │     │      │
│  │   └─────────────────────────────────────────────────────────┘     │      │
│  │                            │                                      │      │
│  │   ┌─────────────────────────────────────────────────────────┐     │      │
│  │   │ TIER 2: SUPPORTING (Include if space, prioritize)      │     │      │
│  │   │                                                         │     │      │
│  │   │ • Warnings near errors                                  │     │      │
│  │   │ • Test fixtures used                                    │     │      │
│  │   │ • Relevant configuration                                │     │      │
│  │   │ • Device state at failure time                          │     │      │
│  │   │                                                         │     │      │
│  │   │ Placement: MIDDLE of context                            │     │      │
│  │   │ Token budget: Up to 40% of total                        │     │      │
│  │   └─────────────────────────────────────────────────────────┘     │      │
│  │                            │                                      │      │
│  │   ┌─────────────────────────────────────────────────────────┐     │      │
│  │   │ TIER 3: OPTIONAL (Include only if budget allows)       │     │      │
│  │   │                                                         │     │      │
│  │   │ • Full test file (not just failed function)             │     │      │
│  │   │ • Previous run comparison                               │     │      │
│  │   │ • Full topology YAML                                    │     │      │
│  │   │ • Success log sections                                  │     │      │
│  │   │                                                         │     │      │
│  │   │ Placement: END of context                               │     │      │
│  │   │ Token budget: Up to 20% of total                        │     │      │
│  │   └─────────────────────────────────────────────────────────┘     │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              PRIORITIZATION DECISION TREE                         │      │
│  │                                                                   │      │
│  │                      Start: Evidence Item                         │      │
│  │                              │                                    │      │
│  │                              ▼                                    │      │
│  │                  ┌────────────────────────┐                       │      │
│  │                  │ Is it an ERROR/        │                       │      │
│  │                  │ EXCEPTION/TRACEBACK?   │                       │      │
│  │                  └──────┬──────────┬──────┘                       │      │
│  │                    YES  │          │  NO                          │      │
│  │                         ▼          ▼                              │      │
│  │                  ┌──────────┐  ┌─────────────────────┐            │      │
│  │                  │ TIER 1   │  │ Is it a WARNING     │            │      │
│  │                  │ CRITICAL │  │ within 10 lines     │            │      │
│  │                  └──────────┘  │ of error?           │            │      │
│  │                                └──────┬──────┬───────┘            │      │
│  │                                  YES  │      │  NO                │      │
│  │                                       ▼      ▼                    │      │
│  │                                ┌──────────┐  ┌────────────────┐   │      │
│  │                                │ TIER 2   │  │ Is it test code│   │      │
│  │                                │SUPPORTING│  │ or config?     │   │      │
│  │                                └──────────┘  └──────┬─────────┘   │      │
│  │                                                YES  │  NO         │      │
│  │                                                     ▼     ▼       │      │
│  │                                              ┌──────────┐ ┌─────┐ │      │
│  │                                              │ TIER 2   │ │TIER │ │      │
│  │                                              │SUPPORTING│ │  3  │ │      │
│  │                                              └──────────┘ └─────┘ │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                PRACTICAL EXAMPLE: SSL FAILURE                     │      │
│  │                                                                   │      │
│  │  Available evidence:                                              │      │
│  │  • 50,000 line test log                                           │      │
│  │  • 500 line test file                                             │      │
│  │  • 800 line topology YAML                                         │      │
│  │  • 10,000 line device config                                      │      │
│  │  • 40,000 line previous run log                                   │      │
│  │                                                                   │      │
│  │  Prioritization:                                                  │      │
│  │                                                                   │      │
│  │  TIER 1 (CRITICAL):                                               │      │
│  │  ┌─────────────────────────────────────────────────────────┐      │      │
│  │  │ [test.log:4521-4548] ← Line numbers                    │      │      │
│  │  │ 2026-08-20 10:28:12 ERROR: SSL handshake failed        │      │      │
│  │  │ Expected CN: *.prisma.local                            │      │      │
│  │  │ Received CN: localhost                                 │      │      │
│  │  │                                                        │      │      │
│  │  │ Traceback:                                             │      │      │
│  │  │   File test_ssl.py, line 67, in test_ssl_connection    │      │      │
│  │  │     client.connect(gateway.ip, verify_ssl=True)        │      │      │
│  │  │   SSLCertVerificationError: CN mismatch                │      │      │
│  │  │                                                        │      │      │
│  │  │ [test_ssl.py:45-67] ← Test function                    │      │      │
│  │  │ def test_ssl_connection(topology):                     │      │      │
│  │  │     gateway = topology.devices['gateway']              │      │      │
│  │  │     client = SSLClient()                               │      │      │
│  │  │     client.connect(gateway.ip, verify_ssl=True)        │      │      │
│  │  │     assert client.is_connected                         │      │      │
│  │  │                                                        │      │      │
│  │  │ Token count: 450 tokens (18% of 2500 budget)           │      │      │
│  │  └─────────────────────────────────────────────────────────┘      │      │
│  │                                                                   │      │
│  │  TIER 2 (SUPPORTING):                                             │      │
│  │  ┌─────────────────────────────────────────────────────────┐      │      │
│  │  │ [test.log:4510-4520] ← Warnings before error           │      │      │
│  │  │ WARN: Using self-signed certificate                    │      │      │
│  │  │ WARN: CN does not match expected pattern               │      │      │
│  │  │                                                        │      │      │
│  │  │ [topology.yaml:gateway] ← Relevant config              │      │      │
│  │  │ gateway:                                               │      │      │
│  │  │   ip: 10.1.1.1                                         │      │      │
│  │  │   ssl_certificate:                                     │      │      │
│  │  │     cert_name: localhost  # ← PROBLEM                  │      │      │
│  │  │     verify: true                                       │      │      │
│  │  │                                                        │      │      │
│  │  │ [conftest.py:topology fixture] ← How topology loaded   │      │      │
│  │  │ @pytest.fixture                                        │      │      │
│  │  │ def topology(testbed):                                 │      │      │
│  │  │     return build_topology("gateway.yaml")              │      │      │
│  │  │                                                        │      │      │
│  │  │ Token count: 350 tokens (14% of budget)                │      │      │
│  │  └─────────────────────────────────────────────────────────┘      │      │
│  │                                                                   │      │
│  │  TIER 3 (OPTIONAL):                                               │      │
│  │  ┌─────────────────────────────────────────────────────────┐      │      │
│  │  │ [previous_run.log] ← Comparison                        │      │      │
│  │  │ Summary: Previous run PASSED with cert_name            │      │      │
│  │  │          *.prisma.local                                │      │      │
│  │  │                                                        │      │      │
│  │  │ Token count: 100 tokens (4% of budget)                 │      │      │
│  │  │                                                        │      │      │
│  │  │ [device_config.txt] ← Device state                     │      │      │
│  │  │ NOT INCLUDED: Config error, not device issue           │      │      │
│  │  │ Saved: 5,000 tokens                                    │      │      │
│  │  │                                                        │      │      │
│  │  │ [test_ssl.py full file] ← Full test file               │      │      │
│  │  │ NOT INCLUDED: Only failed function needed              │      │      │
│  │  │ Saved: 1,000 tokens                                    │      │      │
│  │  └─────────────────────────────────────────────────────────┘      │      │
│  │                                                                   │      │
│  │  FINAL CONTEXT:                                                   │      │
│  │  • Tier 1: 450 tokens (50% of delivered)                          │      │
│  │  • Tier 2: 350 tokens (39% of delivered)                          │      │
│  │  • Tier 3: 100 tokens (11% of delivered)                          │      │
│  │  • Total: 900 tokens (vs 125,000 available)                       │      │
│  │  • Reduction: 99.3%                                               │      │
│  │  • Cost: $0.0027 (vs $0.375)                                      │      │
│  │                                                                   │      │
│  │  OUTCOME: LLM diagnosis in 5 seconds                              │      │
│  │  "Root cause: SSL certificate CN mismatch in topology.yaml        │      │
│  │   Expected: *.prisma.local                                        │      │
│  │   Actual: localhost                                               │      │
│  │   Fix: Update topology.yaml line 5: cert_name: *.prisma.local"    │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Context Windowing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT WINDOWING METHODOLOGY                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Principle: When full document exceeds budget, extract relevant windows      │
│  Strategy: Sliding window, fixed window, or semantic window extraction      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                  SLIDING WINDOW APPROACH                          │      │
│  │                                                                   │      │
│  │  Use case: Long log file, errors distributed throughout           │      │
│  │                                                                   │      │
│  │  Full Log: 50,000 lines                                           │      │
│  │  ┌─────────────────────────────────────────────────────────┐      │      │
│  │  │ Line 1:    [INFO] Test starting...                      │      │      │
│  │  │ Line 2:    [DEBUG] Loading config...                    │      │      │
│  │  │ ...                                                     │      │      │
│  │  │ Line 4521: [ERROR] SSL handshake failed ←─┐             │      │      │
│  │  │ Line 4522: Expected CN: *.prisma         │ Window 1    │      │      │
│  │  │ Line 4523: Received CN: localhost        │ (50 lines)  │      │      │
│  │  │ ...                                      │             │      │      │
│  │  │ Line 4548: [ERROR] Connection closed    ←─┘             │      │      │
│  │  │ ...                                                     │      │      │
│  │  │ Line 8912: [ERROR] Timeout waiting ←──┐                 │      │      │
│  │  │ Line 8913: Device: 10.1.1.1           │ Window 2       │      │      │
│  │  │ ...                                   │ (40 lines)     │      │      │
│  │  │ Line 8934: [ERROR] Retry failed      ←──┘               │      │      │
│  │  │ ...                                                     │      │      │
│  │  │ Line 49999: [INFO] Test completed                       │      │      │
│  │  │ Line 50000: [INFO] Cleanup finished                     │      │      │
│  │  └─────────────────────────────────────────────────────────┘      │      │
│  │                                                                   │      │
│  │  Algorithm:                                                       │      │
│  │  1. Scan log for ERROR/EXCEPTION markers                          │      │
│  │  2. For each ERROR:                                               │      │
│  │     - Extract N lines before (context)                            │      │
│  │     - Extract M lines after (consequences)                        │      │
│  │     - Create window [error-N : error+M]                           │      │
│  │  3. Merge overlapping windows                                     │      │
│  │  4. Deliver consolidated windows                                  │      │
│  │                                                                   │      │
│  │  Example configuration:                                           │      │
│  │  • N (before): 10 lines                                           │      │
│  │  • M (after): 15 lines                                            │      │
│  │  • Window size: 25 lines per error                                │      │
│  │  • 5 errors found → 5 windows → ~125 lines extracted              │      │
│  │  • Reduction: 50,000 → 125 lines (99.75%)                         │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                  FIXED WINDOW APPROACH                            │      │
│  │                                                                   │      │
│  │  Use case: Error known to be in specific section                  │      │
│  │                                                                   │      │
│  │  Strategy: Extract fixed-size window around known error location  │      │
│  │                                                                   │      │
│  │  Example: pytest output structure                                 │      │
│  │  ┌─────────────────────────────────────────────────────────┐      │      │
│  │  │ ... 1000 lines of test execution ...                    │      │      │
│  │  │                                                         │      │      │
│  │  │ ================= FAILURES =================             │      │      │
│  │  │ ___________ test_ssl_connection ___________             │      │      │
│  │  │                                                         │      │      │
│  │  │ topology = <Topology at 0x7f8b...>                      │      │      │
│  │  │                                                         │      │      │
│  │  │     def test_ssl_connection(topology):                  │      │      │
│  │  │         gateway = topology.devices['gateway']           │      │      │
│  │  │         client = SSLClient()                            │      │      │
│  │  │ >       client.connect(gateway.ip, verify_ssl=True)     │      │      │
│  │  │ E       SSLCertVerificationError: CN mismatch           │      │      │
│  │  │                                                         │      │      │
│  │  │ test_ssl.py:67: SSLCertVerificationError                │      │      │
│  │  │ ________________ end _________________                  │      │      │
│  │  │                                                         │      │      │
│  │  │ ... more failures ...                                   │      │      │
│  │  └─────────────────────────────────────────────────────────┘      │      │
│  │                                                                   │      │
│  │  Extraction:                                                      │      │
│  │  1. Find marker: "================= FAILURES ================="    │      │
│  │  2. Extract from marker to end of failures section                │      │
│  │  3. Skip everything before/after                                  │      │
│  │                                                                   │      │
│  │  Result: 200 lines (failures section) vs 50,000 (full log)        │      │
│  │  Reduction: 99.6%                                                 │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                 SEMANTIC WINDOW APPROACH                          │      │
│  │                                                                   │      │
│  │  Use case: Extract logically related sections                     │      │
│  │                                                                   │      │
│  │  Strategy: Group by test case, function, or semantic boundary     │      │
│  │                                                                   │      │
│  │  Example: Multi-test log                                          │      │
│  │  ┌─────────────────────────────────────────────────────────┐      │      │
│  │  │ test_login ... PASSED                                   │      │      │
│  │  │   [300 lines of debug logs]                             │      │      │
│  │  │                                                         │      │      │
│  │  │ test_ssl_connection ... FAILED                          │      │      │
│  │  │   [200 lines including error] ←─── Extract this window  │      │      │
│  │  │                                                         │      │      │
│  │  │ test_data_transfer ... PASSED                           │      │      │
│  │  │   [400 lines of debug logs]                             │      │      │
│  │  │                                                         │      │      │
│  │  │ test_logout ... PASSED                                  │      │      │
│  │  │   [100 lines of debug logs]                             │      │      │
│  │  └─────────────────────────────────────────────────────────┘      │      │
│  │                                                                   │      │
│  │  Algorithm:                                                       │      │
│  │  1. Parse log structure (pytest sections, timestamps, etc)        │      │
│  │  2. Identify semantic boundaries (test start/end markers)         │      │
│  │  3. Extract only sections containing failures                     │      │
│  │  4. Preserve section structure                                    │      │
│  │                                                                   │      │
│  │  Result: 200 lines (failed test section) vs 1,000 (all tests)     │      │
│  │  Reduction: 80%                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │           WINDOW VISUALIZATION                                    │      │
│  │                                                                   │      │
│  │  Original Log (50,000 lines):                                     │      │
│  │  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■             │      │
│  │  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■             │      │
│  │  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■             │      │
│  │                                                                   │      │
│  │  After Windowing (5 windows, 250 lines total):                    │      │
│  │  █████ ........ █████ ............ ████ ... ███ .... █████        │      │
│  │  Window1      Window2          Window3  Window4   Window5        │      │
│  │                                                                   │      │
│  │  Delivered Context:                                               │      │
│  │  ┌─────────────────────────────────────────────────────────┐      │      │
│  │  │ [Window 1: Lines 4510-4548]                             │      │      │
│  │  │ ... (skipped 4509 lines)                                │      │      │
│  │  │ [ERROR] SSL handshake failed                            │      │      │
│  │  │ ...                                                     │      │      │
│  │  │                                                         │      │      │
│  │  │ [Window 2: Lines 8900-8940]                             │      │      │
│  │  │ ... (skipped 4352 lines)                                │      │      │
│  │  │ [ERROR] Timeout waiting                                 │      │      │
│  │  │ ...                                                     │      │      │
│  │  │                                                         │      │      │
│  │  │ [Skipped 41,060 lines of non-error logs]                │      │      │
│  │  └─────────────────────────────────────────────────────────┘      │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              WINDOWING BEST PRACTICES                             │      │
│  │                                                                   │      │
│  │  1. ADD SKIP INDICATORS                                           │      │
│  │     Show "... (skipped N lines)" between windows                  │      │
│  │     Helps LLM understand context gaps                             │      │
│  │                                                                   │      │
│  │  2. PRESERVE LINE NUMBERS                                         │      │
│  │     Include original line numbers in windows                      │      │
│  │     Enables LLM to reference specific log lines                   │      │
│  │                                                                   │      │
│  │  3. MERGE NEARBY WINDOWS                                          │      │
│  │     If Window1 ends at line 100 and Window2 starts at line 105    │      │
│  │     → Merge into single window (lines 90-115)                     │      │
│  │     Reduces fragmentation                                         │      │
│  │                                                                   │      │
│  │  4. DYNAMIC WINDOW SIZING                                         │      │
│  │     Complex errors: larger window (±20 lines)                     │      │
│  │     Simple errors: smaller window (±5 lines)                      │      │
│  │     Adapt to error type                                           │      │
│  │                                                                   │      │
│  │  5. TOKEN BUDGET ENFORCEMENT                                      │      │
│  │     If total windows exceed budget:                               │      │
│  │       Priority 1: First error (likely root cause)                 │      │
│  │       Priority 2: Unique error types                              │      │
│  │       Priority 3: Repeated errors (summarize)                     │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Chunking Strategies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CHUNKING STRATEGIES                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Chunking: Breaking large documents into smaller, manageable pieces         │
│  Goal: Preserve semantic meaning while fitting token budgets                │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              STRATEGY 1: FIXED-SIZE CHUNKING                      │      │
│  │                                                                   │      │
│  │  Split document every N tokens/characters                         │      │
│  │                                                                   │      │
│  │  Document (10,000 tokens):                                        │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Chunk 1: Tokens 0-999      (1000 tokens)           │           │      │
│  │  │ Chunk 2: Tokens 1000-1999  (1000 tokens)           │           │      │
│  │  │ Chunk 3: Tokens 2000-2999  (1000 tokens)           │           │      │
│  │  │ ...                                                │           │      │
│  │  │ Chunk 10: Tokens 9000-9999 (1000 tokens)           │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  ✅ Pros:                                                         │      │
│  │  • Simple to implement                                            │      │
│  │  • Predictable chunk sizes                                        │      │
│  │  • Fast processing                                                │      │
│  │                                                                   │      │
│  │  ❌ Cons:                                                         │      │
│  │  • May split mid-sentence/mid-concept                             │      │
│  │  • Loses semantic coherence                                       │      │
│  │  • Context bleeding between chunks                                │      │
│  │                                                                   │      │
│  │  Use when: Speed matters more than quality                        │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │            STRATEGY 2: SEMANTIC CHUNKING                          │      │
│  │                                                                   │      │
│  │  Split at natural boundaries (paragraphs, sections, functions)    │      │
│  │                                                                   │      │
│  │  Python File:                                                     │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Chunk 1: Imports + module docstring                │           │      │
│  │  │   import anthropic                                 │           │      │
│  │  │   """Module for Claude client."""                 │           │      │
│  │  │                                                    │           │      │
│  │  │ Chunk 2: Class definition + __init__               │           │      │
│  │  │   class ClaudeClient:                              │           │      │
│  │  │       def __init__(self, api_key):                 │           │      │
│  │  │           ...                                      │           │      │
│  │  │                                                    │           │      │
│  │  │ Chunk 3: send_message method                       │           │      │
│  │  │   def send_message(self, prompt):                  │           │      │
│  │  │       ...                                          │           │      │
│  │  │                                                    │           │      │
│  │  │ Chunk 4: get_history method                        │           │      │
│  │  │   def get_history(self):                           │           │      │
│  │  │       ...                                          │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  ✅ Pros:                                                         │      │
│  │  • Preserves semantic meaning                                     │      │
│  │  • Each chunk is self-contained concept                           │      │
│  │  • Better for understanding                                       │      │
│  │                                                                   │      │
│  │  ❌ Cons:                                                         │      │
│  │  • Variable chunk sizes                                           │      │
│  │  • More complex to implement                                      │      │
│  │  • Needs format-specific parsing                                  │      │
│  │                                                                   │      │
│  │  Use when: Comprehension matters, document has structure          │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │          STRATEGY 3: OVERLAPPING CHUNKS                           │      │
│  │                                                                   │      │
│  │  Include overlap between chunks to preserve context               │      │
│  │                                                                   │      │
│  │  Document:                                                        │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Chunk 1: [────────────]                            │           │      │
│  │  │                  [────────────] Chunk 2            │           │      │
│  │  │                          [────────────] Chunk 3    │           │      │
│  │  │           └─────┬─────┘                            │           │      │
│  │  │              Overlap                               │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Example: 1000 token chunks, 200 token overlap                    │      │
│  │  • Chunk 1: Tokens 0-999                                          │      │
│  │  • Chunk 2: Tokens 800-1799   (overlap: 800-999)                  │      │
│  │  • Chunk 3: Tokens 1600-2599  (overlap: 1600-1799)                │      │
│  │                                                                   │      │
│  │  ✅ Pros:                                                         │      │
│  │  • No context loss at boundaries                                  │      │
│  │  • Captures cross-chunk relationships                             │      │
│  │  • Better for retrieval (more chances to match query)             │      │
│  │                                                                   │      │
│  │  ❌ Cons:                                                         │      │
│  │  • Higher storage/compute cost (duplication)                      │      │
│  │  • May retrieve duplicate information                             │      │
│  │                                                                   │      │
│  │  Use when: Context preservation critical (RAG systems)            │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │         STRATEGY 4: HIERARCHICAL CHUNKING                         │      │
│  │                                                                   │      │
│  │  Create chunks at multiple levels of granularity                  │      │
│  │                                                                   │      │
│  │  Documentation Site:                                              │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Level 1: Entire page (summary)                     │           │      │
│  │  │   "PARTS SSL Configuration Guide"                 │           │      │
│  │  │   Summary: How to configure SSL certs...          │           │      │
│  │  │                                                    │           │      │
│  │  │ Level 2: Sections                                  │           │      │
│  │  │   Section 1: "Overview" (300 tokens)               │           │      │
│  │  │   Section 2: "Configuration" (800 tokens)          │           │      │
│  │  │   Section 3: "Troubleshooting" (500 tokens)        │           │      │
│  │  │                                                    │           │      │
│  │  │ Level 3: Subsections                               │           │      │
│  │  │   Config > Basic Setup (200 tokens)                │           │      │
│  │  │   Config > Advanced Options (300 tokens)           │           │      │
│  │  │   Config > Examples (300 tokens)                   │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Retrieval strategy:                                              │      │
│  │  1. Search at Level 1 → Find relevant page                        │      │
│  │  2. Search at Level 2 → Find relevant section                     │      │
│  │  3. Retrieve Level 3 → Get specific content                       │      │
│  │                                                                   │      │
│  │  ✅ Pros:                                                         │      │
│  │  • Efficient multi-level search                                   │      │
│  │  • Can start broad, narrow down                                   │      │
│  │  • Flexible retrieval granularity                                 │      │
│  │                                                                   │      │
│  │  ❌ Cons:                                                         │      │
│  │  • Complex indexing                                               │      │
│  │  • Requires document structure understanding                      │      │
│  │                                                                   │      │
│  │  Use when: Large knowledge base, hierarchical docs                │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              CHUNKING SIZE OPTIMIZATION                           │      │
│  │                                                                   │      │
│  │  Rule of thumb: Chunk size depends on use case                    │      │
│  │                                                                   │      │
│  │  ┌────────────────┬────────────┬─────────────────────┐            │      │
│  │  │  Use Case      │ Chunk Size │ Reasoning           │            │      │
│  │  ├────────────────┼────────────┼─────────────────────┤            │      │
│  │  │ RAG retrieval  │ 500-1000   │ Balance coverage    │            │      │
│  │  │                │  tokens    │ vs precision        │            │      │
│  │  ├────────────────┼────────────┼─────────────────────┤            │      │
│  │  │ Code analysis  │ 200-500    │ Function-level      │            │      │
│  │  │                │  tokens    │ granularity         │            │      │
│  │  ├────────────────┼────────────┼─────────────────────┤            │      │
│  │  │ Log parsing    │ 100-300    │ Error-centric       │            │      │
│  │  │                │  tokens    │ windows             │            │      │
│  │  ├────────────────┼────────────┼─────────────────────┤            │      │
│  │  │ Long documents │ 1000-2000  │ Chapter/section     │            │      │
│  │  │                │  tokens    │ level               │            │      │
│  │  └────────────────┴────────────┴─────────────────────┘            │      │
│  │                                                                   │      │
│  │  TOO SMALL (<100 tokens):                                         │      │
│  │  • Loses context                                                  │      │
│  │  • Too many chunks to manage                                      │      │
│  │  • High retrieval overhead                                        │      │
│  │                                                                   │      │
│  │  TOO LARGE (>2000 tokens):                                        │      │
│  │  • Precision loss in retrieval                                    │      │
│  │  • May include irrelevant content                                 │      │
│  │  • Exceeds budget when combining multiple chunks                  │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              ATIYA CHUNKING IMPLEMENTATION                        │      │
│  │                                                                   │      │
│  │  For test logs:                                                   │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ def chunk_test_log(log_content):                   │           │      │
│  │  │     # Semantic chunking by test case               │           │      │
│  │  │     chunks = []                                    │           │      │
│  │  │     current_test = None                            │           │      │
│  │  │     current_chunk = []                             │           │      │
│  │  │                                                    │           │      │
│  │  │     for line in log_content.split('\n'):           │           │      │
│  │  │         if is_test_start(line):                    │           │      │
│  │  │             if current_chunk:                      │           │      │
│  │  │                 chunks.append({                    │           │      │
│  │  │                     'test': current_test,          │           │      │
│  │  │                     'content': current_chunk       │           │      │
│  │  │                 })                                 │           │      │
│  │  │             current_test = extract_test_name(line) │           │      │
│  │  │             current_chunk = [line]                 │           │      │
│  │  │         else:                                      │           │      │
│  │  │             current_chunk.append(line)             │           │      │
│  │  │                                                    │           │      │
│  │  │     # Filter: keep only failed test chunks         │           │      │
│  │  │     failed_chunks = [c for c in chunks             │           │      │
│  │  │                      if 'FAILED' in c['content']]  │           │      │
│  │  │                                                    │           │      │
│  │  │     return failed_chunks                           │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Result: Only failed test chunks delivered to LLM                 │      │
│  │  Typical reduction: 50,000 lines → 500 lines (99% savings)        │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Metadata Enrichment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      METADATA ENRICHMENT                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Metadata: Information ABOUT the context that helps LLM understand it       │
│  Enrichment: Adding metadata to raw context for better comprehension        │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              TYPES OF METADATA                                    │      │
│  │                                                                   │      │
│  │  1. LOCATION METADATA                                             │      │
│  │     • File path: /tests/test_ssl.py                               │      │
│  │     • Line numbers: Lines 45-67                                   │      │
│  │     • Section: [Test Code] [Topology] [Log]                       │      │
│  │                                                                   │      │
│  │  2. TEMPORAL METADATA                                             │      │
│  │     • Timestamp: 2026-08-20 10:28:12                              │      │
│  │     • Duration: Test ran for 12.5 seconds                         │      │
│  │     • Sequence: Error occurred after 500 successful tests         │      │
│  │                                                                   │      │
│  │  3. CONTEXTUAL METADATA                                           │      │
│  │     • Test name: test_ssl_connection                              │      │
│  │     • Device: gateway-1 (10.1.1.1)                                │      │
│  │     • Topology: gpcs_basic_topology.yaml                          │      │
│  │     • Environment: staging                                        │      │
│  │                                                                   │      │
│  │  4. CLASSIFICATION METADATA                                       │      │
│  │     • Severity: ERROR / WARN / INFO                               │      │
│  │     • Category: SSL / Network / Config                            │      │
│  │     • Component: Gateway / Portal / Agent                         │      │
│  │                                                                   │      │
│  │  5. RELATIONSHIP METADATA                                         │      │
│  │     • Linked to: topology.yaml:gateway.ssl_certificate            │      │
│  │     • Depends on: @pytest.fixture(topology)                       │      │
│  │     • Called by: test suite "SSL Tests"                           │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              BEFORE vs AFTER ENRICHMENT                           │      │
│  │                                                                   │      │
│  │  ❌ WITHOUT METADATA (raw context):                               │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ ERROR: SSL handshake failed                        │           │      │
│  │  │ Expected CN: *.prisma.local                        │           │      │
│  │  │ Received CN: localhost                             │           │      │
│  │  │                                                    │           │      │
│  │  │ def test_ssl_connection(topology):                 │           │      │
│  │  │     gateway = topology.devices['gateway']          │           │      │
│  │  │     client.connect(gateway.ip, verify_ssl=True)    │           │      │
│  │  │     assert client.is_connected                     │           │      │
│  │  │                                                    │           │      │
│  │  │ gateway:                                           │           │      │
│  │  │   ssl_certificate:                                 │           │      │
│  │  │     cert_name: localhost                           │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  LLM has to infer:                                                │      │
│  │  • Where is this from? (log? code? config?)                       │      │
│  │  • Which test failed?                                             │      │
│  │  • What line in what file?                                        │      │
│  │  • How do these pieces relate?                                    │      │
│  │                                                                   │      │
│  │  ✅ WITH METADATA (enriched context):                             │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ === FAILURE SUMMARY ===                            │           │      │
│  │  │ Test: test_ssl_connection                          │           │      │
│  │  │ File: tests/gpcs/test_ssl_tests.py                 │           │      │
│  │  │ Failed: 2026-08-20 10:28:12 (12.5s runtime)        │           │      │
│  │  │ Device: gateway-1 (10.1.1.1)                       │           │      │
│  │  │ Topology: gpcs_basic_topology.yaml                 │           │      │
│  │  │                                                    │           │      │
│  │  │ === ERROR DETAILS ===                              │           │      │
│  │  │ [test.log:4521-4523] 2026-08-20 10:28:12          │           │      │
│  │  │ ERROR: SSL handshake failed                        │           │      │
│  │  │   Expected CN: *.prisma.local                      │           │      │
│  │  │   Received CN: localhost                           │           │      │
│  │  │   Category: SSL_CERT_MISMATCH                      │           │      │
│  │  │   Severity: ERROR                                  │           │      │
│  │  │                                                    │           │      │
│  │  │ === TEST CODE ===                                  │           │      │
│  │  │ [tests/gpcs/test_ssl_tests.py:45-67]              │           │      │
│  │  │ @pytest.mark.ssl                                   │           │      │
│  │  │ def test_ssl_connection(topology):                 │           │      │
│  │  │     """Verify SSL connection to gateway"""         │           │      │
│  │  │     gateway = topology.devices['gateway']          │           │      │
│  │  │     client = SSLClient()                           │           │      │
│  │  │     client.connect(gateway.ip, verify_ssl=True)    │           │      │
│  │  │     assert client.is_connected                     │           │      │
│  │  │   Uses fixture: topology (conftest.py:build_topo)  │           │      │
│  │  │                                                    │           │      │
│  │  │ === CONFIGURATION ===                              │           │      │
│  │  │ [topologies/gpcs_basic_topology.yaml:12-18]        │           │      │
│  │  │ gateway:                                           │           │      │
│  │  │   ip: 10.1.1.1                                     │           │      │
│  │  │   ssl_certificate:                                 │           │      │
│  │  │     cert_name: localhost  # ← MISMATCH            │           │      │
│  │  │     verify: true                                   │           │      │
│  │  │   Expected: *.prisma.local (per test requirements) │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  LLM immediately understands:                                     │      │
│  │  ✓ This is a test failure                                         │      │
│  │  ✓ SSL cert mismatch in topology config                           │      │
│  │  ✓ Exact file and line to fix                                     │      │
│  │  ✓ Relationship between error, test, and config                   │      │
│  │                                                                   │      │
│  │  Result: Faster, more accurate diagnosis                          │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              METADATA ENRICHMENT PATTERNS                         │      │
│  │                                                                   │      │
│  │  PATTERN 1: INLINE TAGS                                           │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ [ERROR] [SSL] [Gateway] [10.1.1.1] [4521]          │           │      │
│  │  │ SSL handshake failed                               │           │      │
│  │  │  └─┬──┘ └┬┘  └──┬───┘  └──┬────┘  └─┬─┘            │           │      │
│  │  │    │     │      │         │         │              │           │      │
│  │  │  Level  Cat  Component  Device  LineNum            │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  PATTERN 2: SECTION HEADERS                                       │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ === LOG EXCERPT: test.log:4521-4548 ===            │           │      │
│  │  │ Timestamp: 2026-08-20 10:28:12                     │           │      │
│  │  │ Test: test_ssl_connection                          │           │      │
│  │  │ ───────────────────────────────────                │           │      │
│  │  │ [actual log content here]                          │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  PATTERN 3: STRUCTURED ANNOTATIONS                                │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ ```python                                          │           │      │
│  │  │ # File: tests/test_ssl.py                          │           │      │
│  │  │ # Lines: 45-67                                     │           │      │
│  │  │ # Fixture dependencies: topology, ssl_client       │           │      │
│  │  │ def test_ssl_connection(topology):                 │           │      │
│  │  │     ...                                            │           │      │
│  │  │ ```                                                │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  PATTERN 4: RELATIONSHIP LINKS                                    │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Error references:                                  │           │      │
│  │  │  → topology.yaml:gateway.ssl_certificate.cert_name │           │      │
│  │  │  → test_ssl.py:67 (connection attempt)             │           │      │
│  │  │  → conftest.py:build_topology (fixture)            │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              ATIYA METADATA IMPLEMENTATION                        │      │
│  │                                                                   │      │
│  │  def enrich_evidence(raw_evidence):                               │      │
│  │      enriched = {                                                 │      │
│  │          'summary': {                                             │      │
│  │              'test_name': extract_test_name(),                    │      │
│  │              'test_file': raw_evidence.test_path,                 │      │
│  │              'failure_time': parse_timestamp(),                   │      │
│  │              'runtime': calculate_duration(),                     │      │
│  │              'device': extract_device_info(),                     │      │
│  │              'topology': raw_evidence.topology_file               │      │
│  │          },                                                        │      │
│  │          'error_details': {                                       │      │
│  │              'source': 'test.log',                                │      │
│  │              'lines': '4521-4523',                                │      │
│  │              'timestamp': '2026-08-20 10:28:12',                  │      │
│  │              'severity': 'ERROR',                                 │      │
│  │              'category': classify_error_type(),                   │      │
│  │              'content': extract_error_lines()                     │      │
│  │          },                                                        │      │
│  │          'test_code': {                                           │      │
│  │              'file': 'tests/test_ssl.py',                         │      │
│  │              'lines': '45-67',                                    │      │
│  │              'fixtures': extract_fixtures(),                      │      │
│  │              'markers': extract_pytest_markers(),                 │      │
│  │              'content': get_function_body()                       │      │
│  │          },                                                        │      │
│  │          'configuration': {                                       │      │
│  │              'file': 'topology.yaml',                             │      │
│  │              'section': 'gateway.ssl_certificate',                │      │
│  │              'lines': '12-18',                                    │      │
│  │              'content': extract_relevant_yaml()                   │      │
│  │          }                                                         │      │
│  │      }                                                             │      │
│  │      return format_for_llm(enriched)                              │      │
│  │                                                                   │      │
│  │  Benefits:                                                        │      │
│  │  • Reduces ambiguity for LLM                                      │      │
│  │  • Enables precise references in diagnosis                        │      │
│  │  • Improves fix accuracy (exact file:line to change)              │      │
│  │  • Better for human review (structured output)                    │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Issues: Shrink Down the Context

### 6.1 Problem: Token Limits and Cost

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  THE CONTEXT BLOAT PROBLEM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Real-world challenge: Evidence often exceeds budget                        │
│                                                                             │
│  Example: Complex test failure in Atiya                                     │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ Available Evidence:                                               │      │
│  │                                                                   │      │
│  │ • Test log:           50,000 lines = 125,000 tokens               │      │
│  │ • Test code:           1,200 lines =   3,000 tokens               │      │
│  │ • Topology YAML:         800 lines =   2,000 tokens               │      │
│  │ • Device config:      10,000 lines =  25,000 tokens               │      │
│  │ • Previous run log:   40,000 lines = 100,000 tokens               │      │
│  │ • Debug screenshots:     5 images  =   5,000 tokens               │      │
│  │ • Stack trace:           200 lines =     500 tokens               │      │
│  │                                                                   │      │
│  │ TOTAL: 260,500 tokens                                             │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ Budget Constraints:                                               │      │
│  │                                                                   │      │
│  │ Claude Sonnet 4.6:                                                │      │
│  │ • Max context window: 200,000 tokens                              │      │
│  │ • System prompt:          500 tokens                              │      │
│  │ • Output reservation:   4,000 tokens                              │      │
│  │ • Available for context: 195,500 tokens                           │      │
│  │                                                                   │      │
│  │ ❌ PROBLEM: 260,500 tokens > 195,500 tokens                       │      │
│  │    Evidence exceeds context window by 65,000 tokens (33%)         │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ Cost Problem (even if it fit):                                    │      │
│  │                                                                   │      │
│  │ Input cost: 260,500 tokens × $3/1M = $0.78                        │      │
│  │ Output cost: 1,000 tokens × $15/1M = $0.015                       │      │
│  │ Total per diagnosis: $0.795                                       │      │
│  │                                                                   │      │
│  │ For 500 diagnoses/day:                                            │      │
│  │ • Daily: $397.50                                                  │      │
│  │ • Monthly: $8,745                                                 │      │
│  │ • Annual: $104,940                                                │      │
│  │                                                                   │      │
│  │ ❌ UNSUSTAINABLE at scale                                         │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ Performance Problem:                                              │      │
│  │                                                                   │      │
│  │ Processing time for 260K tokens:                                  │      │
│  │ • API latency: ~45-60 seconds                                     │      │
│  │ • Too slow for interactive debugging                              │      │
│  │ • Too expensive for bulk processing                               │      │
│  │                                                                   │      │
│  │ "Lost in the middle" effect:                                      │      │
│  │ • Critical evidence buried in 260K tokens                         │      │
│  │ • LLM may miss key details                                        │      │
│  │ • Lower accuracy despite more context                             │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  GOAL: Reduce 260,500 tokens → ~2,500 tokens (99% reduction)                │
│        While preserving diagnostic accuracy                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Solution 1: Smart Truncation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SMART TRUNCATION STRATEGY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Concept: Keep the most important parts, indicate what was skipped          │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              FIRST N + LAST M PATTERN                             │      │
│  │                                                                   │      │
│  │  Test Log (50,000 lines):                                         │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Lines 1-100: Test setup, initialization ──┐        │           │      │
│  │  │   [INFO] Starting test suite              │ KEEP   │           │      │
│  │  │   [INFO] Loading topology                 │ First  │           │      │
│  │  │   [INFO] Building devices                 │  100   │           │      │
│  │  │   ...                                     │        │           │      │
│  │  │                                           ──┘       │           │      │
│  │  │ Lines 101-49800: Test execution                    │           │      │
│  │  │   [DEBUG] Connection attempt 1                     │           │      │
│  │  │   [DEBUG] Sending packet...               ──┐      │           │      │
│  │  │   ... 49,700 lines of debug logs ...        │ SKIP │           │      │
│  │  │   [DEBUG] Waiting for response              │      │           │      │
│  │  │   [DEBUG] Retry attempt 2                 ──┘      │           │      │
│  │  │                                                    │           │      │
│  │  │ Lines 49801-50000: Failure + cleanup ──┐           │           │      │
│  │  │   [ERROR] SSL handshake failed         │ KEEP     │           │      │
│  │  │   [ERROR] Expected: *.prisma.local     │ Last     │           │      │
│  │  │   [ERROR] Received: localhost          │  200     │           │      │
│  │  │   [INFO] Cleaning up topology          │          │           │      │
│  │  │   [INFO] Test completed: FAILED        ──┘         │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Delivered context:                                               │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ [test.log:1-100]                                   │           │      │
│  │  │ [INFO] Starting test suite                         │           │      │
│  │  │ [INFO] Loading topology: gpcs_basic.yaml           │           │      │
│  │  │ ...                                                │           │      │
│  │  │                                                    │           │      │
│  │  │ ... (skipped 49,700 lines of debug logs) ...       │           │      │
│  │  │                                                    │           │      │
│  │  │ [test.log:49801-50000]                             │           │      │
│  │  │ [ERROR] SSL handshake failed                       │           │      │
│  │  │ [ERROR] Expected CN: *.prisma.local                │           │      │
│  │  │ [ERROR] Received CN: localhost                     │           │      │
│  │  │ [INFO] Test completed: FAILED                      │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Result: 300 lines vs 50,000 (99.4% reduction)                    │      │
│  │  Cost: ~750 tokens vs 125,000 tokens                              │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │            SMART SKIP INDICATORS                                  │      │
│  │                                                                   │      │
│  │  DON'T just remove lines silently - SHOW what was removed          │      │
│  │                                                                   │      │
│  │  ❌ BAD (silent truncation):                                      │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ [INFO] Starting test                               │           │      │
│  │  │ [ERROR] SSL handshake failed                       │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │  LLM thinks: Only 2 lines in the log?                             │      │
│  │  Problem: Missing context about what happened between             │      │
│  │                                                                   │      │
│  │  ✅ GOOD (explicit skip indicator):                               │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ [test.log:1-10]                                    │           │      │
│  │  │ [INFO] Starting test suite                         │           │      │
│  │  │ [INFO] Loading topology                            │           │      │
│  │  │                                                    │           │      │
│  │  │ ... (skipped 49,780 lines: DEBUG logs) ...         │           │      │
│  │  │ Summary of skipped section:                        │           │      │
│  │  │   • 500 connection attempts                        │           │      │
│  │  │   • All successful until final attempt             │           │      │
│  │  │   • No errors or warnings                          │           │      │
│  │  │                                                    │           │      │
│  │  │ [test.log:49790-50000]                             │           │      │
│  │  │ [ERROR] SSL handshake failed                       │           │      │
│  │  │ [ERROR] Expected: *.prisma.local                   │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │  LLM understands: Long test, worked until end, then failed        │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │            ADAPTIVE TRUNCATION                                    │      │
│  │                                                                   │      │
│  │  Adjust N and M based on log characteristics                      │      │
│  │                                                                   │      │
│  │  def adaptive_truncate(log_content, max_tokens=2000):             │      │
│  │      lines = log_content.split('\n')                              │      │
│  │      total_lines = len(lines)                                     │      │
│  │                                                                   │      │
│  │      # Count ERROR/WARN lines                                     │      │
│  │      error_lines = [i for i, line in enumerate(lines)             │      │
│  │                     if 'ERROR' in line or 'WARN' in line]         │      │
│  │                                                                   │      │
│  │      if not error_lines:                                          │      │
│  │          # No errors: Keep first 50 + last 50                     │      │
│  │          return first(50) + skip_indicator() + last(50)           │      │
│  │                                                                   │      │
│  │      # Find first and last error positions                        │      │
│  │      first_error_pos = error_lines[0]                             │      │
│  │      last_error_pos = error_lines[-1]                             │      │
│  │                                                                   │      │
│  │      # Include:                                                   │      │
│  │      # • First 20 lines (setup)                                   │      │
│  │      # • 10 lines before first error                              │      │
│  │      # • All lines between first and last error                   │      │
│  │      # • Last 20 lines (cleanup)                                  │      │
│  │                                                                   │      │
│  │      sections = [                                                 │      │
│  │          lines[0:20],                                             │      │
│  │          skip_indicator(lines_skipped=first_error_pos - 30),      │      │
│  │          lines[first_error_pos-10 : last_error_pos+10],           │      │
│  │          skip_indicator(lines_skipped=...),                       │      │
│  │          lines[-20:]                                              │      │
│  │      ]                                                             │      │
│  │      return '\n'.join(sections)                                   │      │
│  │                                                                   │      │
│  │  Benefits:                                                        │      │
│  │  • Preserves error context (what led to it, what followed)        │      │
│  │  • Keeps setup/teardown info (helps identify root cause)          │      │
│  │  • Adaptive to log structure                                      │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              TRUNCATION ROI                                       │      │
│  │                                                                   │      │
│  │  Before truncation:                                               │      │
│  │  • 50,000 lines = 125,000 tokens                                  │      │
│  │  • Cost: $0.375 per diagnosis                                     │      │
│  │  • Time: 45 seconds                                               │      │
│  │                                                                   │      │
│  │  After smart truncation:                                          │      │
│  │  • 300 lines = 750 tokens                                         │      │
│  │  • Cost: $0.0023 per diagnosis                                    │      │
│  │  • Time: 5 seconds                                                │      │
│  │                                                                   │      │
│  │  Savings per diagnosis:                                           │      │
│  │  • Cost: 99.4% reduction ($0.375 → $0.0023)                       │      │
│  │  • Time: 89% reduction (45s → 5s)                                 │      │
│  │  • Tokens: 99.4% reduction (125K → 750)                           │      │
│  │                                                                   │      │
│  │  For 500 diagnoses/day:                                           │      │
│  │  • Cost savings: $186.40/day = $40,900/year                       │      │
│  │  • Time savings: 5.5 hours/day                                    │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Solution 2: Extraction

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EXTRACTION STRATEGY                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Concept: Extract ONLY relevant sections, discard everything else           │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              ERROR-FOCUSED EXTRACTION                             │      │
│  │                                                                   │      │
│  │  Test Log (50,000 lines):                                         │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Line 1:    [INFO] Test starting                    │           │      │
│  │  │ Line 2:    [DEBUG] Loading config                  │           │      │
│  │  │ ...                                                │           │      │
│  │  │ Line 4510: [WARN] Using self-signed cert ──┐       │           │      │
│  │  │ Line 4511: [WARN] CN mismatch warning      │       │           │      │
│  │  │ ...                                        │ Extract│           │      │
│  │  │ Line 4521: [ERROR] SSL handshake failed    │ this  │           │      │
│  │  │ Line 4522: Expected: *.prisma.local        │ window│           │      │
│  │  │ Line 4523: Received: localhost            ──┘       │           │      │
│  │  │ ...                                                │           │      │
│  │  │ Line 8910: [WARN] Connection slow                  │           │      │
│  │  │ Line 8912: [ERROR] Timeout on retry ───┐           │           │      │
│  │  │ Line 8913: Device: 10.1.1.1            │ Extract   │           │      │
│  │  │ Line 8914: Attempt: 3/3                │ this      │           │      │
│  │  │ Line 8915: [ERROR] Giving up          ───┘         │           │      │
│  │  │ ...                                                │           │      │
│  │  │ Line 50000: [INFO] Test completed: FAILED          │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Extraction algorithm:                                            │      │
│  │  1. Scan for ERROR lines                                          │      │
│  │  2. For each ERROR, extract context window:                       │      │
│  │     - 10 lines before (leading context)                           │      │
│  │     - ERROR line itself                                           │      │
│  │     - 10 lines after (consequences)                               │      │
│  │  3. Scan for WARN lines near ERRORs                               │      │
│  │  4. Merge overlapping windows                                     │      │
│  │  5. Discard everything else                                       │      │
│  │                                                                   │      │
│  │  Result: 2 windows × 21 lines = 42 lines vs 50,000                │      │
│  │  Reduction: 99.92%                                                │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              RELEVANCE SCORING EXTRACTION                         │      │
│  │                                                                   │      │
│  │  More sophisticated: Score each line by relevance                 │      │
│  │                                                                   │      │
│  │  Scoring rules:                                                   │      │
│  │  • ERROR line:     100 points                                     │      │
│  │  • WARN line:       50 points                                     │      │
│  │  • Exception/Trace: 80 points                                     │      │
│  │  • Near ERROR (±5): +20 points                                    │      │
│  │  • Stack frame:     40 points                                     │      │
│  │  • FAILED marker:   90 points                                     │      │
│  │  • INFO/DEBUG:       0 points (unless near ERROR)                 │      │
│  │  • SUCCESS marker:   0 points                                     │      │
│  │                                                                   │      │
│  │  Example scoring:                                                 │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Line │ Content                       │ Score        │           │      │
│  │  │ ─────┼───────────────────────────────┼──────        │           │      │
│  │  │ 4508 │ [DEBUG] Connection OK         │   0          │           │      │
│  │  │ 4509 │ [DEBUG] Sending packet        │   0          │           │      │
│  │  │ 4510 │ [WARN] Self-signed cert       │  70 (50+20)  │           │      │
│  │  │ 4511 │ [WARN] CN mismatch            │  70 (50+20)  │           │      │
│  │  │ 4512 │ [DEBUG] Verifying cert        │  20 (near)   │           │      │
│  │  │ 4521 │ [ERROR] SSL failed            │ 100          │           │      │
│  │  │ 4522 │   Expected: *.prisma          │  20 (near)   │           │      │
│  │  │ 4523 │   Received: localhost         │  20 (near)   │           │      │
│  │  │ 4524 │ [DEBUG] Closing connection    │  20 (near)   │           │      │
│  │  │ 4530 │ [INFO] Cleanup started        │   0          │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Extract lines with score > threshold (e.g., 15):                 │      │
│  │  → Lines 4510, 4511, 4512, 4521, 4522, 4523, 4524                 │      │
│  │  → 7 lines extracted, 49,993 lines discarded                      │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              PATTERN-BASED EXTRACTION                             │      │
│  │                                                                   │      │
│  │  Extract based on known patterns (pytest, PARTS logs, etc.)       │      │
│  │                                                                   │      │
│  │  PYTEST LOG PATTERN:                                              │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ ============= FAILURES =============                │           │      │
│  │  │ _________ test_ssl_connection _________             │           │      │
│  │  │                                                    │           │      │
│  │  │     def test_ssl_connection(topology):             │           │      │
│  │  │         gateway = topology.devices['gateway']      │           │      │
│  │  │ >       client.connect(gateway.ip, verify=True)    │           │      │
│  │  │ E       SSLCertVerificationError: CN mismatch      │           │      │
│  │  │                                                    │           │      │
│  │  │ test_ssl.py:67: SSLCertVerificationError           │           │      │
│  │  │ ____________________________________________        │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Extraction:                                                      │      │
│  │  1. Find "FAILURES" section marker                                │      │
│  │  2. Extract from marker until next "=" divider                    │      │
│  │  3. Parse test name, file:line, error message                     │      │
│  │  4. Discard all other sections (PASSED tests, etc.)               │      │
│  │                                                                   │      │
│  │  PARTS LOG PATTERN:                                               │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ 2026-08-20 10:28:12 [partsfwk] ERROR:              │           │      │
│  │  │   Action failed: configure_ssl                     │           │      │
│  │  │   Device: gateway-1                                │           │      │
│  │  │   Reason: Certificate name mismatch                │           │      │
│  │  │   Expected: *.prisma.local                         │           │      │
│  │  │   Actual: localhost                                │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Extraction:                                                      │      │
│  │  1. Find " ERROR:" markers                                        │      │
│  │  2. Extract indented block following ERROR                        │      │
│  │  3. Parse structured fields (Action, Device, Reason, etc.)        │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              EXTRACTION FLOW DIAGRAM                              │      │
│  │                                                                   │      │
│  │   Full Log (50,000 lines)                                         │      │
│  │         │                                                         │      │
│  │         ▼                                                         │      │
│  │   ┌──────────────┐                                                │      │
│  │   │  Scan for    │                                                │      │
│  │   │  ERROR/WARN  │                                                │      │
│  │   └──────┬───────┘                                                │      │
│  │          │                                                        │      │
│  │          ▼                                                        │      │
│  │   Found 2 ERRORs, 3 WARNs                                         │      │
│  │          │                                                        │      │
│  │          ▼                                                        │      │
│  │   ┌──────────────┐                                                │      │
│  │   │  Extract     │                                                │      │
│  │   │  windows     │                                                │      │
│  │   │  (±10 lines) │                                                │      │
│  │   └──────┬───────┘                                                │      │
│  │          │                                                        │      │
│  │          ▼                                                        │      │
│  │   5 windows × 21 lines = 105 lines                                │      │
│  │          │                                                        │      │
│  │          ▼                                                        │      │
│  │   ┌──────────────┐                                                │      │
│  │   │  Merge       │                                                │      │
│  │   │  overlapping │                                                │      │
│  │   └──────┬───────┘                                                │      │
│  │          │                                                        │      │
│  │          ▼                                                        │      │
│  │   2 merged windows = 65 lines                                     │      │
│  │          │                                                        │      │
│  │          ▼                                                        │      │
│  │   ┌──────────────┐                                                │      │
│  │   │  Add metadata│                                                │      │
│  │   │  + structure │                                                │      │
│  │   └──────┬───────┘                                                │      │
│  │          │                                                        │      │
│  │          ▼                                                        │      │
│  │   Formatted context (80 lines with metadata)                      │      │
│  │   = 200 tokens                                                    │      │
│  │                                                                   │      │
│  │   Reduction: 50,000 → 80 lines (99.84%)                           │      │
│  │   Cost: $0.375 → $0.0006 (99.84% savings)                         │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.4 Solution 3: Summarization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SUMMARIZATION STRATEGY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Concept: Pre-summarize large sections, include summaries + critical details│
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              TWO-STAGE PROCESSING                                 │      │
│  │                                                                   │      │
│  │  Stage 1: Summarize each section                                  │      │
│  │  Stage 2: Combine summaries + critical details for final diagnosis│      │
│  │                                                                   │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ STAGE 1: SECTION SUMMARIZATION                     │           │      │
│  │  │                                                    │           │      │
│  │  │ Test log (50,000 lines) →  Break into sections     │           │      │
│  │  │                                                    │           │      │
│  │  │ Section 1: Setup (lines 1-1000)                    │           │      │
│  │  │   ┌─────────────────────────────────────────┐      │           │      │
│  │  │   │ [Full 1000 lines]                       │      │           │      │
│  │  │   │ [INFO] Loading topology...              │      │           │      │
│  │  │   │ [DEBUG] Building devices...             │      │           │      │
│  │  │   │ ...                                     │      │           │      │
│  │  │   └──────────────┬──────────────────────────┘      │           │      │
│  │  │                  │ LLM summarize                   │           │      │
│  │  │                  ▼                                 │           │      │
│  │  │   ┌─────────────────────────────────────────┐      │           │      │
│  │  │   │ SUMMARY (50 tokens):                    │      │           │      │
│  │  │   │ Setup phase loaded topology             │      │           │      │
│  │  │   │ gpcs_basic.yaml, built 3 devices        │      │           │      │
│  │  │   │ (gateway, portal, agent), no errors.    │      │           │      │
│  │  │   └─────────────────────────────────────────┘      │           │      │
│  │  │                                                    │           │      │
│  │  │ Section 2: Execution (lines 1001-49000)            │           │      │
│  │  │   ┌─────────────────────────────────────────┐      │           │      │
│  │  │   │ [Full 48,000 lines of DEBUG logs]       │      │           │      │
│  │  │   └──────────────┬──────────────────────────┘      │           │      │
│  │  │                  │ LLM summarize                   │           │      │
│  │  │                  ▼                                 │           │      │
│  │  │   ┌─────────────────────────────────────────┐      │           │      │
│  │  │   │ SUMMARY (100 tokens):                   │      │           │      │
│  │  │   │ Test executed 500 connection attempts,  │      │           │      │
│  │  │   │ all succeeded. SSL warnings appeared    │      │           │      │
│  │  │   │ starting at attempt 450 regarding       │      │           │      │
│  │  │   │ certificate CN mismatch. Final attempt  │      │           │      │
│  │  │   │ failed with SSL handshake error.        │      │           │      │
│  │  │   └─────────────────────────────────────────┘      │           │      │
│  │  │                                                    │           │      │
│  │  │ Section 3: Failure (lines 49001-50000)             │           │      │
│  │  │   ┌─────────────────────────────────────────┐      │           │      │
│  │  │   │ [Full 1000 lines with errors]           │      │           │      │
│  │  │   │ [ERROR] SSL handshake failed            │      │           │      │
│  │  │   │ Expected: *.prisma.local                │      │           │      │
│  │  │   │ Received: localhost                     │      │           │      │
│  │  │   │ ...                                     │      │           │      │
│  │  │   └──────────────┬──────────────────────────┘      │           │      │
│  │  │                  │ Keep full (contains errors)     │           │      │
│  │  │                  ▼                                 │           │      │
│  │  │   ┌─────────────────────────────────────────┐      │           │      │
│  │  │   │ FULL SECTION (250 tokens)               │      │           │      │
│  │  │   └─────────────────────────────────────────┘      │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ STAGE 2: COMBINE FOR DIAGNOSIS                     │           │      │
│  │  │                                                    │           │      │
│  │  │ Context = Summary1 + Summary2 + FullSection3       │           │      │
│  │  │         = 50 + 100 + 250 = 400 tokens              │           │      │
│  │  │                                                    │           │      │
│  │  │ vs original: 125,000 tokens                        │           │      │
│  │  │ Reduction: 99.68%                                  │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              HIERARCHICAL SUMMARIZATION                           │      │
│  │                                                                   │      │
│  │  For very large logs: Multi-level summarization                   │      │
│  │                                                                   │      │
│  │  Level 1: Micro-summaries (every 1000 lines → 1 sentence)         │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Lines 1-1000:    "Setup completed successfully"    │           │      │
│  │  │ Lines 1001-2000: "Test iterations 1-50, all pass"  │           │      │
│  │  │ Lines 2001-3000: "Test iterations 51-100, all pass"│           │      │
│  │  │ ...                                                │           │      │
│  │  │ Lines 49001-50000: "Final iteration failed: SSL"   │           │      │
│  │  │                                                    │           │      │
│  │  │ 50 micro-summaries (~500 tokens)                   │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Level 2: Macro-summary (50 summaries → overall summary)          │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Combine 50 micro-summaries:                        │           │      │
│  │  │                                                    │           │      │
│  │  │ "Test executed 500 SSL connection iterations,      │           │      │
│  │  │  first 450 succeeded, warnings started appearing   │           │      │
│  │  │  about cert mismatch, final attempt failed with    │           │      │
│  │  │  SSL handshake error. Root cause: cert_name in     │           │      │
│  │  │  topology set to 'localhost' instead of expected   │           │      │
│  │  │  '*.prisma.local'."                                │           │      │
│  │  │                                                    │           │      │
│  │  │ Overall summary (~100 tokens)                      │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Final context = Macro-summary + Error details                    │      │
│  │                = 100 + 200 = 300 tokens                           │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              SUMMARIZATION PROMPTS                                │      │
│  │                                                                   │      │
│  │  Prompt for summarizing log sections:                             │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ System: You are summarizing test execution logs.   │           │      │
│  │  │         Provide concise summaries focusing on:     │           │      │
│  │  │         - What was tested                          │           │      │
│  │  │         - Success/failure status                   │           │      │
│  │  │         - Any warnings or anomalies                │           │      │
│  │  │         - Key metrics (iterations, timing)         │           │      │
│  │  │                                                    │           │      │
│  │  │ User: Summarize this log section (1000 lines):     │           │      │
│  │  │       [log content]                                │           │      │
│  │  │                                                    │           │      │
│  │  │       Limit summary to 2-3 sentences.              │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Example summary output:                                          │      │
│  │  "Test setup phase loaded topology gpcs_basic.yaml and built      │      │
│  │   3 devices (gateway, portal, agent). Configuration validation    │      │
│  │   passed. No errors during initialization."                       │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              SUMMARIZATION TRADEOFFS                              │      │
│  │                                                                   │      │
│  │  ✅ Pros:                                                         │      │
│  │  • Massive token reduction (99%+)                                 │      │
│  │  • Retains high-level understanding                               │      │
│  │  • Preserves critical details in full                             │      │
│  │  • Works with any size log                                        │      │
│  │                                                                   │      │
│  │  ❌ Cons:                                                         │      │
│  │  • Two API calls (summarize, then diagnose)                       │      │
│  │  • Summary quality depends on prompt                              │      │
│  │  • May lose subtle details                                        │      │
│  │  • Higher initial cost (2 LLM calls)                              │      │
│  │                                                                   │      │
│  │  Cost comparison (50K line log):                                  │      │
│  │                                                                   │      │
│  │  Option 1: Send full log                                          │      │
│  │    • 1 call: 125K tokens input                                    │      │
│  │    • Cost: $0.375                                                 │      │
│  │                                                                   │      │
│  │  Option 2: Summarize first                                        │      │
│  │    • Call 1: Summarize 125K → 100 token summary                   │      │
│  │      Cost: $0.375 (input) + $0.0015 (output) = $0.377             │      │
│  │    • Call 2: Diagnose with summary + errors (300 tokens)          │      │
│  │      Cost: $0.0009 (input) + $0.015 (output) = $0.016             │      │
│  │    • Total: $0.393                                                │      │
│  │                                                                   │      │
│  │  ⚠️ Summarization MORE expensive for single diagnosis!            │      │
│  │                                                                   │      │
│  │  BUT: Amortize summarization cost across multiple uses            │      │
│  │                                                                   │      │
│  │  If same log analyzed 10 times:                                   │      │
│  │    • Option 1: 10 × $0.375 = $3.75                                │      │
│  │    • Option 2: $0.377 (summarize once) + 10 × $0.016 = $0.537     │      │
│  │    • Savings: 85.7%                                               │      │
│  │                                                                   │      │
│  │  Use when: Same logs queried multiple times (dashboards, reports) │      │
│  │  Avoid when: One-time diagnosis needed                            │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.5 Solution 4: Caching

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PROMPT CACHING STRATEGY                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Concept: Cache static context, only send changing parts                    │
│                                                                             │
│  Claude supports Prompt Caching: Cache up to 5 min, 90% cost reduction      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              WHAT TO CACHE vs WHAT TO SEND                        │      │
│  │                                                                   │      │
│  │  Typical Atiya diagnosis request:                                 │      │
│  │                                                                   │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ STATIC (same across many diagnoses):              │           │      │
│  │  │ • System prompt (500 tokens)                       │           │      │
│  │  │   "You are a PARTS test expert..."                 │           │      │
│  │  │ • Test code (3,000 tokens)                         │           │      │
│  │  │   def test_ssl_connection(topology): ...           │           │      │
│  │  │ • Topology YAML (2,000 tokens)                     │           │      │
│  │  │   gateway: {...}                                   │           │      │
│  │  │                                                    │           │      │
│  │  │ Total static: 5,500 tokens                         │           │      │
│  │  │ ✅ CACHE THIS (lasts 5 minutes)                    │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ DYNAMIC (changes per diagnosis):                   │           │      │
│  │  │ • Test log excerpt (500 tokens)                    │           │      │
│  │  │   [ERROR] SSL handshake failed...                  │           │      │
│  │  │ • Error details (100 tokens)                       │           │      │
│  │  │   Expected: *.prisma.local                         │           │      │
│  │  │                                                    │           │      │
│  │  │ Total dynamic: 600 tokens                          │           │      │
│  │  │ ❌ SEND FRESH each time                            │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              HOW PROMPT CACHING WORKS                             │      │
│  │                                                                   │      │
│  │  Request 1 (cache MISS):                                          │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ System prompt (500 tokens)                         │           │      │
│  │  │ Test code (3,000 tokens)                           │           │      │
│  │  │ Topology (2,000 tokens)                            │           │      │
│  │  │ ↓ Mark as cacheable ↓                              │           │      │
│  │  │ ---CACHE_BOUNDARY---                               │           │      │
│  │  │ Log excerpt (600 tokens)                           │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Anthropic API:                                                   │      │
│  │  • Processes all 6,100 tokens                                     │      │
│  │  • Caches first 5,500 tokens                                      │      │
│  │  • Charges: 6,100 input tokens at full price                      │      │
│  │  • Returns: cache_creation_input_tokens: 5,500                    │      │
│  │                                                                   │      │
│  │  Request 2 (within 5 minutes, cache HIT):                         │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ [CACHED: 5,500 tokens]                             │           │      │
│  │  │ ---CACHE_BOUNDARY---                               │           │      │
│  │  │ Different log excerpt (600 tokens)                 │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Anthropic API:                                                   │      │
│  │  • Retrieves cached 5,500 tokens (no reprocessing)                │      │
│  │  • Processes new 600 tokens                                       │      │
│  │  • Charges:                                                       │      │
│  │    - 5,500 cached tokens × $0.30/1M = $0.00165 (90% off)          │      │
│  │    - 600 new tokens × $3.00/1M = $0.0018                          │      │
│  │    - Total: $0.00345 (vs $0.0183 without caching)                 │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              IMPLEMENTATION IN ATIYA                              │      │
│  │                                                                   │      │
│  │  def diagnose_with_caching(test_failure):                         │      │
│  │      # Static context (will be cached)                            │      │
│  │      system_prompt = """                                          │      │
│  │      You are a PARTS test failure expert.                         │      │
│  │      Analyze evidence and provide root cause.                     │      │
│  │      """                                                          │      │
│  │                                                                   │      │
│  │      test_code = load_test_code(test_failure.test_file)           │      │
│  │      topology = load_topology(test_failure.topology_file)         │      │
│  │                                                                   │      │
│  │      # Dynamic context (changes per failure)                      │      │
│  │      log_excerpt = extract_errors(test_failure.log_file)          │      │
│  │                                                                   │      │
│  │      # Compose request with cache boundary                        │      │
│  │      response = client.messages.create(                           │      │
│  │          model="claude-sonnet-4-6",                               │      │
│  │          system=[                                                 │      │
│  │              {                                                    │      │
│  │                  "type": "text",                                  │      │
│  │                  "text": system_prompt,                           │      │
│  │                  "cache_control": {"type": "ephemeral"}           │      │
│  │              }                                                    │      │
│  │          ],                                                        │      │
│  │          messages=[                                               │      │
│  │              {                                                    │      │
│  │                  "role": "user",                                  │      │
│  │                  "content": [                                     │      │
│  │                      {                                            │      │
│  │                          "type": "text",                          │      │
│  │                          "text": f"Test Code:\n{test_code}",      │      │
│  │                          "cache_control": {"type": "ephemeral"}   │      │
│  │                      },                                           │      │
│  │                      {                                            │      │
│  │                          "type": "text",                          │      │
│  │                          "text": f"Topology:\n{topology}",        │      │
│  │                          "cache_control": {"type": "ephemeral"}   │      │
│  │                      },                                           │      │
│  │                      {                                            │      │
│  │                          "type": "text",                          │      │
│  │                          "text": f"Error Log:\n{log_excerpt}"     │      │
│  │                          # No cache_control = not cached          │      │
│  │                      }                                            │      │
│  │                  ]                                                │      │
│  │              }                                                    │      │
│  │          ]                                                        │      │
│  │      )                                                            │      │
│  │                                                                   │      │
│  │      return response.content[0].text                              │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              CACHING ROI ANALYSIS                                 │      │
│  │                                                                   │      │
│  │  Scenario: Diagnosing 50 tests from same test suite               │      │
│  │  (same test code + topology, different log excerpts)              │      │
│  │                                                                   │      │
│  │  WITHOUT CACHING:                                                 │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Per diagnosis:                                     │           │      │
│  │  │   Static context: 5,500 tokens                     │           │      │
│  │  │   Dynamic context: 600 tokens                      │           │      │
│  │  │   Total: 6,100 tokens                              │           │      │
│  │  │                                                    │           │      │
│  │  │ Cost per diagnosis:                                │           │      │
│  │  │   6,100 × $3/1M = $0.0183                          │           │      │
│  │  │                                                    │           │      │
│  │  │ 50 diagnoses:                                      │           │      │
│  │  │   50 × $0.0183 = $0.915                            │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  WITH CACHING:                                                    │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Diagnosis 1 (cache creation):                      │           │      │
│  │  │   Full 6,100 tokens: $0.0183                       │           │      │
│  │  │                                                    │           │      │
│  │  │ Diagnoses 2-50 (cache hits):                       │           │      │
│  │  │   Cached 5,500 × $0.30/1M = $0.00165               │           │      │
│  │  │   Fresh 600 × $3/1M = $0.0018                      │           │      │
│  │  │   Total per: $0.00345                              │           │      │
│  │  │                                                    │           │      │
│  │  │ 49 cache hits × $0.00345 = $0.169                  │           │      │
│  │  │                                                    │           │      │
│  │  │ Total: $0.0183 + $0.169 = $0.187                   │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  SAVINGS:                                                         │      │
│  │  • $0.915 → $0.187                                                │      │
│  │  • 79.6% cost reduction                                           │      │
│  │  • $0.728 saved per 50 diagnoses                                  │      │
│  │                                                                   │      │
│  │  For 500 diagnoses/day (10 batches of 50):                        │      │
│  │  • Without caching: 500 × $0.0183 = $9.15/day                     │      │
│  │  • With caching: 10 × $0.187 = $1.87/day                          │      │
│  │  • Daily savings: $7.28                                           │      │
│  │  • Annual savings: $1,597                                         │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              CACHING BEST PRACTICES                               │      │
│  │                                                                   │      │
│  │  1. CACHE LARGE, STATIC CONTENT                                   │      │
│  │     ✅ System prompts (same across all requests)                  │      │
│  │     ✅ Test code (same test suite)                                │      │
│  │     ✅ Topology/config (same testbed)                             │      │
│  │     ✅ Documentation (RAG knowledge base)                          │      │
│  │     ❌ Log excerpts (unique per failure)                          │      │
│  │     ❌ Timestamps, run IDs (always changing)                      │      │
│  │                                                                   │      │
│  │  2. MINIMUM CACHEABLE SIZE: 1024 tokens                           │      │
│  │     Caching < 1024 tokens has no benefit                          │      │
│  │     Combine small sections to reach threshold                     │      │
│  │                                                                   │      │
│  │  3. CACHE DURATION: 5 minutes                                     │      │
│  │     Plan request batches within 5-minute windows                  │      │
│  │     If processing 100 tests, batch in groups of 20-30             │      │
│  │                                                                   │      │
│  │  4. CACHE BOUNDARIES MATTER                                       │      │
│  │     Cache is prefix-based: Must match from start                  │      │
│  │     If system prompt changes, entire cache invalidated            │      │
│  │     Put most stable content first                                 │      │
│  │                                                                   │      │
│  │  5. MONITOR CACHE METRICS                                         │      │
│  │     response.usage.cache_creation_input_tokens                    │      │
│  │     response.usage.cache_read_input_tokens                        │      │
│  │     Track hit rate: cache_read / total_requests                   │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.6 ROI: Cost Reduction Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  CONTEXT ENGINEERING ROI SUMMARY                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Baseline: 500 test diagnoses/day without context engineering               │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              BASELINE COST (NO OPTIMIZATION)                      │      │
│  │                                                                   │      │
│  │  Per diagnosis:                                                   │      │
│  │  • Full log: 125,000 tokens                                       │      │
│  │  • Test code: 3,000 tokens                                        │      │
│  │  • Topology: 2,000 tokens                                         │      │
│  │  • Total input: 130,000 tokens                                    │      │
│  │  • Output: 1,000 tokens                                           │      │
│  │                                                                   │      │
│  │  Cost per diagnosis:                                              │      │
│  │  • Input: 130,000 × $3/1M = $0.39                                 │      │
│  │  • Output: 1,000 × $15/1M = $0.015                                │      │
│  │  • Total: $0.405                                                  │      │
│  │                                                                   │      │
│  │  Daily: 500 × $0.405 = $202.50                                    │      │
│  │  Monthly: $202.50 × 22 = $4,455                                   │      │
│  │  Annual: $4,455 × 12 = $53,460                                    │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │        OPTIMIZED COST (ALL STRATEGIES COMBINED)                   │      │
│  │                                                                   │      │
│  │  Strategy application:                                            │      │
│  │  1. Extraction: 125K tokens → 2K tokens (98.4% reduction)         │      │
│  │  2. Smart truncation: Include metadata (+200 tokens)              │      │
│  │  3. Caching: Cache test code + topology (5K tokens)               │      │
│  │                                                                   │      │
│  │  First diagnosis (cache creation):                                │      │
│  │  • Input: 2,000 (log) + 5,000 (cached) = 7,000 tokens             │      │
│  │  • Output: 1,000 tokens                                           │      │
│  │  • Cost: $0.021 + $0.015 = $0.036                                 │      │
│  │                                                                   │      │
│  │  Subsequent diagnoses (cache hit):                                │      │
│  │  • Cached: 5,000 × $0.30/1M = $0.0015                             │      │
│  │  • Fresh: 2,000 × $3/1M = $0.006                                  │      │
│  │  • Output: 1,000 × $15/1M = $0.015                                │      │
│  │  • Total: $0.0225                                                 │      │
│  │                                                                   │      │
│  │  Average cost (assuming 50 diagnoses per cache cycle):            │      │
│  │  • (1 × $0.036 + 49 × $0.0225) / 50 = $0.023/diagnosis            │      │
│  │                                                                   │      │
│  │  Daily: 500 × $0.023 = $11.50                                     │      │
│  │  Monthly: $11.50 × 22 = $253                                      │      │
│  │  Annual: $253 × 12 = $3,036                                       │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              SAVINGS BREAKDOWN                                    │      │
│  │                                                                   │      │
│  │  ┌────────────────────┬─────────────┬─────────────┬─────────┐     │      │
│  │  │ Metric             │  Baseline   │  Optimized  │ Savings │     │      │
│  │  ├────────────────────┼─────────────┼─────────────┼─────────┤     │      │
│  │  │ Cost per diagnosis │  $0.405     │  $0.023     │  94.3%  │     │      │
│  │  │ Daily cost         │  $202.50    │  $11.50     │  $191   │     │      │
│  │  │ Monthly cost       │  $4,455     │  $253       │  $4,202 │     │      │
│  │  │ Annual cost        │  $53,460    │  $3,036     │  $50,424│     │      │
│  │  ├────────────────────┼─────────────┼─────────────┼─────────┤     │      │
│  │  │ Tokens per diag    │  130,000    │  2,250*     │  98.3%  │     │      │
│  │  │ Processing time    │  45s        │  6s         │  86.7%  │     │      │
│  │  └────────────────────┴─────────────┴─────────────┴─────────┘     │      │
│  │  * Average including cached tokens                                │      │
│  │                                                                   │      │
│  │  🎯 TOTAL ANNUAL SAVINGS: $50,424                                 │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              IMPLEMENTATION INVESTMENT                            │      │
│  │                                                                   │      │
│  │  Development costs:                                               │      │
│  │  • Extraction logic: 20 hours @ $150/hr = $3,000                  │      │
│  │  • Caching implementation: 10 hours @ $150/hr = $1,500            │      │
│  │  • Metadata enrichment: 15 hours @ $150/hr = $2,250               │      │
│  │  • Testing + refinement: 15 hours @ $150/hr = $2,250              │      │
│  │  • Total investment: $9,000                                       │      │
│  │                                                                   │      │
│  │  Payback period:                                                  │      │
│  │  • Monthly savings: $4,202                                        │      │
│  │  • Payback: $9,000 / $4,202 = 2.1 months                          │      │
│  │                                                                   │      │
│  │  1-year ROI:                                                      │      │
│  │  • Investment: $9,000                                             │      │
│  │  • Return: $50,424                                                │      │
│  │  • ROI: ($50,424 - $9,000) / $9,000 = 460%                        │      │
│  │                                                                   │      │
│  │  ✅ COMPELLING BUSINESS CASE                                      │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              SENSITIVITY ANALYSIS                                 │      │
│  │                                                                   │      │
│  │  What if diagnosis volume changes?                                │      │
│  │                                                                   │      │
│  │  ┌────────────────┬─────────────┬────────────┬────────────┐       │      │
│  │  │ Daily diagnoses│ Baseline    │ Optimized  │ Annual     │       │      │
│  │  │                │ annual cost │ annual cost│ savings    │       │      │
│  │  ├────────────────┼─────────────┼────────────┼────────────┤       │      │
│  │  │  100           │  $10,692    │    $607    │  $10,085   │       │      │
│  │  │  250           │  $26,730    │  $1,518    │  $25,212   │       │      │
│  │  │  500 (current) │  $53,460    │  $3,036    │  $50,424   │       │      │
│  │  │  1000          │ $106,920    │  $6,072    │ $100,848   │       │      │
│  │  │  2000          │ $213,840    │ $12,144    │ $201,696   │       │      │
│  │  └────────────────┴─────────────┴────────────┴────────────┘       │      │
│  │                                                                   │      │
│  │  Savings scale linearly with volume                               │      │
│  │  Higher volume → Higher ROI                                       │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Core Mechanics

### 7.1 Context Retrieval Patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT RETRIEVAL PATTERNS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              PATTERN 1: DIRECT RETRIEVAL                          │      │
│  │                                                                   │      │
│  │  Use when: Evidence location known upfront                        │      │
│  │                                                                   │      │
│  │  Flow:                                                            │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Test failure event                                 │           │      │
│  │  │   ├─ test_path: /tests/test_ssl.py                 │           │      │
│  │  │   ├─ log_path: /logs/test_run_12345.log            │           │      │
│  │  │   └─ topology_path: /topologies/gpcs_basic.yaml    │           │      │
│  │  │         │                                          │           │      │
│  │  │         ▼                                          │           │      │
│  │  │ Read files directly:                               │           │      │
│  │  │   test_code = read(test_path)                      │           │      │
│  │  │   log_content = read(log_path)                     │           │      │
│  │  │   topology = read(topology_path)                   │           │      │
│  │  │         │                                          │           │      │
│  │  │         ▼                                          │           │      │
│  │  │ Evidence collected ✓                               │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Example implementation:                                          │      │
│  │    def collect_evidence_direct(failure_event):                    │      │
│  │        evidence = {                                               │      │
│  │            'test_code': Path(failure_event.test_path).read_text(),│      │
│  │            'log': Path(failure_event.log_path).read_text(),       │      │
│  │            'topology': Path(failure_event.topology_path).read(),  │      │
│  │        }                                                          │      │
│  │        return evidence                                            │      │
│  │                                                                   │      │
│  │  ✅ Pros: Fast, simple, deterministic                             │      │
│  │  ❌ Cons: Only works when paths are known                         │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              PATTERN 2: SEARCH-BASED RETRIEVAL                    │      │
│  │                                                                   │      │
│  │  Use when: Evidence location unknown, must search                 │      │
│  │                                                                   │      │
│  │  Flow:                                                            │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Query: "SSL connection test failure"               │           │      │
│  │  │         │                                          │           │      │
│  │  │         ▼                                          │           │      │
│  │  │ Search strategies:                                 │           │      │
│  │  │   1. Grep logs for "SSL" + "ERROR"                 │           │      │
│  │  │   2. Find test files matching "*ssl*"              │           │      │
│  │  │   3. Vector search in documentation                │           │      │
│  │  │         │                                          │           │      │
│  │  │         ▼                                          │           │      │
│  │  │ Candidates found:                                  │           │      │
│  │  │   • 5 log files with SSL errors                    │           │      │
│  │  │   • 3 test files with "ssl" in name                │           │      │
│  │  │   • 10 doc pages about SSL                         │           │      │
│  │  │         │                                          │           │      │
│  │  │         ▼                                          │           │      │
│  │  │ Rank by relevance → Select top 3                   │           │      │
│  │  │ Retrieve selected evidence                         │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Example implementation:                                          │      │
│  │    def collect_evidence_search(query, failure_time):              │      │
│  │        # Time-bound log search                                    │      │
│  │        log_files = find_logs(                                     │      │
│  │            time_range=(failure_time - 1hr, failure_time),         │      │
│  │            contains=["ERROR", "SSL"]                              │      │
│  │        )                                                          │      │
│  │                                                                   │      │
│  │        # Pattern-based test search                                │      │
│  │        test_files = find_files(                                   │      │
│  │            pattern="**/test_*ssl*.py",                            │      │
│  │            directory="/tests"                                     │      │
│  │        )                                                          │      │
│  │                                                                   │      │
│  │        # Vector search docs                                       │      │
│  │        docs = vector_search(                                      │      │
│  │            query="SSL certificate configuration",                 │      │
│  │            top_k=3                                                │      │
│  │        )                                                          │      │
│  │                                                                   │      │
│  │        return {                                                   │      │
│  │            'logs': [f.read() for f in log_files[:2]],             │      │
│  │            'tests': [f.read() for f in test_files[:1]],           │      │
│  │            'docs': docs                                           │      │
│  │        }                                                          │      │
│  │                                                                   │      │
│  │  ✅ Pros: Finds evidence even when location unknown               │      │
│  │  ❌ Cons: Slower, may miss relevant evidence or include noise     │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              PATTERN 3: GRAPH-BASED RETRIEVAL                     │      │
│  │                                                                   │      │
│  │  Use when: Evidence has relationships (test → fixture → config)   │      │
│  │                                                                   │      │
│  │  Flow:                                                            │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ Start node: test_ssl_connection (failed test)      │           │      │
│  │  │         │                                          │           │      │
│  │  │         ▼                                          │           │      │
│  │  │ Traverse relationships:                            │           │      │
│  │  │                                                    │           │      │
│  │  │   test_ssl_connection                              │           │      │
│  │  │         │                                          │           │      │
│  │  │         ├─ uses fixture → topology                 │           │      │
│  │  │         │   └─ loads file → gpcs_basic.yaml        │           │      │
│  │  │         │       └─ references → device configs     │           │      │
│  │  │         │                                          │           │      │
│  │  │         ├─ logs to → test_run_12345.log            │           │      │
│  │  │         │                                          │           │      │
│  │  │         └─ defined in → test_ssl.py                │           │      │
│  │  │             └─ imports → conftest.py               │           │      │
│  │  │         │                                          │           │      │
│  │  │         ▼                                          │           │      │
│  │  │ Collect all related nodes (BFS traversal)          │           │      │
│  │  │ Filter by relevance + importance                   │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Example implementation:                                          │      │
│  │    def collect_evidence_graph(test_node):                         │      │
│  │        graph = build_dependency_graph()                           │      │
│  │        evidence = {}                                              │      │
│  │                                                                   │      │
│  │        # BFS from failed test                                     │      │
│  │        queue = [(test_node, 0)]  # (node, depth)                  │      │
│  │        visited = set()                                            │      │
│  │                                                                   │      │
│  │        while queue and len(evidence) < max_items:                 │      │
│  │            node, depth = queue.pop(0)                             │      │
│  │            if node in visited or depth > max_depth:               │      │
│  │                continue                                           │      │
│  │                                                                   │      │
│  │            visited.add(node)                                      │      │
│  │            evidence[node.type] = node.content                     │      │
│  │                                                                   │      │
│  │            # Add connected nodes                                  │      │
│  │            for neighbor in graph.neighbors(node):                 │      │
│  │                queue.append((neighbor, depth + 1))                │      │
│  │                                                                   │      │
│  │        return evidence                                            │      │
│  │                                                                   │      │
│  │  ✅ Pros: Comprehensive, finds related evidence automatically      │      │
│  │  ❌ Cons: Requires dependency graph, can retrieve too much        │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Context Ranking Algorithms

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT RANKING ALGORITHMS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Once context retrieved, rank by relevance to decide what to include        │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              ALGORITHM 1: KEYWORD MATCHING                        │      │
│  │                                                                   │      │
│  │  Score based on keyword presence                                  │      │
│  │                                                                   │      │
│  │  def rank_by_keywords(content, failure_keywords):                 │      │
│  │      score = 0                                                    │      │
│  │                                                                   │      │
│  │      # Exact matches (high value)                                 │      │
│  │      for keyword in failure_keywords:                             │      │
│  │          score += content.lower().count(keyword.lower()) * 10     │      │
│  │                                                                   │      │
│  │      # Partial matches (medium value)                             │      │
│  │      for keyword in failure_keywords:                             │      │
│  │          if keyword.lower() in content.lower():                   │      │
│  │              score += 5                                           │      │
│  │                                                                   │      │
│  │      # Severity markers (high value)                              │      │
│  │      score += content.count("ERROR") * 20                         │      │
│  │      score += content.count("FAILED") * 15                        │      │
│  │      score += content.count("EXCEPTION") * 15                     │      │
│  │      score += content.count("WARN") * 5                           │      │
│  │                                                                   │      │
│  │      return score                                                 │      │
│  │                                                                   │      │
│  │  Example:                                                         │      │
│  │  Failure keywords: ["SSL", "certificate", "handshake"]            │      │
│  │                                                                   │      │
│  │  Content A: "ERROR: SSL handshake failed. Certificate mismatch."  │      │
│  │    • "SSL": 1 × 10 = 10                                           │      │
│  │    • "handshake": 1 × 10 = 10                                     │      │
│  │    • "Certificate": 1 × 10 = 10                                   │      │
│  │    • "ERROR": 1 × 20 = 20                                         │      │
│  │    • Total: 50 points                                             │      │
│  │                                                                   │      │
│  │  Content B: "INFO: Test started. Loading topology."               │      │
│  │    • No keywords matched                                          │      │
│  │    • Total: 0 points                                              │      │
│  │                                                                   │      │
│  │  Ranking: A (50) > B (0) → Include A, skip B                      │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              ALGORITHM 2: TF-IDF SCORING                          │      │
│  │                                                                   │      │
│  │  Score based on term frequency - inverse document frequency       │      │
│  │                                                                   │      │
│  │  Concept: Rare terms in query that appear in document = high score│      │
│  │                                                                   │      │
│  │  from sklearn.feature_extraction.text import TfidfVectorizer      │      │
│  │  from sklearn.metrics.pairwise import cosine_similarity           │      │
│  │                                                                   │      │
│  │  def rank_by_tfidf(query, documents):                             │      │
│  │      # Build TF-IDF matrix                                        │      │
│  │      vectorizer = TfidfVectorizer()                               │      │
│  │      all_text = [query] + documents                               │      │
│  │      tfidf_matrix = vectorizer.fit_transform(all_text)            │      │
│  │                                                                   │      │
│  │      # Calculate similarity scores                                │      │
│  │      query_vector = tfidf_matrix[0]                               │      │
│  │      doc_vectors = tfidf_matrix[1:]                               │      │
│  │      scores = cosine_similarity(query_vector, doc_vectors)[0]     │      │
│  │                                                                   │      │
│  │      # Rank documents by score                                    │      │
│  │      ranked = sorted(                                             │      │
│  │          zip(documents, scores),                                  │      │
│  │          key=lambda x: x[1],                                      │      │
│  │          reverse=True                                             │      │
│  │      )                                                            │      │
│  │      return ranked                                                │      │
│  │                                                                   │      │
│  │  Example:                                                         │      │
│  │  Query: "SSL certificate handshake failure"                       │      │
│  │                                                                   │      │
│  │  Document A: "ERROR SSL handshake failed cert mismatch"           │      │
│  │    Similarity: 0.85 (high - many matching terms)                  │      │
│  │                                                                   │      │
│  │  Document B: "Connection established successfully"                │      │
│  │    Similarity: 0.12 (low - few matching terms)                    │      │
│  │                                                                   │      │
│  │  Ranking: A (0.85) > B (0.12)                                     │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              ALGORITHM 3: SEMANTIC SIMILARITY                     │      │
│  │                                                                   │      │
│  │  Score based on meaning, not just keywords                        │      │
│  │                                                                   │      │
│  │  from sentence_transformers import SentenceTransformer            │      │
│  │  import numpy as np                                               │      │
│  │                                                                   │      │
│  │  def rank_by_semantic_similarity(query, documents):               │      │
│  │      # Load embedding model                                       │      │
│  │      model = SentenceTransformer('all-MiniLM-L6-v2')              │      │
│  │                                                                   │      │
│  │      # Encode query and documents                                 │      │
│  │      query_embedding = model.encode(query)                        │      │
│  │      doc_embeddings = model.encode(documents)                     │      │
│  │                                                                   │      │
│  │      # Calculate cosine similarity                                │      │
│  │      scores = np.dot(doc_embeddings, query_embedding) /           │      │
│  │               (np.linalg.norm(doc_embeddings, axis=1) *           │      │
│  │                np.linalg.norm(query_embedding))                   │      │
│  │                                                                   │      │
│  │      # Rank by similarity                                         │      │
│  │      ranked_indices = np.argsort(scores)[::-1]                    │      │
│  │      return [(documents[i], scores[i])                            │      │
│  │              for i in ranked_indices]                             │      │
│  │                                                                   │      │
│  │  Example:                                                         │      │
│  │  Query: "authentication failed"                                   │      │
│  │                                                                   │      │
│  │  Document A: "login rejected due to wrong password"               │      │
│  │    Similarity: 0.78 (semantically similar, different words)       │      │
│  │                                                                   │      │
│  │  Document B: "data successfully transmitted"                      │      │
│  │    Similarity: 0.15 (semantically different)                      │      │
│  │                                                                   │      │
│  │  Benefit: Catches "login rejected" even though query said          │      │
│  │           "authentication failed" (synonymous)                    │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              ALGORITHM 4: HYBRID RANKING                          │      │
│  │                                                                   │      │
│  │  Combine multiple signals for best results                        │      │
│  │                                                                   │      │
│  │  def rank_hybrid(query, documents, metadata):                     │      │
│  │      scores = []                                                  │      │
│  │                                                                   │      │
│  │      for doc, meta in zip(documents, metadata):                   │      │
│  │          # Component scores                                       │      │
│  │          keyword_score = rank_by_keywords(doc, query)             │      │
│  │          tfidf_score = calculate_tfidf(query, doc)                │      │
│  │          semantic_score = calculate_semantic(query, doc)          │      │
│  │                                                                   │      │
│  │          # Metadata signals                                       │      │
│  │          recency_score = 1.0 / (1 + meta.age_hours)               │      │
│  │          severity_score = meta.error_count * 5                    │      │
│  │                                                                   │      │
│  │          # Weighted combination                                   │      │
│  │          total_score = (                                          │      │
│  │              0.3 * keyword_score +                                │      │
│  │              0.2 * tfidf_score +                                  │      │
│  │              0.3 * semantic_score +                               │      │
│  │              0.1 * recency_score +                                │      │
│  │              0.1 * severity_score                                 │      │
│  │          )                                                        │      │
│  │          scores.append((doc, total_score))                        │      │
│  │                                                                   │      │
│  │      return sorted(scores, key=lambda x: x[1], reverse=True)      │      │
│  │                                                                   │      │
│  │  Weights can be tuned based on domain:                            │      │
│  │  • Debugging: Higher weight on severity_score                     │      │
│  │  • Documentation: Higher weight on semantic_score                 │      │
│  │  • Real-time monitoring: Higher weight on recency_score           │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Context Compression Techniques

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT COMPRESSION TECHNIQUES                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              TECHNIQUE 1: DEDUPLICATION                           │      │
│  │                                                                   │      │
│  │  Remove duplicate information                                     │      │
│  │                                                                   │      │
│  │  def deduplicate_context(evidence_items):                         │      │
│  │      seen_hashes = set()                                          │      │
│  │      unique_items = []                                            │      │
│  │                                                                   │      │
│  │      for item in evidence_items:                                  │      │
│  │          # Hash content for exact match detection                 │      │
│  │          content_hash = hashlib.md5(                              │      │
│  │              item.content.encode()                                │      │
│  │          ).hexdigest()                                            │      │
│  │                                                                   │      │
│  │          if content_hash not in seen_hashes:                      │      │
│  │              seen_hashes.add(content_hash)                        │      │
│  │              unique_items.append(item)                            │      │
│  │                                                                   │      │
│  │      return unique_items                                          │      │
│  │                                                                   │      │
│  │  Example scenario:                                                │      │
│  │  • Same error appears in 3 different log files                    │      │
│  │  • All 3 retrieved by search                                      │      │
│  │  • Deduplication: Keep first occurrence, discard duplicates       │      │
│  │  • Reduction: 3 × 100 lines → 1 × 100 lines (66% savings)         │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              TECHNIQUE 2: WHITESPACE NORMALIZATION                │      │
│  │                                                                   │      │
│  │  Remove unnecessary whitespace                                    │      │
│  │                                                                   │      │
│  │  def normalize_whitespace(content):                               │      │
│  │      # Remove trailing whitespace from each line                  │      │
│  │      lines = [line.rstrip() for line in content.split('\n')]      │      │
│  │                                                                   │      │
│  │      # Remove empty lines (optional, context-dependent)           │      │
│  │      lines = [line for line in lines if line.strip()]             │      │
│  │                                                                   │      │
│  │      # Collapse multiple spaces to single space                   │      │
│  │      lines = [re.sub(r' +', ' ', line) for line in lines]         │      │
│  │                                                                   │      │
│  │      return '\n'.join(lines)                                      │      │
│  │                                                                   │      │
│  │  Example:                                                         │      │
│  │  Before (25 tokens):                                              │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ ERROR:  SSL    handshake   failed                  │           │      │
│  │  │                                                    │           │      │
│  │  │                                                    │           │      │
│  │  │ Expected:    *.prisma.local                        │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  After (18 tokens):                                               │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ ERROR: SSL handshake failed                        │           │      │
│  │  │ Expected: *.prisma.local                           │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Reduction: 28% (25 → 18 tokens)                                  │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              TECHNIQUE 3: VARIABLE NAME SHORTENING                │      │
│  │                                                                   │      │
│  │  Shorten verbose variable names (careful - may reduce clarity!)   │      │
│  │                                                                   │      │
│  │  Before (30 tokens):                                              │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ expected_certificate_common_name = "*.prisma.local"│           │      │
│  │  │ received_certificate_common_name = "localhost"     │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  After (18 tokens):                                               │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ expected_cn = "*.prisma.local"                     │           │      │
│  │  │ received_cn = "localhost"                          │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  ⚠️ Trade-off: Saves tokens but may hurt comprehension            │      │
│  │  Use only when: Token budget is tight AND LLM can infer meaning   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              TECHNIQUE 4: COMMENT REMOVAL                         │      │
│  │                                                                   │      │
│  │  Remove code comments from test files                             │      │
│  │                                                                   │      │
│  │  def remove_comments(code):                                       │      │
│  │      # Remove single-line comments                                │      │
│  │      code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)         │      │
│  │                                                                   │      │
│  │      # Remove docstrings (triple-quoted strings)                  │      │
│  │      code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)       │      │
│  │      code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)       │      │
│  │                                                                   │      │
│  │      return code                                                  │      │
│  │                                                                   │      │
│  │  Before (50 tokens):                                              │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ def test_ssl_connection(topology):                 │           │      │
│  │  │     """Verify SSL connection to gateway.          │           │      │
│  │  │                                                    │           │      │
│  │  │     This test ensures that the gateway accepts     │           │      │
│  │  │     SSL connections with valid certificates.       │           │      │
│  │  │     """                                            │           │      │
│  │  │     # Get gateway from topology                    │           │      │
│  │  │     gateway = topology.devices['gateway']          │           │      │
│  │  │     client.connect(gateway.ip, verify_ssl=True)    │           │      │
│  │  │     assert client.is_connected                     │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  After (15 tokens):                                               │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ def test_ssl_connection(topology):                 │           │      │
│  │  │     gateway = topology.devices['gateway']          │           │      │
│  │  │     client.connect(gateway.ip, verify_ssl=True)    │           │      │
│  │  │     assert client.is_connected                     │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  ⚠️ Trade-off: Comments may provide valuable context for LLM      │      │
│  │  Use when: Code is self-explanatory                              │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              TECHNIQUE 5: SELECTIVE ABBREVIATION                  │      │
│  │                                                                   │      │
│  │  Abbreviate common patterns while preserving key info             │      │
│  │                                                                   │      │
│  │  abbreviations = {                                                │      │
│  │      r'\[INFO\].*': '[INFO]',     # Collapse INFO lines           │      │
│  │      r'\[DEBUG\].*': '[DEBUG]',   # Collapse DEBUG lines          │      │
│  │      r'Traceback \(most recent call last\):': '[TRACEBACK]',     │      │
│  │      r'^\s+at .*': '  [FRAME]',   # Stack frames                  │      │
│  │  }                                                                │      │
│  │                                                                   │      │
│  │  Before (100 tokens):                                             │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ [INFO] 2026-08-20 10:27:45 Test started            │           │      │
│  │  │ [INFO] 2026-08-20 10:27:46 Loading config          │           │      │
│  │  │ [DEBUG] 2026-08-20 10:27:47 Opening connection     │           │      │
│  │  │ [DEBUG] 2026-08-20 10:27:48 Sending packet         │           │      │
│  │  │ [ERROR] 2026-08-20 10:28:12 SSL handshake failed   │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  After (25 tokens):                                               │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ [INFO] (collapsed 2 lines)                         │           │      │
│  │  │ [DEBUG] (collapsed 2 lines)                        │           │      │
│  │  │ [ERROR] 2026-08-20 10:28:12 SSL handshake failed   │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  │  Reduction: 75% (100 → 25 tokens)                                 │      │
│  │  Preserves: Error details intact                                  │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              COMPRESSION PIPELINE                                 │      │
│  │                                                                   │      │
│  │  Combine techniques for maximum reduction:                        │      │
│  │                                                                   │      │
│  │  def compress_context(evidence):                                  │      │
│  │      # Step 1: Remove duplicates                                  │      │
│  │      evidence = deduplicate_context(evidence)                     │      │
│  │                                                                   │      │
│  │      # Step 2: Normalize whitespace                               │      │
│  │      for item in evidence:                                        │      │
│  │          item.content = normalize_whitespace(item.content)        │      │
│  │                                                                   │      │
│  │      # Step 3: For code, remove comments                          │      │
│  │      for item in evidence:                                        │      │
│  │          if item.type == 'code':                                  │      │
│  │              item.content = remove_comments(item.content)         │      │
│  │                                                                   │      │
│  │      # Step 4: For logs, abbreviate non-critical lines            │      │
│  │      for item in evidence:                                        │      │
│  │          if item.type == 'log':                                   │      │
│  │              item.content = abbreviate_logs(item.content)         │      │
│  │                                                                   │      │
│  │      # Step 5: Validate token count                               │      │
│  │      total_tokens = sum(count_tokens(item.content)                │      │
│  │                         for item in evidence)                     │      │
│  │                                                                   │      │
│  │      if total_tokens > max_tokens:                                │      │
│  │          # Further reduction needed: apply smart truncation       │      │
│  │          evidence = truncate_to_budget(evidence, max_tokens)      │      │
│  │                                                                   │      │
│  │      return evidence                                              │      │
│  │                                                                   │      │
│  │  Typical reduction: 130K tokens → 2K tokens (98.5%)               │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Production Considerations

### 8.1 Performance Metrics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KEY PERFORMANCE METRICS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Track these metrics to measure context engineering effectiveness           │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ 1. TOKEN METRICS                                                  │      │
│  │                                                                   │      │
│  │ • Input tokens per request                                        │      │
│  │   - Target: < 3,000 tokens                                        │      │
│  │   - Alert if: > 10,000 tokens                                     │      │
│  │   - Track: min, max, p50, p95, p99                                │      │
│  │                                                                   │      │
│  │ • Token reduction ratio                                           │      │
│  │   - Ratio = (original_tokens - optimized_tokens) / original_tokens│      │
│  │   - Target: > 95%                                                 │      │
│  │   - Example: (130K - 2.5K) / 130K = 98.1%                         │      │
│  │                                                                   │      │
│  │ • Relevance ratio                                                 │      │
│  │   - Ratio = useful_tokens / total_tokens                          │      │
│  │   - Target: > 80%                                                 │      │
│  │   - Measure by: LLM references in response                        │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ 2. COST METRICS                                                   │      │
│  │                                                                   │      │
│  │ • Cost per diagnosis                                              │      │
│  │   - Target: < $0.05                                               │      │
│  │   - Track trend over time                                         │      │
│  │                                                                   │      │
│  │ • Daily API spend                                                 │      │
│  │   - Set budget alerts                                             │      │
│  │   - Monitor against quota                                         │      │
│  │                                                                   │      │
│  │ • ROI                                                             │      │
│  │   - Savings vs baseline                                           │      │
│  │   - Cost per diagnosis before vs after                            │      │
│  │                                                                   │      │
│  │ • Cache hit rate                                                  │      │
│  │   - cache_read_tokens / total_input_tokens                        │      │
│  │   - Target: > 70% (for batch processing)                          │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ 3. QUALITY METRICS                                                │      │
│  │                                                                   │      │
│  │ • Diagnostic accuracy                                             │      │
│  │   - % of correct root causes identified                           │      │
│  │   - Target: > 90%                                                 │      │
│  │   - Validate with human review                                    │      │
│  │                                                                   │      │
│  │ • Fix success rate                                                │      │
│  │   - % of suggested fixes that work                                │      │
│  │   - Target: > 80%                                                 │      │
│  │   - Track in follow-up tests                                      │      │
│  │                                                                   │      │
│  │ • Confidence scores                                               │      │
│  │   - LLM self-reported confidence (if provided)                    │      │
│  │   - Correlate with actual accuracy                                │      │
│  │                                                                   │      │
│  │ • False positive rate                                             │      │
│  │   - % of diagnoses that are incorrect                             │      │
│  │   - Target: < 5%                                                  │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ 4. LATENCY METRICS                                                │      │
│  │                                                                   │      │
│  │ • Evidence collection time                                        │      │
│  │   - Time to gather all evidence                                   │      │
│  │   - Target: < 2 seconds                                           │      │
│  │                                                                   │      │
│  │ • Context optimization time                                       │      │
│  │   - Time to filter + structure                                    │      │
│  │   - Target: < 1 second                                            │      │
│  │                                                                   │      │
│  │ • API response time                                               │      │
│  │   - Time from request to response                                 │      │
│  │   - Target: < 10 seconds (p95)                                    │      │
│  │                                                                   │      │
│  │ • End-to-end latency                                              │      │
│  │   - Total time: failure event → diagnosis                         │      │
│  │   - Target: < 15 seconds (real-time)                              │      │
│  │   - Target: < 5 minutes (batch)                                   │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              METRICS DASHBOARD EXAMPLE                            │      │
│  │                                                                   │      │
│  │  ┌────────────────────────────────────────────────────┐           │      │
│  │  │ ATIYA CONTEXT ENGINEERING METRICS (24h)            │           │      │
│  │  │                                                    │           │      │
│  │  │ Diagnoses: 487                                     │           │      │
│  │  │ Success rate: 94.2% ✅                             │           │      │
│  │  │                                                    │           │      │
│  │  │ Token Efficiency:                                  │           │      │
│  │  │   Avg input: 2,345 tokens ✅                       │           │      │
│  │  │   Reduction: 98.2% (from 130K baseline)            │           │      │
│  │  │   Relevance: 87% ✅                                │           │      │
│  │  │                                                    │           │      │
│  │  │ Cost:                                              │           │      │
│  │  │   Per diagnosis: $0.023 ✅                         │           │      │
│  │  │   Daily total: $11.20 (under $15 budget) ✅        │           │      │
│  │  │   Cache hit rate: 73% ✅                           │           │      │
│  │  │                                                    │           │      │
│  │  │ Latency:                                           │           │      │
│  │  │   p50: 5.2s ✅                                     │           │      │
│  │  │   p95: 9.8s ✅                                     │           │      │
│  │  │   p99: 14.5s ⚠️ (target: <12s)                    │           │      │
│  │  │                                                    │           │      │
│  │  │ Quality:                                           │           │      │
│  │  │   Accuracy: 94.2% ✅                               │           │      │
│  │  │   Fix success: 87% ✅                              │           │      │
│  │  │   False positives: 2.1% ✅                         │           │      │
│  │  └────────────────────────────────────────────────────┘           │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Cost Analysis with ROI

(Already covered in section 6.6 - see "ROI: Cost Reduction Summary")

### 8.3 Monitoring Dashboards

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MONITORING AND ALERTING                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Production context engineering requires continuous monitoring              │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              MONITORING STACK                                     │      │
│  │                                                                   │      │
│  │  1. METRICS COLLECTION                                            │      │
│  │     • Prometheus: Time-series metrics                             │      │
│  │     • StatsD: Real-time counters                                  │      │
│  │     • Custom logging: Structured JSON logs                        │      │
│  │                                                                   │      │
│  │  2. VISUALIZATION                                                 │      │
│  │     • Grafana: Real-time dashboards                               │      │
│  │     • Kibana: Log analysis                                        │      │
│  │     • Custom reports: Weekly/monthly summaries                    │      │
│  │                                                                   │      │
│  │  3. ALERTING                                                      │      │
│  │     • PagerDuty: Critical alerts                                  │      │
│  │     • Slack: Warning notifications                                │      │
│  │     • Email: Daily summaries                                      │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              ALERT RULES                                          │      │
│  │                                                                   │      │
│  │  CRITICAL (PagerDuty):                                            │      │
│  │  • Accuracy < 80% for > 1 hour                                    │      │
│  │  • API errors > 5% of requests                                    │      │
│  │  • Daily spend > 2× budget                                        │      │
│  │                                                                   │      │
│  │  WARNING (Slack):                                                 │      │
│  │  • Avg tokens > 5,000 per request                                 │      │
│  │  • p95 latency > 15 seconds                                       │      │
│  │  • Cache hit rate < 50%                                           │      │
│  │  • Accuracy < 90% for > 30 minutes                                │      │
│  │                                                                   │      │
│  │  INFO (Email daily):                                              │      │
│  │  • Daily cost summary                                             │      │
│  │  • Performance trends                                             │      │
│  │  • Top failure categories                                         │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              INSTRUMENTATION CODE                                 │      │
│  │                                                                   │      │
│  │  from prometheus_client import Counter, Histogram, Gauge          │      │
│  │                                                                   │      │
│  │  # Metrics                                                        │      │
│  │  diagnoses_total = Counter(                                       │      │
│  │      'atiya_diagnoses_total',                                     │      │
│  │      'Total number of diagnoses performed'                        │      │
│  │  )                                                                │      │
│  │                                                                   │      │
│  │  diagnosis_accuracy = Gauge(                                      │      │
│  │      'atiya_diagnosis_accuracy',                                  │      │
│  │      'Accuracy of diagnoses (0-1)'                                │      │
│  │  )                                                                │      │
│  │                                                                   │      │
│  │  tokens_used = Histogram(                                         │      │
│  │      'atiya_tokens_used',                                         │      │
│  │      'Input tokens per diagnosis',                                │      │
│  │      buckets=[500, 1000, 2000, 5000, 10000, 50000]                │      │
│  │  )                                                                │      │
│  │                                                                   │      │
│  │  api_cost_dollars = Counter(                                      │      │
│  │      'atiya_api_cost_dollars',                                    │      │
│  │      'Total API cost in dollars'                                  │      │
│  │  )                                                                │      │
│  │                                                                   │      │
│  │  # Instrument diagnosis function                                  │      │
│  │  def diagnose_failure(test_failure):                              │      │
│  │      diagnoses_total.inc()                                        │      │
│  │                                                                   │      │
│  │      # Collect evidence                                           │      │
│  │      evidence = collect_evidence(test_failure)                    │      │
│  │      original_tokens = count_tokens(evidence)                     │      │
│  │                                                                   │      │
│  │      # Optimize context                                           │      │
│  │      optimized = optimize_context(evidence)                       │      │
│  │      final_tokens = count_tokens(optimized)                       │      │
│  │      tokens_used.observe(final_tokens)                            │      │
│  │                                                                   │      │
│  │      # Call LLM                                                   │      │
│  │      response = claude_client.diagnose(optimized)                 │      │
│  │      cost = calculate_cost(response.usage)                        │      │
│  │      api_cost_dollars.inc(cost)                                   │      │
│  │                                                                   │      │
│  │      # Track accuracy (if ground truth available)                 │      │
│  │      if test_failure.known_root_cause:                            │      │
│  │          correct = validate_diagnosis(                            │      │
│  │              response.diagnosis,                                  │      │
│  │              test_failure.known_root_cause                        │      │
│  │          )                                                        │      │
│  │          diagnosis_accuracy.set(1.0 if correct else 0.0)          │      │
│  │                                                                   │      │
│  │      return response.diagnosis                                    │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Atiya Lens

### 9.1 Atiya's Context Engineering Implementation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                ATIYA CONTEXT ENGINEERING ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Atiya implements all context engineering patterns covered in this doc      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              ATIYA PIPELINE                                       │      │
│  │                                                                   │      │
│  │  Test Failure Event (from ReportPortal)                           │      │
│  │         │                                                         │      │
│  │         ▼                                                         │      │
│  │  ┌──────────────────────────────────────────────────┐             │      │
│  │  │ 1. EVIDENCE COLLECTION                           │             │      │
│  │  │    (evidence_collector.py)                       │             │      │
│  │  │                                                  │             │      │
│  │  │ • Fetch pytest log from ReportPortal API         │             │      │
│  │  │ • Parse test path from metadata                  │             │      │
│  │  │ • Load test source code                          │             │      │
│  │  │ • Load topology YAML (if referenced)             │             │      │
│  │  │ • Load device config (if config failure)         │             │      │
│  │  │                                                  │             │      │
│  │  │ Output: RawEvidence (130K tokens average)        │             │      │
│  │  └──────────────────┬───────────────────────────────┘             │      │
│  │                     │                                             │      │
│  │                     ▼                                             │      │
│  │  ┌──────────────────────────────────────────────────┐             │      │
│  │  │ 2. CONTEXT SELECTION                             │             │      │
│  │  │    (context_selector.py)                         │             │      │
│  │  │                                                  │             │      │
│  │  │ • Extract ERROR/FAILED lines from log            │             │      │
│  │  │ • Extract WARNs within ±10 lines of errors       │             │      │
│  │  │ • Extract failed test function only              │             │      │
│  │  │ • Extract fixtures used by test                  │             │      │
│  │  │ • Skip DEBUG/INFO logs                           │             │      │
│  │  │ • Skip passing test output                       │             │      │
│  │  │                                                  │             │      │
│  │  │ Reduction: 130K → 2K tokens (98.5%)              │             │      │
│  │  └──────────────────┬───────────────────────────────┘             │      │
│  │                     │                                             │      │
│  │                     ▼                                             │      │
│  │  ┌──────────────────────────────────────────────────┐             │      │
│  │  │ 3. CONTEXT OPTIMIZATION                          │             │      │
│  │  │    (context_optimizer.py)                        │             │      │
│  │  │                                                  │             │      │
│  │  │ • Add metadata:                                  │             │      │
│  │  │   - Line numbers: [pytest.log:4521]              │             │      │
│  │  │   - Timestamps: 2026-08-20 10:28:12              │             │      │
│  │  │   - Source tags: [Test Code] [Topology]          │             │      │
│  │  │                                                  │             │      │
│  │  │ • Structure hierarchically:                      │             │      │
│  │  │   === FAILURE SUMMARY ===                        │             │      │
│  │  │   === ERROR DETAILS ===                          │             │      │
│  │  │   === TEST CODE ===                              │             │      │
│  │  │   === CONFIGURATION ===                          │             │      │
│  │  │                                                  │             │      │
│  │  │ • Validate token count < 3000                    │             │      │
│  │  │                                                  │             │      │
│  │  │ Output: 2.3K tokens (with metadata)              │             │      │
│  │  └──────────────────┬───────────────────────────────┘             │      │
│  │                     │                                             │      │
│  │                     ▼                                             │      │
│  │  ┌──────────────────────────────────────────────────┐             │      │
│  │  │ 4. CONTEXT DELIVERY                              │             │      │
│  │  │    (claude_client.py)                            │             │      │
│  │  │                                                  │             │      │
│  │  │ • Select model: Sonnet 4.6 (balanced)            │             │      │
│  │  │ • System prompt: "PARTS test expert..."          │             │      │
│  │  │ • Cache static context (test code + topology)    │             │      │
│  │  │ • Send fresh log excerpt                         │             │      │
│  │  │                                                  │             │      │
│  │  │ • Call Claude API                                │             │      │
│  │  │ • Track usage metrics                            │             │      │
│  │  │                                                  │             │      │
│  │  │ Cost: $0.023 per diagnosis (with caching)        │             │      │
│  │  └──────────────────┬───────────────────────────────┘             │      │
│  │                     │                                             │      │
│  │                     ▼                                             │      │
│  │              Diagnosis with root cause + fix                      │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Evidence Collection Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                ATIYA EVIDENCE COLLECTION DETAIL                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  evidence_collector.py implementation                                       │
│                                                                             │
│  class EvidenceCollector:                                                   │
│      def __init__(self, report_portal_client):                              │
│          self.rp = report_portal_client                                     │
│                                                                             │
│      def collect(self, test_failure_event):                                 │
│          """Gather all evidence for failed test"""                          │
│          evidence = Evidence()                                              │
│                                                                             │
│          # 1. Get test log from ReportPortal                                │
│          launch_id = test_failure_event.launch_id                           │
│          item_id = test_failure_event.item_id                               │
│          logs = self.rp.get_item_logs(launch_id, item_id)                   │
│                                                                             │
│          evidence.log_content = '\n'.join([                                 │
│              log['message'] for log in logs                                 │
│          ])                                                                 │
│          evidence.log_size = len(evidence.log_content.split('\n'))          │
│                                                                             │
│          # 2. Parse test file path from metadata                            │
│          test_path = test_failure_event.metadata.get('test_file')           │
│          if test_path:                                                      │
│              evidence.test_code = Path(test_path).read_text()               │
│              evidence.test_path = test_path                                 │
│                                                                             │
│          # 3. Find and load topology YAML                                   │
│          topology_ref = self.extract_topology_reference(                    │
│              evidence.test_code                                             │
│          )                                                                  │
│          if topology_ref:                                                   │
│              topology_path = self.resolve_topology_path(topology_ref)       │
│              evidence.topology = Path(topology_path).read_text()            │
│              evidence.topology_path = topology_path                         │
│                                                                             │
│          # 4. Check if device config needed                                 │
│          if self.is_config_related_failure(evidence.log_content):           │
│              device_ip = self.extract_device_ip(evidence.log_content)       │
│              evidence.device_config = self.fetch_device_config(device_ip)   │
│                                                                             │
│          # 5. Metadata                                                      │
│          evidence.failure_time = test_failure_event.timestamp               │
│          evidence.test_name = test_failure_event.name                       │
│          evidence.total_tokens = self.estimate_tokens(evidence)             │
│                                                                             │
│          return evidence                                                    │
│                                                                             │
│      def extract_topology_reference(self, test_code):                       │
│          """Find topology YAML reference in test code"""                    │
│          # Look for build_topology("xxx.yaml") calls                        │
│          match = re.search(                                                 │
│              r'build_topology\(["\'](.+?\.yaml)["\']\)',                    │
│              test_code                                                      │
│          )                                                                  │
│          return match.group(1) if match else None                           │
│                                                                             │
│      def is_config_related_failure(self, log):                              │
│          """Check if failure is configuration-related"""                    │
│          config_keywords = [                                                │
│              "config", "certificate", "ssl", "cert",                        │
│              "topology", "yaml", "parameter"                                │
│          ]                                                                  │
│          return any(kw in log.lower() for kw in config_keywords)            │
│                                                                             │
│  Evidence collection takes ~2 seconds on average                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.3 Results and Metrics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                ATIYA PRODUCTION METRICS (30-DAY AVERAGE)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Deployment: GPCS test automation (Palo Alto Networks)                      │
│  Period: 30 days (2026-07-20 to 2026-08-20)                                 │
│  Total diagnoses: 14,327                                                    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              TOKEN EFFICIENCY                                     │      │
│  │                                                                   │      │
│  │  Original context (without optimization):                         │      │
│  │  • Average: 128,500 tokens per diagnosis                          │      │
│  │  • p50: 95,000 tokens                                             │      │
│  │  • p95: 245,000 tokens                                            │      │
│  │  • Would exceed context window: 8.2% of diagnoses                 │      │
│  │                                                                   │      │
│  │  Optimized context (with Atiya):                                  │      │
│  │  • Average: 2,340 tokens per diagnosis ✅                         │      │
│  │  • p50: 2,100 tokens                                              │      │
│  │  • p95: 3,800 tokens                                              │      │
│  │  • Exceeded budget (>5K): 0.3% of diagnoses                       │      │
│  │                                                                   │      │
│  │  Reduction: 98.2% average (128.5K → 2.3K)                         │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              COST IMPACT                                          │      │
│  │                                                                   │      │
│  │  Without Atiya (estimated):                                       │      │
│  │  • Per diagnosis: $0.387                                          │      │
│  │  • 30 days: 14,327 × $0.387 = $5,545                              │      │
│  │  • Annual projection: $67,700                                     │      │
│  │                                                                   │      │
│  │  With Atiya (actual):                                             │      │
│  │  • Per diagnosis: $0.021 (cache hit), $0.034 (cache miss)         │      │
│  │  • Cache hit rate: 71%                                            │      │
│  │  • Weighted average: $0.025 per diagnosis                         │      │
│  │  • 30 days: 14,327 × $0.025 = $358 ✅                             │      │
│  │  • Annual projection: $4,370                                      │      │
│  │                                                                   │      │
│  │  Savings: $5,187 per month ($63,330 annualized)                   │      │
│  │  Reduction: 93.5%                                                 │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              DIAGNOSTIC QUALITY                                   │      │
│  │                                                                   │      │
│  │  Accuracy (validated on 500 test sample):                         │      │
│  │  • Correct root cause identified: 94.6% ✅                        │      │
│  │  • Partially correct: 3.2%                                        │      │
│  │  • Incorrect: 2.2%                                                │      │
│  │                                                                   │      │
│  │  Fix success rate (100 fixes applied):                            │      │
│  │  • Fix resolved issue: 89% ✅                                     │      │
│  │  • Fix partially resolved: 7%                                     │      │
│  │  • Fix did not help: 4%                                           │      │
│  │                                                                   │      │
│  │  Comparison to baseline (no optimization):                        │      │
│  │  • Baseline accuracy: 91.2%                                       │      │
│  │  • Atiya accuracy: 94.6%                                          │      │
│  │  • Improvement: +3.4 percentage points                            │      │
│  │                                                                   │      │
│  │  ✅ Context engineering IMPROVED accuracy                         │      │
│  │     (Better signal-to-noise ratio)                                │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              PERFORMANCE                                          │      │
│  │                                                                   │      │
│  │  Latency breakdown:                                               │      │
│  │  • Evidence collection: 1.8s avg                                  │      │
│  │  • Context optimization: 0.4s avg                                 │      │
│  │  • Claude API call: 4.2s avg                                      │      │
│  │  • Total (p50): 6.3s ✅                                           │      │
│  │  • Total (p95): 11.2s ✅                                          │      │
│  │  • Total (p99): 18.4s (under 20s target)                          │      │
│  │                                                                   │      │
│  │  Throughput:                                                      │      │
│  │  • Real-time mode: 15-20 diagnoses/minute                         │      │
│  │  • Batch mode: 500+ diagnoses/hour                                │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              IMPACT ON QA TEAM                                    │      │
│  │                                                                   │      │
│  │  Before Atiya:                                                    │      │
│  │  • Manual triage time: 20-30 min per failure                      │      │
│  │  • Daily capacity: 15-20 failures per engineer                    │      │
│  │  • Overnight failures (avg 127): 8+ hours to triage               │      │
│  │                                                                   │      │
│  │  After Atiya:                                                     │      │
│  │  • Automated diagnosis: <15 seconds                               │      │
│  │  • Engineer review time: 2-3 min (validate + apply fix)           │      │
│  │  • Daily capacity: 100+ failures per engineer                     │      │
│  │  • Overnight failures: 1 hour to review all diagnoses             │      │
│  │                                                                   │      │
│  │  Time savings: 87% reduction in triage time                       │      │
│  │  Engineer hours saved: ~6 hours/day per engineer                  │      │
│  │                                                                   │      │
│  │  Productivity gain: 5× increase in throughput                     │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              KEY LEARNINGS                                        │      │
│  │                                                                   │      │
│  │  1. Extraction > Truncation                                       │      │
│  │     • ERROR-focused extraction worked better than smart truncation│      │
│  │     • Relevance ratio improved from 65% → 87%                     │      │
│  │                                                                   │      │
│  │  2. Metadata enrichment critical                                  │      │
│  │     • Adding line numbers improved fix accuracy by 8%             │      │
│  │     • Source tags helped LLM navigate context                     │      │
│  │                                                                   │      │
│  │  3. Caching provides massive savings                              │      │
│  │     • 71% cache hit rate = 3.4× cost reduction                    │      │
│  │     • Batch processing within 5-min windows maximizes hits        │      │
│  │                                                                   │      │
│  │  4. Quality improved with less context                            │      │
│  │     • Counterintuitive: More context hurt accuracy                │      │
│  │     • Root cause: "Lost in the middle" effect                     │      │
│  │     • Lesson: Relevance > Volume                                  │      │
│  │                                                                   │      │
│  │  5. Monitoring essential                                          │      │
│  │     • Caught 3 regressions via metrics alerts                     │      │
│  │     • Accuracy trend analysis identified prompt improvements      │      │
│  │     • Cost tracking prevented budget overruns                     │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT ENGINEERING SUMMARY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WHAT IS CONTEXT ENGINEERING?                                               │
│  The practice of intelligently selecting, structuring, and delivering       │
│  relevant information to LLMs for optimal performance at minimal cost.      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              THE 4 PILLARS                                        │      │
│  │                                                                   │      │
│  │  1. GATHERING    - Identify all potentially relevant sources      │      │
│  │  2. FILTERING    - Select only necessary information              │      │
│  │  3. STRUCTURING  - Organize for optimal comprehension             │      │
│  │  4. DELIVERING   - Present to maximize LLM performance            │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              KEY PRINCIPLES                                       │      │
│  │                                                                   │      │
│  │  • Relevance First: Include only task-relevant information        │      │
│  │  • Signal-to-Noise: Maximize information density                  │      │
│  │  • Cost-Performance: Find minimum sufficient context              │      │
│  │  • Structure Matters: Organize hierarchically                     │      │
│  │  • Metadata Enriches: Add context about context                   │      │
│  │  • Progressive Disclosure: Start minimal, add if needed           │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              STRATEGIES TO SHRINK CONTEXT                         │      │
│  │                                                                   │      │
│  │  1. Smart Truncation                                              │      │
│  │     • Keep first N + last M lines                                 │      │
│  │     • Show skip indicators                                        │      │
│  │     • Adaptive to content                                         │      │
│  │                                                                   │      │
│  │  2. Extraction                                                    │      │
│  │     • Extract ERROR/WARN lines only                               │      │
│  │     • Relevance scoring                                           │      │
│  │     • Pattern-based extraction                                    │      │
│  │                                                                   │      │
│  │  3. Summarization                                                 │      │
│  │     • Two-stage processing                                        │      │
│  │     • Hierarchical summaries                                      │      │
│  │     • Amortize cost across multiple uses                          │      │
│  │                                                                   │      │
│  │  4. Caching                                                       │      │
│  │     • Cache static context (5 min TTL)                            │      │
│  │     • 90% cost reduction on cached tokens                         │      │
│  │     • Batch requests to maximize hit rate                         │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              EXPECTED RESULTS                                     │      │
│  │                                                                   │      │
│  │  Typical reduction: 130,000 tokens → 2,500 tokens (98%)           │      │
│  │  Cost savings: $0.39 → $0.02 per request (95%)                    │      │
│  │  Speed improvement: 45s → 6s (87%)                                │      │
│  │  Quality: Often IMPROVES (better signal-to-noise)                 │      │
│  │                                                                   │      │
│  │  ROI: 460% in first year (typical)                                │      │
│  │  Payback period: 2-3 months                                       │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              WHEN TO USE                                          │      │
│  │                                                                   │      │
│  │  MANDATORY:                                                       │      │
│  │  • Production LLM applications at scale (>100 requests/day)       │      │
│  │  • Large documents (>10K tokens)                                  │      │
│  │  • Cost-sensitive applications                                    │      │
│  │  • RAG systems                                                    │      │
│  │                                                                   │      │
│  │  OPTIONAL:                                                        │      │
│  │  • One-off queries                                                │      │
│  │  • Already small context (<2K tokens)                             │      │
│  │  • Prototyping/experimentation                                    │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              IMPLEMENTATION CHECKLIST                             │      │
│  │                                                                   │      │
│  │  ☐ 1. Baseline metrics (cost, latency, quality)                  │      │
│  │  ☐ 2. Implement extraction logic                                 │      │
│  │  ☐ 3. Add metadata enrichment                                    │      │
│  │  ☐ 4. Structure context hierarchically                            │      │
│  │  ☐ 5. Implement prompt caching                                   │      │
│  │  ☐ 6. Add monitoring & alerts                                    │      │
│  │  ☐ 7. Validate accuracy maintained/improved                      │      │
│  │  ☐ 8. Measure ROI                                                │      │
│  │  ☐ 9. Iterate based on metrics                                   │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              COMMON PITFALLS                                      │      │
│  │                                                                   │      │
│  │  ❌ Over-optimization: Removing too much context                  │      │
│  │     → Monitor accuracy, not just cost                             │      │
│  │                                                                   │      │
│  │  ❌ Silent truncation: No skip indicators                         │      │
│  │     → Always show what was removed                                │      │
│  │                                                                   │      │
│  │  ❌ Premature abstraction: Complex extraction too early           │      │
│  │     → Start simple (keyword extraction), iterate                  │      │
│  │                                                                   │      │
│  │  ❌ Ignoring metadata: Raw content only                           │      │
│  │     → Add line numbers, timestamps, source tags                   │      │
│  │                                                                   │      │
│  │  ❌ No monitoring: Set and forget                                 │      │
│  │     → Continuous monitoring essential                             │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              NEXT STEPS                                           │      │
│  │                                                                   │      │
│  │  1. Measure your baseline (current token usage + cost)            │      │
│  │  2. Identify highest-volume use cases                             │      │
│  │  3. Implement extraction for top use case                         │      │
│  │  4. Add prompt caching                                            │      │
│  │  5. Deploy with monitoring                                        │      │
│  │  6. Measure impact (cost, latency, quality)                       │      │
│  │  7. Iterate and expand to other use cases                         │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  BOTTOM LINE:                                                               │
│  Context Engineering is not optional for production LLM systems.            │
│  It's the difference between $50K/year and $3K/year at scale.               │
│  Start simple, measure everything, iterate based on data.                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**End of Context Engineering Complete Learning**

**Document Stats:**
- Lines: ~3,000
- Topics covered: 10 major sections
- Diagrams: 50+ visual representations
- Production focus: Atiya implementation + real metrics
- Depth: Production-grade with ROI analysis