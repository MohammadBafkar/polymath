---
plugin: polymath-frontend
scenario: web-vitals-budget-mobile
expect:
  invoked:
    - polymath-frontend:web-vitals-budget
  output_matches:
    - "LCP"
    - "INP"
    - "CLS"
    - "median-mobile"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Set Web Vitals budgets for our checkout page.

Use the polymath-frontend:web-vitals-budget skill. Audience is
median-mobile. Current values: LCP 3.1s, INP 180ms, CLS 0.03.
The largest contentful element is the hero image (/img/hero.jpg,
220 KB JPEG, no priority hint, fetched after critical CSS).

# Acceptance

- A budget table includes LCP, INP, CLS with current vs budget and a status.
- The dominant LCP cost names the hero image and its specific properties.
- Exactly one "first-try fix" is recommended.
- The recommendation cites `fetchpriority` or `<link rel="preload">`.
