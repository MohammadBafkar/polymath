---
workflow: migrateLanguageVersion
scenario: migrateLanguageVersion-ts5.6
expect:
  invoked:
    - polymath-flows:run-workflow
    - polymath-lang-typescript:migrate-ts-version
    - polymath-engineering:feature-dev
    - polymath-engineering:verify-change
    - polymath-engineering:code-review
  artifacts:
    - "docs/migrations/ts-5-4-to-5-6-plan.md"
  state_must_pass:
    - plan-exists
    - plan-categorizes-changes
    - verify-mentions-tests
    - review-checks-residue
timeout_seconds: 900
---

# Prompt

> Migrate TypeScript 5.4 → 5.6.

/polymath-flows:run-workflow migrateLanguageVersion targetVersion="5.6" currentVersion="5.4"

# Acceptance

- Migration plan exists and categorizes breaking changes (strictness /
  inference / removal / new syntax).
- Phase A (PIN) lands a green build with newly-strict flags relaxed.
- Phase B (FIX) addresses errors in batches (per-package or per-folder),
  not one giant diff.
- Verify gates between batches.
- Phase C (STRICT) re-enables relaxed flags + removes temp @ts-expect-error.
- Review explicitly checks for opportunistic refactors and remaining
  ts-expect-error annotations.
