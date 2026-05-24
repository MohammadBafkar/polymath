---
name: write-phpunit-test
description: Author PHPUnit / Pest tests — dataProvider for parameter spaces, attribute-based annotations (PHPUnit 10+), Mockery for collaborators.
---

# write-phpunit-test

> Write PHPUnit (or Pest) tests in the project's idiom. PHPUnit 10+ uses PHP attributes (`#[Test]`, `#[DataProvider]`); older versions use docblock annotations (`@test`, `@dataProvider`).

## When to use

- A PHP class / function lacks tests.
- `polymath-qa:coverage-gap` flagged a PHP project.
- A workflow invokes `polymath-lang-php:write-phpunit-test`.

## Procedure

1. **Detect setup.** `composer.json` `require-dev` for `phpunit/phpunit`, `pestphp/pest`, `mockery/mockery`. PHPUnit version drives whether attributes or annotations are idiomatic.
2. **PHPUnit 10+ skeleton.**
   ```php
   use PHPUnit\Framework\TestCase;
   use PHPUnit\Framework\Attributes\Test;
   use PHPUnit\Framework\Attributes\DataProvider;

   final class RefundParserTest extends TestCase
   {
       #[Test]
       public function rejects_empty_input(): void
       {
           $this->expectException(RefundError\Empty::class);
           (new RefundParser())->parseRefund('');
       }

       #[Test]
       #[DataProvider('amountToTier')]
       public function classifies_amount(int $amount, string $expected): void
       {
           $this->assertSame($expected, classify($amount));
       }

       public static function amountToTier(): array
       {
           return [
               [0,    'invalid'],
               [1,    'micro'],
               [100,  'standard'],
           ];
       }
   }
   ```
3. **Pest skeleton (when Pest is the existing idiom).**
   ```php
   it('rejects empty input', function () {
       expect(fn() => parseRefund(''))->toThrow(RefundError\Empty::class);
   });

   it('classifies amount', function (int $amount, string $expected) {
       expect(classify($amount))->toBe($expected);
   })->with([
       [0, 'invalid'],
       [1, 'micro'],
       [100, 'standard'],
   ]);
   ```
4. **Mocking.** Mockery (`Mockery::mock(Interface::class)`) over PHPUnit's `createMock` when you need spy-like flexibility; PHPUnit's built-in mocks for simple cases.
5. **Snake-case method names** are conventional in PHPUnit tests; Pest uses `it('description', fn() => …)` instead.
6. **Time.** Inject a `ClockInterface` (PSR-20) and replace with `Clock\FrozenClock` (`symfony/clock`) in tests.
7. **HTTP.** Symfony HTTP Client or Guzzle both ship a `MockHttpClient` / `MockHandler`; avoid hitting real endpoints.

## Quality bar

- One behavior per `#[Test]` / `it` block.
- DataProviders for parameter spaces; not loops with multiple assertions.
- Mockery `shouldReceive(...)->andReturn(...)` to script collaborators; `andThrow` for failure cases.
- No global state mutated; `setUp` resets.

## Anti-patterns to avoid

- `setUp` that mutates statics. Cross-test contamination.
- Asserting via `print_r` + visual inspection in a CI log.
- A test method named `testFoo1` / `testFoo2`. Name the behavior.
- Ignoring `expectException` and catching manually. The expectation must come before the call.
