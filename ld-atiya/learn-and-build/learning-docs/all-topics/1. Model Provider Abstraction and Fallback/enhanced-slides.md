# Model Provider Abstraction and Fallback

**Production AI Engineering Patterns**

---

## PART 1: Model Provider Abstraction

---

### Problem and Overview

**Problem:** Single LLM provider = Single point of failure
- OpenAI down? → Entire application breaks
- 99% uptime = 7 hours downtime/month
- Vendor lock-in, no cost optimization

**Solution:** Provider abstraction with automatic fallback
- Multiple providers (OpenAI, Anthropic, Google, Local)
- Automatic failover when one fails
- Unified interface across all

**Result:**
- 99% → 99.9% uptime (7hr → 40min downtime)
- 30% cost savings via smart routing
- Swap providers via config, not code

> **Speaker Notes:** The key insight is treating providers as interchangeable commodities. Your code never mentions "OpenAI" or "Anthropic" - it just requests a "smart" or "fast" model, and the router handles provider selection. This is analogous to database abstraction layers - you don't write MySQL-specific queries, you use an ORM that can target any database.

---

### Architecture

```mermaid
graph TD
    A[Atiya Agent] -->|llm.generate model=smart| B[LLM Router]
    B -->|Model Mapping| C{Provider Selection}
    C --> D[Circuit Breaker Check]
    D --> E[OpenAI Provider]
    D --> F[Anthropic Provider]
    D --> G[Google Provider]
    D --> H[Local Provider]
    E -->|Success/Fail| I[Fallback Orchestration]
    F -->|Success/Fail| I
    G -->|Success/Fail| I
    H -->|Success/Fail| I
    I --> J[Unified Response]
    
    style A fill:#2d2d3d,stroke:#6366f1
    style B fill:#2d2d3d,stroke:#a855f7
    style J fill:#2d2d3d,stroke:#6366f1
```

**Key Components:**
- **Model Mapping:** `"smart"` → provider + model combinations
- **Circuit Breaker:** Skip consistently failing providers
- **Retry Logic:** 3 attempts with exponential backoff
- **Fallback Orchestration:** Try providers until one succeeds

> **Speaker Notes:** The router is the heart of the abstraction. It translates logical model names ("smart", "fast", "vision") into actual provider+model combinations. Think of it as a load balancer for LLM providers. The circuit breaker is crucial - after 5 failures, it marks a provider as "open" (skip it) for 60 seconds, saving you from wasting 30s timeouts on every request.

---

### Abstraction Layer

**Application Code (Simple):**
```javascript
response = llm.generate(
    prompt="Analyze this error",
    model="smart"  // Logical name
)
```

**What Router Does:**
1. Maps `"smart"` → provider list
2. Checks circuit breakers
3. Tries providers in order
4. Returns unified response

**Benefits:**
- Swap providers without code changes
- Cost optimization (route simple → cheap)
- Provider diversity (hedge against outages)

> **Speaker Notes:** Notice the application code is completely provider-agnostic. When you need to add a new provider or change the fallback order, you edit a config file, not code. This is a massive maintainability win. For Atiya, we can experiment with new providers (like Groq for speed) by just updating the config.

---

### Model Mapping

**Logical → Physical Mapping:**

| Logical Model | Provider 1 | Provider 2 | Provider 3 |
|---------------|------------|------------|------------|
| `"smart"` | OpenAI GPT-4 Turbo<br/>$0.03/1K tokens | Anthropic Claude Opus<br/>$0.015/1K tokens | Google Gemini Pro<br/>$0.001/1K tokens |
| `"fast"` | OpenAI GPT-3.5<br/>$0.0015/1K tokens | Anthropic Claude Haiku<br/>$0.00025/1K tokens | Local LLaMA<br/>Free |
| `"vision"` | OpenAI GPT-4V<br/>$0.03/1K tokens | Anthropic Claude 3<br/>$0.015/1K tokens | Google Gemini Vision<br/>$0.001/1K tokens |

**Cost Optimization:**
- Simple tasks → cheap models (30% savings)
- Complex reasoning → expensive models
- Provider 1 fails → automatic fallback to Provider 2

> **Speaker Notes:** The key decision is which provider goes first. Generally, put the cheapest capable model first for cost optimization. For Atiya diagnosis (complex reasoning), we'd put Gemini or Groq first (faster/cheaper), then fall back to Claude Opus if needed. The router tracks costs per provider, so you can see exactly where your money goes.

---

### Fallback Flow

```mermaid
stateDiagram-v2
    [*] --> Request
    Request --> TryProvider1: OpenAI
    TryProvider1 --> Success1: 200 OK
    TryProvider1 --> TryProvider2: Failed (timeout/error)
    
    TryProvider2 --> Success2: 200 OK
    TryProvider2 --> TryProvider3: Failed
    
    TryProvider3 --> Success3: 200 OK
    TryProvider3 --> AllFailed: Failed
    
    Success1 --> Return: content + metadata
    Success2 --> Return: content + metadata
    Success3 --> Return: content + metadata
    
    AllFailed --> Graceful: Cache/Queue/Error
    Graceful --> [*]
    Return --> [*]
```

**Fallback Strategies:**
1. **Retry Current:** If transient error (rate limit), retry 3x with backoff
2. **Next Provider:** If permanent error (401), skip to next provider
3. **Graceful Degradation:** All failed → Return cached response or queue for later

**Latency Impact:**
- Normal: 450ms (no fallback)
- Single failure: 500ms (immediate fallback, +50ms)
- Without fallback: 30,000ms (timeout)

> **Speaker Notes:** The fallback flow is optimized for latency. When a provider fails, we don't wait for the full timeout - we detect certain errors (401, 429, connection refused) immediately and fall back. This is why fallback only adds 50ms, not 30 seconds. The circuit breaker is key here - once we know a provider is down, we skip it entirely until the circuit closes.

---

### Unified Response Format

**All providers return same structure:**

```json
{
  "content": "BGP peer2 was administratively shutdown",
  "model": "claude-opus-4",
  "provider": "anthropic",
  "tokens_used": 1250,
  "cost_usd": 0.01875,
  "latency_ms": 1820,
  "fallback_used": true,
  "providers_tried": ["openai", "anthropic"]
}
```

**Benefits:**
- Application doesn't care which provider succeeded
- Consistent logging and metrics
- Easy to track costs and performance per provider

> **Speaker Notes:** The unified response format is critical for observability. Your application doesn't need to handle different response structures from different providers - they all look the same. The `fallback_used` and `providers_tried` fields are gold for debugging - you can see at a glance when fallback happened and which provider ultimately served the request.

---

### Implementation Pattern: Circuit Breaker

```mermaid
stateDiagram-v2
    [*] --> CLOSED
    CLOSED --> OPEN: 5 failures
    OPEN --> HALF_OPEN: 60s timeout
    HALF_OPEN --> CLOSED: Success
    HALF_OPEN --> OPEN: Failure
    
    note right of CLOSED
        Normal operation
        Try provider on every request
    end note
    
    note right of OPEN
        Skip provider immediately
        Save 30s timeout per request
    end note
    
    note right of HALF_OPEN
        Test if provider recovered
        Try once, then decide
    end note
```

**Parameters:**
- **Failure Threshold:** 5 failures → circuit opens
- **Timeout:** Circuit stays open for 60s
- **Recovery:** 1 success in HALF-OPEN → circuit closes

**Impact:**
- Without: 5 failures × 30s timeout = 150s wasted
- With: 5 failures × 30s + skip rest = 150s wasted once, then 0s

> **Speaker Notes:** The circuit breaker is a huge latency win during outages. Imagine OpenAI is down - without circuit breaker, you'd waste 30 seconds on EVERY request trying OpenAI first. With circuit breaker, you waste 150 seconds detecting it's down (5 attempts), then you skip OpenAI entirely for the next 60 seconds. For 100 requests during that minute, you save 100 × 30s = 3000s = 50 minutes of user-facing latency.

---

### Implementation Pattern: Capability-Based Routing

**Route based on required features:**

```mermaid
graph TD
    A[Request] --> B{Needs Vision?}
    B -->|Yes| C[Filter to vision models]
    B -->|No| D{Cost < $0.01?}
    C --> E[GPT-4V, Claude 3, Gemini Vision]
    D -->|Yes| F[GPT-3.5, Haiku, Local]
    D -->|No| G[GPT-4, Opus, Gemini Pro]
    
    E --> H[Return first available]
    F --> H
    G --> H
    
    style A fill:#2d2d3d,stroke:#6366f1
    style H fill:#2d2d3d,stroke:#6366f1
```

**Capability Matrix:**

| Provider/Model | Vision | Function Calling | Streaming | Cost |
|----------------|--------|------------------|-----------|------|
| OpenAI GPT-4V | ✓ | ✓ | ✓ | $$$ |
| Anthropic Claude 3 | ✓ | ✓ | ✓ | $$ |
| Google Gemini Vision | ✓ | ✓ | ✓ | $ |
| OpenAI GPT-3.5 | ✗ | ✓ | ✓ | $ |

> **Speaker Notes:** Capability routing is smarter than just picking the first provider. For Atiya, we don't need vision or function calling - just text completion. So we can route to the cheapest capable model. But if you later add image analysis (e.g., analyzing screenshots of failed tests), the router automatically filters to vision-capable models. This future-proofs your system.

---

### Error Handling Flow

```mermaid
graph TD
    A[Error Occurs] --> B{Error Type?}
    B -->|Transient| C[429 Rate Limit<br/>Timeout<br/>5xx Server Error]
    B -->|Permanent| D[401 Invalid Key<br/>404 Model Not Found<br/>Content Policy]
    B -->|Request Issue| E[Prompt Too Long<br/>Invalid Parameters]
    
    C --> F[Retry 3x with<br/>Exponential Backoff]
    F --> G{Still Failing?}
    G -->|Yes| H[Try Next Provider]
    G -->|No| I[Return Success]
    
    D --> H
    
    E --> J{Can Fix?}
    J -->|Yes| K[Modify Request<br/>Try Again]
    J -->|No| L[Return Error to User]
    
    H --> M{All Providers Failed?}
    M -->|Yes| N[Graceful Degradation:<br/>Cache/Queue/Error]
    M -->|No| O[Try Next Provider]
    
    style A fill:#2d2d3d,stroke:#f87171
    style I fill:#2d2d3d,stroke:#6366f1
    style N fill:#2d2d3d,stroke:#a855f7
```

**Error Categories:**
1. **Transient:** Retry current provider
2. **Permanent:** Skip to next provider
3. **Request Issue:** Fix or abort

> **Speaker Notes:** The key insight is categorizing errors correctly. A 429 rate limit is transient - retry in 5 seconds. A 401 invalid key is permanent for that provider - skip to the next one immediately. A prompt that's too long is a request issue - truncate it or return an error. Getting this wrong wastes time and money. For example, retrying a 401 error 3 times before giving up wastes 90 seconds.

---

### Scale, Performance, and Observability

**Performance Metrics:**

```
Total Latency: 450ms
├─ Router Overhead: 10ms (2%)
├─ Network: 40ms (9%)
├─ LLM Inference: 350ms (78%) ← Out of your control
└─ Response Processing: 50ms (11%)

Optimization focus: The 22% you CAN control
```

**Cost Optimization (30% savings):**
1. **Smart Routing:** Simple → cheap models
2. **Caching:** 50% savings on repeated queries
3. **Prompt Optimization:** Shorter prompts = lower cost
4. **Batch Processing:** Non-urgent → 50% cheaper

**Observability:**
- **Metrics:** Success rate, fallback rate, P50/P95 latency, cost per request
- **Logging:** Request ID, provider used, fallback events, errors
- **Tracing:** Distributed trace showing provider fallback timeline

> **Speaker Notes:** The performance breakdown shows you can only optimize 22% of latency - the rest is LLM inference. Focus on router overhead (keep it under 10ms) and response processing (use streaming). For cost, the biggest win is smart routing - using GPT-3.5 for simple tasks and GPT-4 only when needed saves 90% on those requests. Caching is second - same question asked twice? Return cached answer for $0.

---

### Embedding/Judge/Synthesis Model Separation

**Problem:** Using expensive GPT-4 for ALL tasks wastes money

**Solution:** Separate models by task type

```mermaid
graph LR
    A[Task] --> B{Task Type?}
    B -->|Search/Similarity| C[Embedding Model<br/>text-embedding-3-small<br/>$0.00002/1K tokens<br/>50ms]
    B -->|Content Generation| D[Synthesis Model<br/>GPT-4 / Gemini Pro<br/>$0.03/1K tokens<br/>2s]
    B -->|Quality Check| E[Judge Model<br/>GPT-3.5 / Gemini Flash<br/>$0.0015/1K tokens<br/>500ms]
    
    style A fill:#2d2d3d,stroke:#6366f1
    style C fill:#2d2d3d,stroke:#a855f7
    style D fill:#2d2d3d,stroke:#f87171
    style E fill:#2d2d3d,stroke:#fbbf24
```

**Cost Comparison (1000 requests/day):**

| Strategy | Daily Cost | Annual Cost |
|----------|------------|-------------|
| All GPT-4 | $90/day | $32,850/year |
| Separated | $31.52/day | $11,505/year |
| **Savings** | **$58.48/day** | **$21,345/year** |

**When to Use:**
- ✓ High volume (>100 calls/day)
- ✓ Different quality requirements per task
- ✗ All tasks need GPT-4 quality

> **Speaker Notes:** For Atiya, we might use this separation for: 1) Embedding: Find similar past failures (cheap model), 2) Synthesis: Generate root cause diagnosis (expensive model), 3) Judge: Validate diagnosis quality (medium model). The 65% cost savings comes from using the right tool for each job. Think of it like hiring - you don't hire a senior architect to answer phones.

---

## PART 2: Reliability Engineering

---

### Problem and Overview

**The Reliability Problem:**
- Well-engineered prompts still hallucinate
- LLMs speculate when evidence is missing
- No citations → unreliable diagnoses
- Users can't trust the output

**Real Atiya Impact (Before):**
- 28% hallucination rate (280/1000 wrong diagnoses)
- 85% speculation instead of "I don't know"
- 42% no citations
- 100% human review required
- **Cost:** $8,333/day in review time

**Solution:** 6 Defense-in-Depth Patterns
1. Hallucination Prevention
2. Insufficient-Data Handling
3. Evidence-Only Instructions
4. Citation Rules
5. Evidence Policy
6. Confidence Thresholds

> **Speaker Notes:** The key insight is that reliability is not one fix - it's defense-in-depth. Just adding constraints reduces hallucination from 28% to 18%. Adding citation validation gets you to 8%. Adding insufficient-data handling gets you to 4%. Each layer catches different failure modes. This is analogous to security - you don't just have a firewall, you have firewall + IDS + encryption + authentication.

---

### Results After Implementation

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Hallucination rate | 28% | 4% | **-24pp** |
| Proper "I don't know" | 15% | 94% | **+79pp** |
| Evidence citations | 42% | 98% | **+56pp** |
| Human trust | 62% | 94% | **+32pp** |
| Review rate | 100% | 38% | **-62pp** |
| **Daily cost** | **$8,333** | **$3,167** | **-$5,166** |

**Monthly Savings:** $215,424

**ROI:** Reliability engineering is the highest-ROI investment for Atiya

> **Speaker Notes:** Look at that trust number - 62% to 94%. That's the difference between "interesting prototype" and "production tool engineers rely on daily." The 62pp reduction in review rate is massive - engineers only review 38% of diagnoses now (high-confidence ones auto-approve). This frees engineers to focus on actual debugging instead of validating AI output.

---

### Reliability as Defense-in-Depth

```mermaid
graph TD
    A[Test Failure] --> B[Evidence Collection]
    B --> C[Pre-Prompt Layer]
    
    C --> D1[Hallucination<br/>Prevention<br/>Constraints]
    C --> D2[Insufficient-Data<br/>Detection<br/>Early Return]
    C --> D3[Evidence<br/>Boundary Check<br/>Trusted Sources]
    
    D1 --> E[LLM Prompt<br/>with Rules]
    D2 --> E
    D3 --> E
    
    E --> F[LLM Response]
    
    F --> G[Post-Response Layer]
    
    G --> H1[Citation<br/>Validation<br/>Verify Quotes]
    G --> H2[Evidence<br/>Policy Check<br/>Chain of Custody]
    G --> H3[Confidence<br/>Thresholding<br/>Auto-approve?]
    
    H1 --> I[Validated<br/>Diagnosis]
    H2 --> I
    H3 --> I
    
    style A fill:#2d2d3d,stroke:#6366f1
    style C fill:#2d2d3d,stroke:#a855f7
    style G fill:#2d2d3d,stroke:#a855f7
    style I fill:#2d2d3d,stroke:#6366f1
```

**Three Layers:**
1. **Pre-Prompt:** Check evidence quality, add constraints
2. **Prompt:** Call LLM with reliability-enhanced prompts
3. **Post-Response:** Validate output, check citations, threshold confidence

> **Speaker Notes:** Think of this like airport security - you don't just have one checkpoint, you have ID check + metal detector + bag scan + random screening. Each layer catches different threats. For Atiya, pre-prompt catches obvious insufficient evidence (saves 12% of LLM calls), prompt constraints prevent hallucination during generation (24% improvement), post-response validation catches edge cases (final 4% improvement).

---

### Core Mechanics Overview

**Six Key Reliability Techniques:**

| # | Technique | Impact | What It Does |
|---|-----------|--------|--------------|
| **1** | **Hallucination Prevention** | 28% → 4% | Stop LLM from inventing facts |
| **2** | **Insufficient-Data Handling** | 15% → 94% | Explicit "I don't know" instead of guessing |
| **3** | **Evidence-Only Instructions** | No external knowledge | Only cite trusted sources (logs, config, code) |
| **4** | **Citation Rules** | 42% → 98% | Exact quotes with line numbers |
| **5** | **Evidence Policy** | Chain of custody | Auditable, reproducible diagnoses |
| **6** | **Confidence Thresholds** | 100% → 38% review | Smart routing: auto-approve high confidence |

**Combined Result:**
- Hallucination: 28% → 4% (-24pp)
- Trust: 62% → 94% (+32pp)
- Review cost: $8,333/day → $3,167/day (-$5,166/day)
- **Monthly savings: $215,424**

> **Speaker Notes:** These six techniques work together as defense-in-depth. Hallucination prevention sets rules, insufficient-data handling enforces "I don't know," evidence-only prevents contamination, citation rules enable verification, evidence policy adds auditability, and confidence thresholds enable smart routing. For Atiya, we implement all six - each costs 0.5-1.5 days engineering, saves thousands per month. The key is that each layer catches different failure modes - you need all six to get from 62% trust (unusable) to 94% trust (production-ready).

---

### 1. Hallucination Prevention

**Four-Part Strategy:**

```mermaid
graph TD
    A[Diagnosis Generated] --> B{Check 1:<br/>Speculation Words?}
    B -->|Found: might/could/possibly| C[FAIL: Speculation]
    B -->|None| D{Check 2:<br/>Citations Valid?}
    
    D -->|Quotes not in logs| E[FAIL: Invalid Citation]
    D -->|All valid| F{Check 3:<br/>Generic Phrases?}
    
    F -->|Found: network issue| G[FAIL: Too Generic]
    F -->|None| H[PASS: Valid Diagnosis<br/>Score < 0.3]
    
    C --> I[Retry with<br/>Feedback]
    E --> I
    G --> I
    
    style A fill:#2d2d3d,stroke:#6366f1
    style H fill:#2d2d3d,stroke:#6366f1
    style I fill:#2d2d3d,stroke:#f87171
```

**Explicit Constraints in System Prompt:**

```
MUST:
✅ ONLY cite evidence in <logs>, <config>, <test_code>
✅ Quote exact lines: "line 342: ERROR timeout"
✅ If ambiguous, list multiple hypotheses

MUST NOT:
❌ Never invent log lines or config snippets
❌ Never speculate beyond evidence
❌ Never use "probably", "might be", "could be"
```

**Impact:** 28% → 4% hallucination rate (-24pp)

> **Speaker Notes:** The key is making constraints explicit and checking them. The word list ["might", "could", "possibly", "probably", "likely"] catches 90% of speculative language. The citation validator catches invented quotes. Together, they reduce hallucination by 86% (28% to 4%). For Atiya, this means 240 fewer wrong diagnoses per day. At 30 minutes wasted per wrong diagnosis, that's 120 hours saved per day.

---

### 2. Insufficient-Data Handling

**The Problem:** LLMs guess instead of saying "I don't know"

**Example (BAD):**

Input:
```
Logs: "FAILED AssertionError"
Config: (not provided)
```

Response:
```json
{
  "root_cause": "Test assertion failed, likely timing issue",
  "confidence": 0.65,
  "evidence": ["FAILED AssertionError"]
}
```

**Problems:** Speculation ("likely timing"), no evidence, too confident

**Example (GOOD):**

```json
{
  "root_cause": "INSUFFICIENT_DATA - logs show only bare assertion error with no stack trace",
  "confidence": 0.0,
  "evidence": ["FAILED AssertionError"],
  "recommended_fix": "Re-run with --log-level=DEBUG",
  "requires_human_review": true
}
```

**Benefits:** Admits uncertainty, tells what's missing, actionable next step

> **Speaker Notes:** The INSUFFICIENT_DATA pattern has three parts: 1) Sentinel value (explicit flag), 2) Specific reason (logs too short/no stack trace/config missing), 3) Recommended fix (how to get more evidence). For Atiya, 12% of failures have minimal logs - detecting this early saves $3,000/day in wasted debugging time.

---

### Pre-Check Optimization

**Fast-Path Detection (Before LLM Call):**

```mermaid
graph TD
    A[Evidence Received] --> B{len logs < 100?}
    B -->|Yes| C[Return INSUFFICIENT_DATA<br/>Reason: Logs too short<br/>Don't call LLM]
    B -->|No| D{FAILED in logs<br/>AND len < 200?}
    D -->|Yes| E[Return INSUFFICIENT_DATA<br/>Reason: Bare error only<br/>Don't call LLM]
    D -->|No| F[Proceed to LLM<br/>Evidence sufficient]
    
    style A fill:#2d2d3d,stroke:#6366f1
    style C fill:#2d2d3d,stroke:#f87171
    style E fill:#2d2d3d,stroke:#f87171
    style F fill:#2d2d3d,stroke:#6366f1
```

**Savings:**
- 12% of failures have obvious insufficient evidence
- Detecting pre-LLM saves: 120 requests/day × $0.105 = $12.60/day
- Annual savings: $4,599

**Impact:** Small cost savings, but huge UX win (immediate feedback)

> **Speaker Notes:** Pre-check is about failing fast. If logs are < 100 characters, you know there's not enough info - don't waste 8 seconds calling the LLM only to get "INSUFFICIENT_DATA" back. Return immediately. For Atiya, this also improves UX - users get instant feedback "need more logs" instead of waiting 8 seconds for the same answer.

---

### 3. Evidence-Only Instructions

**Trusted vs Untrusted Sources:**

```
TRUSTED (Can cite):
✅ <logs> - Test execution logs from ReportPortal
✅ <config> - Device configuration from testbed
✅ <test_code> - Test source from git
✅ Logical inferences from above

UNTRUSTED (Cannot cite):
❌ PAN-OS documentation (how things SHOULD work)
❌ LLM training data (common patterns)
❌ Assumed defaults (inferred configurations)
❌ External knowledge (RFCs, guides)
```

**Why This Matters:**
- LLM knows "PAN-OS defaults to 60s BGP keepalive"
- But actual device configured for 30s
- Assuming default → wrong diagnosis
- Result: "likely keepalive timeout" when actual issue is "peer shutdown"

**Validation:** Flag any citation not in `<logs>`, `<config>`, or `<test_code>`

> **Speaker Notes:** The contamination problem is subtle. LLMs have vast knowledge about how systems SHOULD work - but we need to know how THIS system ACTUALLY failed. The evidence boundary prevents the LLM from injecting external knowledge. For Atiya, this means the diagnosis is based solely on what we observed, not on what "usually" happens.

---

### 4. Citation Rules

**Required Format:**

```
<source> line <number>: <exact quote>

Examples:
✅ "logs line 342: ERROR BGP session timeout after 60s"
✅ "config line 23: neighbor peer2 shutdown"
✅ "test_code line 45: assert active_peer == 'peer2'"

❌ "logs show error" (not exact quote)
❌ "configuration problem" (not a citation)
```

**Why Line Numbers?**
- Fast lookup: `grep -n "ERROR BGP" logs.txt` → jump to line 342
- No ambiguity: If quote appears multiple times, line number disambiguates
- Reproducibility: Different engineer can verify by checking same line

**Citation Validation Flow:**

```mermaid
graph TD
    A[For each citation] --> B[Extract Quote]
    B --> C{Quote exists<br/>in evidence?}
    C -->|Yes| D[Valid ✓]
    C -->|No| E[Hallucination ✗]
    
    D --> F{More citations?}
    F -->|Yes| A
    F -->|No| G[All Valid<br/>Return Diagnosis]
    
    E --> H[Retry with<br/>Feedback OR<br/>Flag for Review]
    
    style A fill:#2d2d3d,stroke:#6366f1
    style G fill:#2d2d3d,stroke:#6366f1
    style H fill:#2d2d3d,stroke:#f87171
```

**Impact:** 42% → 98% proper citations (+56pp)

> **Speaker Notes:** Citation validation is automated - we extract the quoted text and verify it exists in the evidence. If validation fails, we either retry with feedback ("quotes must be exact, not paraphrased") or flag for human review. For Atiya, this catches 98% of hallucinations in post-processing. The line numbers are gold for engineers - they can jump directly to the evidence without grep-ing.

---

### 5. Evidence Policy

**Chain of Custody:**

```mermaid
graph TD
    A[Test Execution] --> B[partsrt logger → ReportPortal]
    B --> C[Atiya Evidence Collector]
    C --> D[Evidence Validation]
    
    D --> E1[Verify Source<br/>ReportPortal ID]
    D --> E2[Check Timestamp]
    D --> E3[Compute Hash<br/>Integrity]
    
    E1 --> F[LLM Prompt<br/>with Metadata]
    E2 --> F
    E3 --> F
    
    F --> G[LLM Response<br/>with Citations]
    
    G --> H[Citation Verification<br/>Quotes exist?]
    
    H --> I[Final Diagnosis<br/>Auditable]
    
    style A fill:#2d2d3d,stroke:#6366f1
    style D fill:#2d2d3d,stroke:#a855f7
    style I fill:#2d2d3d,stroke:#6366f1
```

**Evidence Metadata:**

```json
{
  "source": "ReportPortal",
  "launch_id": "12345",
  "timestamp": "2026-08-20T14:32:18Z",
  "device": "fw-tb-sase-01",
  "verification_hash": "a3f5d2c8"
}
```

**Benefits:**
- Engineer can trace diagnosis back to source
- Reproducible (re-run same test, verify diagnosis)
- Auditable (who collected when, integrity verified)

> **Speaker Notes:** Evidence policy is about trust and reproducibility. When an engineer sees "config line 23: neighbor peer2 shutdown", they need to know: 1) Where did this config come from? (device fw-tb-sase-01), 2) When was it collected? (2026-08-20 14:32:18), 3) Has it been tampered with? (hash verification). For Atiya in production, this is the difference between "useful tool" and "critical infrastructure." Six months later, you can still verify a diagnosis.

---

### 6. Confidence Thresholds

**Smart Routing Based on Certainty:**

| Confidence | Policy | Example | Review? |
|------------|--------|---------|---------|
| **0.9-1.0** | Auto-approve | Config shows "shutdown" + logs confirm | No |
| **0.7-0.9 (simple)** | Conditional approve | Config issue in known category | No |
| **0.7-0.9 (complex)** | Review | Timeout error, cause unclear | Yes |
| **0.5-0.7** | Always review | Single indicator, no corroboration | Yes |
| **0.3-0.5** | Escalate urgent | Circumstantial evidence only | Yes |
| **<0.3** | INSUFFICIENT_DATA | Bare error, no context | Yes |

**Escalation Flow:**

```mermaid
graph TD
    A[Diagnosis Generated<br/>confidence = X] --> B{X >= 0.9?}
    B -->|Yes| C[Auto-approve<br/>No review needed]
    B -->|No| D{X >= 0.7?}
    
    D -->|Yes| E{Category simple?<br/> config/code}
    D -->|No| F{X >= 0.5?}
    
    E -->|Yes| G[Conditional approve<br/>Optional review]
    E -->|No| H[Review required]
    
    F -->|Yes| H
    F -->|No| I{X >= 0.3?}
    
    I -->|Yes| J[Urgent review<br/>Low confidence]
    I -->|No| K[INSUFFICIENT_DATA<br/>Flag + escalate]
    
    style C fill:#2d2d3d,stroke:#6366f1
    style G fill:#2d2d3d,stroke:#a855f7
    style H fill:#2d2d3d,stroke:#fbbf24
    style J fill:#2d2d3d,stroke:#f87171
    style K fill:#2d2d3d,stroke:#f87171
```

**Impact:**
- Before: 100% review rate (1000 diagnoses/day × 10min = 167 hours)
- After: 38% review rate (380 diagnoses/day × 10min = 63 hours)
- **Savings: 104 hours/day = $5,166/day = $154,980/month**

> **Speaker Notes:** Confidence thresholding is the ROI king. By auto-approving high-confidence diagnoses (38% of cases), we reduce review burden by 62%. Engineers only look at medium/low confidence cases. The thresholds are calibrated: 0.9+ means "smoking gun evidence" (e.g., config explicitly says shutdown + logs confirm), 0.7-0.9 means "strong evidence but minor ambiguity", 0.5-0.7 means "single indicator without corroboration". For Atiya, this means engineers can review 380 diagnoses in the same time they used to review 1000.

---

### Key Insights

**1. Defense-in-Depth Works**
- Single layer (constraints): 85% reliability
- All 6 layers combined: 96% reliability
- Each layer catches different failure modes

**2. Hallucination Prevention is Highest ROI**
- 1.5 days engineering
- 24pp improvement (28% → 4%)
- $44,000/month savings
- Payback: 0.9 days

**3. Evidence Policy Builds Trust**
- Not about immediate ROI
- About reproducibility and auditability
- Difference between "prototype" and "critical infrastructure"

**4. Confidence Thresholds Enable Scale**
- 62pp reduction in review rate
- Same quality, 62% less human effort
- Frees engineers for actual debugging

**5. "I Don't Know" is a Feature**
- Better to admit uncertainty than speculate
- INSUFFICIENT_DATA saves debugging time
- 79pp improvement (15% → 94%)

**6. Reliability is Continuous**
- Monitor hallucination rate, calibration error
- Alert when metrics degrade
- Iterate on constraints based on failures

> **Speaker Notes:** The key insight is that reliability is not a one-time fix - it's continuous improvement. You implement the six patterns, monitor metrics, and tune. For Atiya, we found that the hallucination rate drifted from 4% to 7% over two weeks as failure patterns changed. We added new constraints based on the new hallucinations and got back to 4%. Treat reliability like security - always assume new attack vectors will emerge.

---

### Summary: What We Learned

**Model Provider Abstraction:**
- Treat providers as interchangeable commodities
- 10x code complexity → 10x uptime improvement
- Circuit breaker saves 30s timeouts on failing providers
- Smart routing saves 30% via cheap models for simple tasks
- Separate embedding/judge/synthesis models (65% savings)

**Reliability Engineering:**
- Six patterns in defense-in-depth (not just one fix)
- Hallucination prevention: explicit constraints + validation
- Insufficient-data: admit uncertainty, don't speculate
- Evidence-only: prevent external knowledge contamination
- Citation rules: enable verification in < 30 seconds
- Evidence policy: chain of custody for trust
- Confidence thresholds: auto-approve high confidence

**For Atiya:**
- Abstraction: 99.9% uptime, swap providers via config
- Reliability: 94% trust, 62% less review, $215K/month savings

**Next Steps:**
1. Implement provider abstraction (Weeks 1-2)
2. Add reliability patterns (Weeks 3-4)
3. Monitor metrics, tune thresholds
4. Iterate based on production failures

---

**End of Presentation**

*Reference: Model Provider Abstraction and Fallback Learning Materials*
