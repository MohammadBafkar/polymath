---
name: conflict-mediation
description: Frame a team conflict — separate positions from interests, structure a difficult conversation, find the shared goal, land concrete commitments; not a perf-review.
---

# conflict-mediation

> People argue positions ("use Postgres") while holding interests ("I don't want to be paged at 3am"). Surface the interests and most technical conflicts dissolve into a solvable constraint problem.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Two people/teams are stuck in a disagreement, an escalation needs facilitating, or a difficult conversation needs preparing.
- Tension is blocking a decision or eroding trust.
- A workflow invokes `polymath-leadership:conflict-mediation`.

Not this when: it's a clean technical decision needing a framework — that is `polymath-decisions:daci` / `tradeoff-matrix`. This handles the *interpersonal* friction around or instead of the decision.

## Inputs

- The parties, the surface disagreement, and (if known) what each actually cares about.
- Your role (party, mediator, or manager) and the history.

## Procedure

**Confidential.** Notes about a conflict between named people are personnel data. Keep them out of the repo and out of shared channels — a private location the user confirms, or nowhere (return them inline). Use only what the user told you; never invent motives, quotes, or history.

1. **Separate people from the problem**: frame it as "us vs the problem", not "me vs you". Lower the temperature before content — emotion unaddressed blocks reasoning.
2. **Positions → interests**: for each side, get past the stated position ("we must do X") to the underlying interest ("because I need Y"). Ask "what makes that important to you?" Interests are where overlap lives; positions are where stalemate lives.
3. **Find the shared goal**: name the higher objective both want (ship reliably, serve the user). Most conflicts share a goal and differ on means.
4. **Prepare the difficult conversation** (if you're a party): state observable facts (not judgments), the impact, and your ask; assume positive intent; plan to listen, not just transmit.
5. **Generate options against interests**: list at least three options before judging any — each side's position restated against both interest-sets, plus at least one option neither party proposed. The third option often beats both originals. Use objective criteria (data, principles) to choose, not who's more senior or louder.
6. **Land concrete commitments**: who does what by when; make agreements specific and verifiable, not "we'll communicate better". Decide what happens if it recurs.
7. **Escalate well if stuck**: a clear, neutral framing for the decider — both interests, the options, the disagreement — not a one-sided appeal.
8. **Follow up**: check the commitments held; repair the relationship, not just the issue.

## Output

Returned inline (or to the confirmed private path), in this shape:

```text
Resolution plan: payments vs platform — who owns the retry library

Side        Position                          Interest
payments    "we keep our own retry code"      no surprise behavior change during peak season
platform    "everyone uses the shared lib"    one place to fix retry storms; less on-call load
Shared goal: no retry-induced incidents this quarter

Options (generated before judging)
  A. payments keeps its own code                  meets payments' interest only
  B. forced migration now                         meets platform's interest only
  C. migrate after the peak freeze, behind a flag, with payments owning the rollout   ← neither side proposed
Criteria: incident data (2 retry storms in shared-lib consumers vs 0 in payments) · peak-freeze calendar
Choice: C

Commitments
  - payments: migration PR behind flag `shared_retry` by 2027-01-15
  - platform: add payments' jitter config to the shared lib by 2026-12-20
  - if a retry incident recurs: escalate to the eng director with both interests stated
Follow-up: check-in 2027-01-20
```

## Quality bar

- Underlying interests (not just positions) are surfaced for each side.
- A shared higher goal is named; options are generated before judging.
- The conversation is framed in observable facts + impact, not character judgments.
- Outcome is concrete, verifiable commitments with a follow-up, not a vague truce.
