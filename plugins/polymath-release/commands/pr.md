---
name: pr
description: Draft a PR description for the current branch following the canonical PR template; saves the draft to docs/pr/<slug>.md without opening a real PR.
---

# /pr

Draft a PR description from the current branch's commits. Writes to `docs/pr/<slug>.md`. v0.1 does **not** open a real GitHub PR.

## What to do

1. Run `git log <base>..HEAD --oneline` to see commits on the branch. Default base is `main`.
2. Run `git diff <base>..HEAD --stat` for the file list.
3. Inspect the PRD (if `docs/prds/<slug>.md` exists) to ground the motivation section.
4. Load the canonical template at `plugins/polymath-release/templates/PR-description.md`.
5. Fill the template:
   - **Summary**: one paragraph in active voice.
   - **Motivation**: link the PRD, ADR, or issue.
   - **Changes**: high-level grouped bullets — not a file-by-file restatement.
   - **Test plan**: concrete steps a reviewer can run.
   - **Risk and rollback**: state explicitly. Even "low risk; revert by reverting the PR" is fine if it's the truth.
   - **Reviewers**: tag by area if you can infer it.
   - **Checklist**: leave unchecked for the author to confirm.
6. Compute the slug from the branch name or the PRD slug.
7. Write `docs/pr/<slug>.md`.

When this command is invoked as part of the `shipFeature` workflow, the workflow's `mustPass` check expects this file to exist.

## Safety

- Never push to a remote.
- Never call `gh pr create` in v0.1.
- Surface a unified diff if the target file already exists.
