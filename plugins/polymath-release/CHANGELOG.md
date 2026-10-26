# Changelog — polymath-release

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 5 analytical, 2 deterministic — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `deprecation-plan` (plus anti-patterns), `migration-guide`, `safe-rollout`: exact output shapes, artifact paths aligned with the workflows that call them, and missing dates/baselines marked instead of invented.
- `commit` and `changelog` are deterministic; canonical slug rule in `pr`.

## [0.11.0]

### Changed

- `commit`: follows the repo's own message convention (`conventions.commit_style` now wired, commitlint, `git log`) instead of forcing Conventional Commits; explicit-path staging; hook failures produce a new commit, never `--amend`.
- `changelog`: uses the repo's changelog generator (Changesets, release-please, towncrier, git-cliff) when present; refactor/style/test/chore are omitted; breaking changes flagged.
- `pr`: the repo's own GitHub PR template wins over the catalog default; merge-base diff against the remote default branch.
- `release-notes`: scoped to version release notes (it collided with `write-release-notes`); breaking-changes layer; no claims without a source.

### Fixed

- `changelog` and `pr` loaded templates from marketplace-only `plugins/...` paths.

### Removed

- The `/commit`, `/pr`, `/changelog`, and `/release-notes` commands — the same-named skills are already `/polymath-release:<name>`.

## [0.8.0]

Release craft: Conventional Commits, PR descriptions, CHANGELOG, release notes.

### Skills

- **changelog** — Write a user-facing CHANGELOG entry under [Unreleased] in Keep-a-Changelog format, mapped from Conventional Commits.
- **commit** — Draft a Conventional Commits message for the current diff; never commits without showing the user the staged changes and the message first.
- **deprecation-plan** — Plan a deprecation — two dates (warn + remove), telemetry-gated removal, comms cadence, exception path, code/header markers. The lifecycle plan, not the customer notice (write-sunset-notice).
- **migration-guide** — Write a consumer migration guide for a breaking change — before/after examples, ordered steps, gotchas, rollback. Consumer upgrade steps, not the deprecation timeline (deprecation-plan).
- **pr** — Draft a PR description for the current branch following the canonical PR template; saves the draft to docs/pr/<slug>.md without opening a real PR.
- **release-notes** — Draft customer-facing release notes from CHANGELOG [Unreleased] entries; emphasizes user benefit over implementation detail.
- **safe-rollout** — Design a safe progressive rollout — flags, canary/blue-green, ring stages, SLO health gates, automated rollback, kill switch. Rollout mechanics, not env promotion or A/B experiments.

### Commands

- **/changelog** — Write one [Unreleased] CHANGELOG line after a change lands.
- **/commit** — Review the staged diff and craft a Conventional Commits message before anything lands.
- **/pr** — Draft a PR body to docs/pr/<slug>.md after committing; opens no real PR.
- **/release-notes** — Draft release notes to docs/release-notes/<version>.md when cutting a version.
