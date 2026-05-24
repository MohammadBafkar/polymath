# PagerDuty MCP tools (reference)

Default server: `@pagerduty/mcp-server` (or any community server speaking the same tool shape). Swap `command`+`args` in `.mcp.json` if you use a different distribution.

Auth: `PAGERDUTY_API_KEY` from `userConfig.pagerdutyApiKey`.

## Tools exposed (subset)

### Read

- `get_incident` — by id.
- `list_incidents` — with status / service / urgency filters.
- `list_log_entries` — per-incident timeline.
- `get_oncall_for_service` — current on-call + next-up.
- `list_services` — service catalog.
- `list_notes` — incident notes.

### Write

- `acknowledge_incident` — ack.
- `resolve_incident` — resolve.
- `snooze_incident` — defer.
- `add_note` — append a note.
- `trigger_incident` — open a new one (use sparingly; usually a monitor does this).

## API-key scope

PagerDuty issues account-wide API keys. Limit blast radius:

- Use a service-account key, not a human's personal key.
- For read-only triage use cases, generate a key with read-only permissions if your plan supports it.
- Rotate keys regularly; the `userConfig.sensitive: true` channel makes rotation a `claude plugin install` re-run.

## Anti-patterns

- Auto-resolving incidents from the model with no human ack.
- Triggering incidents from the model — usually wrong; monitors should trigger.
