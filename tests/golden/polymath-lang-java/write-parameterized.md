---
plugin: polymath-lang-java
scenario: write-parameterized
expect:
  invoked:
    - polymath-lang-java:write-junit5-test
  output_matches:
    - "(@Test|@ParameterizedTest)"
    - "(assertThat|AssertJ|catchThrowable)"
    - "(@Nested|@CsvSource|@MethodSource)"
timeout_seconds: 60
---

# Prompt

> Write JUnit 5 tests for `int classify(int amount)` covering at
> least 4 amount-tier pairs. Use AssertJ for assertions.

Use polymath-lang-java:write-junit5-test.

# Acceptance

- AssertJ chains, not pure JUnit assertEquals.
- @ParameterizedTest with @CsvSource (or @MethodSource) for the tier table.
- Method names describe behavior, not "test1/test2".
- No Thread.sleep; if async is involved, use awaitility.
