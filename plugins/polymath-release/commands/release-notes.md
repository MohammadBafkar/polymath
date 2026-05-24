---
name: release-notes
description: Draft customer-facing release notes from CHANGELOG [Unreleased] entries; emphasizes user benefit over implementation detail.
---

# /release-notes

Draft release notes for the next version from the `[Unreleased]` section of `CHANGELOG.md`.

## What to do

1. Read `CHANGELOG.md`. If `[Unreleased]` is empty, ask the user which range to summarize.
2. Read recent commits (`git log --oneline -20`) to fill in any context missing from the CHANGELOG.
3. Produce the notes in three layers:
   - **Headline**: one sentence on the most important change.
   - **What's new**: each `Added` entry restated in customer language. No internal-only changes.
   - **Notable changes**: `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security` entries that affect customers.
4. Tone: brief, user-benefit oriented, no marketing fluff, no emojis.
5. Write to `docs/release-notes/<version>.md` if a version is supplied, otherwise `docs/release-notes/draft.md`.

## Quality bar

- Each item answers "why does the user care?", not "what changed internally?".
- Breaking changes are called out in their own section with a clear migration path.
- Security fixes credit the reporter when known.
