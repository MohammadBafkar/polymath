---
name: verify-change
description: Run repository-appropriate verification (build, lint, type-check, tests) on the changed files; summarize pass/fail per category.
---

# verify-change

> Run the verification a human reviewer would run before approving the change, scoped to the changed files where possible.

## When to use

- After `feature-dev` and `code-review`, before opening a PR.
- A workflow invokes `polymath-engineering:verify-change`.
- The user says "run the checks" or "verify it works".

## Inputs

- The current diff (used to scope which files matter).
- Project verification commands. Detect from these signals in order:
  1. CI config (`.github/workflows/*.yml`, `.gitlab-ci.yml`, …) — the commands CI actually runs are the best evidence of what "verified" means here.
  2. `CONTRIBUTING.md` / `AGENTS.md` / `CLAUDE.md` "before you push" instructions.
  3. `package.json` scripts: `lint`, `typecheck`, `test` — run through the project context's `stack.package_manager` when set, else the manager the lockfile names (`pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `package-lock.json` → npm).
  4. `pyproject.toml` / `requirements*.txt` with `pytest`, `ruff`, `mypy`.
  5. `Cargo.toml` → `cargo test`, `cargo clippy`.
  6. `go.mod` → `go test ./...`, `go vet ./...`.
  7. `*.csproj` / `*.sln` → `dotnet build`, `dotnet test`.
  8. `Makefile` → `make test` if defined.

## Project localization

Before the procedure, resolve the project snapshot —
`${POLYMATH_DATA_DIR:-$HOME/.polymath/data}/polymath-core/project-context.json`
(ignore it if its `_meta.source` belongs to another repo; absent → read
`.polymath/project.yaml` directly; neither → built-in defaults). Then apply
(contract: `polymath-core:project-context`):

- `skill_overrides["polymath-engineering:verify-change"].test_commands`:
  use the entry matching the project's primary language as the
  verification command, ahead of the detection order below.

## Procedure

1. Identify the verification commands the repo supports.
2. Run them in this order:
   - **Build / compile** (if applicable). A build failure stops the run — nothing downstream is meaningful.
   - **Lint / format check.**
   - **Type-check.**
   - **Unit tests.**
   - **Integration tests** (only if fast or scoped to the change).
   After a successful build, run lint, type-check, and tests independently — one failing category does not hide the others' results.
3. **Read the counts, not just the exit code.** "0 tests collected" (pytest exit 5, `--passWithNoTests`, an over-narrow filter) is not a PASS — report it as `NO TESTS RAN`. Skipped tests are listed.
4. If a step fails, surface the exact error output and the suspected file. Classify each failure as **introduced** or **pre-existing** — re-run the failing check on the base commit (`git stash` or a worktree) when it is cheap. Do not auto-fix unless the user has explicitly authorized it.
5. A test that fails, then passes on one re-run, is reported as `FLAKY` with its name — not as PASS.
6. If a step is unavailable (no test infra, no linter), note "not applicable" rather than skipping silently.

## Output

```text
Verification summary:
  - build      : PASS / FAIL / N/A
  - lint       : PASS / FAIL / N/A
  - typecheck  : PASS / FAIL / N/A
  - unit tests : PASS / FAIL / N/A
  - smoke      : PASS / FAIL / N/A

Tests run: <count>; passed: <count>; failed: <count>; skipped: <count>.
Commands: <exact commands run>

Failures:
  - lint: src/rate_limit.py:42 E501 line too long         (introduced)
  - unit: tests/test_refund.py::test_negative FAIL         (pre-existing — fails on base too)
```

When a workflow gates this step with `stepSummaryMatches` (e.g. on "tests" / "verified"), the summary satisfies it by reporting the verification that actually ran. If nothing ran or something failed, say so plainly — the gate is supposed to catch that.

## Anti-patterns to avoid

- Running the entire test suite when a scoped run is sufficient (wastes time and obscures the signal).
- Treating a missing test framework as success — surface it.
- Auto-fixing without explicit permission.
- Reporting PASS from an exit code when zero tests ran, or after re-running a failure until it went green.
- Writing "verified" in a summary to satisfy a workflow gate when verification did not run.
