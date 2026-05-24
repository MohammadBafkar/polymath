---
name: write-kotlin-test
description: Author Kotlin tests in JUnit 5 or Kotest — MockK + kotlinx.coroutines.test (runTest), backtick-named functions, one behavior per test.
---

# write-kotlin-test

> Write Kotlin tests in the project's idiom. Default JUnit 5 + MockK; Kotest if already in use. `kotlinx.coroutines.test.runTest` for suspending code.

## When to use

- A Kotlin function or class lacks tests.
- `polymath-qa:coverage-gap` flagged a Kotlin module.
- A workflow invokes `polymath-lang-kotlin:write-kotlin-test`.

## Procedure

1. **Detect setup.** Inspect `build.gradle.kts` for `junit-jupiter`, `io.kotest.*`, `io.mockk:mockk`, `kotlinx-coroutines-test`. Match the prevailing style.
2. **JUnit 5 + MockK skeleton.**
   ```kotlin
   class RefundParserTest {
       private val parser = RefundParser()

       @Test fun `rejects empty input`() {
           assertThrows<RefundError.Empty> { parser.parseRefund("") }
       }

       @ParameterizedTest
       @CsvSource("0,invalid", "1,micro", "100,standard")
       fun `classifies amount tier`(amount: Int, expected: String) {
           assertThat(classify(amount)).isEqualTo(expected)
       }
   }
   ```
3. **Kotest skeleton (when Kotest is the existing idiom).**
   ```kotlin
   class RefundParserTest : DescribeSpec({
       describe("parseRefund") {
           it("rejects empty input") {
               shouldThrow<RefundError.Empty> { parser.parseRefund("") }
           }
       }
   })
   ```
4. **Suspending tests.** `@Test fun foo() = runTest { … }` for suspending APIs. `runTest` uses `TestDispatcher`, fast-forwards virtual time, surfaces unfinished children as failures.
5. **MockK.** `every { … } returns …` for stubbing; `verify { … }` for assertions on calls. Use `relaxed = true` for fakes that mostly do nothing; explicit stubs for the rest.
6. **Clocks + time.** Inject `kotlinx.datetime.Clock` (or `java.time.Clock`). In coroutines, prefer `currentTime` over wall-clock checks.
7. **Backtick names.** ``fun `behavior under condition`()`` is Kotlin-idiomatic. Avoid `@DisplayName` unless the name can't be written that way.

## Quality bar

- Suspending tests use `runTest`, not `runBlocking`.
- MockK `every`/`verify` over manual fakes for most cases.
- Backtick names describing behavior.
- Parameterized for parameter spaces with ≥ 3 cases.

## Anti-patterns to avoid

- `runBlocking` in tests. Uses real time; blocks the test thread.
- Mutable `var` properties on test classes shared across tests. Init in `@BeforeEach`.
- MockK `every { … } answers { … }` with side-effecting closures. Tests become hard to reason about.
- Asserting via `println`. Use AssertJ / Kotest matchers.
