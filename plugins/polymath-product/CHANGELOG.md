# Changelog — polymath-product

## [Unreleased]

### Changed

- `product-strategy` skill folded in from the former `polymath-product-strategy` plugin.

### Added

- **PRD template upgrades.** `templates/PRD.md` gains **Locked
  decisions** (with sources; never relitigated silently) and a
  **Deferral registry** (deferred scope with revisit conditions;
  distinct from non-goals). The `prd` skill fills both and adds a
  summary-first checkpoint before drafting the full document.
- `roadmap` skill — sequence a Now/Next/Later roadmap grouped by outcome, with
  confidence, dependencies, and explicit non-commitments per horizon.
- `groom-backlog` skill — refine backlog items to a Definition of Ready
  (clarify, acceptance criteria, estimate, split oversized, flag blockers).
- Skill-triggering tests for both.

## [0.1.0]

### Added

- Initial v0.1 components: `prd`, `acceptance-criteria`, `decompose-epic` skills with materialized `PRD.md` and `User-story-map.md` templates.
