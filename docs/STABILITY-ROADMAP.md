# Stability roadmap — where each plugin stands

This is the human-facing view of
[`shared/stability-evidence.json`](../shared/stability-evidence.json).
The machine-readable ledger is the source of truth; this page exists
so a reader can scan the catalog without opening JSON. The ledger and
this page are reconciled by hand when the ledger changes.

Every plugin is recorded against the **evidence ladder**:

| State                  | Meaning                                                                                                |
| ---------------------- | ------------------------------------------------------------------------------------------------------ |
| `pre-evidence`         | Golden fixture only — the experimental floor.                                                          |
| `on-disk-skill`        | Golden + a parseable bakeoff case + a parseable skill-triggering test. Skill-shaped beta closure.      |
| `on-disk-foundation`   | Golden + executable unit tests + an end-to-end workflow job. Foundation/runner beta closure.           |
| `stable-ready`         | On-disk closure plus a live bakeoff and live trigger run that meet the stable bar. Awaiting adopter.   |
| `stable`               | Promoted, with all live fields populated and a CHANGELOG entry recording the promotion.                |
| `deprecated`           | Off-ladder; CHANGELOG entry names the replacement and removal date.                                    |

The promotion gates that read this ledger live in
[`docs/MATURITY.md`](MATURITY.md) and
[`docs/CONNECTOR-POLICY.md`](CONNECTOR-POLICY.md). The
`STABILITY-1` conformance check in
[`tools/check-stability-evidence.py`](../tools/check-stability-evidence.py)
refuses to merge a status flip that the ledger does not back.

## Iteration plan

The roadmap is executed in iterations so each step ships independent
verifiable value. **No iteration promotes any plugin until its row in
the ledger is fully populated.**

| # | Scope                                                                 | Output                                                                                                                |
| - | --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| 0 | All 43 plugins                                                        | The ledger, schema, and `STABILITY-1` checker land. No status promotions.                                             |
| 1 | 9 skill-shaped beta plugins already at `on-disk-skill`                | Live bakeoff + live trigger run on three phrasings. Mark `stable-ready` only when both pass; promote only with adopter.|
| 2 | `polymath-core`, `polymath-flows` (`on-disk-foundation`)              | Foundation-specific live proof (workflow e2e job + bakeoff coverage where load-bearing). External adopter.            |
| 3 | 4 near-beta experimental + 14 golden-only experimental skill plugins  | Close on-disk evidence (bakeoff case + 3-phrasing trigger test) for each, then run Iteration 1's live-proof loop.     |
| 4 | 14 connector / infra plugins                                          | Add bakeoff + trigger that prove **distinct value** beyond official MCP/CLI/LSP/docs. Populate `distinct_value_url`.   |
| 5 | Promotion batches                                                     | Small PRs (≤ 3 plugins each) flipping catalog status + appending CHANGELOG, with ledger receipts updated in lockstep. |

## Current standing — by evidence state

### `on-disk-skill` — ready for Iteration 1 live proof (9 plugins)

These plugins already have a parseable bakeoff case and a
skill-triggering test on disk. The next step is the live run
(`python3 tools/bakeoff.py run --judge --out-dir .pdata/bakeoff` and
`python3 tools/skill-triggering.py run --timeout 180`).

- `polymath-author`
- `polymath-engineering`
- `polymath-incident`
- `polymath-planning`
- `polymath-product`
- `polymath-security`
- `polymath-sre`
- `polymath-thinking`
- `polymath-writing`

### `on-disk-foundation` — ready for Iteration 2 foundation proof (2 plugins)

These plugins are runners or shared infrastructure: their on-disk
evidence is unit + end-to-end coverage rather than bakeoff cases.

- `polymath-core` — SessionStart loader; has `plugins/polymath-core/tests/`.
- `polymath-flows` — `bin/polymath-flow` runner, 15 workflows each with a strong `mustPass` gate, `plugins/polymath-flows/tests/`.

### `pre-evidence` — Iteration 3 close-evidence work (17 plugins)

Four plugins are listed as "near-beta" in the iteration plan because
they ship multiple skills but have no bakeoff or trigger fixtures yet:

- `polymath-decisions`
- `polymath-observability`
- `polymath-qa`
- `polymath-release`

The remaining 14 are golden-only experimental skill plugins:

- `polymath-ai`
- `polymath-backend`
- `polymath-communication`
- `polymath-data`
- `polymath-design`
- `polymath-devops`
- `polymath-frontend`
- `polymath-leadership`
- `polymath-learning`
- `polymath-mobile`
- `polymath-performance`
- `polymath-platform`
- `polymath-research`

### `pre-evidence` — Iteration 4 connector / infra work (11 plugins)

These need a bakeoff case, a skill-triggering test, **and** a
`distinct_value_url` proving Polymath adds workflow / critique /
safety / artifact value beyond the official MCP / CLI / LSP / docs
surface. The distinct-value field is required before any promotion
past experimental.

- `polymath-connector-observability`
- `polymath-connector-github`
- `polymath-connector-tracker`
- `polymath-connector-pagerduty`
- `polymath-connector-sentry`
- `polymath-connector-slack`
- `polymath-connector-snyk`
- `polymath-connector-statuspage`
- `polymath-connector-terraform`
- `polymath-infra-cloud`
- `polymath-infra-kubernetes`

### `stable-ready` (0 plugins) and `stable` (0 plugins)

No plugin in the catalog has cleared the live bakeoff + live trigger +
external adopter bar yet. The
[`LIMITATIONS.md`](../LIMITATIONS.md) § 1 claim that the catalog has
no external users still stands.

## How the ledger gets updated

1. A plugin earns a new piece of evidence (live run, adopter,
   distinct-value artifact, promotion PR).
2. Update the plugin's entry in
   [`shared/stability-evidence.json`](../shared/stability-evidence.json)
   with the URL or anchor.
3. If the entry now backs a status promotion, change the plugin's
   `status` in
   [`shared/polymath-catalog.json`](../shared/polymath-catalog.json)
   in the same PR.
4. Append a CHANGELOG entry recording the promotion + supporting
   evidence link.
5. Bring this roadmap doc back in sync with the ledger in the same PR.
   `tools/check-stability-evidence.py` (rule `STABILITY-1`) blocks the
   merge if any required ledger field is missing.

## See also

- [docs/MATURITY.md](MATURITY.md) — promotion bar definitions.
- [docs/CONNECTOR-POLICY.md](CONNECTOR-POLICY.md) — connector / infra disclosure rules and distinct-value requirement.
- [docs/QUALITY-DASHBOARD.md](QUALITY-DASHBOARD.md) — where measured artifacts land.
- [shared/stability-evidence.json](../shared/stability-evidence.json) — machine-readable ledger.
- [tools/check-stability-evidence.py](../tools/check-stability-evidence.py) — STABILITY-1 enforcement.
