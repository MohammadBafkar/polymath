# Changelog — polymath-writing

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 6 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `rfc`, `architecture-doc`: Inputs and unattended-run rules; `editorial-pass`: exact cut-report shape.
- Canonical slug rule.

## [0.11.0]

### Changed

- `adr`: finds the repo's existing ADR directory; superseding updates only the old ADR's status line.
- `runbook`: every command/link verified or marked `[VERIFY]`; destructive steps flagged; no secrets.

## [0.8.0]

Writing craft: ADR (Nygard), RFC, runbook, C4 architecture doc.

### Skills

- **adr** — Write an Architecture Decision Record (Michael Nygard format) to docs/adrs/NNNN-<slug>.md; frontmatter validated by the ADR artifact schema. Records a made decision, not a proposal to debate (rfc).
- **architecture-doc** — Write a C4-style architecture document; System Context + Containers (+ Components when interesting) with mermaid diagrams. Describes structure, not a decision (adr) or proposal (rfc).
- **architecture-review-facilitation** — Run an architecture review as a process — entry criteria, reviewer checklist, decision log, and follow-up actions — pairing the design artifact with a red-team pass.
- **editorial-pass** — Review and tighten prose in a Markdown artifact for a target tone (terse, formal, friendly) without dropping information; preserve quotations and load-bearing constraints.
- **rfc** — Draft a lightweight design RFC to docs/rfcs/<slug>.md; Summary, Motivation, Detailed design, Drawbacks, Alternatives, Unresolved questions. A proposal to debate, not a recorded decision (adr).
- **runbook** — Write or refresh an operational runbook for an alert/symptom; structured as TL;DR + Pre-checks + Steps + Verification + Rollback + Escalation.
