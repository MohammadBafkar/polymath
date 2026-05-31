---
plugin: polymath-i18n
scenario: i18n-audit-react-app
expect:
  invoked:
    - polymath-i18n:i18n-audit
  output_matches:
    - "hardcoded"
    - "plural"
  not_invoked:
    - polymath-design:a11y-audit
timeout_seconds: 90
---

# Prompt

> We want to launch our React app in German and Arabic. Audit it for
> internationalization readiness.

Use polymath-i18n:i18n-audit.

# Acceptance

- Hardcoded strings + non-locale-aware formatting flagged with locations.
- Pluralization judged against ICU; RTL/bidi + text expansion assessed for Arabic/German.
- A fallback chain and pseudolocalization-in-CI recommendation included.
