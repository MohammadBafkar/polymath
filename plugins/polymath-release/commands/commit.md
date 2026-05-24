---
name: commit
description: Stage and craft a Conventional Commits message for the current diff; never commits without showing the user the staged changes and the message first.
---

# /commit

Craft a Conventional Commits message for the current diff and create the commit only after the user approves.

## What to do

1. Run `git status` and `git diff --staged` plus `git diff`. If nothing is staged, show what would be staged and ask which files to include.
2. Inspect the diff to determine the commit type:
   - `feat`: new user-facing behavior.
   - `fix`: bug fix.
   - `refactor`: behavior unchanged.
   - `perf`: behavior unchanged, measurable performance improvement.
   - `docs`: documentation only.
   - `test`: tests only.
   - `chore`: build / tooling / dependencies.
   - `style`: formatting only.
3. Determine the scope from the directories touched (e.g. `polymath-flows`, `engineering`, `docs`). One scope only.
4. Compose the message:
   - First line: `type(scope): summary` ≤ 72 chars, imperative mood ("add" not "added").
   - Body (optional): paragraph explaining the why, not the what.
   - Trailer: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`.
5. Show the user the staged files and the proposed message. **Do not commit yet.**
6. On explicit approval, stage the agreed files and run `git commit` with the message.
7. Never use `--amend`, `--no-verify`, `--no-gpg-sign`. Never include unrelated files.

## Safety

- If the diff contains likely secrets (the `polymath-engineering` secret-scan hook should already block edits, but verify here too), stop and report.
- If the user has unstaged changes that look related, ask whether to include them rather than guessing.
- Refuse to commit if the diff is empty.
