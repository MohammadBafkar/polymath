# Scheduled-work queue contract (§ 11.6)

Polymath does not ship its own scheduler. Recurring or future work
(postmortem reminders, weekly retros, dependency scans, DR drills)
is owned by whichever external scheduler the team uses:

- Anthropic Cloud Routines / Scheduled Tasks
- GitHub Actions `schedule:` triggers
- OS cron / launchd + `claude -p`

That scheduler writes JSON to `${CLAUDE_PLUGIN_DATA}/polymath-core/queue.json`:

```jsonc
[
  {
    "id": "postmortem-IC-2026-09",
    "due": "2026-05-25T14:00:00Z",
    "owner": "user",
    "skill": "polymath-incident:postmortem-blameless",
    "note": "Due 48h after incident close"
  }
]
```

Field rules:

| Field    | Required | Meaning                                                                    |
| -------- | -------- | -------------------------------------------------------------------------- |
| `id`     | yes      | Stable identifier; idempotent for repeat writers.                          |
| `due`    | yes      | ISO-8601 timestamp. Tolerates trailing `Z`. Treated as UTC if no offset.   |
| `skill`  | optional | `<plugin>:<skill>` to route to. Displayed when surfaced.                   |
| `owner`  | optional | Free-form ("user", "@oncall", …).                                          |
| `note`   | optional | One-line context shown to the human.                                       |

Anything else is ignored. The polymath-core SessionStart hook reads
this file at session start, filters to entries whose `due` ≤ now (UTC),
and prints them as part of the session preamble. It does **not** delete
entries — the producer is responsible for queue lifecycle.

If the file is absent, malformed, or has no due entries, the hook is
silent. Polymath never blocks a session on queue contents.
