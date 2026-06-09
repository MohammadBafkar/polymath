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
    - "(?i)claim ledger"
    - "(?i)(verified|inferred|unverified|needed)"
    - "(?i)next test"
  not_invoked:
    - polymath-product:prd
timeout_seconds: 120
---

# Prompt

> Use the polymath-research research-scout agent.

We're considering replacing our self-hosted Postgres with a managed vendor
offering to cut ops load. Don't gather live evidence — give me an evidence
plan: which primary sources to check and what would change the decision.

# Acceptance

- The agent returns a structured claim ledger rather than a prose opinion —
  something a same-input no-agent baseline tends not to produce.
- Each claim carries a status (verified / inferred / unverified / needed).
- Because the prompt asks for a plan (not live gathering), unsupported claims
  are marked `unverified` or `needed` rather than asserted.
- The output ends with the cheapest next test that would change the decision.
