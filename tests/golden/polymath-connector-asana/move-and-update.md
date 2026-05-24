---
plugin: polymath-connector-asana
scenario: move-and-update
expect:
  invoked:
    - polymath-connector-asana:asana-task-update
  output_matches:
    - "(gid|GID)"
    - "(section|sections.addTask)"
    - "(custom.field|option)"
timeout_seconds: 90
---

# Prompt

> Move Asana task 1234567890123456 from "In Progress" to "In Review",
> set the "Status" custom field to "Shipping", and assign it to alex@example.com.

Use polymath-connector-asana:asana-task-update.

# Acceptance

- Section name resolved to GID via sections.list before move.
- Custom-field name resolved to GID; enum option resolved by GID, not string.
- Section move done via sections.addTask, not via tasks.update.
- Assignee email resolved to user GID, not passed as a string.
