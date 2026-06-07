---
prompt: "Draft an RFC for the new auth service and put it in docs/rfcs/."
must_appear:
  - "polymath-writing:rfc"
---
A skill that opted into deterministic dispatch purely by adding a routing.yaml
sidecar (no change to route-hint.py or any central table). Proves Phase 1
widening: the 1-of-N narrowing now works for skills, not just workflows.
