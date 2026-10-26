---
name: changelog
description: Write a user-facing CHANGELOG entry under [Unreleased] in Keep-a-Changelog format, mapped from Conventional Commits.
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

1. **Check how this repo keeps its changelog first.** If it uses a generator
   — `.changeset/` (Changesets), `release-please-config.json`,
   `towncrier.toml` / `newsfragments/`, `cliff.toml` (git-cliff), or
   semantic-release — write the entry in *that* tool's format (e.g. a
   changeset file) and do not hand-edit `CHANGELOG.md`.
2. **Read** `CHANGELOG.md`. If absent and no generator is in use, create one
   from [`CHANGELOG-entry.md`](../../templates/CHANGELOG-entry.md).
3. **Inspect** the current diff or recent commits to determine the
   change category. Map Conventional Commits → Keep-a-Changelog:

   | Commit type | CHANGELOG section |
   | ----------- | ----------------- |
   | `feat:`     | **Added**         |
   | `perf:` or a user-visible behavior change | **Changed** |
   | deprecation | **Deprecated**    |
   | removal     | **Removed**       |
   | `fix:`      | **Fixed**         |
   | security fix | **Security**     |
   | `refactor:` `style:` `test:` `chore:` `ci:` with no user impact | *(omit)* |

   A breaking change (`!` after the type, or a `BREAKING CHANGE:` footer) is
   prefixed **BREAKING:** in its bullet and names the migration path.

4. **Write one bullet per logical change**:
   - Imperative tense ("Add rate limiting on /login").
   - User-facing language — what the user can now do (or no longer do).
   - Link to PR if known.
5. **Append under `## [Unreleased]`** in the appropriate subsection.
   Create the subsection if it doesn't exist.
6. **Show the user the diff** before saving.

## Output

```markdown
## [Unreleased]

### Fixed
- Reject negative refund amounts that previously created a credit (#481)
```

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
