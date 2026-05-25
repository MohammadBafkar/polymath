---
plugin: polymath-research
agent: research-scout
scenario: official-tool-boundary
baseline_prompt: "Decide whether Polymath should keep language and connector plugins or defer to official tools."
baseline_misses:
  - "Treats official docs, official MCPs, and Polymath skills as interchangeable instead of separating ownership."
  - "Makes a catalog decision without requiring primary-source evidence for each connector or language plugin."
agent_expected_findings:
  - "Build an inventory that maps each connector/language plugin to an official MCP, official docs, LSP, CLI, or missing upstream capability."
  - "Classify Polymath value as workflow shape, critique, safety checks, or artifact discipline; remove generic factual duplication."
  - "Require primary-source links before promoting any connector or language plugin beyond experimental."
decision_relevance: "This prevents Polymath from competing with official tools where it should compose them instead."
---

# Evidence Notes

The agent is justified only if it changes the decision from broad ownership to
explicit source-of-truth boundaries.
