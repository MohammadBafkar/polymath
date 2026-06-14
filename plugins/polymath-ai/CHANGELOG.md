# Changelog — polymath-ai

<!-- markdownlint-disable MD024 -->

## [0.8.0]

AI craft: prompt engineering, RAG, eval design, agent design, LLM guardrails, cost/latency tuning.

### Skills

- **agent-design** — Design an LLM agent — architecture (ReAct, plan-execute, reflexion), tool/function-calling contract, memory, multi-agent orchestration, and the stop/budget conditions.
- **eval-plan** — Design an evaluation for an LLM feature — task type, dataset shape, automated vs human rubric, regression set, decision threshold.
- **llm-cost-latency** — Cut LLM cost and latency — model routing/cascade, prompt caching, batching, streaming, context trimming, output-token control, and a per-request cost/latency budget.
- **llm-guardrails** — Design guardrails for an LLM feature — input validation, prompt-injection defenses, output filtering/schema validation, allow-deny policy, and human-in-the-loop gates.
- **prompt-engineer** — Author or improve an LLM prompt — clarify task, constrain output shape, place worked examples, bound calibration; vendor-agnostic.
- **rag-design** — Design a retrieval-augmented generation pipeline — chunking, embeddings, retriever, reranker, prompt assembly — with the right cuts for the use case.
