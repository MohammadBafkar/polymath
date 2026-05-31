# Quality scorecard

Polymath reaches stable quality only when the repo proves the product
thesis — not when it has a larger catalog.

## Required gates

Every PR runs:

- **Structural conformance** — `tools/conformance.sh --all`
  (`MANIFEST-3` maturity tier, `CONNECTOR-2` audit, `SKILL-1`,
  `TEMPLATE-1`, `WORKFLOW-1`, `FIXTURE-1`).
- **Lint** — `tools/lint-skills.sh` (description ≤ 200 chars,
  SKILL.md ≤ 500 lines).
- **Token budget** — `tools/token-budget.sh` (≤ 400 tokens per plugin
  always-on; total scales with plugin count).
- **Catalog reproducibility** — `tools/build-catalog.py --check`.
- **Workflow YAML schema** — `plugins/polymath-flows/bin/polymath-flow validate <path>`.
- **Workflow runner tests** — `python3 -m unittest discover -s plugins/polymath-flows/tests`.
- **Project-context loader tests** — `python3 -m unittest discover -s plugins/polymath-core/tests`.
- **Bakeoff case validity** — `python3 tools/bakeoff.py check`. Nine
  cases pre-registered across the catalog. The check enforces the
  symmetric-prompt contract (see § Bakeoff fairness) so the run
  cannot be silently engineered.
- **Skill-triggering frontmatter** — `python3 tools/skill-triggering.py check`.
- **Workflow routing index** — `python3 tools/build-workflow-index.py --check`
  (the committed index matches a fresh build; injected min-index under its
  token ceiling).
- **Workflow-triggering frontmatter** — `python3 tools/workflow-triggering.py
  check` (frontmatter valid; `trigger_prompts` a superset of the workflow's
  own `triggers`). The live `run` mode is opt-in under
  `CLAUDE_CODE_OAUTH_TOKEN`, like skill-triggering.
- **Description disambiguation** — `python3 tools/lint-descriptions.py
  --strict` (no two always-on descriptions token-collide without a
  distinguishing proper noun). `scope_boundary` / `trigger_clarity` are
  reported as advisory means, not gated.
- **Connector / infra boundary** — every in-scope plugin audited in
  [`docs/CONNECTOR-POLICY.md`](CONNECTOR-POLICY.md).
- **Honest limitations** — [`LIMITATIONS.md`](../LIMITATIONS.md) is
  updated alongside any change that resolves a documented limitation.
- **Live-model fixtures** — required CI gate on `main` pushes. Setup
  at [`LIMITATIONS.md § 4.1`](../LIMITATIONS.md#41-providing-the-claude-code-auth-secret).

## Promotion bars

Canonical definitions and per-tier requirements live in
[`docs/MATURITY.md`](MATURITY.md). The short version:

- `experimental` — default; structural + ≥ 1 golden fixture.
- `beta` — on-disk evidence loop closed: skill bakeoff + triggering
  tests, **or** a foundation-runner with ≥ 20 unit-test assertions
  plus an end-to-end job in golden-tests.yml. Live LLM runs are not
  required.
- `stable` — live bakeoff ≥ 8 / delta ≥ 2 (both regex and LLM-judge
  scorers agree under `--judge`), every advertised workflow has at
  least one strong deterministic blocking gate
  (`commandSucceeds` / `artifactValid` / `artifactSchemaStrict` /
  `diffConstraint`), skill-triggering test passing on three trigger
  phrasings, and at least one external user beyond the maintainer.
  Connector / infra plugins stay `experimental` unless primary-source
  evidence shows Polymath adds workflow / critique / safety / artifact
  value beyond the upstream official surface (see
  [CONNECTOR-POLICY.md](CONNECTOR-POLICY.md)).

Promotion is a CHANGELOG entry with the supporting evidence link, not
just a status flip.

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
tools/token-budget.sh
tools/build-catalog.py --check
python3 -m unittest discover -s plugins/polymath-flows/tests
python3 -m unittest discover -s plugins/polymath-core/tests
python3 tools/bakeoff.py check
python3 tools/skill-triggering.py check
```

With an authenticated Claude Code CLI:

```bash
tests/golden/run-fixtures.sh --plugin polymath-thinking
python3 tools/bakeoff.py run --judge
python3 tools/skill-triggering.py run --timeout 180
python3 tools/bakeoff.py calibrate
```
