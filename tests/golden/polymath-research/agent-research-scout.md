---
plugin: polymath-research
scenario: agent-research-scout
agent: research-scout
disable_tools: true
effort: low
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

> Use the polymath-research research-scout agent. Do not browse, inspect files,
> or call external tools; this fixture is an evidence-plan pass only. Keep the
> answer under 500 words.

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
