# Changelog — polymath-ai

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Added

- `eval-plan`: `scripts/winrate.py` — pairwise ship verdict from a Wilson score interval (ties excluded), plus the win count needed to ship; unit-tested. The skill's 114-of-200 rule now comes from the script, not mental arithmetic.

### Changed

- Every skill declares its **Mode** — 6 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `llm-cost-latency`, `llm-guardrails`: exact output shapes (per-request cost arithmetic with sourced prices; trust-boundary and propose-vs-authorize design).
- `prompt-engineer`: compare two structurally different drafts on the eval set before keeping one.

## [0.11.0]

### Changed

- `agent-design`: step 0 decides workflow vs agent before picking a loop; tool errors return as structured tool results; tool count/selection, idempotent mutating tools, untrusted tool output, sub-agent context isolation, and trajectory evals added; concrete Output shape.
- `eval-plan`: pairwise threshold is now a significance test (95% CI above 0.5 — e.g. ≥ 114/200), regression slices run k times against a measured noise floor, judge position/length/self-preference bias controls, held-out split, agentic trajectory scoring.
- `rag-design`: ACL-filtered retrieval first, context-before-question prompt order (long-context guidance), freshness/deletes, retrieved text treated as untrusted, retrieval evaluated separately (recall@k); long-context-with-caching named as the no-RAG alternative.
- `llm-guardrails`: injection detection framed as defense in depth; tools run with the end user's permissions; the private-data + untrusted-content + outbound-channel exfiltration path must be broken.
- `prompt-engineer`: native structured outputs over prompt-only JSON, reasons behind constraints, positive phrasing, reasoning room, eval loop; dropped the unsupported "expert framing changes nothing" claim.
- `llm-cost-latency`: cache write premium/TTL/hit rate, agent-loop history growth, batch APIs; clarified output-token pricing.

## [0.8.0]

AI craft: prompt engineering, RAG, eval design, agent design, LLM guardrails, cost/latency tuning.

### Skills

- **agent-design** — Design an LLM agent — architecture (ReAct, plan-execute, reflexion), tool/function-calling contract, memory, multi-agent orchestration, and the stop/budget conditions.
- **eval-plan** — Design an evaluation for an LLM feature — task type, dataset shape, automated vs human rubric, regression set, decision threshold.
- **llm-cost-latency** — Cut LLM cost and latency — model routing/cascade, prompt caching, batching, streaming, context trimming, output-token control, and a per-request cost/latency budget.
- **llm-guardrails** — Design guardrails for an LLM feature — input validation, prompt-injection defenses, output filtering/schema validation, allow-deny policy, and human-in-the-loop gates.
- **prompt-engineer** — Author or improve an LLM prompt — clarify task, constrain output shape, place worked examples, bound calibration; vendor-agnostic.
- **rag-design** — Design a retrieval-augmented generation pipeline — chunking, embeddings, retriever, reranker, prompt assembly — with the right cuts for the use case.
