---
artifact: Plan
schemaVersion: 0.1
title: "{{title}}"
owner: "{{owner}}"
created: "{{date}}"
status: draft
---

# Plan: {{title}}

## What

What this plan accomplishes, in one paragraph.

## Why

The motivation. Link the PRD or ADR.

## Approach

The chosen approach, in 3–5 bullets. Each bullet is a phase, not a task.

## Locked decisions

Decisions already made — by a spike, an ADR, or the owner — that this plan
builds on. The plan must not relitigate them; reopening one is an explicit
act with the decision's owner, not a drive-by edit.

- Decision: … (source: ADR/spike/owner, link)

## Work breakdown

Numbered steps from start to "done". Each step is independently completable
and produces an observable result.

1. Step one
2. Step two
3. …

## Risks

Known unknowns and their proposed mitigations.

- Risk: … Mitigation: …
- Risk: … Mitigation: …

## Verification

How we know the plan worked. Specific signals or artifacts.

- …

## Deferral registry

Work consciously pushed past this plan, each with the condition that
reopens it — never a bare "later". (Different from Out of scope: deferred
work is wanted, pending its condition.)

- Deferred: … Revisit when: …

## Out of scope

What we are deliberately *not* doing in this plan.

- …

## References

- PRD: `{{prd_link}}`
- ADRs: …
