---
plugin: polymath-learning
scenario: explain-cap-theorem-tiered
expect:
  invoked:
    - polymath-learning:explain
  output_matches:
    - "(undergrad|tier)"
    - "(analogy)"
    - "(break|limit)"
  not_invoked:
    - polymath-learning:code-walkthrough
timeout_seconds: 90
---

# Prompt

> Explain CAP theorem at the curious-undergrad tier.

Use polymath-learning:explain. Concept: CAP theorem. Audience tier:
curious-undergrad. Pick the analogy and immediately state where it breaks.

# Acceptance

- Tier named at the top.
- One analogy used.
- "Where the analogy breaks" line is present and specific.
- One terminology bridge (e.g. "partition" → relatable term).
- Single concept; doesn't drift into PACELC or consensus.
