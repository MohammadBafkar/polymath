---
name: chaos-experiment
description: Design a chaos experiment — hypothesis, blast radius, abort criteria, observation, rollback; small-radius first.
---

# chaos-experiment

> Design one chaos experiment. Output is the hypothesis + plan + abort criteria + observation.

## When to use

- A system is supposed to tolerate a failure that's never been tested.
- An on-call wants to verify a runbook works before they need it.
- A workflow needs a resilience signal before a major release.

## Procedure

1. **Hypothesis** — a single falsifiable statement: "When pod X dies, request error rate stays under 0.5% for 5 minutes." Not "we want to know what happens".
2. **Blast radius** — smallest first. Run in dev → staging → one prod canary → broader prod. Never start in prod.
3. **Failure to inject** — pick one:
   - Pod kill / node drain.
   - Network latency / partition between two services.
   - Disk full on one node.
   - Dependency 5xx burst (one downstream).
   - Clock skew (small).
4. **Abort criteria** — what makes you stop immediately:
   - Customer-facing error rate > X% (above the SLO threshold).
   - On-call alarmed for an unrelated reason.
   - Blast radius leaked (the experiment is affecting more than the target).
5. **Observation** — what you watch during the experiment. Pre-built dashboard. Compare against the hypothesis.
6. **Rollback** — how the injected failure is removed. Some tools do this automatically; never run an experiment without a rollback plan.
7. **Postmortem** — even if the hypothesis holds, capture what you learned. If it didn't hold, this is a fix-now finding.

## Output

```text
Chaos experiment: pod kill on refund-service (canary, staging)

Hypothesis:
  When one refund-service pod dies, error rate stays < 0.5% for 5
  minutes and recovery (back to baseline) takes < 30 seconds.

Pre-conditions:
  - SLO healthy on refund-service.
  - 3 replicas running.
  - On-call team aware (scheduled in #payments-eng).

Injection:
  kubectl delete pod -l app=refund -n payments  (single pod, random)

Observation (5 minutes):
  Grafana dashboard `refund-canary-chaos` showing:
    - request rate
    - 5xx rate (must stay < 0.5%)
    - P99 latency
    - replica count
    - pod restart count

Abort criteria:
  - 5xx rate > 1% sustained 30s.
  - Latency P99 > 2s sustained 60s.
  - Any sev1/sev2 alert fires unrelated to the experiment.

Rollback:
  Replica set controller respawns the pod automatically; no manual action.

Postmortem:
  Did the hypothesis hold? If recovery > 30s, file ticket for readiness probe
  or PDB tuning.

Promotion plan:
  Pass at staging → run on one prod canary pod → pass → run across prod.
```

## Anti-patterns to avoid

- "Just turn off X and see what happens." No hypothesis, no signal.
- Starting in prod.
- No abort criteria.
- No rollback plan because "it'll recover on its own".
