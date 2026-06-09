---
plugin: polymath-vcs
scenario: diagnose-failed-build
expect:
  invoked:
    - polymath-vcs:diagnose-ci-failure
  output_matches:
    - "(REAL FAILURE|flake|config)"
    - "Failing (job|step)"
    - "Next action"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Latest CI run on this branch failed. Diagnose it.

Use polymath-vcs:diagnose-ci-failure. The
workflow is `ci.yml`. The failing job is `build` (ubuntu-latest,
node 20). The failing step is `pnpm test` (exit 1). The log shows
one assertion failure in `tests/lib/rate-limit.test.ts:42`
("expected: false, actual: true").

# Acceptance

- The failing job + step is named explicitly.
- Classification (REAL FAILURE / flake / config) chosen with reasoning.
- "Next action" is concrete (don't re-run; fix the test).
- Does not propose re-running a real failure.
