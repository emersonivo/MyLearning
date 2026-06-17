# Blind Spots & Hiring Penalties

## Expert Panel Introduction

**SRE Hiring Manager**: What follows are the unspoken rules. Things we reject candidates for but rarely explain why. This is the gap between "passed technical screens" and "got the offer."

**Incident Commander**: These are the mistakes that turn 5-minute incidents into career-limiting events. Learn them now, not during your first on-call rotation.

**Staff SRE**: The industry teaches tools. We teach judgment. This section is about judgment.

---

## Part 1: Common Industry Misconceptions

### Misconception 1: "SRE is just DevOps with a different name"

**Reality**: SRE has explicit reliability targets and the authority to say "no."

**The Difference**:
```
DevOps:
- Cultural movement
- Focus: Collaboration between dev and ops
- Goal: Faster delivery
- Authority: Influence, persuasion
- No quantified reliability targets

SRE:
- Engineering discipline  
- Focus: Treating operations as software problems
- Goal: Sustainable reliability
- Authority: Error budget enforcement
- Quantified SLOs and error budgets
```

**Why It Matters in Interviews**:
When asked "What's the difference between DevOps and SRE?", candidates who say "They're basically the same" get rejected. This shows they don't understand SRE's core mandate: **reliability is a feature, with explicit targets**.

**Correct Answer**:
"SRE applies software engineering to operations problems. Unlike DevOps, SRE has quantified reliability targets (SLOs) and can say 'no' to launches when error budget is exhausted. DevOps is about culture and collaboration; SRE is about measurable outcomes."

---

### Misconception 2: "More alerts = better monitoring"

**Reality**: Alert fatigue destroys reliability.

**The Math**:
```
Scenario: 100 alerts, 10% actionable

On-call rotation: 1 week
Alerts received: 100
Actionable: 10
False positives: 90

Result:
- Engineer pages ignored
- Real incidents missed
- Engineer burns out, quits
- MTTR increases (takes longer to notice real problems)
```

**What Senior SREs Know**:
- Every alert must be actionable
- Symptom-based (user impact), not cause-based (Redis is down)
- Tuned to minimize false positives
- Grouped (related alerts fire once, not 50 times)

**Interview Red Flag**:
Candidate says: "I'd add alerts for CPU, memory, disk, network, database connections, queue depth, error rate, latency..."

**Why This Fails**:
Shows they don't understand alert fatigue or prioritization. They're thinking "what could go wrong" not "what matters to users."

**Correct Approach**:
"I'd start with symptom-based alerts tied to SLOs: error rate and latency. Then expand based on actual incidents—only alert on things that previously caused outages and weren't caught."

---

### Misconception 3: "My service is too important to have an error budget"

**Reality**: Everything has an error budget. The question is what it is, not whether it exists.

**Why This Thinking is Dangerous**:
```
Claims:
"Payment processing is critical—we need 100% uptime"
"Auth service can never go down"
"User data must be perfectly consistent"

Reality:
- 100% uptime is physically impossible
- Five 9s (99.999%) = 5 minutes downtime/year
- Cost: Millions in redundancy, complexity, operational burden

Better Question:
"What's the actual user impact of different availability levels?"

Example:
99.9% (43 min/month) vs 99.99% (4.3 min/month):
- User impact: Most users never notice 40-minute outage if not during peak
- Cost difference: 10x infrastructure and operational complexity
```

**Interview Trap**:
Interviewer asks: "What SLO would you set for a payment API?"

**Wrong Answer**: "99.99% or higher—payments are critical"

**Right Answer**: "I'd start by understanding:
- Current baseline reliability
- Cost of each additional nine
- Business impact of different outage durations
- Then propose 99.9% initially, with data to justify higher if needed"

**Why**: Shows you understand tradeoffs, not just ideals.

---

### Misconception 4: "We need 99.99% uptime for everything"

**Reality**: Different services need different SLOs based on user impact.

**SLO Hierarchy Example**:

```
Critical Path (User-facing, revenue-impacting):
- Payment API: 99.95%
- Checkout API: 99.9%
- Product Search: 99.9%

Important but Gracefully Degradable:
- Recommendation Engine: 99.5%
- User Reviews: 99%
- Analytics Dashboard: 99%

Internal Tools:
- Admin Dashboard: 99% (business hours only)
- Internal Reporting: 95%
```

**Cost Analysis**:
```
99.9% (43 min/month):
- 10 instances
- Active-passive failover
- Cost: $10k/month

99.99% (4.3 min/month):
- 50 instances (regional redundancy)
- Active-active across 3 regions
- Cost: $80k/month

99.999% (26 seconds/month):
- 200 instances (global redundancy)
- Active-active across 5 regions
- Custom load balancing
- Cost: $500k/month
```

**Hiring Penalty**:
Candidates who reflexively say "high availability" for everything show they don't understand cost-benefit analysis or priority setting.

---

### Misconception 5: "Incidents are caused by bad engineers"

**Reality**: Incidents are caused by system design flaws that humans trigger.

**Blameless Post-Mortem Principle**:
```
Bad Post-Mortem:
"Engineer deployed without testing"
→ Action: "Engineers must test better"
→ Result: Fear, no learning, problem recurs

Good Post-Mortem:
"Deploy lacked automated integration tests"
"Test environment differed from production"
"No rollback mechanism for failed deploys"
→ Actions:
  1. Add integration tests to CI/CD
  2. Synchronize test/prod environments  
  3. Implement auto-rollback on error spike
→ Result: System improvement, no recurrence
```

**Interview Question**: "Tell me about an outage you caused."

**Wrong Answer**: 
"I made a mistake and deployed bad code. I learned to be more careful."

**Right Answer**:
"I deployed a change that caused an outage. The system allowed the deploy despite test failures. We improved this by adding deploy gates, better testing, and automated rollback. The incident revealed gaps in our safety mechanisms."

**Why This Matters**:
Shows you understand systems thinking and blameless culture, not just personal responsibility.

---

## Part 2: What Beginners Are Never Taught

### Hidden Truth 1: SLOs are negotiation tools, not technical specs

**What bootcamps teach**: "Set SLOs based on user needs"

**What's actually true**: "SLOs are negotiated between SRE, product, and business"

**The Real Process**:
```
Product Manager: "We want 99.99% uptime"
SRE: "Current baseline is 99.5%. Here's the cost to reach 99.99%:"
  - $500k in infrastructure
  - 3 months of engineering time
  - Delayed feature launches
  
PM: "What can we get for less?"
SRE: "99.9% for $100k, 1 month of work"
PM: "What's the user impact difference?"
SRE: "99.9% = 43 min downtime/month
       99.99% = 4 min downtime/month
       Users unlikely to notice either during off-peak"
PM: "Let's start at 99.9% and reevaluate in 6 months"

Negotiated SLO: 99.9%
```

**Why This Isn't Taught**:
Bootcamps teach "best practices," not organizational reality. SRE work is 50% technical, 50% stakeholder management.

**Interview Signal**:
When you discuss SLOs, include phrases like:
- "Negotiate with product"
- "Balance velocity and reliability"
- "Cost-benefit analysis"

---

### Hidden Truth 2: On-call is a design problem, not just a rotation

**What bootcamps teach**: "Set up PagerDuty and rotate on-call"

**What's actually true**: "If you're paged more than 2x/week, your system design is broken"

**The Metric**: 
```
Sustainable on-call:
- Pages per week: 0-2
- False positive rate: <10%
- Pages requiring immediate action: <5%

Unsustainable on-call:
- Pages per week: >5
- False positive rate: >30%
- Engineers quit within 6 months
```

**Design Principles for Sustainable On-Call**:
1. **Fix the root cause**, don't patch symptoms
2. **Alert on symptoms** (user impact), not causes (disk at 80%)
3. **Automate responses** to known issues
4. **Group related alerts** (don't page 50 times for same incident)
5. **Tune thresholds** aggressively

**Interview Question**: "How do you make on-call sustainable?"

**Wrong Answer**: "Rotate frequently so no one burns out"

**Right Answer**: "Reduce pages through better alerting, automation, and fixing root causes. If rotation changes but page volume stays high, you haven't solved the problem. Goal is <2 pages/week."

---

### Hidden Truth 3: Production debugging requires different skills than development

**Development Debugging**:
- Use debugger, set breakpoints
- Reproduce locally
- Add print statements
- Unlimited time to investigate

**Production Debugging**:
- Cannot attach debugger (would pause service)
- Cannot reproduce locally (too many dependencies)
- Cannot add logs and redeploy (takes too long)
- Must debug from existing observability (metrics, logs, traces)

**Skills Gap**:
```
Developers learn: Code debugging
SREs need: System debugging

Example:
Developer: "Let me add more logging and redeploy"
SRE: "Service is down NOW. Use existing logs/metrics to diagnose"
```

**What SREs Actually Do**:
```
1. Check metrics (which golden signal is failing?)
2. Check recent changes (deploys, config changes)
3. Check dependencies (is downstream service failing?)
4. Check resource saturation (CPU/memory/connections/threads)
5. Check logs (for errors in time window)
6. Form hypothesis → test → iterate

Goal: Diagnosis in 5-10 minutes, not 2 hours
```

**Interview Red Flag**:
Candidate's incident response: "I'd add more logging and investigate the code"

**Why This Fails**: Too slow. Shows they don't know how to debug production systems with existing observability.

---

### Hidden Truth 4: Metrics lie (and you need to know when)

**What bootcamps teach**: "Monitor everything with metrics"

**What's actually true**: "Metrics are sampled, aggregated, and lossy. They show trends, not truth."

**Examples of Metric Lies**:

**Lie 1: Low Error Rate with Failing Users**
```
Metric: Error rate = 0%
Reality: Requests timing out before being counted
Users: Experiencing failures
Lesson: Timeout = not logged as error
Fix: Also monitor timeout rate
```

**Lie 2: Healthy Latency with Angry Users**
```
Metric: P99 latency = 200ms
Reality: Critical endpoint (/checkout) at 10s
        Other endpoints (health checks) at 10ms
Users: Can't check out
Lesson: Aggregate metrics hide per-endpoint issues
Fix: Per-endpoint SLOs
```

**Lie 3: Normal CPU with Overloaded Service**
```
Metric: CPU = 40%
Reality: Connection pool exhausted
        Threads blocked waiting
Users: Requests timing out
Lesson: CPU is not the only resource
Fix: Monitor saturation metrics (queue depth, pool utilization)
```

**Interview Question**: "Your dashboard shows everything healthy but users are complaining. How is this possible?"

**Correct Answer**: List 3-5 ways metrics can be misleading (see examples above).

---

### Hidden Truth 5: Rollback is almost always the right first move

**What beginners do**:
```
1. Incident detected
2. Start debugging root cause
3. Find bug in code
4. Fix bug
5. Test fix
6. Deploy fix
7. Service recovers

Time: 45 minutes
```

**What experienced SREs do**:
```
1. Incident detected
2. Check recent deploys
3. Rollback (if recent deploy found)
4. Service recovers

Time: 3 minutes

Then (after recovery):
5. Debug root cause
6. Fix properly
7. Test thoroughly
8. Redeploy
```

**Why Beginners Don't Rollback**:
- Want to "fix it properly"
- Pride ("I can fix this")
- Don't realize MTTR matters more than proper fix
- Conflate mitigation with remediation

**The Rule**: Mitigate first (stop the bleeding), remediate later (proper fix)

**Interview Red Flag**:
Scenario: "You deploy at 2pm. At 2:05pm, errors spike. What do you do?"

**Wrong Answer**: "I'd investigate the logs to find the bug"

**Right Answer**: "Rollback immediately. Investigate after service is healthy."

---

## Part 3: Silent Rejection Criteria

### Rejection Reason 1: Can't distinguish metrics from logs from traces

**Interview Moment**:
"How would you debug slow API responses?"

**Bad Answer**: 
"I'd check the logs"

**Why This Fails**:
Shows they don't understand observability layers. Logs are too verbose for this. Should start with metrics (latency), then traces (identify slow component), then logs (specific errors).

**Good Answer**:
"I'd start with latency metrics to confirm and quantify the slowness. Then use distributed tracing to identify which component in the request path is slow. Only then would I check logs for specific errors in that component."

---

### Rejection Reason 2: Talks about tools, not problems

**Interview Moment**:
"Tell me about your monitoring setup"

**Bad Answer**:
"We use Prometheus, Grafana, ELK stack, Jaeger, PagerDuty"

**Why This Fails**:
Tool listing without context. Shows they can operate tools but don't understand problems tools solve.

**Good Answer**:
"We need to detect when user-facing services violate SLOs. We use Prometheus for metrics (golden signals), Jaeger for distributed tracing to identify bottlenecks, and PagerDuty for alerting. The key challenge is reducing false positives—we've tuned alerts to fire only on sustained SLO violations."

**The Principle**: Problem → Solution, not Tool → Use Case

---

### Rejection Reason 3: No opinions on tradeoffs

**Interview Moment**:
"Should you retry on timeout?"

**Bad Answer**:
"Yes, retries improve reliability"
OR
"No, retries can cause cascades"

**Why This Fails**:
Binary thinking. Real answer is "it depends."

**Good Answer**:
"It depends on:
- Is the operation idempotent?
- What's the timeout duration vs expected latency?
- Is this a transient or permanent failure?
- What's the retry budget?

For payments (non-idempotent), I'd use idempotency keys. For transient network failures, yes with exponential backoff and jitter. For permanent failures (4xx), no retries."

**The Principle**: Show you understand nuance and tradeoffs.

---

### Rejection Reason 4: Describes incidents but not learnings

**Interview Moment**:
"Tell me about a production incident you handled"

**Bad Answer**:
"Database went down. We failed over to replica. It took 30 minutes. We wrote a post-mortem."

**Why This Fails**:
No reflection, no learning, no improvement.

**Good Answer**:
"Database went down. We failed over to replica manually, which took 30 minutes. Post-incident, we realized three gaps: 

1. No automated failover (we built it)
2. No monitoring of replica lag (we added it)
3. No runbook (we created one)

Next time this happened, MTTR was 3 minutes due to automation. The incident revealed system gaps we then fixed."

**The Principle**: Incidents are learning opportunities. Show growth.

---

### Rejection Reason 5: Doesn't quantify impact

**Interview Moment**:
"What was the impact of that outage?"

**Bad Answer**:
"It was bad. Users couldn't access the service."

**Why This Fails**:
Vague, no numbers, doesn't show business impact thinking.

**Good Answer**:
"30-minute total outage from 2pm-2:30pm.
- 100% of checkout requests failed (error rate: 0% → 100%)
- ~1000 users impacted
- Estimated revenue impact: $50k (1000 users × $50 avg cart value)
- Error budget consumed: 30 min of 43.2 min monthly budget (70%)
- Post-incident, we added automated rollback, reducing MTTR to <5 min"

**The Principle**: SREs think in numbers, not feelings.

---

## Part 4: DevOps-to-SRE Transition Gaps

### Gap 1: From "ship fast" to "ship reliably"

**DevOps Mindset**: Move fast, ship features, break things

**SRE Mindset**: Sustainable velocity via reliability

**The Shift**:
```
DevOps: "Let's deploy 10x/day"
SRE: "Let's deploy 10x/day AND maintain 99.9% uptime"

Tools:
- Feature flags (deploy without enabling)
- Canary deployments (1% → 10% → 100%)
- Automated rollback (errors → instant revert)
- Error budgets (quantify acceptable failure)
```

**Interview Signal**:
Discuss velocity AND reliability, not velocity OR reliability.

---

### Gap 2: From "automate everything" to "automate toil"

**DevOps**: Automate any manual task

**SRE**: Automate toil specifically

**Toil Definition** (Google SRE):
- Manual
- Repetitive
- Automatable
- Tactical (not strategic)
- Grows linearly with service scale

**Not Toil**:
- Incident response (requires judgment)
- Capacity planning (requires analysis)
- Architecture decisions

**Interview Question**: "What would you automate first?"

**Wrong Answer**: "Everything"

**Right Answer**: "I'd identify toil—manual, repetitive tasks that scale linearly. Example: provisioning database replicas. Then I'd measure time saved and prioritize highest-ROI automation."

---

### Gap 3: From "my code" to "our service"

**Developer Mindset**: I own my code

**SRE Mindset**: I own the service (code + infrastructure + operations)

**What This Means**:
```
Developer responsibilities:
- Write code
- Pass code review
- Merge to main

SRE responsibilities (includes all above, plus):
- Capacity planning
- On-call rotation
- Incident response
- Performance optimization
- Cost management
- Reliability improvements
```

**The Shift**: Ownership extends through production.

---

## Part 5: Developers-Moving-to-SRE Gaps

### Gap 1: "I can code" ≠ "I can debug production"

**Development Skills**:
- Algorithm design
- Code organization
- Unit testing
- Debugging with IDE

**SRE Skills** (additional):
- System-level thinking
- Debugging without source access (via metrics/logs)
- Distributed system failures
- Resource constraints (CPU/memory/connections)

**The Missing Piece**: Observability-driven debugging

---

### Gap 2: From "works on my machine" to "works at scale"

**Local Development**:
- Single machine
- Small dataset
- No network latency
- Unlimited resources

**Production**:
- Distributed across 100s of machines
- 1TB+ datasets
- Network failures are common
- Resource constraints are real

**What Changes**:
- Caching strategies matter
- Connection pooling matters
- Retry logic matters
- Timeouts matter

**Interview Trap**: System design questions reveal this gap.

---

## Self-Check: Do You Have These Blind Spots?

**Test 1**: Can you explain the difference between DevOps and SRE in 30 seconds?

**Test 2**: If asked "what SLO would you set for X", do you give a number with justification?

**Test 3**: Can you name 3 ways metrics can be misleading?

**Test 4**: Do you describe incidents with numbers (MTTR, impact, error budget)?

**Test 5**: When asked about tools, do you start with problems or tools?

If you fail any test: Review that section.

---

## Final Reality Check

**Hiring Manager's Actual Checklist**:
- [ ] Understands SLO/error budget mechanics
- [ ] Can debug production using metrics/logs/traces
- [ ] Shows systems thinking (not just code thinking)
- [ ] Quantifies impact and tradeoffs
- [ ] Discusses reliability and velocity together
- [ ] Demonstrates learning from incidents
- [ ] Has opinions with nuance (not binary yes/no)
- [ ] Can explain technical concepts simply
- [ ] Asks clarifying questions
- [ ] Shows curiosity about unknowns

**If you check <7 of these, you're not ready for SRE interviews.**
