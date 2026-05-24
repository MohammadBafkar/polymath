---
name: migrate-ts-version
description: Plan a TypeScript version upgrade in phases; classify breaking changes, propose pin/fix/strict.
---

# migrate-ts-version

> Upgrade TypeScript a major (or sometimes a minor) version with a phased plan.

## When to use

- The project pins an old TypeScript version and wants to move.
- A dependency requires a newer TS version.

## Inputs

- Current version (from `package.json devDependencies.typescript`).
- Target version (user-supplied or "latest").
- Strictness flags from `tsconfig.json`.

## Procedure

1. **Read release notes** between current and target. Categorize each notable change:
   - **Compiler strictness defaults** (e.g. `useUnknownInCatchVariables`).
   - **Inference changes** (control-flow analysis, narrowing improvements that flag pre-existing bugs).
   - **API removals / renames** (e.g. removed lib types).
   - **New syntax** (only relevant if you want to adopt it).
2. **Run a probe**:

   ```bash
   # In a throwaway branch
   npm install --save-dev typescript@<target>
   npx tsc --noEmit
   ```

   Capture the error count and categorize: real bug uncovered vs. spurious strictness regression.
3. **Plan in phases**:
   - **Phase A — pin**. Bump the version; relax any newly-strict flag temporarily.
   - **Phase B — fix**. Address errors in batches: per-package, per-folder. Each batch is its own PR.
   - **Phase C — strict**. Re-enable the flag that was relaxed.
4. **Update CI** — make sure the new tsc version runs on the same node version your CI uses.
5. **Library types** — bump matching `@types/*` packages in step.

## Output

```text
TypeScript migration: 5.4 → 5.6

Breaking changes that apply to this repo:
  - useUnknownInCatchVariables now defaults to true (was already on).
  - inferred-narrowing improvement: 12 places where dead branches now error.
  - Removed types: ImportAttributes shape changed.

Phases:
  A. Pin 5.6, leave tsconfig strict-flags untouched.   (1 PR, today)
  B. Fix 12 inferred-narrowing errors in api/ and ui/. (2 PRs, this week)
  C. Verify CI green; remove temporary @ts-expect-error annotations. (1 PR)
```

## Anti-patterns to avoid

- One giant PR that bumps the version and fixes everything.
- `@ts-ignore` to silence narrowing improvements that catch real bugs.
- Skipping the probe ("looks small, should be fine").
