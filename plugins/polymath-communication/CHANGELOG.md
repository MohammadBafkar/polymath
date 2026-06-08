# Changelog — polymath-communication

## [Unreleased]

### Changed

- `write-release-notes`, `write-advisory`, and `write-sunset-notice` skills
  folded in from the former `polymath-content` plugin — customer-facing prose
  is the same audience-first craft as the internal briefs.
- Added the missing `Advisory.md` and `Sunset-notice.md` templates referenced
  by the folded-in skills so the workflow link-check passes.

## [0.1.0]

### Added

- Initial v0.1 components: `exec-brief` (BLUF, one recommendation), `six-pager` (Amazon-style narrative with tenets + FAQ), `meeting-notes` (3 sections only: decisions / actions / open questions) skills.
- Ships `Exec-brief.md` + `Six-pager.md` templates under `templates/`.
