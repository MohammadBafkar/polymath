---
name: lint-with-ruff
description: Run ruff on the diff (lint + format); interpret findings and propose targeted fixes.
---

# lint-with-ruff

> Lint Python diffs with ruff. Interpret the rule code, propose a minimal fix.

## When to use

- A PR touches Python files.
- The user asks "is this code clean?".
- A workflow's pre-merge step needs the linter to pass.

## Inputs

- The diff (`git diff --name-only ... | grep '\.py$'`).
- The repo's ruff config (`pyproject.toml [tool.ruff]` or `ruff.toml`).

## Procedure

1. **Run scoped** — don't lint the whole repo unless requested:

   ```bash
   ruff check --diff $(git diff --name-only HEAD~1 HEAD -- '*.py')
   ruff format --check $(git diff --name-only HEAD~1 HEAD -- '*.py')
   ```

2. **Read the rule code** for each finding. The first letter classifies it:
   - `E`, `W`, `F` — pycodestyle / pyflakes (errors, warnings, undefined).
   - `I` — import sorting.
   - `B` — bugbear (real bugs).
   - `UP` — pyupgrade (syntax modernization).
   - `SIM` — simplification.
   - `C90` / `PLR09xx` — complexity.
   - `S` — bandit (security).
   - `ANN` — annotations.
3. **Classify each finding**:
   - **Real bug** (F, B, S): fix.
   - **Modernization** (UP, SIM): fix if the change is local; defer if it ripples.
   - **Style** (E, W, I): let `ruff format` handle.
   - **Annotation gap** (ANN): hand off to `propose-type-annotations`.
4. **Don't auto-fix unrelated regions.** Pass `--fix-only` to limit, and confirm before broad rewrites.

## Output

```text
ruff: <N> findings on <M> files.

Real bugs:
  - api/refund.py:42 B008  do not use mutable default argument
    Fix: default to None; instantiate inside the function.

Modernization:
  - api/util.py:8 UP007  use X | None over Optional[X]
    Fix: rewrite type annotation (local change, no ripple).

Style: 12 findings — all `ruff format` will auto-fix.
```

## Anti-patterns to avoid

- `--fix` on the whole repo when the diff touched 3 files.
- Disabling a rule globally to silence one finding (use `# noqa: <code>` on the line with a reason).
- Reformatting code that wasn't in the diff.
