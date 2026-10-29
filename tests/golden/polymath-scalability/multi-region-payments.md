---
plugin: polymath-scalability
scenario: multi-region-payments
expect:
  invoked:
    - polymath-scalability:multi-region-design
  output_matches:
    - "(RPO|RTO)"
    - "(home region|single-writer|conflict)"
    - "(failover|failback|fencing|split-brain)"
timeout_seconds: 120
---

# Prompt

> We need our payments API to survive a regional outage with RPO near zero for the ledger and RTO under 15 minutes, and EU data must stay in the EU. Should we go active-active?

Use polymath-scalability:multi-region-design.

# Acceptance

- Justifies multi-region against cheaper options.
- Per-data-class RPO/RTO and replication model.
- Hidden single-region dependencies and a rehearsal plan.
