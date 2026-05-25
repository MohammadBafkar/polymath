---
plugin: polymath-research
scenario: agent-research-scout
agent: research-scout
expect:
  invoked:
    - research-scout
  output_matches:
    - "(official|primary source|source of truth)"
    - "(MCP|docs|LSP|CLI)"
    - "(workflow|critique|safety|artifact)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 120
---

# Prompt

> Use the polymath-research research-scout agent.

Question: Should Polymath keep `polymath-lang-XX` and
`polymath-connector-XX` plugins, or defer to official tools? Produce an
evidence plan that separates official source-of-truth behavior from Polymath's
workflow-specific value.

# Acceptance

- The agent separates official docs/MCP/LSP/CLI ownership from Polymath-owned
  workflow shape.
- The output requires primary-source evidence before promotion.
- The output identifies which plugin categories should stay experimental until
  evidence exists.
