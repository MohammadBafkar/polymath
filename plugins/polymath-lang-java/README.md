# polymath-lang-java

Java craft for the Polymath marketplace.

## What it ships

- Skills:
  - `write-junit5-test` — JUnit 5 + AssertJ + Mockito idiom; `@ParameterizedTest` + `@Nested` for behavior grouping.
  - `audit-build-tooling` — Java release alignment, dependency / plugin pinning, BOM usage, reachable vulnerabilities, repo-URL hygiene.
- Commands: `/polymath-lang-java:test`, `/polymath-lang-java:audit`.

## Installation

```bash
claude plugin install polymath-lang-java@polymath
```

## Dependencies

- `polymath-core`
- `polymath-engineering`

## License

Apache-2.0.
