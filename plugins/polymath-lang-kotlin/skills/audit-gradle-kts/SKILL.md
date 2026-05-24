---
name: audit-gradle-kts
description: Audit build.gradle.kts — Kotlin version + JVM target alignment, plugin pinning, BOM use, multi-module separation, vulnerable deps.
---

# audit-gradle-kts

> Find drift in a Gradle Kotlin DSL setup before it bites: unpinned plugins, Java/Kotlin version skew, missing BOMs, reachable vulnerabilities.

## Procedure

1. **Kotlin version.** `kotlin("jvm") version "X.Y.Z"` should match `kotlin.compilerOptions.languageVersion`. Drift between compiler and language version creates a confusing mix of "available in compiler but reported as error".
2. **JVM target.**
   ```kotlin
   kotlin { jvmToolchain(21) }
   ```
   The toolchain pins Java for both compile + runtime; mixed Java versions across modules ship binary-incompatible bytecode.
3. **Plugin pinning.** `plugins { id("…") version "…" }` always pin. Avoid `apply plugin` without a version.
4. **BOM use.** Spring / Quarkus / Kotest / Ktor all ship BOMs; modules should `implementation(platform("…:bom:…"))` then declare deps without version.
5. **Multi-module.** Use `subprojects { }` for common config (Kotlin compiler args, test framework, code coverage). Per-module specifics in each `build.gradle.kts`.
6. **Vulnerabilities.** `dependencyCheck` or `snyk` plugin. Surface findings with reachable scope.
7. **`kotlin-stdlib`.** Don't pin explicitly when the Kotlin plugin manages it; explicit pins cause weird "module Foo expected …, but found stdlib …" diagnostics during upgrades.

## Output

```text
audit-gradle-kts

Module:            refund-core
Kotlin version:    1.9.23
JVM toolchain:     21 (root); refund-cli overrides to 17 — mismatch.

Pinning
  ✓ All plugins pinned via plugins { id("…") version "…" }.
  ✗ kotlin("jvm") not in version-catalog (libs.versions.toml); upgrade
    requires touching N build files instead of one.

Vulnerabilities (dependencyCheck)
  - jackson-databind 2.15.2 (reachable from refund-core).
    Fix: bump via spring-boot BOM to 2.15.4+.

Stdlib
  - kotlin-stdlib pinned explicitly to 1.9.10 in refund-cli; remove the
    explicit dep and let the Kotlin plugin manage it.

Recommendation: align toolchain at root, introduce libs.versions.toml,
                bump jackson via BOM, drop manual kotlin-stdlib pin.
```

## Anti-patterns to avoid

- Per-module Kotlin or JVM version drift. Binary-incompat bytecode at runtime.
- `apply plugin: "kotlin"` (legacy Groovy) without a version. Floats.
- Explicit `kotlin-stdlib` pin alongside the Kotlin Gradle plugin. Use the plugin's stdlib management.
- Custom Maven repos over HTTP. Flag.
