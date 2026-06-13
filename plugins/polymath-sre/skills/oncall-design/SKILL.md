---
name: oncall-design
description: Design an on-call program — rotation + escalation, alert quality/actionability, runbook coverage, toil budget, handoff, and the operational-review loop.
---

# oncall-design

> A healthy on-call is measured by how often it pages and whether each page was worth waking someone. Design for few, actionable, runbook-backed pages — then protect the humans in the rotation.

## When to use

- Standing up or fixing an on-call rotation, or alert fatigue/burnout is showing.
- Pages are noisy, non-actionable, or land on someone with no runbook.
- A workflow invokes `polymath-sre:oncall-design`.

Not this when: you are running a live incident (`polymath-incident:incident-triage`) or designing the SLO/error budget the alerts derive from (`polymath-sre:slo-design`). This designs the on-call *program*.

## Inputs

- Team size, coverage need (business-hours vs 24×7, regions), and current alert/page volume.
- The services owned and their SLOs.

## Procedure

1. **Rotation + coverage**: size the rotation so on-call recurs sustainably (rule of thumb ≥ 6–8 responders for 24×7; otherwise follow-the-sun or business-hours + best-effort). Define primary/secondary and a humane shift length.
2. **Escalation policy**: who's paged, the time-to-ack before escalating to secondary/manager, and the unambiguous severity ladder. No page should dead-end.
3. **Alert quality — the core**: every page must be *actionable* (a human must do something now) and tied to user-facing symptoms/SLO burn, not raw cause metrics. Audit existing alerts: delete/downgrade non-actionable ones to tickets/dashboards. Target a low pages-per-shift.
4. **Runbook coverage**: every alert links to a runbook with diagnosis + mitigation steps (author via `polymath-writing:runbook`). An alert with no runbook is an incomplete alert.
5. **Toil budget**: cap the fraction of on-call/eng time spent on repetitive manual work; route recurring toil to automation backlog. Track it.
6. **Handoff**: a structured shift handoff (open issues, watch-items, recent changes) so context isn't lost between rotations.
7. **Operational-review loop**: a recurring review of paging volume, noisy alerts, recurring toil, and follow-up actions — the feedback loop that keeps on-call healthy. Feed incident action items (`incidentRetroToActions`) in here.
8. **Comp/sustainability**: acknowledge on-call load (comp, time back, no-meeting recovery) so the rotation is retained.

## Output

- A one-page on-call design: rotation + coverage model, escalation policy with ack timeouts, the alert-quality bar + audit outcome, runbook-coverage requirement, toil budget, handoff format, and the operational-review cadence.

## Quality bar

- Every alert that pages is actionable, symptom/SLO-based, and runbook-linked — non-actionable ones are demoted.
- The rotation size makes on-call sustainable; escalation never dead-ends.
- A toil budget and a recurring operational review exist as the feedback loop.
- A structured handoff is defined.
