---
name: work-breakdown
description: Decompose a goal or plan into independently completable steps; each step produces an observable artifact. Engineering task WBS; not story slicing (decompose-epic) or the plan doc (write-plan).
---

# work-breakdown

> Turn "build X" into a numbered list of steps that can be checked off one at a time.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A plan exists but the steps are vague.
- A workflow needs the decomposed task list before estimating.

## Inputs

- The goal, plan, or PRD to decompose (required). None given: ask for it; never decompose an invented goal.
- Assumed assignee or team (optional) — sets the "~1 day per step" yardstick. Absent: assume one engineer familiar with the codebase and say so.

## Procedure

1. State the end state in one sentence.
2. Walk back from the end state to "today" in independent steps. Each step:
   - Has a verb in front ("Write the migration", "Roll the canary", "Update the runbook").
   - Produces something observable from the outside.
   - Could in principle be assigned to a different contributor.
3. Avoid horizontal slices ("set up the database", then "set up the API", then "set up the UI"). Prefer vertical slices that produce a user-visible behavior.
4. Number steps in dependency order and record each step's prerequisites; the critical path is the longest prerequisite chain to the end state.

## Output

```text
Work breakdown: <goal>

End state: <one sentence>

Steps:
  1. <verb>… → produces <observable>
  2. <verb>… → produces <observable>
  …

Total: <n> steps. Critical path: 1 → 4 → 6.
```

## Quality bar

- No step that is just "investigate" or "discuss". Investigation produces a document — name the document.
- No step longer than ~1 day for the assumed assignee. Decompose further if it is.
- Critical path is named so reviewers know which steps must finish in order.
