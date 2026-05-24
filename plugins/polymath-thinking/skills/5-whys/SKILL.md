---
name: 5-whys
description: Root-cause an incident or bug via the 5-whys technique; stop early if a system cause emerges before five iterations.
---

# 5-whys

> Iteratively ask "why?" to walk back from a symptom to a root cause. Five is a heuristic, not a quota.

## When to use

- An incident or recurring bug needs root-cause analysis.
- A workflow's postmortem step needs structured root cause.
- The user says "why did this happen?" twice in the same conversation.

## Inputs

- The observed symptom (one sentence).
- Anything we already know about the timeline / runtime.

## Procedure

1. State the symptom.
2. Ask "why?" — answer with a verified cause (cite evidence: log line, metric, code path).
3. Repeat against the previous answer. Stop when:
   - The cause is a **system property** (process, structure, incentive) — not another proximate event.
   - Continuing would speculate beyond evidence.
4. Translate the deepest verified cause into one actionable change.

## Output

```text
5-whys: <symptom>

Why 1: <symptom> happened because …  (evidence: …)
Why 2: that happened because …       (evidence: …)
Why 3: that happened because …       (evidence: …)
[Why 4, Why 5 if needed]

Root cause (system level): …
Proposed change: …
```

## Quality bar

- Each "why" cites concrete evidence; "we think" is not evidence.
- The final cause names a process, structure, or incentive — not "Alice forgot".
- The proposed change addresses the root, not a proximate symptom.
