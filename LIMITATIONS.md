# Limitations

The deliberate counterweight to [`README.md`](README.md). This file records
what Polymath is *not* good at, where official tools beat it, and what
the maintainer would not yet trust the catalog with. Read it before the
catalog if you care about depth more than breadth.

Every line below is a falsifiable claim; the absence of a counter-claim
elsewhere is intentional.

## 1. What the catalog does not prove

- The catalog **does not** prove it produces better artifacts than
  baseline Claude Code on a measured set of tasks. The bakeoff harness
  exists ([`tools/bakeoff.py`](tools/bakeoff.py), nine cases under
  [`tests/bakeoff/<plugin>/<scenario>/case.json`](tests/bakeoff/)), the
  LLM-judge in [`tools/bakeoff/judge-prompt.md`](tools/bakeoff/judge-prompt.md)
  can run on demand, but no live run is published. The central
  product thesis is unconfirmed.
- The catalog **has no external users.** Until at least one stable
  plugin has a recorded external adopter, the promotion bar in
  [`docs/QUALITY-SCORECARD.md`](docs/QUALITY-SCORECARD.md) blocks
  every catalog plugin from `stable`. As of today, no plugin in the
  catalog is `stable`.

## 2. Where official tools beat Polymath

- **Language facts and APIs.** For any factual question about a
  language feature, API signature, or LSP behaviour, the official
  docs and LSPs beat any Polymath skill. Polymath defers to external
  catalogs such as [dotnet/skills](https://github.com/dotnet/skills),
  [Laravel Boost](https://laravel.com/docs/12.x/boost), and Python
  skill collections listed at [agentskills.io](https://agentskills.io).
  Projects declare which external catalogs they recommend in
  `.polymath/project.yaml` (`external_skills:`).
- **Service integrations with official MCPs.** Where an official MCP
  exists (GitHub, Jira, Linear, Datadog, Sentry, PagerDuty, Snyk, …),
  the official surface is the source of truth for tool calls. The
  Polymath connector is justified only by the workflow shape, safety
  opinion, or critique it adds, recorded per plugin in
  [`docs/CONNECTOR-POLICY.md`](docs/CONNECTOR-POLICY.md). Connectors
  are now **eligible for `beta` and `stable`** — but only after
  primary-source distinct-value proof is published in
  [`registry/stability-evidence.json`](registry/stability-evidence.json)
  as `distinct_value_url`. The previous "stay experimental" default
  has been replaced by an evidence gate.
- **Cloud resource operations.** For one-off operations against AWS /
  GCP / Azure / Kubernetes, the official MCP families plus the vendor
  CLI are faster and safer than any Polymath wrapper.
  `polymath-infra-*` is justified only when a multi-environment
  workflow, RBAC audit, or destructive-action checklist is the actual
  question. Infra plugins follow the same `distinct_value_url`
  evidence gate as connectors before promoting above experimental.

## 3. Where the catalog is intentionally thin

- **`polymath-ai`** ships three skills (`rag-design`, `prompt-engineer`,
  `eval-plan`). An AI-craft showcase deserves more depth, but the
  catalog prefers to defer to specialised AI-tooling catalogs over
  building shallow surfaces here. Promotion to `stable` is gated on a
  passing bakeoff case for at least one of the three skills.
- **`polymath-data`** is deliberately narrow: SQL authoring + plan
  reading, metric trees, experiment design. Schema migrations
  cross-link to [`polymath-backend:migration-plan`](plugins/polymath-backend/skills/migration-plan/SKILL.md)
  and [`polymath-backend:review-migration`](plugins/polymath-backend/skills/review-migration/SKILL.md).
  Data pipelines / ETL / orchestration and data-science / model
  evaluation are deferred to external catalogs (dbt, Airflow / Dagster
  community docs, ML / AI skill collections) until a Polymath workflow
  shape is load-bearing. See
  [`plugins/polymath-data/README.md`](plugins/polymath-data/README.md)
  for the scope statement.
- **Agents are intentionally rare.** Polymath only ships agents when
  a no-agent baseline + a golden fixture demonstrates forked context
  is load-bearing rather than decorative.
- **Maturity is conservative.** All plugins start at `experimental`.
  The canonical promotion bars live in [`docs/MATURITY.md`](docs/MATURITY.md):
  `beta` is granted on closed on-disk evidence (bakeoff + triggering
  fixtures, or a foundation-runner with unit + e2e coverage); `stable`
  further requires a live bakeoff ≥ 8 / delta ≥ 2 **and** at least one
  external user beyond the maintainer. Every status claim is backed by
  the evidence ledger at
  [`registry/stability-evidence.json`](registry/stability-evidence.json)
  (enforced by `tools/check-stability-evidence.py`, rule `STABILITY-1`).
  No plugin in the catalog is `stable` today.

## 4. Known operational gaps

- **Live-model fixtures are currently disabled.** Only the jobs that
  call a real model are off: `claude-cli-fixtures` in
  [`.github/workflows/golden-tests.yml`](.github/workflows/golden-tests.yml.disabled)
  and `live-bakeoff` in
  [`.github/workflows/evaluation.yml`](.github/workflows/evaluation.yml.disabled)
  were disabled (renamed to `*.yml.disabled`) to avoid spending Claude
  API budget on every push. The six token-free deterministic jobs that
  used to share `golden-tests.yml` (executable unit tests, the
  shipFeature scratch-repo e2e, the hollow-run falsifiability anchor,
  golden-fixture frontmatter parsing, skill-triggering frontmatter, and
  bakeoff-case parsing) now run on every PR and push in
  [`.github/workflows/golden-deterministic.yml`](.github/workflows/golden-deterministic.yml)
  — they are **not** disabled. So CI still proves the executable
  workflow runner, the gate hardening, and fixture well-formedness; what
  it does not prove while the live jobs are off is real model behaviour.
  To re-enable the live gate: rename the `*.yml.disabled` files back and
  set `CLAUDE_CODE_OAUTH_TOKEN` (or `ANTHROPIC_API_KEY`) in repo secrets.
- **The fallback YAML parser in `polymath-flow` folds block scalars.**
  `|` and `>` are both treated as folded — newlines collapse to
  spaces. Workflows that depend on newline-preserving prompts must
  rely on PyYAML being present.
- **No per-case cost telemetry in the bakeoff.** The scorer reports a
  numeric score and a delta, not token cost. Two runs that produce
  equivalent scores at different costs look identical today.
- **No skill-versioning.** Skills evolve in place. A workflow that
  depends on a particular skill's behaviour cannot pin it.
- **No multi-version workflow-schema migration tooling.** When the
  workflow schema bumps from `0.1` to `0.2`, the migration will need
  to be coordinated by hand.

### 4.1 Providing the Claude Code auth secret

The maintainer enables the live CI gate once per repo:

**Preferred — Claude.ai subscription OAuth token.** Same token Claude
Code's `/login` flow stores locally; the cheapest option per call.

```bash
# On the maintainer's machine, after a fresh `claude /login`:
cat ~/.claude/oauth.json | jq -r .access_token

# Add it to the repo (requires `gh auth login` first):
gh secret set CLAUDE_CODE_OAUTH_TOKEN \
  --repo MohammadBafkar/Polymath \
  --body "$(cat ~/.claude/oauth.json | jq -r .access_token)"
```

**Alternative — Anthropic API key.** Per-token billing.

```bash
gh secret set ANTHROPIC_API_KEY \
  --repo MohammadBafkar/Polymath \
  --body "sk-ant-..."
```

**UI alternative.** GitHub → repo → Settings → Secrets and variables
→ Actions → New repository secret → name `CLAUDE_CODE_OAUTH_TOKEN`
(or `ANTHROPIC_API_KEY`), paste the value, save.

**Verification.** Push a no-op commit to `main`; confirm the
`claude-cli-fixtures` job runs (rather than failing with the
"no Claude auth available" message).

**Rotation.** OAuth tokens expire. Refresh with `claude /login` and
re-set the secret. Tokens cannot be displayed after setting — only
overwritten.

**Forks.** Forks cannot read repo secrets (GitHub policy). The CI
workflows detect PRs without auth and emit a warning instead of
failing. The hard gate fires only on `push` events to
`refs/heads/main` in the upstream repo.

## 5. What the maintainer refuses to do

- Refuses to claim a plugin is `stable` without a passing bakeoff
  case at score ≥ 8/10 with delta ≥ 2 over baseline.
- Refuses to promote a connector to `stable` while its `polymath_value`
  row in [`docs/CONNECTOR-POLICY.md`](docs/CONNECTOR-POLICY.md) is
  empty.
- Refuses to ship a new agent without a no-agent baseline + a golden
  fixture proving forked context is load-bearing.
- Refuses to publish customer-facing release notes claiming the
  marketplace "produces better software work than baseline Claude
  Code" until at least three bakeoff cases meet the threshold.

## 6. What would change this document

- A published bakeoff run meeting the
  [`QUALITY-SCORECARD.md`](docs/QUALITY-SCORECARD.md) bar would
  remove § 1's first bullet.
- An external user of any plugin would remove § 1's second bullet.
- Cost telemetry in the bakeoff harness would remove a § 4 bullet.
- A coordinated workflow-schema migration would remove another § 4
  bullet.

If you find a claim here that is no longer true, open a PR updating
this file and the relevant section of
[`docs/QUALITY-SCORECARD.md`](docs/QUALITY-SCORECARD.md) in the same
commit.
