---
plugin: polymath-lang-typescript
scenario: write-vitest-for-debounce
expect:
  invoked:
    - polymath-lang-typescript:write-vitest-test
  output_matches:
    - "it("
    - "vi.useFakeTimers"
    - "advanceTimersByTime"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 120
---

# Prompt

> Write vitest tests for this debounce utility.

```ts
// src/util/debounce.ts
export function debounce<T extends (...args: unknown[]) => void>(
  fn: T,
  delayMs: number,
): T {
  let timer: ReturnType<typeof setTimeout> | undefined;
  return ((...args: Parameters<T>) => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delayMs);
  }) as T;
}
```

Use polymath-lang-typescript:write-vitest-test. Cover: the
debounced function only fires once after the delay; rapid calls
collapse to one fire with the latest arguments; the timer is
cancelable.

# Acceptance

- Uses `vi.useFakeTimers()` and `vi.advanceTimersByTime`.
- At least 2 `it(…)` blocks describing distinct behaviors.
- Cleanup uses `vi.useRealTimers()` (afterEach or end-of-test).
- No real `setTimeout`-based waits.
