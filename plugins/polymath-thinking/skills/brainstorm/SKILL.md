---
name: brainstorm
description: Generate divergent options (≥10) for a problem before converging — quantity beats quality; not convergent down-selection or ranking (prioritize).
---

# brainstorm

> Divergent-converge brainstorm. Output is a list of genuinely distinct ideas, then a short convergence note against stated criteria.

**Mode:** generative — diverge before converging. Produce genuinely different options first (the obvious answer is one candidate, not the answer), then narrow with stated criteria.

## When to use

- The user says "brainstorm", "what are our options?", "give me some ideas".
- A workflow needs an exploration step before committing to one direction (`polymath-thinking:deliberate` calls this for its Diverge phase).

## Inputs

- The problem statement (required, one paragraph max). A solution-shaped request ("we need a cache") is reframed as the problem it solves before diverging.
- Constraints (optional): time, budget, tech stack. Treat them as soft unless stated as hard — one lens deliberately breaks them.
- Convergence criteria (optional, default: impact, cost to try, reversibility). Fix them **before** diverging so the ideas aren't judged by criteria invented to favor one.

## Procedure

1. **Diverge — at least 10 ideas, one per lens, then more from whichever lens is richest.** Each lens forces a different *mechanism*:
   - **Default** — the industry-standard approach.
   - **Cheap** — a lower-cost, lower-quality alternative.
   - **Big bet** — higher investment, higher payoff.
   - **Do nothing** — accept the cost; always include it.
   - **Inversion** — what would make the problem worse? Invert it.
   - **Remove a step** — delete a stage, approval, or component instead of improving it.
   - **Break a constraint** — what if the soft constraint didn't hold (no budget cap, no legacy API)?
   - **Borrow** — how another domain solves the same shape (logistics, games, biology, finance).
   - **Extreme user** — design for the heaviest or the most novice user; what falls out?
   - **Push it to the user / machine** — self-serve, automate, or make the system do it.
2. **Distinctness check.** Two ideas are the same idea if they share the mechanism — a different parameter, vendor, or config of one mechanism counts once. Merge duplicates and refill from another lens until ≥ 10 remain.
3. Keep each idea to one line naming its mechanism. **No evaluation during divergence.**
4. Tag the 2–3 least obvious ideas `★ non-obvious` — the ones a reader would not have listed in a minute.
5. **Converge** against the criteria fixed in Inputs: pick the top 2, give the criterion that decided each, and one risk per pick. A `★` idea that loses still gets one line on what would make it win.

## Output

```text
Brainstorm: cut new-hire time-to-first-PR from 10 days to 3

Criteria (fixed before diverging): impact on days saved, cost to try, reversibility

Ideas:
  1. [default]      Onboarding checklist + buddy for week 1
  2. [cheap]        Record the senior walkthrough once; new hires watch it day 1
  3. [big bet]      Ephemeral dev environments: one command, working stack in 10 min
  4. [do nothing]   Accept 10 days; revisit when hiring > 5/month
  5. [inversion]    Worst case = blocked on access → pre-provision every account before day 1
  6. [remove step]  ★ Delete the local setup entirely: first PR is made in a cloud IDE
  7. [constraint]   Let new hires merge to a sandbox service with no review gate in week 1
  8. [borrow]       ★ Restaurant "stage" model — first task is a scripted, real, tiny fix
  9. [extreme user] Design for the bootcamp grad → every README step is copy-pasteable
 10. [automate]     A bot opens a starter issue tailored to the hire's team on day 0

Top 2:
  - #5 pre-provisioned access — wins on impact (blocks are 4 of the 10 days) at near-zero cost. Risk: security review of pre-created accounts.
  - #3 ephemeral environments — wins on impact; reversible as a pilot on one team. Risk: 2–3 weeks of platform work.
  ★ #6 would win if the codebase already built in a cloud IDE — check before ruling it out.
```

## Quality bar

- ≥ 10 ideas after the distinctness merge; each names a different mechanism.
- Every lens was tried; "do nothing" is always present.
- At least two ideas are tagged `★ non-obvious`, and they are genuinely surprising, not the default reworded.
- Convergence uses the criteria fixed before diverging, and names which criterion decided each pick.

## Anti-patterns to avoid

- Stopping at 3 ideas, or padding to 10 with variants of one mechanism ("X with config A", "X with config B").
- Converging mid-divergence ("that won't work because…" during step 1).
- Picking the default as a top pick without saying why the non-obvious ones lost.
- Inventing convergence criteria after seeing the ideas.
