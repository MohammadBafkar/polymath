---
name: tech-debt-management
description: Triage technical debt — classify (deliberate/accidental), quantify principal vs interest, and sequence paydown against feature work with a payback rationale.
---

# tech-debt-management

> "Tech debt" with no interest rate is just a complaint. Quantify what each item *costs you per sprint* and pay down the high-interest debt that sits under active work — ignore the rest.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Velocity is dropping, change is risky, or a "we need to refactor everything" push needs discipline.
- Planning how much capacity to spend on debt vs features this cycle.
- A workflow invokes `polymath-engineering:tech-debt-management`.

Not this when: you are doing one safe refactor of known code — that is the `refactorWithSafety` workflow. For decomposing a monolith specifically, `polymath-architecture:service-decomposition`. This skill manages the debt *portfolio*.

## Inputs

- The codebase areas under pain, recent incident/bug hotspots, and where upcoming features will land.
- Team capacity and the current feature pressure.

## Procedure

1. **Inventory the debt** as discrete items, not vibes: each with a location, a symptom (slow change, bugs, on-call pain), and evidence (churn × bug rate, lead-time, incident links).
2. **Classify** (Fowler quadrant): *deliberate-prudent* ("ship now, fix Q3" — track it), *deliberate-reckless*, *inadvertent-prudent* ("now we know how we should've done it"), *inadvertent-reckless*. Classification sets urgency and prevents moralizing.
3. **Quantify interest vs principal**: *interest* = the recurring cost it imposes (extra hours per change, defect rate, on-call toil); *principal* = the cost to fix it. High-interest, low-principal items are the obvious wins.
4. **Locate against the roadmap**: debt under code you're about to change has high realized interest; debt in stable, untouched code has near-zero interest — leave it. This is the single biggest prioritization lever.
5. **Sequence** with one fixed formula so two runs rank the same: `rank score = interest (h/month) ÷ principal (h) × 2 if a roadmap item in the next quarter touches that code, else × 1`; sort descending, ties broken by higher interest, then by location. Items with no evidence for interest or principal are listed unranked as `[TBD: measure]`, never scored on a guess. Then bundle paydown into the features that traverse that code rather than as a separate "refactor sprint" where possible.
6. **Set a sustainable budget**: a standing fraction of capacity (e.g. ~15–20%) for debt, with the high-interest items named — not an unbounded stop-the-world.
7. **Make it visible + prevent regression**: track the inventory, define "definition of done" guards (tests, lint, review) so new reckless debt is caught at the boundary.

## Output

`docs/tech-debt/register.md` (updated in place), in this shape:

```text
Tech-debt register — payments (as of 2026-10-26)

#  Item                                      Quadrant              Interest   Principal  Roadmap  Score
1  retry logic copy-pasted in 4 clients      inadvertent-prudent   12 h/mo    16 h       ×2 (Q1 retry work)   1.50
2  no index on refunds.merchant_id           deliberate-prudent     6 h/mo     4 h       ×1                   1.50
3  hand-rolled CSV export (3 bugs in 90 d)    inadvertent-reckless   5 h/mo    40 h       ×2 (exports revamp)  0.25
—  legacy SOAP adapter                         deliberate-prudent    [TBD: measure] —     ×1  (stable, untouched — leave it)

Evidence: churn × bug rate from git log + tracker labels `bug`, 90-day window; on-call toil from the pager export.
Budget: 15% of capacity; bundle #1 into the Q1 retry work, #3 into the exports revamp; do #2 this sprint (4 h).
Guards: lint rule against new HTTP clients outside lib/http; review checklist item "retry via shared lib".
```

Ties (#1 and #2 at 1.50) break by higher interest — #1 first.

## Quality bar

- Each item has evidence (churn/bugs/lead-time), not just opinion.
- Interest and principal are quantified; ranking is interest÷principal, weighted by roadmap proximity.
- Debt in stable, untouched code is explicitly deprioritized.
- A sustainable standing budget is recommended, not a one-time refactor freeze.
