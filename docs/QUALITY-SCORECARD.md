# Quality scorecard

Polymath reaches 9+ quality only when the repo proves the product thesis, not
when it has a larger catalog.

## Current Gates

- Structural conformance: `tools/conformance.sh --all` (includes `MANIFEST-3` maturity tier, `CONNECTOR-2` audit, `AGENT-1` evidence).
- Token budget: `tools/token-budget.sh`.
- Catalog reproducibility: `tools/build-catalog.py --check`.
- Workflow runner tests: `python3 -m unittest discover -s plugins/polymath-flows/tests`.
- Agent evidence: `tools/check-agent-evidence.py`.
- Bakeoff case validity: `tools/bakeoff.py check`. **9 cases** pre-registered across the stable bundle. The check enforces the symmetric-prompt contract (see § Bakeoff fairness below) so the run cannot be silently engineered.
- Connector / lang / infra boundary: every in-scope plugin audited in [`docs/CONNECTOR-POLICY.md`](CONNECTOR-POLICY.md) (`CONNECTOR-2`).
- Honest limitations: [`LIMITATIONS.md`](../LIMITATIONS.md) is updated alongside any change that resolves a documented limitation.
- Live-model fixtures: required CI gate on `main` pushes. Setup at [`LIMITATIONS.md § 4.1`](../LIMITATIONS.md#41-how-to-provide-the-key).

## 9+ Promotion Bar

1. Every advertised workflow has at least one strong deterministic blocking
   gate: `commandSucceeds`, `artifactValid`, `artifactSchemaStrict`, or
   `diffConstraint`.
2. Every agent has a no-agent baseline evidence record and a live golden
   fixture.
3. The stable bundle beats baseline Claude Code on at least three bakeoff cases:
   Polymath score >= 8/10 and delta >= 2 points per case.
4. Connector and language plugins stay experimental unless primary-source
   evidence shows Polymath adds workflow, critique, safety, or artifact value
   beyond official docs, MCPs, LSPs, or CLIs.
5. Stable promotion requires a CHANGELOG entry and at least one external user
   beyond the maintainer.

## Bakeoff fairness

The bakeoff only measures plugin value if both sides are given the same
problem. A case is **gameable** when the polymath prompt contains the
rubric's pass-tokens but the baseline prompt does not — the polymath
side earns points the baseline cannot, regardless of model quality.

Symmetric-prompt contract, enforced by `tools/bakeoff.py check`:

- `baseline_prompt` and `polymath_prompt` must contain the same problem
  statement and the same input context (code, notes, draft, etc.).
- The only acceptable difference is a single sentence at the end of
  `polymath_prompt` naming the Polymath skill / workflow / agent under
  test (e.g. *"Use Polymath's incident postmortem-blameless skill."*).
- That hint sentence may not contain any rubric `pass_regex` token.
- Rubric `pass_regex` items may match content in BOTH prompts (they are
  part of the shared input) or in NEITHER (the rubric tests output
  quality), but never in only one.

Any case whose `baseline_prompt` and `polymath_prompt` are asymmetric
on a rubric token fails `bakeoff check` with one of:

```text
error: <case>: rubric leak: pass-token 'X' (rubric 'Y') appears in
  polymath_prompt but not in baseline_prompt — engineered advantage
  for Polymath
error: <case>: rubric leak: pass-token 'X' (rubric 'Y') appears in
  baseline_prompt but not in polymath_prompt — biased against Polymath
```

This check is mandatory on every PR (`bakeoff-parse` job in
`.github/workflows/golden-tests.yml`) and is the structural defence
against the most common bakeoff failure mode: rubric-aware
prompt-engineering.

## Running The Proof Loop

```bash
tools/conformance.sh --all
tools/lint-skills.sh
tools/token-budget.sh
tools/build-catalog.py --check
python3 -m unittest discover -s plugins/polymath-flows/tests
python3 tools/check-agent-evidence.py
python3 tools/bakeoff.py check
```

With an authenticated Claude Code CLI:

```bash
tests/golden/run-fixtures.sh --plugin polymath-thinking
tests/golden/run-fixtures.sh --plugin polymath-research
python3 tools/bakeoff.py run
```
