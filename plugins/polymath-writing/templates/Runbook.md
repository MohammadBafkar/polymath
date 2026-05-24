---
artifact: Runbook
schemaVersion: 0.1
title: "{{title}}"
owner: "{{owner}}"
last_reviewed: "{{date}}"
severity_for: ["sev1", "sev2"]
---

# Runbook: {{title}}

## When this runbook applies

The specific alert, symptom, or condition that should make an on-call open
this runbook. Be precise — link the alert definition if applicable.

## TL;DR

Three bullets. What is broken, the fastest reliable mitigation, the rollback.

- Symptom: …
- Mitigation: …
- Rollback / fallback: …

## Pre-checks

What to confirm before taking action.

- [ ] You have access to <system>.
- [ ] The alert is still firing.
- [ ] No active change freeze.

## Steps

Numbered, copy-paste friendly. Each step has an expected outcome.

1. **<verb>** — command or action. Expected: ….
2. **<verb>** — …. Expected: ….
3. …

## Verification

How to confirm the system is healthy after the action.

- …

## Rollback

How to reverse the action if it makes things worse.

- …

## Escalation

When to page whom.

- After <N> minutes with no improvement, page <team>.
- For data-loss risk, page <team> immediately.

## References

- Alert: …
- Architecture doc: …
- Related ADRs: …
