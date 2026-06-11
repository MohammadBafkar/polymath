---
name: intake
description: Classify an ambiguous or multi-step request before work starts — score 4 confidence dimensions, ask only what the repo can't answer, stop at plateau, record the route via pipeline mark.
---

# intake

> The expensive failure is building the wrong thing confidently. Spend a few
> questions to pin intent, scope, constraints, and acceptance — then stop
> asking and route.

## When to use

- The pipeline directive (`routing.mode: classify|enforce`) points here for
  an ambiguous or multi-step request.
- A request names an outcome but not a surface, scope, or success test.
- The enforce gate denied a mutating tool call because nothing was
  classified yet.

Not for trivial or conversational turns — answering directly *is* the
classification there; record it with `mark --surface direct`. Not for
turning a fuzzy goal into a full plan (`fuzzyGoalToPlan` workflow does
that); intake decides *where the request goes*, in one screen.

## Procedure

1. **Score four confidence dimensions, 0–5 each**, from the request plus the
   project context (`polymath-core:project-context`):
   - **Intent** — what outcome the user wants and why now.
   - **Scope** — which surfaces/files/systems change, roughly how much.
   - **Constraints** — tech, process, or policy bounds any solution must
     respect (stack, conventions docs, compliance).
   - **Acceptance** — how success will be judged (tests, metric, artifact,
     reviewer).
2. **Apply the never-ask list before composing any question.** Never ask
   what the repo or config already answers:
   - stack, language, framework, test framework → project snapshot / repo
   - commit style, review conventions, doc locations → `conventions` /
     `.polymath/` conventions docs
   - tracker/CI/cloud providers → `.polymath/capabilities.yaml`
   - anything a 30-second read of the named file answers → read it
   - secrets or credentials — never ask, never echo
3. **Ask in batches of at most 3**, targeting the lowest-scoring dimensions
   first. Prefer concrete either/or questions over open ones.
4. **Re-score after each batch. Stop on plateau or confidence**: stop when a
   batch raises no dimension by ≥1 (plateau — more questions are not
   producing signal; proceed on stated assumptions and flag them), or when
   every dimension is ≥4. Never exceed 3 batches.
5. **Choose the route**, smallest surface that fits:
   - matching catalog/project workflow (multi-step arc) → propose it by
     name (propose-first contract; `polymath-core:route` can confirm)
   - single skill → name it
   - trivial after clarification → `direct`
   - Surfaces declared `trust: auto-headless` that are read-only may be run
     without propose-confirm when `routing.mode != hint`.
6. **Record the classification** so the gate opens (1h validity):
   `"${CLAUDE_PLUGIN_ROOT}/bin/polymath-pipeline" mark --surface <choice>`
   (the directive/deny message carries the absolute path).
7. **Output one screen**: the 4 scores with one-line justifications, open
   assumptions, the chosen route, and the mark confirmation.

## Quality bar

- No question that the never-ask list forbids.
- Stopped at plateau — question count is evidence of discipline, not rigor.
- Assumptions proceeding-on are written down, not implied.
- The route is the *smallest* fitting surface, and `mark` was actually run.
