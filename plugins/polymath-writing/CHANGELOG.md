# Changelog — polymath-writing

## [0.1.0]

### Added

- `adr`, `rfc`, `runbook`, `architecture-doc`, and `editorial-pass`
  skills.
- `ADR.md`, `RFC.md`, `Runbook.md`, `Architecture-doc.md` templates
  under `templates/`.
- Frontmatter on each template is validated by its matching schema
  under `registry/schemas/artifacts/`:
  [`ADR`](../../registry/schemas/artifacts/ADR.schema.json),
  [`RFC`](../../registry/schemas/artifacts/RFC.schema.json),
  [`Runbook`](../../registry/schemas/artifacts/Runbook.schema.json)
  (load-bearing `last_reviewed` staleness field), and
  [`ArchitectureDoc`](../../registry/schemas/artifacts/ArchitectureDoc.schema.json)
  (`levels` enum mirrors the skill's "skip C4 L4 by default"
  constraint).
- `editorial-pass` takes a markdown artifact + target tone
  (terse / formal / friendly) + optional length budget and returns a
  tightened copy without rewriting quotations or dropping load-bearing
  constraints.
