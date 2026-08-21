# colo-flux Specification - Quick Reference

**Last Updated:** 2026-08-16  
**Use this during ALL Aspect 26 (Claude Code) learning sessions**

---

## What colo-flux Is

**A button-driven Streamlit automation tool for Colo SC performance testing**

**NOT:** A chat interface, multi-agent coordinator, or complex AI orchestration system  
**YES:** Simple UI with buttons that trigger Python functions calling Claude API

---

## The 6 Button Operations

```
╔════════════════════════════════════════════════════════╗
║  colo-flux - Colo SC Performance Automation            ║
╠════════════════════════════════════════════════════════╣
║                                                         ║
║  [Deploy Latest AMI - SC]  [Deploy Latest AMI - RN]   ║
║  [Deploy saas-agent - SC]  [Deploy saas-agent - RN]   ║
║                                                         ║
║  [Full Deployment (3-Step)]  [Cleanup]                ║
║                                                         ║
║  [Run Daily Perf Test & Auto-Triage]                   ║
║                                                         ║
║  Tabs: [Operations] [Dashboard] [Results] [Triage]    ║
╚════════════════════════════════════════════════════════╝
```

### 1. Deploy Latest AMI (Colo SC or RN)
- Find latest AMI from artifact registry
- Upgrade existing instances in-place
- **Reference:** `~/reg/pa_regression_hook/tools/colo-flux/deploy_ami.sh`

### 2. Deploy Latest saas-agent (Colo SC or RN)
- Find latest saas-agent version
- Upgrade saas-agent on instances

### 3. Full Deployment (3-Step)
- Step 1: Provision infrastructure
- Step 2: Deploy Colo SC/RN
- Step 3: Configure and verify
- **Reference:** `~/reg/pa_regression_hook/tools/colo-flux/3_step_deployment.sh`

### 4. Cleanup Deployment
- Teardown test environment
- **Reference:** `~/reg/pa_regression_hook/tools/colo-flux/cleanup.sh`

### 5. Run Daily Perf Test & Auto-Triage
- Run PARTS performance tests
- Compare vs baseline
- **Auto-triage failures** using Claude Opus
- **Use Batches API** for overnight runs (50% savings)

### 6. Dashboard Tab
- View historical results
- See triage reports
- Track performance trends

---

## Claude Model Selection (Per Operation)

| Operation | Model | Why | Cost |
|-----------|-------|-----|------|
| Find latest image/version | **Haiku 4.5** | Simple API query, JSON parsing | ~$0.01 |
| Deploy/Upgrade | **Sonnet 4.6** | Orchestration, error handling | ~$0.10 |
| Performance analysis | **Sonnet 4.6** | Statistical comparison | ~$0.10 |
| **Auto-triage failures** | **Opus 4.7** | Deep root cause analysis + RAG | ~$1.00 |
| **Overnight triage** | **Opus 4.7 Batches** | Same, 50% cheaper | ~$0.50 |

---

## Architecture Pattern (Simple!)

```python
# Streamlit UI
if st.button("Run Daily Perf Test"):
    # 1. Run tests (PARTS framework)
    results = run_perf_tests()
    
    # 2. If failed, call Claude for triage
    if results.failed:
        if is_overnight():
            # Use Batches API (50% cheaper)
            batch_id = submit_triage_batch(results)
            st.info(f"Triage submitted (batch {batch_id})")
        else:
            # Real-time triage
            triage = call_claude_opus(results)
            st.success(f"Triage complete: {triage}")
```

**Key Principle:** Buttons → Python handlers → Claude API calls → Store results → Display

---

## What You'll Build (Phase by Phase)

### Phase 1 🔷 (Weeks 1-5)
- [ ] Claude API integration (Anthropic SDK)
- [ ] Model selection logic (Haiku/Sonnet/Opus)
- [ ] Structured outputs (DeploymentStatus, TestResults, TriageReport)
- [ ] Cost tracking per operation
- [ ] **Deliverable:** AMI deployment buttons + basic dashboard

### Phase 2 🔷 (Weeks 6-10)
- [ ] PostgreSQL: deployment history, test results
- [ ] State tracking for deployments
- [ ] Prompt caching for templates
- [ ] Error handling and retry logic
- [ ] **Deliverable:** Full deployment + cleanup working

### Phase 3 🔷 (Weeks 11-16)
- [ ] **Batches API integration** (50% cost savings for overnight triage)
- [ ] Structured error responses (isError, isRetryable, errorCategory)
- [ ] Loop termination for 3-step deployments
- [ ] Retry logic and graceful degradation
- [ ] **Deliverable:** Daily perf test with auto-triage (Batches API)

### Phase 4 🔷 (Weeks 17-21)
- [ ] RAG knowledge base (Colo 100G playbook, JIRA, past failures)
- [ ] pgvector for semantic search
- [ ] Two-stage RAG (retrieve → judge relevance)
- [ ] Intelligent triage with historical data
- [ ] **Deliverable:** Smart triage with RAG-powered root cause analysis

### Phase 5 (Weeks 22-24)
- [ ] Production Streamlit deployment
- [ ] Dashboard tabs (Operations, Results, Triage)
- [ ] Performance charts and trends
- [ ] Cost monitoring dashboard
- [ ] **Deliverable:** Production UI

### Phase 6 (Weeks 25-28)
- [ ] Security controls
- [ ] Golden dataset (100+ scenarios)
- [ ] Triage accuracy testing (>85%)
- [ ] CI/CD integration
- [ ] **Deliverable:** Production-hardened colo-flux

---

## Key Simplifications (What NOT to Build)

**❌ DO NOT BUILD:**
- Multi-agent coordinator/orchestrator
- Hub-and-spoke architecture
- CrewAI or LangGraph frameworks (overkill for buttons)
- Chat interface or conversational agent
- Complex agent pipeline

**✅ ACTUALLY BUILD:**
- Simple Streamlit buttons
- Python functions calling Claude API
- Smart model selection (Haiku/Sonnet/Opus)
- Batches API for cost optimization
- RAG for intelligent triage

---

## Success Criteria

- [ ] 6 buttons fully functional
- [ ] Deploy + test cycle <10 minutes
- [ ] Auto-triage accuracy >85%
- [ ] Batches API saves 50% on overnight runs
- [ ] Cost per full cycle <$2
- [ ] Dashboard shows trends and triage reports

---

## Integration References

**Deployment Scripts:**
- Location: `~/reg/pa_regression_hook/tools/colo-flux/`
- Use as reference for button handler implementations

**Data Sources:**
- GCP Artifact Registry (for latest images)
- PARTS framework (for performance tests)
- PostgreSQL (for results, history, baselines)
- Colo 100G playbook (for RAG)
- JIRA API (for past failures)

---

## When Learning Aspect 26 (Claude Code Topics)

**Remember:**
1. **Learn** Claude Code patterns (how Claude implements the concept)
2. **Apply** to colo-flux (button-driven, simple architecture)
3. **Don't over-engineer** (no complex multi-agent orchestration)
4. **Use reference scripts** in `~/reg/pa_regression_hook/tools/colo-flux/`

**Example - Phase 3 Learning:**
- **Study:** Claude Code's multi-agent patterns (Agent tool, subagents, orchestration)
- **Understand:** When/why to use complex orchestration
- **Apply to colo-flux:** Simple Batches API for overnight triage (NOT multi-agent coordinator)
- **Reason:** Buttons are the orchestrator, Claude provides intelligence per button

---

## Quick Comparison: Atiya vs colo-flux

| Aspect | Atiya (Track 1) | colo-flux (Track 2) |
|--------|-----------------|---------------------|
| **Learning** | AI concepts (Aspects 1-25) | Claude Code (Aspect 26) |
| **Implementation** | `/go-atiya` skill | You build it |
| **Architecture** | Multi-agent pricing pipeline | Button-driven automation |
| **Orchestration** | CrewAI or LangGraph | Simple button handlers |
| **Complexity** | High (learn multi-agent patterns) | Low (practical automation) |
| **Purpose** | Master AI theory | Master Claude Code |

**Both are production systems, different complexity levels for different learning goals**

---

**Always reference this document during Aspect 26 learning to stay aligned!**
