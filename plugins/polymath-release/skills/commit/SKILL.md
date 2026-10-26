---
name: commit
description: Draft a Conventional Commits message for the current diff; never commits without showing the user the staged changes and the message first.
---

# commit

> Craft a Conventional Commits message for the current diff. Never
> commit until the user has approved the staged files AND the message.

## When to use

- The user says "commit this", "make a commit", or names a Conventional
  Commits scope.
- A workflow's release step needs a structured commit.

## Inputs

- The current working-tree state (staged + unstaged).
- Optional: hint about the type (`feat` / `fix` / `refactor` / …).
- Optional: scope hint.

## Procedure

1. **Inspect.** Run `git status` and `git diff --staged` plus
   `git diff`. If nothing is staged, show what would be staged and ask
   which files to include.
2. **Learn the repo's message convention before writing one.** Use, in
   order: the project context's `conventions.commit_style`, a commitlint /
   commitizen config, `CONTRIBUTING.md`, and the last ~20 subjects in
   `git log --oneline`. Conventional Commits is the default only when the
   repo shows no other convention — never force it onto a repo that writes
   plain imperative subjects or `[JIRA-123] …` prefixes.
3. **Determine type** from the diff (Conventional Commits repos):
   - `feat` — new user-facing behavior.
   - `fix` — bug fix.
   - `refactor` — behavior unchanged.
   - `perf` — behavior unchanged, measurable performance improvement.
   - `docs` — documentation only.
   - `test` — tests only.
   - `chore` — build / tooling / dependencies.
   - `style` — formatting only.
4. **Determine scope** from the directories touched (e.g.
   `polymath-flows`, `engineering`, `docs`). Pick one scope. If the
   diff truly spans multiple unrelated scopes, split into multiple
   commits instead of choosing a vague umbrella.
5. **Compose the message:**
   - First line: `type(scope): summary` (or the repo's own subject format)
     ≤ 72 chars, imperative mood ("add" not "added").
   - Body (optional): paragraph explaining the **why**, not the what.
   - Trailer: from the project snapshot's `attribution.commit_trailer`
     (`polymath-core:project-context`) when it is a non-empty string —
     append it verbatim as the final line. Absent or empty = NO trailer;
     never invent one. Catalog-authoring work follows
     `polymath-core/skills/conventions/SKILL.md`.
6. **Show the user** the staged files and the proposed message.
   **Do not commit yet.**
7. **On explicit approval**, stage the agreed files by explicit path
   (`git add -- <paths>`, never `git add -A` / `.`) and run `git commit`
   with the message.
8. **If a pre-commit hook fails**, the commit did not happen: fix the
   reported problem, re-stage, and create a **new** commit after showing
   the change — never `--amend` (it would rewrite the *previous* commit)
   and never `--no-verify`.
9. **Never** use `--amend`, `--no-verify`, `--no-gpg-sign`. Never
   include unrelated files.

## Safety

- If the diff contains likely secrets (the `polymath-engineering`
  secret-scan hook should already block edits, but verify here too),
  stop and report.
- If the user has unstaged changes that look related, ask whether to
  include them rather than guessing.
- Refuse to commit if the diff is empty.

## Output

```text
Staged:  src/refunds.py, tests/test_refunds.py
Message: fix(refunds): guard against negative refund amounts

Shown to user for approval before commit. On approval:
  a1b2c3d  fix(refunds): guard against negative refund amounts
```

- The proposed commit message (shown to user before commit).
- The list of files about to be staged.
- After approval and commit: the commit hash + a one-line summary.

## Quality bar

- The message follows the repo's own convention; in Conventional Commits repos the type is unambiguous.
- Summary ≤ 72 chars.
- One scope per commit (no umbrella scopes).
- Imperative mood, no past tense.

## Anti-patterns to avoid

- Committing without explicit user approval.
- Choosing `chore` when the diff is actually a `feat` or `fix`.
- Bundling refactor + behavior change into one commit.
- Using `--amend` to "fix" a hook failure (creates two-commit-in-one
  audit trails).
