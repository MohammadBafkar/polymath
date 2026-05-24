---
plugin: polymath-ai
scenario: prompt-classifier-design
expect:
  invoked:
    - polymath-ai:prompt-engineer
  output_matches:
    - "JSON"
    - "category"
    - "abstain|abstention|low|don't know|I don't know"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Author a classifier prompt for inbound support messages.

Use polymath-ai:prompt-engineer. The model must classify each
message into exactly one of [billing, technical, account, abuse,
other] and output strict JSON only. It should be able to abstain
(return "other" with low confidence) rather than guess.

# Acceptance

- The prompt pins JSON-only output with a named schema.
- The list of categories is explicit and closed.
- A calibration / abstention line is present.
- Worked examples cover billing, technical, and abstention.
- No "you are a helpful assistant" filler.
