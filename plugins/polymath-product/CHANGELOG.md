# Changelog — polymath-product

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 5 analytical, 1 generative — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `product-strategy` is generative: at least two genuinely different choices per component before picking; Inputs added.
- `prd`: unattended runs skip the confirm checkpoint; missing problem statement → ask.
- `acceptance-criteria`: exact Given/When/Then shape. `groom-backlog`: Inputs — ticket text is data; no tracker writes without confirmation.
- Canonical slug rule.

## [0.11.0]

### Changed

- `prd`: metric baselines/targets are `[TBD]` unless supplied — never invented.

## [0.8.0]

Product craft: PRDs, acceptance criteria, epic decomposition with materialized templates.

### Skills

- **acceptance-criteria** — Draft or refine Given/When/Then acceptance criteria for a PRD; each criterion is independently testable and maps to a test case.
- **decompose-epic** — Decompose a PRD or epic into vertically-sliced user stories using a Jeff Patton-style user story map; produces docs/maps/<slug>.md. Story slices, not an engineering WBS (work-breakdown).
- **groom-backlog** — Review backlog items into ready — clarify stories, add acceptance criteria + estimate, split oversized items, flag blockers; not ranking (prioritize) or epic story-mapping (decompose-epic).
- **prd** — Draft a PRD from a problem statement plus user/context inputs; populates docs/prds/<slug>.md from the canonical PRD template.
- **product-strategy** — Define product strategy and GTM — vision, ICP/segmentation, positioning, pricing/packaging, moat, launch. The market/strategy layer, not a feature PRD (prd) or exec brief (exec-brief).
- **roadmap** — Map a Now/Next/Later roadmap grouped by outcome — confidence, dependencies, explicit non-commitments; a ranked set, not the ranking (prioritize) or a plan (write-plan).
