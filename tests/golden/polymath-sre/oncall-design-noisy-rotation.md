---
plugin: polymath-sre
scenario: oncall-design-noisy-rotation
expect:
  invoked:
    - polymath-sre:oncall-design
  output_matches:
    - "(actionable|symptom|SLO)"
    - "(runbook)"
    - "(toil|escalation|rotation)"
  not_invoked:
    - polymath-incident:incident-triage
timeout_seconds: 120
---

# Prompt

> Our on-call is miserable: ~40 pages a shift, most are CPU/memory
> alerts nobody acts on, half have no runbook, and people are burning
> out. Help me redesign it.

Use polymath-sre:oncall-design.

# Acceptance

- Non-actionable cause-metric alerts (raw CPU/memory) are demoted; pages must be actionable and symptom/SLO-based.
- Runbook coverage is required for every paging alert.
- Rotation/escalation sized for sustainability; a toil budget + operational-review loop is defined.
- Targets a low pages-per-shift, with the alert audit as the first step.
