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

Not this when: you are shaping a single prompt's wording and output — that is `polymath-ai:prompt-engineer`. For retrieval design, `polymath-ai:rag-design`. For the eval harness, `polymath-ai:eval-plan`.

## Inputs

- The task the agent performs and the tools/actions available.
- Latency, cost, and autonomy constraints (can it act without confirmation?).

## Procedure

1. **Pick the control pattern by task shape**:
   - *Single-shot + tools* — one model call that may call tools; simplest, use when one round suffices.
   - *ReAct (reason→act→observe loop)* — interleaved reasoning and tool calls until done; the default for multi-step tool use.
   - *Plan-then-execute* — plan the steps up front, then execute; better for long tasks where mid-course replanning is costly.
   - *Reflexion / critic* — a verify step that critiques and retries; add only where correctness justifies the extra calls.
   - *Multi-agent* — separate agents with distinct roles/tools; justify the orchestration cost (a single agent with more tools is often simpler).
2. **Define the tool contract** per tool: name, when to use, typed inputs/outputs, side-effect class (read-only vs mutating), and the failure/needs-confirmation behavior. Ambiguous tool descriptions are the top cause of wrong tool calls.
3. **Design memory** explicitly: what is in the working context each turn, what is summarized, what is retrieved on demand, and the context-window budget. Unbounded transcript growth is a latency/cost bug waiting to happen.
4. **Set hard stop conditions**: max steps, max tokens/cost, wall-clock, and a "no-progress" detector. Every loop must terminate by construction.
5. **Decide autonomy + human-in-the-loop**: which actions run freely (read-only), which require confirmation (mutating/irreversible). Map to a propose-vs-act policy.
6. **Plan failure handling**: tool errors, malformed tool args, and model refusals each get a recovery path (retry, reprompt, escalate, abort).
7. **Make it observable + evaluable**: trace each step (thought, tool, args, result); hand the success criteria to `polymath-ai:eval-plan`.

## Output

- A one-page agent design: control pattern + rationale, the tool contract table, the memory/context-budget plan, stop/budget conditions, the autonomy/HITL policy, and the failure-recovery paths.

## Quality bar

- Every loop has explicit, enumerated stop conditions — no "until done".
- Each tool states its side-effect class and confirmation requirement.
- Context growth is bounded (summarize/retrieve), with a stated token budget.
- The control pattern is the simplest that fits — multi-agent is justified, not assumed.
