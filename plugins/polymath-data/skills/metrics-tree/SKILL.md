---
name: metrics-tree
description: Decompose a North Star metric into a tree of input metrics so each team can see the lever they own; output is a tree, not a dashboard.
---

# metrics-tree

> Decompose a North Star into the input metrics that move it. Each leaf is a lever a team owns.

## When to use

- A team is asked "how does your work move the North Star?".
- An OKR planning session needs the metric tree before goals.
- The user says "what metrics should we track?".

## Inputs

- The North Star metric (the single number the org cares about).
- The product surface and the teams that work on it.

## Procedure

1. **Restate the North Star**. One sentence: what it measures, what unit, what aggregation, what time grain. "Weekly Active Buyers" is more useful than "engagement".
2. **Decompose multiplicatively** first. North Star = Reach × Conversion × Retention (for example). Each multiplicand is a top-level branch.
3. **Decompose each branch** until you reach a number a team can directly move with a quarter's work. That's a leaf.
4. **Each leaf has**:
   - A name.
   - A definition (SQL-able).
   - A current baseline value.
   - An owning team.
   - A direction (↑ or ↓ is good).
5. **Sanity check**: if any leaf can't be moved without crossing into another team's surface, the tree is wrong — re-decompose.

## Output

```text
North Star: Weekly Active Buyers
  Definition: distinct users with ≥1 paid purchase in the trailing 7 days.

Decomposition (multiplicative):
  WAB = Reach × Activation × Repeat

  Reach
    └ Sessions / week
        └ Marketing-driven sessions (owner: Growth)
        └ Organic sessions (owner: SEO)
        └ Returning-user sessions (owner: Engagement)

  Activation
    └ Sessions → first purchase rate
        └ PDP load → add-to-cart rate (owner: Catalog)
        └ Add-to-cart → checkout completion rate (owner: Checkout)

  Repeat
    └ Buyers (W) → buyers (W+1) retention
        └ Post-purchase email open rate (owner: Lifecycle)
        └ Reorder-flow completion rate (owner: Lifecycle)

Each leaf:
  Sessions / week (organic):
    SQL: count distinct user_id where source='organic' and ts >= now() - 7d
    Baseline: 320k
    Direction: ↑
```

## Anti-patterns to avoid

- Decomposing additively when the relationship is multiplicative ("WAB = ad clicks + organic + referral" double-counts).
- Leaves that two teams would have to coordinate to move.
- Vanity metrics ("page views") that don't connect upward.
