# Changelog — polymath-leadership

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 6 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `coaching-plan`, `conflict-mediation`, `hiring-loop`: exact output shapes.
- `conflict-mediation`: confidentiality rule; at least three options, one neither party proposed.
- `hiring-loop`: candidate feedback and debrief notes stay in the ATS, never the repo.

## [0.11.0]

### Changed

- `perf-review`, `one-on-one-prep`, `coaching-plan`: personnel notes go to a private, non-versioned (git-ignored) location, never committed; only user-provided evidence.
- `hiring-loop`: no protected-characteristic questions.

## [0.8.0]

Leadership craft: 1:1 prep, performance reviews, OKR setting, hiring-loop design, conflict mediation, coaching/growth plans.

### Skills

- **coaching-plan** — Build a coaching/growth plan for a report — assess current vs next-level expectations, pick 1–2 growth areas, concrete practice + sponsorship, and a check-in cadence.
- **conflict-mediation** — Frame a team conflict — separate positions from interests, structure a difficult conversation, find the shared goal, land concrete commitments; not a perf-review.
- **hiring-loop** — Design a hiring loop — role scorecard, structured interview stages mapped to signals, interviewer calibration, evidence-based debrief, and a bias-resistant decision.
- **okr-setting** — Set OKRs — one ambitious Objective, 3–5 measurable Key Results with baselines + targets + confidence, named Anti-OKRs, weekly confidence cadence.
- **one-on-one-prep** — Draft a 1:1 agenda — direct-report items first, manager items second, a rotating pulse question, carryover commitments; never cancel for "no agenda".
- **perf-review** — Write a perf review — evidence-anchored, calibrated against level expectations, no surprises; areas-for-growth section already heard from 1:1s.
