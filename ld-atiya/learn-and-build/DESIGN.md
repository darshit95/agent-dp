# Atiya Agent Design Document

## Executive Summary

Atiya is an **AI Revenue Manager** for small-medium independent motels (10-100 rooms). Unlike traditional RMS that are black-box algorithms, Atiya is a truly agentic system that:

- **Forms hypotheses** about demand changes
- **Investigates** using multiple data sources
- **Reasons** about evidence with confidence scoring
- **Explains** decisions in plain English
- **Learns** from owner feedback and actual outcomes
- **Proves value** with clear ROI tracking

## Problem Statement

- Less than 10% of independent hotels use any RMS
- Existing solutions (RoomPriceGenie, PriceLabs) are either:
  - Too expensive for small motels
  - Too complex (designed for revenue managers)
  - Black-box (no explanation of WHY a price was recommended)
  - No learning from owner feedback
  - Optimize wrong metric (ADR/RevPAR instead of contribution profit)

## Target User

**"Sam"** - Owner-operator of a 40-room independent motel
- Tech comfort: 2/10 (comfortable with smartphone, not complex systems)
- Time available: 30 minutes/day for pricing decisions
- Goal: Increase revenue without spending hours on data analysis
- Fear: Losing control to an algorithm they don't understand

## Core Differentiators

| Feature | Competitors | Atiya |
|---------|------------|-------|
| **Pricing Logic** | Black-box algorithm | Explainable with reasoning |
| **Learning** | None | Learns from owner feedback |
| **Confidence** | Always certain | Confidence-based escalation |
| **Optimization** | ADR/RevPAR | Contribution profit |
| **Cold Start** | Needs 6+ months history | Works Day 1 |
| **Control** | Autopilot or manual | Multiple autonomy levels |
| **ROI** | Dashboard metrics | Proves attributed revenue |

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       ATIYA AGENTIC SYSTEM                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                 ORCHESTRATOR AGENT (Brain)                     │ │
│  │                                                                │ │
│  │  GOALS:                                                        │ │
│  │  - Primary: Maximize RevPAR within guardrails                  │ │
│  │  - Secondary: Improve occupancy on weak nights                 │ │
│  │  - Learned: Adjusted targets from owner's actual results       │ │
│  │                                                                │ │
│  │  CAPABILITIES:                                                 │ │
│  │  - Plans multi-step investigations                             │ │
│  │  - Decides: act autonomously OR ask human                      │ │
│  │  - Maintains state across sessions                             │ │
│  │  - Learns from accepted/rejected recommendations               │ │
│  └──────────────────────────┬────────────────────────────────────┘ │
│                             │                                       │
│      ┌──────────────────────┼──────────────────────┐               │
│      │                      │                      │               │
│      ▼                      ▼                      ▼               │
│  ┌──────────┐        ┌──────────┐          ┌──────────┐           │
│  │ MARKET   │        │ DEMAND   │          │ PRICING  │           │
│  │ INTEL    │        │ ANALYST  │          │STRATEGIST│           │
│  │ AGENT    │        │ AGENT    │          │ AGENT    │           │
│  │          │        │          │          │          │           │
│  │ - Scrape │        │ - Form   │          │ - Generate│          │
│  │   comps  │        │   demand │          │   price   │          │
│  │ - Find   │        │   hypo-  │          │   options │          │
│  │   events │        │   theses │          │ - Simulate│          │
│  │ - Weather│        │ - Test   │          │   outcomes│          │
│  │          │        │   data   │          │ - Explain │          │
│  └──────────┘        └──────────┘          └──────────┘           │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    AGENTIC DIAGNOSTIC LOOP                     │ │
│  │                                                                │ │
│  │   FORM → INVESTIGATE → ANALYZE → DECIDE → (LOOP or ACT)       │ │
│  │                                                                │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                      LEARNING LOOP                             │ │
│  │                                                                │ │
│  │  RECOMMEND → OWNER ACCEPTS/REJECTS → OUTCOME DATA → LEARN     │ │
│  │                                                                │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Infrastructure Architecture (Multi-Agent + Oracle Cloud)

```
                        INTERNET
                           │
                           ▼
              https://atiya.your-domain.com
                           │
                           ▼
            ┌──────────────────────────────┐
            │        Cloudflare            │
            │   (Free SSL/DNS/Caching)     │
            └──────────────┬───────────────┘
                           │
            ┌──────────────▼───────────────┐
            │    Oracle Cloud Free Tier    │
            │                              │
            │  ┌────────────────────────┐  │
            │  │   VM.Standard.A1.Flex  │  │
            │  │   4 OCPU, 24GB RAM     │  │
            │  │   200GB Storage        │  │
            │  └───────────┬────────────┘  │
            │              │               │
            │  ┌───────────▼────────────┐  │
            │  │   Docker Environment   │  │
            │  │                        │  │
            │  │  Streamlit UI          │  │
            │  │  FastAPI Backend       │  │
            │  │    + CrewAI/LangGraph  │  │
            │  │  PostgreSQL + pgvector │  │
            │  │                        │  │
            │  └────────────────────────┘  │
            └──────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │   LiteLLM   │          │  Free APIs  │
       │   Gateway   │          │             │
       └──────┬──────┘          │ - NWS       │
              │                 │ - Ticketmaster│
       ┌──────┴──────┐          │ - Beds24    │
       ▼             ▼          └─────────────┘
┌─────────────┐ ┌─────────────┐
│Gemini 3.6   │ │   Groq      │
│Flash ($0)   │ │ Fallback($0)│
└─────────────┘ └─────────────┘
```

---

## Pricing Algorithm

### Core Principle: Optimize Contribution Profit

```
Expected_Profit(price) = 
    E[occupied_room_nights | price, context] × net_room_margin
    + E[ancillary_margin]
    - E[incremental_operating_cost]
    - E[displacement_cost]

Where:
net_room_margin = price - OTA_commission - channel_discount - payment_cost - expected_refund
```

### Candidate-Price Optimization

Instead of a black-box model outputting "$157.43":

1. Generate candidates: $109, $119, $129, $139, $149, $159, $169
2. For each candidate:
   - Forecast bookings (demand curve)
   - Apply cancellation/no-show probability
   - Estimate channel mix
   - Deduct: commission, payment, cleaning costs
   - Estimate displacement value
   - Check legal/channel constraints
3. Select: argmax(expected_contribution_profit)
4. Explain: "Recommend $149 because..."

### Signal Weights

| Signal | Weight | Source |
|--------|--------|--------|
| Occupancy Level | 25% | Owner input / Beds24 |
| Competitor Rates | 25% | Web scraping |
| Events | 20% | Ticketmaster + local |
| Day of Week | 15% | Historical patterns |
| Lead Time | 10% | Days until check-in |
| Learned Factor | 5% | Owner feedback |

### Pricing Schedule

- **Morning (6:00 AM):** Full analysis, next 90 days
- **Evening (4:00 PM):** Tonight/tomorrow adjustments
- **Event-triggered:** Large booking/cancellation, competitor compression

---

## User Workflows

### Onboarding (6 Steps)

1. Sign Up
2. Property Details (name, address, rooms)
3. Room Types (categories, base rates)
4. Set Guardrails (floor/ceiling per room type)
5. Connect Integration (Beds24 API or Manual)
6. Launch Dashboard

### Daily Operation

```
Morning:
  Agent scrapes overnight data
  → Analyzes demand
  → Generates recommendations
  → Owner reviews (30 sec)
  → Owner accepts/rejects/modifies
  → Rate applied (auto via Beds24 or manual)

Evening:
  Agent checks same-day/next-day
  → Adjusts if significant change
```

### Weekly Check-in

Owner inputs actual results:
- Total rooms sold
- Total room revenue
- (Optional) ADR, occupancy

Agent:
- Compares predicted vs actual
- Updates learned factors
- Generates weekly learning report

### Monthly Review

Agent generates:
- Before/After comparison
- Revenue attribution (Atiya-driven uplift)
- ROI calculation
- Next month's goal suggestion

---

## Integration Options

### Option A: Manual (Any PMS)

Owner enters data weekly, applies rates manually.

### Option B: Beds24 API

```
Beds24 API
    │
    ├── GET /bookings    → Reservations, history
    ├── GET /inventory   → Rooms available
    ├── GET /prices      → Current rates
    │
    └── PUT /prices      → Push new rates
                              │
                              ▼
                         OTAs updated
```

---

## Data Model

### Core Entities

```
Property
  ├── id, name, address, timezone
  ├── floor_rate, ceiling_rate
  └── autonomy_level (manual/semi-auto/autopilot)

RoomType
  ├── property_id, name, count
  └── base_rate, floor, ceiling

Recommendation
  ├── property_id, room_type_id, date
  ├── recommended_price, confidence
  ├── reasoning (JSON)
  ├── status (pending/accepted/rejected/modified)
  └── actual_price_applied

BookingSnapshot
  ├── property_id, snapshot_time, arrival_date
  ├── rooms_on_books, remaining_inventory
  └── pickup_since_last

WeeklyActuals
  ├── property_id, week_start
  ├── rooms_sold, revenue, adr, occupancy
  └── predicted_revpar, actual_revpar

CompetitorQuote
  ├── competitor_id, capture_time, stay_date
  ├── price, available, room_type
  └── source

Event
  ├── name, date, venue, distance_miles
  ├── category (concert/conference/sports/local)
  └── estimated_impact
```

---

## Legal Constraints (Built-In)

1. **Transient Occupancy Tax:** Stored separately, never counted as revenue
2. **Hidden Fee Law (CA SB 478, FTC):** Mandatory fees in advertised price
3. **Emergency Price Gouging (CA Penal 396):** Hard kill switch, max +10%
4. **Antitrust:** Only public competitor data, independent pricing
5. **Channel Parity:** Per actual contract terms

---

## Confidence-Based Escalation

| Confidence | Agent Behavior |
|------------|----------------|
| >85% HIGH | Act autonomously (if autopilot) |
| 60-85% MEDIUM | Recommend with explanation |
| <60% LOW | Present options, ask owner |
| UNCERTAIN | Request more information |

---

## Evaluation Metrics

### Predictive

- MAE/WAPE for occupancy forecast
- Calibration of confidence scores
- Cancellation model accuracy

### Commercial

- Contribution profit (primary)
- RevPAR, ADR, Occupancy
- Recommendation acceptance rate
- Revenue attribution

### Causal

- A/B comparison: accepted vs rejected days
- Before/After comparison
- Event capture vs baseline

---

## Development Phases

| Phase | Weeks | Skills | Focus |
|-------|-------|--------|-------|
| 1 | 1-4 | 1, 11, 12 | Foundation + Model Integration |
| 2 | 5-8 | 13, 14, 16, 17 | Data Collection Agents |
| 3 | 9-12 | 19, 25, 26, 27 | Agentic Pricing Engine |
| 4 | 13-16 | 6, 18, 20 | LLM Integration & Explainability |
| 5 | 17-20 | 2, 3, 15, 28 | Human Loop & Learning |
| 6 | 21-24 | 21, 22, 23, 24 | RAG Knowledge Base |
| 7 | 25-28 | 4, 5, 7, 8, 9, 10 | Production Hardening |

---

## Success Criteria

1. **Owner can onboard in <10 minutes**
2. **Agent explains every recommendation**
3. **Owner spends <30 seconds/day on pricing**
4. **Measurable RevPAR improvement within 30 days**
5. **ROI proof: attributed revenue > cost**
6. **All 28 AI skills learned and documented**
