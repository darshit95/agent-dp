# Atiya - Complete Product Requirements

This document consolidates all product requirements, algorithms, and infrastructure specifications.

---

# Atiya Functional Specification

## 1. Product Overview

### 1.1 Vision
Atiya is an **AI Revenue Manager** for small-medium independent motels that thinks, learns, and collaborates with owners - not a black-box algorithm.

### 1.2 Target Market
- Small to medium independent motels (10-100 rooms)
- Owner-operators with low tech comfort (2/10)
- Currently not using any RMS (90% of independents)

### 1.3 Key Differentiators
| Feature | Competitors | Atiya |
|---------|------------|-------|
| Explainability | Black-box | Plain English reasoning |
| Learning | None | Learns from owner feedback |
| Cold Start | Needs 6+ months data | Works Day 1 |
| Optimization | ADR/RevPAR | Contribution Profit |
| Control | All-or-nothing | Confidence-based |

---

## 2. User Personas

### 2.1 Primary: Sam (Owner-Operator)

**Profile:**
- Role: Owner-operator of 40-room urban motel
- Tech comfort: 2/10 (smartphone OK, complex systems not OK)
- Time available: 30 min/day for pricing
- Current approach: Gut feel + occasional competitor check

**Goals:**
- Increase revenue without becoming a data analyst
- Feel in control of pricing decisions
- Understand WHY a price is recommended
- Prove ROI to justify any software cost

**Pain Points:**
- Overwhelmed by existing RMS complexity
- Doesn't trust black-box algorithms
- No time to analyze competitor data daily
- Missing revenue on event days

---

## 3. User Workflows

### 3.1 Onboarding Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. Sign Up │───▶│ 2. Property │───▶│ 3. Room     │
│             │    │    Details  │    │    Types    │
└─────────────┘    └─────────────┘    └─────────────┘
                                            │
┌─────────────┐    ┌─────────────┐    ┌─────▼───────┐
│ 6. Dashboard│◀───│ 5. Connect  │◀───│ 4. Set      │
│    Launch   │    │   (Beds24   │    │   Guardrails│
│             │    │   or Manual)│    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### Step 1: Sign Up
- Email/password or Google OAuth
- Accept terms of service
- Verify email

#### Step 2: Property Details
- Property name
- Address (for competitor/event detection)
- Timezone
- Total rooms

#### Step 3: Room Types
For each room type:
- Name (e.g., "Standard King", "Double Queen")
- Count available
- Base rate (starting price)
- Description (optional)

#### Step 4: Set Guardrails
For each room type:
- Floor rate (minimum acceptable)
- Ceiling rate (maximum acceptable)

Global settings:
- Maximum daily change (e.g., ±15%)
- Emergency ceiling (auto-set for legal compliance)

#### Step 5: Connect Integration
**Option A: Beds24 API**
- Enter API key and property ID
- Test connection
- Sync historical data (12 months)
- Choose autonomy level (Manual/Semi-Auto/Autopilot)

**Option B: Manual**
- Confirm manual mode
- Schedule weekly check-in reminder

#### Step 6: Dashboard Launch
- View initial competitor analysis
- See first recommendations
- Review KPIs baseline

### 3.2 Daily Operation Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MORNING CYCLE (6:00 AM)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │ Agent    │───▶│ Agent    │───▶│ Agent    │───▶│ Owner    │     │
│  │ scrapes  │    │ analyzes │    │ generates│    │ reviews  │     │
│  │ overnight│    │ demand   │    │ rates    │    │ (30 sec) │     │
│  └──────────┘    └──────────┘    └──────────┘    └─────┬────┘     │
│                                                        │           │
│                                          ┌─────────────▼─────────┐ │
│                                          │ [✓] Accept            │ │
│                                          │ [✗] Reject            │ │
│                                          │ [~] Modify            │ │
│                                          └───────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 Weekly Check-in (Manual Mode)

```
┌─────────────────────────────────────────────────────────────────────┐
│                   WEEKLY CHECK-IN (Every Monday)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  "Help me learn how I'm doing for you!"                             │
│                                                                     │
│  Last Week's Actuals (Aug 1-7):                                     │
│  ─────────────────────────────                                      │
│  Total Rooms Sold:        [  182  ]                                 │
│  Total Room Revenue:      [ $24,570 ]                               │
│  (or) Average Daily Rate: [ $135.00 ]                               │
│                                                                     │
│  Occupancy % (if known):  [  65%  ]                                 │
│                                                                     │
│                              [Submit]                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.4 Monthly Review

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MONTHLY PERFORMANCE REVIEW                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  YOUR RESULTS (Before vs After):                                    │
│  ┌───────────────────┬────────────┬────────────┬──────────┐        │
│  │ Metric            │ Before     │ With Atiya │ Change   │        │
│  ├───────────────────┼────────────┼────────────┼──────────┤        │
│  │ RevPAR            │ $78.50     │ $89.20     │ +13.6%   │        │
│  │ ADR               │ $118.00    │ $127.50    │ +8.1%    │        │
│  │ Occupancy         │ 66.5%      │ 70.0%      │ +3.5pts  │        │
│  │ Revenue           │ $68,950    │ $78,330    │ +$9,380  │        │
│  └───────────────────┴────────────┴────────────┴──────────┘        │
│                                                                     │
│  ATIYA'S VALUE:                                                     │
│  • Additional revenue: +$9,380                                      │
│  • Your Atiya cost: $60                                             │
│  • ROI: 156x return                                                 │
│                                                                     │
│  NEXT MONTH'S GOAL:                                                 │
│  Agent suggests: Target RevPAR $92.00 (+3.1%)                       │
│  [Accept goal]  [Set different goal: $____]                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. UI Mockups

### 4.1 Dashboard (Main Screen)

```
┌─────────────────────────────────────────────────────────────────────┐
│  ATIYA                                    Sam's Motor Lodge  [⚙️]   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  TODAY: August 9, 2026                                        │ │
│  │                                                                │ │
│  │  🟢 Autopilot: ON                         [Turn Off]          │ │
│  │                                                                │ │
│  │  Current Occupancy: 72%  |  ADR: $142  |  RevPAR: $102        │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  📊 PENDING RECOMMENDATIONS                                   │ │
│  │                                                                │ │
│  │  ┌─────────────────────────────────────────────────────────┐  │ │
│  │  │  Tomorrow (Sat, Aug 10) - Standard Room                 │  │ │
│  │  │  ──────────────────────────────────────                 │  │ │
│  │  │  Current: $135  →  Recommended: $159 (+17.8%)           │  │ │
│  │  │                                                          │  │ │
│  │  │  Why: County Fair starts Saturday. 4/6 competitors      │  │ │
│  │  │       sold out. Booking pace +40% above normal.         │  │ │
│  │  │                                                          │  │ │
│  │  │  Confidence: 88% (HIGH)                                  │  │ │
│  │  │                                                          │  │ │
│  │  │  [✓ Accept]  [✗ Reject]  [Modify: $_____]              │  │ │
│  │  └─────────────────────────────────────────────────────────┘  │ │
│  │                                                                │ │
│  │  [View all 14 recommendations →]                              │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  📈 THIS WEEK                                                 │ │
│  │                                                                │ │
│  │  RevPAR: $98.50 (+8.2% vs last week)                         │ │
│  │  Recommendations accepted: 12/14 (86%)                        │ │
│  │  Estimated uplift: +$1,240                                    │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [Dashboard] [Calendar] [Competitors] [Settings] [Help]            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Calendar View

```
┌─────────────────────────────────────────────────────────────────────┐
│  ATIYA > Calendar                                    August 2026    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ◀ July                                              September ▶   │
│                                                                     │
│  ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐                       │
│  │ Sun │ Mon │ Tue │ Wed │ Thu │ Fri │ Sat │                       │
│  ├─────┼─────┼─────┼─────┼─────┼─────┼─────┤                       │
│  │     │     │     │     │     │     │  1  │                       │
│  │     │     │     │     │     │     │$142 │                       │
│  │     │     │     │     │     │     │ 85% │                       │
│  ├─────┼─────┼─────┼─────┼─────┼─────┼─────┤                       │
│  │  2  │  3  │  4  │  5  │  6  │  7  │  8  │                       │
│  │$128 │$115 │$112 │$118 │$125 │$145 │$155 │                       │
│  │ 78% │ 62% │ 58% │ 65% │ 72% │ 88% │ 92% │                       │
│  ├─────┼─────┼─────┼─────┼─────┼─────┼─────┤                       │
│  │  9  │ 10  │ 11  │ 12  │ 13  │ 14  │ 15  │                       │
│  │$138 │$159 │$145 │$142 │$138 │$165 │$175 │                       │
│  │ 72% │ 🎪  │ 🎪  │ 🎪  │ 75% │ 🎵  │ 🎵  │ ← Events detected    │
│  └─────┴─────┴─────┴─────┴─────┴─────┴─────┘                       │
│                                                                     │
│  Legend:                                                            │
│  🎪 County Fair (Aug 10-12)    🎵 Concert at Event Center          │
│  🟢 Above avg rate   🟡 Normal   🔴 Below avg                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.3 Results Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│  ATIYA > Results                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Period: [Last 30 days ▼]  Compare to: [Prior 30 days ▼]           │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  BEFORE vs AFTER                                               │ │
│  │                                                                │ │
│  │   RevPAR         Contribution Profit         Occupancy         │ │
│  │   ████████ $89   ██████████████ $24.5K       ████████ 70%     │ │
│  │   █████    $79   █████████     $18.2K        ██████   66%     │ │
│  │         +13.6%              +34.6%                  +3.5pts    │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  ATIYA-ATTRIBUTED REVENUE                                      │ │
│  │                                                                │ │
│  │  What would have happened: $68,950 (baseline)                  │ │
│  │  What actually happened:   $78,330                             │ │
│  │  ────────────────────────────────────────                      │ │
│  │  ATIYA UPLIFT: +$9,380 (+13.6%)                               │ │
│  │                                                                │ │
│  │  Your cost: $60  |  NET VALUE: +$9,320  |  ROI: 156x          │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  🏆 WIN STORIES                                                │ │
│  │                                                                │ │
│  │  1. County Fair Weekend (Aug 10-12)                            │ │
│  │     • Atiya: +22% price increase                               │ │
│  │     • Result: 98% occupancy, +$2,340 extra revenue             │ │
│  │                                                                │ │
│  │  2. Competitor Compression (Aug 20)                            │ │
│  │     • 4/6 competitors sold out at 4pm                          │ │
│  │     • Atiya raised rates +18% same day                         │ │
│  │     • Captured +$12 ADR on 12 walk-ins                         │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. API Specifications

### 5.1 Internal APIs

#### Recommendations API
```
GET /api/recommendations
  ?property_id=123
  &from_date=2026-08-09
  &to_date=2026-08-23
  
Response:
{
  "recommendations": [
    {
      "id": "rec_abc123",
      "date": "2026-08-10",
      "room_type": "standard",
      "current_rate": 135.00,
      "recommended_rate": 159.00,
      "confidence": 0.88,
      "reasoning": {
        "summary": "County Fair starts Saturday...",
        "factors": [
          {"name": "event", "impact": "+25%", "detail": "County Fair"},
          {"name": "competitors", "impact": "+18%", "detail": "4/6 sold out"},
          {"name": "pace", "impact": "+40%", "detail": "Above normal"}
        ]
      },
      "status": "pending"
    }
  ]
}

POST /api/recommendations/{id}/accept
POST /api/recommendations/{id}/reject
POST /api/recommendations/{id}/modify
  Body: {"applied_rate": 145.00}
```

### 5.2 Beds24 Integration

See `docs/AGENT_DESIGN.md` for full Beds24 API integration details.

---

## 6. Data Models

### 6.1 Core Entities

```python
class Property:
    id: str
    name: str
    address: str
    timezone: str
    total_rooms: int
    floor_rate: Decimal
    ceiling_rate: Decimal
    autonomy_level: Literal["manual", "semi_auto", "autopilot"]
    beds24_api_key: Optional[str]
    beds24_property_id: Optional[str]

class RoomType:
    id: str
    property_id: str
    name: str
    count: int
    base_rate: Decimal
    floor_rate: Decimal
    ceiling_rate: Decimal

class Recommendation:
    id: str
    property_id: str
    room_type_id: str
    date: date
    current_rate: Decimal
    recommended_rate: Decimal
    confidence: float  # 0.0 - 1.0
    reasoning: dict
    status: Literal["pending", "accepted", "rejected", "modified"]
    applied_rate: Optional[Decimal]
    created_at: datetime
    decided_at: Optional[datetime]

class WeeklyActuals:
    id: str
    property_id: str
    week_start: date
    rooms_sold: int
    revenue: Decimal
    adr: Decimal
    occupancy: float
    predicted_revpar: Decimal
    actual_revpar: Decimal
```

---

## 7. Success Metrics

### 7.1 User Adoption
- Onboarding completion rate: >80%
- Daily active users: >60% of registered
- Monthly churn: <5%

### 7.2 Agent Performance
- Recommendation acceptance rate: >70%
- Prediction accuracy (RevPAR): within 10%
- Confidence calibration: 85% confidence = 85% correct

### 7.3 Business Impact
- Average RevPAR improvement: >10%
- Owner-reported satisfaction: >4.5/5
- ROI demonstrated: >10x cost

---

## 8. Non-Functional Requirements

### 8.1 Performance
- Dashboard load: <2 seconds
- Recommendation generation: <30 seconds
- Scraping complete: <5 minutes

### 8.2 Availability
- Uptime: 99%
- Pricing runs: 2x daily guaranteed

### 8.3 Security
- All data encrypted at rest and in transit
- API keys stored securely
- No sensitive guest data collected

### 8.4 Privacy
- Only aggregate booking data used
- No individual guest profiling
- GDPR/CCPA compliant design

---

# Atiya Pricing Algorithm Design

## 1. Core Principle: Optimize Contribution Profit

### 1.1 Why Not ADR or RevPAR?

| Metric | Problem |
|--------|---------|
| **ADR (Average Daily Rate)** | High ADR can mean empty rooms |
| **Occupancy** | High occupancy can mean selling too cheap |
| **RevPAR** | Ignores channel costs, cleaning, commissions |

### 1.2 Contribution Profit Formula

```
Expected_Profit(price) = 
    E[occupied_room_nights | price, context] × net_room_margin
    + E[ancillary_margin]
    - E[incremental_operating_cost]
    - E[displacement_cost]

Where:
    net_room_margin = price 
                    - OTA_commission (15-20%)
                    - payment_cost (2-3%)
                    - expected_refund
```

### 1.3 Why This Matters

**Example 1: Channel Economics**
- OTA booking at $160: Net = $160 × 0.82 = $131.20
- Direct booking at $150: Net = $150 × 0.97 = $145.50
- **Direct wins by $14.30 per room**

**Example 2: Length of Stay**
- Three 1-night stays at $145: Revenue = $435, Cleanings = 3
- One 3-night stay at $135: Revenue = $405, Cleanings = 1
- At $40/cleaning: 3-night stay is **more profitable**

---

## 2. Candidate-Price Optimization

### 2.1 Why Not Black-Box?

Traditional ML: Model outputs "$157.43" → No explanation

Our approach: Generate candidates, score each transparently

### 2.2 The Process

```
┌─────────────────────────────────────────────────────────────────┐
│                CANDIDATE PRICE OPTIMIZATION                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  For arrival date D, room type R:                               │
│                                                                 │
│  1. Generate candidates: $109, $119, $129, $139, $149, $159     │
│                                                                 │
│  2. For each candidate price P:                                 │
│     ┌────────────────────────────────────────────────────────┐  │
│     │ a. Forecast demand at price P (demand curve)           │  │
│     │ b. Apply cancellation/no-show probability              │  │
│     │ c. Estimate channel mix (OTA vs direct %)              │  │
│     │ d. Calculate net room margin                           │  │
│     │ e. Add ancillary margin                                │  │
│     │ f. Subtract: cleaning, amenities                       │  │
│     │ g. Estimate displacement (opportunity cost)            │  │
│     │ h. CHECK: Legal/channel constraints                    │  │
│     │ i. SCORE: Expected contribution profit                 │  │
│     └────────────────────────────────────────────────────────┘  │
│                                                                 │
│  3. Select: argmax(expected_contribution_profit)                │
│                                                                 │
│  4. Output: "$149 recommended (+$84 vs current)"                │
│             with full reasoning                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Candidate Generation

```python
def generate_candidates(base_rate: float, floor: float, ceiling: float) -> list[float]:
    """Generate price candidates within guardrails."""
    step = 5 if base_rate < 100 else 10
    
    candidates = []
    price = floor
    while price <= ceiling:
        candidates.append(price)
        price += step
    
    # Always include current rate and base rate
    if base_rate not in candidates:
        candidates.append(base_rate)
    
    return sorted(set(candidates))
```

---

## 3. Multi-Model Stack

### 3.1 Model Components

| Model | Purpose | Algorithm | Input |
|-------|---------|-----------|-------|
| **Demand Forecast** | Predict room requests | LightGBM | Calendar, pace, events |
| **Booking Curve** | Expected rooms at D-7/14/30 | Historical percentiles | Property history |
| **Cancellation** | P(cancel) per reservation | Logistic regression | Channel, lead time |
| **No-Show** | P(no-show) | Historical rates | Channel, payment |
| **Elasticity** | Price-demand relationship | Causal estimation | Experiments |
| **Displacement** | Opportunity cost | Dynamic programming | Future demand |

### 3.2 Demand Forecast Model

**Features:**
```python
features = [
    # Calendar
    'day_of_week', 'month', 'is_weekend', 'is_holiday',
    
    # Booking pace
    'rooms_on_books_d7', 'rooms_on_books_d14', 'rooms_on_books_d30',
    'pickup_last_24h', 'pickup_last_72h',
    
    # Pace anomaly
    'pickup_vs_historical_percentile',
    
    # Competitors
    'comp_median_rate', 'comp_availability_pct',
    'own_vs_comp_gap',
    
    # Events
    'event_within_10mi', 'event_category', 'event_size',
    
    # Weather
    'forecast_rain_prob', 'forecast_temp',
]
```

### 3.3 Elasticity Estimation

**WARNING: Correlation is NOT causation**

```
WRONG:
  Regress: historical_price vs historical_occupancy
  → Finds "higher prices → more bookings"
  → Why? Hotel raises prices when demand is HIGH

RIGHT:
  1. Run bounded price experiments
  2. Randomly vary prices on matched dates
  3. Measure actual booking response
  4. Estimate true elasticity per segment
```

**Segment-Specific Elasticity:**
- Business travelers: Low elasticity (less price sensitive)
- OTA leisure: High elasticity (very price sensitive)
- Direct leisure: Medium elasticity
- Last-minute: Variable

---

## 4. Input Signals

### 4.1 Signal Weights (Initial)

| Signal | Weight | Source |
|--------|--------|--------|
| Occupancy Level | 25% | Owner / Beds24 |
| Competitor Rates | 25% | Web scraping |
| Events | 20% | Ticketmaster + local |
| Day of Week | 15% | Historical patterns |
| Lead Time | 10% | Days until check-in |
| Learned Factor | 5% | Owner feedback |

### 4.2 Occupancy Factor

```python
def occupancy_factor(current_occupancy: float, forecast_occupancy: float) -> float:
    """
    Adjust price based on occupancy pressure.
    
    Higher occupancy → Higher factor → Higher price
    """
    if forecast_occupancy < 0.50:
        return 0.90  # -10%
    elif forecast_occupancy < 0.65:
        return 0.95  # -5%
    elif forecast_occupancy < 0.75:
        return 1.00  # Base
    elif forecast_occupancy < 0.85:
        return 1.10  # +10%
    elif forecast_occupancy < 0.95:
        return 1.20  # +20%
    else:
        return 1.30  # +30%
```

### 4.3 Competitor Factor

```python
def competitor_factor(
    own_rate: float,
    comp_median: float,
    comp_availability: float
) -> float:
    """
    Adjust based on competitive position.
    
    comp_availability: % of competitors with rooms available
    Lower availability = compression = opportunity to raise
    """
    # Compression factor
    if comp_availability < 0.3:
        compression_boost = 1.15  # Most competitors sold out
    elif comp_availability < 0.5:
        compression_boost = 1.10
    else:
        compression_boost = 1.00
    
    # Position factor
    gap = (comp_median - own_rate) / comp_median
    if gap > 0.15:
        position_factor = 1.10  # We're much cheaper, can raise
    elif gap > 0.05:
        position_factor = 1.05
    elif gap > -0.05:
        position_factor = 1.00
    else:
        position_factor = 0.95  # We're expensive
    
    return compression_boost * position_factor
```

### 4.4 Event Factor

```python
def event_factor(events: list[Event], distance_threshold: float = 25) -> float:
    """
    Adjust based on nearby events.
    
    Uses learned impact coefficients per event category.
    """
    if not events:
        return 1.00
    
    total_impact = 0.0
    for event in events:
        if event.distance_miles <= distance_threshold:
            # Base impact by category (learned over time)
            category_impact = {
                'major_concert': 0.40,
                'conference': 0.30,
                'sports': 0.25,
                'local_fair': 0.12,  # Learned: owner prefers conservative
                'community': 0.05,
            }.get(event.category, 0.10)
            
            # Distance decay
            distance_factor = 1.0 - (event.distance_miles / distance_threshold)
            
            total_impact += category_impact * distance_factor
    
    return 1.0 + min(total_impact, 0.50)  # Cap at +50%
```

---

## 5. Learned Adjustment Factor

### 5.1 What It Captures

```python
Learned_Factor = f(
    acceptance_rate,           # How often owner accepts
    adjustment_patterns,       # How much owner modifies
    outcome_accuracy,          # Predicted vs actual RevPAR
    event_impact_calibration,  # Actual vs predicted event impact
    owner_risk_preference,     # Conservative vs aggressive
)
```

### 5.2 Evolution Over Time

| Week | Factor | What Happened |
|------|--------|---------------|
| 1-2 | 1.00 | Neutral - learning |
| 3-4 | 0.97 | Owner rejected 3 high recommendations |
| 5-8 | 0.95 | Owner consistently applies 5% lower |
| 9-12 | varies | Per-segment: events=0.88, weekends=1.02 |

### 5.3 Implementation

```python
class LearnedAdjustment:
    def __init__(self, property_id: str):
        self.property_id = property_id
        self.history = []
    
    def record(
        self,
        recommended: float,
        applied: float,
        outcome_revpar: float,
        predicted_revpar: float,
        context: dict
    ):
        """Record outcome for learning."""
        self.history.append({
            'recommended': recommended,
            'applied': applied,
            'adjustment': applied / recommended,
            'revpar_error': outcome_revpar - predicted_revpar,
            'context': context,
        })
    
    def get_factor(self, context: dict) -> float:
        """Get learned adjustment factor for context."""
        if len(self.history) < 5:
            return 1.0  # Not enough data
        
        # Calculate average adjustment for similar contexts
        similar = [h for h in self.history if self._similar(h['context'], context)]
        
        if len(similar) < 3:
            return self._global_factor()
        
        return sum(h['adjustment'] for h in similar) / len(similar)
```

---

## 6. Legal Constraints

### 6.1 Built Into Engine

```python
def apply_legal_constraints(
    recommended: float,
    property: Property,
    date: date
) -> tuple[float, list[str]]:
    """
    Apply legal constraints BEFORE returning recommendation.
    Returns (constrained_price, applied_constraints).
    """
    constraints_applied = []
    price = recommended
    
    # 1. Floor/Ceiling (owner-set)
    if price < property.floor_rate:
        price = property.floor_rate
        constraints_applied.append('floor_rate')
    if price > property.ceiling_rate:
        price = property.ceiling_rate
        constraints_applied.append('ceiling_rate')
    
    # 2. Emergency Price Gouging (CA Penal 396)
    if is_emergency_declared(property.state, date):
        pre_emergency_rate = get_pre_emergency_rate(property)
        emergency_ceiling = pre_emergency_rate * 1.10  # Max +10%
        if price > emergency_ceiling:
            price = emergency_ceiling
            constraints_applied.append('emergency_ceiling')
    
    # 3. Maximum Daily Change
    current_rate = get_current_rate(property, date)
    max_change = current_rate * property.max_daily_change_pct
    if abs(price - current_rate) > max_change:
        if price > current_rate:
            price = current_rate + max_change
        else:
            price = current_rate - max_change
        constraints_applied.append('max_daily_change')
    
    return price, constraints_applied
```

### 6.2 Constraint Summary

| Constraint | Rule | Implementation |
|------------|------|----------------|
| **Floor Rate** | Never go below owner's minimum | Hard cap |
| **Ceiling Rate** | Never exceed owner's maximum | Hard cap |
| **Emergency Ceiling** | +10% max during emergencies | Kill switch |
| **Max Daily Change** | Prevent jarring swings | ±15% default |
| **Channel Parity** | Per actual contract | Config-driven |

---

## 7. Confidence Scoring

### 7.1 Factors

```python
def calculate_confidence(
    data_quality: float,
    model_certainty: float,
    historical_accuracy: float,
    constraint_headroom: float
) -> float:
    """
    Calculate confidence in recommendation.
    
    Returns 0.0 - 1.0 mapped to:
    - > 0.85: HIGH - can act autonomously
    - 0.60-0.85: MEDIUM - recommend with explanation
    - < 0.60: LOW - ask owner
    """
    return (
        0.30 * data_quality +
        0.30 * model_certainty +
        0.25 * historical_accuracy +
        0.15 * constraint_headroom
    )
```

### 7.2 Data Quality Score

```python
def data_quality_score(date: date, property: Property) -> float:
    """Score based on data completeness."""
    score = 1.0
    
    # Competitor data freshness
    if comp_data_age_hours > 24:
        score -= 0.2
    
    # Event data available
    if not events_checked_today:
        score -= 0.1
    
    # Historical data depth
    if historical_days < 90:
        score -= 0.2
    
    # Weather forecast available
    if not weather_forecast_available:
        score -= 0.05
    
    return max(0.0, score)
```

---

## 8. Cold Start Strategy

### 8.1 Phase Progression

| Phase | Weeks | Approach | Behavior |
|-------|-------|----------|----------|
| **Bootstrap** | 1-2 | Rules only | Conservative, asks often |
| **Learning** | 3-4 | Rules + observation | Calibrates confidence |
| **Adaptive** | 5-8 | Rules + ML | Adjusts weights |
| **Optimizing** | 9+ | Full ML | Contextual bandits |

### 8.2 Bootstrap (No History)

When property has no history:
1. Set rates based on competitor median
2. Use regional demand patterns
3. Apply conservative event factors
4. Ask for owner confirmation on everything
5. Learn from outcomes

---

## 9. Explanation Generation

### 9.1 Structure

```python
def generate_explanation(
    recommendation: Recommendation,
    factors: list[Factor],
    constraints: list[str]
) -> str:
    """
    Generate human-readable explanation.
    
    Example output:
    "I recommend $154, up from $139.
    
    Why:
    • Net occupancy forecast: 82%
    • D-7 pickup: 91st percentile for Thursdays
    • 2/6 competitors unavailable (compression)
    • Comp-set median: $169 (we're 9% below)
    • County Fair active (+15% historical impact)
    
    Confidence: 82% (HIGH)
    
    Constraints passed:
    ✓ Above floor ($95)
    ✓ Below ceiling ($199)
    ✓ Within daily change limit"
    """
```

### 9.2 Factor Ranking

Show factors by contribution, highest first:
1. Event impact (if present)
2. Competitor compression
3. Booking pace anomaly
4. Occupancy forecast
5. Day of week pattern

---

## 10. Implementation Plan

### 10.1 Phase 1: Rule-Based MVP

```python
# Simple multiplicative formula
price = (
    base_rate
    * occupancy_factor(occupancy)
    * competitor_factor(comp_median, comp_availability)
    * event_factor(events)
    * day_of_week_factor(dow)
    * learned_factor
)
price = apply_legal_constraints(price)
```

### 10.2 Phase 2: ML Demand Model

- Train LightGBM on historical bookings
- Features: calendar, pace, events, weather
- Predict occupancy at each candidate price

### 10.3 Phase 3: Elasticity Estimation

- Run bounded price experiments
- Estimate segment-specific elasticity
- Build demand curves

### 10.4 Phase 4: Contextual Bandits

- Explore/exploit for price discovery
- Learn optimal prices per context
- Thompson sampling or UCB

---

# Atiya Infrastructure & Cost Analysis

## 1. Architecture Overview

### 1.1 Production Stack

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
            │  │        FREE            │  │
            │  └───────────┬────────────┘  │
            │              │               │
            │  ┌───────────▼────────────┐  │
            │  │   Docker Environment   │  │
            │  │                        │  │
            │  │  ┌──────────────────┐  │  │
            │  │  │  Streamlit UI    │  │  │
            │  │  │  (Dashboard)     │  │  │
            │  │  └────────┬─────────┘  │  │
            │  │           │            │  │
            │  │  ┌────────▼─────────┐  │  │
            │  │  │  FastAPI Backend │  │  │
            │  │  │  + CrewAI/       │  │  │
            │  │  │    LangGraph     │  │  │
            │  │  │  (Multi-Agent)   │  │  │
            │  │  └────────┬─────────┘  │  │
            │  │           │            │  │
            │  │  ┌────────▼─────────┐  │  │
            │  │  │   PostgreSQL +   │  │  │
            │  │  │   pgvector       │  │  │
            │  │  │   (Database)     │  │  │
            │  │  └─────────────────┘  │  │
            │  └────────────────────────┘  │
            └──────────────┬───────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │   LiteLLM   │          │  Free APIs  │
       │   Gateway   │          │             │
       └──────┬──────┘          │ • NWS       │
              │                 │ • Ticketmaster│
       ┌──────┴──────┐          │ • Google    │
       ▼             ▼          └─────────────┘
┌─────────────┐ ┌─────────────┐
│Gemini 3.6   │ │   Groq      │
│Flash        │ │ (Fallback)  │
│  PRIMARY    │ │             │
│    $0       │ │    $0       │
└─────────────┘ └─────────────┘
```

---

## 2. Component Breakdown

### 2.1 Compute & Storage

| Component | Choice | Specification | Cost |
|-----------|--------|---------------|------|
| **Server** | Oracle Cloud VM.Standard.A1.Flex | 4 OCPUs (ARM), 24GB RAM | $0 |
| **Storage** | Oracle Block Volume | 200GB SSD | $0 |
| **Network** | Oracle Cloud | 10TB/month outbound | $0 |
| **OS** | Ubuntu 24.04 LTS | ARM64 | $0 |

### 2.2 Software Stack

| Component | Choice | Purpose | Cost |
|-----------|--------|---------|------|
| **Agent Orchestration** | CrewAI or LangGraph (OSS) | Multi-agent coordination, state management | $0 |
| **Backend API** | FastAPI (Python) | REST API, async processing, job scheduling | $0 |
| **Database** | PostgreSQL 16 + pgvector (Docker) | Persistence, vector storage | $0 |
| **Web UI** | Streamlit (Docker) | Owner-facing dashboard | $0 |
| **Reverse Proxy** | Nginx | Route to services | $0 |

### 2.3 AI/ML Services

| Service | Choice | Tier | Limit | Cost |
|---------|--------|------|-------|------|
| **LLM (Primary)** | Gemini 3.6 Flash | Free | ~1500 req/day | $0 |
| **LLM (Fallback)** | Groq | Free | 30 req/min | $0 |
| **LLM Abstraction** | LiteLLM | OSS | Unlimited | $0 |
| **Embeddings** | Gemini Embedding | Free | ~1500 req/day | $0 |
| **Vector DB** | FAISS or pgvector | OSS | In-memory | $0 |

### 2.4 External APIs

| API | Provider | Free Tier | Use Case |
|-----|----------|-----------|----------|
| **Weather** | NWS API | Unlimited | Weather forecast |
| **Events** | Ticketmaster Discovery | 5,000 req/day | Concert/event detection |
| **Maps** | Google Places | $200 credit/mo | Competitor lookup |
| **DNS/SSL** | Cloudflare | Free tier | SSL certificates |

---

## 3. Oracle Cloud Free Tier Details

### 3.1 Always Free Resources

Oracle Cloud provides ARM-based instances permanently free:

| Resource | Specification | Notes |
|----------|---------------|-------|
| **vCPUs** | 4 OCPUs total | Can split across VMs |
| **RAM** | 24GB total | Can split across VMs |
| **Block Storage** | 200GB total | Boot + data volumes |
| **Object Storage** | 10GB | For backups |
| **Network** | 10TB/month egress | Plenty for our use |

### 3.2 Recommended Configuration

**Single VM Setup:**
```
VM: VM.Standard.A1.Flex
├── 4 OCPU (ARM Ampere)
├── 24GB RAM
├── 100GB Boot Volume
└── 100GB Data Volume (PostgreSQL)
```

**Docker Memory Allocation:**
```
FastAPI + CrewAI/LangGraph:  6GB RAM
PostgreSQL + pgvector:       4GB RAM
Streamlit:                   2GB RAM
System buffers:              12GB RAM
```

### 3.3 Account Setup Gotchas

```
⚠️ IMPORTANT: Oracle Cloud requires credit card for verification
   but will NOT charge unless you upgrade.

⚠️ ARM instances (Always Free) may have limited availability.
   If unavailable, wait and retry or select different region.

⚠️ Enable MFA immediately - Oracle locks accounts without it.

⚠️ Set budget alert at $0.01 to catch any unexpected charges.
```

---

## 4. LLM Cost Analysis

### 4.1 Gemini 3.6 Flash (Primary)

**Free Tier Limits:**
- ~1,500 requests/day
- 4 million tokens/minute
- No cost until limits exceeded

**Our Usage Estimate (10 motels):**
```
Per motel per day:
├── Morning pricing run:    ~20 requests
├── Evening pricing run:    ~15 requests
├── Event investigation:    ~5 requests
├── Owner chat queries:     ~5 requests
└── Total:                  ~45 requests/motel/day

10 motels × 45 requests = 450 requests/day
Free tier: 1,500 requests/day
Headroom: 3.3x
```

### 4.2 Groq (Fallback)

**Free Tier Limits:**
- 30 requests/minute
- Excellent latency
- Falls back when Gemini rate-limited

**Usage Pattern:**
```
Normal operation: 0 Groq requests (Gemini handles all)
Rate-limited:     Groq handles overflow
Emergency:        Full Groq fallback
```

### 4.3 Cost Protection Strategy

```python
# llm/gateway.py - $0 guarantee logic

class LLMGateway:
    def get_completion(self, messages, task_type="general"):
        # Check Gemini quota
        if self.gemini_quota_available():
            try:
                return self.call_gemini(messages)
            except RateLimitError:
                pass
        
        # Check Groq quota
        if self.groq_quota_available():
            try:
                return self.call_groq(messages)
            except RateLimitError:
                pass
        
        # Graceful degradation - NEVER auto-enable paid tier
        return {
            "error": "Service busy, try again in a few minutes",
            "retry_after": 300
        }
```

---

## 5. Free Data Sources

### 5.1 Priority 1: Essential (Free, Reliable)

| Source | Data | API | Daily Limit |
|--------|------|-----|-------------|
| **NWS API** | Weather forecast, alerts | REST | Unlimited |
| **Ticketmaster** | Events, concerts | REST | 5,000/day |
| **Google Business** | Competitor rates | Scrape | Careful |

### 5.2 Priority 2: Valuable (Free, Moderate Effort)

| Source | Data | Method | Notes |
|--------|------|--------|-------|
| **Booking.com** | Competitor prices | Scrape | Rate limit carefully |
| **Expedia** | Competitor prices | Scrape | Use proxy rotation |
| **Local CVB sites** | Local events | Scrape | Per-city custom |

### 5.3 Priority 3: Nice-to-Have (Free, Low Priority)

| Source | Data | Method |
|--------|------|--------|
| **Facebook Events** | Local happenings | Scrape |
| **State labor data** | Economic trends | Download |
| **Google Trends** | Search interest | API |

### 5.4 Skip (Expensive)

| Source | Why Skip |
|--------|----------|
| **STR/CoStar** | $$$$ market data |
| **AirDNA** | $$$$ vacation rental analytics |
| **Mews/Cloudbeds** | Requires paid partnership |

---

## 6. Monthly Cost Projections

### 6.1 Phase 1: MVP (0-50 motels)

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 1: MVP                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Infrastructure                                             │
│  ├── Oracle Cloud VM:         $0                            │
│  ├── Cloudflare DNS/SSL:      $0                            │
│  └── Domain:                  ~$12/year (~$1/mo)            │
│                                                             │
│  AI Services                                                │
│  ├── Gemini 3.6 Flash:        $0 (within free tier)         │
│  ├── Groq:                    $0 (fallback only)            │
│  └── Embeddings:              $0 (within free tier)         │
│                                                             │
│  External APIs                                              │
│  ├── NWS Weather:             $0                            │
│  ├── Ticketmaster:            $0                            │
│  └── Web scraping:            $0 (rotating free proxies)    │
│                                                             │
│  ─────────────────────────────────────────────              │
│  TOTAL:                       $1/month                      │
│                                                             │
│  Max motels at this tier:     ~50                           │
│  Revenue at 50 motels:        $3,750/month                  │
│  (50 motels × avg 25 rooms × $3/room)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Phase 2: Growth (50-200 motels)

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 2: GROWTH                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Infrastructure                                             │
│  ├── Oracle Cloud (stay free):  $0                          │
│  ├── Backup instance:           $20/mo (optional)           │
│  └── Domain + extras:           $3/mo                       │
│                                                             │
│  AI Services (upgrade for volume)                           │
│  ├── Gemini Pro (paid):         $20-50/mo                   │
│  └── Embeddings (paid):         $10/mo                      │
│                                                             │
│  Monitoring                                                 │
│  ├── Sentry (error tracking):   $0 (free tier)              │
│  └── Grafana Cloud:             $0 (free tier)              │
│                                                             │
│  ─────────────────────────────────────────────              │
│  TOTAL:                         $53-83/month                │
│                                                             │
│  Max motels at this tier:       ~200                        │
│  Revenue at 200 motels:         $15,000/month               │
│  Margin:                        99%+                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Phase 3: Scale (200+ motels)

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 3: SCALE                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Infrastructure                                             │
│  ├── Cloud servers (multi-region):  $100-200/mo             │
│  ├── Managed PostgreSQL:            $50/mo                  │
│  ├── Load balancer:                 $20/mo                  │
│  └── CDN/caching:                   $20/mo                  │
│                                                             │
│  AI Services                                                │
│  ├── Gemini Enterprise:             $100-200/mo             │
│  └── Dedicated embeddings:          $30/mo                  │
│                                                             │
│  Operations                                                 │
│  ├── Monitoring stack:              $50/mo                  │
│  └── Support tools:                 $30/mo                  │
│                                                             │
│  ─────────────────────────────────────────────              │
│  TOTAL:                             $400-600/month          │
│                                                             │
│  Max motels at this tier:           ~1000                   │
│  Revenue at 1000 motels:            $75,000/month           │
│  Margin:                            99%+                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Setup Instructions

### 7.1 Oracle Cloud VM Setup

```bash
# 1. Create Oracle Cloud account
# https://cloud.oracle.com/
# Requires credit card (verification only, $0 charged)

# 2. Create VM instance
# - Shape: VM.Standard.A1.Flex
# - OCPU: 4 (max free)
# - Memory: 24GB (max free)
# - OS: Ubuntu 24.04 (aarch64)
# - Boot volume: 100GB
# - Add SSH key

# 3. Configure security list
# Ingress rules:
# - TCP 22 (SSH)
# - TCP 80 (HTTP)
# - TCP 443 (HTTPS)
# - TCP 8000 (FastAPI, internal only)
# - TCP 8501 (Streamlit, internal only)

# 4. SSH into VM
ssh ubuntu@<your-vm-ip>

# 5. Install Docker
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
newgrp docker

# 6. Verify installation
docker --version
docker compose version
```

### 7.2 Docker Compose Configuration

```yaml
# docker-compose.yml

services:
  postgres:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_DB: atiya
      POSTGRES_USER: atiya
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U atiya"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build: ./backend
    restart: unless-stopped
    ports:
      - "127.0.0.1:8000:8000"
    environment:
      - DATABASE_URL=postgresql://atiya:${DB_PASSWORD}@postgres:5432/atiya
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - AGENT_FRAMEWORK=${AGENT_FRAMEWORK:-crewai}  # or langraph
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  streamlit:
    build: ./dashboard
    restart: unless-stopped
    ports:
      - "127.0.0.1:8501:8501"
    environment:
      - DATABASE_URL=postgresql://atiya:${DB_PASSWORD}@postgres:5432/atiya
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./app:/app
    depends_on:
      - postgres

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
      - streamlit

volumes:
  pg_data:
```

### 7.3 Nginx Configuration

```nginx
# nginx/nginx.conf

events {
    worker_connections 1024;
}

http {
    # Main dashboard
    server {
        listen 80;
        server_name atiya.yourdomain.com;
        
        location / {
            proxy_pass http://streamlit:8501;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
    
    # API backend (internal)
    server {
        listen 80;
        server_name api.atiya.yourdomain.com;
        
        location / {
            proxy_pass http://api:8000;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

### 7.4 Cloudflare Setup

```
1. Add your domain to Cloudflare (free plan)

2. Update DNS records:
   A    atiya       → <Oracle VM IP>
   A    api.atiya   → <Oracle VM IP>

3. SSL/TLS settings:
   - Mode: Full (strict)
   - Generate Origin Certificate
   - Download and install on VM

4. Security settings:
   - Enable "Always Use HTTPS"
   - Enable Bot Fight Mode (free)
```

---

## 8. Multi-Agent Orchestration Architecture

### 8.1 Agent Framework Choice (Phase 3)

During Week 11-16, implement in **both** frameworks and choose the best:

**CrewAI Approach:**
- Role-based agent definition
- Sequential, hierarchical, or consensual processes
- Built-in memory system
- Simple configuration

**LangGraph Approach:**
- Explicit state machine
- Conditional routing and loops
- Full control over data flow
- Time-travel debugging

**Decision criteria:** Ease of debugging, state visibility, production stability

### 8.2 Morning Pricing Workflow (Multi-Agent)

```
┌─────────────────────────────────────────────────────────────┐
│  MULTI-AGENT WORKFLOW: Morning Pricing Run (6:00 AM)       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [FastAPI Cron Job: 0 6 * * *]                              │
│           │                                                 │
│           ▼                                                 │
│  [Orchestrator Agent]                                       │
│           │                                                 │
│           ├──> [Market Intel Agent]                         │
│           │    ├─> Scrape competitors                       │
│           │    ├─> Fetch local events                       │
│           │    └─> Get weather forecast                     │
│           │         │                                       │
│           │         ▼                                       │
│           │    [Return: market_data dict]                   │
│           │                                                 │
│           ├──> [Demand Analyst Agent]                       │
│           │    ├─> Form demand hypotheses                   │
│           │    ├─> Analyze occupancy trends                 │
│           │    └─> Test hypotheses vs evidence              │
│           │         │                                       │
│           │         ▼                                       │
│           │    [Return: demand_forecast dict]               │
│           │                                                 │
│           ├──> [Pricing Strategist Agent]                   │
│           │    ├─> Generate candidate prices                │
│           │    ├─> Calculate contribution profit            │
│           │    ├─> Apply guardrails                         │
│           │    └─> Confidence scoring                       │
│           │         │                                       │
│           │         ▼                                       │
│           │    [Return: recommendation dict]                │
│           │                                                 │
│           ▼                                                 │
│  [Orchestrator: Synthesize]                                 │
│           │                                                 │
│           ▼                                                 │
│  [Store in PostgreSQL]                                      │
│           │                                                 │
│           ▼                                                 │
│  [Notify Owner if confidence < 0.8]                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.3 Hypothesis-Driven Investigation (Agentic Loop)

```
┌─────────────────────────────────────────────────────────────┐
│  AGENTIC LOOP: Demand Investigation                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [State: PricingState(TypedDict)]                           │
│   ├─ property_id                                           │
│   ├─ market_data                                           │
│   ├─ hypothesis                                            │
│   ├─ evidence                                              │
│   ├─ confidence                                            │
│   └─ recommendation                                        │
│                                                             │
│  ┌────────────────────────────────────────────┐            │
│  │  FORM HYPOTHESIS                           │            │
│  │  (Demand Analyst Agent)                    │            │
│  └───────────────┬────────────────────────────┘            │
│                  │                                         │
│                  ▼                                         │
│  ┌────────────────────────────────────────────┐            │
│  │  INVESTIGATE                               │            │
│  │  (Market Intel Agent)                      │            │
│  │  - Check competitors                       │            │
│  │  - Look for events                         │            │
│  │  - Analyze weather impact                  │            │
│  └───────────────┬────────────────────────────┘            │
│                  │                                         │
│                  ▼                                         │
│  ┌────────────────────────────────────────────┐            │
│  │  ANALYZE EVIDENCE                          │            │
│  │  (Demand Analyst Agent)                    │            │
│  │  - Classify: CONFIRMED/REFUTED/INCONCLUSIVE│            │
│  │  - Update confidence score                 │            │
│  └───────────────┬────────────────────────────┘            │
│                  │                                         │
│           ┌──────┴──────┐                                  │
│           ▼             ▼                                  │
│      [Confidence   [Confidence                             │
│       >= 0.8]      < 0.8]                                  │
│           │             │                                  │
│           ▼             ▼                                  │
│      [Generate]   [Loop: Form                              │
│      Recommendation  Next Hypothesis]                      │
│           │             │                                  │
│           │             └──────┐                           │
│           │                    │                           │
│           ▼                    ▼                           │
│      [Return Final    [Max 5 iterations]                   │
│       Recommendation]      │                               │
│                            ▼                               │
│                       [Human Escalation]                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.4 Agent State Persistence

**All agent state stored in PostgreSQL:**
```sql
-- Agent execution state
CREATE TABLE agent_runs (
    run_id UUID PRIMARY KEY,
    property_id INT,
    agent_type VARCHAR(50),  -- 'orchestrator', 'market_intel', etc.
    state JSONB,             -- Full agent state
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Investigation history
CREATE TABLE hypothesis_investigations (
    id UUID PRIMARY KEY,
    run_id UUID REFERENCES agent_runs(run_id),
    hypothesis TEXT,
    evidence JSONB,
    confidence FLOAT,
    outcome VARCHAR(20)      -- 'CONFIRMED', 'REFUTED', etc.
);
```

---

## 9. Monitoring & Maintenance

### 9.1 Free Monitoring Stack

| Tool | Purpose | Cost |
|------|---------|------|
| **FastAPI Logging** | Agent execution logs | $0 |
| **Grafana Cloud** | Metrics dashboards | $0 (free tier) |
| **Sentry** | Error tracking | $0 (free tier) |
| **Uptime Robot** | Availability monitoring | $0 (free tier) |

### 9.2 Key Metrics to Monitor

```
┌─────────────────────────────────────────────────────────────┐
│  CRITICAL METRICS                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  System Health                                              │
│  ├── CPU usage (stay under 70%)                             │
│  ├── Memory usage (stay under 80%)                          │
│  ├── Disk usage (stay under 80%)                            │
│  └── Workflow success rate (target 99%)                     │
│                                                             │
│  LLM Quotas                                                 │
│  ├── Gemini daily requests (track against 1500 limit)       │
│  ├── Groq fallback count (should be near 0)                 │
│  └── "Service busy" responses (should be 0)                 │
│                                                             │
│  Business Metrics                                           │
│  ├── Active properties                                      │
│  ├── Recommendation acceptance rate                         │
│  ├── Average confidence score                               │
│  └── Owner engagement (logins, actions)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 Maintenance Tasks

**Daily:**
- Check agent execution logs (FastAPI)
- Monitor LLM quota usage

**Weekly:**
- Review error logs
- Check scraper health
- Backup PostgreSQL

**Monthly:**
- Update Docker images
- Review cost projections
- Optimize slow queries

---

## 10. Scaling Triggers

### 10.1 When to Upgrade

| Signal | Threshold | Action |
|--------|-----------|--------|
| **LLM quota** | >80% daily usage | Upgrade Gemini tier |
| **CPU sustained** | >80% for 1 hour | Add Oracle instance |
| **Memory** | >90% usage | Optimize or add RAM |
| **Response time** | >5s average | Add caching layer |
| **Motels** | >100 properties | Consider dedicated DB |

### 10.2 Horizontal Scaling Path

```
Phase 1 (MVP):
  Single Oracle VM → All services

Phase 2 (Growth):
  Oracle VM 1 → FastAPI + Streamlit
  Oracle VM 2 → PostgreSQL (dedicated)

Phase 3 (Scale):
  Region 1 → Full stack (US West)
  Region 2 → Full stack (US East)
  Load balancer → Route by location
```

---

## 11. Backup Strategy

### 11.1 PostgreSQL Backups

```bash
# Daily backup script (cron)
#!/bin/bash

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d)

# Dump database
docker exec postgres pg_dump -U atiya atiya > $BACKUP_DIR/atiya_$DATE.sql

# Compress
gzip $BACKUP_DIR/atiya_$DATE.sql

# Upload to Oracle Object Storage (free 10GB)
oci os object put \
  --bucket-name atiya-backups \
  --file $BACKUP_DIR/atiya_$DATE.sql.gz

# Keep only last 7 days locally
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

### 11.2 Agent Code Backups

```bash
# Backup agent code and configuration weekly
tar -czf /backup/atiya-backend-$(date +%Y%m%d).tar.gz \
  ./backend \
  .env \
  docker-compose.yml
```

---

## 12. Security Checklist

```
[ ] Oracle Cloud MFA enabled
[ ] SSH key-only authentication
[ ] Firewall rules restrict ports
[ ] Database not exposed to internet
[ ] API keys in environment variables
[ ] Cloudflare SSL enforced
[ ] FastAPI endpoints behind auth
[ ] Regular security updates
[ ] Backup encryption enabled
[ ] Audit logging enabled
[ ] Agent LLM calls logged for security review
[ ] Prompt injection testing in CI
```
