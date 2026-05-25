---
plugin: polymath-thinking
agent: architecture-critic
scenario: adr-rate-limit-store
baseline_prompt: "Review an ADR that chooses Redis for /login rate-limit counters after the lead already favored Redis."
baseline_misses:
  - "Partition policy is unstated: login can fail open and weaken abuse controls, or fail closed and lock out legitimate users."
  - "Counter keys may encode IP, account, or tenant data without a retention or privacy boundary."
agent_expected_findings:
  - "Force an explicit fail-open/fail-closed policy for Redis outage and regional partition cases."
  - "Demand a keying and retention strategy that avoids unnecessary PII and supports abuse investigation."
  - "Compare Redis against gateway-native rate limiting or a local token bucket fallback before accepting the ADR."
decision_relevance: "These findings change whether Redis is safe as the primary control or only acceptable behind a fallback/guardrail."
---

# Evidence Notes

The agent is justified only if it challenges the preferred store decision rather
than polishing the existing ADR. The review should make the rollback and outage
policy explicit before implementation.
