# Limitations

This document is the deliberate counterweight to `README.md`. It records,
in writing, what Polymath is not good at, where official tools beat it,
where claims outrun evidence, and what the maintainer would not yet trust
the catalog with. Reviewers should read this before `README.md` if they
care about depth more than breadth.

The honesty here is itself a feature: every line below is a falsifiable
claim, and the absence of a counter-claim in `README.md` or the catalog
is intentional.

## 1. What Polymath does not currently prove

- Polymath has **not** demonstrated that it produces better artifacts than
  baseline Claude Code on a measured set of tasks. The bakeoff harness
  exists (`tools/bakeoff.py`, `tests/bakeoff/cases/*.json`) and three
  cases are pre-registered, but no live run has been published. Until at
  least three cases meet the `decision_threshold` in
  `docs/QUALITY-SCORECARD.md`, the central product thesis is unconfirmed.
- Polymath has **not** demonstrated that its agents outperform a
  no-agent baseline on real Claude runs. The evidence records under
  `tests/agent-evidence/` declare what the baseline is expected to miss;
  the live golden fixtures that confirm or refute those expectations
  are auth-dependent and are not yet enforced as a required CI gate
  by default on every PR.
- Polymath has **not** measured external adoption. The catalog claims
  no external users for any of the eight `stable` plugins, and the
  `9+ Promotion Bar` in `docs/QUALITY-SCORECARD.md` explicitly requires
  at least one external user before any new promotion to `stable`.

## 2. Where official tools beat Polymath today

- **Language facts and APIs.** For any factual question about a language
  feature, API signature, or LSP behaviour, the official docs and LSPs
  beat any `polymath-lang-*` plugin. The lang plugins exist to encode
  judgement (migration plans, test idioms, build audits), not facts.
  If a question is "what does this API return?", reach for the official
  surface, not Polymath.
- **Service integrations with official MCPs.** Where an official MCP
  exists (GitHub, Jira, Linear, Datadog, Sentry, etc.), the official
  surface is the source of truth for tool calls. The Polymath connector
  is justified only by the workflow shape, safety opinion, or critique
  it adds, as recorded in `docs/CONNECTOR-POLICY.md`. Connectors that
  fail that disclosure are flagged in the same document for demotion at
  the next release.
- **Cloud resource operations.** For one-off operations against AWS,
  Azure, GCP, or Kubernetes, the official MCP families plus the vendor
  CLI are faster and safer than any Polymath wrapper. `polymath-infra-*`
  is justified only when a multi-environment workflow, RBAC audit, or
  destructive-action checklist is the actual question.

## 3. Where the catalog is intentionally thin

- **`polymath-ai` is currently underbuilt** relative to the marketplace's
  identity. It ships three skills (`rag-design`, `prompt-engineer`,
  `eval-plan`) when an AI-craft showcase needs roughly twice that depth.
  Promotion to `stable` is gated on the bakeoff demonstrating measurable
  uplift on at least one AI-craft case.
- **There are only two agents.** `architecture-critic` and
  `research-scout` are the entire agent surface. The third reviewer in
  the design conversation named seven; the catalog has chosen quality
  over breadth and will add agents only when each ships with an
  evidence record under the `no-agent baseline` rule (see
  `docs/PLUGIN-AUTHORING.md` § 6).
- **The "Polymath core" set is narrow on purpose.** Eight plugins claim
  `stable` (`polymath-core`, `-thinking`, `-planning`, `-writing`,
  `-decisions`, `-engineering`, `-flows`, `-author`). The remaining
  63 are openly `experimental`. The catalog has chosen a small
  defended surface over a large undefended one.

## 4. Known operational gaps

- **Live-model fixtures are auth-dependent.** Without a
  `CLAUDE_CODE_OAUTH_TOKEN` (or `ANTHROPIC_API_KEY`) in repo secrets,
  the `claude-cli-fixtures` and bakeoff jobs in `.github/workflows/`
  cannot prove the agents' and workflows' real behaviour. The CI is
  configured to fail the build when auth is missing on `main` pushes
  (see § 5 below), but a fork without that secret cannot reproduce
  the proof.

  ### 4.1 How to provide the key

  The maintainer enables the live CI gate once per repo. Two paths:

  **Preferred — a Claude.ai subscription OAuth token.** This is the
  same token Claude Code's `/login` flow stores locally and is the
  cheapest option per call.

  ```bash
  # On the maintainer's machine, after a fresh `claude /login`:
  cat ~/.claude/oauth.json | jq -r .access_token

  # Then add it to the repo (requires `gh auth login` first):
  gh secret set CLAUDE_CODE_OAUTH_TOKEN \
    --repo MohammadBafkar/Polymath \
    --body "$(cat ~/.claude/oauth.json | jq -r .access_token)"
  ```

  **Alternative — an Anthropic API key.** Falls back to per-token
  billing instead of a subscription. Use this only if the maintainer
  doesn't have a Claude.ai seat.

  ```bash
  gh secret set ANTHROPIC_API_KEY \
    --repo MohammadBafkar/Polymath \
    --body "sk-ant-..."
  ```

  **UI alternative.** GitHub → repo → Settings → Secrets and variables
  → Actions → New repository secret → name `CLAUDE_CODE_OAUTH_TOKEN`
  (or `ANTHROPIC_API_KEY`), paste the value, save.

  **Verification.** Push a no-op commit to `main` and confirm the
  `claude-cli-fixtures` job runs (rather than failing with the
  "no Claude auth available" message). The first successful run is
  the credential proof; thereafter every push to `main` exercises the
  live fixtures.

  **Rotation.** OAuth tokens expire. When CI starts failing on the
  install step, refresh with `claude /login` locally, re-extract the
  token, and re-set the secret. Tokens cannot be displayed after
  setting — only overwritten.

  **Forks.** Forks cannot read this secret (GitHub policy). The CI
  workflow detects PRs without auth and emits a warning instead of
  failing, so forks can still open PRs that pass non-live gates. The
  hard gate fires only on `push` events to `refs/heads/main` in the
  upstream repo.
- **The fallback YAML parser in `polymath-flow` only folds block
  scalars.** It does not preserve newlines (`|` and `>` are both
  treated as folded). Workflows that depend on newline-preserving
  prompts must rely on PyYAML being present.
- **No cost telemetry.** The bakeoff scorer reports a numeric score
  and a delta, but does not yet report token cost per case. Two
  runs that produce equivalent scores at different costs look
  identical to the harness today.
- **No multi-version migration story.** When the workflow schema
  bumps from 0.1 to 0.2, the catalog's existing workflows will need
  a coordinated migration; the tooling for that is not built.
- **No skill-versioning.** Skills evolve in place; there is no
  per-skill semver, so a workflow that depends on a particular
  skill's behaviour cannot pin it.

## 5. What we would refuse to do today

- We would refuse to claim a plugin is `stable` without a passing
  bakeoff case that exercises its primary skill at score ≥ 8/10
  with a delta of at least 2 points over baseline.
- We would refuse to promote a connector to `stable` while its
  `polymath_value` row in `docs/CONNECTOR-POLICY.md` is empty.
- We would refuse to merge a new agent without a no-agent baseline
  evidence record and a matching golden fixture (enforced by
  `AGENT-1` in `tools/conformance.sh`).
- We would refuse to publish customer-facing release notes claiming
  the marketplace "produces better software work than baseline
  Claude Code" until the bakeoff has been run and the artifacts are
  checked in.

## 6. What would change this document

- A published bakeoff run that meets the `9+ Promotion Bar` in
  `docs/QUALITY-SCORECARD.md` would remove § 1's first two bullets.
- An external user adopting a `stable` plugin would remove § 1's
  third bullet.
- Cost telemetry in the bakeoff harness would remove § 4's third
  bullet.
- A coordinated workflow-schema migration would remove § 4's fourth
  bullet.

Reviewers who find a claim here that is no longer true should open a
PR that updates this file and the relevant section of
`docs/QUALITY-SCORECARD.md` in the same commit.
