---
name: write-go-test
description: Author idiomatic Go tests — table-driven + t.Run subtests + t.Cleanup + httptest; one behavior per row.
---

# write-go-test

> Write Go tests in the standard library idiom: `testing.T`, table-driven, subtests, no third-party assertion library unless the repo already uses one.

## When to use

- A Go function or method behavior is uncovered.
- `polymath-qa:coverage-gap` flagged `MISSING (unit)` items in a Go module.
- A workflow invokes `polymath-lang-go:write-go-test`.

## Inputs

- The behavior(s) under test.
- Module conventions: package layout, whether `_test` packages are used (black-box), assertion preferences (stdlib vs `testify/require`).

## Procedure

1. **Detect setup.** `go.mod` for module path + minimum Go version. Check existing tests for assertion library (stdlib `t.Errorf` vs `testify`); match the prevailing style.
2. **File layout** — `foo.go` → `foo_test.go` in the same package by default. Use a `pkg_test` (external test package) when you want to avoid coupling to unexported helpers; surface this choice in the test header comment if non-obvious.
3. **Table-driven structure.** Each behavior is one row:
   ```go
   cases := []struct {
       name      string
       input     T
       want      U
       wantErr   bool
   }{
       {"happy path", ..., ..., false},
       {"empty input returns ErrEmpty", ..., ..., true},
   }
   for _, tc := range cases {
       tc := tc // capture for parallel
       t.Run(tc.name, func(t *testing.T) {
           t.Parallel()
           got, err := UnderTest(tc.input)
           if (err != nil) != tc.wantErr {
               t.Fatalf("err = %v, wantErr = %v", err, tc.wantErr)
           }
           if !reflect.DeepEqual(got, tc.want) {
               t.Errorf("got %v, want %v", got, tc.want)
           }
       })
   }
   ```
4. **`t.Helper()` + `t.Cleanup()`.** Any reusable assertion helper calls `t.Helper()`. Resources (temp files, fakes, servers) register cleanup via `t.Cleanup(func(){…})`, not `defer` — survives panics in subtests and keeps test order independent.
5. **`httptest`, `iotest`, `testing/fstest`.** Prefer the stdlib fakes over hand-rolling: `httptest.NewServer` for HTTP, `fstest.MapFS` for filesystems, `iotest.ErrReader` for forced errors.
6. **Goroutines + concurrency.** Tests with multiple goroutines need either explicit synchronization (`sync.WaitGroup`) or `-race` enabled. Add a comment when the test depends on `-race` to catch a regression.
7. **Errors.** Test for sentinel errors with `errors.Is`, for typed errors with `errors.As`, never with string contains.
8. **One behavior per row.** A row that asserts on three fields is a failed row even when only one field is wrong — the failure message must name which field.

## Output

A test file with package declaration, imports, helper functions, and `Test<Name>` functions using the table-driven pattern.

## Quality bar

- Subtests via `t.Run` — failure isolation + selective `go test -run` matching.
- `t.Parallel()` where the test is genuinely independent (most pure functions; never anything touching shared globals).
- `t.Cleanup` for teardown, not `defer`.
- Errors compared with `errors.Is` / `errors.As`, never `err.Error() == "…"`.

## Anti-patterns to avoid

- One giant `TestFoo` with manual `if` branches instead of a table. Failure messages won't say which case failed.
- `time.Sleep` in tests. Use synthetic clocks, channels, or polling helpers; sleeps make tests flaky.
- Asserting on log output. Logs are not contract; assert on returned values + errors.
- Skipping `t.Helper()`. The reported line moves to the helper, not the caller, and the failure looks wrong.
