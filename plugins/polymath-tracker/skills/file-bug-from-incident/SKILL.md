---
name: file-bug-from-incident
description: File tracker bug tickets from a postmortem's action items — one per action, severity/priority mapped from incident sev, postmortem updated with the keys. Provider-agnostic (Jira or Linear).
---

# file-bug-from-incident

> Convert one incident's findings into one or more tracker tickets — one per
> discrete action item, each independently actionable. Works against whichever
> issue tracker the project configures (Jira or Linear).

## When to use

- A postmortem (from `polymath-incident:postmortem-blameless`) produced action items.
- A sev2/sev1 needs follow-up tickets before closing.
- A `respondToIncident` / `incidentRetroToActions` workflow's tickets step runs,
  resolving `${capabilities.issue_tracker.plugin}:file-bug-from-incident` here.

## Resolve the provider first

Read `${capabilities.issue_tracker.provider}` (or infer from which credentials
are configured: `jira*` → Jira, `linearApiKey` → Linear). The provider decides
the create tool and the priority vocabulary:

| Provider | Create tool | Sev → field |
| --- | --- | --- |
| Jira | `jira_create_issue` | severity: sev1→Critical, sev2→High, sev3→Medium, sev4→Low |
| Linear | `issue.create` (team-scoped) | priority: sev1→Urgent, sev2→High, sev3→Medium, sev4→Low |

If neither set of credentials is present, stop and say which to configure.

## Inputs

- The postmortem markdown.
- Jira: a mapping of code areas → Jira components.
- Linear: the team identifier (slug or ID — required; Linear issues are team-scoped).

## Procedure

1. **Parse** the postmortem's "Action items" section. Each row is a candidate ticket.
2. **For each action that is a bug:**
   - Title: imperative + concrete (e.g. "Add burn-rate alert at 6h window for refund SLO").
   - Description: link the postmortem, summarize the root cause in 2–3 sentences,
     paste the relevant timeline rows, attach the dashboard / log URLs.
   - Severity / priority: map from incident sev per the table above. Allow an
     explicit override; a silent downgrade requires a comment.
   - Routing: Jira → component by code area; Linear → component/area labels in
     the team's vocabulary.
   - Due date: from the postmortem's action-item row. "TBD" is rejected.
   - Owner/assignee: a specific person from the team named in the postmortem
     (not a team name); if "TBD", file to the on-call rotation and add a
     "@owner please confirm ownership" comment.
3. **Create** one ticket per action via the provider's create tool, capturing
   the returned key/identifier (e.g. `PROJ-481`, `ENG-89`).
4. **Link back:** update the postmortem's action-items table with each key + URL
   so the trail is bidirectional.

## Quality bar

- One ticket per discrete action item; never an umbrella "improve reliability".
- Severity/priority maps consistently from incident sev — no silent downgrades.
- Due date is set; "TBD" is not acceptable for post-incident action items.
- Postmortem updated with the resulting keys.
- Linear only: file into the action-item owner's team; cross-team work needs an
  explicit handoff (Linear is team-scoped).

## Anti-patterns to avoid

- Filing one umbrella ticket instead of discrete, actionable ones.
- Filing without a specific assignee ("the ENG team will handle it").
- Combining two action items into one ticket to save effort — they were discrete
  in the postmortem; keep them discrete.
- Skipping the postmortem-side update; future readers can't find the tickets.
