---
name: llm-cost-latency
description: Cut LLM cost and latency — model routing/cascade, prompt caching, batching, streaming, context trimming, output-token control, and a per-request cost/latency budget.
---

# llm-cost-latency

> LLM spend is dominated by tokens × model tier × call count. Most savings come from sending fewer tokens to a smaller model less often — measure the request first, then cut the biggest line.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

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

```text
LLM cost/latency plan: support-reply drafting

Per request (measured, 1,000-request sample):
  input  6,200 tok (system 1,800 · retrieved 3,900 · history 500) × $3.00/M = $0.0186
  output   450 tok × $15.00/M                                              = $0.0068
  total  $0.0254/request · p95 latency 7.8 s (TTFT 1.1 s, generation 6.7 s)
  largest line: retrieved context (61% of input cost)

Cuts (expected)
  1. retrieve top-4 not top-10 chunks (eval: answer quality 91% → 90%, within noise)   −$0.0070
  2. prompt caching on the 1,800-token system prefix (hit rate 85% measured in staging)  −$0.0041
  3. cap output at 300 tokens + "3 short paragraphs" format                             −$0.0023, −2.2 s p95
  4. route "FAQ-match" requests (38%) to the small tier after eval-plan passes on that slice
Streaming: on — first paint at TTFT
Budget + tripwire: ≤ $0.015/request and p95 ≤ 5 s; alert at 120% of either for 1 h
```

Prices are the provider's current list prices, cited with the date checked; an unknown price is `[TBD: price]`, never remembered.

## Quality bar

- The optimization targets the measured largest cost/latency contributor, not a guess.
- Any model downgrade is gated by an eval that shows quality holds.
- Prompt caching is exploited via prefix-stable prompt ordering where the provider supports it.
- A per-request budget + tripwire is named.
