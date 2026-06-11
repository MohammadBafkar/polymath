# Polymath telemetry

> **TL;DR:** One opt-in, **local-only** JSONL file. Nothing is ever sent
> anywhere. Off by default; requires exactly `POLYMATH_TELEMETRY=1`.

This document exists because [PRIVACY.md](PRIVACY.md) requires every
collected field to be documented before any telemetry ships. It describes
the complete current surface.

## What exists

`polymath-flow` (the workflow runner) appends one line per invocation to

```text
${CLAUDE_PLUGIN_DATA}/telemetry.jsonl     # polymath-flows' own data dir
```

**only** when the environment carries exactly `POLYMATH_TELEMETRY=1`.
Unset, `0`, or any other value disables it entirely (verified by a unit
test in `plugins/polymath-flows/tests/`). There is no network call — the
file never leaves the machine, and Polymath ships nothing that reads it
beyond you.

## The complete payload

```json
{"ts": "2026-06-11T10:00:00+00:00", "tool": "polymath-flow", "cmd": "start",
 "exit": 0, "duration_ms": 41, "workflow": "shipFeature"}
```

| Field         | Content                                                          |
| ------------- | ---------------------------------------------------------------- |
| `ts`          | UTC timestamp of the invocation                                  |
| `tool`        | Always `polymath-flow`                                           |
| `cmd`         | The subcommand (`start`, `next`, `assert`, …)                    |
| `exit`        | Exit code (outcome)                                              |
| `duration_ms` | Wall-clock duration of the command                               |
| `workflow`    | Catalog/project workflow *name* — only for commands that take one |

Deliberately excluded: run ids (their slug derives from user-supplied
titles), prompts, step summaries, file paths, file contents, inputs,
usernames, hostnames. The payload matches the maximum allowed by the
[PRIVACY.md](PRIVACY.md) contract: name + duration + outcome.

## Lifecycle

The file grows by one line per runner invocation and is yours to truncate
or delete at any time; nothing depends on it. Writing is fail-open — an
unwritable data dir never affects the runner.
