---
name: hiring-loop
description: Design a hiring loop — role scorecard, structured interview stages mapped to signals, interviewer calibration, evidence-based debrief, and a bias-resistant decision.
---

# hiring-loop

> Unstructured interviews mostly measure similarity to the interviewer. A structured loop — defined signals, consistent questions, evidence before opinion — is the single biggest predictive and fairness upgrade.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Designing or fixing an interview process for a role, or running a debrief/decision.
- Loops feel ad hoc, interviewers overlap, or decisions hinge on "culture fit" vibes.
- A workflow invokes `polymath-leadership:hiring-loop`.

Not this when: you are evaluating an existing report (`polymath-leadership:perf-review`) or developing one (`coaching-plan`). This is candidate hiring.

## Inputs

- The role, its level, and the must-have vs nice-to-have competencies.
- The current loop and known failure modes (false positives/negatives, drop-off).

## Procedure

1. **Write a scorecard first**: the 4–6 competencies this role must demonstrate (technical depth, design, collaboration, etc.), each with what "meets the bar" looks like at this level. Hire against the scorecard, not a gut composite.
2. **Map each competency to a stage**: every interview owns specific signals so the loop *covers* the scorecard with minimal overlap. No two interviewers should unknowingly test the same thing while a competency goes unmeasured.
3. **Standardize within a stage**: the same core questions/rubric per candidate for a role, so candidates are comparable and the signal isn't interviewer-dependent. Use work-sample/behavioral (past behavior) over hypotheticals.
4. **Calibrate interviewers**: shared rubric, example answers at each level, shadow/reverse-shadow before going solo. Recalibrate when a hire surprises.
5. **Evidence before opinion**: interviewers submit written, evidence-based feedback and a recommendation *before* the debrief — to prevent groupthink and anchoring on the loudest voice.
6. **Structured debrief**: review against the scorecard competency by competency; a "no" with evidence outweighs a vague "yes". Decide hire/no-hire (+ level) with a named decision-owner.
7. **Guard against bias**: consistent process, diverse panel where possible, focus on job-relevant signal, watch for affinity/halo. Track funnel + outcome metrics to catch systematic bias. Never ask about protected characteristics (age, family plans, religion, health, nationality…) — check questions with HR/legal for each hiring jurisdiction.
8. **Candidate experience**: timely, respectful, clear — a rejected candidate is a future customer/applicant.
9. **Candidate data stays in the ATS.** Interview feedback and debrief notes are personal data: never write them into the repo or a shared doc. This skill designs the loop; it does not store evaluations.

## Output

`docs/hiring/<role-slug>-loop.md` (the loop design only — no candidate data), in this shape:

```text
Hiring loop: Senior Backend Engineer (L5)

Scorecard (meets-the-bar at L5)
  C1 system design         designs a service with explicit failure modes and data ownership
  C2 coding                production-quality code with tests in a realistic task
  C3 operational judgment  debugs from evidence; knows when to roll back
  C4 collaboration         disagrees with evidence; unblocks others
  C5 ownership             drives ambiguous work to done without a script

Stage → competency (no overlap, full coverage)
  screen (45m)            C5 (past-behavior: "the last ambiguous project you drove")
  coding (75m)            C2 — work sample: add rate limiting to a small service, rubric v3
  design (60m)            C1 — same prompt for every candidate: "refund service, multi-region"
  incident (45m)          C3 — replay of a sanitized real incident
  collaboration (45m)     C4 — past-behavior questions, rubric v2
Calibration: every interviewer shadows 2 + reverse-shadows 1 before solo; recalibrate quarterly
Feedback rule: written evidence + recommendation in the ATS before the debrief opens
Debrief: competency by competency vs the scorecard; decision owner: hiring manager
Bias guards: same questions per stage; protected-topic list reviewed by HR; funnel by stage tracked monthly
```

## Quality bar

- A scorecard exists and the loop covers every competency with minimal overlap.
- Questions/rubrics are standardized within a stage; past-behavior over hypothetical.
- Written evidence is submitted before the debrief; the decision is scorecard-anchored with an owner.
- Bias guards and funnel metrics are in place.
