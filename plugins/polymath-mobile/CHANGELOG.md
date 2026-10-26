# Changelog — polymath-mobile

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 3 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `deep-links` (link parameters are untrusted input), `mobile-perf` (no guessed dominant cost), `push-notifications` (test sends only with approval): Inputs sections.

## [0.11.0]

### Fixed

- `mobile-perf`: device tiers corrected (median Android is mid-range, not a flagship); measurement tools named.
- `push-notifications`: Android 13+ `POST_NOTIFICATIONS`; collapse keys and token cleanup.
- `deep-links`: saved post-login targets validated (open redirect).

## [0.8.0]

Mobile craft: mobile perf budgets, push notification design, deep-link routing.

### Skills

- **deep-links** — Design deep-link routing — universal/app links over custom schemes, deferred deep-link for install path, fallback web URL, signed param verification.
- **mobile-perf** — Set mobile perf budgets — cold start (TTI), warm start, scroll FPS, memory; per audience device tier (low-end Android baseline); identify the dominant cost. Native only; not web CWV.
- **push-notifications** — Design push notifications — opt-in moment, payload shape, tap-deep-link, silent vs visible, quiet hours, unsub path; respect the OS bucket constraints.
