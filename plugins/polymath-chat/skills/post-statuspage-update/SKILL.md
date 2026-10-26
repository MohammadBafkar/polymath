---
name: post-statuspage-update
description: Post a customer-facing Statuspage incident update — maps internal severity to public status, scopes components, and re-writes the comms body for customers.
---

# post-statuspage-update

> Translate an internal incident update into a public Statuspage post. Output is the posted incident ID + update ID so subsequent updates thread under the same incident.

> **MCP binding (read before any tool call):** if your host has a `statuspage` MCP server, use its tools for this skill's data access. Check your own tool list — it may be registered under another name (a Claude Code connector appears as `mcp__claude_ai_<Name>__*`). Tool names differ between servers: use the closest match, and say so when the server is read-only. Never install or start a second copy. If there is none, work without MCP tool calls (give the user the rewritten body and the field values to enter in the Statuspage UI) and ask before suggesting an install.

## When to use

- `polymath-incident:comms-update` produced an *internal* update and the incident is sev1/sev2 (customer-visible).
- An incident's impacted scope changed and the public components need re-mapping.
- The incident moves between phases (investigating → identified → monitoring → resolved) and the public page must reflect it.

## Inputs

- Incident ID (required) — Polymath/internal identifier; used to dedupe a Statuspage incident.
- Internal comms body (required) — produced by `polymath-incident:comms-update`.
- Severity (required) — one of `sev1`, `sev2`, `sev3`. Drives the status mapping.
- Affected component IDs (required) — Statuspage component IDs, not names. Resolve via `components.list`.
- Phase (required) — one of `investigating`, `identified`, `monitoring`, `resolved`. Drives the Statuspage `status` field.

## Procedure

1. **Resolve components.** Call `components.list` and map each affected internal service to its public component ID. Refuse to post if any mapping is missing (silently skipping components misleads customers).
2. **Map severity → impact, and each affected component's status.**
   - sev1 → impact `critical`; components `major_outage` (or `partial_outage` if only some customers are down)
   - sev2 → impact `major`; components `partial_outage` or `degraded_performance`
   - sev3 → impact `minor`; components `degraded_performance` (only post sev3 if customers are visibly affected)
3. **Re-write the body for customers.** Strip internal jargon (service codenames, ticket IDs, on-call handles). Keep three sections: **What's happening**, **Who's affected**, **Next update at HH:MM TZ**.
4. **Get explicit approval — this is public.** Show the exact customer-facing body, status, impact, and component statuses to the incident commander / comms lead and wait for a yes. Never publish to a status page on inference alone.
5. **Find or create the incident.**
   - If `docs/incidents/<id>-statuspage.json` (step 8's artifact) already holds a Statuspage incident ID, update that incident.
   - Otherwise list unresolved Statuspage incidents and match by name before calling `incidents.create` — a retry after a timeout must not open a second public incident.
6. **Post the update** via `incidents.update` with `status` = phase, `impact` = mapped severity, `body` = the rewritten body, and `component_ids` / component statuses for affected components.
7. **On `resolved`** — set status `resolved`, set all affected components back to `operational`, and write the final post-resolution body (cause summary at a level customers can read; never raw stack traces or PII).
8. **Return the incident + update IDs** and save them as step artifacts (`docs/incidents/<id>-statuspage.json`).

## Output

```text
post-statuspage-update

Incident:    2026-09-refund-async (Statuspage id: abc123)
Phase:       monitoring
Impact:      major
Components:  refund-api (cmp_001), refund-worker (cmp_004)
Update id:   upd_5678
Public URL:  https://status.example.com/incidents/abc123
```

## Quality bar

- Nothing published without explicit human approval of the exact text.
- Component IDs resolved (no name-based posting).
- Severity → impact mapping is explicit.
- Body strips internal codenames + ticket IDs.
- On `resolved`, components are flipped back to `operational` — leaving them degraded is a common post-incident leak.

## Anti-patterns to avoid

- Posting the raw internal comms body to the public page. Customers do not need ticket IDs or service codenames.
- Creating a new Statuspage incident per update instead of updating the existing one. Floods the page and breaks RSS subscribers.
- Setting impact `none` because "it's almost over". If it's posted publicly, it had impact — record it honestly.
- Forgetting to flip components back to `operational` on resolution. Dashboards keep showing red after the fact.
