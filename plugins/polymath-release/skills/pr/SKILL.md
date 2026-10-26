---
name: pr
description: Draft a PR description for the current branch following the canonical PR template; saves the draft to docs/pr/<slug>.md without opening a real PR.
---

# pr

> Draft a PR description from the current branch's commits. Writes to
> `docs/pr/<slug>.md`. **Drafts only** — it never opens a real GitHub PR;
> that's `polymath-vcs:open-pr`, which consumes this draft.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- The user says "draft a PR", "PR description for this branch".
- A workflow's release step needs the PR draft artifact.

## Inputs

- The current branch's commits (read via `git log`).
- Optional: PRD path at `docs/prds/<slug>.md` (anchors motivation).
- Optional: target base branch (default: the remote's default branch — `git symbolic-ref --short refs/remotes/origin/HEAD`, else `main`).

## Project localization

Before the procedure, resolve the project snapshot —
`${POLYMATH_DATA_DIR:-$HOME/.polymath/data}/polymath-core/project-context.json`
(ignore it if its `_meta.source` belongs to another repo; absent → read
`.polymath/project.yaml` directly; neither → built-in defaults). Then apply
(contract: `polymath-core:project-context`):

- `prompts.pr_description_template`: when set, use that file as the PR
  body template instead of the catalog default.

## Procedure

1. Run `git fetch origin <base>` (when a remote exists), then
   `git log origin/<base>..HEAD --oneline` to see the branch's own commits.
2. Run `git diff origin/<base>...HEAD --stat` (three dots: against the merge
   base) for the file list.
3. Inspect the PRD (if `docs/prds/<slug>.md` exists) to ground the
   motivation section.
4. Pick the template, first match wins: the project context's
   `prompts.pr_description_template`; the repo's own GitHub template
   (`.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`,
   root `PULL_REQUEST_TEMPLATE.md`, or `docs/PULL_REQUEST_TEMPLATE.md`); else
   the catalog default [`PR-description.md`](../../templates/PR-description.md).
   A repo template's headings win over the catalog's — keep the
   PRDescription frontmatter for the workflow gate.
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
6. **Slug** from the branch name (reuse the PRD's slug when the PR implements one): a workflow's `${workflow.slug}` wins; otherwise lowercase it, replace each run of characters outside `a-z0-9` with `-`, trim `-` at the ends, and cut to ≤ 60 characters at a `-`. An existing file at the target path is updated in place (show the diff), never duplicated.
7. Write `docs/pr/<slug>.md` with the validated frontmatter
   (artifact: PRDescription).

The PR draft is **a file**, not an opened PR. Pair with
`polymath-vcs:open-pr` to open the actual PR via MCP.

## Safety

- Never push to a remote.
- Never call `gh pr create` — PR creation is `polymath-vcs:open-pr`'s job, after the user approves this draft.
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
