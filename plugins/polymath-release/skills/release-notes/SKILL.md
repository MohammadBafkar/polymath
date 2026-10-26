---
name: release-notes
description: Draft version release notes (GitHub release / docs page) from CHANGELOG [Unreleased]; not a customer announcement (write-release-notes).
---

# release-notes

> Draft the release notes that ship *with a version* — the GitHub release
> body or docs changelog page — from the `[Unreleased]` section of
> `CHANGELOG.md`. Readers are users and integrators upgrading; **user
> benefit** over implementation detail.

## When to use

- The user says "draft release notes for vX.Y.Z".
- A workflow's release step needs the customer-facing notes.
- Not the marketing/customer announcement (email, blog, in-app) — that is
  `polymath-communication:write-release-notes`, which can start from these
  notes.

## Inputs

- `CHANGELOG.md` `[Unreleased]` section.
- Optional: target version string (e.g. "0.3.0").
- Recent commits (`git log --oneline -20`) to fill in context missing
  from the CHANGELOG.

## Procedure

1. **Read** `CHANGELOG.md`. If `[Unreleased]` is empty, ask the user
   which commit range to summarize.
2. **Read** recent commits to fill in any context missing from the
   CHANGELOG.
3. **Produce the notes in layers:**
   - **Headline**: one sentence on the most important change.
   - **Breaking changes** (only when present, and first after the
     headline): each with its migration step or a link to the
     `polymath-release:migration-guide`.
   - **What's new**: each `Added` entry restated in user language.
     No internal-only changes.
   - **Notable changes**: `Changed` / `Deprecated` / `Removed` /
     `Fixed` / `Security` entries that affect users.
   Every item traces to a CHANGELOG entry or commit — never add a claim
   (a speedup figure, a fixed bug) the sources don't contain.
4. **Tone**: brief, user-benefit oriented, no marketing fluff, no
   emojis.
5. **Write to** `docs/release-notes/<version>.md` if a version is
   supplied, otherwise `docs/release-notes/draft.md`.

## Output

- File: `docs/release-notes/<version>.md`.
- Summary listing the headline and the count of items in each layer.

## Quality bar

- Each item answers "why does the user care?", not "what changed
  internally?".
- Breaking changes are called out in their own section with a clear
  migration path.
- Security fixes credit the reporter when known.
- Notes are scannable in under 30 seconds — anything longer goes in
  the linked CHANGELOG.

## Anti-patterns to avoid

- Marketing adjectives ("blazing-fast", "delightful").
- Internal refactor / build-system entries that don't affect users.
- Restating the CHANGELOG verbatim (it's already linked).
- Combining migration steps and feature announcements in one bullet.

## Cross-plugin pairing

- For broader customer content (advisories, sunset notices, public
  announcements), use `polymath-communication:write-advisory` or `polymath-communication:write-sunset-notice`.
- For the PR description that ships with the release commit, use
  `polymath-release:pr`.
