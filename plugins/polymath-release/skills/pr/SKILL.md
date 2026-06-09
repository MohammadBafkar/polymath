---
name: pr
description: Draft a PR description for the current branch following the canonical PR template; saves the draft to docs/pr/<slug>.md without opening a real PR.
---

# pr

> Draft a PR description from the current branch's commits. Writes to
> `docs/pr/<slug>.md`. **Does not** open a real GitHub PR in v0.1;
> that's `polymath-vcs:open-pr`.

## When to use

- The user says "draft a PR", "PR description for this branch".
- A workflow's release step needs the PR draft artifact.

## Inputs

- The current branch's commits (read via `git log`).
- Optional: PRD path at `docs/prds/<slug>.md` (anchors motivation).
- Optional: target base branch (default `main`).

## Procedure

1. Run `git log <base>..HEAD --oneline` to see commits on the branch.
   Default `<base>` is `main`.
2. Run `git diff <base>..HEAD --stat` for the file list.
3. Inspect the PRD (if `docs/prds/<slug>.md` exists) to ground the
   motivation section.
4. Load the canonical template at
   `plugins/polymath-release/templates/PR-description.md`.
5. Fill the template:
   - **Summary**: one paragraph in active voice. What does this PR do?
     Why now?
   - **Motivation**: link the PRD, ADR, or issue.
   - **Changes**: high-level grouped bullets — not a file-by-file
     restatement.
   - **Test plan**: concrete steps a reviewer can run.
   - **Risk and rollback**: state explicitly. Even "low risk; revert
     by reverting the PR" is fine if it's the truth.
   - **Reviewers**: tag by area if you can infer from CODEOWNERS or
     diff paths.
   - **Checklist**: leave unchecked for the author to confirm.
6. Compute the slug from the branch name or the PRD slug.
7. Write `docs/pr/<slug>.md` with the validated frontmatter
   (artifact: PRDescription).

The PR draft is **a file**, not an opened PR. Pair with
`polymath-vcs:open-pr` to open the actual PR via MCP.

## Safety

- Never push to a remote.
- Never call `gh pr create` in v0.1.
- Surface a unified diff if the target file already exists.
- Do not invent reviewers — only suggest from CODEOWNERS or the diff.

## Output

- File: `docs/pr/<slug>.md` with PRDescription frontmatter.
- Summary listing the linked PRD/ADR and the suggested base branch.

## Workflow validation

```yaml
mustPass:
  - id: pr-draft-valid
    type: artifactSchemaStrict
    path: docs/pr/${workflow.slug}.md
    artifact: PRDescription
    minBodyChars: 300
```

## Quality bar

- Summary is one paragraph in active voice.
- Motivation links a concrete PRD / ADR / issue.
- Test plan has actionable steps a reviewer can execute.
- Risk + rollback are explicit, not "low risk, none."

## Anti-patterns to avoid

- File-by-file restatement of the diff (the reviewer can read it).
- "Cleanup" PRs without explicit motivation.
- Marking own PR ready-for-review without test plan filled.
- Bundling refactor + feature in one PR description.
