# Quality scorecard

Polymath reaches stable quality only when the repo proves the product
thesis — not when it has a larger catalog. This file names the gates,
what they measure, and how to run the proof loop. Promotion bars are
defined once, in [`docs/MATURITY.md`](MATURITY.md); the per-rule
conformance table lives in [AGENTS.md](../AGENTS.md).

## Required gates (every PR)

- **Structural conformance** — `tools/conformance.sh --all`. The
  machine-readable gate registry is
  [`registry/gates.json`](../registry/gates.json) (GATES-1 enforces
  bijectivity with the script and runs every registered `--self-test`);
  the narrative rule table (MANIFEST, SKILL, TEMPLATE, WORKFLOW,
  SURFACE, CAPABILITY, TOOL, TRUST, DESC, INTEGRATION, MCP-PKG, AGENT,
  FIXTURE, DOCS, STABILITY) is in [AGENTS.md](../AGENTS.md).
- **Lint** — `tools/lint-skills.sh` (description ≤ 200 chars,
  SKILL.md ≤ 500 lines) plus markdownlint.
- **Token budget** — `tools/token-report.py budget` (≤ 400 tokens per plugin
  always-on; total scales with plugin count), `tools/token-report.py
  profiles` (PROFILE-2: each install profile's summed always-on cost stays
  within its declared `alwaysOnBudget` in
  [`registry/polymath-profiles.json`](../registry/polymath-profiles.json)),
  and `tools/build-surface-index.py --hint-budget` (HINT-BUDGET: the worst
  single-candidate ambient route hint stays ≤ 120 tokens). The workflow
  SessionStart injection is tiered — Tier A repo-relevant ≤ 400 tokens,
  Tier B one pointer line — owned by `tools/build-workflow-index.py`.
- **Routing SLO (ROUTE-EVAL-1)** — `tools/triggering.py route-eval --gate`
  (run inside `conformance.sh --all`). Gates the schema-locked invariants
  on the held-out corpus: token precision 1.0, zero false positives, and
  partial-install correctness (an uninstalled match must render the
  one-line install affordance; an installed one must not).
  Naturalistic reach and constrained-top-3 (whether a case's
  intended surface appears in the deterministic shortlist that
  `/polymath-core:route` and `polymath-pipeline:intake` read as their
  step 0 — `route-hint.py --shortlist`) are reported, never floored. The
  current numbers are published in
  [`plugins/polymath-core/data/route-metrics.json`](../plugins/polymath-core/data/route-metrics.json)
  (single producer: `route-eval --write-metrics`; the gate fails on drift).
- **Deterministic golden suite** —
  [`.github/workflows/golden-deterministic.yml`](../.github/workflows/golden-deterministic.yml):
  polymath-flows + polymath-core unit tests, the shipFeature
  scratch-repo end-to-end job, the hollow-run falsifiability anchor,
  golden-fixture frontmatter parsing, `python3
  tools/triggering.py skill check`, and `python3 tools/bakeoff.py
  check` (which enforces the symmetric-prompt contract, see § Bakeoff
  fairness).
- **Drift gates (COUNT-1, TESTDIR-1, DOCPATH-1)** —
  `tools/check-registry.py aggregates|testdirs|docpaths` (run inside
  `conformance.sh --all`). README aggregate counts are marker-wrapped and
  recomputed from the tree; fixture dirs must name real plugins; relative
  doc links must resolve. Each takes `--self-test` to prove it can fail.
- **Config + coupling hygiene (DEADCONF-1, COUPLING-1)** —
  `tools/check-registry.py deadconfig` (every `project.schema.json`
  property is read by a real consumer — skill contract, hook, runner, or
  tool — or is listed in
  [`registry/deadconfig-exemptions.json`](../registry/deadconfig-exemptions.json)
  with a reason; loader admission/validation and `*.sh` scaffolders do
  not count) and `tools/export-agents-skills.py --coupling-ratchet`
  (catalog-wide Claude-coupling occurrences stay at or below the frozen
  ceiling in
  [`registry/coupling-baseline.json`](../registry/coupling-baseline.json)
  — coupling may shrink but never grow silently). Both run inside
  `conformance.sh --all` and take `--self-test`.
- **Honest limitations** — [`LIMITATIONS.md`](../LIMITATIONS.md) is
  updated alongside any change that resolves a documented limitation.

Outside the per-PR loop:

- **Catalog reproducibility** — `tools/build-catalog.py --check`, run
  by the Pages deploy on `main` pushes.
- **Live-model runs** — bakeoff, skill-triggering `run` mode,
  workflow-triggering `run` mode, golden fixtures live, and the DESC-2
  behavioral half spend Claude API budget. They run WEEKLY via
  [`model-ci.yml`](../.github/workflows/model-ci.yml) on an ISO-week
  rotation (one suite per week: skill → workflow → golden+DESC-2), with
  the bakeoff monthly on the first scheduled run; everything sits behind
  a secret-presence guard (`CLAUDE_CODE_OAUTH_TOKEN` preferred) that
  skips cleanly — never a red X for a missing secret. The older
  on-demand `/evaluate` PR workflow still ships disabled. See
  [`LIMITATIONS.md § 4`](../LIMITATIONS.md#4-known-operational-gaps).
- **Platform-churn canary** —
  [`platform-canary.yml`](../.github/workflows/platform-canary.yml) runs
  the MANIFEST-1 validation surface (`claude plugin validate --strict` on
  the marketplace root and every plugin) against
  `@anthropic-ai/claude-code@latest` weekly, while every other workflow
  pins `@2.1.175`. If a new CLI rejects manifests the pinned version
  accepts, the canary goes red before the pin is bumped. Purely
  structural — no model token, scheduled-only so it never gates a PR.

## Promotion bars

Canonical tier definitions and per-tier requirements live in
[`docs/MATURITY.md`](MATURITY.md). Promotion is a CHANGELOG entry with
the supporting evidence link, not just a status flip; receipts live in
[`registry/stability-evidence.json`](../registry/stability-evidence.json)
(rule `STABILITY-1`).

## What gets measured and where it lands

| Surface                          | Source                                                              | Cadence                                         |
| -------------------------------- | ------------------------------------------------------------------- | ----------------------------------------------- |
| Conformance pass rate per plugin | [`tools/conformance.sh --all`](../tools/conformance.sh)             | every PR (validate.yml)                         |
| Fixture + case well-formedness   | golden-deterministic.yml                                            | every PR                                        |
| Token budget                     | [`tools/token-report.py budget`](../tools/token-report.py)          | every PR (token-budget.yml)                     |
| Route precision / FP / reach     | [`tools/triggering.py route-eval --gate`](../tools/triggering.py)   | every PR (conformance ROUTE-EVAL-1)             |
| Skill-triggering pass rate       | [`tools/triggering.py skill run`](../tools/triggering.py)           | opt-in live run (evaluation workflow disabled)  |
| Bakeoff regex deltas             | [`tools/bakeoff.py run`](../tools/bakeoff.py)                       | opt-in live run (evaluation workflow disabled)  |
| Bakeoff LLM-judge deltas         | [`tools/bakeoff.py run --judge`](../tools/bakeoff.py)               | opt-in live run                                 |
| Judge calibration drift          | [`tools/bakeoff.py calibrate`](../tools/bakeoff.py)                 | opt-in live run                                 |

Per-run JSON reports land under `.pdata/bakeoff/<case-id>.json`, one
per case, with `baseline_score`, `polymath_score`, `delta`, the
`threshold` block (`minimum_polymath_score`, `minimum_delta`),
per-side rubric results, and — when the judge is enabled — a parallel
`judge` block with its own scores and delta.

The evaluation workflow
([`evaluation.yml.disabled`](../.github/workflows/evaluation.yml.disabled))
uploads the `.pdata/bakeoff/` tree as a GitHub Actions artifact
(`evaluation-<run_id>`, 30-day retention) and answers `/evaluate` PR
comments with a summary table. It ships disabled to avoid Claude API
cost; rename it to `evaluation.yml` to enable both.

## Bakeoff fairness

The bakeoff only measures plugin value if both sides receive the same
problem. A case is **gameable** when the polymath prompt contains the
rubric's pass-tokens but the baseline prompt does not — the polymath
side earns points the baseline cannot, regardless of model quality.

Symmetric-prompt contract, enforced by `tools/bakeoff.py check`:

- `baseline_prompt` and `polymath_prompt` must contain the same
  problem statement and the same input context (code, notes, draft,
  etc.).
- The only acceptable difference is a single sentence at the end of
  `polymath_prompt` naming the Polymath skill / workflow / agent
  under test (e.g. *"Use Polymath's incident postmortem-blameless
  skill."*).
- That hint sentence may not contain any rubric `pass_regex` token.
- Rubric `pass_regex` items may match content in BOTH prompts (they
  are part of the shared input) or in NEITHER (the rubric tests
  output quality), but never in only one.

Any case whose `baseline_prompt` and `polymath_prompt` are asymmetric
on a rubric token fails `bakeoff check` with a `rubric leak` error
naming the token and the offending side. This is the structural
defence against rubric-aware prompt engineering.

## LLM-judge

In addition to the regex scorer, the bakeoff can run an LLM-judge for
holistic 0–10 scoring. The judge prompt is pinned at
[`tools/bakeoff/judge-prompt.md`](../tools/bakeoff/judge-prompt.md);
the judge model is `claude-sonnet-4-6`. Opt in with `--judge` or
`POLYMATH_BAKEOFF_JUDGE=1`.

The judge is calibrated against frozen human-blind gold scores at
`tools/bakeoff/calibration/<id>.json` (the directory is empty by
default; populate it to enable drift checks). Drift > 1 fails
`python3 tools/bakeoff.py calibrate`.

## Running the proof loop

```bash
tools/conformance.sh --all
tools/lint-skills.sh
tools/token-report.py budget
tools/build-catalog.py --check
python3 -m unittest discover -s plugins/polymath-flows/tests
python3 -m unittest discover -s plugins/polymath-core/tests
python3 tools/bakeoff.py check
python3 tools/triggering.py skill check
```

With an authenticated Claude Code CLI (`CLAUDE_CODE_OAUTH_TOKEN` or
`ANTHROPIC_API_KEY`):

```bash
tests/golden/run-fixtures.sh --plugin polymath-thinking
python3 tools/bakeoff.py run --judge --out-dir .pdata/bakeoff
python3 tools/triggering.py skill run --timeout 180
python3 tools/bakeoff.py calibrate
python3 tools/triggering.py skill list   # inspect expected invocations
```
