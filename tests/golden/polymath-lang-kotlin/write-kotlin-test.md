---
plugin: polymath-lang-kotlin
scenario: write-kotlin-test
expect:
  invoked:
    - polymath-lang-kotlin:write-kotlin-test
  output_matches:
    - "(@Test|DescribeSpec|FunSpec)"
    - "(runTest|kotlinx.coroutines.test)"
    - "(MockK|every|verify|assertThat)"
timeout_seconds: 60
---

# Prompt

> Write Kotlin tests for `suspend fun parseRefund(input: String): Refund`
> that throws RefundError.Empty on empty input. Use kotlinx.coroutines.test.

Use polymath-lang-kotlin:write-kotlin-test.

# Acceptance

- Suspending test uses runTest, not runBlocking.
- Backtick-named functions describe behavior.
- MockK pattern used if collaborator is mocked.
- One behavior per test function.
