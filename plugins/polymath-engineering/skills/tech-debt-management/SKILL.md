---
name: tech-debt-management
description: Inventory and prioritize technical debt — classify (deliberate/accidental), quantify principal vs interest, and sequence paydown against feature work with a payback rationale.
---

# tech-debt-management

> "Tech debt" with no interest rate is just a complaint. Quantify what each item *costs you per sprint* and pay down the high-interest debt that sits under active work — ignore the rest.

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
5. **Sequence**: rank by interest ÷ principal, gated by proximity to upcoming work; bundle paydown into the features that traverse that code rather than as a separate "refactor sprint" where possible.
6. **Set a sustainable budget**: a standing fraction of capacity (e.g. ~15–20%) for debt, with the high-interest items named — not an unbounded stop-the-world.
7. **Make it visible + prevent regression**: track the inventory, define "definition of done" guards (tests, lint, review) so new reckless debt is caught at the boundary.

## Output

- A prioritized debt register: each item with classification, quantified interest + principal, proximity to roadmap, and an interest÷principal rank; plus a recommended paydown budget and the top items to bundle into upcoming work.

## Quality bar

- Each item has evidence (churn/bugs/lead-time), not just opinion.
- Interest and principal are quantified; ranking is interest÷principal, weighted by roadmap proximity.
- Debt in stable, untouched code is explicitly deprioritized.
- A sustainable standing budget is recommended, not a one-time refactor freeze.
