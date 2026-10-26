# Changelog — polymath-decisions

<!-- markdownlint-disable MD024 -->

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
