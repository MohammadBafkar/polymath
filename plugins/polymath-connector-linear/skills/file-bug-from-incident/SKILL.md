---
name: file-bug-from-incident
description: File Linear bug issues from a postmortem's action items — one issue per action, severity mapped from incident sev, postmortem updated with the resulting keys.
---

# file-bug-from-incident

> Mirror of `polymath-connector-jira:file-bug-from-incident` for Linear teams. One discrete action item → one Linear issue.

## When to use

- A postmortem (from `polymath-incident:postmortem-blameless`) produced action items.
- A `respondToIncident` workflow's `tickets` step is using Linear instead of Jira.

## Inputs

- The postmortem markdown.
- The team identifier (Linear team slug or ID — required; tickets are team-scoped).

## Procedure

1. **Parse** the postmortem's "Action items" section.
2. **For each bug action item**:
   - Title: imperative + concrete.
   - Description: link the postmortem, summarize the root cause in 2–3 sentences, paste the relevant timeline rows, include dashboard / log URLs.
   - Priority: map from incident sev (sev1 → Urgent, sev2 → High, sev3 → Medium, sev4 → Low). Caller can override.
   - Labels: component / area labels matching the team's vocabulary.
   - Due date: from the postmortem's row. "TBD" rejected.
   - Assignee: a person from the team named in the postmortem.
3. **Create** via `issue.create` for each. Capture the returned identifier (e.g. `ENG-89`).
4. **Link back**: update the postmortem's action-items table with each issue's identifier and URL so the trail is bidirectional.

## Quality bar

- One issue per discrete action item. No umbrella tickets.
- Priority is mapped consistently from sev; downgrade requires a comment.
- Due date is set; "TBD" rejected.
- Postmortem's action-items table updated with Linear keys.

## Anti-patterns to avoid

- "ENG team will handle" instead of a specific assignee.
- Combining two action items into one issue to save effort. They were discrete in the postmortem; keep them discrete.
- Filing into a different team than the action-item owner. Linear is team-scoped; cross-team work needs an explicit handoff.
