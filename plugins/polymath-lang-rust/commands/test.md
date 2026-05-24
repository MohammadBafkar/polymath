---
description: Author or extend a Rust test for the behavior(s) you describe.
---

Invoke `polymath-lang-rust:write-rust-test` for the behavior(s) the user describes.

Inputs to gather from context:
- The function / impl under test (file + signature).
- Whether tests go in `mod tests` (unit) or `tests/` (integration).
- `tokio` features / `proptest` availability per Cargo.toml dev-dependencies.

After writing the test:
- Run `cargo test --workspace` and surface any failures.
- Run `cargo test --workspace --all-features` if features gate the code under test.
