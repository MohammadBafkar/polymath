---
name: safe-rollout
description: Design a safe progressive rollout — flags, canary/blue-green, ring stages, SLO health gates, automated rollback, kill switch. Rollout mechanics, not env promotion or A/B experiments.
---

# safe-rollout

> Ship change to users gradually, watch the signals that matter, and make rollback the default reflex — not a heroic incident response.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A change is risky enough that an all-at-once deploy is unwise: large blast radius, new infra, irreversible data path.
- The user asks how to roll out behind a flag, do a canary, or stage a percentage rollout safely.
- A workflow invokes `polymath-release:safe-rollout`.

This designs *rollout mechanics*. It is not promoting a build across environments (`polymath-devops:env-promotion`), running an A/B experiment to learn (`polymath-data:run-experiment` / the `experimentToGA` workflow), or defining the SLO itself (`polymath-sre:slo-design` — consume it here).

## Inputs

- The change and its blast radius (who/what breaks if it's wrong).
- Reversibility: is it flag-toggleable, or does it touch data/schema?
- The SLIs/SLOs that define "healthy" for the affected journey. Absent: run `polymath-sre:slo-design` first, or propose gate thresholds marked `[VERIFY: SLO]` — never a gate without a number.
- Designing the rollout never executes it: flag flips, traffic shifts, and deploys are shown as commands for the operator and run only on their explicit go-ahead.

## Procedure

1. **Choose the technique** by reversibility and infra:
   - *Feature flag* — app-level, instant off; the default for code-path changes.
   - *Canary / ring* — route a small % (or internal ring) to the new version; widen on health.
   - *Blue-green* — full standby environment; instant cutover + cutback. Use for infra/runtime swaps.
2. **Stage the ramp** — e.g. internal → 1% → 5% → 25% → 100%, with a bake time per stage.
3. **Define health gates** — the SLIs and thresholds that must hold to advance; tie to `polymath-sre:slo-design`. Breach = halt + auto-rollback, not a page-and-wait.
4. **Automate rollback** — flag-off / route-back / redeploy-previous; state the trigger and the expected time-to-safe.
5. **Kill switch** — a single, tested control that disables the change instantly, independent of the deploy pipeline.
6. **Data/irreversibility** — for schema/data changes, pair with expand/contract migration; a flag cannot roll back a destructive write.
7. **Slug** from the change name: a workflow's `${workflow.slug}` wins; otherwise lowercase it, replace each run of characters outside `a-z0-9` with `-`, trim `-` at the ends, and cut to ≤ 60 characters at a `-`. An existing file at the target path is updated in place (show the diff), never duplicated.
8. Write `docs/rollouts/<slug>.md`.

## Output

`docs/rollouts/<slug>.md`, in this shape:

```text
Rollout: checkout-v2        technique: canary (new service) + feature flag `checkout_v2`

Stages (advance only when every gate holds for the full bake):
  internal (staff)  bake 24h
  1%                bake 2h
  5%                bake 4h
  25%               bake 24h (covers a daily peak)
  100%

Health gates (vs. the control cohort, from slo-design):
  checkout success rate ≥ 99.5%  ·  p95 latency ≤ 800 ms  ·  payment-provider 5xx ≤ 0.2%
Rollback (automatic): any gate breached for 5 consecutive minutes → route 100% back to v1; time-to-safe ≤ 2 min
Kill switch: flag `checkout_v2` off — independent of the deploy pipeline; tested in staging on 2026-10-20
Irreversible: order-table write path is expand/contract — v2 writes both columns until the contract phase
Operator commands (run on explicit go-ahead only): <flag / traffic-shift commands per stage>
```

## Quality bar

- Every stage has an explicit advance criterion (a metric + threshold), not "looks fine".
- Rollback is automated and its trigger is a measured signal, not human judgment alone.
- A kill switch exists and is independent of a full redeploy.
- Irreversible (data) changes are called out and not hidden behind a flag that can't actually undo them.

## Anti-patterns

- "Canary" that is one box for five minutes with no health gate (theater).
- Flag with no kill switch or no removal plan (flags become permanent tech debt).
- Rollback that requires a manual redeploy under incident pressure.
