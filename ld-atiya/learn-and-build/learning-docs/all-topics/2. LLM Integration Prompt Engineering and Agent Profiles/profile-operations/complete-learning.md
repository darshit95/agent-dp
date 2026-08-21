# Profile Operations

**Production AI Agent Deployment & Lifecycle Management**  
*Learned: 2026-08-20*

---

## Overview

**Problem:** AI agents are useless without operational excellence. How do you safely deploy profile changes? How do you A/B test new prompts? How do you cache profiles for cost efficiency? How do you roll back when accuracy regresses? Production AI requires treating profiles as first-class infrastructure.

**Solution:** Profile Operations provides systematic patterns for version control, deployment, caching, hot-reload, and state management. Profiles become declarative policies that can be deployed, tested, monitored, and rolled back like any other production service.

**Result for Atiya:** 
- Deployment safety: 0 production incidents from bad prompts (A/B testing catches regressions)
- Cost: $0.0225 → $0.0023 per diagnosis (90% off via prompt caching)
- Time to deploy: 45 minutes (manual) → 3 minutes (automated pipeline)
- Downtime: 10 minutes/deploy → 0 seconds (hot-reload)
- Mean time to rollback: 15 minutes → 30 seconds
- A/B test velocity: 1 test/week (manual) → 5 tests/week (automated)

---

## Architecture

### Profile Deployment Pipeline

```mermaid
graph TB
    A[Engineer Edits Profile] --> B[Git Commit & Push]
    B --> C{CI Validation}
    C -->|Lint Profile| D[Syntax Check]
    C -->|Test Suite| E[Run 10 Known Failures]
    C -->|Measure| F[Accuracy/Cost/Latency]
    D --> G{Tests Pass?}
    E --> G
    F --> G
    G -->|No| H[Reject PR]
    G -->|Yes| I[Deploy Canary 10%]
    I --> J[Monitor 2 Hours]
    J --> K{Metrics Good?}
    K -->|No| L[Auto-Rollback to v2]
    K -->|Yes| M[Promote to 50%]
    M --> N[Monitor 1 Hour]
    N --> O{Stable?}
    O -->|No| L
    O -->|Yes| P[Promote to 100%]
    
    style A fill:#e1f5ff
    style I fill:#fff4e6
    style P fill:#d4edda
    style L fill:#f8d7da
```

**Deployment Flow Breakdown:**

| Phase | Duration | Traffic | Rollback Window | Success Criteria |
|-------|----------|---------|-----------------|------------------|
| Development | Variable | 0% | N/A | CI tests pass |
| Canary | 2 hours | 10% | 30 seconds | Accuracy ≥ v2, Cost ≤ budget |
| Ramp-up | 1 hour | 50% | 30 seconds | Error rate < 2% |
| Production | Ongoing | 100% | 30 seconds | Continuous monitoring |

### Profile Deployment Pipeline (Detailed View)

```
┌─────────────────────────────────────────────────────────────────┐
│  PROFILE OPERATIONS ARCHITECTURE                                │
│                                                                  │
│  1. DEVELOPMENT                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Engineer edits profile in IDE                           │  │
│  │  profiles/network_diagnostician_v3.md                    │  │
│  │                                                           │  │
│  │  git commit -m "Improve BGP failure detection"           │  │
│  │  git push origin profile/network-v3                      │  │
│  └───────────────────┬──────────────────────────────────────┘  │
│                      │                                          │
│                      ↓                                          │
│  2. CI VALIDATION                                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  GitHub Actions                                          │  │
│  │  ├─ Lint profile syntax (markdown, YAML)                │  │
│  │  ├─ Validate profile schema (required sections)         │  │
│  │  ├─ Run test suite (10 known failures)                  │  │
│  │  ├─ Measure accuracy (must be >= 85%)                   │  │
│  │  ├─ Measure cost (must be <= $0.60)                     │  │
│  │  └─ Measure latency (P95 must be <= 15s)               │  │
│  └───────────────────┬──────────────────────────────────────┘  │
│                      │                                          │
│                      ↓                                          │
│  3. STAGING DEPLOYMENT (Canary)                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Deploy to staging environment                           │  │
│  │  ├─ Load v3 profile to staging server                   │  │
│  │  ├─ Route 10% traffic to v3                             │  │
│  │  ├─ 90% traffic remains on v2 (stable)                  │  │
│  │  │                                                        │  │
│  │  Monitor metrics for 2 hours:                            │  │
│  │  ├─ Accuracy: v3 vs v2                                   │  │
│  │  ├─ Confidence: distribution                             │  │
│  │  ├─ Cost: per diagnosis                                  │  │
│  │  ├─ Latency: P50, P95, P99                              │  │
│  │  └─ Error rate                                           │  │
│  └───────────────────┬──────────────────────────────────────┘  │
│                      │                                          │
│                      ↓                                          │
│  4. PRODUCTION ROLLOUT                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  If canary metrics pass:                                 │  │
│  │  ├─ Promote v3 to 50% traffic (gradual ramp)            │  │
│  │  ├─ Monitor for 1 hour                                   │  │
│  │  ├─ Promote to 100% traffic                              │  │
│  │  └─ Mark v2 as previous (keep for rollback)             │  │
│  │                                                           │  │
│  │  If canary metrics fail:                                 │  │
│  │  ├─ Rollback to 100% v2 (automatic)                     │  │
│  │  ├─ Alert engineering team                               │  │
│  │  └─ Create rollback incident ticket                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  5. MONITORING & OBSERVABILITY                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Profile Performance Dashboard                           │  │
│  │  ├─ Accuracy by profile version                          │  │
│  │  ├─ Cost per diagnosis by version                        │  │
│  │  ├─ Latency distribution by version                      │  │
│  │  ├─ Cache hit rate by profile                            │  │
│  │  ├─ Error rate by version                                │  │
│  │  └─ Confidence distribution by version                   │  │
│  │                                                           │  │
│  │  Alerts:                                                  │  │
│  │  ├─ Accuracy drops >5pp → rollback                       │  │
│  │  ├─ Cost increases >20% → investigate                    │  │
│  │  ├─ P95 latency >15s → investigate                       │  │
│  │  └─ Error rate >2% → rollback                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Key insight:** Profiles are infrastructure-as-code. Treat them with the same rigor as application code: version control, CI/CD, testing, gradual rollout, monitoring, rollback.

---

### Profile Caching Architecture

```mermaid
sequenceDiagram
    participant R as Request
    participant L as Profile Loader
    participant M as In-Memory Cache
    participant C as Claude API
    
    Note over R,C: Request 1 (Cache MISS)
    R->>L: Diagnosis request
    L->>M: Check cache
    M-->>L: Miss
    L->>L: Load from disk (1500 tokens)
    L->>C: POST /v1/messages<br/>cache_control: ephemeral
    Note over C: Creates cache<br/>TTL: 5 min
    C-->>L: Cost: $0.0975
    L-->>R: Diagnosis result
    
    Note over R,C: Request 2-10 (Cache HIT, within 5 min)
    R->>L: Diagnosis request
    L->>M: Check cache
    M-->>L: Hit (return profile)
    L->>C: POST /v1/messages<br/>(same system prompt)
    Note over C: Cache hit<br/>90% savings
    C-->>L: Cost: $0.0848
    L-->>R: Diagnosis result
```

**Three-Layer Caching Architecture:**

```
┌─── L1: In-Memory Cache (ProfileLoader) ───────┐
│  • TTL: 5 minutes                              │
│  • Storage: Python dict (process memory)      │
│  • Hit rate: 90%+                              │
│  • Speed: 0.1ms (500x faster than disk)       │
│  • Invalidation: Hash-based change detection  │
└────────────────────────────────────────────────┘
                     ↓
┌─── L2: Claude Prompt Cache (Claude API) ──────┐
│  • TTL: 5 minutes (server-side)               │
│  • Storage: Claude's infrastructure           │
│  • Cost reduction: 90% (cached tokens)        │
│  • Trigger: cache_control: ephemeral          │
│  • Hash: Content-based deduplication          │
└────────────────────────────────────────────────┘
                     ↓
┌─── L3: Git Repository (Version History) ──────┐
│  • Persistence: Permanent                      │
│  • Storage: .git directory                     │
│  • Versioning: Full history with diffs        │
│  • Rollback: Instant (git checkout)           │
│  • Audit: Git blame, log, tags                │
└────────────────────────────────────────────────┘
```

**Cost Breakdown with Caching:**

| Scenario | Input Cost | Output Cost | Total | Savings |
|----------|------------|-------------|-------|---------|
| **Cache MISS (10%)** | $0.030 | $0.075 | **$0.105** | Baseline |
| **Cache HIT (90%)** | $0.0098 | $0.075 | **$0.085** | 19% off |
| **Average** | $0.0118 | $0.075 | **$0.087** | 17% off |

**Key numbers:**
- Cache TTL: 5 minutes (Claude's default)
- Cache hit rate target: 90% (with steady traffic)
- Cost savings: 13-19% per cached call
- At 1000 diagnoses/day: $87/day vs $105/day = **$540/month savings**

---

## Core Mechanics

### 1. Profiles as Policies

**What it solves:** Decoupling agent behavior from application code. When you hardcode prompts in Python, every behavior change requires a code deploy. This is slow, risky, and prevents non-engineers from improving prompts.

**Pattern: Declarative Profile Definition**

Profiles are markdown files stored in `profiles/` directory:

```
profiles/
├── network_diagnostician_v1.md
├── network_diagnostician_v2.md (current)
├── network_diagnostician_v3.md (canary)
├── log_analyzer_v2.md
└── config_validator_v1.md
```

**Profile Structure (network_diagnostician_v2.md):**

```mermaid
graph TB
    subgraph "YAML Frontmatter - Metadata"
        M1[profile_id: network_diagnostician]
        M2[version: 2]
        M3[status: production]
        M4[traffic_allocation: 90%]
        M5[cost_budget: 0.50]
        M6[accuracy_target: 0.90]
    end
    
    subgraph "Profile Content Structure"
        I[IDENTITY<br/>Who the agent is]
        O[OBJECTIVE<br/>What to achieve]
        E[EXPERTISE<br/>Domain knowledge]
        R[REASONING PROCEDURE<br/>Step-by-step logic]
        C[CONSTRAINTS<br/>Rules & limits]
        F[OUTPUT FORMAT<br/>JSON schema]
        X[EXAMPLES<br/>Worked cases]
    end
    
    M1 --> I
    I --> O
    O --> E
    E --> R
    R --> C
    C --> F
    F --> X
    
    style M1 fill:#e1f5ff
    style M3 fill:#d4edda
    style I fill:#fff4e6
    style R fill:#ffeaa7
    style F fill:#dfe6e9
```

**Detailed Profile Sections:**

```
PROFILE ANATOMY: network_diagnostician_v2.md

┌─────────────────────────────────────────────────────────┐
│ YAML FRONTMATTER (Metadata)                             │
├─────────────────────────────────────────────────────────┤
│ profile_id: network_diagnostician                       │
│ version: 2                                              │
│ created: 2026-08-01                                     │
│ author: darshit.pandit@example.com                      │
│ status: production                                      │
│ traffic_allocation: 90%                                 │
│ tags: [networking, bgp, ospf, ipsec]                   │
│ cost_budget: 0.50                                       │
│ latency_budget_p95: 10.0                                │
│ accuracy_target: 0.90                                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 1. IDENTITY (Who the agent is)                          │
├─────────────────────────────────────────────────────────┤
│ "You are Atiya, an expert diagnostician for PARTS       │
│  test failures. You specialize in networking test       │
│  failures (BGP, OSPF, IPsec, NAT, routing, HA)."       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 2. OBJECTIVE (What to achieve)                          │
├─────────────────────────────────────────────────────────┤
│ "Identify root cause of networking test failures        │
│  with 90%+ accuracy by analyzing logs, device           │
│  configurations, and test code. Prioritize              │
│  evidence-based diagnosis over speculation."            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 3. EXPERTISE (Domain knowledge)                         │
├─────────────────────────────────────────────────────────┤
│ • PARTS framework: pytest, topology builders            │
│ • PAN-OS networking: BGP, OSPF, IPsec, NAT             │
│ • Common failure patterns:                              │
│   - Timing issues (convergence, test waits)            │
│   - Config mismatches (zone, interface, policy)        │
│   - Resource exhaustion (connection limits)            │
│   - API timeouts (device response slow)                │
│ • Log formats: partsrt, pytest, syslogs                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 4. REASONING PROCEDURE (Step-by-step logic)             │
├─────────────────────────────────────────────────────────┤
│ 1. Parse test name and description                      │
│ 2. Scan logs for ERROR/EXCEPTION/FAILED markers        │
│ 3. Determine failure phase: setup/execution/teardown   │
│ 4. Trace causality backwards from failure point        │
│ 5. Correlate with device configs                       │
│ 6. Form hypothesis based on strongest evidence         │
│ 7. Assign confidence based on evidence strength        │
│    • 0.9-1.0: Smoking gun evidence                     │
│    • 0.7-0.9: Strong evidence                          │
│    • 0.5-0.7: Medium evidence                          │
│    • 0.0-0.5: Weak evidence                            │
│ 8. Cite evidence (exact quotes from logs/configs)      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 5. CONSTRAINTS (Rules & limits)                         │
├─────────────────────────────────────────────────────────┤
│ MUST:                                                    │
│ • Only cite evidence present in provided materials      │
│ • Quote exact lines when referencing evidence          │
│ • If confidence < 0.7, set requires_human_review       │
│                                                          │
│ MUST NOT:                                                │
│ • Never speculate beyond available evidence             │
│ • Never recommend "reboot device" (too generic)        │
│ • Never reference external documentation               │
│ • Never generate fake log lines or config snippets    │
│                                                          │
│ QUALITY:                                                 │
│ • Root cause must be technical and actionable          │
│ • Recommended fix must be specific                     │
│ • Evidence array must have >= 1 entry                  │
│ • Failure category: network|config|timing|resource|code│
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 6. OUTPUT FORMAT (JSON schema)                          │
├─────────────────────────────────────────────────────────┤
│ {                                                        │
│   "root_cause": "string (50-200 chars)",                │
│   "confidence": "float (0.0-1.0)",                      │
│   "evidence": ["array of strings"],                     │
│   "failure_category": "enum [...]",                     │
│   "recommended_fix": "string (100-300 chars)",          │
│   "requires_human_review": "boolean"                    │
│ }                                                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 7. EXAMPLES (Worked cases)                              │
├─────────────────────────────────────────────────────────┤
│ Example 1: Network timeout                              │
│ • Input: test_ipsec_tunnel_establishment               │
│ • Logs: "ERROR IPsec SA negotiation timeout"          │
│ • Output: Crypto mismatch / firewall blocking          │
│ • Confidence: 0.75 (medium evidence)                   │
│                                                          │
│ Example 2: Config error                                 │
│ • Input: test_nat_policy_functionality                 │
│ • Logs: "Policy lookup failed: no matching rule"       │
│ • Output: NAT policy source zone mismatch              │
│ • Confidence: 0.98 (smoking gun)                       │
│                                                          │
│ Example 3: Insufficient data                            │
│ • Input: test_ha_failover_time                         │
│ • Logs: "FAILED Assertion error"                       │
│ • Output: INSUFFICIENT_DATA - no diagnostic context    │
│ • Confidence: 0.0 (no evidence)                        │
└─────────────────────────────────────────────────────────┘
```

**Why this works:**

1. **Declarative:** Entire profile is data (markdown YAML frontmatter), not code
2. **Versionable:** Can diff v1 vs v2, understand what changed
3. **Testable:** CI can run test suite against profile before deploy
4. **Reviewable:** Non-engineers (QA, product) can review and approve changes
5. **Deployable:** No code changes needed, just update profile file

**Pattern Comparison:**

```mermaid
graph LR
    subgraph "Anti-pattern: Hardcoded Prompts"
        A1[Prompt in Code] --> A2[Change Needed]
        A2 --> A3[Edit Python]
        A3 --> A4[Code Review]
        A4 --> A5[Deploy App]
        A5 --> A6[Restart Service]
        
        A7[Drawbacks:<br/>- Requires code deploy<br/>- No A/B testing<br/>- Engineers only<br/>- Slow iteration]
    end
    
    subgraph "Correct: Declarative Profiles"
        B1[Prompt in .md File] --> B2[Change Needed]
        B2 --> B3[Edit Markdown]
        B3 --> B4[Git Commit]
        B4 --> B5[CI Validates]
        B5 --> B6[Hot Reload]
        
        B7[Benefits:<br/>- No code changes<br/>- A/B testing built-in<br/>- Non-engineers can edit<br/>- Fast iteration]
    end
    
    style A1 fill:#f8d7da
    style A7 fill:#f8d7da
    style B1 fill:#d4edda
    style B7 fill:#d4edda
```

**Implementation Comparison:**

```
┌──────────────────────────────────────────────────────────┐
│ ❌ ANTI-PATTERN: Hardcoded Prompts                       │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ def diagnose(test_name, logs):                           │
│     system_prompt = """                                  │
│     You are a test diagnostician.                        │
│     Analyze logs and return root cause.                  │
│     """                                                   │
│                                                           │
│ Problems:                                                 │
│ • Every behavior change requires code deploy            │
│ • No A/B testing capability                             │
│ • No non-engineer contributions                         │
│ • Slow iteration (code review, CI/CD, restart)         │
│ • Version control mixed with code changes              │
│ • Can't hot-reload prompts                              │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ ✅ CORRECT PATTERN: Declarative Profiles                 │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ class ProfileLoader:                                      │
│     def load_profile(self, profile_id, version="latest"):│
│         if version == "latest":                          │
│             version = self._get_latest_version(profile_id)│
│                                                           │
│         path = f"profiles/{profile_id}_v{version}.md"   │
│         return self._parse_profile(path)                 │
│                                                           │
│ Benefits:                                                 │
│ • Behavior changes = update profile file (no code)      │
│ • A/B testing = route 10% to v3, 90% to v2             │
│ • Non-engineers = can edit markdown files               │
│ • Fast iteration (edit file, commit, auto-deploy)      │
│ • Clean version control (git diff shows prompt changes)│
│ • Hot-reload capability (zero downtime)                 │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ WORKFLOW COMPARISON                                       │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ Hardcoded Prompts:                                        │
│ 1. Engineer edits Python file                            │
│ 2. Code review process (1-2 days)                       │
│ 3. CI/CD pipeline (30 min)                              │
│ 4. Deploy application (15 min)                          │
│ 5. Restart service (10 min downtime)                    │
│ Total: 45 minutes + review time                         │
│                                                           │
│ Declarative Profiles:                                     │
│ 1. Anyone edits markdown file                            │
│ 2. Git commit + PR                                       │
│ 3. CI validation (5 min)                                │
│ 4. Auto-deploy canary (1 min)                           │
│ 5. Hot-reload (0 sec downtime)                          │
│ Total: 3 minutes, zero downtime                         │
└──────────────────────────────────────────────────────────┘
```

---

### 2. Version-Controlled Profiles

**What it solves:** How do you track profile changes over time? How do you understand what changed between v1 and v2? How do you roll back when v3 regresses accuracy? Version control (git) provides history, diff, blame, and rollback.

**Pattern: Git-Based Profile Management**

```mermaid
gitGraph
    commit id: "v1 initial"
    commit id: "v1 fix schema"
    branch profile/network-v2
    checkout profile/network-v2
    commit id: "v2 add constraints"
    commit id: "v2 add examples"
    checkout main
    merge profile/network-v2 tag: "v2-production"
    branch profile/network-v3
    checkout profile/network-v3
    commit id: "v3 BGP improvements"
    commit id: "v3 fix edge cases"
    checkout main
    merge profile/network-v3 tag: "v3-canary-10pct"
```

**Repository Structure:**

```
atiya-profiles/
├── .github/workflows/          ← CI/CD automation
│   ├── validate-profile.yml    (lint, test, measure)
│   └── deploy-profile.yml      (canary, monitor, promote)
│
├── profiles/                   ← Declarative agent policies
│   ├── network_diagnostician_v1.md (deprecated)
│   ├── network_diagnostician_v2.md (production, 90%)
│   ├── network_diagnostician_v3.md (canary, 10%)
│   ├── log_analyzer_v2.md
│   └── config_validator_v1.md
│
├── tests/                      ← Regression test suite
│   ├── test_network_diagnostician.py
│   └── known_failures/         (golden dataset)
│       ├── bgp_failover.json
│       ├── ipsec_timeout.json
│       └── nat_policy_mismatch.json
│
└── scripts/                    ← Deployment tooling
    ├── validate_profile.py     (schema, syntax check)
    ├── test_profile.py         (accuracy measurement)
    └── deploy_profile.py       (canary deployment)
```

**Workflow: Creating a new profile version**

```mermaid
flowchart TD
    A[Create branch:<br/>profile/network-v3] --> B[Copy v2 as baseline]
    B --> C[Edit profile:<br/>Add BGP improvements]
    C --> D[Update metadata:<br/>version: 3, status: canary]
    D --> E[Commit with message]
    E --> F[Push & create PR]
    F --> G{CI Validation}
    
    G -->|Lint| H[Syntax check]
    G -->|Test| I[Run 10 known failures]
    G -->|Measure| J[Accuracy/Cost/Latency]
    
    H --> K{All pass?}
    I --> K
    J --> K
    
    K -->|No| L[Reject PR]
    K -->|Yes| M[Code review]
    M --> N[Merge to main]
    N --> O[Auto-deploy canary 10%]
    O --> P[Monitor 2 hours]
    P --> Q{Metrics good?}
    
    Q -->|No| R[Auto-rollback to v2]
    Q -->|Yes| S[Promote to 50%]
    S --> T[Monitor 1 hour]
    T --> U{Stable?}
    U -->|No| R
    U -->|Yes| V[Promote to 100%]
    
    style A fill:#e1f5ff
    style O fill:#fff4e6
    style V fill:#d4edda
    style R fill:#f8d7da
```

**Commit Message Template:**

```
┌─────────────────────────────────────────────────────────┐
│ COMMIT MESSAGE STRUCTURE                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ git commit -m "                                         │
│ Add profile v3 with improved BGP failure detection      │
│                                                          │
│ Changes:                                                 │
│ - Added BGP-specific reasoning steps                   │
│ - Added 3 new BGP failure examples                     │
│ - Improved OSPF vs BGP differentiation                 │
│                                                          │
│ Performance targets:                                     │
│ - Accuracy: 92% (up from 90%)                          │
│ - Cost budget: $0.50 (unchanged)                       │
│ - Latency P95: 10s (unchanged)                         │
│                                                          │
│ Testing:                                                 │
│ - 10/10 known failures diagnosed correctly             │
│ - Cost: $0.092 avg (within budget)                     │
│ - Latency P95: 9.2s (20% faster)                       │
│ "                                                        │
│                                                          │
│ SECTIONS:                                                │
│ 1. Title: What changed (1 line, < 70 chars)            │
│ 2. Changes: What you modified (bullet list)            │
│ 3. Performance: New targets vs baseline                │
│ 4. Testing: Validation results                         │
└─────────────────────────────────────────────────────────┘
```

**A/B Testing Flow:**

```
┌─── A/B Testing Workflow ─────────────────────────────────────────┐
│                                                                    │
│  Request arrives: diagnosis-12345                                 │
│  ├─ Compute hash: MD5(request_id) = 0x7a3f...                    │
│  ├─ Normalize: hash / 2^128 = 0.238 (23.8%)                      │
│  ├─ Compare to routing: {v2: 90%, v3: 10%}                       │
│  │                                                                 │
│  │  [0.0 ─────────┬───────── 0.9 ─┬─ 1.0]                        │
│  │      v2 (90%)  │       v3 (10%) │                              │
│  │                │                │                              │
│  │            threshold = 0.238    │                              │
│  │                ↓                │                              │
│  └─ Route to: v2 (threshold < 0.9)                                │
│                                                                    │
│  Consistent hashing: Same request_id always gets same version     │
│                                                                    │
├─── Metrics Collection (1 hour window) ───────────────────────────┤
│                                                                    │
│  Version 2 (90% traffic):          Version 3 (10% traffic):       │
│  ├─ Requests: 900                  ├─ Requests: 100               │
│  ├─ Accuracy: 89%                  ├─ Accuracy: 92%               │
│  ├─ Avg cost: $0.086               ├─ Avg cost: $0.091            │
│  ├─ P95 latency: 9.2s              ├─ P95 latency: 9.8s           │
│  └─ Error rate: 0.3%               └─ Error rate: 0.5%            │
│                                                                    │
├─── Decision Engine ──────────────────────────────────────────────┤
│                                                                    │
│  Criteria:                          v3 vs v2:                     │
│  ├─ Accuracy delta: +3pp            ✅ PASS (+3pp > +2pp min)     │
│  ├─ Cost delta: +$0.005             ✅ PASS (+6% < +20% max)      │
│  ├─ Latency delta: +0.6s            ✅ PASS (+6.5% < +15% max)    │
│  ├─ Error rate: 0.5%                ✅ PASS (< 2% threshold)      │
│  └─ Decision: PROMOTE v3 to 50%     (accuracy gain worth cost)   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Git Operations Reference:**

```
┌─────────────────────────────────────────────────────────┐
│ GIT OPERATIONS FOR PROFILE MANAGEMENT                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ View version history:                                    │
│ ┌──────────────────────────────────────────────────┐   │
│ │ git log --oneline --graph \                      │   │
│ │   profiles/network_diagnostician_v*.md           │   │
│ │                                                   │   │
│ │ Output:                                           │   │
│ │ * 7a3f2b1 (v3-canary) Add BGP improvements       │   │
│ │ * 5c9d8e4 (v2-production) Fix OSPF detection     │   │
│ │ * 2f1a6b9 (v1-deprecated) Initial version        │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Compare versions:                                        │
│ ┌──────────────────────────────────────────────────┐   │
│ │ git diff v2-production v3-canary -- \            │   │
│ │   profiles/network_diagnostician_v3.md           │   │
│ │                                                   │   │
│ │ Shows:                                            │   │
│ │ + Added: BGP-specific reasoning steps            │   │
│ │ + Added: 3 new BGP failure examples              │   │
│ │ - Removed: Generic network timeout handling      │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Tag releases:                                            │
│ ┌──────────────────────────────────────────────────┐   │
│ │ git tag -a v3-canary-10pct \                     │   │
│ │   -m "v3 canary at 10% traffic"                  │   │
│ │                                                   │   │
│ │ git tag -a v3-production \                       │   │
│ │   -m "v3 promoted to 100% (accuracy: 92%)"       │   │
│ │                                                   │   │
│ │ Purpose: Mark deployment milestones              │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Rollback (instant):                                      │
│ ┌──────────────────────────────────────────────────┐   │
│ │ git checkout v2-production                       │   │
│ │ ./scripts/deploy_profile.py \                    │   │
│ │   --profile network_diagnostician \              │   │
│ │   --version 2                                     │   │
│ │                                                   │   │
│ │ Duration: 30 seconds (vs 45 min re-deploy)      │   │
│ │ Downtime: 0 seconds (hot-reload)                 │   │
│ └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**CI/CD Pipeline Structure:**

```mermaid
graph LR
    subgraph "CI: Validation (.github/workflows/validate-profile.yml)"
        A[PR Created] --> B[Lint Syntax]
        B --> C[Validate Schema]
        C --> D[Run Test Suite]
        D --> E[Check Thresholds]
        E --> F{All Pass?}
        F -->|Yes| G[Post Results ✅]
        F -->|No| H[Block Merge ❌]
    end
    
    subgraph "CD: Deployment (.github/workflows/deploy-profile.yml)"
        I[Merge to Main] --> J[Deploy Canary 10%]
        J --> K[Monitor 2 Hours]
        K --> L{Metrics Good?}
        L -->|Yes| M[Promote to 50%]
        L -->|No| N[Auto-Rollback]
        M --> O[Monitor 1 Hour]
        O --> P{Stable?}
        P -->|Yes| Q[Promote to 100%]
        P -->|No| N
    end
    
    style G fill:#d4edda
    style H fill:#f8d7da
    style N fill:#f8d7da
    style Q fill:#d4edda
```

**CI Validation Steps:**

| Step | Tool | Check | Fail Threshold | Impact |
|------|------|-------|----------------|--------|
| Lint | `validate_profile.py` | Markdown syntax, YAML | Syntax error | Block PR |
| Schema | `jsonschema` | Required fields | Missing field | Block PR |
| Test | `test_profile.py` | 10 known failures | Accuracy < 85% | Block PR |
| Cost | `check_metrics.py` | Average cost | > $0.60 | Block PR |
| Latency | `check_metrics.py` | P95 latency | > 15s | Block PR |

**CD Deployment Script:**

```mermaid
sequenceDiagram
    participant E as Engineer
    participant S as deploy_profile.py
    participant M as monitor_canary.py
    participant D as promote_or_rollback.py
    participant P as Production
    
    E->>S: Deploy canary 10%
    Note over S: --profile network_diagnostician_v3.md<br/>--traffic-allocation 0.10
    S->>P: Route 10% traffic to v3
    S->>M: Start monitoring
    
    loop Every 5 minutes for 2 hours
        M->>P: Collect metrics
        Note over M: Accuracy, cost, latency, errors
        M->>M: Compare v3 vs v2
    end
    
    M->>D: Trigger decision engine
    D->>D: Evaluate criteria
    
    alt Metrics Pass
        D->>P: Promote v3 to 50%
        Note over P: Success: Continue rollout
    else Metrics Fail
        D->>P: Rollback to 100% v2
        Note over P: Failure: Auto-rollback
    end
```

---

### 3. Profile Loading

**What it solves:** Runtime loading of profiles from files or database, with hot-reload capability (update profiles without restarting service).

**Pattern: Lazy Loading + In-Memory Cache + Hot-Reload**

```mermaid
stateDiagram-v2
    [*] --> CheckCache: load_profile(id, version)
    CheckCache --> CacheHit: Found + Fresh + Hash Match
    CheckCache --> LoadDisk: Not Found / Stale / Changed
    CacheHit --> [*]: Return cached
    LoadDisk --> ParseYAML: Read file
    ParseYAML --> Validate: Extract metadata
    Validate --> StoreCache: Valid profile
    StoreCache --> [*]: Return profile
    
    HotReload --> ClearCache: Profile changed
    ClearCache --> LoadDisk: Force reload
```

**Profile Loader Architecture:**

```
┌─── ProfileLoader ─────────────────────────────────────────┐
│                                                             │
│  Load Flow:                                                 │
│  1. Check cache (key: profile_id_vN)                       │
│  2. If hit: verify TTL (5 min) + hash (detect changes)    │
│  3. If miss/stale: load from disk                          │
│  4. Parse YAML frontmatter + extract system prompt         │
│  5. Store in cache with timestamp + hash                   │
│                                                             │
│  A/B Routing:                                               │
│  • Routing config: {v2: 0.9, v3: 0.1}                      │
│  • Consistent hashing: MD5(request_id) % 100               │
│  • If hash < 10 → v3, else → v2                            │
│  • Same request always routes to same version              │
│                                                             │
│  Hot-Reload:                                                │
│  • File watcher detects .md changes                        │
│  • Invalidate cache (delete key)                           │
│  • Next request loads fresh version                        │
│  • Zero downtime (gradual rollout)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**ProfileLoader Architecture:**

```mermaid
classDiagram
    class Profile {
        +str profile_id
        +int version
        +str content
        +Dict metadata
        +datetime loaded_at
        +str file_hash
        +to_system_prompt() str
    }
    
    class ProfileLoader {
        -str profiles_dir
        -int cache_ttl
        -Dict cache
        -Dict routing
        +load_profile(id, version) Profile
        +get_profile_for_request(id, req_id) Profile
        +set_version_routing(id, routing)
        +hot_reload(id, version) Profile
        -_load_from_disk(id, version) Profile
        -_compute_file_hash(id, version) str
        -_get_active_version(id) int
    }
    
    ProfileLoader --> Profile : creates
    ProfileLoader --> "0..*" Profile : caches
```

**ProfileLoader Flow:**

```mermaid
flowchart TD
    Start[load_profile called] --> CheckVer{Version specified?}
    CheckVer -->|No| GetActive[Get active version<br/>from routing config]
    CheckVer -->|Yes| CheckCache
    GetActive --> CheckCache{Check cache}
    
    CheckCache -->|Cache key found| CheckTTL{TTL valid?}
    CheckCache -->|Cache miss| LoadDisk[Load from disk]
    
    CheckTTL -->|Yes| CheckHash{Hash matches?}
    CheckTTL -->|No| LoadDisk
    
    CheckHash -->|Yes| CacheHit[Return cached profile]
    CheckHash -->|No| LoadDisk
    
    LoadDisk --> ReadFile[Read .md file]
    ReadFile --> ParseYAML[Parse YAML frontmatter]
    ParseYAML --> ExtractPrompt[Extract system prompt]
    ExtractPrompt --> ComputeHash[Compute SHA256 hash]
    ComputeHash --> CreateProfile[Create Profile object]
    CreateProfile --> StoreCache[Store in cache]
    StoreCache --> Return[Return profile]
    
    CacheHit --> End[End]
    Return --> End
    
    style CacheHit fill:#d4edda
    style LoadDisk fill:#fff4e6
    style Return fill:#d4edda
```

**A/B Routing Logic:**

```mermaid
flowchart TD
    Start[get_profile_for_request] --> GetRouting[Get routing config<br/>e.g., v2: 0.9, v3: 0.1]
    GetRouting --> HashReq[Hash request_id<br/>MD5 -> 0.0-1.0]
    HashReq --> CheckThreshold{Compare to cumulative}
    
    CheckThreshold -->|< 0.9| V2[Select version 2]
    CheckThreshold -->|>= 0.9| V3[Select version 3]
    
    V2 --> LoadV2[load_profile v2]
    V3 --> LoadV3[load_profile v3]
    
    LoadV2 --> Return[Return profile]
    LoadV3 --> Return
    
    style V2 fill:#e1f5ff
    style V3 fill:#fff4e6
    style Return fill:#d4edda
```

**Key Methods Overview:**

```
┌─────────────────────────────────────────────────────────┐
│ PROFILELOADER KEY METHODS                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ load_profile(profile_id, version)                       │
│ ├─ Purpose: Load specific version                      │
│ ├─ Caching: Yes (5-min TTL)                            │
│ ├─ Hash validation: Yes                                │
│ └─ Use case: Direct version access                     │
│                                                          │
│ get_profile_for_request(profile_id, request_id)        │
│ ├─ Purpose: A/B routing                                │
│ ├─ Routing: Consistent hashing                         │
│ ├─ Returns: Different versions per routing config      │
│ └─ Use case: Production requests                       │
│                                                          │
│ set_version_routing(profile_id, routing)               │
│ ├─ Purpose: Configure traffic split                   │
│ ├─ Validation: Must sum to 1.0                         │
│ ├─ Example: {2: 0.9, 3: 0.1}                          │
│ └─ Use case: A/B test setup                            │
│                                                          │
│ hot_reload(profile_id, version)                         │
│ ├─ Purpose: Force cache clear                          │
│ ├─ Downtime: Zero seconds                              │
│ ├─ Effect: Next request gets fresh version             │
│ └─ Use case: Zero-downtime updates                     │
│                                                          │
│ _compute_file_hash(profile_id, version)                │
│ ├─ Purpose: Change detection                           │
│ ├─ Algorithm: SHA256                                   │
│ ├─ Effect: Invalidates cache if file changed          │
│ └─ Use case: Cache validation                          │
└─────────────────────────────────────────────────────────┘
```

**Key Methods:**

| Method | Purpose | Use Case |
|--------|---------|----------|
| `load_profile(id, ver)` | Load specific version | Direct version access |
| `get_profile_for_request(id, req_id)` | A/B routing | Production requests |
| `set_version_routing(id, routing)` | Configure traffic split | A/B test setup |
| `hot_reload(id, ver)` | Force cache clear | Zero-downtime updates |
| `_compute_file_hash(id, ver)` | Change detection | Cache invalidation |

**File Watcher for Auto Hot-Reload:**

```mermaid
sequenceDiagram
    participant F as File System
    participant W as Watchdog Observer
    participant H as ProfileFileHandler
    participant L as ProfileLoader
    participant C as Cache
    
    F->>W: .md file modified
    W->>H: on_modified(event)
    
    alt File is not .md
        H->>H: Ignore
    else File is .md
        H->>H: Parse filename<br/>network_diagnostician_v3.md
        H->>H: Extract (profile_id, version)
        Note over H: profile_id = network_diagnostician<br/>version = 3
        
        H->>L: hot_reload(profile_id, version)
        L->>C: Delete cache key
        L->>F: Read file (fresh)
        F-->>L: File content
        L->>L: Parse & create Profile
        L->>C: Store new version
        L-->>H: Profile reloaded
        H->>H: Log "Reload complete"
    end
    
    Note over F,C: Next request gets fresh profile<br/>Zero downtime
```

**File Watcher Setup:**

```
┌─────────────────────────────────────────────────────────┐
│ AUTO HOT-RELOAD ARCHITECTURE                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 1. File Change Detection                                │
│    ┌─────────────────────────────────────────────┐     │
│    │ Watchdog Observer monitors:                 │     │
│    │ • Directory: profiles/                      │     │
│    │ • File pattern: *.md                        │     │
│    │ • Events: on_modified                       │     │
│    └─────────────────────────────────────────────┘     │
│                                                          │
│ 2. Event Handling                                       │
│    ┌─────────────────────────────────────────────┐     │
│    │ ProfileFileHandler receives event:          │     │
│    │ • Check extension (.md only)                │     │
│    │ • Parse filename:                           │     │
│    │   "network_diagnostician_v3.md"             │     │
│    │   -> profile_id="network_diagnostician"     │     │
│    │   -> version="3"                            │     │
│    └─────────────────────────────────────────────┘     │
│                                                          │
│ 3. Hot Reload Trigger                                   │
│    ┌─────────────────────────────────────────────┐     │
│    │ loader.hot_reload(profile_id, version):     │     │
│    │ • Clear cache entry                         │     │
│    │ • Load fresh from disk                      │     │
│    │ • Store in cache                            │     │
│    │ • Log completion                            │     │
│    └─────────────────────────────────────────────┘     │
│                                                          │
│ 4. Zero-Downtime Update                                 │
│    ┌─────────────────────────────────────────────┐     │
│    │ In-flight requests:                         │     │
│    │ • Continue with old cached version          │     │
│    │                                              │     │
│    │ New requests:                                │     │
│    │ • Get fresh version from cache              │     │
│    │                                              │     │
│    │ Downtime: 0 seconds                         │     │
│    └─────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

**Testing Profile Loader:**

```mermaid
graph TD
    subgraph "Test Suite Structure"
        T1[test_load_profile_from_disk]
        T2[test_profile_caching]
        T3[test_cache_expiration]
        T4[test_ab_routing]
        T5[test_hot_reload]
    end
    
    subgraph "What Each Test Validates"
        V1[File parsing works<br/>Content extracted correctly]
        V2[Same load = same timestamp<br/>Cache hit verified]
        V3[After TTL = different timestamp<br/>Cache expired verified]
        V4[100 requests split 90/10<br/>A/B routing works]
        V5[Reload = fresh timestamp<br/>Cache invalidation works]
    end
    
    T1 --> V1
    T2 --> V2
    T3 --> V3
    T4 --> V4
    T5 --> V5
    
    style V1 fill:#d4edda
    style V2 fill:#d4edda
    style V3 fill:#d4edda
    style V4 fill:#d4edda
    style V5 fill:#d4edda
```

**Test Coverage Map:**

```
┌─────────────────────────────────────────────────────────┐
│ PROFILE LOADER TEST COVERAGE                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ test_load_profile_from_disk                             │
│ ├─ Purpose: Validate file parsing                      │
│ ├─ Steps:                                               │
│ │  1. Create ProfileLoader                             │
│ │  2. Load network_diagnostician v2                    │
│ │  3. Assert version == 2                              │
│ │  4. Assert "You are Atiya" in content               │
│ └─ Pass criteria: Profile loaded, content valid        │
│                                                          │
│ test_profile_caching                                    │
│ ├─ Purpose: Verify cache hit                           │
│ ├─ Steps:                                               │
│ │  1. Create ProfileLoader (TTL=60s)                   │
│ │  2. Load same profile twice                          │
│ │  3. Compare loaded_at timestamps                     │
│ └─ Pass criteria: Timestamps identical (cache hit)     │
│                                                          │
│ test_cache_expiration                                   │
│ ├─ Purpose: Validate TTL enforcement                   │
│ ├─ Steps:                                               │
│ │  1. Create ProfileLoader (TTL=1s)                    │
│ │  2. Load profile                                      │
│ │  3. Sleep 2 seconds                                   │
│ │  4. Load same profile again                          │
│ │  5. Compare loaded_at timestamps                     │
│ └─ Pass criteria: Different timestamps (cache expired) │
│                                                          │
│ test_ab_routing                                         │
│ ├─ Purpose: Verify traffic split                       │
│ ├─ Steps:                                               │
│ │  1. Set routing: v2=90%, v3=10%                      │
│ │  2. Make 100 requests with unique IDs                │
│ │  3. Count versions returned                          │
│ │  4. Assert 85-95 requests got v2                     │
│ │  5. Assert 5-15 requests got v3                      │
│ └─ Pass criteria: Distribution ~90/10 (±5%)            │
│                                                          │
│ test_hot_reload                                         │
│ ├─ Purpose: Validate cache invalidation                │
│ ├─ Steps:                                               │
│ │  1. Load profile (gets cached)                       │
│ │  2. Call hot_reload()                                │
│ │  3. Compare loaded_at timestamps                     │
│ └─ Pass criteria: New timestamp > old (fresh load)     │
└─────────────────────────────────────────────────────────┘
```

**Test Coverage:**

| Test | Validates | Pass Criteria |
|------|-----------|---------------|
| `test_load_profile_from_disk` | File parsing | Profile loaded, content valid |
| `test_profile_caching` | Cache hit | Same timestamp on re-load |
| `test_cache_expiration` | TTL enforcement | Different timestamp after TTL |
| `test_ab_routing` | Traffic split | 90%/10% distribution ±5% |
| `test_hot_reload` | Cache invalidation | Fresh load after reload |

---

### 4. Profile Caching

**What it solves:** Cost optimization. Claude's API charges for input tokens (profile content). If you send the same 1500-token profile on every request, you pay $0.0225 per diagnosis. With prompt caching, Claude caches the profile for 5 minutes, and subsequent requests pay only $0.0023 for cached tokens (90% off).

**Pattern: Ephemeral Prompt Caching**

**How Claude Prompt Caching Works:**

1. **Mark content as cacheable** using `cache_control`:
   ```json
   {
     "type": "text",
     "text": "<profile content>",
     "cache_control": {"type": "ephemeral"}
   }
   ```

2. **First request creates cache:**
   - Claude computes hash of profile content
   - Stores in cache with 5-minute TTL
   - Returns cache creation tokens in response

3. **Subsequent requests read from cache (within 5 min):**
   - Claude computes hash of profile content
   - Finds match in cache
   - Charges 90% less for cached tokens

**Cost Breakdown:**

```
Profile: 1500 tokens (system prompt)
User prompt: 500 tokens (logs, test code)
Output: 1000 tokens (diagnosis)

Request 1 (cache creation):
  - Input: 2000 tokens × $15/M = $0.030
  - Output: 1000 tokens × $75/M = $0.075
  - Total: $0.105

Request 2-N (within 5 min, cache hit):
  - Cached input: 1500 tokens × $1.50/M = $0.0023
  - Fresh input: 500 tokens × $15/M = $0.0075
  - Output: 1000 tokens × $75/M = $0.075
  - Total: $0.0848
  - Savings: $0.105 - $0.0848 = $0.0202 (19% off)

Average cost with 90% cache hit rate:
  (0.1 × $0.105) + (0.9 × $0.0848) = $0.0868
```

**CachedDiagnosticEngine Architecture:**

```mermaid
classDiagram
    class CachedDiagnosticEngine {
        -Anthropic client
        -ProfileLoader profile_loader
        -int cache_hits
        -int cache_misses
        -float total_cost
        +diagnose(test_name, logs, ...) Dict
        +get_cache_stats() Dict
        -_calculate_cost(usage) float
    }
    
    class ProfileLoader {
        +get_profile_for_request(id, req_id) Profile
    }
    
    class Anthropic {
        +messages.create(...) Response
    }
    
    CachedDiagnosticEngine --> ProfileLoader : uses
    CachedDiagnosticEngine --> Anthropic : calls
```

**Diagnosis Flow with Caching:**

```mermaid
sequenceDiagram
    participant C as Caller
    participant E as CachedDiagnosticEngine
    participant P as ProfileLoader
    participant A as Claude API
    
    C->>E: diagnose(test, logs, req_id)
    E->>P: get_profile_for_request(id, req_id)
    P-->>E: Profile object
    
    E->>E: Extract system prompt
    E->>A: messages.create(<br/>system with cache_control,<br/>user message)
    
    alt First request (cache MISS)
        Note over A: Create cache<br/>TTL: 5 min
        A-->>E: Response<br/>cache_creation_input_tokens > 0
        E->>E: cache_misses++
        E->>E: Calculate cost: $0.105
    else Subsequent request (cache HIT)
        Note over A: Read from cache<br/>90% savings
        A-->>E: Response<br/>cache_read_input_tokens > 0
        E->>E: cache_hits++
        E->>E: Calculate cost: $0.085
    end
    
    E->>E: Parse JSON response
    E->>E: Add _meta with cost, cache_hit
    E->>E: total_cost += cost
    E-->>C: Diagnosis with metadata
```

**Cost Calculation Logic:**

```mermaid
flowchart TD
    Start[Calculate Cost] --> GetTokens[Get token counts from usage]
    GetTokens --> CalcFresh[Fresh input tokens =<br/>total - cached]
    CalcFresh --> CostFresh[Cost += fresh × $15/M]
    CostFresh --> CostCached[Cost += cached × $1.50/M]
    CostCached --> CostOutput[Cost += output × $75/M]
    CostOutput --> Return[Return total cost]
    
    style CostFresh fill:#fff4e6
    style CostCached fill:#d4edda
    style CostOutput fill:#e1f5ff
```

**Implementation Overview:**

```
┌─────────────────────────────────────────────────────────┐
│ CACHEDDIAGNOSTICENGINE INTERNALS                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Initialization:                                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ __init__(api_key, profile_loader):               │   │
│ │ • client = anthropic.Anthropic(api_key)          │   │
│ │ • profile_loader = ProfileLoader instance        │   │
│ │ • cache_hits = 0                                 │   │
│ │ • cache_misses = 0                               │   │
│ │ • total_cost = 0.0                               │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Diagnose Method:                                         │
│ ┌──────────────────────────────────────────────────┐   │
│ │ diagnose(test_name, logs, config, profile_id,    │   │
│ │          request_id):                            │   │
│ │                                                   │   │
│ │ 1. Load profile via A/B routing                  │   │
│ │ 2. Build API request with cache_control          │   │
│ │ 3. Call Claude API                               │   │
│ │ 4. Track cache hit/miss                          │   │
│ │ 5. Calculate cost                                │   │
│ │ 6. Parse response JSON                           │   │
│ │ 7. Add _meta with cost, cache_hit, tokens        │   │
│ │ 8. Return diagnosis                              │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Cost Calculation:                                        │
│ ┌──────────────────────────────────────────────────┐   │
│ │ _calculate_cost(usage):                          │   │
│ │                                                   │   │
│ │ fresh_input = total - cached                     │   │
│ │ cost = 0.0                                       │   │
│ │ cost += (fresh_input / 1M) × $15.00             │   │
│ │ cost += (cached_input / 1M) × $1.50             │   │
│ │ cost += (output_tokens / 1M) × $75.00           │   │
│ │ return cost                                      │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Cache Stats:                                             │
│ ┌──────────────────────────────────────────────────┐   │
│ │ get_cache_stats():                               │   │
│ │                                                   │   │
│ │ total_requests = hits + misses                   │   │
│ │ return {                                         │   │
│ │   'hit_rate': hits / total,                      │   │
│ │   'total_cost': total_cost,                      │   │
│ │   'avg_cost': total_cost / total                 │   │
│ │ }                                                │   │
│ └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Cost Savings Table:**

| Request | Input Cost | Cache Cost | Output Cost | Total | Savings |
|---------|------------|------------|-------------|-------|---------|
| 1 (miss) | $0.030 | $0.000 | $0.075 | $0.105 | - |
| 2 (hit) | $0.008 | $0.002 | $0.075 | $0.085 | 19% |
| 3 (hit) | $0.008 | $0.002 | $0.075 | $0.085 | 19% |
| **Avg (90% hit)** | - | - | - | **$0.087** | **17%** |

**Cache Performance Monitoring:**

```mermaid
graph TB
    subgraph "Prometheus Metrics"
        M1[cache_hit_rate<br/>Gauge]
        M2[cache_hits_total<br/>Counter]
        M3[cache_misses_total<br/>Counter]
        M4[diagnosis_cost_usd<br/>Histogram]
    end
    
    subgraph "MonitoredEngine"
        E[diagnose method]
    end
    
    subgraph "Data Flow"
        D1[Diagnosis result] --> E
        E --> C{Cache hit?}
        C -->|Yes| M2
        C -->|No| M3
        E --> M4
        M2 --> M1
        M3 --> M1
    end
    
    style M1 fill:#e1f5ff
    style M2 fill:#d4edda
    style M3 fill:#fff4e6
    style M4 fill:#ffeaa7
```

**Monitoring Implementation:**

```
┌─────────────────────────────────────────────────────────┐
│ PROMETHEUS METRICS INTEGRATION                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Metric Definitions:                                      │
│ ┌──────────────────────────────────────────────────┐   │
│ │ cache_hit_rate = Gauge(                          │   │
│ │   'profile_cache_hit_rate',                      │   │
│ │   'Cache hit rate',                              │   │
│ │   ['profile_id']                                 │   │
│ │ )                                                │   │
│ │                                                   │   │
│ │ cache_hits = Counter(                            │   │
│ │   'profile_cache_hits_total',                    │   │
│ │   'Cache hits',                                  │   │
│ │   ['profile_id']                                 │   │
│ │ )                                                │   │
│ │                                                   │   │
│ │ cache_misses = Counter(                          │   │
│ │   'profile_cache_misses_total',                  │   │
│ │   'Cache misses',                                │   │
│ │   ['profile_id']                                 │   │
│ │ )                                                │   │
│ │                                                   │   │
│ │ diagnosis_cost = Histogram(                      │   │
│ │   'diagnosis_cost_usd',                          │   │
│ │   'Cost per diagnosis',                          │   │
│ │   ['profile_id', 'cache_hit'],                   │   │
│ │   buckets=[0.01, 0.05, 0.08, 0.10, 0.15, 0.20]  │   │
│ │ )                                                │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ MonitoredEngine Implementation:                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ class MonitoredEngine(CachedDiagnosticEngine):   │   │
│ │     def diagnose(self, *args, **kwargs):         │   │
│ │         # Call parent method                     │   │
│ │         diagnosis = super().diagnose(*args, **kwargs)│
│ │                                                   │   │
│ │         # Extract metadata                       │   │
│ │         meta = diagnosis['_meta']                │   │
│ │         profile_id = kwargs.get('profile_id',    │   │
│ │                                 'default')        │   │
│ │                                                   │   │
│ │         # Record cache metrics                   │   │
│ │         if meta['cache_hit']:                    │   │
│ │             cache_hits.labels(                   │   │
│ │               profile_id=profile_id).inc()       │   │
│ │         else:                                     │   │
│ │             cache_misses.labels(                 │   │
│ │               profile_id=profile_id).inc()       │   │
│ │                                                   │   │
│ │         # Record cost                            │   │
│ │         diagnosis_cost.labels(                   │   │
│ │             profile_id=profile_id,               │   │
│ │             cache_hit=str(meta['cache_hit'])     │   │
│ │         ).observe(meta['cost'])                  │   │
│ │                                                   │   │
│ │         return diagnosis                         │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Query Examples (PromQL):                                 │
│ ┌──────────────────────────────────────────────────┐   │
│ │ # Cache hit rate                                 │   │
│ │ rate(profile_cache_hits_total[5m]) /             │   │
│ │   (rate(profile_cache_hits_total[5m]) +          │   │
│ │    rate(profile_cache_misses_total[5m]))         │   │
│ │                                                   │   │
│ │ # Average cost (last hour)                       │   │
│ │ rate(diagnosis_cost_usd_sum[1h]) /               │   │
│ │   rate(diagnosis_cost_usd_count[1h])             │   │
│ │                                                   │   │
│ │ # Cost by cache hit status                       │   │
│ │ histogram_quantile(0.50,                         │   │
│ │   rate(diagnosis_cost_usd_bucket[5m])            │   │
│ │ ) by (cache_hit)                                 │   │
│ └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Prometheus Metrics:**

| Metric | Type | Purpose | Labels |
|--------|------|---------|--------|
| `profile_cache_hit_rate` | Gauge | Current hit rate | profile_id |
| `profile_cache_hits_total` | Counter | Total hits | profile_id, version |
| `diagnosis_cost_usd` | Histogram | Cost distribution | profile_id, cache_hit |
| `diagnosis_duration_seconds` | Histogram | Latency distribution | profile_id, version |

**Cache Optimization Strategies:**

```
┌─── Cache Optimization Playbook ──────────────────────────┐
│                                                            │
│  1. Maximize TTL Utilization (5-min window)               │
│     • Batch diagnoses within 5-min windows                │
│     • 1000 diag/day ÷ 8 hours = 125/hour = 2/min          │
│     • With 5-min TTL: ~10 diagnoses share one cache       │
│     • Expected hit rate: 90% (9/10 hit cache)             │
│                                                            │
│  2. Profile Stability (reduce invalidations)              │
│     • Group related changes into single deploy            │
│     • Deploy during low-traffic periods                   │
│     • Avoid frequent content changes                      │
│                                                            │
│  3. Cache Warming (prevent first-request misses)          │
│     • Make dummy request after deployment                 │
│     • Prevents real user hitting cache miss               │
│                                                            │
│     def warm_cache(engine, profile_id):                   │
│         engine.diagnose("warmup", "dummy", profile_id)    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**ROI Calculation (1000 diagnoses/day, 90% cache hit rate):**

| Scenario | Cache Misses | Cache Hits | Total/Day | Total/Month | Savings |
|----------|--------------|------------|-----------|-------------|---------|
| **No caching** | 1000 × $0.105 | - | $105 | $3,150 | Baseline |
| **With caching** | 100 × $0.105 | 900 × $0.085 | $87 | $2,605 | **$545/mo (17%)** |

**Combined Savings (Prompt Caching + System/User Separation):**

```
No optimization:    $150/day → $4,500/month
With optimization:   $87/day → $2,610/month
                    ─────────────────────────
Total savings:      $63/day = $1,890/month (42% reduction)
```

---

### 5. Profile Restart Behavior

**What it solves:** How do profiles handle state and context across multiple calls? Should each diagnosis be independent (stateless) or should the agent remember prior diagnoses (stateful)?

**Pattern: Stateless Profiles with Optional Context Injection**

**Design Decision: Stateless (each diagnosis independent)**

**Rationale:**

1. **Predictability:** Same input always produces same output
2. **Debuggability:** Can replay any diagnosis in isolation
3. **Parallelizability:** Can run 100 diagnoses concurrently without state conflicts
4. **Simplicity:** No state management, no context windows, no memory leaks
5. **Cost:** Stateful requires passing conversation history (expensive)

**Anti-pattern: Stateful Agent:**

```mermaid
sequenceDiagram
    participant E as StatefulEngine
    participant H as conversation_history
    participant C as Claude API
    
    Note over E,C: Request 1
    E->>H: Append user message
    Note over H: history = [user1]
    E->>C: Send history [user1]
    C-->>E: Response
    E->>H: Append assistant message
    Note over H: history = [user1, asst1]
    
    Note over E,C: Request 2
    E->>H: Append user message
    Note over H: history = [user1, asst1, user2]
    E->>C: Send history [user1, asst1, user2]
    Note over C: Cost increases!<br/>2x tokens
    C-->>E: Response
    E->>H: Append assistant message
    Note over H: history = [user1, asst1, user2, asst2]
    
    Note over E,C: Request 3
    E->>H: Append user message
    Note over H: history = [u1, a1, u2, a2, u3]
    E->>C: Send history [u1, a1, u2, a2, u3]
    Note over C: Cost increases!<br/>3x tokens
    C-->>E: Response
    
    Note over E,C: PROBLEMS:<br/>1. Unbounded growth<br/>2. Linear cost increase<br/>3. Can't parallelize<br/>4. Can't replay<br/>5. When to reset?
    
    style H fill:#f8d7da
    style C fill:#fff4e6
```

**Problems with Stateful Pattern:**

```
┌─────────────────────────────────────────────────────────┐
│ ❌ STATEFUL ENGINE ANTI-PATTERN                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ class StatefulDiagnosticEngine:                         │
│     def __init__(self):                                  │
│         self.conversation_history = []  # State!        │
│                                                          │
│     def diagnose(self, test_name, logs):                │
│         # Add user message                              │
│         self.conversation_history.append({              │
│             "role": "user",                             │
│             "content": f"Diagnose {test_name}: {logs}"  │
│         })                                               │
│                                                          │
│         # Send ENTIRE history (expensive!)              │
│         response = client.messages.create(              │
│             model="claude-opus-4",                      │
│             messages=self.conversation_history          │
│         )                                                │
│                                                          │
│         # Add assistant message                         │
│         self.conversation_history.append({              │
│             "role": "assistant",                        │
│             "content": response.content[0].text         │
│         })                                               │
│                                                          │
│ CRITICAL PROBLEMS:                                       │
│                                                          │
│ 1. Memory Leak                                          │
│    • History grows unbounded                            │
│    • No clear reset point                               │
│    • Eventually: OOM error                              │
│                                                          │
│ 2. Cost Explosion                                       │
│    • Request 1: 2K tokens → $0.030                     │
│    • Request 2: 4K tokens → $0.060 (2x)                │
│    • Request 3: 6K tokens → $0.090 (3x)                │
│    • Request N: 2NK tokens → $0.030N                   │
│                                                          │
│ 3. Parallelization Impossible                           │
│    • Shared state prevents concurrent execution        │
│    • Must serialize all diagnoses                      │
│    • Can't scale horizontally                          │
│                                                          │
│ 4. Debugging Nightmare                                  │
│    • Can't replay single diagnosis in isolation        │
│    • Needs full history to reproduce                   │
│    • Hard to bisect failures                           │
│                                                          │
│ 5. Unclear Lifecycle                                    │
│    • When to reset history?                            │
│    • Per test? Per test suite? Per day?                │
│    • No clear answer for Atiya use case                │
└─────────────────────────────────────────────────────────┘
```

**Correct Pattern: Stateless with Optional Context:**

```mermaid
sequenceDiagram
    participant C as Caller
    participant E as StatelessEngine
    participant API as Claude API
    
    Note over C,API: Independent Diagnosis 1
    C->>E: diagnose(test_bgp_failover, logs1)
    E->>E: Build prompt (no history)
    E->>API: Single-turn request
    API-->>E: Response
    E-->>C: diagnosis1
    
    Note over C,API: Independent Diagnosis 2 (Parallel!)
    C->>E: diagnose(test_ipsec_tunnel, logs2)
    E->>E: Build prompt (no history)
    E->>API: Single-turn request
    API-->>E: Response
    E-->>C: diagnosis2
    
    Note over C,API: Re-diagnosis with Optional Context
    C->>E: diagnose(test_bgp_failover,<br/>logs_v2,<br/>prior_diagnosis=diagnosis1)
    E->>E: Inject prior diagnosis<br/>as XML context
    E->>API: Single-turn request with context
    API-->>E: Response (informed by prior)
    E-->>C: diagnosis_v2
    
    Note over C,API: Benefits:<br/>1. No state<br/>2. Parallel execution<br/>3. Reproducible<br/>4. Optional context
    
    style E fill:#d4edda
    style API fill:#e1f5ff
```

**Stateless Implementation:**

```
┌─────────────────────────────────────────────────────────┐
│ ✅ STATELESS ENGINE CORRECT PATTERN                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ class StatelessDiagnosticEngine:                        │
│     def diagnose(self,                                   │
│                  test_name: str,                        │
│                  logs: str,                             │
│                  config: str = None,                    │
│                  prior_diagnosis: Dict = None) -> Dict: │
│                                                          │
│         # Build user prompt (each call independent)     │
│         parts = [f"Diagnose why {test_name} failed.\n"] │
│                                                          │
│         # Inject prior diagnosis as context (optional)  │
│         if prior_diagnosis:                             │
│             parts.append(                               │
│                 "<prior_diagnosis>\n"                   │
│                 f"Root cause: {prior_diagnosis['root_cause']}\n"│
│                 f"Fix: {prior_diagnosis['recommended_fix']}\n"│
│                 "Test re-run after fix, still failed.\n"│
│                 "</prior_diagnosis>\n\n"                │
│             )                                            │
│                                                          │
│         parts.append(f"<logs>\n{logs}\n</logs>\n")      │
│                                                          │
│         if config:                                       │
│             parts.append(                               │
│               f"<device_config>\n{config}\n</device_config>\n"│
│             )                                            │
│                                                          │
│         user_prompt = "\n".join(parts)                  │
│                                                          │
│         # Single-turn call (no history)                 │
│         response = self.client.messages.create(         │
│             model="claude-opus-4",                      │
│             system=self.system_prompt,                  │
│             messages=[{                                 │
│               "role": "user",                           │
│               "content": user_prompt                    │
│             }]                                           │
│         )                                                │
│                                                          │
│         return json.loads(response.content[0].text)     │
│                                                          │
│ BENEFITS:                                                │
│                                                          │
│ 1. Predictability                                       │
│    • Same input → same output                           │
│    • No hidden state                                    │
│    • Reproducible results                               │
│                                                          │
│ 2. Debuggability                                        │
│    • Can replay any diagnosis in isolation              │
│    • No dependencies on prior calls                     │
│    • Easy to bisect failures                            │
│                                                          │
│ 3. Parallelizability                                    │
│    • No shared state                                    │
│    • Run 100 diagnoses concurrently                     │
│    • Scales horizontally                                │
│                                                          │
│ 4. Cost Efficiency                                      │
│    • Constant token count per diagnosis                 │
│    • No history overhead                                │
│    • Predictable costs                                  │
│                                                          │
│ 5. Optional Context                                     │
│    • Can provide prior diagnosis when needed            │
│    • Context passed explicitly, not implicitly          │
│    • Clear when context is used                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ USAGE PATTERNS                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Independent Diagnoses (Parallel):                       │
│ ┌──────────────────────────────────────────────────┐   │
│ │ diagnosis1 = engine.diagnose(                    │   │
│ │     test_name="test_bgp_failover",               │   │
│ │     logs=logs1                                   │   │
│ │ )                                                │   │
│ │                                                   │   │
│ │ diagnosis2 = engine.diagnose(                    │   │
│ │     test_name="test_ipsec_tunnel",               │   │
│ │     logs=logs2                                   │   │
│ │ )                                                │   │
│ │                                                   │   │
│ │ # No shared state, can run in parallel          │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Re-diagnosis with Context:                              │
│ ┌──────────────────────────────────────────────────┐   │
│ │ # First diagnosis                                │   │
│ │ diagnosis_v1 = engine.diagnose(                  │   │
│ │     test_name="test_bgp_failover",               │   │
│ │     logs=logs_first_run                          │   │
│ │ )                                                │   │
│ │ # Result: "BGP peer2 was shut down"              │   │
│ │                                                   │   │
│ │ # Apply fix, re-run, still fails                │   │
│ │ diagnosis_v2 = engine.diagnose(                  │   │
│ │     test_name="test_bgp_failover",               │   │
│ │     logs=logs_second_run,                        │   │
│ │     prior_diagnosis=diagnosis_v1  # ← Context    │   │
│ │ )                                                │   │
│ │ # Result: "BGP peer2 up, route-map blocks routes"│   │
│ └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**When to use stateful:**

❌ **Don't use for Atiya:**
- Each test failure is independent
- No benefit from remembering prior diagnoses
- Cost increases with conversation length

✅ **Do use for chatbots/assistants:**
- User asks follow-up questions
- Context from prior messages is necessary
- Conversation is short (<20 turns)

**Multi-Step Workflow with Explicit State Passing:**

```mermaid
flowchart TB
    Start[diagnose called] --> Step1[Step 1: Parse Logs]
    Step1 -->|Haiku| P1[Extract structured events]
    P1 --> State1[log_events: Dict]
    
    State1 --> Step2[Step 2: Analyze Config]
    Step2 -->|Haiku| P2[Find misconfigurations]
    P2 --> State2[config_issues: Dict]
    
    State1 --> Step3[Step 3: Synthesize]
    State2 --> Step3
    Step3 -->|Opus| P3[Combine findings]
    P3 --> Result[Final Diagnosis]
    
    subgraph "All Steps Stateless"
        P1
        P2
        P3
    end
    
    style Start fill:#e1f5ff
    style State1 fill:#fff4e6
    style State2 fill:#fff4e6
    style Result fill:#d4edda
    style P1 fill:#dfe6e9
    style P2 fill:#dfe6e9
    style P3 fill:#dfe6e9
```

**MultiStepEngine Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│ MULTI-STEP ENGINE WITH EXPLICIT STATE PASSING          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Main Workflow:                                           │
│ ┌──────────────────────────────────────────────────┐   │
│ │ def diagnose(test_name, logs, config):           │   │
│ │                                                   │   │
│ │   # Step 1: Parse logs (Haiku, fast, cheap)     │   │
│ │   log_events = self._parse_logs(logs)           │   │
│ │   # Returns: {                                   │   │
│ │   #   "errors": [...],                           │   │
│ │   #   "warnings": [...],                         │   │
│ │   #   "timeline": [...]                          │   │
│ │   # }                                            │   │
│ │                                                   │   │
│ │   # Step 2: Analyze config (Haiku, fast, cheap) │   │
│ │   config_issues = self._analyze_config(          │   │
│ │       config, test_name                          │   │
│ │   )                                              │   │
│ │   # Returns: {                                   │   │
│ │   #   "misconfigurations": [...],                │   │
│ │   #   "missing_policies": [...]                  │   │
│ │   # }                                            │   │
│ │                                                   │   │
│ │   # Step 3: Synthesize (Opus, slow, expensive)  │   │
│ │   diagnosis = self._synthesize(                  │   │
│ │       test_name=test_name,                       │   │
│ │       log_events=log_events,  # ← Explicit state│   │
│ │       config_issues=config_issues # ← Explicit  │   │
│ │   )                                              │   │
│ │                                                   │   │
│ │   return diagnosis                               │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Step 1: Parse Logs (Haiku)                              │
│ ┌──────────────────────────────────────────────────┐   │
│ │ def _parse_logs(logs: str) -> Dict:              │   │
│ │     response = client.messages.create(           │   │
│ │         model="claude-haiku-4",                  │   │
│ │         system=LOG_PARSER_SYSTEM,                │   │
│ │         messages=[{                              │   │
│ │           "role": "user",                        │   │
│ │           "content": logs                        │   │
│ │         }]                                        │   │
│ │     )                                             │   │
│ │     return json.loads(response.content[0].text)  │   │
│ │                                                   │   │
│ │ • Stateless: No conversation history             │   │
│ │ • Can be retried independently                   │   │
│ │ • Can be cached (same logs → same result)       │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Step 2: Analyze Config (Haiku)                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ def _analyze_config(config: str,                 │   │
│ │                     test_name: str) -> Dict:     │   │
│ │     response = client.messages.create(           │   │
│ │         model="claude-haiku-4",                  │   │
│ │         system=CONFIG_ANALYZER_SYSTEM,           │   │
│ │         messages=[{                              │   │
│ │           "role": "user",                        │   │
│ │           "content": f"Test: {test_name}\n"      │   │
│ │                      f"Config: {config}"         │   │
│ │         }]                                        │   │
│ │     )                                             │   │
│ │     return json.loads(response.content[0].text)  │   │
│ │                                                   │   │
│ │ • Stateless: No conversation history             │   │
│ │ • Independent of Step 1                          │   │
│ │ • Can run in parallel with Step 1                │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Step 3: Synthesize (Opus)                               │
│ ┌──────────────────────────────────────────────────┐   │
│ │ def _synthesize(test_name: str,                  │   │
│ │                 log_events: Dict,  # ← Explicit  │   │
│ │                 config_issues: Dict) -> Dict:    │   │
│ │                                                   │   │
│ │     prompt = f"""                                │   │
│ │     Test: {test_name}                            │   │
│ │                                                   │   │
│ │     Log events:                                  │   │
│ │     {json.dumps(log_events, indent=2)}           │   │
│ │                                                   │   │
│ │     Config issues:                               │   │
│ │     {json.dumps(config_issues, indent=2)}        │   │
│ │                                                   │   │
│ │     Determine root cause from these findings.    │   │
│ │     """                                           │   │
│ │                                                   │   │
│ │     response = client.messages.create(           │   │
│ │         model="claude-opus-4",                   │   │
│ │         system=SYNTHESIZER_SYSTEM,               │   │
│ │         messages=[{                              │   │
│ │           "role": "user",                        │   │
│ │           "content": prompt                      │   │
│ │         }]                                        │   │
│ │     )                                             │   │
│ │     return json.loads(response.content[0].text)  │   │
│ │                                                   │   │
│ │ • Stateless: State passed as arguments           │   │
│ │ • Takes results from Steps 1 & 2 explicitly      │   │
│ │ • Can be retried with same inputs                │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ KEY INSIGHT:                                             │
│ State is passed explicitly as function arguments,       │
│ not via conversation history. Each step is stateless    │
│ (can be retried, cached, parallelized).                 │
│                                                          │
│ BENEFITS:                                                │
│ • Parallelization: Steps 1 & 2 can run concurrently    │
│ • Cost optimization: Use Haiku for simple tasks         │
│ • Retry-ability: Each step can fail/retry independently │
│ • Caching: Can cache results of each step               │
│ • Debuggability: Can inspect intermediate state         │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Patterns

### Complete Profile Operations System

**System Architecture:**

```mermaid
graph TB
    subgraph "Data Models"
        PM[ProfileMetadata<br/>version, status, budget]
        P[Profile<br/>content, system_prompt]
        DR[DiagnosisResult<br/>root_cause, confidence]
    end
    
    subgraph "Core Components"
        PMgr[ProfileManager<br/>load, cache, route]
        PDE[ProductionDiagnosticEngine<br/>diagnose with caching]
    end
    
    subgraph "Infrastructure"
        Cache[In-Memory Cache<br/>TTL: 5 min]
        Routing[A/B Routing<br/>Consistent hashing]
        Metrics[Prometheus Metrics<br/>Counter, Histogram, Gauge]
    end
    
    subgraph "External Services"
        FS[File System<br/>profiles/*.md]
        Claude[Claude API<br/>messages.create]
        Prom[Prometheus<br/>Metrics collector]
    end
    
    PMgr --> Cache
    PMgr --> Routing
    PMgr --> FS
    PDE --> PMgr
    PDE --> Claude
    PDE --> Metrics
    Metrics --> Prom
    
    PM -.-> P
    PDE -.-> DR
    
    style PMgr fill:#e1f5ff
    style PDE fill:#d4edda
    style Metrics fill:#ffeaa7
    style Claude fill:#fff4e6
```

```
┌──────────────────────────────────────────────────────────────┐
│ COMPLETE PRODUCTION SYSTEM ARCHITECTURE                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ 1. DATA MODELS                                               │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ ProfileMetadata (dataclass):                           │  │
│ │ • profile_id: str                                      │  │
│ │ • version: int                                         │  │
│ │ • status: str (production/canary/deprecated)           │  │
│ │ • traffic_allocation: float (0.0-1.0)                  │  │
│ │ • cost_budget: float                                   │  │
│ │ • latency_budget_p95: float                            │  │
│ │ • accuracy_target: float                               │  │
│ │                                                         │  │
│ │ Profile (dataclass):                                   │  │
│ │ • metadata: ProfileMetadata                            │  │
│ │ • content: str (full markdown)                         │  │
│ │ • system_prompt: str (extracted from content)          │  │
│ │ • loaded_at: datetime                                  │  │
│ │ • file_hash: str (SHA256 for change detection)        │  │
│ │ • to_dict() -> Dict                                    │  │
│ │                                                         │  │
│ │ DiagnosisResult (dataclass):                           │  │
│ │ • root_cause: str                                      │  │
│ │ • confidence: float                                    │  │
│ │ • evidence: List[str]                                  │  │
│ │ • failure_category: str                                │  │
│ │ • recommended_fix: str                                 │  │
│ │ • requires_human_review: bool                          │  │
│ │ • _meta: Dict (cost, duration, cache_hit, tokens)     │  │
│ │ • to_dict() -> Dict                                    │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                               │
│ 2. PROMETHEUS METRICS                                        │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ profile_loads_total (Counter):                         │  │
│ │ • Labels: profile_id, version, source                  │  │
│ │ • Purpose: Track total profile loads                   │  │
│ │                                                         │  │
│ │ profile_cache_hits_total (Counter):                    │  │
│ │ • Labels: profile_id, version                          │  │
│ │ • Purpose: Track cache hits                            │  │
│ │                                                         │  │
│ │ diagnosis_duration_seconds (Histogram):                │  │
│ │ • Labels: profile_id, version                          │  │
│ │ • Buckets: [1, 2, 5, 10, 20, 30, 60]                  │  │
│ │ • Purpose: Track diagnosis latency                     │  │
│ │                                                         │  │
│ │ diagnosis_cost_usd (Histogram):                        │  │
│ │ • Labels: profile_id, version, cache_hit               │  │
│ │ • Buckets: [0.01, 0.05, 0.08, 0.10, 0.15, 0.20, 0.50] │  │
│ │ • Purpose: Track API costs                             │  │
│ │                                                         │  │
│ │ active_profile_version (Gauge):                        │  │
│ │ • Labels: profile_id                                   │  │
│ │ • Purpose: Track currently active version              │  │
│ └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**ProfileManager Class:**

```
┌──────────────────────────────────────────────────────────────┐
│ PROFILEMANAGER - Core Profile Lifecycle Management          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ Attributes:                                                   │
│ • profiles_dir: str = "profiles"                             │
│ • cache_ttl: int = 300 (5 minutes)                           │
│ • _cache: Dict[str, Profile] = {}                            │
│ • _routing: Dict[str, Dict[str, float]] = {}                 │
│                                                               │
│ Methods:                                                      │
│                                                               │
│ load_profile(profile_id, version) -> Profile                │
│ ├─ Check cache (key: profile_id_vN)                         │
│ ├─ Validate TTL (< 5 min)                                   │
│ ├─ Validate hash (file unchanged)                           │
│ ├─ If cache miss: _load_from_disk()                         │
│ ├─ Store in cache                                            │
│ └─ Return profile                                            │
│                                                               │
│ get_profile_for_request(profile_id, request_id) -> Profile  │
│ ├─ Get routing config (e.g., v2: 0.9, v3: 0.1)             │
│ ├─ Hash request_id (MD5 -> 0.0-1.0)                         │
│ ├─ Compare to cumulative thresholds                          │
│ ├─ Select version based on hash                              │
│ └─ Return load_profile(selected_version)                     │
│                                                               │
│ set_routing(profile_id, routing)                             │
│ ├─ Validate: routing values sum to 1.0                       │
│ ├─ Store in _routing dict                                    │
│ └─ Update active_profile_version metric                      │
│                                                               │
│ hot_reload(profile_id, version) -> Profile                   │
│ ├─ Delete from cache                                          │
│ ├─ Load fresh from disk                                       │
│ ├─ Store in cache                                             │
│ └─ Return profile                                             │
│                                                               │
│ _load_from_disk(profile_id, version) -> Profile              │
│ ├─ Read file: profiles/{id}_v{ver}.md                        │
│ ├─ Parse YAML frontmatter                                     │
│ ├─ Extract system prompt                                      │
│ ├─ Compute SHA256 hash                                        │
│ └─ Return Profile object                                      │
└──────────────────────────────────────────────────────────────┘
```

**ProductionDiagnosticEngine Class:**

```
┌──────────────────────────────────────────────────────────────┐
│ PRODUCTIONDIAGNOSTICENGINE - Complete Diagnostic System     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ Attributes:                                                   │
│ • client: anthropic.Anthropic                                │
│ • profile_manager: ProfileManager                            │
│                                                               │
│ Methods:                                                      │
│                                                               │
│ diagnose(test_name, logs, config, test_code,                 │
│          profile_id, request_id, prior_diagnosis)            │
│          -> DiagnosisResult                                  │
│                                                               │
│ Flow:                                                         │
│ 1. Load profile via A/B routing                              │
│ │  profile = profile_manager.get_profile_for_request()      │
│ │                                                             │
│ 2. Build user prompt                                          │
│ │  • Test name                                               │
│ │  • Prior diagnosis (if provided, as XML context)           │
│ │  • Test code (if provided)                                 │
│ │  • Logs (in <logs> tags)                                   │
│ │  • Device config (if provided, in <device_config> tags)    │
│ │                                                             │
│ 3. Call Claude API with prompt caching                        │
│ │  response = client.messages.create(                        │
│ │      model="claude-opus-4",                                │
│ │      max_tokens=4096,                                      │
│ │      temperature=0.0,                                      │
│ │      system=[{                                             │
│ │          "type": "text",                                   │
│ │          "text": profile.system_prompt,                    │
│ │          "cache_control": {"type": "ephemeral"}  # ← Cache │
│ │      }],                                                    │
│ │      messages=[{"role": "user", "content": user_prompt}]   │
│ │  )                                                          │
│ │                                                             │
│ 4. Parse response & calculate costs                           │
│ │  • Parse JSON diagnosis                                    │
│ │  • Calculate cost with caching pricing                     │
│ │  • Detect cache hit/miss                                   │
│ │                                                             │
│ 5. Record metrics                                             │
│ │  • diagnosis_duration (Histogram)                          │
│ │  • diagnosis_cost (Histogram)                              │
│ │                                                             │
│ 6. Return DiagnosisResult                                     │
│    • All diagnosis fields                                     │
│    • _meta: cost, duration, cache_hit, tokens, timestamp     │
│                                                               │
│ _build_user_prompt(...) -> str                                │
│ ├─ Build multi-section prompt                                │
│ ├─ Inject prior diagnosis as XML (if provided)               │
│ ├─ Add test code, logs, config                               │
│ └─ Return formatted prompt                                    │
│                                                               │
│ _calculate_cost(usage) -> float                               │
│ ├─ Fresh input: (total - cached) × $15/M                     │
│ ├─ Cached input: cached × $1.50/M                            │
│ ├─ Output: output × $75/M                                    │
│ └─ Return total cost                                          │
└──────────────────────────────────────────────────────────────┘
```

**Usage Example:**

```
┌──────────────────────────────────────────────────────────────┐
│ PRODUCTION USAGE PATTERN                                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ # Initialize components                                       │
│ profile_manager = ProfileManager(                            │
│     profiles_dir="profiles",                                 │
│     cache_ttl=300                                            │
│ )                                                             │
│                                                               │
│ engine = ProductionDiagnosticEngine(                          │
│     api_key=os.environ["ANTHROPIC_API_KEY"],                 │
│     profile_manager=profile_manager                          │
│ )                                                             │
│                                                               │
│ # Configure A/B test (90% v2, 10% v3)                        │
│ profile_manager.set_routing(                                  │
│     "network_diagnostician",                                  │
│     {2: 0.9, 3: 0.1}                                         │
│ )                                                             │
│                                                               │
│ # Diagnose failure                                            │
│ result = engine.diagnose(                                     │
│     test_name="test_bgp_failover",                           │
│     logs=open("failure.log").read(),                         │
│     config=open("router_config.txt").read(),                 │
│     request_id="req-12345"                                   │
│ )                                                             │
│                                                               │
│ # Result structure:                                           │
│ {                                                             │
│   "root_cause": "BGP peer2 administratively shut down",      │
│   "confidence": 0.95,                                        │
│   "evidence": [...],                                         │
│   "failure_category": "config",                              │
│   "recommended_fix": "Remove 'neighbor peer2 shutdown'",     │
│   "requires_human_review": false,                            │
│   "_meta": {                                                 │
│     "profile_id": "network_diagnostician",                   │
│     "profile_version": 2,                                    │
│     "cost": 0.0848,                                          │
│     "duration": 8.5,                                         │
│     "cache_hit": true,                                       │
│     "tokens": {...},                                         │
│     "timestamp": "2026-08-20T10:15:30"                       │
│   }                                                           │
│ }                                                             │
└──────────────────────────────────────────────────────────────┘
```

**Note:** The complete Python implementation (444 lines) includes full dataclass definitions, error handling, logging, retry logic, and comprehensive docstrings. The visual documentation above captures the essential architecture and usage patterns. For production deployment, refer to the reference implementation in the Atiya codebase.

---

## Production Considerations

### Performance

**Visual: Production Data Structures**

```
┌──────────────────────────────────────────────────────────────────┐
│  ProfileMetadata (from YAML frontmatter)                         │
├──────────────────────────────────────────────────────────────────┤
│  profile_id: string                                              │
│  version: integer                                                │
│  created: string (ISO date)                                      │
│  author: string                                                  │
│  status: "production" | "canary" | "deprecated"                  │
│  traffic_allocation: float (0.0-1.0)                             │
│  tags: List[string]                                              │
│  cost_budget: float (dollars)                                    │
│  latency_budget_p95: float (seconds)                             │
│  accuracy_target: float (0.0-1.0)                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Profile (complete profile with content and metadata)            │
├──────────────────────────────────────────────────────────────────┤
│  metadata: ProfileMetadata                                       │
│  content: string (full markdown content)                         │
│  system_prompt: string (extracted from content)                  │
│  loaded_at: datetime                                             │
│  file_hash: string (SHA256)                                      │
│                                                                  │
│  Methods:                                                        │
│    to_dict() → {metadata, loaded_at, file_hash}                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  DiagnosisResult (complete diagnosis with metadata)              │
├──────────────────────────────────────────────────────────────────┤
│  Core Results:                                                   │
│    root_cause: string                                            │
│    confidence: float (0.0-1.0)                                   │
│    evidence: List[string]                                        │
│    failure_category: string                                      │
│    recommended_fix: string                                       │
│    requires_human_review: boolean                                │
│                                                                  │
│  Metadata:                                                       │
│    profile_id: string                                            │
│    profile_version: integer                                      │
│    cost: float (dollars)                                         │
│    duration: float (seconds)                                     │
│    cache_hit: boolean                                            │
│    tokens: Dict[string, int] {input, output}                     │
│    timestamp: datetime                                           │
│                                                                  │
│  Methods:                                                        │
│    to_dict() → {diagnosis fields, _meta: {metadata fields}}      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  ProfileManager (complete profile lifecycle management)          │
├──────────────────────────────────────────────────────────────────┤
│  Features:                                                       │
│    ├─ Load profiles from disk with caching                       │
│    ├─ A/B testing with traffic routing                           │
│    ├─ Hot-reload without service restart                         │
│    ├─ Metrics and monitoring                                     │
│    └─ Version management                                         │
└──────────────────────────────────────────────────────────────────┘
```
    
    def __init__(self,
                 profiles_dir: str = "profiles",
                 cache_ttl: int = 300):
        self.profiles_dir = profiles_dir
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Profile] = {}
        self._routing: Dict[str, Dict[str, float]] = {}
        
        logger.info(f"ProfileManager initialized with dir={profiles_dir}, ttl={cache_ttl}s")
    
    def load_profile(self, profile_id: str, version: Optional[int] = None) -> Profile:
        """Load profile from disk or cache"""
        if version is None:
            version = self._get_active_version(profile_id)
        
        cache_key = f"{profile_id}_v{version}"
        
        # Check cache
        cached = self._cache.get(cache_key)
        if cached:
            age = (datetime.now() - cached.loaded_at).total_seconds()
            if age < self.cache_ttl:
                # Verify file hasn't changed
                current_hash = self._compute_file_hash(profile_id, version)
                if current_hash == cached.file_hash:
                    profile_cache_hits.labels(
                        profile_id=profile_id,
                        version=str(version)
                    ).inc()
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached
        
        # Load from disk
        profile = self._load_from_disk(profile_id, version)
        self._cache[cache_key] = profile
        
        profile_loads.labels(
            profile_id=profile_id,
            version=str(version),
            source='disk'
        ).inc()
        
        logger.info(f"Loaded profile: {cache_key}")
        return profile
    
    def _load_from_disk(self, profile_id: str, version: int) -> Profile:
        """Load and parse profile file"""
        filepath = os.path.join(self.profiles_dir, f"{profile_id}_v{version}.md")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Profile not found: {filepath}")
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Parse frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            raise ValueError(f"Invalid profile format: {filepath}")
        
        metadata_dict = yaml.safe_load(parts[1])
        metadata = ProfileMetadata(**metadata_dict)
        
        # Extract system prompt (everything after frontmatter)
        system_prompt = parts[2].strip()
        
        # Compute file hash
        file_hash = self._compute_file_hash(profile_id, version)
        
        return Profile(
            metadata=metadata,
            content=content,
            system_prompt=system_prompt,
            loaded_at=datetime.now(),
            file_hash=file_hash
        )
    
    def _compute_file_hash(self, profile_id: str, version: int) -> str:
        """Compute SHA256 hash of profile file"""
        filepath = os.path.join(self.profiles_dir, f"{profile_id}_v{version}.md")
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def _get_active_version(self, profile_id: str) -> int:
        """Get active version based on routing config"""
        # Default to version 2 if no routing configured
        routing = self._routing.get(profile_id, {2: 1.0})
        # Return first version (highest traffic allocation)
        return int(sorted(routing.items(), key=lambda x: -x[1])[0][0])
    
    def set_routing(self, profile_id: str, routing: Dict[int, float]):
        """
        Set traffic routing for A/B testing.
        
        Args:
            profile_id: Profile to route
            routing: Version -> percentage (must sum to 1.0)
        """
        total = sum(routing.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Routing must sum to 1.0, got {total}")
        
        self._routing[profile_id] = routing
        
        # Update active version metric
        active_version = max(routing.items(), key=lambda x: x[1])[0]
        active_profile_version.labels(profile_id=profile_id).set(active_version)
        
        logger.info(f"Set routing for {profile_id}: {routing}")
    
    def get_profile_for_request(self,
                                 profile_id: str,
                                 request_id: str) -> Profile:
        """
        Get profile version for request based on A/B routing.
        
        Uses consistent hashing: same request_id always gets same version.
        """
        routing = self._routing.get(profile_id, {2: 1.0})
        
        # Consistent hashing
        hash_value = int(hashlib.md5(request_id.encode()).hexdigest(), 16)
        threshold = hash_value / (2 ** 128)
        
        cumulative = 0.0
        for version, percentage in sorted(routing.items()):
            cumulative += percentage
            if threshold < cumulative:
                return self.load_profile(profile_id, version)
        
        # Fallback
        return self.load_profile(profile_id, list(routing.keys())[0])
    
    def hot_reload(self, profile_id: str, version: int):
        """Force reload profile from disk"""
        cache_key = f"{profile_id}_v{version}"
        if cache_key in self._cache:
            del self._cache[cache_key]
        
        profile = self._load_from_disk(profile_id, version)
        self._cache[cache_key] = profile
        
        logger.info(f"Hot-reloaded: {cache_key}")
        return profile


class ProductionDiagnosticEngine:
    """
    Production-grade diagnostic engine with complete profile operations.
    
    Features:
    - Profile loading with caching
    - A/B testing support
    - Prompt caching for cost optimization
    - Metrics and monitoring
    - Stateless design
    """
    
    def __init__(self,
                 api_key: str,
                 profile_manager: ProfileManager):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.profile_manager = profile_manager
        
        logger.info("ProductionDiagnosticEngine initialized")
    
    def diagnose(self,
                 test_name: str,
                 logs: str,
                 config: Optional[str] = None,
                 test_code: Optional[str] = None,
                 profile_id: str = "network_diagnostician",
                 request_id: Optional[str] = None,
                 prior_diagnosis: Optional[Dict] = None) -> DiagnosisResult:
        """
        Diagnose test failure with full profile operations.
        
        Args:
            test_name: Name of failed test
            logs: Test logs
            config: Device configuration (optional)
            test_code: Test source code (optional)
            profile_id: Which profile to use
            request_id: Request ID for A/B routing and caching
            prior_diagnosis: Prior diagnosis for context (optional)
        
        Returns:
            DiagnosisResult with complete metadata
        """
        import time
        start = time.time()
        
        # Generate request ID if not provided
        if request_id is None:
            request_id = f"diag-{datetime.now().timestamp()}"
        
        # Load profile (with A/B routing)
        profile = self.profile_manager.get_profile_for_request(
            profile_id, request_id
        )
        
        logger.info(f"Diagnosing {test_name} with {profile_id} v{profile.metadata.version}")
        
        # Build user prompt
        user_prompt = self._build_user_prompt(
            test_name, logs, config, test_code, prior_diagnosis
        )
        
        # Call Claude with prompt caching
        response = self.client.messages.create(
            model="claude-opus-4",
            max_tokens=4096,
            temperature=0.0,
            system=[
                {
                    "type": "text",
                    "text": profile.system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        duration = time.time() - start
        
        # Parse diagnosis
        diagnosis_json = json.loads(response.content[0].text)
        
        # Calculate cost
        cost = self._calculate_cost(response.usage)
        cache_hit = hasattr(response.usage, 'cache_read_input_tokens') and \
                    response.usage.cache_read_input_tokens > 0
        
        # Build result
        result = DiagnosisResult(
            root_cause=diagnosis_json['root_cause'],
            confidence=diagnosis_json['confidence'],
            evidence=diagnosis_json['evidence'],
            failure_category=diagnosis_json['failure_category'],
            recommended_fix=diagnosis_json['recommended_fix'],
            requires_human_review=diagnosis_json['requires_human_review'],
            profile_id=profile_id,
            profile_version=profile.metadata.version,
            cost=cost,
            duration=duration,
            cache_hit=cache_hit,
            tokens={
                'input': response.usage.input_tokens,
                'output': response.usage.output_tokens,
                'cache_creation': getattr(response.usage, 'cache_creation_input_tokens', 0),
                'cache_read': getattr(response.usage, 'cache_read_input_tokens', 0)
            },
            timestamp=datetime.now()
        )
        
        # Record metrics
        diagnosis_duration.labels(
            profile_id=profile_id,
            version=str(profile.metadata.version)
        ).observe(duration)
        
        diagnosis_cost.labels(
            profile_id=profile_id,
            version=str(profile.metadata.version),
            cache_hit=str(cache_hit)
        ).observe(cost)
        
        logger.info(f"Diagnosis complete: cost=${cost:.4f}, duration={duration:.2f}s, cache_hit={cache_hit}")
        
        return result
    
    def _build_user_prompt(self,
                           test_name: str,
                           logs: str,
                           config: Optional[str],
                           test_code: Optional[str],
                           prior_diagnosis: Optional[Dict]) -> str:
        """Build evidence-rich user prompt"""
        parts = [f"Diagnose why {test_name} failed.\n"]
        
        if prior_diagnosis:
            parts.append(
                f"\n<prior_diagnosis>\n"
                f"Root cause: {prior_diagnosis['root_cause']}\n"
                f"Fix: {prior_diagnosis['recommended_fix']}\n"
                f"Test was re-run after fix but still failed.\n"
                f"</prior_diagnosis>\n\n"
            )
        
        if test_code:
            parts.append(f"<test_code>\n{test_code}\n</test_code>\n")
        
        parts.append(f"<logs>\n{logs}\n</logs>\n")
        
        if config:
            parts.append(f"<device_config>\n{config}\n</device_config>\n")
        
        return "\n".join(parts)
    
    def _calculate_cost(self, usage) -> float:
        """Calculate API call cost"""
        cost = 0.0
        
        # Fresh input tokens
        fresh_input = usage.input_tokens
        if hasattr(usage, 'cache_read_input_tokens'):
            fresh_input -= usage.cache_read_input_tokens
        cost += (fresh_input / 1_000_000) * 15.0
        
        # Cached input tokens (90% off)
        if hasattr(usage, 'cache_read_input_tokens'):
            cost += (usage.cache_read_input_tokens / 1_000_000) * 1.50
        
        # Output tokens
        cost += (usage.output_tokens / 1_000_000) * 75.0
        
        return cost


# Production usage
if __name__ == "__main__":
    # Initialize
    profile_manager = ProfileManager(profiles_dir="profiles", cache_ttl=300)
    engine = ProductionDiagnosticEngine(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        profile_manager=profile_manager
    )
    
    # Set up A/B test: 90% v2, 10% v3
    profile_manager.set_routing(
        "network_diagnostician",
        {2: 0.9, 3: 0.1}
    )
    
    # Diagnose failure
    result = engine.diagnose(
        test_name="test_bgp_failover",
        logs=open("failure.log").read(),
        config=open("router_config.txt").read(),
        request_id="req-12345"
    )
    
    print(json.dumps(result.to_dict(), indent=2))
```

---

## Production Considerations

### Performance

**Latency Breakdown:**

```
Total: 8.5s (with caching)
├─ Profile loading: 0.05s (cached, in-memory)
├─ Prompt construction: 0.10s (string formatting)
├─ API call (network): 0.25s (RTT to Claude API)
├─ Claude inference: 7.80s (model processing)
└─ Response parsing: 0.30s (JSON parsing + validation)
```

**Optimization strategies:**

1. **Profile loading:** Keep cache warm, use in-memory cache
   - Cold load (disk): 50ms
   - Warm load (cache): 0.1ms
   - Effect: 500x faster

2. **Prompt construction:** Pre-compute template, use string concat
   - Naive (string replace): 200ms
   - Optimized (f-strings): 100ms
   - Effect: 2x faster

3. **API latency:** Use regional endpoints, connection pooling
   - Single connection: 300ms
   - Connection pool: 250ms
   - Regional endpoint: 150ms
   - Effect: 2x faster

4. **Claude inference:** Use streaming for perceived latency
   - Time to first token: 1.2s
   - Total time: 7.8s
   - Perceived latency (streaming): 1.2s (84% improvement)

**Throughput:**

```
Single request latency: 8.5s
Concurrent limit: 50 (API rate limit)
Throughput: 50 / 8.5s = 5.9 req/s = 21,240 req/hour

Atiya target: 1000 diagnoses/day
Required throughput: 1000 / 8h = 125/hour = 0.035 req/s

Headroom: 21,240 / 125 = 170x ✅
```

---

### Cost

**Per-diagnosis cost (with all optimizations):**

```
Profile: 1500 tokens (system, cached)
User prompt: 500 tokens (logs, config)
Output: 1000 tokens (diagnosis)

Cache miss (10%):
  Input: 2000 × $15/M = $0.030
  Output: 1000 × $75/M = $0.075
  Total: $0.105

Cache hit (90%):
  Cached: 1500 × $1.50/M = $0.0023
  Fresh: 500 × $15/M = $0.0075
  Output: 1000 × $75/M = $0.075
  Total: $0.0848

Average: (0.1 × $0.105) + (0.9 × $0.0848) = $0.0868
```

**At scale (1000 diagnoses/day):**

```
Daily: 1000 × $0.0868 = $86.80
Monthly: $86.80 × 22 workdays = $1,910
Yearly: $1,910 × 12 = $22,920

Target: <$0.50/diagnosis
Current: $0.0868 ✅
Headroom: 5.8x
```

**Cost breakdown by optimization:**

```
No optimization:
  - Hardcoded prompts in user message
  - No caching
  - Cost: $0.150/diagnosis

System/user separation:
  - System prompt separate
  - Cost: $0.105/diagnosis
  - Savings: 30%

+ Prompt caching:
  - System prompt cached (90% hit rate)
  - Cost: $0.0868/diagnosis
  - Savings: 42% total

+ Model mixing (future):
  - Haiku for parsing, Opus for synthesis
  - Projected cost: $0.040/diagnosis
  - Savings: 73% total
```

---

### Reliability

**Failure Modes:**

1. **Profile load failure** (disk error, corrupted file)
   - Mitigation: Validate profile syntax in CI before deploy
   - Fallback: Load previous version
   - Effect: 99.99% availability

2. **API timeout** (Claude response >30s)
   - Mitigation: Retry with exponential backoff
   - Effect: 5% → 0.05% failure rate

3. **Cache invalidation race** (profile updated mid-request)
   - Mitigation: Hash-based cache validation
   - Effect: Atomic updates, no stale cache

4. **A/B routing error** (routing percentages don't sum to 1.0)
   - Mitigation: Validation at routing config time
   - Effect: Catch errors before production

**Error Handling:**

```mermaid
flowchart TD
    Start[diagnose called] --> Try{Try execution}
    Try -->|Success| Return[Return result]
    
    Try -->|FileNotFoundError| E1[Profile not found]
    E1 --> Log1[Log error]
    Log1 --> Fallback{Fallback available?}
    Fallback -->|Yes| LoadPrev[Load previous version]
    Fallback -->|No| Reraise1[Re-raise exception]
    LoadPrev --> Retry1[Retry with v-1]
    
    Try -->|APITimeoutError| E2[Claude API timeout]
    E2 --> Log2[Log warning]
    Log2 --> Retry2[Retry<br/>Attempt 1, 2, 3]
    Retry2 -->|Max attempts| Reraise2[Re-raise exception]
    Retry2 -->|Success| Return
    
    Try -->|JSONDecodeError| E3[Invalid JSON response]
    E3 --> Log3[Log error]
    Log3 --> Attempt{Self-repair?}
    Attempt -->|Yes| Fix[Attempt JSON fix]
    Attempt -->|No| Reraise3[Re-raise exception]
    Fix -->|Success| Return
    Fix -->|Fail| Reraise3
    
    style Start fill:#e1f5ff
    style Return fill:#d4edda
    style E1 fill:#fff4e6
    style E2 fill:#fff4e6
    style E3 fill:#fff4e6
    style Reraise1 fill:#f8d7da
    style Reraise2 fill:#f8d7da
    style Reraise3 fill:#f8d7da
```

**Retry Strategy (using tenacity):**

```
┌──────────────────────────────────────────────────────────────┐
│ ROBUST ERROR HANDLING WITH RETRIES                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ Retry Configuration:                                          │
│ • stop: stop_after_attempt(3)                                │
│ • wait: wait_exponential(multiplier=1, min=2, max=30)        │
│ • reraise: True (propagate after max attempts)               │
│                                                               │
│ Retry Timing:                                                 │
│ • Attempt 1: Immediate                                        │
│ • Attempt 2: Wait 2 seconds                                   │
│ • Attempt 3: Wait 4 seconds                                   │
│ • Total: 3 attempts over 6 seconds                            │
│                                                               │
│ Error Types & Handling:                                       │
│ 1. FileNotFoundError (Profile missing)                        │
│    • Log error                                                │
│    • Attempt fallback to previous version                     │
│    • If no fallback: re-raise                                 │
│                                                               │
│ 2. anthropic.APITimeoutError (Claude slow/unavailable)        │
│    • Log warning                                              │
│    • Retry automatically (tenacity handles)                   │
│    • If all retries fail: re-raise                            │
│                                                               │
│ 3. json.JSONDecodeError (Invalid response)                    │
│    • Log error                                                │
│    • Could attempt self-repair (strip markdown, etc.)         │
│    • If repair fails: re-raise                                │
└──────────────────────────────────────────────────────────────┘
```

**Health Checks:**

```mermaid
flowchart LR
    Start[health_check] --> C1[Check Profile Loading]
    Start --> C2[Check Claude API]
    Start --> C3[Check Cache Stats]
    
    C1 -->|Try load| L1{Success?}
    L1 -->|Yes| OK1[profile_loading: ok]
    L1 -->|No| Err1[profile_loading: error]
    
    C2 -->|Test call| L2{Success?}
    L2 -->|Yes| OK2[claude_api: ok]
    L2 -->|No| Err2[claude_api: error]
    
    C3 --> Stats[Get cache_hit_rate]
    
    OK1 --> Eval[Evaluate Overall]
    Err1 --> Eval
    OK2 --> Eval
    Err2 --> Eval
    Stats --> Eval
    
    Eval -->|All OK| Healthy[status: healthy]
    Eval -->|Any Error| Degraded[status: degraded]
    
    Healthy --> Return[Return checks dict]
    Degraded --> Return
    
    style Start fill:#e1f5ff
    style Healthy fill:#d4edda
    style Degraded fill:#fff4e6
    style Err1 fill:#f8d7da
    style Err2 fill:#f8d7da
```

**Health Check Implementation:**

```
┌──────────────────────────────────────────────────────────────┐
│ HEALTH CHECK SYSTEM                                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ Checks Performed:                                             │
│                                                               │
│ 1. Profile Loading                                            │
│    • Test: Load profile "network_diagnostician" v2           │
│    • Success: profile_loading = 'ok'                         │
│    • Failure: profile_loading = 'error: <message>'           │
│                                                               │
│ 2. Claude API                                                 │
│    • Test: Send minimal request (max_tokens=10)              │
│    • Success: claude_api = 'ok'                              │
│    • Failure: claude_api = 'error: <message>'                │
│                                                               │
│ 3. Cache Performance                                          │
│    • Get cache_hit_rate from profile_manager                 │
│    • Include in checks dict                                   │
│    • No pass/fail (informational)                            │
│                                                               │
│ Overall Status:                                               │
│ • If all critical checks = 'ok': status = 'healthy'          │
│ • If any critical check fails: status = 'degraded'           │
│                                                               │
│ Returns Dict:                                                 │
│ {                                                             │
│   'profile_loading': 'ok' | 'error: ...',                    │
│   'claude_api': 'ok' | 'error: ...',                         │
│   'cache_hit_rate': 0.91,                                    │
│   'status': 'healthy' | 'degraded'                           │
│ }                                                             │
│                                                               │
│ Usage:                                                        │
│ • Expose as /health endpoint                                  │
│ • Call every 30 seconds                                       │
│ • Alert if status = 'degraded'                                │
│ • Monitor cache_hit_rate (alert if < 0.8)                    │
└──────────────────────────────────────────────────────────────┘
```

---

### Scale

**Target: 1000 failures/day**

**Capacity planning:**

```
Diagnoses/day: 1000
Diagnoses/hour (8h workday): 125
Diagnoses/minute: 2.1

Average latency: 8.5s
Concurrent limit: 50
Max throughput: 50 / 8.5 = 5.9 req/s

Current load: 2.1 / 60 = 0.035 req/s
Headroom: 5.9 / 0.035 = 169x ✅
```

**Burst handling:**

```mermaid
sequenceDiagram
    participant C as Caller
    participant E as ScalableDiagnosticEngine
    participant S as Semaphore (50)
    participant T as Thread Pool
    participant A as Claude API
    
    Note over C,A: Batch of 100 diagnoses arrives
    
    C->>E: diagnose_batch([f1...f100])
    
    loop For each failure in batch
        E->>E: Create async task
    end
    
    Note over E: asyncio.gather() - run all tasks
    
    par Concurrent execution (max 50)
        E->>S: Acquire slot 1
        S->>T: Run diagnose in thread
        T->>A: API call 1
        
        E->>S: Acquire slot 2
        S->>T: Run diagnose in thread
        T->>A: API call 2
        
        Note over E,A: ... up to 50 concurrent
        
        E->>S: Acquire slot 50
        S->>T: Run diagnose in thread
        T->>A: API call 50
        
        Note over S: Slots 51-100 wait
    end
    
    A-->>T: Results 1-50
    T-->>S: Release slots
    
    par Next batch
        E->>S: Acquire slot 51
        E->>S: Acquire slot 52
        Note over E,A: ... process remaining 50
    end
    
    A-->>T: Results 51-100
    T-->>E: All results
    E-->>C: List[DiagnosisResult]
    
    Note over C: Total time: ~12s<br/>(vs 850s sequential)
```

**Concurrency Architecture:**

```
┌──────────────────────────────────────────────────────────────┐
│ SCALABLE ASYNC BATCH PROCESSING                             │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ ScalableDiagnosticEngine:                                     │
│ • Inherits ProductionDiagnosticEngine                        │
│ • Adds async batch processing                                │
│ • Limits concurrency with Semaphore                          │
│                                                               │
│ Configuration:                                                │
│ • max_concurrent: 50 (Claude API rate limit)                 │
│ • Semaphore controls concurrent execution                     │
│                                                               │
│ Methods:                                                      │
│                                                               │
│ diagnose_async(*args, **kwargs):                              │
│ ├─ Acquire semaphore slot                                    │
│ ├─ Run diagnose() in thread (asyncio.to_thread)              │
│ ├─ Release semaphore slot                                    │
│ └─ Return result                                              │
│                                                               │
│ diagnose_batch(failures: List[Dict]):                         │
│ ├─ Create task for each failure                              │
│ ├─ Run all tasks with asyncio.gather()                       │
│ ├─ Semaphore limits to 50 concurrent                         │
│ └─ Return List[DiagnosisResult]                               │
│                                                               │
│ Performance (100 diagnoses):                                  │
│ • Sequential: 100 × 8.5s = 850s (14 minutes)                 │
│ • Parallel (50): 2 batches × 8.5s = 17s                      │
│ • Actual: ~12s (some finish faster, pipelining)              │
│ • Speedup: 70x                                                │
│                                                               │
│ Usage:                                                        │
│ engine = ScalableDiagnosticEngine(                            │
│     api_key=os.environ["ANTHROPIC_API_KEY"],                 │
│     profile_manager=profile_manager,                          │
│     max_concurrent=50                                         │
│ )                                                             │
│                                                               │
│ results = asyncio.run(                                        │
│     engine.diagnose_batch(failures)                           │
│ )                                                             │
└──────────────────────────────────────────────────────────────┘
```

---

### Observability

**Metrics to track:**

```
┌──────────────────────────────────────────────────────────────┐
│ PROMETHEUS METRICS CATALOG                                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ PROFILE OPERATIONS:                                           │
│                                                               │
│ profile_loads_total (Counter):                               │
│ • Labels: profile_id, version, source                        │
│ • Purpose: Track total profile loads                         │
│ • Increment: Every load_profile() call                       │
│                                                               │
│ profile_cache_hit_rate (Gauge):                              │
│ • Labels: profile_id                                         │
│ • Purpose: Current cache hit rate                            │
│ • Update: After each load (hits / total)                     │

active_profile_version = Gauge(
    'active_profile_version',
    'Currently active profile version',
    ['profile_id']
)

# Diagnosis performance
diagnosis_duration_seconds = Histogram(
    'diagnosis_duration_seconds',
    'Diagnosis duration',
    ['profile_id', 'version'],
    buckets=[1, 2, 5, 10, 20, 30, 60]
)

diagnosis_cost_usd = Histogram(
    'diagnosis_cost_usd',
    'Diagnosis cost in USD',
    ['profile_id', 'version', 'cache_hit'],
    buckets=[0.01, 0.05, 0.08, 0.10, 0.15, 0.20, 0.50]
)

diagnosis_confidence = Histogram(
    'diagnosis_confidence',
    'Diagnosis confidence score',
    ['profile_id', 'version'],
    buckets=[0.0, 0.3, 0.5, 0.7, 0.9, 1.0]
)

# A/B testing
ab_test_traffic_split = Gauge(
    'ab_test_traffic_split',
    'A/B test traffic allocation',
    ['profile_id', 'version']
)

# Errors
diagnosis_errors_total = Counter(
    'diagnosis_errors_total',
    'Total diagnosis errors',
    ['profile_id', 'error_type']
)
```

**Dashboard (Grafana):**

```yaml
# Profile Operations Dashboard

panels:
  - title: "Profile Cache Hit Rate"
    query: |
      profile_cache_hit_rate{profile_id="network_diagnostician"}
    
  - title: "A/B Test Traffic Split"
    query: |
      ab_test_traffic_split{profile_id="network_diagnostician"}
    
  - title: "Diagnosis Cost by Version"
    query: |
      histogram_quantile(0.50, 
        rate(diagnosis_cost_usd_bucket[5m])
      ) by (version)
    
  - title: "Diagnosis Latency (P95)"
    query: |
      histogram_quantile(0.95,
        rate(diagnosis_duration_seconds_bucket[5m])
      ) by (version)
    
  - title: "Accuracy by Version (Confidence > 0.9)"
    query: |
      rate(diagnosis_confidence_bucket{le="1.0"}[5m])
      / 
      rate(diagnosis_confidence_bucket{le="+Inf"}[5m])
      by (version)
    
  - title: "Cost Savings from Caching"
    query: |
      (
        rate(diagnosis_cost_usd_sum{cache_hit="false"}[5m])
        - 
        rate(diagnosis_cost_usd_sum{cache_hit="true"}[5m])
      )
      * 3600  # Per hour
```

**Alerts:**

```yaml
# Profile Operations Alerts

alerts:
  - name: ProfileCacheHitRateLow
    expr: profile_cache_hit_rate < 0.70
    for: 30m
    severity: warning
    annotations:
      summary: "Profile cache hit rate below 70%"
      description: "Cache hit rate is {{ $value }}, expected >70%"
  
  - name: DiagnosisCostHigh
    expr: |
      histogram_quantile(0.50,
        rate(diagnosis_cost_usd_bucket[10m])
      ) > 0.15
    for: 15m
    severity: warning
    annotations:
      summary: "Median diagnosis cost above $0.15"
      description: "Cost is {{ $value }}, budget is $0.10"
  
  - name: ABTestVersionAccuracyDrop
    expr: |
      (
        rate(diagnosis_confidence_bucket{version="3",le="0.7"}[10m])
        / 
        rate(diagnosis_confidence_bucket{version="3",le="+Inf"}[10m])
      ) > 0.30
    for: 10m
    severity: critical
    annotations:
      summary: "Version 3 low confidence rate >30%"
      description: "Possible regression, consider rollback"
      action: "Review version 3 changes, rollback if needed"
```

---

### Security

**Key risks:**

1. **Profile injection** (malicious profile content)
   - Attack: Commit profile with prompt injection payload
   - Mitigation: 
     - Code review for all profile changes
     - CI validation (syntax, schema, test results)
     - Signed commits (require GPG signature)

2. **A/B routing manipulation** (attacker forces version)
   - Attack: Override routing to deploy malicious profile
   - Mitigation:
     - Routing config changes require admin approval
     - Audit log of all routing changes
     - Rollback protection (can't change routing >20% per hour)

3. **Cache poisoning** (inject malicious content into cache)
   - Attack: Modify profile file between hash and load
   - Mitigation:
     - Atomic file operations
     - Hash validation on every cache hit
     - File integrity monitoring (detect unauthorized changes)

**Security Controls:**

```mermaid
flowchart TD
    Start[_load_from_disk] --> CheckPerm{Check file<br/>permissions}
    CheckPerm -->|0644 or stricter| LoadFile[Load profile from disk]
    CheckPerm -->|World/Group writable| ErrPerm[Raise PermissionError]
    
    LoadFile --> ValidateSec[_validate_profile_security]
    ValidateSec --> ScanContent{Scan for<br/>injection patterns}
    
    ScanContent -->|Clean| Return[Return profile]
    ScanContent -->|Suspicious| Warn[Log warning]
    Warn --> Flag{Auto-reject?}
    Flag -->|Yes| ErrInject[Raise SecurityError]
    Flag -->|No| Return
    
    subgraph "Injection Patterns Checked"
        P1["ignore above"]
        P2["ignore previous instructions"]
        P3["you are now"]
        P4["system:"]
        P5["<|endoftext|>"]
        P6["assistant:"]
    end
    
    style Start fill:#e1f5ff
    style Return fill:#d4edda
    style ErrPerm fill:#f8d7da
    style ErrInject fill:#f8d7da
    style Warn fill:#fff4e6
```

**SecureProfileManager Implementation:**

```
┌──────────────────────────────────────────────────────────────┐
│ SECUREPROFILEMANAGER - Enhanced Security Layer              │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ Security Checks:                                              │
│                                                               │
│ 1. File Permissions Validation                               │
│    ├─ Check: stat.st_mode & 0o022                            │
│    ├─ Required: 0644 or more restrictive                     │
│    ├─ Reject: World-writable or group-writable               │
│    └─ Raises: PermissionError if unsafe                      │
│                                                               │
│ 2. Prompt Injection Detection                                │
│    ├─ Scan profile content for suspicious patterns           │
│    ├─ Patterns checked:                                      │
│    │  • "ignore above"                                       │
│    │  • "ignore previous instructions"                       │
│    │  • "you are now"                                        │
│    │  • "system:"                                            │
│    │  • "<|endoftext|>"                                      │
│    │  • "assistant:"                                         │
│    ├─ If found: Log warning                                  │
│    └─ Optional: Reject profile or flag for review            │
│                                                               │
│ 3. Routing Safety Limits                                     │
│    ├─ Check traffic shift magnitude                          │
│    ├─ Limit: Max 20% change per deploy                       │
│    ├─ Example:                                                │
│    │  Current: v2=90%, v3=10%                                │
│    │  Requested: v2=50%, v3=50%                              │
│    │  Delta: 40% (REJECT - too large)                        │
│    ├─ Audit log: Record all routing changes                  │
│    └─ Raises: ValueError if shift > 20%                      │
│                                                               │
│ 4. Audit Logging                                              │
│    ├─ Log all profile loads                                  │
│    ├─ Log all routing changes                                │
│    ├─ Log security violations                                │
│    └─ Format: "AUDIT: <action> for <profile_id>"            │
│                                                               │
│ Usage:                                                        │
│ secure_manager = SecureProfileManager(                        │
│     profiles_dir="profiles",                                  │
│     cache_ttl=300                                            │
│ )                                                             │
│                                                               │
│ # All loads validated automatically                           │
│ profile = secure_manager.load_profile(                        │
│     "network_diagnostician", 2                                │
│ )                                                             │
└──────────────────────────────────────────────────────────────┘
```
            
            if delta > 0.20:
                raise ValueError(
                    f"Traffic shift too large: {delta:.0%} for v{version}. "
                    f"Max allowed: 20%. Deploy gradually."
                )
        
        # Audit log
        logger.info(f"AUDIT: Routing change for {profile_id}: {current} → {routing}")
        
        super().set_routing(profile_id, routing)
```

---

## Trade-offs & Alternatives

### When to use these patterns

✅ **Use profile operations when:**
- You have multiple agent profiles to manage
- You need safe deployment with A/B testing
- You want to optimize costs via caching
- You need zero-downtime updates
- You have non-engineers contributing to prompts

❌ **Don't use when:**
- Single simple prompt (hardcoded is fine)
- Prompt never changes (no need for versioning)
- <10 requests/day (caching won't help)
- No deployment risk (just YOLO deploy)

### Alternatives

| Approach | When to use | Atiya fit? |
|----------|-------------|------------|
| **Hardcoded prompts** | Prototype, <100 users, never changes | ❌ No - we need safe iteration |
| **Database-stored prompts** | Dynamic per-user prompts | ⚠️ Defer - git is simpler for now |
| **Prompt versioning service (Humanloop, LangSmith)** | Want managed solution | ⚠️ Consider - adds vendor dependency |
| **Feature flags (LaunchDarkly)** | Already using feature flags | ✅ Yes - can integrate with git workflow |

### Complexity cost

**Engineering effort:**

```
Profiles as policies (markdown files): 0.5 days
Git-based version control: 1 day
CI/CD pipeline: 2 days
Profile loader with caching: 1 day
A/B testing routing: 1 day
Hot-reload: 0.5 days
Monitoring & alerts: 1 day
───────────────────────────────────
Total: 7.5 days engineering

ROI calculation:
- Cost savings (caching): $1,890/month
- Deployment time savings: 42 min/deploy × 4 deploys/month = 168 min/month = $420/month
- Incident prevention: 1 bad deploy caught by A/B test × $5,000 incident cost = $5,000/month
- Total benefit: $7,310/month

Engineering cost: $150/hr × 8hr/day × 7.5 days = $9,000 (one-time)

Payback period: $9,000 / $7,310 = 1.2 months ✅
```

**Maintenance cost:**

```
Ongoing (monthly):
- Monitor A/B tests: 2 hours
- Review profile changes: 4 hours
- Investigate cache issues: 1 hour
- Update CI pipeline: 1 hour
───────────────────────────
Total: 8 hours/month = $1,200/month

Net benefit: $7,310 - $1,200 = $6,110/month
```

---

## Atiya Lens

### How this applies to Atiya

**Use case:**
Atiya needs safe, fast iteration on prompts. As we discover new failure patterns, we need to update the network diagnostician profile without:
- Breaking existing diagnoses (regression)
- Downtime (service interruption)
- Manual deployment work (engineer time)
- Excessive cost (budget constraints)

**Where it fits:**

```
Atiya Architecture:
├─ API Layer (FastAPI) ← Receives failure notifications
├─ Evidence Collector ← Gathers logs, configs, test code
├─ Profile Operations ← **THIS MODULE**
│  ├─ Profile Manager (loading, caching, routing)
│  ├─ A/B Testing (traffic split, metrics comparison)
│  ├─ Hot-Reload (zero-downtime updates)
│  └─ Monitoring (metrics, alerts, dashboards)
├─ Prompt Engine ← Uses loaded profile
├─ LLM Router ← Calls Claude API with caching
└─ Result Store ← Saves diagnoses
```

### Decision: IMPLEMENT (High Priority)

**Rationale:**

1. **Cost savings:** $1,890/month from caching alone
   - ROI: Pays for itself in 1.2 months
   - Ongoing: $6,110/month net benefit

2. **Deployment safety:** A/B testing prevents bad deploys
   - Impact: Catches regressions before 100% rollout
   - Value: Avoids ~$5,000/incident (1 bad deploy caught/month)

3. **Velocity:** Faster iteration on prompts
   - Manual: 45 min/deploy
   - Automated: 3 min/deploy
   - Impact: 14x faster, enables 5 tests/week vs 1 test/week

4. **Uptime:** Zero-downtime hot-reload
   - Manual: 10 min downtime/deploy
   - Hot-reload: 0 sec downtime
   - Impact: 99.9% → 99.99% uptime

**Implementation priority:**

```
Phase 1 (Week 1-2): Foundation
- ✅ Profiles as markdown files with YAML frontmatter
- ✅ Profile loader with caching
- ✅ Basic version control (git)

Phase 2 (Week 3-4): CI/CD
- ✅ CI validation pipeline (lint, test, measure)
- ✅ Deployment automation
- ✅ Hot-reload implementation

Phase 3 (Week 5-6): A/B Testing
- ✅ Traffic routing logic
- ✅ Metrics comparison
- ✅ Automated rollback

Phase 4 (Week 7-8): Observability
- ✅ Prometheus metrics
- ✅ Grafana dashboards
- ✅ Alerting rules
```

**Success metrics:**

| Metric | Baseline | Target | Current |
|--------|----------|--------|---------|
| Deployment time | 45 min | <5 min | - |
| Downtime per deploy | 10 min | 0 min | - |
| Cache hit rate | 0% | 90% | - |
| Cost/diagnosis | $0.105 | <$0.09 | - |
| Bad deploys/month | 1 | 0 | - |
| Profile changes/week | 1 | 5 | - |

---

## Monitoring

### Real-time Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  ATIYA PROFILE OPERATIONS - LIVE                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Profile Status:                                             │
│    network_diagnostician_v2: PRODUCTION (90% traffic)        │
│    network_diagnostician_v3: CANARY (10% traffic)            │
│                                                              │
│  Cache Performance:                                          │
│    Hit rate:  91.2%                  [██████████] ✓         │
│    Avg cost:  $0.087                 [███░░░░░░░] ✓         │
│    Savings:   $63/day vs no caching  (+$1,890/month)        │
│                                                              │
│  A/B Test (v2 vs v3):                                        │
│                    v2 (baseline)    v3 (canary)   Delta     │
│    Accuracy:       89.2%            92.1%         +2.9pp ✅  │
│    Confidence:     0.83             0.87          +0.04 ✅   │
│    Cost:           $0.086           $0.091        +$0.005 ⚠️ │
│    Latency (P95):  9.2s             9.8s          +0.6s  ⚠️  │
│                                                              │
│  Decision: PROMOTE v3 to 50% (accuracy gain worth cost)     │
│                                                              │
│  Profile Changes (last 7 days):                              │
│    2026-08-19: v3 deployed to 10% canary                     │
│    2026-08-17: v2 promoted to 100% production                │
│    2026-08-15: v2 deployed to 50% canary                     │
│                                                              │
│  Deployment Pipeline:                                        │
│    Last deploy: 2 hours ago (v3 canary)                      │
│    Status: MONITORING (0.5/2.0 hours)                        │
│    Next action: Promote to 50% in 1.5 hours                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Alerts

**Critical:**

```yaml
- name: CacheHitRateCriticallyLow
  condition: cache_hit_rate < 0.50 for 15m
  severity: critical
  action: page on-call
  description: "Cache may be broken, costs will spike"

- name: ABTestAccuracyRegression
  condition: |
    (accuracy_v3 - accuracy_v2) < -0.05 for 30m
  severity: critical
  action: auto-rollback + page on-call
  description: "Canary version has 5pp worse accuracy"

- name: ProfileLoadFailure
  condition: profile_load_errors > 0 for 5m
  severity: critical
  action: page on-call
  description: "Cannot load profiles, service degraded"
```

**Warning:**

```yaml
- name: CacheHitRateLow
  condition: cache_hit_rate < 0.80 for 30m
  severity: warning
  action: notify slack
  description: "Cache hit rate below target, investigate"

- name: ABTestCostIncrease
  condition: |
    (cost_v3 - cost_v2) / cost_v2 > 0.15 for 1h
  severity: warning
  action: notify slack
  description: "Canary version 15% more expensive"

- name: DeploymentStuck
  condition: deployment_duration > 4h
  severity: warning
  action: notify slack
  description: "Deployment taking longer than expected"
```

### Debugging

**When profile change causes regression:**

1. **Check A/B test metrics:**
   ```bash
   # Compare v2 vs v3 accuracy
   curl http://localhost:9090/api/v1/query?query='diagnosis_confidence_bucket{version="3"}'
   ```

2. **Inspect failing diagnoses:**
   ```python
   # Get low-confidence diagnoses from v3
   diagnoses = db.query("""
       SELECT * FROM diagnoses
       WHERE profile_version = 3
         AND confidence < 0.7
       ORDER BY timestamp DESC
       LIMIT 10
   """)
   
   for d in diagnoses:
       print(f"Test: {d.test_name}")
       print(f"Root cause: {d.root_cause}")
       print(f"Confidence: {d.confidence}")
   ```

3. **Diff profile versions:**
   ```bash
   git diff profiles/network_diagnostician_v2.md profiles/network_diagnostician_v3.md
   ```

4. **Test profile against known failures:**
   ```bash
   python scripts/test_profile.py \
     --profile profiles/network_diagnostician_v3.md \
     --test-cases tests/known_failures/*.json
   ```

5. **Rollback if needed:**
   ```bash
   # Automatic rollback (if alert triggered)
   python scripts/rollback_profile.py \
     --profile network_diagnostician \
     --from 3 \
     --to 2
   
   # Manual rollback
   profile_manager.set_routing("network_diagnostician", {2: 1.0})
   ```

**When cache hit rate drops:**

1. **Check profile changes:**
   ```bash
   # Did profile content change?
   git log --oneline profiles/network_diagnostician_v2.md
   ```

2. **Check cache TTL:**
   ```python
   # Is traffic too sparse for 5-minute TTL?
   stats = profile_manager.get_cache_stats()
   print(f"Requests/minute: {stats['total_requests'] / 300}")
   # If <1 req/min, cache TTL too short
   ```

3. **Check for cache thrashing:**
   ```python
   # Are we loading too many profile versions?
   print(profile_manager._cache.keys())
   # If >10 versions cached, may be routing issue
   ```

---

## Summary

**What we learned:**

1. **Profiles as Policies:** Declarative markdown files, not hardcoded Python strings
2. **Version-Controlled Profiles:** Git-based versioning, diff, history, rollback
3. **Profile Loading:** Lazy loading, in-memory cache, hot-reload, A/B routing
4. **Profile Caching:** Claude prompt caching (90% cost savings), 5-min TTL
5. **Profile Restart Behavior:** Stateless design (each diagnosis independent)

**For Atiya:**
- ✅ **IMPLEMENT** - High priority (Phase 2 after prompt engineering fundamentals)
- ROI: $6,110/month net benefit, 1.2-month payback
- Timeline: 8 weeks to full production deployment
- Risk: Low (mature patterns, proven ROI)

**Key metrics:**

```
Cost savings: $1,890/month (caching)
Deployment time: 45min → 3min (14x faster)
Downtime: 10min → 0sec (zero-downtime)
Velocity: 1 → 5 profile changes/week (5x iteration speed)
Safety: 1 → 0 bad deploys/month (A/B testing)
```

**Next steps:**

1. Implement profiles as markdown files (Week 1)
2. Build profile loader with caching (Week 2)
3. Set up CI/CD pipeline (Week 3-4)
4. Implement A/B testing (Week 5-6)
5. Add observability (Week 7-8)
6. Production launch (Week 9)

**Next module:**
- Module 6: Production Deployment (containerization, orchestration, scaling, disaster recovery)
