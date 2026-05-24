---
plugin: polymath-lang-swift
scenario: write-swift-test
expect:
  invoked:
    - polymath-lang-swift:write-xctest
  output_matches:
    - "(XCTAssert|#expect|@Test)"
    - "(async|throws)"
    - "(parser|RefundError)"
timeout_seconds: 60
---

# Prompt

> Write Swift tests for `func parseRefund(_ input: String) throws -> Refund`
> that throws `RefundError.empty` on empty input.

Use polymath-lang-swift:write-xctest.

# Acceptance

- One behavior per test function.
- Error asserted with XCTAssertThrowsError or `#expect(throws:)`.
- Async tests use `async throws` if the API is async.
- No XCTestExpectation if not required.
