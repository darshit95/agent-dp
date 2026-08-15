# Architecture Decisions

This document records significant architecture decisions with context and reasoning.

---

## ADR-001: Use n8n + Oracle Cloud for Infrastructure

**Status:** Accepted  
**Date:** 2026-08-08

### Decision
Deploy Atiya using n8n (workflow orchestration) on Oracle Cloud Free Tier instead of Streamlit Cloud alone or paid cloud services.

### Context
Need $0 infrastructure that can:
- Run AI workflows on schedule (2x daily pricing)
- Handle background scraping and processing
- Scale beyond Streamlit Community Cloud's 1GB RAM limit
- Support PostgreSQL for production data

### Why
- Oracle Cloud Free Tier: 4 OCPUs, 24GB RAM, 200GB storage - forever free
- n8n provides visual workflow automation with AI capabilities
- Docker gives full control over environment
- PostgreSQL is production-grade (vs SQLite)

### Rejected Alternatives
| Alternative | Why Not Chosen |
|-------------|----------------|
| Streamlit Cloud only | 1GB RAM limit, no background jobs |
| AWS Free Tier | Only 12 months free |
| Heroku | No longer has free tier |
| Railway | Free tier too limited |

---

## ADR-002: Optimize Contribution Profit, Not ADR/RevPAR

**Status:** Accepted  
**Date:** 2026-08-08

### Decision
The pricing algorithm optimizes **Expected Contribution Profit** rather than ADR (Average Daily Rate) or RevPAR.

### Context
Traditional RMS optimize for ADR or RevPAR, but these metrics ignore:
- OTA commissions (15-20%)
- Payment processing fees (2-3%)
- Cleaning costs per departure
- Channel economics

### Why
- A $150 direct booking is more profitable than a $160 OTA booking
- A 3-night stay costs one cleaning, three 1-night stays cost three cleanings
- Maximizing ADR can lead to empty rooms
- Maximizing occupancy can lead to selling too cheap

### Formula
```
Expected_Profit(price) = 
    E[occupied_room_nights | price, context] × net_room_margin
    + E[ancillary_margin]
    - E[incremental_operating_cost]
    - E[displacement_cost]
```

---

## ADR-003: Use LiteLLM with Gemini Primary, Groq Fallback

**Status:** Accepted  
**Date:** 2026-08-08

### Decision
Use LiteLLM as the model gateway with Gemini 3.6 Flash as primary LLM and Groq as fallback.

### Context
Need $0 LLM costs while maintaining quality for:
- Agent reasoning and hypothesis formation
- Natural language explanations
- Structured output generation

### Why
- Gemini 3.6 Flash: Best free model for agents (reasoning, tool calling)
- Groq Free Tier: Backup when Gemini rate-limited
- LiteLLM: Provider abstraction for easy switching
- Never auto-enable paid tier

### Implementation
```python
try:
    response = completion(model="gemini/gemini-3.6-flash", ...)
except RateLimitError:
    response = completion(model="groq/llama-3.3-70b-versatile", ...)
```

---

## ADR-004: Support Both Manual and Beds24 API Integration

**Status:** Accepted  
**Date:** 2026-08-08

### Decision
Support two integration modes:
- **Option A (Manual):** Owner enters data weekly, applies rates manually
- **Option B (Beds24 API):** Full automation with real-time data sync

### Context
Target users may or may not have Beds24. We need to work with any PMS.

### Why
- Manual mode works with any PMS (broadest reach)
- Beds24 has open REST API (best automation)
- Don't require PMS change for adoption
- Beds24 users get premium experience

### Trade-offs
| Mode | Pros | Cons |
|------|------|------|
| Manual | Works everywhere | More owner effort |
| Beds24 | Full automation | Requires Beds24 |

---

## ADR-005: Candidate-Price Optimization Over Black-Box ML

**Status:** Accepted  
**Date:** 2026-08-08

### Decision
Generate discrete price candidates ($109, $119, $129...) and score each transparently, rather than using a black-box model that outputs a single price.

### Context
Traditional RMS use ML models that output "$157.43" with no explanation.

### Why
- Explainability: Can show "At $149, expected profit is $X"
- Debugging: Easy to see why a price was chosen
- Trust: Owner understands the decision
- Constraints: Easy to apply floor/ceiling/legal limits

### Implementation
```
For each candidate in [$109, $119, ..., $199]:
    1. Forecast demand at this price
    2. Apply cancellation/no-show rates
    3. Calculate contribution profit
    4. Check all constraints
    5. Score candidate
Select argmax(profit)
```

---

## ADR-006: Confidence-Based Escalation

**Status:** Accepted  
**Date:** 2026-08-08

### Decision
Agent behavior varies based on confidence level:
- >85% HIGH: Act autonomously (if autopilot mode)
- 60-85% MEDIUM: Recommend with explanation
- <60% LOW: Present options, ask owner

### Context
Traditional RMS are either full autopilot or full manual. Neither is ideal.

### Why
- Owners don't trust black-box decisions
- Owners don't want to review every decision
- Confidence-based approach balances both
- Builds trust over time as accuracy proven

---

## ADR-007: Built-In Legal Constraints

**Status:** Accepted  
**Date:** 2026-08-08

### Decision
Legal constraints (tax, hidden fees, price gouging, antitrust) are built into the pricing engine, not policy documents.

### Context
Pricing algorithms can violate laws if not carefully constrained.

### Constraints Implemented
1. **Transient Occupancy Tax:** Separate from revenue
2. **Hidden Fee Law:** Mandatory fees in advertised price
3. **Emergency Price Gouging:** Hard cap at +10% during emergencies
4. **Antitrust:** Only public competitor data, independent pricing
5. **Channel Parity:** Per actual contract terms

### Why
- Legal violations are serious
- Policy documents get ignored
- Engine-level constraints are enforced

---

## ADR-008: Results Dashboard with Revenue Attribution

**Status:** Accepted  
**Date:** 2026-08-08

### Decision
Dashboard must show clear before/after comparison and attribute revenue to Atiya's recommendations.

### Context
Owners need to see ROI to justify paying for the service.

### Metrics Shown
- Before/After RevPAR, ADR, Occupancy
- Atiya-attributed revenue uplift
- Recommendation acceptance rate
- Win stories (specific days where Atiya made impact)

### Why
- "Prove value or die"
- Owners are skeptical of AI claims
- Clear ROI justifies cost

---

## Template for New Decisions

```markdown
## ADR-XXX: [Title]

**Status:** Proposed | Accepted | Deprecated  
**Date:** YYYY-MM-DD

### Decision
[What is being decided]

### Context
[Why this decision is needed]

### Why
[Reasoning for the decision]

### Rejected Alternatives
[What else was considered and why not chosen]

### Consequences
[Implications of this decision]
```
