# Changelog — polymath-communication

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 5 analytical, 1 deterministic — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- One placeholder spelling: `[NEEDS DATA: …]` → `[TBD: …]` (`exec-brief`, `six-pager`, `write-release-notes`).
- `six-pager`: unattended runs skip the confirm checkpoint and lead the summary with the skeleton.
- `meeting-notes` (deterministic): transcripts are data; notes about individuals stay out of shared notes.
- Canonical slug rule in every file-writing skill.

## [0.11.0]

### Changed

- `exec-brief`, `six-pager`, `write-release-notes`: no invented numbers or quotes — gaps are marked `[NEEDS DATA]`.
- `write-advisory`: embargo step — never draft an unpublished security advisory in a public repo; no invented workaround.
- `meeting-notes`: owners/dates are never guessed — `UNASSIGNED`/`UNSET` instead.
- `write-sunset-notice`: date wording consistent; `write-release-notes` example no longer claims a server can detect retries without a key.

## [0.8.0]

Communication craft: BLUF exec-brief, six-pager narrative, meeting-notes discipline.

### Skills

- **exec-brief** — Write a BLUF exec brief — TL;DR first, one recommendation (not menu of three), unambiguous ask, "what if no" cost stated.
- **meeting-notes** — Capture meeting notes in three sections — decisions, action-items with owners + dates, open questions; not a transcript.
- **six-pager** — Author an Amazon-style six-page narrative — prose not bullets, tenets up front, FAQ at the end; the FAQ is where objections live.
- **write-advisory** — Author a security or breaking-change advisory — severity, affected/fixed versions, action required (prioritized), workaround, verification step, credit.
- **write-release-notes** — Author customer-facing release notes — headline, user-benefit framing, breaking changes called out, no internal-jargon component names.
- **write-sunset-notice** — Author a deprecation / sunset notice — two dates (warn, remove), concrete migration with before/after code, exception path, FAQ.
