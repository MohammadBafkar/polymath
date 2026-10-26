---
name: ci-pipeline-github
description: Author a GitHub Actions workflow — lint/test/build/deploy with caching, concurrency control, OIDC for cloud auth, minimal permissions.
---

# ci-pipeline-github

> Write a `.github/workflows/*.yml` that's correct, fast, and secure.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A new repo needs CI.
- An existing workflow is slow, leaky, or sprawling.

## Inputs

- Language + framework.
- Deploy target (registry, k8s, serverless, …).
- Existing convention (other workflows in the repo to mirror).

## Project localization

Before the procedure, resolve the project snapshot —
`${POLYMATH_DATA_DIR:-$HOME/.polymath/data}/polymath-core/project-context.json`
(ignore it if its `_meta.source` belongs to another repo; absent → read
`.polymath/project.yaml` directly; neither → built-in defaults). Then apply
(contract: `polymath-core:project-context`):

- `conventions_docs`: read role `deployment` — pipeline standards and
  branch-to-environment mapping there override the generic layout
  below.

## Procedure

1. **Scope per workflow** — separate files for separate triggers. `ci.yml` for PRs + main, `deploy.yml` for tags, `nightly.yml` for cron. Don't shove everything into one workflow with branchy `if`s.
2. **Triggers**:
   - PRs: lint + test + build (no deploy).
   - main: same + publish artifacts.
   - tags `v*`: release.
3. **`permissions:` declared explicitly** at the workflow level (default to `contents: read`). Each job overrides as needed.
4. **`concurrency:`** to cancel superseded runs on the same ref. Saves runner minutes. For **deploy** workflows use `cancel-in-progress: false` — cancelling a deploy mid-flight can leave an environment half-updated; queue them instead.
5. **Cache** — language-aware caches (`actions/setup-node` with `cache: 'pnpm'`, `actions/setup-python` with `cache: 'pip'`, `actions/cache` keyed on lock files for Go modules).
6. **OIDC for cloud auth** — never store long-lived cloud credentials as secrets. Use the cloud provider's GitHub OIDC trust for `aws-actions/configure-aws-credentials@v4`, `google-github-actions/auth@v2`, `azure/login@v2`.
7. **Pin third-party actions by full commit SHA** (with a `# vX.Y.Z` comment; Dependabot/Renovate keep them fresh) — anything outside `actions/*`, and always for actions that touch credentials or publish artifacts. Floating major tags (`@v4`) are acceptable only for GitHub's own `actions/*`.
8. **Untrusted input never reaches a shell.** `${{ github.event.pull_request.title }}`, issue bodies, branch names, and commit messages are attacker-controlled: pass them through `env:` and quote the variable — never interpolate `${{ … }}` directly into `run:`. Never use `pull_request_target` (or `workflow_run`) to check out and run PR code with secrets or a write token.
9. **Fork PRs get no secrets and no OIDC token** — gate credentialed jobs with `if: github.event_name == 'push'` (or same-repo PRs) so fork PRs don't fail on auth.
10. **Fail fast** — set `fail-fast: false` only when matrix jobs are genuinely independent and you want signal across all.

## Output

```yaml
name: ci

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: corepack enable            # pnpm must exist before setup-node's pnpm cache step
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm test --reporter=dot

  build:
    needs: test
    if: github.event_name == 'push'   # fork PRs get no OIDC token
    runs-on: ubuntu-latest
    permissions:
      id-token: write    # OIDC for cloud login
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@<full-commit-sha>              # v3.x
      - uses: aws-actions/configure-aws-credentials@<full-commit-sha>   # v4.x
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions
          aws-region: us-east-1
      - uses: docker/build-push-action@<full-commit-sha>                # v6.x
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: 123456789012.dkr.ecr.us-east-1.amazonaws.com/refund:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Quality bar

- `permissions:` declared at workflow level; jobs grant the minimum.
- No `AWS_ACCESS_KEY_ID` / `GCP_SERVICE_ACCOUNT_KEY` in secrets — use OIDC.
- Concurrency-grouped to cancel superseded runs.
- Cache configured for the language.
- Build outputs only push on main / tags, not on PRs.

## Anti-patterns to avoid

- `secrets.AWS_ACCESS_KEY_ID` for cloud auth.
- One workflow with 8 `if: github.event_name == …` branches.
- `actions/checkout@master` (use pinned versions).
- `run: echo "${{ github.event.pull_request.title }}"` — script injection; route it through `env:`.
- `pull_request_target` + checkout of the PR head — runs untrusted code with your secrets.
- Running deploy on every PR.
