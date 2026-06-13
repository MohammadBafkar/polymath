# polymath-ai

AI craft for the Polymath marketplace. Vendor-agnostic; principles apply across Anthropic, OpenAI, open models.

## What it ships

- Skills:
  - `prompt-engineer` — author/improve a single prompt's wording and output shape.
  - `rag-design` — retrieval architecture (chunking, embeddings, reranking, eval).
  - `eval-plan` — design the offline/online eval harness for an LLM feature.
  - `agent-design` — agent control pattern (ReAct, plan-execute, reflexion), tool contract, memory, stop/budget conditions, multi-agent orchestration.
  - `llm-guardrails` — input validation, prompt-injection defense, output filtering/schema validation, propose-vs-authorize action policy, fail-closed.
  - `llm-cost-latency` — model routing/cascade, prompt caching, token trimming, batching, streaming, and a per-request cost/latency budget.

## Installation

```bash
claude plugin install polymath-ai@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
