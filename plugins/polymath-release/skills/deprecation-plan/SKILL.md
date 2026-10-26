---
name: deprecation-plan
description: Plan a deprecation — two dates (warn + remove), telemetry-gated removal, comms cadence, exception path, code/header markers. The lifecycle plan, not the customer notice (write-sunset-notice).
---

# deprecation-plan

> Deprecation is a contract with a timeline, not a surprise. Set two dates, prove usage actually dropped before you pull it, and give people a way out.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A capability (API, endpoint, flag, feature, config) is going away and you need the staged plan.
- The user asks how to deprecate/sunset/retire something on a schedule.
- A workflow invokes `polymath-release:deprecation-plan` (see also the `deprecationToRemoval` / `sunsetCapability` workflows).

This is the *plan*. It is not the customer-facing notice copy (`polymath-communication:write-sunset-notice`), the consumer upgrade steps (`polymath-release:migration-guide`), or removing dead code (engineering).

## Inputs

- What is being deprecated and why; the replacement (or "no replacement").
- Who depends on it (internal/external; known consumers) and current usage signal.
- Constraints: contracts/SLAs, support windows, regulatory.
- Missing dates or usage data are never invented: dates the owner hasn't set are proposed and marked `[VERIFY: date]`; an unmeasured usage baseline is `[TBD: baseline — measure before announcing]`.

## Procedure

1. **Two dates** — *warn* (deprecation announced, still works) and *remove* (gone). State the support window between them and the rationale.
2. **Telemetry gate** — define the usage metric and the threshold the metric must be under before removal proceeds; removal is gated on data, not just the calendar.
3. **Markers** — how the deprecation is signalled in-product: `Deprecation`/`Sunset` HTTP headers, log warnings, SDK deprecation annotations, changelog.
4. **Comms cadence** — announce at warn, reminders at intervals, final notice before remove; route to the affected audience.
5. **Exception path** — how a blocked consumer requests an extension, and who approves.
6. **Migration** — link the upgrade path (`polymath-release:migration-guide`); deprecation without a migration path is just breakage.
7. **Slug** from the capability name: a workflow's `${workflow.slug}` wins; otherwise lowercase it, replace each run of characters outside `a-z0-9` with `-`, trim `-` at the ends, and cut to ≤ 60 characters at a `-`. An existing file at the target path is updated in place (show the diff), never duplicated.
8. Write `docs/deprecations/<slug>-plan.md` (the customer notice from `write-sunset-notice` lives beside it at `docs/deprecations/<slug>.md`).

## Output

`docs/deprecations/<slug>-plan.md`, in this shape:

```text
Deprecation plan: GET /v1/search  →  replacement: GET /v2/search

Dates:      warn 2026-11-02 · remove 2027-02-01  (90-day window: matches the public API support policy)
Gate:       remove only when v1 calls < 0.5% of v2 calls for 14 consecutive days
            metric: http_requests_total{route="/v1/search"} — baseline [TBD: measure before announcing]
Markers:    Deprecation + Sunset headers on every v1 response; SDK @deprecated in 4.8; CHANGELOG Deprecated entry
Comms:      announce at warn → reminders at −60d, −30d, −7d → final notice at remove (owner: API PM)
Exception:  extension requests via the API support form; approver: [VERIFY: approver role]; max +60 days
Migration:  docs/migrations/v1-search-guide.md
If the gate fails on the remove date: removal slips; re-check weekly; escalate the top 3 callers by name.
```

## Quality bar

- Two explicit dates with a justified support window between them.
- Removal is gated on a usage threshold, not the date alone; the metric is named.
- An exception/extension path exists with an approver.
- A migration path is linked; "just stop using it" is not a migration path.
- What happens when the gate fails on the removal date is written down.

## Anti-patterns to avoid

- One date ("deprecated as of today") with no removal date — open-ended deprecations rot.
- Removing on the calendar while usage is still above the gate.
- An exception path with no approver or no maximum extension.
- Inventing a usage baseline instead of measuring it.
