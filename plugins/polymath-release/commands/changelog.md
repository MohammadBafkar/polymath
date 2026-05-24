---
name: changelog
description: Append a user-facing entry to CHANGELOG.md under [Unreleased] using the Keep-a-Changelog format mapped from Conventional Commits.
---

# /changelog

Append a CHANGELOG entry that describes the user-facing impact of the current diff.

## What to do

1. Read `CHANGELOG.md`. If absent, create one from `plugins/polymath-release/templates/CHANGELOG-entry.md`.
2. Inspect the current diff or recent commits to determine the change category, mapping Conventional Commits → Keep-a-Changelog:
   - `feat:` → **Added**
   - `refactor:`, `perf:`, `style:` → **Changed**
   - deprecation → **Deprecated**
   - removal → **Removed**
   - `fix:` → **Fixed**
   - security fix → **Security**
3. Write one bullet per logical change. Imperative tense ("Add rate limiting on /login"), user-facing language, link to PR if known.
4. Append under `## [Unreleased]` in the appropriate subsection. Create the subsection if it doesn't exist.
5. Show the user the diff before saving.

## Quality bar

- No internal refactors without user impact.
- Each bullet is one line unless the bullet itself is the user-facing explanation.
- No emojis.
