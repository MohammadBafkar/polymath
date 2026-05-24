---
name: inspect-deployment
description: Inspect a Vercel deployment — build status, runtime logs, edge-function exit codes, traffic split, and a rollback recommendation.
---

# inspect-deployment

> Given a Vercel deployment URL or ID, classify it as healthy / degraded / broken and produce a rollback recommendation grounded in build + runtime + edge-function evidence.

## When to use

- A production deployment looks slow or broken and the on-call wants a fast read.
- A preview deployment needs verification before promote.
- A pre-rollback sanity check on which deployment was healthy before the bad one.

## Inputs

- Deployment ID or URL (required) — `dpl_…` ID, or a `*.vercel.app` URL the plugin resolves.
- Project (optional) — fall back to the project parsed from the deployment.

## Procedure

1. **Resolve the deployment** via the vercel MCP (`deployments.get`). Capture: `state` (BUILDING/READY/ERROR/CANCELED), `creator`, `target` (production/preview), `gitSource` (commit sha + branch).
2. **Build evidence.** If `state = ERROR`, fetch `deployments.logs.builds` and surface the first failing build step + its tail. If `state = READY`, sample the build log for warnings (Next.js `bigger-than-2MB`, missing env vars, deprecation notices).
3. **Runtime evidence.** Fetch `deployments.logs.runtime` for the last 15 minutes. Bucket by:
   - 5xx ratio (target < 0.2%).
   - p95 / p99 latency by route.
   - Edge function `exit_code != 0` count.
   - Cold-start ratio (proxy for size regression).
4. **Traffic split.** `deployments.aliases.list` — what domains/paths point at this deployment. A green deployment with no traffic is suspicious for prod; a red one with 100% traffic is urgent.
5. **Classify.**
   - **healthy** — `state=READY`, 5xx < 0.2%, p99 within baseline, no edge errors.
   - **degraded** — `READY` but at least one metric exceeds threshold; rollback advisable.
   - **broken** — `ERROR`/`CANCELED`, or `READY` with > 2% 5xx — rollback required.
6. **Rollback recommendation.** Identify the previous `READY` deployment with `target = production` and reference its ID + commit sha. The actual rollback is `deployments.promote` (out of scope for the skill; surface as a proposed action).

## Output

```text
inspect-deployment

Deployment:    dpl_abcDEF (production)
Commit:        a1b2c3d on main, "feat(refund): switch to async writes"
State:         READY
Traffic:       100% via refund.example.com (promoted 2026-05-23 14:02)

Runtime (last 15 min)
  Requests:    142,901
  5xx ratio:   3.4%       ⚠ above 0.2% threshold
  p99 latency: 1,420ms    ⚠ baseline 320ms
  Edge errors: 412 (refund-fn exit_code=1)

Classification: BROKEN
  Reason: 5xx ratio + edge-function exit_code != 0 indicate runtime regression.

Rollback target:
  Previous READY production deployment: dpl_xyz789 (commit f3e2d1a, 2026-05-22 11:08).
  Proposed action (operator):
    vercel.deployments.promote(dpl_xyz789)
```

## Quality bar

- State + build + runtime + edge all considered before classification.
- Rollback target is the previous READY *production* deployment, not just the previous deployment.
- Mutating action (`promote`) is surfaced for operator approval, not executed.
- Latency / error baselines named, not implied.

## Anti-patterns to avoid

- Classifying `state=READY` as healthy without checking runtime metrics. Vercel marks the deploy `READY` when *build* succeeds; runtime regressions don't change the state.
- Rolling back to "the previous deployment" without filtering to production target. A previous *preview* is not a rollback target.
- Surfacing the build log only. Most prod regressions are runtime, not build-time.
- Auto-promoting. Promotion is a money-/customer-affecting action; require operator approval.
