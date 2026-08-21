# Claude Code - Complete Learning

**Last Updated:** 2026-08-16  
**Purpose:** Consolidated Claude Code learning from all skills (Aspects 26)

This document captures all Claude Code topics across the learning journey, organized by skill.

---

## Skill 1: Model/Provider Abstraction and Fallback

### 1.C1. Claude 4.X Model Family

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLAUDE 4.X MODEL FAMILY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐          │
│   │   OPUS 4.7      │   │   SONNET 4.6    │   │   HAIKU 4.5     │          │
│   │                 │   │                 │   │                 │          │
│   │  "The Thinker"  │   │  "The Worker"   │   │  "The Sprinter" │          │
│   │                 │   │                 │   │                 │          │
│   │  • Deepest      │   │  • Balanced     │   │  • Fastest      │          │
│   │    reasoning    │   │    quality      │   │    response     │          │
│   │  • Complex      │   │  • Code gen     │   │  • Simple       │          │
│   │    planning     │   │  • Analysis     │   │    tasks        │          │
│   │  • Hard bugs    │   │  • General use  │   │  • Bulk work    │          │
│   │                 │   │                 │   │                 │          │
│   │  $15/$75 per 1M │   │  $3/$15 per 1M  │   │  $0.25/$1.25    │          │
│   │  (in/out)       │   │  (in/out)       │   │  per 1M         │          │
│   └─────────────────┘   └─────────────────┘   └─────────────────┘          │
│           ▲                     ▲                     ▲                    │
│           │                     │                     │                    │
│   ┌───────┴─────────────────────┴─────────────────────┴───────┐            │
│   │                    models.py:12-16                         │            │
│   │  class ClaudeModel(Enum):                                  │            │
│   │      OPUS = "claude-opus-4-7"                              │            │
│   │      SONNET = "claude-sonnet-4-6"                          │            │
│   │      HAIKU = "claude-haiku-4-5-20251001"                   │            │
│   └────────────────────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────┘
```

**In colo-flux:** `models.py:12-16` defines the enum, `models.py:29-32` defines costs.

**Model IDs:**
- Opus 4.7: `claude-opus-4-7`
- Sonnet 4.6: `claude-sonnet-4-6`
- Haiku 4.5: `claude-haiku-4-5-20251001`

### 1.C2. Model Selection for Different Tasks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MODEL SELECTION FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                          ┌──────────────┐                                   │
│                          │  Task Type   │                                   │
│                          │  + Complexity│                                   │
│                          └──────┬───────┘                                   │
│                                 │                                           │
│                                 ▼                                           │
│                    ┌────────────────────────┐                               │
│                    │    select_model()      │                               │
│                    │    models.py:36-78     │                               │
│                    └────────────┬───────────┘                               │
│                                 │                                           │
│        ┌────────────────────────┼────────────────────────┐                  │
│        │                        │                        │                  │
│        ▼                        ▼                        ▼                  │
│   ┌─────────┐             ┌─────────┐             ┌─────────┐               │
│   │ PLANNING│             │ CODE_GEN│             │MONITORING│              │
│   │         │             │         │             │         │               │
│   │ Always  │             │ Always  │             │ Always  │               │
│   │ OPUS    │             │ SONNET  │             │ HAIKU   │               │
│   └─────────┘             └─────────┘             └─────────┘               │
│                                                                             │
│        ┌─────────────────────────────────────────────────┐                  │
│        │                    ANALYSIS                      │                  │
│        │  ┌─────────────┬─────────────┬─────────────┐    │                  │
│        │  │   simple    │   medium    │   complex   │    │                  │
│        │  │     ↓       │     ↓       │      ↓      │    │                  │
│        │  │   HAIKU     │   SONNET    │   SONNET    │    │                  │
│        │  └─────────────┴─────────────┴─────────────┘    │                  │
│        └─────────────────────────────────────────────────┘                  │
│                                                                             │
│        ┌─────────────────────────────────────────────────┐                  │
│        │                     DEBUG                        │                  │
│        │  ┌─────────────┬─────────────┬─────────────┐    │                  │
│        │  │   simple    │   medium    │   complex   │    │                  │
│        │  │     ↓       │     ↓       │      ↓      │    │                  │
│        │  │   SONNET    │   SONNET    │    OPUS     │    │                  │
│        │  └─────────────┴─────────────┴─────────────┘    │                  │
│        └─────────────────────────────────────────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Decision Matrix:**

```
┌──────────────┬─────────┬─────────┬─────────┐
│  Task Type   │ simple  │ medium  │ complex │
├──────────────┼─────────┼─────────┼─────────┤
│ PLANNING     │  OPUS   │  OPUS   │  OPUS   │
│ CODE_GEN     │ SONNET  │ SONNET  │ SONNET  │
│ MONITORING   │ HAIKU   │ HAIKU   │ HAIKU   │
│ ANALYSIS     │ HAIKU   │ SONNET  │ SONNET  │
│ DEBUG        │ SONNET  │ SONNET  │  OPUS   │
└──────────────┴─────────┴─────────┴─────────┘
```

**In colo-flux:** `models.py:36-78` implements `select_model()`. CLI uses it at `cli.py:62`.

**Key Principle:** Pick the smallest model that can handle the task well. Overusing Opus wastes cost; underusing creates quality issues.

### 1.C3. Fast Mode with Opus 4.6

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FAST MODE (NOT YET IMPLEMENTED)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Fast Mode is a CLAUDE CODE PLATFORM feature, not an API feature.          │
│   It gives Opus-quality responses with faster output in the CLI/IDE.        │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │                     Claude Code CLI                              │       │
│   │                                                                  │       │
│   │    $ /fast                    ← Toggle fast mode                 │       │
│   │    Fast mode: ON              ← Opus with faster streaming       │       │
│   │                                                                  │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
│   FUTURE COLO-FLUX ENHANCEMENT:                                             │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │                                                                  │       │
│   │   # cli.py - potential addition                                  │       │
│   │   @cli.command()                                                 │       │
│   │   @click.option('--fast', is_flag=True)                          │       │
│   │   def analyze_log(logfile, fast):                                │       │
│   │       if fast:                                                   │       │
│   │           model = ClaudeModel.OPUS  # Use best model             │       │
│   │           # Enable streaming for faster perceived response       │       │
│   │                                                                  │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
│   STATUS: Not implemented in colo-flux Phase 1                              │
│   REASON: Requires streaming support (Phase 2 enhancement)                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Speed/Capability Comparison:**
```
Opus 4.7:  [████████████] Deep reasoning, slower output
Fast 4.6:  [█████] Same capability, faster output
Sonnet:    [███████] Balanced
Haiku:     [██] Fast, simple
```

**When to Use:**
- Time-sensitive tasks requiring Opus-level reasoning
- Interactive debugging where speed matters
- Not just for making things faster - use when Opus quality needed with time constraints

### 1.C4. Claude API Fundamentals and SDK Usage

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CLAUDE API & SDK USAGE IN COLO-FLUX                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         1. SDK INITIALIZATION                         │  │
│  │                            client.py:38-42                            │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  self.client = anthropic.Anthropic(                             │  │  │
│  │  │      api_key=self.config.api_key,     ← From ANTHROPIC_API_KEY  │  │  │
│  │  │      timeout=self.config.timeout,      ← 300 seconds default    │  │  │
│  │  │  )                                                              │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      2. MESSAGES API CALL                             │  │
│  │                        client.py:102-118                              │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  kwargs = {                                                     │  │  │
│  │  │      "model": "claude-sonnet-4-6",     ← Model selection        │  │  │
│  │  │      "max_tokens": 4096,                ← Response limit        │  │  │
│  │  │      "messages": [                      ← Conversation history  │  │  │
│  │  │          {"role": "user", "content": "..."},                    │  │  │
│  │  │          {"role": "assistant", "content": "..."},               │  │  │
│  │  │          {"role": "user", "content": "new message"}             │  │  │
│  │  │      ],                                                         │  │  │
│  │  │      "system": "You are a PARTS expert..."  ← System prompt     │  │  │
│  │  │  }                                                              │  │  │
│  │  │  response = self.client.messages.create(**kwargs)               │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                   3. CONVERSATION HISTORY                             │  │
│  │                        client.py:44-46                                │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  Turn 1: User asks question                                     │  │  │
│  │  │      history = [{"role": "user", "content": "Q1"}]              │  │  │
│  │  │                                                                 │  │  │
│  │  │  Turn 1: Assistant responds                                     │  │  │
│  │  │      history = [{"role": "user", "content": "Q1"},              │  │  │
│  │  │                 {"role": "assistant", "content": "A1"}]         │  │  │
│  │  │                                                                 │  │  │
│  │  │  Turn 2: User follows up (Claude has context!)                  │  │  │
│  │  │      history = [{"role": "user", "content": "Q1"},              │  │  │
│  │  │                 {"role": "assistant", "content": "A1"},         │  │  │
│  │  │                 {"role": "user", "content": "Q2"}]              │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     4. RETRY WITH TENACITY                            │  │
│  │                       client.py:145-160                               │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  @retry(                                                        │  │  │
│  │  │      stop=stop_after_attempt(3),        ← Max 3 retries         │  │  │
│  │  │      wait=wait_exponential(min=1, max=60),  ← Backoff           │  │  │
│  │  │      retry=retry_if_exception_type(RateLimitError)              │  │  │
│  │  │  )                                                              │  │  │
│  │  │  def _call():                                                   │  │  │
│  │  │      return self.client.messages.create(**kwargs)               │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      5. USAGE TRACKING                                │  │
│  │                       client.py:162-180                               │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  response.usage.input_tokens   →  self.total_input_tokens       │  │  │
│  │  │  response.usage.output_tokens  →  self.total_output_tokens      │  │  │
│  │  │                                                                 │  │  │
│  │  │  cost = estimate_cost(model, input_tokens, output_tokens)       │  │  │
│  │  │  self.total_cost += cost                                        │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Claude API vs Claude Code:**
```
┌────────────────────────┬─────────────────────────┐
│ Claude Code            │ Claude API              │
│ (Interactive tool)     │ (Programmatic access)   │
├────────────────────────┼─────────────────────────┤
│ • CLI/Desktop/Web      │ • Build your own apps   │
│ • Agent capabilities   │ • Full control          │
│ • Tools, skills        │ • Programmatic calls    │
│ • For users            │ • For developers        │
└────────────────────────┴─────────────────────────┘
```

**Installation:**
```bash
pip install anthropic
```

**Common Patterns:**
- **Log Analysis**: System prompt defines expertise, user message contains log
- **Code Generation**: System prompt specifies format/style, user message describes requirements
- **Strategy Planning**: System prompt sets context, user message asks for plan

### 1.C5. Message Batches API

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MESSAGE BATCHES API FLOW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USER has 100 log files to analyze overnight                                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ STEP 1: CREATE BATCH REQUESTS                  batch.py:54-79      │    │
│  │                                                                     │    │
│  │   log1.log ──┐                                                      │    │
│  │   log2.log ──┼──► BatchRequest(custom_id="log1.log",               │    │
│  │   log3.log ──┤                 content="...",                       │    │
│  │      ...     │                 model=HAIKU)                         │    │
│  │   log100.log─┘                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ STEP 2: SUBMIT BATCH                           batch.py:77-79      │    │
│  │                                                                     │    │
│  │   batch = client.batches.create(requests=formatted_requests)       │    │
│  │   return batch.id  ──────────────────────────► "batch_abc123"      │    │
│  │                                                                     │    │
│  │   ⚡ Returns IMMEDIATELY - does not wait for processing            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ STEP 3: ANTHROPIC PROCESSES (up to 24 hours)                        │    │
│  │                                                                     │    │
│  │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐         │    │
│  │   │  log1   │    │  log2   │    │  log3   │    │  ...    │         │    │
│  │   │ analyze │    │ analyze │    │ analyze │    │         │         │    │
│  │   └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘         │    │
│  │        ▼              ▼              ▼              ▼              │    │
│  │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐         │    │
│  │   │ result1 │    │ result2 │    │ result3 │    │  ...    │         │    │
│  │   └─────────┘    └─────────┘    └─────────┘    └─────────┘         │    │
│  │                                                                     │    │
│  │   💰 50% COST SAVINGS vs real-time API calls                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ STEP 4: POLL STATUS                            batch.py:81-100     │    │
│  │                                                                     │    │
│  │   $ colo-flux batch-status batch_abc123                             │    │
│  │                                                                     │    │
│  │   Batch ID: batch_abc123                                            │    │
│  │   Status: in_progress          ← or "ended" when complete           │    │
│  │   Request counts:                                                   │    │
│  │     Total: 100                                                      │    │
│  │     Succeeded: 45                                                   │    │
│  │     Processing: 55                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ STEP 5: GET RESULTS                            batch.py:122-155    │    │
│  │                                                                     │    │
│  │   $ colo-flux batch-results batch_abc123                            │    │
│  │                                                                     │    │
│  │   [log1.log]                                                        │    │
│  │   Root cause: SSL certificate expired on 2026-08-15                 │    │
│  │                                                                     │    │
│  │   [log2.log]                                                        │    │
│  │   Root cause: Connection timeout - firewall blocking port 443       │    │
│  │   ...                                                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Benefits:**
1. **Cost**: 50% discount on same models/quality
2. **Scale**: Process up to 10,000 requests per batch
3. **Async**: Submit and forget, check later

**Processing Time:**
- Up to 24 hours (usually faster)
- Check status anytime
- Results stored for 30 days

### 1.C6. Tradeoffs: Real-time vs Batch Processing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REAL-TIME vs BATCH PROCESSING                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│        REAL-TIME (Messages API)              BATCH (Batches API)            │
│        ─────────────────────────             ──────────────────────         │
│                                                                             │
│   ┌─────────────────────────┐           ┌─────────────────────────┐         │
│   │   colo-flux analyze-log │           │  colo-flux batch-analyze│         │
│   │      single_file.log    │           │       logs_directory/   │         │
│   └───────────┬─────────────┘           └───────────┬─────────────┘         │
│               │                                     │                       │
│               ▼                                     ▼                       │
│   ┌─────────────────────────┐           ┌─────────────────────────┐         │
│   │  client.send_message()  │           │ processor.submit_batch()│         │
│   │      cli.py:70-76       │           │     cli.py:166-172      │         │
│   └───────────┬─────────────┘           └───────────┬─────────────┘         │
│               │                                     │                       │
│               ▼                                     ▼                       │
│   ┌─────────────────────────┐           ┌─────────────────────────┐         │
│   │      BLOCKS until       │           │   Returns batch_id      │         │
│   │    response received    │           │     IMMEDIATELY         │         │
│   │     (2-30 seconds)      │           │                         │         │
│   └───────────┬─────────────┘           └───────────┬─────────────┘         │
│               │                                     │                       │
│               ▼                                     ▼                       │
│   ┌─────────────────────────┐           ┌─────────────────────────┐         │
│   │   Print analysis NOW    │           │   Check back in hours   │         │
│   └─────────────────────────┘           │  colo-flux batch-status │         │
│                                         │  colo-flux batch-results│         │
│                                         └─────────────────────────┘         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                           COMPARISON TABLE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌────────────────┬───────────────────────┬───────────────────────┐        │
│   │    Aspect      │      REAL-TIME        │        BATCH          │        │
│   ├────────────────┼───────────────────────┼───────────────────────┤        │
│   │ Latency        │ Seconds               │ Up to 24 hours        │        │
│   │ Cost           │ Full price            │ 50% DISCOUNT          │        │
│   │ Use case       │ Interactive debugging │ Overnight bulk work   │        │
│   │ User waits?    │ Yes                   │ No                    │        │
│   │ Complexity     │ Simple                │ Need status tracking  │        │
│   │ Best for       │ 1-10 items            │ 10-10,000 items       │        │
│   └────────────────┴───────────────────────┴───────────────────────┘        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                          WHEN TO USE WHICH                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   USE REAL-TIME:                         USE BATCH:                         │
│   ✓ Debugging a failing test NOW         ✓ Analyze last night's failures   │
│   ✓ Interactive troubleshooting          ✓ Process 100+ log files          │
│   ✓ Need answer in < 1 minute            ✓ Results needed by morning       │
│   ✓ Single file analysis                 ✓ Budget-conscious bulk work      │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │  COST EXAMPLE:                                                   │       │
│   │                                                                  │       │
│   │  100 log files × 1000 input tokens × 500 output tokens          │       │
│   │                                                                  │       │
│   │  Real-time (HAIKU):                                              │       │
│   │    Input:  100 × 1000 / 1M × $0.25 = $0.025                      │       │
│   │    Output: 100 × 500 / 1M × $1.25  = $0.0625                     │       │
│   │    Total: $0.0875                                                │       │
│   │                                                                  │       │
│   │  Batch (HAIKU, 50% off):                                         │       │
│   │    Total: $0.0875 × 0.5 = $0.044  ← HALF THE COST               │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.C7. Claude Code Platforms

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE PLATFORMS vs COLO-FLUX                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CLAUDE CODE = Anthropic's official agentic coding tool                    │
│   COLO-FLUX   = Our custom tool built WITH the Claude API                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     CLAUDE CODE PLATFORMS                           │    │
│  │                                                                     │    │
│  │   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────────────┐    │    │
│  │   │   CLI   │   │ Desktop │   │   Web   │   │ IDE Extensions  │    │    │
│  │   │         │   │  App    │   │  App    │   │ (VSCode, etc)   │    │    │
│  │   │ claude  │   │Mac/Win  │   │claude.ai│   │                 │    │    │
│  │   │ command │   │         │   │/code    │   │                 │    │    │
│  │   └────┬────┘   └────┬────┘   └────┬────┘   └────────┬────────┘    │    │
│  │        │             │             │                  │             │    │
│  │        └─────────────┴──────┬──────┴──────────────────┘             │    │
│  │                             │                                       │    │
│  │                             ▼                                       │    │
│  │              ┌──────────────────────────────┐                       │    │
│  │              │  Claude Code uses Claude API  │                       │    │
│  │              │  (same API colo-flux uses!)   │                       │    │
│  │              └──────────────────────────────┘                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    HOW THEY RELATE                                  │    │
│  │                                                                     │    │
│  │                                                                     │    │
│  │   ┌─────────────────┐          ┌─────────────────┐                  │    │
│  │   │  Claude Code    │          │    colo-flux    │                  │    │
│  │   │  (the platform) │          │  (our CLI tool) │                  │    │
│  │   └────────┬────────┘          └────────┬────────┘                  │    │
│  │            │                            │                           │    │
│  │            │   You ran /colo-flux       │                           │    │
│  │            │   in Claude Code CLI       │                           │    │
│  │            │   to BUILD colo-flux!      │                           │    │
│  │            │                            │                           │    │
│  │            ▼                            ▼                           │    │
│  │   ┌─────────────────────────────────────────────────┐               │    │
│  │   │              ANTHROPIC CLAUDE API               │               │    │
│  │   │                                                 │               │    │
│  │   │  • Messages API (real-time)                     │               │    │
│  │   │  • Batches API (50% off)                        │               │    │
│  │   │  • Models: Opus, Sonnet, Haiku                  │               │    │
│  │   └─────────────────────────────────────────────────┘               │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    KEY DIFFERENCE                                   │    │
│  │                                                                     │    │
│  │   Claude Code:                                                      │    │
│  │   • General-purpose AI coding assistant                             │    │
│  │   • Interactive, conversational                                     │    │
│  │   • Built-in tools (file edit, bash, etc.)                          │    │
│  │   • For developers writing any code                                 │    │
│  │                                                                     │    │
│  │   colo-flux:                                                        │    │
│  │   • PARTS-specific automation                                       │    │
│  │   • Domain-focused prompts                                          │    │
│  │   • Can run headless (CI/CD, cron)                                  │    │
│  │   • Batch processing for cost savings                               │    │
│  │   • For QA engineers analyzing test failures                        │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                   USAGE SCENARIOS                                   │    │
│  │                                                                     │    │
│  │   1. Developer uses Claude Code CLI to write colo-flux code         │    │
│  │      $ claude                                                       │    │
│  │      > /learn-and-implement  ← skill that teaches + builds colo-flux│    │
│  │                                                                     │    │
│  │   2. QA engineer uses colo-flux CLI to analyze failures             │    │
│  │      $ colo-flux analyze-log failure.log                            │    │
│  │                                                                     │    │
│  │   3. CI/CD pipeline uses colo-flux for automated triage             │    │
│  │      $ colo-flux batch-analyze /nightly/logs/                       │    │
│  │      $ colo-flux batch-results $BATCH_ID >> report.txt              │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Platform Selection:**
- **CLI**: Automation scripts, CI/CD integration, terminal workflows
- **Desktop**: Complex multi-file tasks, visual file management
- **Web**: Quick access, sharing, no installation needed
- **IDE Extension**: Active development, context-aware assistance

**Note:** All platforms use the same underlying Claude models and capabilities. The difference is interface and integration, not AI capability.

---

## Implementation: colo-flux Phase 1

**What Was Built:**
A Claude-powered automation foundation for PARTS testing workflows with:
- Smart model selection (Opus/Sonnet/Haiku based on task type)
- Claude API client with conversation history and retry logic
- Batch processing for 50% cost savings on bulk operations
- CLI interface for real-time and batch operations

**Key Components:**
1. `config.py`: API configuration and settings
2. `models.py`: Task-based model selection logic
3. `client.py`: Claude API wrapper with retry/history
4. `batch.py`: Batch operations processor
5. `cli.py`: Command-line interface
6. `tests/`: Unit and integration tests

**Commands Implemented:**
- `colo-flux analyze-log <file>`: Real-time log analysis
- `colo-flux batch-analyze <dir>`: Batch process logs (50% savings)
- `colo-flux batch-status <id>`: Check batch status
- `colo-flux batch-results <id>`: Retrieve batch results
- `colo-flux stats`: Show usage statistics

**Success Criteria Met:**
✅ Model selection works correctly  
✅ Real-time API calls functional  
✅ Conversation history maintained  
✅ Batch processing implemented  
✅ CLI commands operational  
✅ Error handling and retries working  
✅ Cost tracking implemented  
✅ Tests passing

### Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COLO-FLUX COMPLETE ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                           USER COMMANDS                                     │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│   │ analyze-log │  │debug-failure│  │batch-analyze│  │batch-status │       │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│          │                │                │                │              │
│          └────────────────┴────────┬───────┴────────────────┘              │
│                                    │                                       │
│                                    ▼                                       │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                           cli.py                                    │  │
│   │                     (Click command routing)                         │  │
│   └─────────────────────────────────┬───────────────────────────────────┘  │
│                                     │                                      │
│                    ┌────────────────┴────────────────┐                     │
│                    │                                 │                     │
│                    ▼                                 ▼                     │
│   ┌─────────────────────────────┐   ┌─────────────────────────────┐       │
│   │        client.py            │   │         batch.py            │       │
│   │   (Real-time Messages)      │   │    (Batches API 50% off)    │       │
│   │                             │   │                             │       │
│   │ • send_message()            │   │ • submit_batch()            │       │
│   │ • conversation_history      │   │ • get_status()              │       │
│   │ • retry with tenacity       │   │ • get_results()             │       │
│   │ • usage tracking            │   │                             │       │
│   └──────────────┬──────────────┘   └──────────────┬──────────────┘       │
│                  │                                 │                       │
│                  └─────────────┬───────────────────┘                       │
│                                │                                           │
│                                ▼                                           │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                         models.py                                   │  │
│   │                                                                     │  │
│   │  select_model(TaskType, complexity) ──► OPUS / SONNET / HAIKU      │  │
│   │  estimate_cost(model, in_tokens, out_tokens) ──► $0.xxx            │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                │                                           │
│                                ▼                                           │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                         config.py                                   │  │
│   │                                                                     │  │
│   │  ClaudeConfig:                                                      │  │
│   │    api_key ← ANTHROPIC_API_KEY env var                              │  │
│   │    default_model = "claude-sonnet-4-6"                              │  │
│   │    max_tokens = 4096                                                │  │
│   │    timeout = 300s                                                   │  │
│   │    max_retries = 3                                                  │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                │                                           │
│                                ▼                                           │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     ANTHROPIC CLAUDE API                            │  │
│   │                   (anthropic Python SDK)                            │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways

**Model Selection:**
- Use smallest model that handles the task
- Opus for complex reasoning, Sonnet for most work, Haiku for simple/bulk
- Fast mode for time-sensitive Opus-level tasks

**API Usage:**
- API is stateless - manage conversation history yourself
- System prompts define behavior, user messages contain task
- Include full context in each call

**Cost Optimization:**
- Batch API: 50% savings when time allows
- Right-size models: Don't use Opus for simple tasks
- Hybrid approach: Real-time for critical, batch for comprehensive

**Platform Choice:**
- Claude Code (CLI/Desktop/Web/IDE) for interactive work
- Claude API for programmatic automation and custom apps
- Choose based on workflow, not capability

---

**Next:** Skill 2 will cover LLM Integration, Prompt Engineering, and Agent Profiles (12 Claude topics + 33 technical subskills)
