# Quality scorecard

Polymath reaches 9+ quality only when the repo proves the product thesis, not
when it has a larger catalog.

## Current Gates

- Structural conformance: `tools/conformance.sh --all` (includes `MANIFEST-3` maturity tier, `CONNECTOR-2` audit, `AGENT-1` evidence).
- Token budget: `tools/token-budget.sh`.
- Catalog reproducibility: `tools/build-catalog.py --check`.
- Workflow runner tests: `python3 -m unittest discover -s plugins/polymath-flows/tests`.
- Agent evidence: `tools/check-agent-evidence.py`.
- Bakeoff case validity: `tools/bakeoff.py check`. **9 cases** pre-registered across the stable bundle.
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
