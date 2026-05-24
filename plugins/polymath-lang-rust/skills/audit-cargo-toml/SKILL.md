---
name: audit-cargo-toml
description: Audit Cargo.toml — edition, MSRV (rust-version), workspace inheritance, feature-flag hygiene, vulnerable versions via cargo-audit / cargo-deny.
---

# audit-cargo-toml

> Spot stale or risky Cargo metadata before it bites. Output: categorized findings with concrete fixes (commands + diffs).

## When to use

- A Rust crate or workspace hasn't had a dep refresh in months.
- `cargo audit` is reporting findings nobody's read.
- A new contributor's `cargo build` produces warnings.

## Procedure

1. **`edition` and `rust-version`.**
   - `edition` should match the org's baseline (2021 or 2024 when stable).
   - `rust-version` should pin the MSRV (oldest supported toolchain). Crates without it accidentally adopt new-Rust features in a patch release.
2. **Workspace inheritance.** Workspaces should declare versions / authors / license at the root via `[workspace.package]` and have members say `version.workspace = true`. Inheritance is opt-in per field; missing-but-overridden fields are a smell.
3. **Feature flags.**
   - `default = [...]` should be small and well-motivated. A `default` that pulls in everything makes downstream feature flags useless.
   - Optional dependencies use `dep:foo` syntax in 2024 edition; the legacy implicit-feature behavior is being phased out.
   - Check for "feature unification": a workspace where members enable different feature sets of the same dep can break in `--release` mode but pass in `--debug`.
4. **`cargo-audit` / `cargo-deny`.**
   - `cargo audit` reports advisories from RustSec; surface findings that affect the dep graph (vs. transitively-pruned).
   - `cargo deny check` enforces a policy (denied crates, license allowlist, source registries). Flag missing `deny.toml` for non-toy projects.
5. **Yanked versions.** `cargo update --dry-run` warns about yanked versions held by `Cargo.lock`. Stuck-on-yanked is a supply-chain footgun.
6. **`patch` and `replace`.** `[patch.crates-io]` overrides for a local fork are fine *with* a tracking comment pointing at the upstream PR; without, they rot.
7. **`profile` overrides.** `[profile.release]` set to debug-friendly settings (debug=true, lto=false, codegen-units=high) silently slows release binaries. Verify against the project's actual prod profile.

## Output

```text
audit-cargo-toml

Workspace:    refund-api (members: 5)
Edition:      2021 (consider 2024 once your MSRV permits)
rust-version: 1.74 (missing on 2 of 5 members — set workspace inheritance)

Workspace inheritance:
  ✓ version, authors, license, edition at root.
  ✗ refund-cli does not inherit `license`.

Default features:
  refund-core/default = ["tracing", "tokio", "rustls", "postgres"]
  → "postgres" pulls a 4MB graph; consider moving behind a feature.

cargo audit:
  - chrono 0.4.x (RUSTSEC-2024-xxxx)  Segfault in localtime_r on glibc.
    Status: reachable from refund-core. Fix: bump to chrono 0.4.38+.

cargo deny:
  No deny.toml — recommend adding one with at least:
    licenses.allow = ["Apache-2.0", "MIT", "BSD-3-Clause"]

Yanked:
  - hyper 0.14.27 is yanked (use 0.14.28+).
```

## Quality bar

- MSRV present and matched across workspace.
- Default features reasoned about, not just listed.
- `cargo audit` findings filtered to *reachable* where the tool reports it.
- `[patch]` / `[replace]` entries have explanatory comments or are flagged.

## Anti-patterns to avoid

- `cargo update` to "fix" deps without reading the resulting `Cargo.lock` diff.
- Adding optional deps without listing them in the `[features]` table. They never get enabled by anyone and rot.
- A `default = ["full"]` umbrella feature. Makes downstream `default-features = false` users impossible to support cleanly.
- Pinning to `=1.2.3` (exact) without a reason. Most pinning should be `^1.2` (caret) and let consumers float patches.
