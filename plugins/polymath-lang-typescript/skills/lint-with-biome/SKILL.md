---
name: lint-with-biome
description: Run biome (or eslint+prettier fallback) on the diff and interpret findings.
---

# lint-with-biome

> Lint TS/JS diffs with biome (preferred) or eslint+prettier (fallback).

## When to use

- A PR touches `.ts` / `.tsx` / `.js` / `.jsx` files.
- A workflow needs lint to pass before merging.

## Inputs

- The diff (`git diff --name-only ... -- '*.{ts,tsx,js,jsx}'`).
- Repo lint config: `biome.json` (preferred) or `.eslintrc.*` + `.prettierrc*`.

## Procedure

1. **Detect** which linter is configured:
   - `biome.json` present → biome.
   - `.eslintrc.*` + no `biome.json` → eslint+prettier.
   - Neither → ask the user before introducing a config.
2. **Run scoped**:

   ```bash
   # biome
   biome check --no-errors-on-unmatched $(git diff --name-only HEAD~1 HEAD -- '*.{ts,tsx,js,jsx}')
   biome format --no-errors-on-unmatched $(git diff --name-only HEAD~1 HEAD -- '*.{ts,tsx,js,jsx}')

   # eslint
   npx eslint $(git diff --name-only HEAD~1 HEAD -- '*.{ts,tsx,js,jsx}')
   npx prettier --check $(git diff --name-only HEAD~1 HEAD -- '*.{ts,tsx,js,jsx}')
   ```

3. **Classify findings** by biome's diagnostic category (or the eslint rule prefix):
   - `lint/correctness/*` / eslint `no-*` real bugs → fix.
   - `lint/suspicious/*` likely bugs → fix or annotate.
   - `lint/style/*` → let `biome format` (or prettier) handle.
   - `lint/complexity/*` → fix only if the change is local.
4. **Don't auto-fix unrelated regions.** `biome check --apply --reporter=json` should be scoped to the diff files.

## Output

```text
biome: <N> findings on <M> files.

Real bugs:
  - api/refund.ts:42  lint/correctness/noUnreachable
    Fix: dead code after early return; remove the unreachable block.

Style: 7 findings — `biome format` will auto-fix.
```

## Anti-patterns to avoid

- Disabling rules globally to silence one diff.
- Running on the whole repo when 3 files changed.
- Mixing eslint and biome configs in the same repo without picking a primary.
