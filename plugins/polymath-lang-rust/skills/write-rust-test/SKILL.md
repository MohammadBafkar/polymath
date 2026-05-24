---
name: write-rust-test
description: Author idiomatic Rust tests — #[test] + #[tokio::test] + proptest; mod tests inline for unit, tests/ dir for integration.
---

# write-rust-test

> Write Rust tests in the standard idiom — `#[test]` for sync, `#[tokio::test]` for async, `proptest!` for invariants. One behavior per test.

## When to use

- A Rust function / impl block lacks tests.
- `polymath-qa:coverage-gap` flagged a Rust crate.
- A workflow invokes `polymath-lang-rust:write-rust-test`.

## Inputs

- The behavior(s) under test.
- Crate setup: `tokio` (which features), `proptest` available, `criterion` for bench.

## Procedure

1. **Detect setup.** Read `Cargo.toml` `[dev-dependencies]` for `tokio`, `proptest`, `assert_matches`, `mockall`. Match the prevailing style.
2. **Location.**
   - **Unit tests** — `#[cfg(test)] mod tests` inside the same file, *below* the impl. Access to private items + crate-internal types.
   - **Integration tests** — `tests/<area>.rs`. Treats the crate as an external user; verifies the public API.
   - **Doc tests** — ``` blocks in doc comments. Great for examples that must keep compiling.
3. **`#[test]` skeleton.**
   ```rust
   #[test]
   fn rejects_empty_input() {
       let err = parse_refund("").expect_err("expected error");
       assert!(matches!(err, RefundError::Empty));
   }
   ```
4. **Async — `#[tokio::test]`.** Specify a flavor explicitly when the test needs it: `#[tokio::test(flavor = "current_thread")]` for deterministic ordering, `flavor = "multi_thread"` only when the test exercises concurrency.
5. **Result-returning tests.** Use `Result<(), Error>` to use `?` instead of `.unwrap()`. Easier-to-read failures: each `?` short-circuits with its own error.
6. **Property-based — `proptest!`.**
   ```rust
   proptest! {
       #[test]
       fn roundtrip(amount in 0u64..1_000_000) {
           let r = Refund::new(amount);
           prop_assert_eq!(r.amount(), amount);
       }
   }
   ```
   Always set a strategy with explicit bounds; `any::<u64>()` over a budget-bound type causes spurious failures.
7. **`assert_matches!` over `match { _ => panic!(...) }`.** Concise; the failure message includes the actual variant.
8. **Test fixtures.** Use `once_cell::sync::Lazy` or a `#[fixture]` macro (`rstest`) only when fixtures are genuinely shared. Inline `let mut env = ...` is fine for one-off setups.

## Output

A test file (or `mod tests` block) with `#[test]` / `#[tokio::test]` / `proptest!` definitions per behavior.

## Quality bar

- One behavior per test name.
- `assert_matches!` for enum-y assertions.
- Async tests pick a flavor explicitly when concurrency matters.
- proptest strategies have explicit bounds.

## Anti-patterns to avoid

- `.unwrap()` everywhere in tests instead of `?` + `Result<(), E>`. Loses error context.
- Sharing mutable state across tests via `static`. Cargo runs tests in parallel; mutable statics flake.
- Mocking std types (`fs`, `time`). Use `tempfile::tempdir()` and inject clocks via traits.
- Testing through `println!` and reading stdout. Assert on returned values.
