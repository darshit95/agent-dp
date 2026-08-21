# Model/Provider Abstraction and Fallback

**Production AI Engineering Pattern**  
*Learned: 2026-08-15*

---

## Overview

**Problem:** Building AI agents that depend on a single LLM provider (OpenAI, Anthropic) creates a single point of failure. When the provider goes down, your entire application breaks.

**Solution:** Model/Provider Abstraction creates a unified interface across multiple LLM providers with automatic fallback when failures occur.

**Result:** 
- Single provider: 99% uptime = 7 hours downtime/month
- Multi-provider: 99.9% uptime = 40 minutes downtime/month

---

## Architecture

```
┌─────────────────────────────────────┐
│  ATIYA AGENT                        │
│  llm.generate(model="smart")        │  ← Simple interface
└────────────┬────────────────────────┘
             │
             ↓
┌────────────────────────────────────┐
│  LLM ROUTER (Abstraction Layer)    │
│  ├─ Model mapping                  │
│  ├─ Provider selection             │
│  ├─ Circuit breaker check          │
│  ├─ Retry logic                    │
│  └─ Fallback orchestration         │
└──┬──────┬──────────┬────────────┬──┘
   │      │          │            │
   ↓      ↓          ↓            ↓
OpenAI Anthropic  Google     Local
Provider Provider Provider  Provider
```

**Key insight:** Application code never mentions specific providers - it uses logical model names ("smart", "fast", "vision").

---

## Core Mechanics

### 1. Abstraction Interface

```python
# What your app calls
response = llm.generate(
    prompt="Analyze this error",
    model="smart"  # Logical model name
)
```

### 2. Model Mapping

```
Logical Model → Provider + Actual Model

"smart"  → [openai/gpt-4-turbo, anthropic/claude-opus, google/gemini-pro]
"fast"   → [openai/gpt-3.5, anthropic/claude-haiku]
"vision" → [openai/gpt-4v, anthropic/claude-3, google/gemini-vision]
```

### 3. Fallback Flow

```
Request → Try Provider 1 → Success? → Return
              ↓ Failed
          Try Provider 2 → Success? → Return
              ↓ Failed
          Try Provider 3 → Success? → Return
              ↓ Failed
          All Failed → Error/Cache/Queue
```

### 4. Unified Response

All providers return the same structure:
```python
{
    content: str,           # AI's response
    model: str,             # Actual model used
    provider: str,          # Which provider served this
    tokens_used: int,
    cost_usd: float,
    latency_ms: float,
    fallback_used: bool,
    providers_tried: list
}
```

---

## Implementation Patterns

### Pattern 1: Simple Fallback Chain

**Use case:** Basic reliability, prefer cheaper/faster providers first

```
Flow: Try providers in order until one succeeds

Pseudocode:
for provider in [openai, anthropic, google]:
    try:
        return provider.generate(prompt)
    except ProviderError:
        continue
raise AllProvidersFailed()
```

### Pattern 2: Circuit Breaker

**Use case:** Stop wasting time on consistently failing providers

```
State Machine:

CLOSED (normal) → 5 failures → OPEN (skip) → 60s timeout → HALF-OPEN (test)
                                                 ↓ failure ↓
                                                   OPEN

Benefit: After circuit opens, requests skip failing provider immediately 
         (no 30s timeout waste)
```

### Pattern 3: Capability-Based Routing

**Use case:** Route based on required features (vision, function calling)

```
Decision Tree:

Request needs vision?
    YES → Filter to [GPT-4V, Claude 3, Gemini Vision]
    NO  → Cost < $0.01?
          YES → Use [GPT-3.5, Haiku, Local]
          NO  → Use [GPT-4, Opus, Gemini Pro]
```

### Pattern 4: Smart Model Mapping

**Use case:** Application uses semantic names, router handles provider details

```yaml
# config.yaml
models:
  smart:
    - {provider: openai, model: gpt-4-turbo, cost: 0.03}
    - {provider: anthropic, model: claude-opus, cost: 0.015}
  
  fast:
    - {provider: openai, model: gpt-3.5, cost: 0.0015}
    - {provider: anthropic, model: claude-haiku, cost: 0.00025}
```

---

## Configuration

### Key Parameters

| Parameter | Default | Purpose | Tune When |
|-----------|---------|---------|-----------|
| `timeout` | 30s | Max wait for provider | Increase for complex prompts |
| `max_retries` | 3 | Retry attempts | Decrease for latency-sensitive apps |
| `failure_threshold` | 5 | Failures before circuit opens | Lower for faster failover |
| `circuit_timeout` | 60s | How long circuit stays open | Increase during known outages |
| `cache_ttl` | 1hr | Cache response lifetime | Increase for expensive queries |

### Environment-Specific Config

```
                 DEV         STAGING      PROD
Providers        1           2            3+
Circuit Breaker  Disabled    Enabled      Enabled
Timeout          60s         30s          10s
Retries          1           2            3
Cache TTL        60s         1hr          24hr
Logging          DEBUG       INFO         WARNING
```

---

## Trade-offs

| Dimension | Simple (Direct API) | With Abstraction |
|-----------|---------------------|------------------|
| **Code Complexity** | 10 lines | 500+ lines |
| **Reliability** | 99% (single provider) | 99.9% (multi-provider) |
| **Flexibility** | Hardcoded provider | Swap via config |
| **Cost** | Variable | Optimized (30% savings) |
| **Latency (normal)** | 450ms | 460ms (+10ms overhead) |
| **Latency (failure)** | 30s timeout | 500ms (immediate fallback) |
| **When to Use** | Prototypes | Production |

**Decision:** Accept 10x code complexity for 10x better uptime in production.

---

## Failure Modes

### Three Categories

```
TRANSIENT (retry + fallback)
├─ Rate limits (429)
├─ Timeouts (network)
└─ 5xx errors (server down)
→ Strategy: Retry with backoff OR immediate fallback

PERMANENT (skip + fallback)
├─ Invalid API key (401)
├─ Model not found (404)
└─ Content policy violation
→ Strategy: Skip provider, try next

REQUEST-SPECIFIC (fix or abort)
├─ Prompt too long
└─ Invalid parameters
→ Strategy: Modify request OR return error
```

### Error Handling Flow

```
Error occurs
    ↓
Is it transient? → YES → Retry 3x with backoff
    ↓                     Still failing? → Next provider
    NO
    ↓
Is it permanent? → YES → Skip provider → Next provider
    ↓
    NO
    ↓
Request issue? → YES → Fix request OR fail to user
    ↓
    NO
    ↓
All providers failed?
    ↓
Graceful degradation:
├─ Return cached response?
├─ Use local model?
├─ Queue for later?
└─ Show error to user
```

---

## Testing Strategy

### Test Pyramid

```
        ▲
       ╱ ╲      E2E (few, slow, real APIs)
      ╱───╲     Verify real integration
     ╱     ╲
    ╱ Int. ╲    Integration (many, fast, mocked)
   ╱────────╲   Test fallback logic
  ╱          ╲
 ╱   Unit     ╲ Unit (most, fastest, isolated)
╱──────────────╲ Test each provider
```

### Test Types

**Unit:** Does OpenAI provider parse responses correctly?
```python
mock_openai_api(returns="Hello")
assert provider.generate("Hi").content == "Hello"
```

**Integration:** Does fallback work when provider fails?
```python
provider1 = Mock(side_effect=TimeoutError())
provider2 = Mock(returns=Success())
assert router.generate().provider == "provider2"
```

**Chaos:** What happens when all providers fail?
```python
all_providers = [Mock(side_effect=Error()) for _ in range(3)]
with pytest.raises(AllProvidersFailed):
    router.generate()
```

**E2E:** Does it work with real OpenAI API?
```python
@pytest.mark.e2e
response = production_router.generate("Hello")
assert "hello" in response.content.lower()
```

**Circuit Breaker:** Does it stop calling failing providers?
```python
# After 5 failures
assert circuit_state == "OPEN"
assert openai_provider.call_count == 5  # Not 8 (saved 3 calls)
```

---

## Observability

### What to Log

```
INFO (always):
├─ Request started: {request_id, model, user}
├─ Provider used: {provider, latency, cost}
├─ Fallback occurred: {from, to, reason}
└─ Request completed: {tokens, cost}

WARNING (important):
├─ Provider failed: {error, retry_count}
├─ High latency: {latency, threshold}
└─ Rate limit hit: {retry_after}

ERROR (needs attention):
├─ All providers failed: {providers_tried}
└─ Circuit breaker opened: {provider}
```

### Metrics Dashboard

```
RELIABILITY              PERFORMANCE
├─ Success Rate: 99.8%  ├─ P50 Latency: 450ms
├─ Fallback Rate: 3.2%  ├─ P95 Latency: 2.1s
└─ Provider Health      └─ Throughput: 120/s
    OpenAI: 98.5% ✓
    Anthropic: 99.1% ✓    COST
    Google: 85.2% ✗       ├─ Daily: $124.50
                          ├─ Per Request: $0.012
                          └─ By Provider:
                              OpenAI: 72%
                              Anthropic: 22%
```

### Distributed Tracing

```
TRACE: request_abc123 [0ms ──────── 520ms]
│
├─ ModelMapper.resolve()      [0ms ─ 2ms]
├─ CircuitBreaker.check()     [2ms ─ 3ms]
├─ OpenAIProvider.generate()  [3ms ──── 503ms] ✗ TIMEOUT
├─ FallbackHandler.next()     [503ms ─ 505ms]
└─ AnthropicProvider.generate() [505ms ── 520ms] ✓

Insight: Fallback added only 17ms overhead
```

---

## Performance & Cost

### Latency Breakdown

```
Total: 450ms
├─ Router overhead: 10ms (2%)
├─ Network: 40ms (9%)
├─ Model inference: 350ms (78%) ← Out of your control
└─ Response processing: 50ms (11%)

Optimization focus: The 22% you can control
```

### Cost Optimization (30% savings)

```
STRATEGY 1: Smart Routing
Simple tasks → Cheap models (Claude Haiku: $0.25/1M)
Complex tasks → Smart models (GPT-4: $30/1M)

STRATEGY 2: Caching (50% savings on repeated queries)
Same prompt = cached response = $0

STRATEGY 3: Prompt Optimization (20% savings)
Shorter prompts = fewer tokens = lower cost

STRATEGY 4: Batch Processing (10% savings)
Non-urgent tasks → batch API (50% cheaper)
```

---

## Security

### Key Threats & Mitigations

| Threat | Mitigation |
|--------|------------|
| **Prompt Injection** | Sanitize input, separate user/system prompts |
| **API Key Leakage** | Environment vars, never log keys, rotate regularly |
| **Data Leakage** | PII detection, redaction, use local models for sensitive data |
| **Cost Abuse** | Rate limiting (10 req/min), cost budgets ($100/day), auth required |

---

## Production Deployment

### Deployment Flow

```
DEV → Unit Tests
  ↓
STAGING → E2E Tests + Manual QA
  ↓
CANARY → 5% traffic, monitor 30min
  ↓
ROLLOUT → 10% → 50% → 100% (gradual)
  ↓
STABLE → 24hr monitoring → decommission old
```

### Rollback Plan

```
Issue detected (10x latency spike)
    ↓
IMMEDIATE (< 1 min): kubectl rollout undo
    ↓
SHORT TERM (< 1 hr): Investigate, fix, test, re-deploy
    ↓
LONG TERM (next day): Postmortem, add regression test
```

---

## Debugging

### Troubleshooting Guide

**Symptom: High latency**
```
Check:
□ Provider status pages (outage?)
□ Circuit breaker stuck open?
□ Timeout too long?

Fix:
→ Lower timeout (30s → 10s)
→ Reorder fallback chain (put fast provider first)
```

**Symptom: High cost**
```
Check:
□ Using expensive model for simple tasks?
□ Cache hit rate dropped?
□ Prompts getting longer?

Fix:
→ Route simple tasks to cheap models
→ Increase cache TTL
→ Optimize prompts
```

**Symptom: All providers failing**
```
Check:
□ Network issue?
□ Invalid API keys?
□ Request malformed?

Fix:
→ Check network connectivity
→ Verify API keys in secret manager
→ Validate request format
```

---

## Production Anti-Patterns

```
❌ Hardcoded Provider
   response = openai.create(...)
   → No fallback, vendor lock-in
   ✓ Use: router.generate(model="smart")

❌ No Timeout
   response = provider.call()  # Waits forever
   → Blocks everything
   ✓ Use: provider.call(timeout=10)

❌ Retry Forever
   while True: try: call() except: continue
   → Wastes money, never fails fast
   ✓ Use: Retry 3x with exponential backoff

❌ No Observability
   response = provider.call()  # Silent
   → Can't debug failures
   ✓ Use: Log request, response, cost, latency

❌ Same Model for Everything
   all_tasks = router.generate(model="gpt-4")
   → 10x cost, slower
   ✓ Use: Smart routing (simple→fast, complex→smart)
```

---

## Key Takeaways

1. **Reliability:** Multi-provider abstraction increases uptime from 99% to 99.9%
2. **Cost:** Smart routing saves 30% by using cheap models for simple tasks
3. **Circuit Breaker:** Prevents wasting 30s timeouts on failing providers
4. **Testing:** Unit (most) → Integration → Chaos → E2E (few)
5. **Observability:** Log request/response, track metrics, distributed tracing
6. **Deployment:** Canary → gradual rollout → monitor → rollback if needed
7. **Trade-off:** Accept 500 lines complexity for production reliability

---

## Implementation Checklist for Atiya

```
Phase 1: Core (Week 1)
□ Define LLMResponse interface
□ Implement OpenAI provider
□ Implement Anthropic provider
□ Build simple router with fallback
□ Add model mapping config
□ Write unit tests

Phase 2: Reliability (Week 2)
□ Add circuit breaker
□ Add retry with exponential backoff
□ Add timeout enforcement
□ Write integration tests
□ Write chaos tests

Phase 3: Observability (Week 3)
□ Add structured logging
□ Add metrics collection
□ Add distributed tracing
□ Build monitoring dashboard
□ Set up alerts

Phase 4: Production (Week 4)
□ Add caching layer
□ Add rate limiting
□ Run E2E tests
□ Deploy to staging
□ Canary deployment
□ Full production rollout
```

---

---

## Advanced Subskills

### 11. Embedding/Judge/Synthesis Model Separation

**Problem:** Using the same expensive model for all tasks wastes money.

**Solution:** Separate tasks by model specialization:

```
Task Separation Architecture:

┌──────────────────────────────────────────────────┐
│  EMBEDDING (Search/Similarity)                   │
│  Model: text-embedding-3-small                   │
│  Cost: $0.00002/1K tokens                        │
│  Speed: 50ms                                     │
│  Use: Vector search, similarity matching         │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  SYNTHESIS (Generation)                          │
│  Model: GPT-4 / Gemini Pro                       │
│  Cost: $0.03/1K tokens                           │
│  Speed: 2s                                       │
│  Use: Complex reasoning, content generation      │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  JUDGE (Evaluation)                              │
│  Model: GPT-3.5 / Gemini Flash                   │
│  Cost: $0.0015/1K tokens                         │
│  Speed: 500ms                                    │
│  Use: Quality checks, binary decisions           │
└──────────────────────────────────────────────────┘
```

**Model Selection Strategy:**

| Task Type | Model | Reason |
|-----------|-------|--------|
| Embedding | text-embedding-3-small | Fast, cheap, good enough |
| Synthesis | GPT-4 / Gemini Pro | Need reasoning |
| Judge | GPT-3.5 / Gemini Flash | Simple evaluation |
| Extraction | GPT-3.5 | Structured output |
| Classification | Fine-tuned model | High volume |

**Cost Comparison (1000 requests/day):**

```
Without Separation (all GPT-4):
├─ Embedding: $30
├─ Synthesis: $30
└─ Judging: $30
Total: $90/day

With Separation:
├─ Embedding: $0.02
├─ Synthesis: $30
└─ Judging: $1.50
Total: $31.52/day

SAVINGS: $58.48/day = 65% reduction
```

**When to Use:**
- ✓ High volume (>100 calls/day)
- ✓ Different quality requirements
- ✓ Cost is a concern
- ✗ Low volume (<10 calls/day)
- ✗ All tasks need GPT-4 quality

---

### 12. Partial-Result Preservation

**Problem:** Streaming responses fail mid-stream, losing all progress.

**Solution:** Save checkpoints during streaming to preserve partial results.

**Architecture:**

```
Streaming with Checkpoints:

Time: 0s ──────────────────────> 10s

Stream: ████████████████░░░░ (timeout at 7s)
        │    │    │    │
        ↓    ↓    ↓    ↓
Save: [1]  [2]  [3]  [4] ✗ timeout

┌────────────────────────────────┐
│ CHECKPOINT STORAGE             │
│ request_id: abc123             │
│ chunks_received: 4             │
│ content: "1. Consider...       │
│           2. Competitor...     │
│           3. Weather..."       │
│ status: INCOMPLETE             │
│ resume_from: chunk 4           │
└────────────────────────────────┘

RETRY: Resume from chunk 4, don't regenerate 1-3
```

**Preservation Strategies:**

1. **Chunk-Based:** Save every N chunks
2. **Semantic:** Save at complete sentences
3. **Time-Based:** Save every 1 second

**Recovery Flow:**

```
Request starts
    ↓
Stream chunks + save checkpoints
    ↓
   / \
Success? Timeout?
  │       │
  ✓       ↓
 Done   Return partial + retry option
           │
           ↓
       User choice:
       ├─ Keep partial (free)
       └─ Retry from checkpoint
```

**Cost Analysis:**

```
Without Preservation:
Timeout at 70% → Lost 700 tokens
Retry from start → 1000 tokens
Total: 1700 tokens = $0.051

With Preservation:
Timeout at 70% → Saved 700 tokens
Retry only 30% → 300 tokens
Total: 1000 tokens = $0.03

SAVINGS: 41% per timeout
```

**When to Use:**
- ✓ Long generations (>10s)
- ✓ Network unreliable
- ✓ Expensive to regenerate
- ✗ Short generations (<2s)
- ✗ Partial results useless

---

### 13. Optional-Dependency Failure Isolation

**Problem:** One optional service fails → entire agent fails.

**Solution:** Classify dependencies, isolate optional failures.

**Dependency Classification:**

```
┌─────────────────────────────────────────┐
│  CRITICAL (must succeed)                │
│  ├─ LLM Provider                        │
│  ├─ Database                            │
│  └─ Auth Service                        │
│  → Failure: ABORT entire request        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  IMPORTANT (degrade if fail)            │
│  ├─ Cache                               │
│  ├─ Analytics                           │
│  └─ Monitoring                          │
│  → Failure: CONTINUE without feature    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  OPTIONAL (nice to have)                │
│  ├─ Weather API                         │
│  ├─ Email notifications                 │
│  └─ Audit logs                          │
│  → Failure: SILENTLY SKIP               │
└─────────────────────────────────────────┘
```

**Graceful Degradation Flow:**

```
User: "Generate pricing recommendation"

Step 1: Get competitor rates (LLM) ✓ CRITICAL
    ↓
Step 2: Fetch weather data ✗ OPTIONAL
    │ Action: SKIP, continue without
    ↓
Step 3: Check cache ✗ IMPORTANT
    │ Action: DEGRADE (skip cache)
    ↓
Step 4: Generate recommendation ✓ CRITICAL
    ↓
Step 5: Send email ✗ OPTIONAL
    │ Action: SKIP silently
    ↓
Return recommendation (with degradation warnings)
```

**Response Structure:**

```json
{
  "status": "success_degraded",
  "recommendation": {
    "price": 150,
    "confidence": 0.75
  },
  "degradations": [
    {
      "service": "weather_api",
      "impact": "Using historical average",
      "severity": "minor"
    },
    {
      "service": "cache",
      "impact": "Slower response",
      "severity": "moderate"
    }
  ]
}
```

**Circuit Breaker for Optional Services:**

```
Weather API (Optional):

Normal: Try on every request
    ↓ 3 failures
Open: Skip Weather API for 60s
    ↓ timeout
Half-Open: Try once
    ↓ success
Closed: Resume normal

Benefit: Don't waste time on failing optional services
```

**When to Use:**
- ✓ Multiple dependencies
- ✓ Some are non-critical
- ✓ User experience can degrade gracefully
- ✗ All dependencies critical
- ✗ All-or-nothing system

---

## Completion Status

### All 13 Subskills Covered ✓

1. ✓ Unified Model Gateway
2. ✓ Provider Adapter Pattern
3. ✓ Capability-Aware Model Routing
4. ✓ Cost- and Latency-Aware Routing
5. ✓ Retry, Backoff, and Circuit Breaking
6. ✓ Rate-Limit and Quota Management
7. ✓ Fallback Policies and Graceful Degradation
8. ✓ Model and Configuration Versioning
9. ✓ Multi-Model Routing
10. ✓ Task-Specific Model Selection
11. ✓ Embedding/Judge/Synthesis Model Separation
12. ✓ Partial-Result Preservation
13. ✓ Optional-Dependency Failure Isolation

### Implementation Roadmap for Atiya

**Phase 1: Core (Week 1)**
- Unified interface
- 2 providers (Gemini, Groq)
- Simple fallback
- Model mapping

**Phase 2: Reliability (Week 2)**
- Circuit breaker
- Retry with backoff
- Timeout enforcement

**Phase 3: Observability (Week 3)**
- Structured logging
- Metrics collection
- Distributed tracing

**Phase 4: Production (Week 4)**
- Caching layer
- Rate limiting
- E2E tests
- Deployment

---

**Status:** Skill 1 Learning Complete (13/13 subskills) ✓

**Next:** Use `/go-atiya` to implement in Atiya (Aspects 24-25)
