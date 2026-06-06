---
name: route
description: Choose the right Polymath workflow, skill, connector, agent, or external catalog for a user prompt; returns JSON with confidence, evidence, and alternatives.
---

# route

> Pick the smallest Polymath surface that fits the user's prompt and project context.

## When to use

- A user asks which Polymath plugin, skill, agent, connector, or workflow should handle a request.
- An agent sees a prompt that might match a Polymath workflow but the user did not name one.
- Several sibling skills could apply and choosing silently would be risky.
- A project-local `.polymath/project.yaml` or `.polymath/capabilities.yaml` might change the right provider.

## Routing Inputs

- The user's prompt and any attached file paths, URLs, ticket keys, diffs, or logs.
- Installed Polymath skill/command/agent descriptions already visible in context.
- If available, read `${CLAUDE_PLUGIN_DATA}/polymath-core/project-context.json`.
- For workflow candidates, read `../../../polymath-flows/data/workflow-index.min.json`; if two workflows tie, read `../../../polymath-flows/data/workflow-detect.json`.
- For provider-dependent work, read `.polymath/capabilities.yaml` or [`docs/CAPABILITIES.md`](../../../../docs/CAPABILITIES.md).

Do not bulk-load every `SKILL.md`. Load the chosen target's body only after routing.

## Procedure

1. **Honor explicit targets.** If the user names a plugin, skill, command, agent, or workflow, route there unless it is missing or unsafe.
2. **Classify the work shape.**
   - Multi-step SDLC arc with dependent artifacts or gates -> prefer a `polymath-flows` workflow.
   - One bounded artifact or procedure -> prefer a skill.
   - Service/tool action -> prefer a connector resolved through project capabilities.
   - Forked-context critique, panel, or deep research -> consider an agent.
   - Language/API fact or framework-specific implementation detail -> prefer official docs, LSPs, or external skill catalogs declared by the project.
3. **Use context signals.**
   - Paths like `docs/prds/**`, `docs/plans/**`, `docs/adrs/**`, incident URLs, PR URLs, package manifests, or diffs should influence routing.
   - Capability provider names (`jira`, `linear`, `github`, `datadog`, `sentry`, `pagerduty`) are evidence, not final routing by themselves.
4. **Break ties explicitly.**
   - If top candidates are within `0.10` confidence, return `route_type="clarify"` with one question.
   - If the user asks for "triage" without a tracker or URL, ask which issue tracker.
   - If a workflow fits but approval is required, return the workflow as a proposal, not an auto-start.
5. **Prefer the smaller surface.**
   - Do not route to a workflow for a single skill-shaped ask.
   - Do not route to a connector when official docs or an external catalog is the real source of truth.
   - Do not route to a thin experimental plugin when an installed beta workflow covers the same journey.

## Confidence

- `0.90-1.00`: user named the target or the prompt exactly matches a workflow trigger plus context.
- `0.75-0.89`: one strong candidate and weak alternatives.
- `0.60-0.74`: plausible candidate but missing context; include alternatives.
- `<0.60`: ask a clarifying question.

## Output

Return JSON only unless the user explicitly asks for prose:

```json
{
  "route_type": "workflow | skill | connector | agent | external | clarify",
  "target": "polymath-flows:run-workflow reviewPR",
  "confidence": 0.86,
  "evidence": [
    "prompt asks for multi-critic PR/diff review",
    "diff or PR URL is present"
  ],
  "alternatives": [
    "polymath-engineering:code-review",
    "polymath-security:owasp-review"
  ],
  "question": null,
  "next_action": "Propose the reviewPR workflow and wait for approval before running it."
}
```

For `route_type="clarify"`, `target` is `null`, `question` is one short question, and `alternatives` lists the competing targets.

## Examples

- "Review this PR for correctness, security, and missing tests" -> `workflow`, `polymath-flows:run-workflow reviewPR`.
- "Append a changelog entry for this diff" -> `skill`, `polymath-release:changelog`.
- "Triage this Jira ticket" -> `connector`, `polymath-connector-tracker:jira-triage`.
- "How do I use this framework API?" -> `external`, official docs or project-declared external skill catalog.
- "Help me decide between Postgres and DynamoDB" -> `workflow`, `polymath-flows:run-workflow decideUnderAmbiguity`, unless the user only wants a quick comparison.

## Anti-patterns

- Starting a workflow without confirmation.
- Loading many skill bodies just to choose one.
- Treating connector plugins as factual authorities when official MCPs/docs own the source data.
- Hiding uncertainty behind a low-confidence guess.
