# Claude Code - Quick Reference Slides

**Purpose:** Fast revision slides for Claude Code topics

---

## Slide 1: Claude 4.X Model Family

**Three Models:**

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| **Opus 4.7** | Complex reasoning, architecture | Slower | Highest |
| **Sonnet 4.6** | Most tasks, production default | Balanced | Medium |
| **Haiku 4.5** | Simple tasks, bulk processing | Fastest | Lowest |

**Fast Mode:** Opus 4.6 with faster output (toggle with `/fast`)

**Key:** Use smallest model that handles the task well

---

## Slide 2: Model Selection Matrix

| Task | Model | Why |
|------|-------|-----|
| Complex planning | Opus 4.7 | Deep reasoning needed |
| Code generation | Sonnet 4.6 | Quality + speed balance |
| Simple queries | Haiku 4.5 | Fast, cost-effective |
| Debugging (complex) | Opus 4.7 | Multi-layer analysis |
| Debugging (standard) | Sonnet 4.6 | Most issues |
| Bulk processing | Haiku 4.5 | High throughput |
| Interactive work | Sonnet 4.6 | Default workhorse |

---

## Slide 3: Claude API Basics

**Installation:**
```bash
pip install anthropic
```

**Basic Call:**
```python
client = anthropic.Anthropic(api_key="...")
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "..."}]
)
```

**Key Concepts:**
- API is stateless (you manage history)
- System prompt = behavior definition
- Messages = conversation context

---

## Slide 4: Message Batches API

**What:** Submit many requests, get results later, **50% cost savings**

**When to Use:**
- ✅ Non-urgent bulk processing
- ✅ Overnight analysis jobs
- ✅ Weekly/monthly reports
- ❌ Interactive/real-time work

**Processing:** Up to 24 hours (usually faster)

**Scale:** Up to 10,000 requests per batch

---

## Slide 5: Real-time vs Batch Tradeoffs

```
┌─────────────────────┬─────────────────────┐
│ Real-time           │ Batch               │
├─────────────────────┼─────────────────────┤
│ Immediate results   │ Delayed (≤24h)      │
│ Interactive work    │ Bulk processing     │
│ Full cost           │ 50% cost savings    │
│ User waiting        │ Background work     │
└─────────────────────┴─────────────────────┘
```

**Hybrid Strategy:**
- Real-time: Critical decisions, active monitoring
- Batch: Comprehensive analysis, detailed reports

---

## Slide 6: Claude Code Platforms

| Platform | Use Case |
|----------|----------|
| **CLI** | Automation, scripting, CI/CD |
| **Desktop** | Complex tasks, file management |
| **Web** | Quick access, sharing |
| **IDE** | Active coding, context-aware |

**Note:** Same models/capabilities, different interfaces

---

## Slide 7: Cost Optimization Strategies

1. **Right-size models**
   - Don't use Opus for simple tasks
   - Use Haiku for bulk/simple work

2. **Batch when possible**
   - 50% savings for non-urgent work
   - Good for nightly/weekly jobs

3. **Smart routing**
   - Route by task complexity
   - Fallback to cheaper models

4. **Conversation management**
   - Don't send unnecessary history
   - Clear context when starting new topic

---

## Slide 8: colo-flux Implementation

**Built:** Claude API foundation for PARTS automation

**Components:**
- Model selector (task → optimal model)
- API client (history, retry, errors)
- Batch processor (50% cost savings)
- CLI interface (analyze-log, batch-analyze)

**Use Cases:**
- Real-time: Debug active failures
- Batch: Overnight analysis of all test results

---

## Slide 9: Error Handling Best Practices

**Retry Logic:**
- Exponential backoff for rate limits
- Max 3 attempts default
- Log failures for debugging

**Graceful Degradation:**
- Timeout → partial results if available
- Invalid model → fallback to Sonnet
- API error → clear user message

**Monitoring:**
- Track token usage
- Log cost per request
- Alert on unexpected spikes

---

## Slide 10: Quick Command Reference

**colo-flux CLI:**
```bash
# Real-time analysis
colo-flux analyze-log <file>

# Batch processing (50% savings)
colo-flux batch-analyze <directory>

# Check batch status
colo-flux batch-status <batch-id>

# Get batch results
colo-flux batch-results <batch-id>

# Usage stats
colo-flux stats
```

---

## Slide 11: Key Patterns

**Log Analysis:**
```python
system = "You are a test automation expert."
model = select_model(TaskType.ANALYSIS, "medium")
response = client.send_message(log_content, model, system)
```

**Code Generation:**
```python
system = "Generate valid Python code."
model = select_model(TaskType.CODE_GEN)
response = client.send_message(requirements, model, system)
```

**Batch Analysis:**
```python
requests = [BatchRequest(id, content, model) for ...]
batch_id = processor.submit_batch(requests)
results = processor.wait_for_completion(batch_id)
```

---

## Slide 12: Decision Tree

```
Need Claude for task?
├─ Yes
│   ├─ Urgent/Interactive?
│   │   ├─ Yes → Real-time API
│   │   │   ├─ Complex? → Opus 4.7
│   │   │   ├─ Standard? → Sonnet 4.6
│   │   │   └─ Simple? → Haiku 4.5
│   │   └─ No → Batch API (50% savings)
│   │       └─ Select model by complexity
│   └─ Build custom app
│       └─ Use Anthropic SDK
└─ No → Use deterministic logic
```

---

## Slide 13: Common Mistakes to Avoid

❌ **Using Opus for everything** → Wastes cost  
❌ **Not managing history** → Context bloat, high cost  
❌ **No retry logic** → Fails on transient errors  
❌ **Ignoring batch option** → Paying 2x for non-urgent work  
❌ **Wrong model for task** → Poor quality or slow/expensive  
❌ **No error handling** → Poor user experience  
❌ **Not tracking costs** → Budget surprises

---

## Slide 14: Testing Strategy

**Unit Tests:**
- Model selection logic
- Cost estimation
- Request formatting

**Integration Tests:**
- Real API calls (with key)
- Batch submission/retrieval
- Error scenarios

**Mocking:**
- Use for tests without API key
- Mock API responses
- Test error handling

---

## Slide 15: Production Checklist

✅ API key from secure source (env var, secrets manager)  
✅ Retry logic with exponential backoff  
✅ Error handling for rate limits, timeouts  
✅ Cost tracking and monitoring  
✅ Conversation history management  
✅ Model selection based on task  
✅ Batch for non-urgent bulk work  
✅ Logging for debugging  
✅ Tests covering key scenarios  
✅ Documentation for usage

---

**End of Skill 1 Claude Topics**

Next: Skill 2 - Prompt Engineering, Agent Profiles, Skills, Plugins, MCP
