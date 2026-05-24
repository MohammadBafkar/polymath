---
name: audit-csproj-modernization
description: Audit .csproj modernization — SDK-style, implicit usings, nullable, CPM, Directory.Build.props.
---

# audit-csproj-modernization

> Read a .csproj (or a whole solution) and report what's worth modernizing. Output is findings, not edits.

## When to use

- A .NET project hasn't been touched in a while.
- A team is consolidating package versions across multiple projects.
- A PR adds a new project and should match modern conventions.

## Procedure

For each project file, check:

1. **SDK-style format**. `<Project Sdk="Microsoft.NET.Sdk">` at the root. Legacy `<Project ToolsVersion=…>` is a flag.
2. **TargetFramework(s)**. Are we on a supported version (LTS or current)? Multi-target only when actually needed.
3. **Nullable reference types**. `<Nullable>enable</Nullable>` — on or off, consistent across projects in the solution.
4. **Implicit usings**. `<ImplicitUsings>enable</ImplicitUsings>` for .NET 6+.
5. **Treat warnings as errors**. `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` for production projects (test projects can be looser).
6. **Lang version**. `<LangVersion>latest</LangVersion>` or pin explicitly; don't leave it at the default.
7. **Central Package Management (CPM)**. Is there a `Directory.Packages.props` with `<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>` at the repo root? If not, are versions consistent across `.csproj` files? Inconsistency is a flag.
8. **Directory.Build.props / Directory.Build.targets**. Shared properties live there — not duplicated across .csproj files.
9. **PackageReference vs packages.config**. packages.config means a legacy project; migrating is a precondition for everything else.
10. **AssemblyInfo**. SDK-style autogenerates it. If the project also has a hand-written `AssemblyInfo.cs`, it's a flag for cleanup.

## Output

```text
csproj audit: src/Refunds.csproj

Findings:
  - SDK-style:                    ok
  - TargetFramework:              net8.0 (current LTS — ok)
  - Nullable:                     missing — recommend enable
  - ImplicitUsings:               missing — recommend enable
  - TreatWarningsAsErrors:        false — recommend true for prod project
  - LangVersion:                  default — recommend pin to latest
  - Central Package Management:   not configured at solution root
  - Directory.Build.props:        absent — three repeated properties found
                                  across 4 .csproj files (suggest extracting)

Recommended sequence:
  1. Introduce Directory.Build.props with TreatWarningsAsErrors, LangVersion.
  2. Enable Nullable + ImplicitUsings in Refunds.csproj. Fix warnings in
     a follow-up PR.
  3. Adopt CPM via Directory.Packages.props when other projects join.
```

## Anti-patterns to avoid

- Modernizing every project in one PR.
- Enabling Nullable without a plan for the resulting warnings (use `propose-nullable-references` skill).
- Adopting CPM in only some projects (it must be solution-wide).
