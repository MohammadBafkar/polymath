---
plugin: polymath-security
skill: stride-threat-model
trigger_prompts:
  - "threat model the new login endpoint using STRIDE"
  - "produce a STRIDE threat model for our payment refund flow"
  - "walk through the spoofing/tampering/repudiation/info-disclosure/DoS/privilege-escalation risks on this service"
must_invoke:
  - polymath-security:stride-threat-model
allow_invoke:
  - polymath-thinking:red-team
  - polymath-thinking:pre-mortem
  - polymath-core:*
---

# Why this test exists

STRIDE is the specific methodology the skill teaches. The third prompt
spells out the categories without naming STRIDE, to catch
over-fitting.
