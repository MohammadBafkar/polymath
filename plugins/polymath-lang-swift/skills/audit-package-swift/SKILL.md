---
name: audit-package-swift
description: Audit Package.swift — swift-tools-version, swiftLanguageVersions, dependency versioning, platforms, exact-pin discipline.
---

# audit-package-swift

> Spot rot in `Package.swift` before a `swift build` flips a contributor over.

## Procedure

1. **`// swift-tools-version`.** Pin to the oldest tool version that compiles the manifest. Don't bump just because Xcode did.
2. **`swiftLanguageVersions`** — keep aligned with the deployment toolchain. Mixed v5/v6 across packages is a porting smell.
3. **Platforms.** `.macOS(.v13)`, `.iOS(.v16)` should match support policy. Old platforms inflate test matrix; new platforms exclude users on older Xcode.
4. **Dependency pinning.**
   - `.upToNextMajor(from: "1.0.0")` — usual SemVer caret.
   - `.exact("1.2.3")` — only with a tracking comment (why this version pinned).
   - `.branch("main")` — usable for development; never in a published release.
   - Local-path dependencies (`.package(path: …)`) — fine in a workspace; flag if leaking into a shipped package.
5. **Resources.** Declare resources explicitly (`resources: [.copy("Foo.json")]`) — auto-discovery exists but is order-dependent and bites.
6. **Tests target deps.** `XCTest` / `Testing` should be in `dev-dependencies` only — never in main `dependencies` (carries test binaries into release builds).
7. **`Package.resolved`** — commit it for executables and libraries with binary distribution; for pure libraries, omit to let downstream pick versions.
8. **Vulnerabilities.** Swift ecosystem lacks a canonical advisory DB; cross-check against GitHub Security Advisories for each dep.

## Output

```text
audit-package-swift

Tools version:  5.9 (current toolchain 6.0; consider bumping after MSRV review)
Swift versions: [.v5] — consider adding .v6 once consumers migrate.

Platforms
  .iOS(.v16), .macOS(.v13) — aligned with org support policy.

Dependencies (4)
  github.com/apple/swift-async-algorithms  .upToNextMajor("1.0.0")  ✓
  github.com/apple/swift-collections        .exact("1.0.6")          ⚠ exact-pin without comment
  github.com/example/refund-internal        .branch("main")          ✗ branch dep in release

Tests target
  ✓ Testing in dependencies of testTarget only.

Recommendation: replace .exact pin with .upToNextMajor or add a tracking
                comment; replace .branch with a tagged version before release.
```

## Anti-patterns to avoid

- `.branch("main")` in a released package.
- `.exact("…")` pins without a comment explaining why.
- Putting test-only deps in the main `dependencies` list.
- Auto-discovering resources without declaring them; one rename breaks the bundle.
