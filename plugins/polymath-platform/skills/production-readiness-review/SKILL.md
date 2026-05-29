---
name: production-readiness-review
description: Score a service's launch readiness across reliability, security, observability, and operability into a go / no-go / conditional-go verdict with owned remediation items.
---

# production-readiness-review

> A go/no-go launch gate. It does not re-derive the underlying analyses — it
> *composes* the existing reliability, security, observability, and operability
> skills into one scored readiness verdict with tracked remediation.

## When to use

- A service or major feature is approaching its first production launch (or a big traffic step-up).
- A team wants a repeatable launch gate instead of an ad-hoc "looks fine to me".
- A workflow needs a single readiness verdict before promoting to prod.

## Inputs

- The service / change under review and its intended launch scope.
- Links to existing artifacts if present: SLOs, threat model, dashboards, runbook.

## Procedure

Score each dimension Red / Amber / Green with one line of evidence. Pull the
substance from the owning skill rather than re-deriving it:

1. **Reliability** — are SLOs defined for the critical journeys, with an error
   budget and a rollback path? Use `polymath-sre:slo-design` and
   `polymath-sre:error-budget-policy`. Amber if SLOs exist but no rollback.
2. **Security** — has the change been threat-modelled / reviewed, with owned
   mitigations? Use `polymath-security:stride-threat-model` or
   `polymath-security:owasp-review`. Red if an external trust boundary is unmodelled.
3. **Observability** — do the RED/USE signals and alerts exist to detect the SLO
   burning? Use `polymath-observability:metrics-design` and `:logging-strategy`.
   Amber if metrics exist but no alert routes to an owner.
4. **Operability** — is there a runbook, an on-call owner, and a tested rollback?
   Use `polymath-writing:runbook`. Red if no named owner.

Then:
5. **Verdict** — **Go** only if every dimension is Green; **Conditional-go** if any
   Amber, listing the conditions; **No-go** if any Red. The verdict follows the
   rule mechanically — do not average away a Red.
6. **Remediation** — every Amber/Red becomes a tracked item with an owner and a
   due-before date. Write `docs/readiness/<slug>-prr.md`.

## Output

- File: `docs/readiness/<slug>-prr.md` — the four scored dimensions with
  evidence, the verdict, and the remediation table (item, owner, due-before).
- One-line summary: the verdict and the count of blocking (Red) items.

## Quality bar

- Each dimension cites evidence (an SLO, a threat ID, a dashboard, a runbook), not a vibe.
- The verdict is mechanical: one Red ⇒ No-go; the gate is not negotiable by averaging.
- Every Amber/Red has an owner and a date — no unowned remediation.
- Composes the dimension skills; does not re-author SLOs, threat models, or runbooks inline.
