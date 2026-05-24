---
name: write-junit5-test
description: Author idiomatic JUnit 5 tests — @Test, @ParameterizedTest, AssertJ chains, @Nested for behavior grouping; one behavior per @Test.
---

# write-junit5-test

> Write JUnit 5 tests in the prevailing project idiom. AssertJ chains preferred over Hamcrest. Parameterized tests for parameter spaces; `@Nested` to group related behaviors.

## When to use

- A Java class / method has no test or low coverage.
- `polymath-qa:coverage-gap` flagged a Java module.
- A workflow invokes `polymath-lang-java:write-junit5-test`.

## Inputs

- The behavior(s) under test.
- Build tool (Maven / Gradle) and assertion library (AssertJ / Hamcrest / pure JUnit).

## Procedure

1. **Detect setup.** Inspect `pom.xml` / `build.gradle.kts` for `junit-jupiter`, `assertj-core`, `mockito-core`. Match the prevailing assertion style.
2. **File layout** — `src/main/java/com/x/Foo.java` → `src/test/java/com/x/FooTest.java`. Class name `<TypeUnderTest>Test`.
3. **`@Test` skeleton (AssertJ).**
   ```java
   @Test
   void rejectsEmptyInput() {
       Throwable t = catchThrowable(() -> parser.parseRefund(""));
       assertThat(t)
           .isInstanceOf(RefundException.class)
           .hasMessage("input must not be empty");
   }
   ```
4. **Naming.** Method name describes the behavior in plain English: `rejectsEmptyInput`, `returnsFullRefundWhenAmountNotProvided`, `propagatesUpstreamTimeout`. Avoid `testFoo` / `test1`.
5. **`@ParameterizedTest`.** For parameter spaces:
   ```java
   @ParameterizedTest(name = "[{index}] amount={0} → tier={1}")
   @CsvSource({
       "0,    invalid",
       "1,    micro",
       "100,  standard",
       "9999, premium"
   })
   void classifiesAmount(int amount, String tier) {
       assertThat(classify(amount)).isEqualTo(tier);
   }
   ```
6. **`@Nested` to group behaviors.** `@Nested class WhenInputIsEmpty { ... }`. Builds a readable hierarchical report.
7. **Lifecycle.** `@BeforeEach` for per-test fixtures; `@BeforeAll` only for genuinely shared, idempotent setup. Static + mutable state across tests is a flake source.
8. **Mocks (Mockito).** Prefer `@ExtendWith(MockitoExtension.class)` + `@Mock` over `mock(Type.class)` plumbing. Verify behavior, not implementation — `verify(repo).save(captor.capture())` then `assertThat(captor.getValue()).…`.
9. **Async / Concurrency.** `awaitility` for "eventually" assertions; `Thread.sleep` flakes. For Kotlin or Reactor code, prefer `StepVerifier` over manual subscribe.
10. **Time.** Don't hard-code `Instant.now()` in tests. Inject a `Clock` (Java 8+) and use `Clock.fixed(...)` in tests.

## Output

A test class with imports, fixtures, and `@Test` / `@ParameterizedTest` / `@Nested` definitions.

## Quality bar

- Method names describe behavior, not implementation.
- AssertJ chains over Hamcrest `assertThat(x, is(equalTo(y)))`. One assertion vocabulary per project.
- Parameterized tests for parameter spaces (≥ 3 cases).
- `@Nested` groups for distinct contexts.
- `awaitility` over `Thread.sleep`.

## Anti-patterns to avoid

- `@DisplayName("Test 1")`. Use the method name; DisplayName for the rare time the method name can't be plain English.
- `@RunWith` (JUnit 4 idiom). JUnit 5 uses `@ExtendWith`.
- Verifying private methods via reflection. Test through the public surface.
- A single `@Test` with 12 assertions that all explore the same path. Split into per-behavior tests.
