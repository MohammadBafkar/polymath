---
name: audit-go-mod
description: Audit go.mod / go.sum — toolchain directive, indirect bloat, replace directives, vulnerable versions, unused modules.
---

# audit-go-mod

> Spot the rot in `go.mod` before it bites. Output is a categorized audit + concrete fixes you can paste into a PR.

## When to use

- A Go module hasn't had a dep refresh in months.
- Vulnerability scanner flagged the project.
- Onboarding a new contributor and `go build` produces warnings.

## Procedure

1. **Toolchain.** Check `go` and `toolchain` directives.
   - `go 1.X` should match the minimum supported version, not the local dev version.
   - `toolchain go1.X.Y` pins a specific compiler; useful for reproducible builds but a regular review item.
2. **Direct vs indirect.** Anything with `// indirect` shouldn't appear in direct imports — `go mod tidy` would remove it. A non-trivial indirect list means a direct dep is dragging the world in.
3. **Replace directives.** `replace` is fine for monorepo-relative paths and for forks awaiting upstream fixes; an unmotivated `replace` pointing at someone's fork is a supply-chain footgun.
4. **Vulnerabilities.** Run `govulncheck ./...`. Surface only the ones that affect *called* code (govulncheck does the reachability check; reachable findings are real, unreachable ones are noise).
5. **Major-version migrations.** `module example.com/foo/v2` needs the `/v2` suffix in imports. Pre-`/v2` libraries pinned at `v1.X` while consumers already migrated → version skew.
6. **Unused.** `go mod why <module>` for each direct dep — a tree that ends at "main module does not need module foo" is a candidate for removal.
7. **Workspace.** If `go.work` exists, ensure every member's module is listed; missing members silently fall back to released versions.

## Output

```text
audit-go-mod

Module:        github.com/example/refund-api (Go 1.22)
Toolchain:     go1.22.3 (pinned)

Direct deps (18) — non-trivial:
  github.com/jackc/pgx/v5     v5.5.5
  github.com/stretchr/testify v1.9.0
  ...

Indirect (217) — high; review whether a direct dep is the cause.

Issues
  - github.com/google/uuid v1.3.0 — `govulncheck` flags GO-2024-2611
    (reachable from main).
    Fix: bump to v1.6.0 (`go get github.com/google/uuid@v1.6.0`).

  - replace github.com/foo/bar => github.com/our-fork/bar v0.0.0-2024…
    No tracking comment. Add a comment with the upstream PR or rationale,
    or drop the replace if the fix has landed.

  - github.com/stretchr/objx — indirect-only, drags 4 transitive deps.
    Investigate which direct dep imports it (`go mod why -m`).

Recommendation: 1 dep bump, 1 replace cleanup, 1 transitive investigation.
```

## Quality bar

- Vuln findings filtered to *reachable* by `govulncheck`. Unreachable are noted but not blocking.
- Replace directives explained (or flagged when not).
- Recommendations are concrete commands, not "consider updating deps".

## Anti-patterns to avoid

- Blanket `go get -u ./...`. Floods PRs with unrelated bumps; loses change provenance.
- Treating every `govulncheck` warning as urgent. Reachability matters.
- Removing `// indirect` comments by hand. `go mod tidy` is authoritative.
- Adding `replace` directives "just for now" with no tracking comment. They outlive the urgency.
