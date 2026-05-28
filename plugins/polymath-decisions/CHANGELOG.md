# Changelog — polymath-decisions

## [0.1.0]

### Added

- `daci`, `tradeoff-matrix`, `cynefin-frame` skills.
- `DACI-decision.md` + `Tradeoff-matrix.md` templates under `templates/`.
- Frontmatter on both templates is validated by
  [`DACIDecision.schema.json`](../../shared/schemas/artifacts/DACIDecision.schema.json)
  (exactly one Approver, Approver ≠ Driver, real due date — no "TBD")
  and [`TradeoffMatrix.schema.json`](../../shared/schemas/artifacts/TradeoffMatrix.schema.json)
  (minimum criteria/options counts, optional `would_flip_when`
  falsifiability anchor).
