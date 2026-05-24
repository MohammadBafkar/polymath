---
plugin: polymath-lang-rust
scenario: write-proptest
expect:
  invoked:
    - polymath-lang-rust:write-rust-test
  output_matches:
    - "(#\\[test\\]|#\\[tokio::test\\]|proptest)"
    - "(assert_matches|Result|expect_err)"
    - "(strategy|in 0|prop_assert)"
timeout_seconds: 60
---

# Prompt

> Write Rust tests for `pub fn parse_refund(input: &str) -> Result<Refund, RefundError>`.
> Include a property-based test that round-trips amounts in 0..1_000_000.

Use polymath-lang-rust:write-rust-test.

# Acceptance

- `#[test]` for sync cases.
- `proptest!` with an explicit strategy range.
- Errors asserted with `assert_matches!` or matches!, not string compare.
- Result-returning test where `?` simplifies the body.
