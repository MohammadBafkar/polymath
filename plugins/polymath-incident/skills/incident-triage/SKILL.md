---
name: incident-triage
description: Triage an inbound alert or report — classify severity, name the incident commander, open comms, decide whether to mitigate or investigate first.
---

# incident-triage

> First five minutes after a page. Pin severity, roles, and the first move. Output is concise and the alarm is still ringing.

## When to use

- A pager has fired and the on-call doesn't know what to do first.
- An inbound customer report describes something that *might* be an incident.

## Procedure

1. **Confirm impact** — is something user-visible broken? If not, downgrade to a ticket. (A noisy alert with no user impact is a tuning bug, not an incident.)
2. **Set severity** — pick from a fixed scale:
   - **sev1** — major user-visible outage, revenue impact, or data integrity at risk. All hands.
   - **sev2** — significant degradation; subset of users; workaround exists.
   - **sev3** — limited or low-priority degradation; can wait for business hours.
   - **sev4** — internal only, not user-visible.
3. **Name roles** — even in a small team:
   - **Incident Commander** — coordinates; doesn't fix.
   - **Operator** — touches systems.
   - **Comms lead** — talks to users and stakeholders.
   - **Scribe** — keeps a running timeline.
   The IC can be one person; the operator and scribe should not.
4. **Open comms** — incident channel (e.g. `#inc-2026-09`), status page set to `investigating` for sev1/sev2, internal stakeholder list pinged.
5. **Decide: mitigate or diagnose first?**
   - If a known rollback / failover restores service quickly → **mitigate first**, diagnose after.
   - If mitigation is risky or the root cause is unclear → **diagnose first**, but timebox (e.g. 10 min) before falling back to mitigation.

## Output

```text
Incident triage: <title>

Severity: sev1 (revenue-impacting checkout failure)
IC:        @oncall-payments
Operator:  @platform-on-call
Comms:     @oncall-pm
Scribe:    @oncall-eng

Comms:
  - Channel:    #inc-2026-09
  - Status page: posted "investigating" at 14:05
  - Stakeholder ping: VP-eng, support-lead

First move: MITIGATE FIRST.
  Action: roll refund-service back to the previous image tag (last good
  build is refund:0.4.7-prior).
  Verification: refund p99 latency below SLO for 5 minutes after rollback.

Timebox: if mitigation hasn't recovered service within 10 minutes, IC
re-evaluates: deeper diagnosis or escalation.
```

## Quality bar

- Severity assigned within 5 minutes.
- IC named (a person, not "TBD").
- Decision (mitigate vs diagnose) explicit with verification.
- Timebox on diagnosis if chosen first.

## Anti-patterns to avoid

- IC who's also the operator — they'll stop coordinating to fix things.
- "All hands" without an IC — no one is making decisions.
- Diagnosis without a timebox.
- Skipping the status page during a sev1 — silence makes customer trust worse.
