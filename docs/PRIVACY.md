# Polymath privacy + telemetry policy

> **TL;DR:** Polymath **sends nothing, anywhere, ever**. The only telemetry
> that exists at all is one **opt-in, local-only** JSONL the workflow runner
> writes on your machine when you set `POLYMATH_TELEMETRY=1` — documented
> field-by-field in [the telemetry surface section below](#the-telemetry-surface).

## What we collect

Nothing, by default.

- No usage analytics.
- No skill-invocation counts.
- No error reports.
- No hook diagnostic phone-home.
- No anonymized identifiers.

With exactly `POLYMATH_TELEMETRY=1` in the environment, `polymath-flow`
appends command name + workflow name + duration + exit code to a JSONL in
its own plugin data dir — local-only, fail-open, no network, payload capped
per the contract below, fully described in
[the telemetry surface section](#the-telemetry-surface).
Unset or any other value (including `0`) disables it; a unit test in
`plugins/polymath-flows/tests/` verifies the off state writes nothing.

The plugin code in this repository contains no network calls except those you explicitly trigger through:

- Connector MCP servers (e.g. `polymath-vcs` calling GitHub on your behalf). Those calls go directly from the MCP server to the vendor's API with credentials you supplied via `userConfig`.
- The Claude Code runtime itself, governed by Anthropic's terms.

## The telemetry contract

Every telemetry surface — the local runner JSONL today, anything added
later — is bound by:

1. **Off by default.** Requires explicit `POLYMATH_TELEMETRY=1` in the environment.
2. **Local-disable always works.** Unsetting the variable, or setting `POLYMATH_TELEMETRY=0`, fully disables collection. Plugins MUST honor this — verified by a unit/CI gate before any telemetry ships.
3. **Documented payload.** [The telemetry surface section](#the-telemetry-surface) lists every field collected and how it's used, before the feature is enabled. No "stealth" telemetry.
4. **No content.** Prompts, transcripts, file contents, secrets, and user-identifying information are explicitly out of scope. The maximum payload is plugin name + skill name + duration + outcome (success/failure code).
5. **No third-party SDK.** Polymath does not embed analytics SDKs (e.g. Google Analytics, Mixpanel). Any future telemetry endpoint will be a first-party Polymath service that the user can inspect via a documented URL.
6. **Offline-first.** Polymath continues to work fully when offline. Telemetry is never load-bearing on functionality.

## The telemetry surface

The complete current surface, satisfying contract item 3.

`polymath-flow` (the workflow runner) appends one line per invocation to

```text
${CLAUDE_PLUGIN_DATA}/telemetry.jsonl     # polymath-flows' own data dir
```

**only** when the environment carries exactly `POLYMATH_TELEMETRY=1`.
Unset, `0`, or any other value disables it entirely (verified by a unit
test in `plugins/polymath-flows/tests/`). There is no network call — the
file never leaves the machine, and Polymath ships nothing that reads it
beyond you.

### The complete payload

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
contract above: name + duration + outcome.

### Lifecycle

The file grows by one line per runner invocation and is yours to truncate
or delete at any time; nothing depends on it. Writing is fail-open — an
unwritable data dir never affects the runner.

## What about MCP servers?

Each connector plugin runs an MCP server in a subprocess (e.g. `@modelcontextprotocol/server-github`). Those servers are governed by their own upstream privacy policies. Read the policy for the specific server you install before granting it credentials.

Polymath's responsibility ends at:

- Validating the plugin manifest (no untrusted code is hidden in the manifest itself).
- Ensuring `userConfig.sensitive: true` credentials are masked in `claude plugin list` output and not echoed to logs.
- Making the `command` and `args` of every `.mcp.json` legible in the plugin's source tree (i.e. nothing fetched at install time without you seeing it).

## Reporting concerns

Open an issue at <https://github.com/MohammadBafkar/Polymath/issues> with the label `privacy`. Or mail the maintainer listed in `.github/CODEOWNERS`.
