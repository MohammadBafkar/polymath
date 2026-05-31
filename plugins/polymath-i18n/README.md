# polymath-i18n

Internationalization craft: treat i18n as an architecture property and find where the code assumes one language, region, or text direction before a locale launch does.

## What it ships

- Skills: `i18n-audit` — audit for hardcoded strings, locale-aware date/number/currency formatting, ICU plurals/gender, text expansion, RTL/bidi, the fallback chain, and a pseudolocalization-in-CI workflow.

## Why it exists

The audit found localization-i18n was the one SDLC phase with **zero** coverage. This plugin adds an i18n-readiness audit; it complements `polymath-design:a11y-audit` (accessibility) without overlapping it.

## Installation

```bash
claude plugin install polymath-i18n@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
