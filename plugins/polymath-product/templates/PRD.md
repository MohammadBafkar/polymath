---
artifact: PRD
schemaVersion: 0.1
title: "{{title}}"
status: draft
owner: "{{owner}}"
created: "{{date}}"
---

# {{title}}

## Problem

What user or business problem are we solving? Quote the user pain or business
constraint that motivated this work. Include who is affected and how often it occurs.

## Users / customers

Who experiences this problem? List primary and secondary user types. If you have
personas from `polymath-research`, link them here. If not, describe the user in
one paragraph: their role, their day, the moment of pain.

## Goals

What outcomes does this PRD commit to? Each goal is one sentence and should be
testable. Avoid implementation language.

- Goal 1
- Goal 2
- Goal 3

## Non-goals

What is explicitly out of scope? Listing what we are not doing now prevents scope
creep and helps reviewers calibrate expectations.

- Non-goal 1
- Non-goal 2

## Requirements

Functional requirements expressed as behaviors the system must support. Each
requirement is verifiable. Acceptance criteria (see below) refine these.

1. The system MUST …
2. The system MUST …
3. The system SHOULD …

## Acceptance criteria

Concrete, testable statements for the smallest shippable slice. Format: Given /
When / Then. These map directly to test cases.

- Given …, when …, then …
- Given …, when …, then …

## Metrics

How will we measure success? Pick at most three primary metrics. If you have a
North Star metric from `polymath-product`, reference it here.

- Adoption: …
- Quality: …
- Performance: …

## Risks and open questions

Known risks and the call-outs that must be resolved before implementation.
Include at least one open question if there is uncertainty about scope.

- Risk: … Mitigation: …
- Open question: …

## Out of scope (future work)

What is deferred? List the things we know will come later so reviewers and
stakeholders do not raise them as gaps.

- …

## Rollout plan

How will we ship this? Reference flag/canary plans from `polymath-release` if
applicable. For v0.1, a single paragraph is sufficient.

## References

Link related ADRs, RFCs, design docs, and prior conversations.
