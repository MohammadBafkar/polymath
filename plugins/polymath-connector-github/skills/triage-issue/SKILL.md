---
name: triage-issue
description: Triage an inbound GitHub issue — label, severity, area, ask for missing repro details if needed, route to the right team.
---

# triage-issue

> Triage one GitHub issue via the github MCP server. Output is structured triage actions, not opinions.

## When to use

- An inbound issue lands and someone needs to decide what to do with it.
- A workflow has a "triage backlog" step.

## Procedure

1. **Fetch** the issue (`get_issue`) and its comments.
2. **Classify**:
   - **Bug** — observed behavior differs from documented or implied. Severity by impact (sev1–4 mirror).
   - **Feature request** — net-new capability. Defer to product if not aligned with roadmap.
   - **Question / support** — route to the support / docs channel; close as "answered" with the answer linked.
   - **Duplicate** — close with a link to the original.
   - **Won't fix** — close with a one-line reason.
3. **Area label** — by code area (`area/api`, `area/ui`, `area/payments`). Use CODEOWNERS if available to derive the right label.
4. **Severity label** — `sev1` / `sev2` / `sev3` / `sev4` matching incident-triage vocabulary.
5. **Missing repro?** — if a bug lacks: version, OS, steps to reproduce, expected vs actual, add a comment requesting them and add a `needs/repro` label. Use a polite template; don't berate.
6. **Assign** — to a team (via team handle), not a person, unless the team has an explicit rotation owner.

## Output

Each finding produces a github MCP action:

```text
Triage: <issue url>

Classification: Bug, sev3, area/payments.
Reproduction: complete (version + steps + expected/actual).

Actions:
  - add_issue_labels: ["bug", "sev3", "area/payments"]
  - update_issue: assignees=[team-payments]
  - add_comment: thank-you-and-acknowledged template

Routing: payments team via team-payments handle.
```

## Anti-patterns to avoid

- "Won't fix" without a reason.
- Assigning to a person who is no longer on the team.
- Closing as "duplicate" without linking the original.
- Asking for repro when the repro is already in the body — read first.
