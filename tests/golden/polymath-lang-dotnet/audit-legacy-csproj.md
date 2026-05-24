---
plugin: polymath-lang-dotnet
scenario: audit-legacy-csproj
expect:
  invoked:
    - polymath-lang-dotnet:audit-csproj-modernization
  output_matches:
    - "Nullable"
    - "ImplicitUsings"
    - "TargetFramework"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Audit this .csproj for modernization opportunities.

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
    <OutputType>Library</OutputType>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
    <PackageReference Include="Serilog" Version="2.10.0" />
  </ItemGroup>
</Project>
```

Use polymath-lang-dotnet:audit-csproj-modernization.

# Acceptance

- Reports SDK-style: ok.
- Calls out missing `<Nullable>` and `<ImplicitUsings>`.
- Notes TargetFramework `net6.0` is no longer LTS-current (LTS is `net8.0`).
- Recommends extracting shared properties into Directory.Build.props if other
  projects share them.
- The recommendation does not insist on modernizing everything in one PR.
