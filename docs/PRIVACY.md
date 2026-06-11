# Polymath privacy + telemetry policy

> **TL;DR:** Polymath **sends nothing, anywhere, ever**. The only telemetry
> that exists at all is one **opt-in, local-only** JSONL the workflow runner
> writes on your machine when you set `POLYMATH_TELEMETRY=1` — documented
> field-by-field in [TELEMETRY.md](TELEMETRY.md).

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
per the contract below, fully described in [TELEMETRY.md](TELEMETRY.md).
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
3. **Documented payload.** [`docs/TELEMETRY.md`](TELEMETRY.md) lists every field collected and how it's used, before the feature is enabled. No "stealth" telemetry.
4. **No content.** Prompts, transcripts, file contents, secrets, and user-identifying information are explicitly out of scope. The maximum payload is plugin name + skill name + duration + outcome (success/failure code).
5. **No third-party SDK.** Polymath does not embed analytics SDKs (e.g. Google Analytics, Mixpanel). Any future telemetry endpoint will be a first-party Polymath service that the user can inspect via a documented URL.
6. **Offline-first.** Polymath continues to work fully when offline. Telemetry is never load-bearing on functionality.

## What about MCP servers?

Each connector plugin runs an MCP server in a subprocess (e.g. `@modelcontextprotocol/server-github`). Those servers are governed by their own upstream privacy policies. Read the policy for the specific server you install before granting it credentials.

Polymath's responsibility ends at:

- Validating the plugin manifest (no untrusted code is hidden in the manifest itself).
- Ensuring `userConfig.sensitive: true` credentials are masked in `claude plugin list` output and not echoed to logs.
- Making the `command` and `args` of every `.mcp.json` legible in the plugin's source tree (i.e. nothing fetched at install time without you seeing it).

## Reporting concerns

Open an issue at <https://github.com/MohammadBafkar/Polymath/issues> with the label `privacy`. Or mail the maintainer listed in `.github/CODEOWNERS`.
