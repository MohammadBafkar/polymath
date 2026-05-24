---
name: write-xctest
description: Author Swift tests in XCTest or Swift Testing — async/await, parameterized via #expect, one behavior per test, no UI-driven flakes.
---

# write-xctest

> Write Swift tests in the project's idiom: XCTest (`XCTestCase`) for established codebases, Swift Testing (`@Test`, `#expect`, `#require`) for newer Swift 6+ projects.

## When to use

- A Swift type or function lacks tests.
- `polymath-qa:coverage-gap` flagged a Swift package.
- A workflow invokes `polymath-lang-swift:write-xctest`.

## Inputs

- The behavior(s) under test.
- Setup: XCTest vs Swift Testing, async patterns in use, Combine vs async/await.

## Procedure

1. **Detect setup.** `Package.swift` `testTarget` dependencies: `XCTest` (older) or `Testing` (Swift Testing). Match the prevailing style; don't mix unless deliberately migrating.
2. **XCTest skeleton.**
   ```swift
   final class RefundParserTests: XCTestCase {
       func test_rejects_empty_input() throws {
           XCTAssertThrowsError(try parser.parseRefund("")) { error in
               XCTAssertEqual(error as? RefundError, .empty)
           }
       }
   }
   ```
3. **Swift Testing skeleton.**
   ```swift
   @Suite struct RefundParserTests {
       @Test func rejectsEmptyInput() throws {
           #expect(throws: RefundError.empty) {
               try parser.parseRefund("")
           }
       }

       @Test(arguments: [
           (0,    "invalid"),
           (1,    "micro"),
           (100,  "standard"),
       ])
       func classifies(amount: Int, expected: String) {
           #expect(classify(amount) == expected)
       }
   }
   ```
4. **Async/await.** Tests can be `async throws`. No `XCTestExpectation` plumbing needed unless you're observing a callback API.
5. **Time + clocks.** Inject a `Clock` (Swift 5.7+ `ContinuousClock` / `SuspendingClock`) and replace with `ImmediateClock` (test helper) in tests. Don't `await Task.sleep` for time-based assertions.
6. **Concurrency.** When testing actors, `await` the actor's method; XCTest waits correctly. Avoid `XCTWaiter` unless legacy.
7. **Combine.** `sink` + `XCTestExpectation` is the legacy idiom; for new code prefer `AsyncPublisher` + `for await` so the test reads top-to-bottom.

## Output

A Swift test file with imports, `@Test` / `func test_…` definitions matching the project's framework.

## Quality bar

- One behavior per `@Test` / `test_*` function.
- Async tests use `async throws`, not `XCTestExpectation` unless required.
- Parameterized tests via `@Test(arguments:)` (Swift Testing) or per-call data drivers; not loops with assertions inside.
- No `sleep` calls; use injected clocks.

## Anti-patterns to avoid

- Mixing XCTest + Swift Testing in the same target without a migration plan.
- `XCTUnwrap` followed by a force-unwrap. Use `try #require(…)` or `try XCTUnwrap(…)` and then access by name.
- Asserting on log output. Logs aren't contract.
- One mega-test exercising five behaviors. Failure messages won't point at the right one.
