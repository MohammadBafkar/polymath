# Maturity tiers — single source of truth

Every plugin declares a maturity tier in
[`registry/polymath-catalog.json`](../registry/polymath-catalog.json) via
the `status` field. The tier is a contract with users about how much to
trust the plugin. This file is the canonical definition; other docs
link here.

The status field used to live in `.claude-plugin/marketplace.json`,
but Claude Code's `plugin validate --strict` rejects unknown fields
there. The catalog file is Polymath's own schema; the validator does
not see it.

The tier is **not** a quality label — it is a statement about how the
plugin's value has been *verified on disk*. A polished `experimental`
plugin is fine; a `beta` plugin with no fixtures is not.

`tools/conformance.sh` rejects any plugin whose
`registry/polymath-catalog.json` entry is missing `status` or sets it
to an unknown value (rule `MANIFEST-3`).

## Tiers

| Tier | Meaning |
| --- | --- |
| `experimental` | Scaffolded. May change shape, be renamed, be merged into another plugin, or be removed. Default for new plugins and most `polymath-connector-*` / `polymath-infra-*` plugins. |
| `beta` | Structurally proven on disk. Evidence loop is closed, but no live LLM run has been published. Shape is unlikely to change in a breaking way but is not guaranteed. |
| `stable` | Demonstrated value with live results. Breaking changes go through a deprecation cycle. No plugin in the catalog is `stable` today (see [LIMITATIONS.md](../LIMITATIONS.md)). |
| `deprecated` | Scheduled for removal. The plugin's README must name the replacement and the removal date. |

## Promotion bars

### experimental (default)

Required:

1. `claude plugin validate --strict` passes.
2. `plugin.json` carries `name`, `version`, `description`, `license`.
3. `README.md` and `CHANGELOG.md` present.
4. At least one golden fixture under `tests/golden/<plugin>/*.md`.
5. SKILL.md discipline: description ≤ 200 chars, body ≤ 500 lines.
6. Token budget: listing ≤ 400 tokens per plugin.

This is `FIXTURE-1` + `DOCS-1` + `SKILL-1` + `MANIFEST-{1,2,3}` in
`tools/conformance.sh`. CI enforces.

### beta — promotion bar

A plugin promotes from `experimental` to `beta` when **either** path is
satisfied:

**Path A — skill-shaped plugins.** The plugin's primary value is one
or more skills called by a user or workflow.

- Everything from `experimental`, **and**
- At least one parseable bakeoff case under `tests/bakeoff/<plugin>/<scenario>/case.json` (validated by `python3 tools/bakeoff.py check`), **and**
- At least one parseable skill-triggering test under `tests/skill-triggering/<plugin>/<skill>.md` (validated by `python3 tools/skill-triggering.py check`).

**Path B — foundation / runner plugins.** The plugin's primary value
is an executable (`bin/`), a hook script, a SessionStart loader, or a
shared schema/template that other plugins consume.

- Everything from `experimental`, **and**
- At least one executable unit-test file under `plugins/<plugin>/tests/`, **and**
- The test suite covers ≥ 20 deterministic assertions (`python3 -m unittest discover -s plugins/<plugin>/tests`), **and**
- The plugin's primary executable is exercised by at least one end-to-end job in `.github/workflows/golden-deterministic.yml` (the always-on, token-free half of the golden suite).

Live LLM runs are **not** required for `beta`. The bar is on-disk
evidence that the value loop is closed — that the catalog can prove
behaviour without paying for inference on every PR.

### stable — promotion bar

A plugin promotes from `beta` to `stable` only when all of the
following hold:

1. Aggregate rubric score ≥ 8.0 and every claimed surface ≥ 8 in a
   published bakeoff run (see [QUALITY-SCORECARD.md § Bakeoff fairness](QUALITY-SCORECARD.md#bakeoff-fairness)).
2. Every advertised workflow has at least one strong deterministic
   blocking gate: `commandSucceeds`, `artifactValid`,
   `artifactSchemaStrict`, or `diffConstraint`.
3. At least one bakeoff case for the plugin's primary skill scores
   ≥ 8/10 with a delta ≥ 2 over baseline. When `--judge` is enabled,
   both the regex and the LLM-judge scorers must agree.
4. At least one skill-triggering test passes on three different
   trigger phrasings (live run, not just parseable).
5. Connector and infra plugins are **eligible for `stable` only after
   distinct-value proof plus the normal stable gates.** Eligibility
   requires primary-source evidence — a bakeoff case, side-by-side
   artifact, or documented workflow-shape gap — that Polymath adds
   workflow, critique, safety, or artifact value beyond official docs,
   MCPs, LSPs, or CLIs. The evidence URL is recorded in
   [`registry/stability-evidence.json`](../registry/stability-evidence.json)
   as `distinct_value_url`. Connector/infra plugins also need this
   field populated before promoting to `beta`. See
   [docs/CONNECTOR-POLICY.md](CONNECTOR-POLICY.md).
6. A CHANGELOG entry records the promotion and the supporting
   evidence link (PR or artifact run id).
7. At least one external user beyond the maintainer (a tracked
   issue, fork, or PR citing the plugin's files).

Promotion to `stable` is a CHANGELOG entry, not just a status flip.

### Stability evidence ledger

The receipts that back every status claim live in
[`registry/stability-evidence.json`](../registry/stability-evidence.json) —
one entry per catalog plugin, with `target_status`, `evidence_state`,
`live_bakeoff_run`, `live_trigger_run`, `external_user_url`,
`promotion_pr`, `changelog_entry`, and (for connector/infra) the
required `distinct_value_url`. The ledger is enforced by
[`tools/check-stability-evidence.py`](../tools/check-stability-evidence.py)
as the `STABILITY-1` conformance gate: the catalog cannot claim
`stable` for a plugin unless the ledger has populated every required
field, and connector/infra plugins cannot reach `beta` without the
distinct-value URL. The human-facing view of the ledger lives at
[`docs/STABILITY-ROADMAP.md`](STABILITY-ROADMAP.md).

### deprecated

Set when a plugin is on a removal path. Required:

- `README.md` names the replacement (official MCP, official skill,
  another Polymath plugin, or "no replacement — covered by …").
- `README.md` names the removal date or removal trigger.
- `CHANGELOG.md` records the deprecation.

`deprecated` does not mean "low quality" or "thin." A connector that
ships only when no official MCP exists is correctly `experimental`,
not `deprecated`.

## Demotion

A plugin demotes when its on-disk evidence regresses below the tier's
bar — e.g. a bakeoff case is deleted, an external adopter retracts,
the live bakeoff stops passing. Demotion is a CHANGELOG entry that
names the regression.

A `beta` plugin missing the required fixtures is in violation of this
policy and must be demoted to `experimental` at the next release.

## What the tier does NOT promise

- Per-plugin tier is **not** an inheritance: depending on a `stable`
  plugin doesn't make the dependent plugin `stable`.
- Tier says nothing about UX polish, prose quality, or template
  aesthetics. Those are linted separately by
  [`tools/lint-skills.sh`](../tools/lint-skills.sh).
- Tier says nothing about portability to non-Claude-Code harnesses.
  See [`docs/PORTABILITY.md`](PORTABILITY.md) for the agentskills.io
  v1.0 export path and the surfaces that do not port.

## See also

- [docs/QUALITY-SCORECARD.md](QUALITY-SCORECARD.md) — gates and the bakeoff-fairness contract.
- [docs/QUALITY-DASHBOARD.md](QUALITY-DASHBOARD.md) — where measured artifacts land.
- [docs/CONNECTOR-POLICY.md](CONNECTOR-POLICY.md) — connector / infra disclosure rules.
- [docs/PLUGIN-AUTHORING.md](PLUGIN-AUTHORING.md) — authoring layout and conventions.
- [LIMITATIONS.md](../LIMITATIONS.md) — what the catalog does NOT prove yet.
