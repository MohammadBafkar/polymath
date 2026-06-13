# Changelog — polymath-ai

## [0.7.0]

### Added

- Three skills closing the agent/production-LLM gap (whetstone-coverage program, P2):
  `agent-design` (control patterns, tool contract, memory, stop/budget conditions,
  multi-agent), `llm-guardrails` (input validation, prompt-injection defense, output
  validation, propose-vs-authorize, fail-closed), and `llm-cost-latency` (model
  routing/cascade, prompt caching, token/call-count cuts, per-request budget). Each
  declares a soft-tier `routing.yaml`. LLM-security *review* lands separately in
  `polymath-security` (P4).

## [0.1.0]

### Added

- Initial v0.1 components: `prompt-engineer`, `rag-design`, `eval-plan` skills.
