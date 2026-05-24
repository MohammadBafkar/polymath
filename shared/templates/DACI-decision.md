---
artifact: DACIDecision
schemaVersion: 0.1
title: "{{title}}"
status: open
driver: "{{driver}}"
approver: "{{approver}}"
contributors: []
informed: []
created: "{{date}}"
due: "{{due_date}}"
---

# DACI: {{title}}

## Driver

One person. Owns the decision process, runs the meetings, drafts the doc.
The Driver is **not** the approver.

- `{{driver}}`

## Approver

One person (or one role). The decision is theirs to make. If you can't name
a single approver, you don't have a decision-ready situation — escalate the
framing first.

- `{{approver}}`

## Contributors

People whose input is required before the decision. They don't approve;
they ensure the decision isn't made in ignorance.

- …

## Informed

People who need to know the outcome. Not consulted before the decision.

- …

## Context

What problem are we deciding about? Quote the constraint that forced this
decision now.

## Options

Two or more, each with a one-line summary.

- **Option A** — …
- **Option B** — …
- **Option C** — …

## Recommendation

The Driver's recommendation, in one paragraph, including the trade-off you'd
accept.

## Decision

To be filled by the Approver. One of: A / B / C / "defer with reason".

## Rationale

Approver's one-paragraph rationale. This is what future readers need.

## Implementation owner

Who executes after the decision. May or may not be the Driver.

## References

- PRD / ADR / RFC links.
- Related earlier decisions.
