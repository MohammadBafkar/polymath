---
plugin: polymath-lang-go
scenario: write-table-test
expect:
  invoked:
    - polymath-lang-go:write-go-test
  output_matches:
    - "(t.Run|table)"
    - "(t.Parallel|t.Cleanup|t.Helper)"
    - "(errors.Is|errors.As|wantErr)"
timeout_seconds: 60
---

# Prompt

> Write Go tests for a function `func ParseRefund(input string) (Refund, error)`
> that returns `ErrEmpty` on empty input and a typed error on malformed input.

Use polymath-lang-go:write-go-test.

# Acceptance

- Table-driven cases with `t.Run` subtests.
- `t.Parallel()` for independent rows.
- `t.Cleanup` if resources are created (or note absence).
- Errors compared via `errors.Is` / `errors.As`, not string contains.
