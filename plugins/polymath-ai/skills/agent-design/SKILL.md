---
name: agent-design
description: Design an LLM agent — architecture (ReAct, plan-execute, reflexion), tool/function-calling contract, memory, multi-agent orchestration, and the stop/budget conditions.
---

# agent-design

> An agent is a loop around a model with tools and a stopping rule. Most agent failures are a missing stop condition, a vague tool contract, or unbounded context — design those first.

## When to use

- Building a feature where the model must call tools, take multiple steps, or coordinate sub-agents.
- An existing agent loops forever, burns tokens, or calls the wrong tool.
- A workflow invokes `polymath-ai:agent-design`.

Not this when: you are shaping a single prompt's wording and output — that is `polymath-ai:prompt-engineer`. For retrieval design, `polymath-ai:rag-design`. For the eval harness, `polymath-ai:eval-plan`. For the input/output safety layer, `polymath-ai:llm-guardrails`.

## Inputs

- The task the agent performs and the tools/actions available.
- Latency, cost, and autonomy constraints (can it act without confirmation?).

## Procedure

0. **Decide whether it needs to be an agent.** If the steps are known in advance, a deterministic workflow — a prompt chain, a router, parallel calls with a merge, or an evaluator-optimizer loop with a fixed iteration cap — is cheaper, faster, and easier to test. Choose an open-ended agent loop only when the path genuinely depends on what the model discovers along the way, and say which it is.
1. **Pick the control pattern by task shape**:
   - *Single-shot + tools* — one model call that may call tools; simplest, use when one round suffices.
   - *ReAct (reason→act→observe loop)* — interleaved reasoning and tool calls until done; the default for multi-step tool use.
   - *Plan-then-execute* — plan the steps up front, then execute; better for long tasks where mid-course replanning is costly.
   - *Reflexion / critic* — a verify step that critiques and retries; add only where correctness justifies the extra calls.
   - *Multi-agent* (orchestrator + sub-agents) — justify the orchestration cost; a single agent with well-scoped tools is often simpler. Sub-agents earn their place by isolating context: give each a minimal brief and have it return a condensed result, not its transcript.
2. **Define the tool contract** per tool: name, when to use (and when not), typed inputs/outputs, side-effect class (read-only vs mutating), idempotency, and failure behavior. Ambiguous tool descriptions are the top cause of wrong tool calls. Keep the toolset small — selection accuracy drops as near-duplicate tools pile up; load rarely used tools on demand.
3. **Return errors as tool results.** A failed call returns a structured, model-readable error (what failed, whether retrying can help, what to try instead) — not an exception that kills the loop or a silent empty result.
4. **Design memory** explicitly: what is in the working context each turn, what is summarized, what is retrieved on demand, and the context-window budget. Unbounded transcript growth is a latency/cost bug waiting to happen (each turn re-sends the history).
5. **Set hard stop conditions**: max steps, max tokens/cost, wall-clock, and a "no-progress" detector (same tool + same args repeated, no new information). Every loop must terminate by construction.
6. **Decide autonomy + human-in-the-loop**: which actions run freely (read-only), which require confirmation (mutating/irreversible). Map to a propose-vs-act policy. Mutating tools should be idempotent (accept a request ID) so a retried step can't double-apply.
7. **Treat tool output as untrusted input.** Web pages, documents, emails, and API responses the agent reads can carry injected instructions; scope each tool's privileges so a hijacked agent can't exceed the user's own authority (design the controls with `polymath-ai:llm-guardrails`).
8. **Plan failure handling**: tool errors, malformed tool args, and model refusals each get a recovery path (retry, reprompt, escalate, abort).
9. **Make it observable + evaluable**: trace each step (thought, tool, args, result, tokens). Evaluate trajectories as well as final answers — right tool, right args, no wasted or unsafe steps — and hand the success criteria to `polymath-ai:eval-plan`.

## Output

```text
Agent design: <agent name>

Shape:      agent loop (path depends on findings) | workflow (steps known)
Pattern:    ReAct, single agent — why: <reason>; rejected: multi-agent (<reason>)

Tools:
  name            when to use              side effect   idempotent   on failure
  search_orders   look up an order by id   read-only     n/a          error result: not_found | retryable
  issue_refund    after user confirmation  mutating      request_id   error result; never auto-retry

Memory:     last 6 turns verbatim + rolling summary; order data fetched on demand
            context budget: 24k tokens/turn
Stop:       ≤ 12 steps · ≤ $0.40 · ≤ 90 s · abort on 2 identical consecutive calls
Autonomy:   reads free; issue_refund requires explicit user confirmation
Untrusted:  order notes + email bodies → data only; agent cannot email out
Failures:   malformed args → reprompt once; tool 5xx → retry ×2 with backoff; refusal → escalate
Evals:      trajectory + outcome suite → polymath-ai:eval-plan
```

## Quality bar

- The workflow-vs-agent choice is explicit; an agent loop is justified by a path that genuinely can't be known in advance.
- Every loop has explicit, enumerated stop conditions — no "until done".
- Each tool states its side-effect class, idempotency, and confirmation requirement, and fails with a structured error result.
- Context growth is bounded (summarize/retrieve), with a stated token budget.
- Tool output is treated as untrusted; privileges are scoped so injection can't escalate.
- Evaluation covers trajectories, not only final answers.
