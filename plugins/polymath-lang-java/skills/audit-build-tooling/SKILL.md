---
name: audit-build-tooling
description: Audit Maven pom.xml or Gradle build.gradle(.kts) — Java version, dependency version pinning, plugin pinning, multi-module separation, vulnerable versions.
---

# audit-build-tooling

> Spot the drift in Maven / Gradle config that turns a build into a foot-gun: floating versions, mixed Java targets, vulnerable dependencies, BOM gaps.

## When to use

- A Java project hasn't had a dep refresh in months.
- Vulnerability scanner flagged the build.
- Onboarding a new contributor and `mvn` / `gradle` produces deprecation warnings.

## Procedure

1. **Java version.**
   - Maven: `<maven.compiler.release>` (preferred) or `<maven.compiler.source>`/`<target>`.
   - Gradle: `java.toolchain { languageVersion = JavaLanguageVersion.of(...) }`.
   - The release/target should match the minimum supported runtime. Mixed source/target across modules is a smell — pin at the parent / root.
2. **Dependency version pinning.**
   - Floating versions (`1.0+`, `[1.0,2.0)`) make builds non-reproducible. Pin or use a BOM.
   - Spring Boot, Quarkus, etc. ship BOMs (`spring-boot-dependencies`); modules should `import` the BOM and declare deps without version.
3. **Plugin pinning.**
   - Maven: `<pluginManagement>` should pin every plugin used. Unpinned plugins float to "latest" on each developer's local Maven.
   - Gradle: `plugins { id("...") version "..." }` always pin the version; never use `apply plugin: "..."` without a version.
4. **Multi-module separation.**
   - Maven: parent POM contains versions; child modules omit them.
   - Gradle: `subprojects { }` / `allprojects { }` configure the common bits; per-module specifics in each `build.gradle.kts`.
   - Cross-module deps via `:module-name` (Gradle) or `<dependency>` with project coordinates (Maven), never paths or jars.
5. **Vulnerabilities.**
   - Maven: `mvn dependency-check:check` (OWASP plugin) or Snyk integration.
   - Gradle: `gradle dependencyCheckAnalyze` or `gradle dependencies --scan`.
   - Surface findings with **reachable** scope where the tool reports it.
6. **Dependency hygiene.**
   - Unused dependencies bloat the runtime classpath. `mvn dependency:analyze` lists declared-but-unused.
   - Duplicate versions (`<version>1.0</version>` in two modules) — let the parent decide.
   - SNAPSHOT versions in published artifacts. SNAPSHOT in a release build is a footgun.
7. **Repository config.** Custom Maven repos / Gradle `maven { url … }` entries — verify origin (corporate vs. random), enforce HTTPS, prefer `mavenCentral()` for OSS deps.

## Output

```text
audit-build-tooling

Build:        Maven (multi-module: api, core, cli)
Java release: 21 (api), 17 (cli) — mismatch; pin at parent.

Pinning
  ✓ All deps pinned via spring-boot-dependencies BOM.
  ✗ maven-compiler-plugin not in <pluginManagement>; using 3.8.1 implicitly.

Vulnerabilities
  - jackson-databind 2.15.2 → RUSTSEC equivalent: CVE-2023-xxxxx
    Reachable from api module. Bump to 2.15.4 (already in newer BOM).

Unused
  - api: declares commons-logging but uses slf4j; remove commons-logging.

Repos
  - https://maven.example.internal — corporate mirror, HTTPS ✓, has cert.
  - http://repo.example.com — HTTP, not HTTPS — security risk.

Recommendation: align Java release at parent, pin maven-compiler-plugin,
                bump jackson-databind, remove commons-logging, fix HTTP repo URL.
```

## Quality bar

- Java version pinned at parent / root.
- BOMs used where the framework provides one.
- Vulnerabilities filtered to reachable.
- HTTP repository URLs flagged explicitly.

## Anti-patterns to avoid

- `<version>RELEASE</version>` or `+` floating versions. Non-reproducible builds.
- Per-module Java version drift. Causes binary incompatibilities at runtime.
- "Apply plugin without version" in Gradle. Floats; reproducibility footgun.
- Adding a custom repo without a tracking comment. Random repos rot or get hijacked.
