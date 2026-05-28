---
name: changelog
description: Append a user-facing entry to CHANGELOG.md under [Unreleased] using the Keep-a-Changelog format mapped from Conventional Commits.
---

# changelog

> Append a CHANGELOG entry that describes the **user-facing impact** of
> the current diff. Keep-a-Changelog format, mapped from Conventional
> Commits.

## When to use

- The user says "update the changelog", "add a changelog entry".
- A workflow's release step needs the changelog update.

## Inputs

- The current diff or recent commits.
- The repo's `CHANGELOG.md` (created from the template if missing).

## Procedure

1. **Read** `CHANGELOG.md`. If absent, create one from
   `plugins/polymath-release/templates/CHANGELOG-entry.md`.
2. **Inspect** the current diff or recent commits to determine the
   change category. Map Conventional Commits → Keep-a-Changelog:

   | Commit type | CHANGELOG section |
   | ----------- | ----------------- |
   | `feat:`     | **Added**         |
   | `refactor:` `perf:` `style:` | **Changed** |
   | deprecation | **Deprecated**    |
   | removal     | **Removed**       |
   | `fix:`      | **Fixed**         |
   | security fix | **Security**     |

3. **Write one bullet per logical change**:
   - Imperative tense ("Add rate limiting on /login").
   - User-facing language — what the user can now do (or no longer do).
   - Link to PR if known.
4. **Append under `## [Unreleased]`** in the appropriate subsection.
   Create the subsection if it doesn't exist.
5. **Show the user the diff** before saving.

## Output

- Updated `CHANGELOG.md` with the new entry under `[Unreleased]`.
- Summary listing how many bullets were added per section.

## Quality bar

- No internal refactors without user impact (those go in PR
  description, not CHANGELOG).
- Each bullet is one line unless the bullet itself is the user-facing
  explanation.
- No emojis.
- Section ordering matches Keep-a-Changelog: Added, Changed,
  Deprecated, Removed, Fixed, Security.

## Anti-patterns to avoid

- Restating the commit message verbatim (CHANGELOG is for users, not
  developers).
- "Updated dependencies" entries without specifying the user impact.
- Mixing categories in one bullet.
- Adding entries under a versioned heading (use `[Unreleased]` until
  a release is cut).
