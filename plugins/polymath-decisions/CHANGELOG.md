# Changelog — polymath-decisions

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Added

- `tradeoff-matrix`: `scripts/weigh.py` — per-cell `w × s = v` math, totals, ranking, non-differentiating criteria, and the full ±1 sensitivity sweep over every weight and score (guessed scores flagged); unit-tested. The template example reproduces exactly.

### Changed

- Every skill declares its **Mode** — 4 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `cynefin-frame`: Inputs; classification without evidence is reported as Confusion.
- Canonical slug rule (`daci`, `evidence-ledger`, `tradeoff-matrix`).

## [0.11.0]

### Fixed

- `evidence-ledger`: description was 202 chars (SKILL-1 failure); unsourced claims can't be Facts.
- `daci`: no nonexistent "script"; never invents Driver/Approver names.
- `tradeoff-matrix`: sensitivity check (does a ±1 change flip the winner).

## [0.8.0]

Decision craft: DACI roles, weighted tradeoff matrix, Cynefin domain framing.

### Skills

- **cynefin-frame** — Classify a decision context — Clear / Complicated / Complex / Chaotic — and pick the response that fits the domain instead of forcing one shape on all problems.
- **daci** — Run a DACI decision (Driver, Approver, Contributors, Informed) for a non-trivial decision; assigns one Approver, names the deadline.
- **evidence-ledger** — Frame a decision's evidence — separate facts, assumptions, and unknowns; per unknown name confidence and what would resolve it; not a full decision record (daci) or tradeoff scoring (tradeoff-matrix).
- **tradeoff-matrix** — Score options against weighted criteria; surfaces where the numeric ranking disagrees with the gut call and names the tie-breaker.
