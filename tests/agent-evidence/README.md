# Agent evidence

Agents are allowed only when forked context is expected to find something a
same-context lead is likely to miss. Each agent evidence file records the
baseline prompt, the expected baseline misses, and the findings the agent must
surface before the agent can be promoted beyond experimental use.

These files are not a substitute for live Claude fixture runs. They are the
reviewable contract that live runs must satisfy.

Required frontmatter:

```yaml
plugin: polymath-thinking
agent: architecture-critic
scenario: adr-cache-store
baseline_prompt: "Review this ADR without using a subagent."
baseline_misses:
  - "Failure mode the same-context lead often misses."
agent_expected_findings:
  - "Finding the forked-context agent must surface."
decision_relevance: "Why the delta changes the decision."
```
