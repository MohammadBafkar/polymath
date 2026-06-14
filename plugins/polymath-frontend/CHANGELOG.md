# Changelog — polymath-frontend

<!-- markdownlint-disable MD024 -->

## [0.8.0]

Frontend craft: component contracts, Web Vitals budgets, bundle bloat hunts.

### Skills

- **bundle-analyze** — Audit a JavaScript bundle for the biggest bytes and propose the cheapest cut; uses the bundler's report rather than guessing.
- **component-design** — Design a UI component's contract — props, state, side effects, a11y, and the smallest set of tests that locks the contract.
- **i18n-audit** — Audit software for i18n readiness — hardcoded strings, locale date/number/currency formatting, ICU plurals, pseudolocalization, RTL/bidi, fallback chain. Internationalization, not UX copywriting.
- **web-vitals-budget** — Set Core Web Vitals budgets (LCP, INP, CLS) per route and propose the cheapest fix path when one is over budget. Web routes only; not mobile (mobile-perf) or backend (perf-budget).
