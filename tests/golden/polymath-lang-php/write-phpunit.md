---
plugin: polymath-lang-php
scenario: write-phpunit
expect:
  invoked:
    - polymath-lang-php:write-phpunit-test
  output_matches:
    - "(#\\[Test\\]|@test|it\\()"
    - "(DataProvider|with\\(|->with)"
    - "(expectException|toThrow|RefundError)"
timeout_seconds: 60
---

# Prompt

> Write PHPUnit tests for RefundParser::parseRefund that throws
> RefundError\\Empty on empty input. Include a dataProvider for 3 valid amounts.

Use polymath-lang-php:write-phpunit-test.

# Acceptance

- #[Test] attribute or @test annotation depending on PHPUnit version.
- DataProvider (or Pest with()) for parameter space.
- expectException or toThrow for the empty input case.
- One behavior per test method.
