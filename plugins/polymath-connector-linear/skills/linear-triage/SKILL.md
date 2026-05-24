---
name: linear-triage
description: Triage a Linear issue — classify type/priority/state, ask for missing repro, transition through the workflow state machine, route to the right team.
---

# linear-triage

> Triage one Linear issue via the linear MCP. Linear-specific: respects the team's workflow states (Backlog / Todo / In Progress / In Review / Done / Cancelled) and project-cycle awareness.

## When to use

- A Linear key (TEAM-123 with "Linear" in the prompt) or `linear.app/.../issue/TEAM-123` URL surfaces in the prompt.
- Periodic backlog triage.

## Procedure

1. **Fetch** the issue via `issue.get`. Pull description, labels, current state, current cycle, assignee.
2. **Classify**:
   - **Bug** — observed behavior differs. Severity per the team's labels.
   - **Feature** — net-new capability. Estimate via `polymath-planning:estimate`.
   - **Improvement** — measurable refinement of existing capability.
   - **Task** — operational; lower priority unless tied to a milestone.
   - **Duplicate** — relate-to the original; transition to `Cancelled`.
3. **Labels** — set the area / component / type labels using the team's existing vocabulary. Don't invent new ones without team sign-off.
4. **Missing repro** — for bugs lacking version + steps + expected/actual, add a polite comment via `comment.create` and a `needs-info` label.
5. **State transition** via `issue.update`. Linear workflow states are team-specific; resolve names via `workflowState.list` for the team before transitioning. The standard pattern:
   - New / Backlog → Todo (when triaged and ready to work).
   - Todo → In Progress (assignee starts).
   - In Progress → In Review (PR up).
   - In Review → Done (merged + verified).
   - Anywhere → Cancelled (with a reason in the description).
6. **Cycle** — Linear's sprint analog. Assign to the current cycle for high-priority items; backlog for lower priority. Don't bulk-move; cycles work best with team capacity in mind.
7. **Assignee** — a person, not a team. (Linear assigns to people, not groups; surface the team via labels.)

## Output

```text
linear-triage: ENG-7

Title:    Refund p99 latency above SLO
Type:     Bug | Priority: Urgent | Cycle: 2026-W22.
Repro:    complete.

Actions (linear MCP):
  - issue.update: labels=["type:bug","priority:urgent","component:refund-svc"]
  - issue.update: assigneeId=<user-id for @alice>
  - issue.update: stateId=<workflowState 'In Progress'>
  - issue.update: cycleId=<cycle 2026-W22>
  - comment.create: thank-you + linked SLO doc.

Routing: assigned @alice; component label drives payments-eng visibility.
```

## Quality bar

- State transition uses an actual workflowState ID, not the name (Linear's API needs IDs).
- Cycle assignment considers capacity, not just priority.
- Labels match existing vocabulary; new labels are flagged for team sign-off.
- Assignee is a person.

## Anti-patterns to avoid

- Transitioning to "In Progress" before an assignee is set.
- Mass-assigning a cycle full of items in one pass without capacity review.
- Inventing new labels per-triage. Drift sets in fast.
- Closing as duplicate without `issueRelation.create` linking the original.
