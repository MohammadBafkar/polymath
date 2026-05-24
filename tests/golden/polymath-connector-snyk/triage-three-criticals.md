---
plugin: polymath-connector-snyk
scenario: triage-three-criticals
expect:
  invoked:
    - polymath-connector-snyk:triage-vulns
  output_matches:
    - "(REACHABLE|reachability)"
    - "(PATCH|DEFER|ACCEPT)"
    - "SNYK-"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Triage these three Snyk findings.

Use polymath-connector-snyk:triage-vulns.

1. SNYK-JS-LODASH-1234567 — lodash@4.17.20 — reachable (used in
   src/util/format.ts:42).
2. SNYK-JS-MINIMIST-2345678 — minimist@1.2.5 — transitive via gulp,
   NOT reachable.
3. SNYK-JS-MARKED-3456789 — marked@2.0.0 — devDependency only.

# Acceptance

- Each finding has a class (Exploitable+Reachable / Reachable / Not Reachable / Dev-only).
- Each has a concrete action (PATCH / DEFER / ACCEPT) and a date or version target.
- DEFER includes a re-evaluation date.
- ACCEPT (if used) requires `.snyk` policy entry with expiration. No "ignore until next release".
