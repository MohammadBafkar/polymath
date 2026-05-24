# polymath-lang-rust

Rust craft for the Polymath marketplace.

## What it ships

- Skills:
  - `write-rust-test` — `#[test]` + `#[tokio::test]` + `proptest!` with explicit bounds; `Result<(), E>` over `.unwrap()`.
  - `audit-cargo-toml` — edition + MSRV + workspace inheritance + feature hygiene + cargo-audit-reachable findings + cargo-deny gaps.
- Commands: `/polymath-lang-rust:test`, `/polymath-lang-rust:audit`.

## Installation

```bash
claude plugin install polymath-lang-rust@polymath
```

## Dependencies

- `polymath-core`
- `polymath-engineering`

## License

Apache-2.0.
