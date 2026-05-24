---
name: write-vitest-test
description: Author idiomatic vitest tests — describe/it, vi.mock at boundaries; one behavior per test.
---

# write-vitest-test

> Write vitest tests in the project's idiom.

## When to use

- A TypeScript / JavaScript behavior is uncovered.
- `polymath-qa:coverage-gap` flagged `MISSING (unit)` items in a TS/JS project.
- A workflow invokes `polymath-lang-typescript:write-vitest-test`.

## Inputs

- The behavior(s) under test.
- Repo conventions: `vitest.config.ts`, test file glob, setup file, environment (`node` vs `jsdom`).

## Procedure

1. **Test layout** — match the repo: co-located `*.test.ts` next to source, or `tests/` directory. Don't introduce a new convention.
2. **Environment** — `node` by default; `jsdom` only if the unit under test touches the DOM. Set per-file with `// @vitest-environment jsdom` when needed.
3. **Name** — `describe("rateLimit", () => { it("rejects the sixth attempt in the window", …) })`. Describes the behavior, not the implementation.
4. **Use built-in matchers**:
   - `expect(x).toBe(y)` for primitives and references.
   - `expect(x).toEqual(y)` for deep equality.
   - `expect(fn).toThrow(/message substring/)` for sync throws.
   - `await expect(promise).rejects.toThrow(...)` for async rejections.
5. **Mock at the boundary**:
   - `vi.mock("./network-client", () => ({ fetch: vi.fn() }))` for module-level deps.
   - `vi.spyOn(globalThis, "Date").mockReturnValue(…)` for clock.
   - Don't mock internal helpers in the same module.
6. **Async** — `async/await`, no `done()` callbacks. Vitest handles unhandled rejections.
7. **Fake timers** — `vi.useFakeTimers()` + `vi.advanceTimersByTime(60_000)` for rate-limit / debounce / interval tests. Always `vi.useRealTimers()` in cleanup.
8. **Snapshots** — only for stable, *intentional* artifacts (rendered HTML for a specific component variant; never for arbitrary objects).

## Output

- `*.test.ts` files in the conventional location.
- Each test runs green via `npx vitest run <path>` invoked through `polymath-engineering:verify-change`.

## Anti-patterns to avoid

- `vi.mock` on the module under test.
- `it.skip` left in the diff.
- Snapshots that capture timestamps or generated IDs.
- `expect.anything()` / `expect.any(Object)` everywhere.
