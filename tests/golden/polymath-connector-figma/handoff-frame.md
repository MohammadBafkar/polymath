---
plugin: polymath-connector-figma
scenario: handoff-frame
expect:
  invoked:
    - polymath-connector-figma:design-spec-handoff
  output_matches:
    - "(node-id|frame)"
    - "(token|color/|text/|space/)"
    - "(missing|state)"
timeout_seconds: 90
---

# Prompt

> Produce a build-ready spec for the Figma frame at
> https://www.figma.com/file/abc123?node-id=42:108 — web target,
> design system acme-ds-v3.

Use polymath-connector-figma:design-spec-handoff.

# Acceptance

- Spec names component instances + variants.
- Tokens identified by name (not raw values).
- Missing states explicitly listed (not silently dropped).
- Copy strings are verbatim; missing ones flagged rather than invented.
