# Changelog — polymath-thinking

<!-- markdownlint-disable MD024 -->

## [0.8.0]

Thinking craft: brainstorm, 5-whys, pre-mortem, red-team.

### Skills

- **5-whys** — Investigate an incident or bug via the 5-whys technique — iterative root-cause drill-down; stop early if a system cause emerges before five iterations.
- **brainstorm** — Generate divergent options (≥10) for a problem before converging — quantity beats quality; not convergent down-selection or ranking (prioritize).
- **deliberate** — Run an iterative observe-frame-options-tradeoffs-risks-revise loop for a plan, design, doc, idea, or implementation; composes brainstorm, red-team, and pre-mortem.
- **first-principles** — Decompose a problem to first principles — strip to fundamentals, drop inherited assumptions, rebuild from bedrock; not option generation (brainstorm) or framing (problem-framing).
- **pre-mortem** — Frame the project as already failed and list the most plausible reasons why, so they can be mitigated before launch; not adversarial critique (red-team).
- **problem-framing** — Frame the problem before any solution — symptom vs root need, who/what/why, constraints, premature-solution bias. A problem statement, not options (brainstorm) or root-cause (5-whys).
- **red-team** — Critique a plan, design, or PRD adversarially — objections with the strongest case the proposer hasn't refuted; not pre-launch failures (pre-mortem).

### Commands

- **/deliberate** — Run a deliberation on a hard or ambiguous call before you commit; alias for polymath-thinking:deliberate.

### Subagents

- **architecture-critic** — Critique an ADR or design in a forked context; hunts invariants, failure modes, and cheaper alternatives the lead may miss.
