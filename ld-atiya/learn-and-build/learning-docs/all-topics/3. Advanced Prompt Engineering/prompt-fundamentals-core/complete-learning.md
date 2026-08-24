# Prompt Engineering Fundamentals (Core)

**Context:** Production AI agent development for test failure diagnosis (Atiya)  
**Scope:** System design, template patterns, production architecture  
**Outcome:** Reliable, cost-effective AI integration

---

## 1. Problem and Overview

### The Challenge

**Without structured prompt engineering:**
```
Developer Query: "Why did this test fail?"
LLM Response: [Hallucinated guess based on test name alone]
              [Ignores actual logs, topology, or error traces]
              [Different answer each retry]
              [Cost: $0.50/query, 90% false positives]
```

**With structured prompt engineering:**
```
System Template: [Define role, constraints, evidence policy]
User Evidence:   [Parsed logs, topology state, error traces in XML]
LLM Response:    [Structured JSON with root cause + confidence]
                 [Cached context reduces cost by 90%]
                 [Reproducible, auditable results]
```

### Business Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Cost per query | $0.50 | $0.05 | 10x reduction |
| False positive rate | 90% | 15% | 6x better |
| Response time | 45s | 8s | 5.6x faster |
| Cache hit rate | 0% | 85% | New capability |
| Reliability | 2/10 queries usable | 8.5/10 | 4.25x |

### Why It Matters

**Quality:** Structured prompts enforce evidence-based reasoning  
**Cost:** Prompt caching saves 90% on repeated context  
**Reliability:** Explicit output schemas enable validation  
**Observability:** Template versioning enables A/B testing  

---

## 2. Architecture

### System View

```
┌─────────────────────────────────────────────────────────────┐
│                    PROMPT ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────┐      ┌─────────────┐      ┌──────────────┐ │
│  │  Evidence  │──1──>│   Template  │──2──>│  LLM Client  │ │
│  │ Collector  │      │   Engine    │      │  (Anthropic) │ │
│  └────────────┘      └─────────────┘      └──────────────┘ │
│        │                    │                      │         │
│        │                    │                      │         │
│        v                    v                      v         │
│  ┌────────────┐      ┌─────────────┐      ┌──────────────┐ │
│  │  Raw Data  │      │  Messages   │      │  JSON Output │ │
│  │  - Logs    │      │  - System   │      │  - Validated │ │
│  │  - Topology│      │  - User     │      │  - Structured│ │
│  │  - Errors  │      │  - Cached   │      │  - Auditable │ │
│  └────────────┘      └─────────────┘      └──────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Flow:
1. Evidence Collector gathers context (logs, topology, errors)
2. Template Engine injects into system/user prompts
3. LLM Client sends request with caching headers
4. Validation layer checks output against schema
```

### Component Interactions

```
┌──────────────────────────────────────────────────────────────┐
│                   REQUEST LIFECYCLE                           │
└──────────────────────────────────────────────────────────────┘

Test Failure Event
        │
        v
┌───────────────────┐
│ Evidence Collector│ <── Reads: Logs, Topology YAML, Error Traces
└─────────┬─────────┘
          │
          v
┌───────────────────┐
│ Template Selector │ <── Chooses: diagnostic.yaml based on task
└─────────┬─────────┘
          │
          v
┌───────────────────┐
│  Message Builder  │ <── Constructs:
└─────────┬─────────┘      System: [Role + Constraints + Format]
          │                User:   [Evidence in XML tags]
          │
          v
┌───────────────────┐
│   LLM Client      │ <── Sends: POST to Anthropic API
└─────────┬─────────┘      Headers: cache-control, anthropic-beta
          │
          │ (8 second latency, cache hit)
          v
┌───────────────────┐
│  JSON Validator   │ <── Checks: Schema compliance, required fields
└─────────┬─────────┘
          │
          v
┌───────────────────┐
│  Output Handler   │ <── Returns: Structured diagnosis to caller
└───────────────────┘
```

### Data Flow Pattern

```
Evidence (Raw) ────> Template (Structured) ────> LLM (Reasoning) ────> Output (Validated)

Example:
  "Test failed      "You are a test        "Analyze this        {"root_cause":
   at line 42"       diagnostician.         failure evidence:    "timeout",
   [5MB log]         Output JSON.           <logs>...</logs>     "confidence": 0.9,
   [Topology]        Use evidence."         <topology>..."       "reasoning": "..."}
```

---

## 3. Core Mechanics

### 3.1 LLM API Integration

**Connection Pattern:**
```
┌──────────────────────────────────────────────────────┐
│           LLM CLIENT ARCHITECTURE                     │
├──────────────────────────────────────────────────────┤
│                                                        │
│  Application Code                                     │
│         │                                             │
│         v                                             │
│  ┌──────────────────┐                                │
│  │  LLMClient       │                                │
│  │  - __init__()    │ <── API key from env/keychain  │
│  │  - send()        │                                │
│  │  - _retry()      │                                │
│  └────────┬─────────┘                                │
│           │                                           │
│           v                                           │
│  ┌──────────────────┐                                │
│  │ anthropic.Client │ <── Official SDK                │
│  └────────┬─────────┘                                │
│           │                                           │
│           v                                           │
│  ┌──────────────────┐                                │
│  │  HTTP Transport  │                                │
│  │  - TLS 1.3       │                                │
│  │  - Retry logic   │                                │
│  │  - Timeout: 120s │                                │
│  └────────┬─────────┘                                │
│           │                                           │
│           v                                           │
│     api.anthropic.com                                │
│                                                        │
└──────────────────────────────────────────────────────┘
```

**Retry Strategy:**
```
Attempt 1 ──> [Network Error] ──> Wait 1s
Attempt 2 ──> [429 Rate Limit] ──> Wait 2s (exponential backoff)
Attempt 3 ──> [200 OK] ──> Success

Max retries: 3
Backoff: exponential (1s, 2s, 4s)
Timeout per attempt: 120s
Fatal errors (no retry): 400 Bad Request, 401 Unauthorized
```

**Request Structure:**
```
POST https://api.anthropic.com/v1/messages
Headers:
  x-api-key: sk-ant-...
  anthropic-version: 2023-06-01
  anthropic-beta: prompt-caching-2024-07-31
  content-type: application/json

Body:
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 4096,
  "temperature": 0.0,
  "system": [
    {
      "type": "text",
      "text": "You are a test diagnostician...",
      "cache_control": {"type": "ephemeral"}
    }
  ],
  "messages": [
    {
      "role": "user",
      "content": "<evidence>...</evidence>"
    }
  ]
}
```

---

### 3.2 System Prompt Design (7 Components)

**Component Architecture:**
```
┌────────────────────────────────────────────────────────────┐
│              SYSTEM PROMPT STRUCTURE                        │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  1. IDENTITY/ROLE                                           │
│     "You are a test diagnostician for PARTS framework..."  │
│     └─> Sets: Expertise domain, perspective                │
│                                                              │
│  2. OBJECTIVE                                               │
│     "Your goal: identify root cause of test failures..."   │
│     └─> Defines: Success criteria, primary task            │
│                                                              │
│  3. CONSTRAINTS                                             │
│     "- Only use provided evidence                          │
│      - No speculation beyond logs                          │
│      - Flag insufficient data as 'unknown'"                │
│     └─> Guards: Hallucination, overconfidence              │
│                                                              │
│  4. OUTPUT FORMAT                                           │
│     "Return JSON: {root_cause, confidence, reasoning}"     │
│     └─> Enforces: Structured, parseable output             │
│                                                              │
│  5. EXAMPLES                                                │
│     "Example failure: <logs>timeout</logs>                 │
│      Analysis: {root_cause: 'network_timeout', ...}"       │
│     └─> Demonstrates: Expected reasoning pattern           │
│                                                              │
│  6. EVIDENCE POLICY                                         │
│     "Evidence format: <logs>...</logs> <topology>...</>"   │
│     └─> Specifies: Input structure, what to expect         │
│                                                              │
│  7. BEHAVIORAL INSTRUCTIONS                                 │
│     "- Prefer infrastructure causes over code bugs         │
│      - Weight recent errors higher than warnings           │
│      - Cite line numbers from logs in reasoning"           │
│     └─> Guides: Prioritization, detail level               │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

**Component 1: Identity/Role**
```
WEAK:   "You are a helpful assistant."
STRONG: "You are an expert PARTS test diagnostician with 10 years
         experience debugging network automation failures in Palo Alto
         Networks products. You specialize in topology configuration
         errors, device state mismatches, and timing-related flakes."

Why stronger: Primes LLM with domain context, sets expertise boundary
```

**Component 2: Objective**
```
WEAK:   "Help debug the test."
STRONG: "Your objective: identify the single most likely root cause of
         test failure from provided evidence. Success = actionable fix
         for test developer (e.g., 'increase timeout', 'fix BGP config')."

Why stronger: Clear success criteria, output constraints
```

**Component 3: Constraints**
```
CRITICAL CONSTRAINTS:

1. Evidence-Only Policy:
   "Base analysis ONLY on provided <logs>, <topology>, <error_trace>.
    Do NOT infer details about code, network state, or device config
    beyond what is explicitly shown."

2. Confidence Threshold:
   "If evidence is insufficient for 0.7+ confidence, return:
    {root_cause: 'insufficient_evidence', confidence: 0.0,
     reasoning: 'Missing: [list required data]'}"

3. No External Knowledge:
   "Do NOT reference general PAN-OS bugs, known issues, or external
    documentation unless they appear in the provided evidence."

Why critical: Prevents hallucination, forces grounded reasoning
```

**Component 4: Output Format**
```
SCHEMA ENFORCEMENT:

"Return ONLY valid JSON matching this schema:
{
  "root_cause": string,        // One of: config_error, timeout,
                                //         auth_failure, race_condition,
                                //         insufficient_evidence
  "confidence": float,          // 0.0 to 1.0
  "reasoning": string,          // 2-3 sentences citing evidence
  "suggested_fix": string,      // Actionable next step
  "evidence_citations": [       // Line numbers or XML tags referenced
    "logs:line_142",
    "topology:service_connection_config"
  ]
}

Do NOT include markdown, explanations, or preamble. Output must parse
as JSON."

Why critical: Enables validation, downstream processing, A/B testing
```

**Component 5: Examples (Few-Shot Learning)**
```
EXAMPLE 1: Timeout Failure

Input:
<logs>
[2026-08-20 14:32:15] INFO: Starting BGP peer verification
[2026-08-20 14:32:45] ERROR: Verification timeout after 30s
[2026-08-20 14:32:45] ERROR: Expected state: Established, Got: Idle
</logs>

<topology>
bgp_peer_timeout: 30
expected_convergence_time: 45
</topology>

Output:
{
  "root_cause": "timeout",
  "confidence": 0.95,
  "reasoning": "Verification timeout (30s) is shorter than expected BGP
                convergence time (45s). Line 2 shows timeout triggered
                before convergence could complete.",
  "suggested_fix": "Increase bgp_peer_timeout to 60s in topology YAML",
  "evidence_citations": ["logs:line_2", "topology:bgp_peer_timeout"]
}

---

EXAMPLE 2: Configuration Error

Input:
<logs>
[2026-08-20 15:10:22] ERROR: API call failed: 400 Bad Request
[2026-08-20 15:10:22] ERROR: Response: {"error": "Invalid VLAN ID: 5000"}
</logs>

<topology>
service_connection:
  vlan_id: 5000  # Valid range: 1-4094
</topology>

Output:
{
  "root_cause": "config_error",
  "confidence": 0.98,
  "reasoning": "API explicitly rejected VLAN ID 5000 as invalid (line 2).
                Topology specifies 5000, which exceeds valid range 1-4094.",
  "suggested_fix": "Change vlan_id to value between 1-4094 in topology",
  "evidence_citations": ["logs:line_2", "topology:vlan_id"]
}

Why include examples: Shows expected reasoning depth, citation style
```

**Component 6: Evidence Policy**
```
EVIDENCE STRUCTURE:

"User input will contain evidence in XML tags:

<logs>
  Raw test execution logs, timestamp-prefixed lines
</logs>

<topology>
  YAML topology configuration for the test
</topology>

<error_trace>
  Python exception traceback if test crashed
</error_trace>

<device_state>
  Output from device show commands at failure time
</device_state>

Prioritize <error_trace> and <logs> ERROR lines over INFO/DEBUG.
Correlate <topology> settings with observed behavior in <logs>."

Why specify: LLM knows what to expect, how to weight sources
```

**Component 7: Behavioral Instructions**
```
REASONING HEURISTICS:

1. Prioritization:
   "Weight failures in this order:
    1. Explicit errors (ERROR, CRITICAL, Exception)
    2. Timeouts and hung operations
    3. Unexpected state transitions
    4. Warnings or INFO messages"

2. Root Cause Depth:
   "Prefer immediate cause over downstream effects.
    Example: 'auth_failure caused connection_timeout'
    → root_cause = 'auth_failure', not 'connection_timeout'"

3. Citation Requirements:
   "Every claim in reasoning MUST reference:
    - Log line number, OR
    - Topology key path, OR
    - Error message substring
    Avoid generic statements like 'the logs show issues'."

4. Ambiguity Handling:
   "If multiple causes are plausible with similar confidence:
    - List top 2 in reasoning
    - Return highest confidence as root_cause
    - Note 'also possible: X' in reasoning"

Why specify: Guides LLM toward consistent, useful output
```

---

### 3.3 User Prompt Design

**Evidence Structure Pattern:**
```
┌─────────────────────────────────────────────────────┐
│          USER PROMPT ANATOMY                         │
├─────────────────────────────────────────────────────┤
│                                                       │
│  <test_context>                                      │
│    test_id: test_bgp_convergence_basic               │
│    suite: gpcs-tests/bgp                             │
│    timestamp: 2026-08-20T14:32:00Z                   │
│  </test_context>                                     │
│                                                       │
│  <logs>                                              │
│    [2026-08-20 14:32:15] INFO: Test started          │
│    [2026-08-20 14:32:45] ERROR: Timeout after 30s    │
│    [14,523 more lines...]                            │
│  </logs>                                             │
│                                                       │
│  <topology>                                          │
│    bgp_peers:                                        │
│      - peer_ip: 10.0.0.1                             │
│        timeout: 30                                   │
│    [2,340 more lines...]                             │
│  </topology>                                         │
│                                                       │
│  <error_trace>                                       │
│    Traceback (most recent call last):                │
│      File "test_bgp.py", line 142                    │
│        assert state == "Established"                 │
│    AssertionError: Idle != Established               │
│  </error_trace>                                      │
│                                                       │
└─────────────────────────────────────────────────────┘

Size: ~50KB per test failure
Cache: <logs> and <topology> marked for prompt caching
Reuse: 85% cache hit rate across test suite
```

**XML Tag Strategy:**
```
WHY XML TAGS?

1. Unambiguous Boundaries:
   LLM can reliably extract <logs> section even if content contains
   nested JSON, YAML, or prose that might confuse delimiter parsing.

2. Hierarchical Structure:
   <device_state>
     <device id="firewall-1">
       <interface name="eth1">
         ...
       </interface>
     </device>
   </device_state>

3. Selective Attention:
   "Focus on <error_trace> and <logs> ERROR lines first, then
    correlate with <topology> settings."

4. Caching Alignment:
   Anthropic's prompt caching operates on text blocks. Wrapping large
   evidence in consistent tags creates stable cache keys.

ALTERNATIVES (and why XML is better):

- JSON: Requires escaping quotes, backslashes in raw logs
- YAML: Indentation-sensitive, fragile with multi-line strings
- Markdown: No clear section boundaries, harder to parse
- Plain text: No structure, relies on natural language headers
```

**Evidence Prioritization:**
```
ORDERING STRATEGY (most important first):

1. <test_context>      # Small, rarely changes, sets stage
2. <error_trace>       # Most diagnostic signal if present
3. <logs> (last 500)   # Recent errors trump early warnings
4. <topology>          # Large, stable → cache candidate
5. <device_state>      # Large, stable → cache candidate
6. <logs> (full)       # Huge, stable → prime cache candidate

CACHING MARKERS:

{
  "type": "text",
  "text": "<logs>[Full 50KB log dump]</logs>",
  "cache_control": {"type": "ephemeral"}  # <── Cache this block
}

Result: First request = 50KB upload, subsequent requests = 0.1KB upload
Cost: 90% reduction on cache hits
```

---

### 3.4 System/User Separation

**Correct Pattern:**
```
┌──────────────────────────────────────────────────────┐
│            SYSTEM vs USER MESSAGE ROLES               │
├──────────────────────────────────────────────────────┤
│                                                        │
│  SYSTEM MESSAGE (Instructions):                      │
│    "You are a test diagnostician.                    │
│     Output JSON schema: {...}                        │
│     Use evidence from user message."                 │
│                                                        │
│  ✓ Sets role, constraints, format                    │
│  ✓ Cacheable across all test failures                │
│  ✓ Versioned independently                           │
│                                                        │
├──────────────────────────────────────────────────────┤
│                                                        │
│  USER MESSAGE (Evidence):                            │
│    "<logs>...</logs>                                 │
│     <topology>...</topology>"                        │
│                                                        │
│  ✓ Contains task-specific data                       │
│  ✓ Large, stable sections cache well                 │
│  ✓ Changes per test, but structure is consistent     │
│                                                        │
└──────────────────────────────────────────────────────┘

ANTI-PATTERN (all in user message):

"You are a test diagnostician. Output JSON: {...}
 Here are the logs: [50KB dump]"

Why wrong:
- Mixes instructions with evidence
- Instructions not cached separately
- Template changes invalidate evidence cache
```

**Caching Benefits:**
```
CACHE HIT ANALYSIS:

Request 1 (test_bgp_001 failure):
  System:  [2KB instructions] ──> Upload, cache for 5 min
  User:    [50KB logs + topology] ──> Upload, cache for 5 min
  Cost:    52KB upload = $0.05

Request 2 (test_bgp_002 failure, same topology):
  System:  [CACHE HIT] ──> $0.00
  User:    [500 byte new logs] + [49.5KB cached topology] ──> $0.005
  Cost:    0.5KB upload = $0.005

Request 3 (test_bgp_003, new logs, same topology):
  System:  [CACHE HIT] ──> $0.00
  User:    [1KB new logs] + [49KB cached topology] ──> $0.01
  Cost:    1KB upload = $0.01

Total for 3 failures: $0.065 vs $0.15 without caching (57% savings)

Over 1000 test failures/day: $21.67 vs $50.00 (56% cost reduction)
```

**Template Versioning:**
```
INDEPENDENT EVOLUTION:

system_prompt_v3.yaml:
  - Change: Added "cite line numbers" to behavioral instructions
  - Impact: All future requests use v3
  - Cache: System prompt cache invalidated, rebuilds
  - Evidence: User evidence cache UNAFFECTED (still valid)

This separation enables A/B testing:
  - 50% of requests use system_v3
  - 50% of requests use system_v4
  - Same evidence, different reasoning instructions
  - Measure: Which version has higher accuracy?
```

---

### 3.5 Explicit Output Format

**JSON Schema Enforcement:**
```
OUTPUT SCHEMA (embedded in system prompt):

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["root_cause", "confidence", "reasoning"],
  "properties": {
    "root_cause": {
      "type": "string",
      "enum": [
        "config_error",
        "timeout",
        "auth_failure",
        "race_condition",
        "api_error",
        "device_unreachable",
        "insufficient_evidence"
      ]
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "reasoning": {
      "type": "string",
      "minLength": 50,
      "maxLength": 500
    },
    "suggested_fix": {
      "type": "string"
    },
    "evidence_citations": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}

VALIDATION FLOW:

LLM Output ──> JSON Parser ──> Schema Validator ──> Application
                  │                   │
                  v (fail)            v (fail)
              Retry with         Retry with
              "Invalid JSON"     "Missing required field: X"
```

**Validation Layers:**
```
LAYER 1: JSON Syntax
  Input:  '{"root_cause": "timeout", "confidence": 0.9'  # Missing }
  Error:  JSONDecodeError: Unterminated object
  Action: Retry with hint: "Output was not valid JSON. Ensure balanced braces."

LAYER 2: Schema Compliance
  Input:  {"root_cause": "network_issue", "confidence": 0.9}
  Error:  'network_issue' not in enum [config_error, timeout, ...]
  Action: Retry with hint: "root_cause must be one of: [list]"

LAYER 3: Business Logic
  Input:  {"root_cause": "timeout", "confidence": 0.9, "reasoning": "Bug"}
  Error:  reasoning too short (< 50 chars)
  Action: Retry with hint: "reasoning must be 50-500 chars with evidence"

LAYER 4: Semantic Check
  Input:  {"root_cause": "timeout", "confidence": 0.9,
           "reasoning": "The test failed due to timeout",
           "evidence_citations": []}
  Error:  No citations provided
  Action: Retry with hint: "Include evidence_citations from logs/topology"
```

**Retry Strategy:**
```
RETRY WITH FEEDBACK:

Attempt 1:
  Request:  [System prompt] + [Evidence]
  Response: {"root_cause": "unknown_error", "confidence": 0.5}
  Validation: FAIL - "unknown_error" not in enum

Attempt 2:
  Request:  [System prompt] + [Evidence] + [Assistant: {previous output}]
           + [User: "Error: root_cause must be one of: config_error, timeout,
                    auth_failure, race_condition, api_error,
                    device_unreachable, insufficient_evidence"]
  Response: {"root_cause": "timeout", "confidence": 0.9, "reasoning": "..."}
  Validation: PASS

Max retries: 2
Fallback: If still invalid after 2 retries, return:
  {"root_cause": "insufficient_evidence", "confidence": 0.0,
   "reasoning": "LLM failed to produce valid output", "error": true}
```

---

### 3.6 Per-Step Templates (Multi-Agent Pattern)

**Multi-Step Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│        TEST FAILURE DIAGNOSIS WORKFLOW                       │
└─────────────────────────────────────────────────────────────┘

Step 1: TRIAGE
  Template: triage.yaml
  Input:    Test name, first 100 log lines, error trace
  Output:   {category: "network" | "config" | "timing" | "unknown",
             severity: "critical" | "medium" | "low"}
  
  │
  v

Step 2: DETAILED ANALYSIS (conditional on category)
  
  IF category == "config":
    Template: config_analysis.yaml
    Input:    Full logs, topology YAML, device state
    Output:   {root_cause: "config_error", field: "vlan_id", ...}
  
  ELSE IF category == "timing":
    Template: timing_analysis.yaml
    Input:    Logs (filtered for timestamps), topology timeouts
    Output:   {root_cause: "timeout", operation: "BGP convergence", ...}
  
  ELSE:
    Template: general_diagnostic.yaml
    Input:    All available evidence
    Output:   {root_cause: ..., confidence: ...}
  
  │
  v

Step 3: SOLUTION GENERATION
  Template: solution_generator.yaml
  Input:    Diagnosis from step 2, topology context
  Output:   {suggested_fix: "...", pr_description: "...",
             test_changes_needed: true/false}

BENEFITS:

1. Specialization:
   Each template optimized for its step (triage is fast/cheap,
   detailed analysis is thorough/expensive)

2. Cost Control:
   Only run expensive step 2 if triage indicates high-value signal
   (skip analysis for "test_name_typo" category)

3. Composability:
   Mix and match: triage_v2 + config_analysis_v1 + solution_v3

4. Observability:
   Log which template/version was used at each step for debugging
```

**Template Specialization Example:**
```
TRIAGE TEMPLATE (fast, cheap):

System Prompt:
  "You are a test triage specialist. Quickly categorize failures.
   Output: {category: string, severity: string}
   Do NOT perform detailed analysis - that's step 2."

Evidence (minimal):
  <test_name>test_bgp_convergence_basic</test_name>
  <error_trace>[Last exception only]</error_trace>
  <logs>[First 100 lines + last 50 lines]</logs>

Model: claude-haiku-4-5  (fast, cheap)
Max tokens: 256
Temperature: 0.0
Cost: $0.001 per request

---

CONFIG ANALYSIS TEMPLATE (detailed, expensive):

System Prompt:
  "You are a topology config expert. Analyze YAML structure and
   correlate with device errors. Output: {root_cause, config_path,
   expected_value, actual_value, suggested_fix}"

Evidence (complete):
  <logs>[Full 50KB log dump]</logs>
  <topology>[Full 100KB topology YAML]</topology>
  <device_state>[Device show command output]</device_state>

Model: claude-sonnet-4-5  (thorough, expensive)
Max tokens: 4096
Temperature: 0.0
Cost: $0.05 per request (with caching: $0.005)

ONLY CALLED IF: triage category == "config" AND severity == "critical"
```

---

### 3.7 Atiya Production Architecture

**System Diagram:**
```
┌──────────────────────────────────────────────────────────────┐
│                   ATIYA ARCHITECTURE                          │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐                                            │
│  │ ReportPortal │ <── Test results + logs                    │
│  │   Webhook    │                                            │
│  └──────┬───────┘                                            │
│         │                                                     │
│         v                                                     │
│  ┌──────────────┐                                            │
│  │   Atiya API  │                                            │
│  │  (FastAPI)   │                                            │
│  └──────┬───────┘                                            │
│         │                                                     │
│         v                                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Evidence Collector                          │    │
│  │  - Fetch full logs from ReportPortal                │    │
│  │  - Load topology YAML from git                      │    │
│  │  - Extract error traces from test output            │    │
│  │  - Query device state (if accessible)               │    │
│  └───────────────┬─────────────────────────────────────┘    │
│                  │                                           │
│                  v                                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Template Engine                             │    │
│  │  - Select: diagnostic_v3.yaml                       │    │
│  │  - Inject: Evidence into system/user prompts        │    │
│  │  - Add: Cache control headers                       │    │
│  └───────────────┬─────────────────────────────────────┘    │
│                  │                                           │
│                  v                                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         LLM Client (Anthropic SDK)                  │    │
│  │  - Model: claude-sonnet-4-5-20250929               │    │
│  │  - Temperature: 0.0                                 │    │
│  │  - Max tokens: 4096                                 │    │
│  │  - Retry: 3 attempts, exponential backoff           │    │
│  └───────────────┬─────────────────────────────────────┘    │
│                  │                                           │
│                  v                                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Response Validator                          │    │
│  │  - Parse JSON                                       │    │
│  │  - Validate schema                                  │    │
│  │  - Check confidence threshold (> 0.7)               │    │
│  └───────────────┬─────────────────────────────────────┘    │
│                  │                                           │
│                  v                                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Output Handler                              │    │
│  │  - Post diagnosis to ReportPortal as comment        │    │
│  │  - Log to observability (DataDog/Prometheus)        │    │
│  │  - Store in SQLite for audit trail                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                                │
└──────────────────────────────────────────────────────────────┘

DATA FLOW TIMING:
1. Test failure event ──> Atiya webhook: 0.1s
2. Evidence collection: 2s (parallel fetches)
3. Template injection: 0.05s
4. LLM request (cache hit): 8s
5. Validation + posting: 0.5s
Total: ~11s from failure to diagnosis posted
```

**Prompt Template Storage:**
```
templates/
├── diagnostic_v3.yaml          # Current production
├── diagnostic_v4_beta.yaml     # A/B test candidate
├── triage_v1.yaml              # Multi-step: step 1
├── config_analysis_v2.yaml     # Multi-step: step 2a
└── timing_analysis_v1.yaml     # Multi-step: step 2b

YAML Structure (diagnostic_v3.yaml):

metadata:
  version: "3.0"
  created: "2026-07-15"
  author: "atiya-team"
  description: "Main diagnostic template with enhanced citation requirements"

system_prompt: |
  You are an expert PARTS test diagnostician...
  [7-component structure as defined in section 3.2]

output_schema:
  type: object
  required: [root_cause, confidence, reasoning]
  properties:
    root_cause:
      type: string
      enum: [config_error, timeout, ...]
    ...

model_config:
  model: claude-sonnet-4-5-20250929
  temperature: 0.0
  max_tokens: 4096

cache_strategy:
  system_prompt: true      # Cache system prompt
  topology: true           # Cache topology blocks
  logs: true               # Cache full log dumps
  device_state: true

Why YAML: Version control, diff-friendly, non-technical team can edit
```

**Environment Configuration:**
```
PRODUCTION ENV VARS:

ANTHROPIC_API_KEY=sk-ant-api03-...           # From secret manager
ATIYA_TEMPLATE_DIR=/opt/atiya/templates
ATIYA_TEMPLATE_VERSION=diagnostic_v3.yaml
ATIYA_MODEL=claude-sonnet-4-5-20250929
ATIYA_MAX_TOKENS=4096
ATIYA_TEMPERATURE=0.0
ATIYA_CACHE_ENABLED=true
ATIYA_RETRY_MAX=3
ATIYA_TIMEOUT_SEC=120
REPORTPORTAL_API_KEY=...
REPORTPORTAL_ENDPOINT=https://rp.internal/api/v1
LOG_LEVEL=INFO
OBSERVABILITY_BACKEND=datadog
```

---

## 4. Use Cases

### Atiya: Test Failure Diagnosis

**Problem Statement:**
- PARTS test suite: 10,000+ tests, 200-500 failures/day
- Manual triage: 10-15 min/failure = 50-125 hours/day
- Developer productivity lost to false positives, flaky tests
- No systematic root cause categorization

**Atiya Solution:**
```
INPUT:
  Test: test_bgp_peer_convergence_multi_tenant
  Status: FAILED
  Duration: 47s
  Error: AssertionError: Expected 'Established', got 'Idle'
  Logs: [52KB]
  Topology: [topology_colo_100g.yaml, 128KB]

PROCESSING:
  1. Evidence collection: 2.1s
  2. Template selection: diagnostic_v3.yaml
  3. LLM analysis (cache hit): 7.8s
  4. Validation: 0.2s
  5. Post to ReportPortal: 0.5s

OUTPUT:
{
  "root_cause": "timeout",
  "confidence": 0.92,
  "reasoning": "BGP convergence timeout (30s) is insufficient for
                multi-tenant topology with 8 peers. Logs line 1847 shows
                last peer still in 'OpenSent' state at timeout. Topology
                specifies bgp_peer_timeout: 30, but expected_convergence
                documented as 45s for 8-peer scenario.",
  "suggested_fix": "Increase bgp_peer_timeout to 60s in
                    topology_colo_100g.yaml, section bgp_config",
  "evidence_citations": [
    "logs:line_1847:last_peer_state=OpenSent",
    "topology:bgp_config:bgp_peer_timeout",
    "topology:docs:expected_convergence_time_8_peers"
  ]
}

DEVELOPER EXPERIENCE:
  - Notification in ReportPortal: +11s after failure
  - Diagnosis accuracy: 92% confidence
  - Actionable fix: Direct file + line to edit
  - Time saved: 10 min manual debugging → 11s automated
```

**Impact Metrics:**
```
BEFORE ATIYA:
  - 200 failures/day × 10 min triage = 2000 min/day (33 hours)
  - False positive rate: 40% (80 failures were flakes/infra)
  - Root cause categorization: Manual, inconsistent
  - Mean time to fix: 2-3 days (lost in backlog)

AFTER ATIYA:
  - 200 failures/day × 11s diagnosis = 37 min/day (automated)
  - False positive filtering: 85% flakes auto-labeled
  - Root cause categories: Standardized (7 types)
  - Mean time to fix: 4-6 hours (prioritized by confidence)

ROI:
  - Developer time saved: 32 hours/day = $12,800/day (@ $400/hr)
  - LLM cost: 200 × $0.05/diagnosis = $10/day
  - Net savings: $12,790/day = $3.8M/year
```

---

## 5. Design Methodologies

### Template Design Workflow

**Iterative Refinement Process:**
```
┌────────────────────────────────────────────────────────────┐
│          TEMPLATE DEVELOPMENT LIFECYCLE                     │
└────────────────────────────────────────────────────────────┘

Step 1: DEFINE OBJECTIVE
  ├─ What decision does the LLM need to make?
  ├─ What inputs are available?
  ├─ What output format is needed?
  └─ Example: "Categorize test failure root cause from logs"

Step 2: DRAFT INITIAL TEMPLATE
  ├─ Identity: "You are a test diagnostician"
  ├─ Objective: "Identify root cause from evidence"
  ├─ Constraints: "Only use provided logs, no speculation"
  ├─ Format: JSON schema with required fields
  └─ Examples: 2-3 representative failures

Step 3: TEST WITH REAL DATA
  ├─ Collect: 20 historical test failures with known root causes
  ├─ Run: Template against each failure
  ├─ Measure: Accuracy (correct root cause %)
  └─ Baseline: v1 achieves 65% accuracy

Step 4: IDENTIFY FAILURE MODES
  ├─ Review: 7 incorrect diagnoses (35% error rate)
  ├─ Pattern 1: Confusing timeouts with config errors (3 cases)
  ├─ Pattern 2: Hallucinating device state not in logs (2 cases)
  ├─ Pattern 3: Insufficient evidence flagged incorrectly (2 cases)
  └─ Root cause: Template lacks timeout-specific guidance

Step 5: REFINE TEMPLATE
  ├─ Add: Behavioral instruction "Weight timeout errors separately"
  ├─ Add: Example of timeout vs config error distinction
  ├─ Strengthen: Evidence-only constraint with explicit warning
  ├─ Add: Confidence threshold guidance (< 0.7 → insufficient)
  └─ Version: v2

Step 6: RETEST
  ├─ Run: v2 against same 20 failures
  ├─ Measure: 85% accuracy (17/20 correct)
  ├─ Improvement: +20 percentage points
  └─ Failure modes: 2 ambiguous cases, 1 missing evidence

Step 7: A/B TEST IN PRODUCTION
  ├─ Deploy: 50% traffic to v1, 50% to v2
  ├─ Measure: Developer feedback, confidence scores
  ├─ Duration: 1 week (500 failures)
  ├─ Result: v2 → 82% accuracy, v1 → 63%
  └─ Decision: Promote v2 to 100% traffic

Step 8: CONTINUOUS MONITORING
  ├─ Track: Confidence distribution, error rates
  ├─ Alert: If accuracy drops below 75%
  ├─ Review: Monthly, incorporate new failure patterns
  └─ Iterate: v3 development starts for edge cases
```

**Visual: Template Evolution**
```
VERSION HISTORY:

v1 (baseline):
  ┌──────────────────────────────────────┐
  │ System Prompt: 800 words            │
  │ Examples: 2                          │
  │ Constraints: Generic                 │
  │ Accuracy: 65%                        │
  │ Avg confidence: 0.72                 │
  └──────────────────────────────────────┘
        │
        v (refinement)
v2 (timeout focus):
  ┌──────────────────────────────────────┐
  │ System Prompt: 1200 words (+400)    │
  │ Examples: 4 (+2 timeout cases)       │
  │ Constraints: Evidence-only emphasis  │
  │ Behavioral: Timeout prioritization   │
  │ Accuracy: 85% (+20pp)                │
  │ Avg confidence: 0.81 (+0.09)         │
  └──────────────────────────────────────┘
        │
        v (config detail)
v3 (current production):
  ┌──────────────────────────────────────┐
  │ System Prompt: 1400 words (+200)    │
  │ Examples: 5 (+1 config error)        │
  │ Constraints: Citation requirements   │
  │ Behavioral: Root cause depth guide   │
  │ Accuracy: 89% (+4pp)                 │
  │ Avg confidence: 0.84 (+0.03)         │
  │ Cost: -12% (better caching)          │
  └──────────────────────────────────────┘
```

---

### Testing Methodology

**Evaluation Framework:**
```
TEST DATASET STRUCTURE:

ground_truth_failures.jsonl (100 labeled examples):

{"test_id": "test_001", "root_cause": "timeout", "logs": "...",
 "topology": "...", "verified_by": "dev_alice", "date": "2026-07-01"}
{"test_id": "test_002", "root_cause": "config_error", ...}
...

METRICS:

1. Accuracy:
   Correct root_cause predictions / Total predictions
   Target: > 85%

2. Precision by category:
   For root_cause="timeout":
     True positives / (True positives + False positives)
   Target: > 80% per category

3. Recall by category:
   For root_cause="timeout":
     True positives / (True positives + False negatives)
   Target: > 80% per category

4. Confidence calibration:
   Do 90% confidence predictions have 90% accuracy?
   Measure: Brier score, calibration plots

5. Cost per diagnosis:
   LLM API cost / Number of diagnoses
   Target: < $0.10 per diagnosis (with caching: < $0.01)

6. Latency:
   Time from evidence collection to validated output
   Target: < 15s (p95), < 10s (p50)
```

**Automated Testing Pipeline:**
```
┌────────────────────────────────────────────────────────┐
│         TEMPLATE EVALUATION PIPELINE                    │
└────────────────────────────────────────────────────────┘

1. Load Template:
   template = load_yaml("diagnostic_v3.yaml")

2. Load Test Data:
   failures = read_jsonl("ground_truth_failures.jsonl")

3. For Each Test Case:
   ├─ Build system prompt from template
   ├─ Build user evidence from failure.logs + failure.topology
   ├─ Call LLM API
   ├─ Parse + validate response
   ├─ Compare: response.root_cause == failure.root_cause
   ├─ Record: latency, cost, confidence
   └─ Log errors for manual review

4. Aggregate Metrics:
   ├─ Overall accuracy: 89/100 = 89%
   ├─ By category:
   │   timeout: 18/20 = 90%
   │   config_error: 25/28 = 89%
   │   auth_failure: 12/15 = 80%
   │   ...
   ├─ Avg latency: 8.2s (p50), 12.5s (p95)
   ├─ Avg cost: $0.008/diagnosis (cache hit rate: 87%)
   └─ Confidence distribution: [histogram]

5. Generate Report:
   ├─ Confusion matrix (predicted vs actual)
   ├─ Error analysis (11 incorrect predictions)
   ├─ Calibration plot (confidence vs accuracy)
   └─ Cost breakdown (cache hits vs misses)

6. Decision:
   IF accuracy > 85% AND cost < $0.01:
     PROMOTE template to production
   ELSE:
     ITERATE on template design
```

**Confusion Matrix Example:**
```
PREDICTED vs ACTUAL (v3 template, 100 test cases):

                    ACTUAL
                timeout  config  auth  race  api  device  insuff
PREDICTED
timeout            18      2      0     1     0     0       0
config_error        1     25      0     0     1     0       0
auth_failure        0      0     12     0     1     0       0
race_condition      0      1      0     8     0     0       0
api_error           0      0      1     0    10     0       0
device_unreachable  0      0      0     0     0     6       0
insufficient_evid   1      0      2     0     0     1       8

Key insights:
- timeout ↔ race_condition confusion (2 cases): Need better timing analysis
- config_error ↔ api_error (1 case): API rejections due to bad config
- auth_failure ↔ insufficient_evidence (2 cases): Need stronger evidence checks
```

---

## 6. Issues and Solutions

### Common Pitfalls

**Issue 1: Hallucination (Inventing Facts)**
```
SYMPTOM:
  Diagnosis: "BGP peer 10.0.0.1 failed due to misconfigured AS number 65001"
  Reality: Logs never mention AS 65001, topology doesn't specify it
  Root cause: LLM filled gaps with plausible-sounding BGP knowledge

SOLUTION:
  1. Strengthen evidence-only constraint:
     "Base analysis ONLY on text that appears verbatim in <logs>,
      <topology>, or <error_trace>. If information is not present,
      state 'insufficient_evidence' rather than inferring."

  2. Require citations:
     "Every claim must reference: logs:line_X or topology:path:to:key"

  3. Add negative examples:
     "WRONG: 'AS number mismatch' (not in evidence)
      RIGHT: 'insufficient_evidence - AS numbers not logged'"

  4. Validate citations post-hoc:
     Check that evidence_citations actually exist in provided evidence
```

**Issue 2: Over-Confidence on Ambiguous Data**
```
SYMPTOM:
  Evidence: "ERROR: Connection timeout"
  Diagnosis: {root_cause: "timeout", confidence: 0.95}
  Reality: Could be network issue, firewall block, or device crash
  Problem: LLM didn't recognize ambiguity

SOLUTION:
  1. Add ambiguity detection guidance:
     "If multiple root causes are plausible with similar likelihood,
      reduce confidence to < 0.7 and list alternatives in reasoning:
      'Most likely timeout (0.6), but also possible: device_unreachable
       (0.3) - insufficient evidence to distinguish.'"

  2. Confidence calibration:
     Train on dataset where ambiguous cases have ground truth confidence
     scores (e.g., 2 experts disagree → max confidence = 0.6)

  3. Add threshold behavior:
     "confidence < 0.7 → return 'insufficient_evidence' as root_cause"
```

**Issue 3: Template Drift (Accuracy Degrades Over Time)**
```
SYMPTOM:
  Week 1: 89% accuracy
  Week 4: 82% accuracy
  Week 8: 76% accuracy
  Cause: New test failure patterns not covered by template examples

SOLUTION:
  1. Continuous monitoring:
     Track weekly accuracy on held-out test set
     Alert if drops below 80%

  2. Failure pattern analysis:
     Weekly review of low-confidence diagnoses (< 0.5)
     Identify common patterns in errors

  3. Template updates:
     Add new examples for emerging patterns
     Refine constraints based on new failure modes
     Version bump: v3 → v4

  4. A/B test updates:
     Deploy v4 to 10% traffic, compare to v3
     Rollout if accuracy improvement > 3pp
```

**Issue 4: Cost Blowup (Cache Misses)**
```
SYMPTOM:
  Expected cost: $0.008/diagnosis (with caching)
  Actual cost: $0.045/diagnosis
  Cache hit rate: 20% (expected: 85%)
  Cause: Evidence structure varies, breaks cache keys

SOLUTION:
  1. Standardize evidence format:
     Always use same XML tag structure, even if sections are empty:
     <logs>...</logs>
     <topology>...</topology>
     <device_state>N/A</device_state>  # Not "omit if missing"

  2. Separate stable from volatile:
     Cache: <topology> (changes rarely)
     Don't cache: <logs> (unique per test)
     BUT: Cache "log preamble" if stable across tests

  3. Monitor cache metrics:
     Track: cache_creation_input_tokens, cache_read_input_tokens
     Alert if cache hit rate < 70%

  4. Template versioning hygiene:
     Don't change system prompt frivolously - each change invalidates cache
     Batch template updates (weekly) vs continuous tweaks
```

---

### Debugging Strategies

**Strategy 1: Evidence Replay**
```
PROBLEM:
  Diagnosis incorrect for test_bgp_042, but can't reproduce

APPROACH:
  1. Save full request/response:
     {
       "request": {
         "system": "...",
         "messages": [{"role": "user", "content": "..."}]
       },
       "response": {
         "root_cause": "timeout",
         "confidence": 0.9,
         ...
       },
       "actual_root_cause": "config_error"
     }

  2. Replay in isolation:
     Load saved request, send to LLM, compare response
     Validates: Was this a one-time fluke or systematic error?

  3. Inspect evidence:
     Print <logs> and <topology> sections
     Question: Is config_error signal actually present?

  4. Template experiment:
     Modify system prompt: Add "Pay special attention to config errors"
     Rerun: Does diagnosis change to config_error?
     Result: Identifies template weakness
```

**Strategy 2: Confidence Distribution Analysis**
```
METRIC:
  Histogram of confidence scores for 500 diagnoses

HEALTHY DISTRIBUTION:
  0.0-0.3: 5%   (insufficient evidence cases)
  0.3-0.5: 8%   (ambiguous, low confidence)
  0.5-0.7: 12%  (moderate confidence)
  0.7-0.9: 40%  (high confidence)
  0.9-1.0: 35%  (very high confidence)

UNHEALTHY DISTRIBUTION (overconfident):
  0.0-0.3: 2%
  0.3-0.5: 3%
  0.5-0.7: 5%
  0.7-0.9: 20%
  0.9-1.0: 70%  ← RED FLAG: Too many max-confidence predictions

ACTION:
  Review high-confidence errors (confidence > 0.9 but wrong)
  Add calibration examples to template:
    "Confidence 0.9+ should only apply when evidence is unambiguous
     and directly states the root cause"
```

**Strategy 3: Incremental Rollback**
```
SYMPTOM:
  Accuracy dropped from 89% to 82% after deploying v4

APPROACH:
  1. Identify change:
     Diff: diagnostic_v3.yaml vs diagnostic_v4.yaml
     Change: Added 200 words on "device state correlation"

  2. Hypothesis:
     New guidance confusing LLM, causing over-reliance on device_state
     which is often incomplete

  3. Test:
     Create v4.1: Remove device state guidance
     Evaluate on test set: Accuracy = 88%
     Conclusion: Device state guidance was harmful

  4. Rollback:
     Revert to v3 in production
     Learn: Device state requires more careful integration
```

**Strategy 4: Citation Audit**
```
CHECK:
  Do evidence_citations actually exist in the provided evidence?

SCRIPT:
  for citation in response.evidence_citations:
    if citation.startswith("logs:line_"):
      line_num = int(citation.split("_")[1])
      if line_num > len(logs.split("\n")):
        ERROR: "Citation out of range: {citation}"
    elif citation.startswith("topology:"):
      path = citation.split(":")[1:]
      if not yaml_path_exists(topology, path):
        ERROR: "Citation path not found: {citation}"

RESULT:
  8/100 responses had invalid citations → hallucination
  ACTION: Add to template: "Only cite line numbers that exist"
```

---

## 7. Production Considerations

### ROI Analysis

**Cost Breakdown:**
```
LLM API COSTS (per month, 6000 diagnoses):

Without Caching:
  ├─ System prompt: 2000 tokens × $0.003/1K = $0.006/request
  ├─ Evidence (avg): 50,000 tokens × $0.003/1K = $0.15/request
  ├─ Output: 800 tokens × $0.015/1K = $0.012/request
  └─ Total per request: $0.168
      × 6000 requests/month = $1,008/month

With Caching (85% hit rate):
  ├─ First request (cache miss, 15%):
  │   System: 2000 tokens × $0.00375/1K (cache write) = $0.0075
  │   Evidence: 50,000 tokens × $0.00375/1K = $0.1875
  │   Output: 800 tokens × $0.015/1K = $0.012
  │   Subtotal: $0.207 × 900 requests = $186.30
  │
  └─ Cached requests (85%):
      System: 2000 tokens × $0.0003/1K (cache read) = $0.0006
      Evidence: 50,000 tokens × $0.0003/1K = $0.015
      Output: 800 tokens × $0.015/1K = $0.012
      Subtotal: $0.0276 × 5100 requests = $140.76

Total with caching: $327/month
Savings: $681/month (68% reduction)

DEVELOPER TIME SAVED:
  ├─ Before: 6000 failures × 10 min triage = 1000 hours
  ├─ After: 6000 failures × 30 sec review = 50 hours
  └─ Saved: 950 hours/month × $400/hr = $380,000/month

NET ROI:
  Benefit: $380,000/month
  Cost: $327/month (LLM) + $2,000/month (infra/ops)
  ROI: 163x return on investment
```

**Infrastructure Costs:**
```
ATIYA PLATFORM (monthly):

┌──────────────────────────────────────────────────────┐
│ Component               │ Cost      │ Details        │
├──────────────────────────────────────────────────────┤
│ API Server (FastAPI)    │ $120      │ AWS ECS 2vCPU  │
│ Database (SQLite/S3)    │ $15       │ S3 storage     │
│ Observability (DataDog) │ $200      │ Logs + metrics │
│ ReportPortal integration│ $50       │ Webhook hosting│
│ LLM API (Anthropic)     │ $327      │ With caching   │
│ Template storage (Git)  │ $0        │ Existing repo  │
│ Secrets (AWS KMS)       │ $5        │ API key mgmt   │
│ Engineering overhead    │ $1,283    │ 10% of costs   │
├──────────────────────────────────────────────────────┤
│ TOTAL                   │ $2,000/mo │                │
└──────────────────────────────────────────────────────┘

BREAK-EVEN ANALYSIS:
  If 1 developer (cost: $16,000/month) saves 12.5% of time:
    $16,000 × 0.125 = $2,000 saved = BREAK-EVEN
  
  Actual: 950 hours/month saved across 20 developers
    = 47.5 hours/developer/month
    = ~30% time savings per developer
    = 15x above break-even threshold
```

---

### Monitoring & Observability

**Key Metrics Dashboard:**
```
┌────────────────────────────────────────────────────────────┐
│              ATIYA PRODUCTION METRICS                       │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  Request Volume:                                            │
│    ├─ Diagnoses/day: 200 (↑ 5% WoW)                        │
│    ├─ Peak hour: 2pm UTC (45 req/hr)                       │
│    └─ Weekend traffic: 12 req/day                          │
│                                                              │
│  Quality:                                                   │
│    ├─ Accuracy (manual review, n=50/week): 89% (→)         │
│    ├─ Avg confidence: 0.84 (→)                             │
│    ├─ Insufficient evidence rate: 8% (↑ 2pp)               │
│    └─ Developer feedback (thumbs up): 76% (↑ 3pp)          │
│                                                              │
│  Performance:                                               │
│    ├─ P50 latency: 8.2s (→)                                │
│    ├─ P95 latency: 12.5s (→)                               │
│    ├─ P99 latency: 18.3s (↑ 1.2s) ← ALERT                 │
│    └─ Timeout rate: 0.3% (→)                               │
│                                                              │
│  Cost:                                                      │
│    ├─ Avg cost/diagnosis: $0.008 (↓ $0.001)                │
│    ├─ Cache hit rate: 87% (↑ 2pp)                          │
│    ├─ Cache write tokens: 52M (→)                          │
│    └─ Monthly spend: $310 (under budget)                   │
│                                                              │
│  Errors:                                                    │
│    ├─ LLM API failures: 0.5% (→)                           │
│    ├─ JSON parse errors: 0.2% (→)                          │
│    ├─ Schema validation failures: 0.1% (→)                 │
│    └─ Evidence collection failures: 1.2% (↑ 0.4pp) ← WATCH │
│                                                              │
└────────────────────────────────────────────────────────────┘

ALERTS:
  🚨 P99 latency > 15s → Investigate LLM API slowness
  ⚠️  Evidence collection failures > 2% → Check ReportPortal API
```

**Logging Strategy:**
```
LOG LEVELS:

INFO: Request start/end, cache hits, output posted
  Example: "Diagnosis completed: test_bgp_042, root_cause=timeout,
            confidence=0.92, latency=8.1s, cache_hit=true"

WARN: Retries, low confidence, validation failures
  Example: "Low confidence diagnosis: test_xyz_123, confidence=0.45,
            root_cause=insufficient_evidence"

ERROR: LLM API failures, unrecoverable errors
  Example: "LLM API error: 429 Rate Limit Exceeded, attempt 3/3 failed"

DEBUG: Full prompts, responses (sampled 1%)
  Example: "System prompt: [2000 chars], User evidence: [50KB],
            Response: {root_cause: 'timeout', ...}"

STRUCTURED LOGS (JSON):
{
  "timestamp": "2026-08-20T14:32:15Z",
  "level": "INFO",
  "test_id": "test_bgp_042",
  "root_cause": "timeout",
  "confidence": 0.92,
  "latency_ms": 8100,
  "cache_hit": true,
  "template_version": "diagnostic_v3",
  "model": "claude-sonnet-4-5-20250929",
  "tokens": {"input": 52000, "output": 800}
}
```

**Distributed Tracing:**
```
TRACE SPANS (OpenTelemetry):

┌─ diagnosis_request (11.2s total) ───────────────────────┐
│                                                           │
│  ├─ evidence_collection (2.1s)                          │
│  │  ├─ fetch_logs_from_reportportal (1.8s)              │
│  │  ├─ load_topology_from_git (0.2s)                    │
│  │  └─ extract_error_trace (0.1s)                       │
│  │                                                        │
│  ├─ template_injection (0.05s)                          │
│  │                                                        │
│  ├─ llm_request (8.4s)                                  │
│  │  ├─ build_request (0.02s)                            │
│  │  ├─ api_call (8.2s) ← CACHE HIT                     │
│  │  └─ parse_response (0.18s)                           │
│  │                                                        │
│  ├─ validation (0.2s)                                   │
│  │  ├─ json_parse (0.05s)                               │
│  │  ├─ schema_check (0.10s)                             │
│  │  └─ citation_audit (0.05s)                           │
│  │                                                        │
│  └─ output_handling (0.45s)                             │
│     ├─ post_to_reportportal (0.40s)                     │
│     └─ log_to_datadog (0.05s)                           │
│                                                           │
└───────────────────────────────────────────────────────────┘

INSIGHTS:
  - 73% of time in LLM API (expected)
  - ReportPortal fetch = 16% (can optimize with caching)
  - Output posting = 4% (acceptable)
```

**Anomaly Detection:**
```
AUTOMATED CHECKS (hourly):

1. Accuracy Drift:
   IF manual_review_accuracy < 0.80:
     ALERT: "Atiya accuracy below threshold (current: 76%)"
     ACTION: Review last 20 diagnoses, check for pattern

2. Confidence Collapse:
   IF avg_confidence < 0.70 (7-day rolling):
     ALERT: "Average confidence dropped to 0.68"
     ACTION: Check if new failure types appearing

3. Cost Spike:
   IF daily_cost > $15 (expected: $10):
     ALERT: "LLM costs 50% above baseline"
     ACTION: Check cache hit rate, request volume

4. Latency Regression:
   IF p95_latency > 15s (baseline: 12.5s):
     ALERT: "Latency spike detected"
     ACTION: Check LLM API status, evidence collection time
```

---

## 8. Atiya Lens

### Implementation Specifics

**Evidence Collection Pipeline:**
```
┌────────────────────────────────────────────────────────┐
│      ATIYA EVIDENCE COLLECTOR ARCHITECTURE              │
└────────────────────────────────────────────────────────┘

Input: ReportPortal test failure event
  {
    "launch_id": "12345",
    "test_id": "67890",
    "test_name": "test_bgp_convergence_basic",
    "status": "FAILED",
    "error": "AssertionError: Idle != Established"
  }

Step 1: Fetch Logs (parallel)
  ├─ ReportPortal API: GET /api/v1/test/67890/logs
  ├─ Returns: List of log entries with timestamps
  └─ Format: 
      [
        {"level": "INFO", "message": "Test started", "time": "..."},
        {"level": "ERROR", "message": "Timeout after 30s", ...},
        ...
      ]

Step 2: Load Topology (cached, git)
  ├─ Parse test path: gpcs-tests/bgp/test_bgp_convergence_basic.py
  ├─ Find runlist: data/runfiles/bgp_regression.yaml
  ├─ Extract topology: data/topology/topology_colo_100g.yaml
  ├─ Git fetch: git show HEAD:data/topology/topology_colo_100g.yaml
  └─ Cache: Store in memory for 5 min (same topology for suite)

Step 3: Extract Error Trace
  ├─ Check logs for "Traceback" keyword
  ├─ Extract: Lines from "Traceback" to last exception line
  └─ Example:
      Traceback (most recent call last):
        File "test_bgp.py", line 142, in test_bgp_convergence_basic
          assert state == "Established"
      AssertionError: Idle != Established

Step 4: Device State (conditional)
  ├─ IF test has @pytest.fixture(device_snapshot=True):
  │   Fetch: Device show command outputs from test cleanup phase
  │   Example: "show bgp summary", "show interface"
  └─ ELSE: Skip (not all tests capture device state)

Step 5: Assemble Evidence
  ├─ Combine into XML structure:
      <test_context>...</test_context>
      <logs>...</logs>
      <topology>...</topology>
      <error_trace>...</error_trace>
      <device_state>...</device_state> (if available)
  └─ Total size: 50-150KB depending on test

Output: Structured evidence ready for template injection
Latency: ~2s (parallel fetches + git I/O)
```

**Template Selection Logic:**
```
DECISION TREE:

IF error_trace contains "Timeout":
  template = "timing_analysis_v1.yaml"
ELIF topology.type == "colo_100g":
  template = "colo_diagnostic_v2.yaml"
ELIF test_name contains "auth" OR "login":
  template = "auth_diagnostic_v1.yaml"
ELSE:
  template = "general_diagnostic_v3.yaml"  ← Default

CURRENT PRODUCTION:
  - 92% of failures use general_diagnostic_v3.yaml
  - 5% use timing_analysis_v1.yaml
  - 3% use auth_diagnostic_v1.yaml
  - Colo-specific template in development (not deployed)
```

**Output Integration:**
```
POSTING DIAGNOSIS TO REPORTPORTAL:

1. Format as comment:
   ```
   🤖 Atiya AI Diagnosis

   **Root Cause:** timeout (confidence: 92%)

   **Analysis:**
   BGP convergence timeout (30s) is insufficient for multi-tenant
   topology with 8 peers. Logs line 1847 shows last peer still in
   'OpenSent' state at timeout. Topology specifies bgp_peer_timeout: 30,
   but expected_convergence documented as 45s for 8-peer scenario.

   **Suggested Fix:**
   Increase bgp_peer_timeout to 60s in topology_colo_100g.yaml,
   section bgp_config

   **Evidence Citations:**
   - logs:line_1847:last_peer_state=OpenSent
   - topology:bgp_config:bgp_peer_timeout
   - topology:docs:expected_convergence_time_8_peers

   ---
   _Generated by Atiya v3.2 • template: diagnostic_v3 • model: claude-sonnet-4-5_
   ```

2. Post via ReportPortal API:
   POST /api/v1/test/67890/log
   {
     "message": "[formatted markdown above]",
     "level": "INFO",
     "time": "2026-08-20T14:32:26Z"
   }

3. Add tags to test:
   POST /api/v1/test/67890/update
   {
     "tags": ["atiya:timeout", "atiya:confidence_0.92"]
   }

4. Notification:
   Slack webhook to #test-failures channel (if confidence > 0.8):
   "🔍 High-confidence diagnosis for test_bgp_042: timeout (92%)"
```

---

### Metrics and Results

**Production Performance (30-day window):**
```
VOLUME:
  - Total diagnoses: 6,247
  - Avg per day: 208
  - Peak day: 312 (2026-08-15, major regression run)

QUALITY:
  - Manual review sample: 200 diagnoses
  - Accuracy: 178/200 = 89%
  - Breakdown:
      Correct diagnosis: 178 (89%)
      Partially correct: 12 (6%, right category, wrong detail)
      Incorrect: 10 (5%)
  
  - Developer feedback (opt-in thumbs up/down):
      Thumbs up: 1,824 (76%)
      Thumbs down: 579 (24%)
      No feedback: 3,844 (62% no vote)

CONFIDENCE DISTRIBUTION:
  - 0.0-0.3:   418 (6.7%)  ← Insufficient evidence cases
  - 0.3-0.5:   500 (8.0%)
  - 0.5-0.7:   812 (13.0%)
  - 0.7-0.9: 2,561 (41.0%)
  - 0.9-1.0: 1,956 (31.3%)

ROOT CAUSE BREAKDOWN:
  - timeout: 2,187 (35%)
  - config_error: 1,562 (25%)
  - device_unreachable: 937 (15%)
  - auth_failure: 562 (9%)
  - race_condition: 437 (7%)
  - api_error: 312 (5%)
  - insufficient_evidence: 250 (4%)

LATENCY:
  - P50: 8.2s
  - P95: 12.5s
  - P99: 18.3s
  - Max: 45s (1 case, LLM API slow)

COST:
  - Total spend: $310
  - Per diagnosis: $0.0496
  - Cache hit rate: 87%
  - Cache savings: $681 (68% reduction vs no caching)

TIME SAVINGS:
  - Before Atiya: 6247 × 10 min = 1,041 hours
  - With Atiya: 6247 × 30 sec = 52 hours
  - Saved: 989 hours = 24.7 work-weeks
  - $ Value: 989 × $400/hr = $395,600
```

**Accuracy Deep Dive:**
```
ERROR ANALYSIS (22 errors in 200-sample review):

1. Timeout vs Race Condition (6 errors):
   - Symptom: Intermittent timeouts misclassified as pure timeout
   - Root cause: Template lacks "intermittent" detection guidance
   - Fix: Add to v4 template

2. Config Error Missed (4 errors):
   - Symptom: Invalid VLAN ID in topology not detected
   - Root cause: Validation error buried in 50KB logs
   - Fix: Pre-filter logs for "Invalid", "Bad Request" keywords

3. Insufficient Evidence False Positive (5 errors):
   - Symptom: Enough evidence present, but LLM flagged insufficient
   - Root cause: Evidence in non-standard log format
   - Fix: Improve evidence extraction to normalize formats

4. Auth Failure Hallucination (3 errors):
   - Symptom: Claimed "401 Unauthorized" when logs showed "403 Forbidden"
   - Root cause: LLM confused HTTP status codes
   - Fix: Add examples distinguishing 401 vs 403

5. Topology Parsing Error (4 errors):
   - Symptom: YAML parsing failed, returned incomplete topology
   - Root cause: Malformed YAML in test's topology override
   - Fix: Add YAML validation before sending to LLM
```

**Developer Feedback Examples:**
```
POSITIVE (thumbs up):

"Saved me 20 minutes tracking down this timeout issue. Fix worked!" 
  — Alice, SASE team, test_bgp_convergence_multi_tenant

"Diagnosis was spot-on. VLAN ID out of range, exactly as Atiya said."
  — Bob, GPCS team, test_service_connection_create

"Love the evidence citations - jumped straight to logs:line_1847"
  — Carol, Infrastructure team, test_device_reachability

NEGATIVE (thumbs down):

"Said timeout, but it was actually a config error with BGP AS number"
  — Dave, BGP team, test_bgp_peer_establishment
  [Atiya team note: Added to error analysis, will fix in v4]

"Confidence 0.95 but completely wrong - said auth failure, was race condition"
  — Eve, Auth team, test_multi_user_login
  [Atiya team note: Overconfidence issue, calibrating in v4]

"Insufficient evidence verdict, but logs had clear error message"
  — Frank, Troubleshooting team, test_api_error_handling
  [Atiya team note: Evidence extraction bug, hotfixed]
```

---

## 9. Summary

### Core Principles

**Prompt engineering is architecture, not art:**
- System prompts = configuration files (7-component structure)
- Evidence format = API contract (XML for stability)
- Output schema = strongly-typed interface (JSON validation)
- Caching = performance optimization (90% cost reduction)

**Production readiness requires:**
1. Evidence-only constraints (prevent hallucination)
2. Explicit output schemas (enable validation)
3. Confidence calibration (avoid overconfidence)
4. Prompt caching (control costs)
5. Template versioning (enable iteration)
6. Observability (monitor quality/cost/latency)

**ROI drivers:**
- Quality: 89% accuracy → developer trust
- Cost: $0.05 → $0.005/diagnosis via caching
- Speed: 10 min → 11s per diagnosis
- Scale: 200 diagnoses/day with zero marginal cost

### Atiya Outcomes

**Quantitative:**
- 6,247 diagnoses in 30 days
- 89% accuracy (manual review)
- 76% developer approval
- $310/month LLM cost vs $395K/month time saved
- 163x ROI

**Qualitative:**
- Test failures triaged within seconds, not hours
- Standardized root cause categories enable trend analysis
- Evidence citations teach developers debugging skills
- Confidence scores help prioritize urgent vs flaky failures

### Key Takeaways

**For AI agent development:**
1. Separate instructions (system) from evidence (user)
2. Require citations for every claim
3. Use explicit JSON schemas, validate output
4. Mark stable content for caching
5. A/B test template changes
6. Monitor accuracy continuously

**For Atiya evolution:**
- Template v4: Address timeout/race confusion, add intermittency detection
- Multi-step workflow: Triage → Detailed analysis → Solution generation
- Feedback loop: Low-confidence diagnoses → manual review → training data
- Cost optimization: Pre-filter logs, cache topology separately

**Prompt engineering = software engineering:**
- Templates are code (version control, code review, testing)
- Evidence is data (schemas, validation, transformation)
- LLM is a service (SLAs, retries, observability)
- Production requires discipline, not magic

---

**END OF DOCUMENT**

Total lines: ~2,100
Focus: Visual diagrams, production patterns, Atiya specifics
Outcome: Complete learning resource for prompt engineering fundamentals in production AI agent context
