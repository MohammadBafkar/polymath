---
name: write-xunit-test
description: Author idiomatic xUnit tests — [Fact]/[Theory], fixtures, async; one behavior per test.
---

# write-xunit-test

> Write xUnit tests in the project's idiom.

## When to use

- A C# behavior is uncovered.
- `polymath-qa:coverage-gap` flagged `MISSING (unit)` items in a .NET project.
- A workflow invokes `polymath-lang-dotnet:write-xunit-test`.

## Inputs

- The behavior(s) under test.
- Repo conventions: which test project (`*.Tests.csproj`), assertion library (`Assert.*` vs `FluentAssertions` vs `Shouldly`), and any `IClassFixture`/`ICollectionFixture` patterns.

## Procedure

1. **Detect** the test runner setup. xUnit + `Microsoft.NET.Test.Sdk` is the default. If `FluentAssertions` is referenced, match its style; otherwise stick to `Assert.*`.
2. **File layout** — match the source. `src/Refunds/RateLimit.cs` → `tests/Refunds.Tests/RateLimitTests.cs`. Class name `<TypeUnderTest>Tests`.
3. **`[Fact]` vs `[Theory]`**:
   - `[Fact]` — one behavior with one input set.
   - `[Theory]` + `[InlineData]` — same behavior across multiple inputs.
   - `[MemberData]` / `[ClassData]` — when the inputs need real C# expressions or are too long for inline.
4. **Naming** — `MethodUnderTest_StateUnderTest_ExpectedBehavior`, e.g. `Allow_SixthAttemptInWindow_ReturnsFalse`. Or `Should…When…` if the project uses that convention.
5. **Arrange / Act / Assert** with visible blank lines. One Act per test.
6. **Async** — `public async Task TestName()` returning `Task`. Use `await Assert.ThrowsAsync<T>` for exceptions.
7. **Fixtures** —
   - `IClassFixture<TFixture>` for per-class setup shared across the class.
   - `ICollectionFixture<TFixture>` for cross-class sharing (registered via `[CollectionDefinition]`).
   - Never use static state for shared setup.
8. **Theory data** — prefer immutable record types or tuples. Don't return mutable lists from `[ClassData]`.
9. **Mocking** — `Moq` or `NSubstitute` at boundaries. Don't mock the SUT's collaborators inside the same class.

## Output

- `*Tests.cs` files in the conventional test project.
- Each test runs green via `dotnet test --filter "FullyQualifiedName~<TestName>"` invoked through `polymath-engineering:verify-change`.

## Anti-patterns to avoid

- `[Fact(Skip = "TODO")]` left in.
- Multiple `Act` lines in one test.
- Sharing mutable state via static fields.
- `Thread.Sleep(...)` to "wait for the async thing".
