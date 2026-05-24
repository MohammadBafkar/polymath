---
plugin: polymath-writing
scenario: adr-for-rate-limit-store
expect:
  invoked:
    - polymath-writing:adr
  artifacts:
    - "docs/adrs/0001-rate-limit-store.md"
  output_matches:
    - "(Context|Decision|Consequences|Alternatives)"
  not_invoked:
    - polymath-writing:rfc
timeout_seconds: 90
---

# Prompt

> Write an ADR for the rate-limit store choice.

Use polymath-writing:adr. Title: "Use Redis for rate-limit store".
The team is choosing between in-memory (per-instance), Redis (shared
across instances), and Postgres (overkill). Decision: Redis.

# Acceptance

- docs/adrs/NNNN-rate-limit-store.md exists with ADR frontmatter
  (artifact: ADR, status proposed/accepted, deciders set).
- All sections present: Status, Context, Decision, Consequences,
  Alternatives considered.
- At least two alternatives listed with concrete rejection reasons.
- Consequences section includes negatives (not just positives).
