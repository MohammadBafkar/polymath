---
plugin: polymath-frontend
skill: i18n-audit
trigger_prompts:
  - "audit our app for internationalization before we launch in German and Arabic"
  - "check for hardcoded strings and RTL issues"
  - "are we ready to localize this product"
must_invoke:
  - polymath-frontend:i18n-audit
allow_invoke:
  - polymath-frontend:*
  - polymath-design:*
  - polymath-frontend:*
  - polymath-core:*
forbidden_prompts:
  - "audit this UI for accessibility against WCAG"
  - "improve the microcopy on the signup button"
---

# Why this test exists

i18n/localization/RTL/hardcoded-string phrasings route here. Forbidden
prompts guard against `polymath-design:a11y-audit` (accessibility) and UX copywriting.
