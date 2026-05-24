---
name: file-bug-from-incident
description: File a Jira bug from an incident — pre-fills repro from the timeline, links the postmortem, sets severity from incident sev, routes by component.
---

# file-bug-from-incident

> Convert one incident's findings into one or more Jira bugs. Each bug is independently actionable.

## When to use

- A postmortem produced action items that include bug fixes.
- A sev2/sev1 needs follow-up tickets before closing.

## Inputs

- The postmortem markdown (from `polymath-incident:postmortem-blameless`).
- Mapping of components/areas to Jira components.

## Procedure

1. **Parse** the postmortem's "Action items" section. Each row is a candidate ticket.
2. **For each action that's a bug**:
   - Title: imperative + concrete (e.g. "Add burn-rate alert at 6h window for refund SLO").
   - Description: link the postmortem, summarize the root cause in 2–3 sentences, paste the relevant timeline rows, attach the dashboard / logs URLs.
   - Severity: map from incident sev (sev1 → Critical, sev2 → High, sev3 → Medium, sev4 → Low). Allow override.
   - Component: by code area.
   - Due date: from the postmortem's action-item due date.
   - Owner: the team named in the postmortem.
3. **Create** via `jira_create_issue` for each, capturing the resulting key.
4. **Link** each created issue back into the postmortem document as a row in the action-items table.

## Quality bar

- One bug per discrete action item; don't pack three into one ticket.
- Severity maps consistently from incident sev — don't downgrade silently.
- Due date is set; "TBD" is not acceptable for post-incident action items.
- Postmortem updated with the Jira keys, so the trail is bidirectional.

## Anti-patterns to avoid

- Filing one umbrella ticket "improve reliability".
- Filing without an owner.
- Skipping the postmortem-side update; future readers can't find the tickets.
