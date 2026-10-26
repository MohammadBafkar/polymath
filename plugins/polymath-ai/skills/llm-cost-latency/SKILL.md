---
name: llm-cost-latency
description: Cut LLM cost and latency — model routing/cascade, prompt caching, batching, streaming, context trimming, output-token control, and a per-request cost/latency budget.
---

# llm-cost-latency

> LLM spend is dominated by tokens × model tier × call count. Most savings come from sending fewer tokens to a smaller model less often — measure the request first, then cut the biggest line.

## When to use

- An LLM feature is too slow or too expensive, or you are sizing one before launch.
- You need a per-request cost/latency budget and a path to hit it.
- A workflow invokes `polymath-ai:llm-cost-latency`.

Not this when: this is a non-LLM service's latency/cost — that is `polymath-performance:backend-tail-latency` / `perf-budget`. For prompt wording quality, `polymath-ai:prompt-engineer`.

## Inputs

- The current model, prompt sizes (system + context + output), call pattern, and measured cost/latency.
- The quality bar the cheaper path must still clear.

## Procedure

1. **Account the request**: break cost into input tokens, output tokens, and model tier; break latency into time-to-first-token, generation time, and tool/round-trips. Optimize the largest contributor, not the easiest.
2. **Right-size the model**: route easy cases to a smaller/cheaper model and escalate only hard ones (a cascade). Reserve the top tier for tasks that measurably need it — verify with `polymath-ai:eval-plan` that the cheaper model still passes.
3. **Cut input tokens**: trim/compress context, retrieve less but better (tune `rag-design`), drop stale transcript, and reuse a stable system prompt to exploit **prompt caching** (order prefix-stable content first; check the provider's minimum cacheable length, cache TTL, and the write premium vs read discount, then measure the cache-hit rate). In agent loops, input cost grows with every turn because the history is re-sent — caching and summarization matter most there.
4. **Cut output tokens**: ask for the minimal format (structured/short), cap max output, and stop sequences — output tokens are priced several times higher than input and dominate generation latency.
5. **Cut call count**: batch independent requests (asynchronous batch APIs trade latency for a large discount on non-interactive work), collapse multi-call chains where one call suffices, and cache deterministic results.
6. **Hide latency**: stream tokens to first paint; parallelize independent tool calls; precompute where the input is known ahead of time.
7. **Set the budget + tripwire**: a per-request cost and p95 latency target, with an alert when exceeded — the same discipline as a perf budget.

## Output

- A one-page plan: the per-request cost/latency breakdown, the model-routing/cascade decision, the input/output/call-count cuts with expected savings, caching/streaming plan, and the budget + tripwire.

## Quality bar

- The optimization targets the measured largest cost/latency contributor, not a guess.
- Any model downgrade is gated by an eval that shows quality holds.
- Prompt caching is exploited via prefix-stable prompt ordering where the provider supports it.
- A per-request budget + tripwire is named.
