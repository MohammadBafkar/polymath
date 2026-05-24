# polymath-lang-php

PHP craft for the Polymath marketplace.

## What it ships

- Skills:
  - `write-phpunit-test` — PHPUnit 10+ attributes (`#[Test]`, `#[DataProvider]`), Pest patterns, Mockery for collaborators, PSR-20 clock injection.
  - `audit-composer-json` — PHP requirement, pin discipline, `roave/security-advisories`, autoload sanity, require/require-dev separation.
- Commands: `/polymath-lang-php:test`, `/polymath-lang-php:audit`.

## Installation

```bash
claude plugin install polymath-lang-php@polymath
```

## Dependencies

- `polymath-core`, `polymath-engineering`

## License

Apache-2.0.
