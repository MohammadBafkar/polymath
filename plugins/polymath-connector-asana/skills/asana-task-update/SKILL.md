---
name: asana-task-update
description: Update an Asana task — move sections, set assignee + due date + custom fields, resolved by GID not name (Asana API rejects name-based references).
---

# asana-task-update

> Move an Asana task between sections and update its fields without sending name-based references the API silently misroutes. Output is the updated task GID + the field deltas applied.

## When to use

- A workflow step completes and the corresponding Asana task moves from "In Progress" → "In Review".
- A `polymath-product` PRD ships and its tracking task gets a "Shipped" custom-field update.
- A retro finds an action item that already has an Asana task and just needs the assignee/due-date updated.

## Inputs

- Task GID (required) — Asana's numeric task identifier (visible in the task URL).
- Target section name (optional) — resolved to a section GID before the update.
- Field updates (required) — assignee, due_on, notes, custom fields. Custom fields specified by name are resolved to GIDs.

## Procedure

1. **Resolve the project GID** from the task. Custom fields and sections are project-scoped.
2. **Resolve the section GID.** Call `sections.list` on the project, match `name` → `gid`. Refuse to update if the target section name does not exist (creating sections silently is rarely intended).
3. **Resolve custom field GIDs.** For each field name in the input, call `custom_field_settings.list` on the project; match `custom_field.name` → `gid`. Resolve enum option names to their option GIDs too — Asana custom fields with type `enum` require option GIDs, not strings.
4. **Resolve assignee.** If the input is an email or display name, call `users.list` in the workspace; match to a user GID. Reject if multiple matches (ambiguous).
5. **Apply the update** via `tasks.update` with all resolved GIDs + value pairs. Asana's API merges; it does not overwrite, so omit fields you do not want to touch.
6. **Move section** via `sections.addTask` (separate call — `tasks.update` does not move sections).
7. **Return** the updated task GID, the section move, and the resolved field deltas.

## Output

```text
asana-task-update

Task:       1234567890123456 ("Refund async writes — PRD")
Project:    1234567890123000 ("Q3 Engineering")
Section:    "In Progress" → "In Review" (gid 1234567890999)
Assignee:   alex@example.com → user gid 0987654321
Due date:   2026-05-31
Custom fields:
  - "Status"      → option "Shipping" (gid ...)
  - "Engineer"    → user gid 0987654321
```

## Quality bar

- All references resolved to GIDs before the API call.
- Section move is a separate call from field update.
- Ambiguous assignee matches refuse rather than guessing.
- Custom-field enum options resolved by GID (string values silently no-op).

## Anti-patterns to avoid

- Passing section/field/user *names* to `tasks.update`. The Asana API does not resolve them; the update appears to succeed but the field is unchanged.
- Trying to move sections via `tasks.update` with a `memberships` write. The supported path is `sections.addTask`.
- Picking the first user match for an ambiguous name. Distinct people occasionally share names; ask, do not guess.
- Setting `completed: true` on a task that has open subtasks. Asana allows it but reviewers usually treat that as a process violation.
