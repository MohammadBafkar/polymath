---
name: one-on-one-prep
description: Draft a 1:1 agenda — direct-report items first, manager items second, a rotating pulse question, carryover commitments; never cancel for "no agenda".
---

# one-on-one-prep

> The 1:1 is the direct report's meeting. The manager prepares. Output is a doc that's good enough to walk into the room with — and good enough to skim afterward.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Before a scheduled 1:1.
- A new direct report joins and the cadence is being set.
- A 1:1 has drifted into status-update mode and you want to reset it.

## Inputs

- Direct report's name.
- Date of the 1:1.
- Carryover from the last 1:1 (if any).

## Procedure

**Confidential.** 1:1 notes are personnel data. Default to a private, non-versioned location — outside the repo, or a repo path that `git check-ignore` confirms is ignored (add the ignore entry first if needed) — or the company's HR system; never commit or push them. Confirm the path with the user before writing. Use only evidence the user provided; never invent incidents, quotes, or feedback.

1. Read [`1-on-1.md`](../../templates/1-on-1.md).
2. Write `<private-dir>/people/<direct-report>/1on1-<date>.md` (default `<private-dir>`: `~/.polymath/private`):
   - **Direct report's agenda** — left blank for them to fill. If they consistently leave it blank, that's a topic, not a reason to cancel.
   - **Manager's agenda** — career, feedback (both directions), strategic context, blockers you can unblock. Pick 1–2; don't dump 5.
   - **Pulse check** — pick ONE rotating question.
   - **Carryover** — last meeting's commitments. Closed loop or not?
   - **Commitments** — what each of you owes the other by next 1:1.
3. Stop. The notes get filled during/after the meeting; don't pre-write them.

## Quality bar

- Direct report's agenda comes first in the doc.
- Manager has 1–2 prepared topics, not 5.
- One pulse question, rotated weekly.
- Carryover is honestly evaluated; "in progress" is not closed.

## Output

- File: `<private-dir>/people/<direct-report>/1on1-<date>.md` — never committed. Shape: the [`1-on-1.md`](../../templates/1-on-1.md) template.
- Summary listing the pulse question + manager's 1–2 prepared topics.

## Anti-patterns to avoid

- Cancel "because no agenda". There's always Pulse.
- Manager dominates with status. The 1:1 is theirs.
- Feedback delivered for the first time at perf-review. 1:1s are where that lands.
- Skipping carryover. The previous meeting becomes invisible if you do.
