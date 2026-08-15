# Model/Provider Abstraction - Quick Reference Slides

---

## Slide 1: The Problem

**Single Provider = Single Point of Failure**

```
OpenAI goes down → Your app breaks

99% uptime = 7 hours downtime/month ❌
```

**Solution:** Multi-provider abstraction with fallback

```
99.9% uptime = 40 minutes downtime/month ✓
```

---

## Slide 2: Architecture

```
Application Layer
      ↓
   "model=smart"
      ↓
LLM Router (Abstraction)
   ↓  ↓  ↓  ↓
   O  A  G  L
   p  n  o  o
   e  t  o  c
   n  h  g  a
   A  r  l  l
   I  o  e
      p
      i
      c
```

**Key:** App never mentions providers, only logical model names

---

## Slide 3: Request Flow

```
1. App: llm.generate(model="smart")
2. Router: "smart" → [openai/gpt-4, anthropic/opus]
3. Try OpenAI → Timeout ✗
4. Fallback to Anthropic → Success ✓
5. Return unified response
```

---

## Slide 4: Circuit Breaker States

```
CLOSED (normal)
    ↓ 5 failures
OPEN (skip provider)
    ↓ 60 seconds
HALF-OPEN (test once)
    ↓ success
CLOSED
```

**Benefit:** Skip failing provider immediately (no 30s timeout waste)

---

## Slide 5: Implementation Patterns

| Pattern | When to Use |
|---------|-------------|
| **Simple Fallback** | Basic reliability |
| **Circuit Breaker** | Prevent timeout waste |
| **Capability Routing** | Vision, function calling |
| **Cost Routing** | Use cheap models for simple tasks |

---

## Slide 6: Configuration Tuning

| Parameter | Default | When to Tune |
|-----------|---------|--------------|
| `timeout` | 30s | Complex prompts → 60s |
| `max_retries` | 3 | Latency-sensitive → 1 |
| `failure_threshold` | 5 | Faster failover → 3 |
| `cache_ttl` | 1hr | Expensive queries → 24hr |

---

## Slide 7: Cost Optimization (30% Savings)

```
Strategy 1: Smart Routing
Simple → Haiku ($0.25/1M)
Complex → GPT-4 ($30/1M)

Strategy 2: Caching
Same prompt = $0

Strategy 3: Shorter Prompts
5000 tokens → 500 tokens = 10x cheaper

Strategy 4: Batch API
Non-urgent = 50% cheaper
```

---

## Slide 8: Failure Categories

```
TRANSIENT → Retry + Fallback
├─ Rate limits
├─ Timeouts
└─ 5xx errors

PERMANENT → Skip + Fallback
├─ Invalid API key
├─ Model not found
└─ Content violation

REQUEST-SPECIFIC → Fix or Abort
├─ Prompt too long
└─ Invalid params
```

---

## Slide 9: Testing Pyramid

```
     E2E (few, slow)
    ╱───────────────╲
   ╱  Integration    ╲
  ╱   (many, fast)    ╲
 ╱──────────────────────╲
╱    Unit (most)         ╲
──────────────────────────

Unit: Test each provider
Integration: Test fallback
Chaos: All providers fail
E2E: Real API calls
```

---

## Slide 10: Observability - What to Track

**Metrics:**
- Success rate (target: >99%)
- P95 latency (target: <3s)
- Fallback rate (target: <10%)
- Cost per request
- Provider health

**Logs:**
- Request started/completed
- Provider failures
- Fallback events
- Circuit breaker state changes

**Alerts:**
- Success rate <95% → Page
- Circuit breaker opened → Notify
- Cost spike 3x → Notify

---

## Slide 11: Latency Breakdown

```
Total: 450ms

Router: 10ms (2%)
Network: 40ms (9%)
Model: 350ms (78%) ← Can't optimize
Processing: 50ms (11%)

Focus: Optimize the 22% you control
```

---

## Slide 12: Security Checklist

```
□ API keys in environment (not code)
□ PII detection enabled
□ Prompt injection sanitization
□ Rate limiting (10 req/min)
□ Cost budgets ($100/day)
□ TLS for all API calls
□ Never log API keys
□ Rotate keys regularly
```

---

## Slide 13: Deployment Flow

```
DEV → Unit Tests
  ↓
STAGING → E2E + Manual QA
  ↓
CANARY → 5% traffic, 30min
  ↓
ROLLOUT → 10% → 50% → 100%
  ↓
STABLE → 24hr → done
```

**Rollback:** `kubectl rollout undo` (< 1 minute)

---

## Slide 14: Debugging Quick Guide

| Symptom | First Check | Quick Fix |
|---------|-------------|-----------|
| High latency | Provider status | Lower timeout, reorder chain |
| High cost | Model usage | Route simple → cheap |
| All fail | Network/keys | Check connectivity, verify keys |

---

## Slide 15: Production Anti-Patterns

```
❌ DON'T                      ✓ DO
────────────────────────────────────────
Hardcode provider           → Use router
No timeout                  → timeout=10s
Retry forever              → Retry 3x max
No logging                 → Log everything
Same model for all         → Smart routing
```

---

## Slide 16: Implementation Phases

```
Phase 1: Core (Week 1)
├─ Abstraction interface
├─ 2 providers (OpenAI, Anthropic)
└─ Simple fallback

Phase 2: Reliability (Week 2)
├─ Circuit breaker
└─ Retry with backoff

Phase 3: Observability (Week 3)
├─ Logging
└─ Metrics

Phase 4: Production (Week 4)
├─ Caching
└─ Deployment
```

---

## Slide 17: Key Metrics Targets

```
Metric              Target      Alert If
─────────────────────────────────────────
Success Rate        >99%        <95%
P95 Latency         <3s         >10s
Fallback Rate       <10%        >20%
Cost/Request        $0.01       3x spike
Circuit Open Time   <5%         >20%
Cache Hit Rate      >20%        <10%
```

---

## Slide 18: Environment Config

```
              DEV     STAGING    PROD
Providers     1       2          3+
Circuit       Off     On         On
Timeout       60s     30s        10s
Retries       1       2          3
Cache         1min    1hr        24hr
Logging       DEBUG   INFO       WARN
```

---

## Slide 19: Trade-off Summary

| Aspect | Direct API | With Abstraction |
|--------|-----------|------------------|
| Code | 10 lines | 500 lines |
| Uptime | 99% | 99.9% |
| Cost | Variable | -30% |
| Latency | 450ms | 460ms |
| Flexibility | None | High |

**Decision:** 10x complexity for 10x reliability

---

## Slide 20: Quick Start for Atiya

**Minimal Implementation (100 lines):**

```python
# 1. Interface
class LLMRouter:
    def generate(self, prompt, model="smart"):
        providers = config.get_providers(model)
        for provider in providers:
            try:
                return provider.generate(prompt)
            except:
                continue
        raise AllProvidersFailed()

# 2. Config
models:
  smart: [openai/gpt-4, anthropic/opus]
  fast: [openai/gpt-3.5, anthropic/haiku]

# 3. Use it
response = router.generate(
    prompt="Analyze this",
    model="smart"
)
```

**Start here, add features as needed.**

---

## Slide 21: When Providers Fail - Timeline

```
TIME    EVENT                   CIRCUIT     ACTION
───────────────────────────────────────────────────
00:00   Req 1 → OpenAI timeout  CLOSED      → Anthropic ✓
00:05   Req 2 → OpenAI timeout  CLOSED      → Anthropic ✓
00:10   Req 3 → OpenAI timeout  CLOSED      → Anthropic ✓
00:15   Req 4 → OpenAI timeout  CLOSED      → Anthropic ✓
00:20   Req 5 → OpenAI timeout  OPEN! 🔴    → Anthropic ✓
00:25   Req 6                   OPEN        SKIP OpenAI → Anthropic (fast!)
01:20   (60s passed)            HALF-OPEN   Test OpenAI
01:21   Req 7 → OpenAI success  CLOSED 🟢   Healed!
```

**Insight:** Requests 6+ skip failing provider = no timeout waste

---

## Slide 22: Model Mapping Example

```yaml
# Semantic names in code
model: "smart"  → High quality reasoning
model: "fast"   → Quick responses
model: "cheap"  → Cost-optimized
model: "vision" → Image analysis

# Router maps to actual providers
smart:
  - openai/gpt-4-turbo ($0.03/1K)
  - anthropic/claude-opus ($0.015/1K)

fast:
  - openai/gpt-3.5 ($0.0015/1K)
  - anthropic/claude-haiku ($0.00025/1K)

vision:
  - openai/gpt-4v
  - anthropic/claude-3
  - google/gemini-vision
```

---

## Slide 23: Response Normalization

**Problem:** Each provider has different response format

**Solution:** Router converts to unified format

```
OpenAI response  ┐
Anthropic response├→ Normalizer → Unified LLMResponse
Google response  ┘

{
  content: "answer",
  model: "gpt-4-turbo",
  provider: "openai",
  tokens: 245,
  cost: 0.0147,
  latency: 487
}
```

---

## Slide 24: Production Checklist

```
Before Deployment:
□ Unit tests pass
□ Integration tests pass
□ Chaos tests pass
□ E2E tests pass
□ Logging configured
□ Metrics dashboard ready
□ Alerts set up
□ Rollback plan documented
□ API keys in secret manager
□ Rate limiting enabled
□ Cost budgets set
□ Staging tested
```

---

## Slide 25: Advanced - Embedding/Judge/Synthesis Separation

**Problem:** Using GPT-4 for everything = 100x wasted cost

**Solution:** Separate by task type

```
┌──────────────────────────────────┐
│ EMBEDDING → text-embedding-3     │
│ (Search)     $0.00002/1K         │
│              50ms                │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ SYNTHESIS → GPT-4 / Gemini Pro   │
│ (Generate)   $0.03/1K            │
│              2s                  │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ JUDGE → GPT-3.5 / Gemini Flash   │
│ (Evaluate) $0.0015/1K            │
│            500ms                 │
└──────────────────────────────────┘

1000 requests/day:
Without: $90/day (all GPT-4)
With: $31.52/day
SAVINGS: 65%
```

---

## Slide 26: Advanced - Partial-Result Preservation

**Problem:** Streaming fails mid-generation → lose everything

**Solution:** Checkpoint during streaming

```
Stream: ████████████░░░░ timeout at 70%
        │    │    │
        Save Save Save

Without Preservation:
- Lost 700 tokens
- Retry 1000 tokens
- Total: 1700 tokens

With Preservation:
- Saved 700 tokens
- Retry 300 tokens
- Total: 1000 tokens

SAVINGS: 41% per timeout
```

**When:** Long generations, unreliable network

---

## Slide 27: Advanced - Optional-Dependency Isolation

**Problem:** Weather API fails → entire agent fails

**Solution:** Classify & isolate dependencies

```
CRITICAL → ABORT if fails
├─ LLM Provider
├─ Database
└─ Auth

IMPORTANT → DEGRADE if fails
├─ Cache
└─ Analytics

OPTIONAL → SKIP if fails
├─ Weather API
├─ Email
└─ Audit logs
```

**Result:** Agent continues with degraded features, not total failure

---

## Slide 28: Summary - All 13 Subskills

1. **Abstraction** = Unified interface across all providers
2. **Fallback** = Automatic switch when provider fails
3. **Circuit Breaker** = Skip consistently failing providers
4. **Model Mapping** = "smart" → actual provider/model
5. **Cost Optimization** = Smart routing saves 30%
6. **Testing** = Unit → Integration → Chaos → E2E
7. **Observability** = Log + metrics + tracing
8. **Deployment** = Canary → gradual → monitor
9. **Reliability** = 99% → 99.9% uptime
10. **Trade-off** = Complexity for reliability
11. **Model Separation** = Different models for different tasks (65% savings)
12. **Partial Preservation** = Checkpoint streaming (41% savings on retry)
13. **Dependency Isolation** = Graceful degradation for optional services

**Status: 13/13 Subskills Complete** ✓

**Start simple (100 lines), add features as needed**
