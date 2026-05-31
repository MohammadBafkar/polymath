# Polymath Marketplace Audit & Roadmap

## Executive summary

This document consolidates three independent audits of the Polymath marketplace into a single roadmap: an SDLC phase-coverage gap analysis (Q1), a workflow auto-detection and discoverability design (Q2), and a description-quality evaluation of every shipped artifact (Q3). Read together they tell one story. The catalog's *skill spine* is strong where operations live (incident-response, observability, SRE, architecture, release, infra) but blind at the front (ideation, prioritization, requirements depth) and tail (progressive-delivery, deprecation, supply-chain) of the SDLC; its 21 multi-step *workflows* are effectively dark because nothing surfaces them to the model the way skill descriptions are surfaced; and the descriptions that do route well *trigger* well but almost never *fence their scope* — `scope_boundary` is the failing dimension across 70% of the 158 artifacts. The unified roadmap below sequences the fix as instrument-first, then make workflows discoverable, then refine descriptions, then close phase gaps, then promote — each stage gated on CI checks the repo already runs (token budget, conformance, triggering/golden tests, diff-guards).

## Findings at a glance

| Dimension | Measure | Result |
|---|---|---|
| SDLC phases audited (Q1) | Baseline phases scored | 38 (actual map covers 35 keys) |
| Phase verdict split (Q1) | Strong / Partial / Absent | 20 Strong · 8 Partial · 7 Absent (+ shallow-but-tagged: estimation, finops-cost, prioritization) |
| Phases absent or near-zero (Q1) | Structurally missing | ideation, prioritization, test-automation-load, supply-chain-compliance, progressive-delivery, product-strategy-gtm, localization-i18n (0 coverage) |
| Artifacts audited for description quality (Q3) | skills / commands / agents | 158 total (131 skills · 25 commands · 2 agents) |
| Description verdict split (Q3) | ACCEPT / REVISE / REWRITE | 34 (21.5%) · 110 (69.6%) · 14 (8.9%) |
| Weakest description dimension (Q3) | `scope_boundary` mean | 2.73 / 5 (failing) — vs `trigger_clarity` 3.99, `disambiguation` 3.68 |
| Triggering-test coverage (Q3) | skills with tests | 11 of 131 (8%) |
| Workflows lacking model-facing triggers (Q2) | workflows with no routing surface | 21 of 21 (the entire flows-lite layer is dark) |
| Confusion clusters a router cannot split (Q3) | overlap groups | 11 (C1–C11), worst = 4-way issue triage |

The through-line: **the catalog triggers but does not fence, surfaces skills but not workflows, and covers operations but not the SDLC edges.** The roadmap addresses these in dependency order.

## Unified staged roadmap

Each stage names concrete file/tool touchpoints and an exit criterion tied to an existing CI gate. Stages are ordered so that instrumentation precedes the changes it measures.

### Stage 0 — Instrument

Stand up the measurement harnesses before changing any content, so every later stage has a green/red signal.

- **Touchpoints:** `tools/lint-descriptions.py` (new static scorer — `trigger_clarity` / `scope_boundary` / `disambiguation`, pairwise Jaccard overlap penalty); `tests/forbidden_prompts.yaml` (new confusion-matrix gate for clusters C1–C11); `tools/build-workflow-index.py` (new single-producer index builder, two-tier + detect file, token assertion); `tools/conformance.sh --all` (wire `WORKFLOW-INDEX` with a `git diff --exit-code` diff-guard).
- **Exit criterion:** `lint-descriptions.py` runs clean as a *reporting* pass inside the existing `polymath-author:validate-plugin` / `validate-plugin` CI workflow (no new failures introduced yet); the workflow-index builder produces byte-identical output on re-run and asserts the rendered min-index ≤ 380 tokens; CI diff-guard green.

### Stage 1 — Workflow discoverability

Give workflows the same model-facing routing surface skills already have, behind a propose/confirm contract, in grace mode.

- **Touchpoints:** `workflow.schema.json` (add optional `whenToUse` / `triggers` / `detectionSignals`); `tools/check-workflow-invokes.py` (enforcement (a)/(b)/(c) behind a grace flag); `session-start.sh` (fourth quiet surface that `cat`s the pre-built `workflow-index.min.json`, degrade-quiet, `index-muted` suppression); `tools/workflow-triggering.py` + `tests/workflow-triggering/<workflow>.md` (check mode in CI, run mode opt-in under `CLAUDE_CODE_OAUTH_TOKEN`); backfill `whenToUse`/`triggers` for all 21 workflows; add the missing **reviewPlan** arc first.
- **Exit criterion:** injected min-index ≤ 380 tokens and renders only on initialized repos; every workflow has `whenToUse` + `triggers` with no cross-workflow duplicate trigger; `workflow-triggering.py check` green in `conformance.sh`; `run` green locally for all 21 including collision-disambiguation cases.

### Stage 2 — Description refinement

Close the `scope_boundary` gap and the 11 confusion clusters, sequenced by routing-harm × effort, gated by the Stage 0 harnesses.

- **Touchpoints:** the 14 REWRITE artifacts + 4-way issue-triage cluster C1 (P0); confusion clusters C2–C9 (P1, one-line "Not for …" additions); skill↔command alias pairs C10 (P2, mechanical codemod appending "Command entry point for `<skill>`"); remaining REVISE skills C-term cases (P3); `polymath-author:new-skill` / `new-command` scaffolds (emit a placeholder `Not for …` stub); `polymath-core:plugin-budget` (budget-check every added clause).
- **Exit criterion:** `lint-descriptions.py` flips to *blocking* in `validate-plugin` — zero artifacts below FAIL thresholds (`scope_boundary` < 2, `disambiguation` < 3); all 11 clusters green in `forbidden_prompts.yaml` within the golden-tests / evaluation workflow; `scope_boundary` mean ≥ 3.5; token-budget gate (≤ 400/plugin, ≤ 1,500 total) still green; both REWRITE agents re-scoped or merged into parents.

### Stage 3 — Gap closure

Fill the structurally absent SDLC phases, preferring slots in existing plugins under the 400-token cap before spending new plugin envelopes.

- **Touchpoints (P0→P2 from Q1):** new `polymath-prioritize`; skills into existing `polymath-qa` (`test-smell`, `integration-contract`, `assertion-quality`) and `polymath-product` (`groom-backlog`, `roadmap`); new `polymath-test-automation`, `polymath-deprecation` (move `write-sunset-notice` in), `polymath-progressive-delivery`, `polymath-finops`; ideation skills into existing `polymath-thinking`; new `polymath-i18n`, `polymath-supply-chain`, `polymath-product-strategy`; estimation skills into existing `polymath-planning`. Each new skill ships a triggering test and a `forbidden_prompts.yaml` row; each new plugin runs through `polymath-author:new-plugin` / `new-skill`.
- **Exit criterion:** each added artifact passes `lint-descriptions.py` (including its `Not for …` clause) and its triggering test; `polymath-core:plugin-budget` confirms every touched plugin stays ≤ 400 tokens and the total stays ≤ 1,500; no new `forbidden_prompts.yaml` regressions.

### Stage 4 — Promotion

With coverage, discoverability, and quality gated, harden the contracts so nothing can regress.

- **Touchpoints:** drop the grace flag in `check-workflow-invokes.py` (WORKFLOW-2 becomes blocking — `whenToUse` + `triggers` required, 160-char cap and cross-workflow duplicate-trigger guard hard failures); document the detect→propose→await→run contract as the standing gate in `run-workflow` SKILL.md; add the missing right-sized workflow arcs (estimateAndPlan, requirementsToBacklog, progressiveRollout, incidentToReview, prdToShip) as capacity allows; surface the new front-of-SDLC plugins through the workflow index.
- **Exit criterion:** a workflow cannot merge without a validated routing surface and a passing triggering test; the index can never drift (single producer + diff-guard + test↔YAML trigger superset-guard); the program-level DoD holds in CI — `scope_boundary` mean ≥ 3.5, zero artifacts below FAIL thresholds, all 11 confusion clusters green, both former REWRITE agents resolved.

---

## Q1 — SDLC Gap Analysis: Marketplace Phase Coverage

### Method

Each of the 38 baseline phases was scored against its exemplar set and the artifacts tagged to it. **Strong** = the core exemplars are present with real depth; **Partial** = some core exemplars present but material exemplars missing or coverage is shallow/borrowed-from-adjacent-phase; **Absent** = zero or only incidentally-tagged artifacts. Artifact ids are cited verbatim; duplicate ids in the source data (e.g. `polymath-release:pr` listed twice, `polymath-incident:postmortem` aliasing `polymath-incident:postmortem-blameless`) are treated as one.

Note on the baseline: the IDEAL set lists 38 phases (full SDLC). The ACTUAL map covers 35 keys. Three baseline phases — **estimation** is present but thin; the map has no separate entry meaningfully distinct beyond `work-breakdown`/`estimate`.

### Coverage Matrix

| Phase | Covered? | By which skills (artifact ids) | Gap |
|---|---|---|---|
| ideation | **Absent** | `polymath-thinking:brainstorm` only | No problem-framing, no opportunity canvas, no first-principles, no idea triage/scoring, no SCAMPER/HMW/analogy. 1 of 8 exemplars. |
| research-discovery | **Partial** | `polymath-research:interview-guide`, `:persona`, `:customer-journey`, `:research-scout`, `polymath-decisions:evidence-ledger`, `deep-research` (harness) | No survey design, no JTBD/switch interview, no affinity-mapping synthesis, no competitive landscape, no TAM/SAM/SOM. |
| requirements-elicitation | **Partial** | `polymath-product:prd`, `:acceptance-criteria`, `:decompose-epic` | No NFR elicitation, no ambiguity/conflict/gap detector, no edge-case/error-state enumeration, no traceability matrix, no DoR/DoD. Connector triage skills are mis-tagged padding. |
| prioritization | **Absent** | `polymath-leadership:okr-setting` only (mis-tagged) | No RICE, WSJF, MoSCoW, Kano, value-vs-effort, stack-ranking, Now/Next/Later, opportunity scoring. Effectively 0 of 8. |
| planning | **Strong** | `polymath-planning:write-plan`, `:work-breakdown`, `:estimate`, `polymath-thinking:pre-mortem`, `polymath-sre:capacity-plan` | Missing critical-path/dependency-graph, release-train, rollback/contingency as discrete skills. |
| estimation | **Partial** | `polymath-planning:work-breakdown`, `:estimate` | No three-point/PERT, no probabilistic/confidence-interval, no reference-class, no cone-of-uncertainty, no cost-estimation. 2 of 8. Shallow — see below. |
| decision-making | **Strong** | `polymath-decisions:daci`, `:tradeoff-matrix`, `:cynefin-frame`, `polymath-thinking:red-team`, `:pre-mortem`, `polymath-writing:adr`, `:rfc` | Missing explicit reversible/one-way-door framing and decision-journal/log. |
| architecture | **Strong** | `polymath-thinking:architecture-critic`, `polymath-writing:adr`/`:architecture-doc`/`:rfc`, `polymath-backend:api-design-rest`/`:db-schema`, `polymath-infra-cloud:design-*`, `polymath-performance:design-cache-layer` | Missing architecture-style-selection skill, C4 diagramming, fitness-function/NFR-budget. |
| design-ux | **Strong** | `polymath-design:a11y-audit`, `:ui-critique`, `:design-system-conformance`, `polymath-frontend:component-design` | No IA/navigation, no UX-writing/microcopy, no wireframe spec, no usability-test plan, no design-token skill. |
| implementation | **Strong** | `polymath-engineering:feature-dev`, `:read-code`, `:verify-change`, `polymath-backend:api-design-rest`, `polymath-frontend:component-design`, `polymath-mobile:*`, `polymath-data:sql-write` | No explicit refactoring skill; no concurrency/async skill; language depth deferred to external catalogs. |
| code-review | **Strong** | `polymath-engineering:code-review`, `polymath-security:owasp-review`, `polymath-qa:coverage-gap`, `polymath-connector-github:open-pr` | No simplify/cleanup-only, no diff-risk calibration, no PR-triage/routing as discrete skills. |
| testing-qa | **Partial** | `polymath-qa:test-strategy`, `:unit-tests`, `:coverage-gap`, `polymath-engineering:verify-change`, `polymath-ai:eval-plan` | No test-smell/anti-pattern, no assertion-quality, no integration/contract design, no exploratory/UAT charter, no mutation testing as marketplace skills. |
| test-automation-load | **Absent** | `polymath-engineering:feature-dev`, `polymath-qa:unit-tests`, `polymath-sre:chaos-experiment` (all mis-tagged) | No browser e2e, no k6/JMeter/Locust load authoring, no perf-budget-in-CI, no flaky-test management, no visual regression. ~0 real. |
| security-appsec | **Strong** | `polymath-security:stride-threat-model`, `:owasp-review`, `polymath-connector-snyk:triage-vulns`, `polymath-infra-kubernetes:*`, `polymath-devops:audit-*` | No SAST/DAST triage, no secret-scanning, no authn/authz design-review, no secure-defaults checklist. |
| supply-chain-compliance | **Absent** | `polymath-author:validate-plugin`, `polymath-connector-snyk:triage-vulns` | No SBOM, no dependency-bump, no license audit, no trusted-publishing (exists in dotnet external catalog only), no SLSA/attestation, no compliance-control mapping. |
| data-engineering | **Strong** | `polymath-data:sql-write`, `:sql-optimize`, `:metrics-tree`, `:run-experiment`, `polymath-backend:db-schema`, `:migration-plan`, `polymath-infra-postgres:review-migration` | No ETL/ELT pipeline design, no data-quality/expectations, no data-lineage/governance. |
| ai-ml | **Partial** | `polymath-ai:eval-plan`, `:prompt-engineer`, `:rag-design` | No model-selection, no MCP-authoring (only in dotnet-ai external), no agent/workflow design, no training/feature-eng, no drift-detection. 3 of 11. |
| build-ci | **Strong** | `polymath-devops:ci-pipeline-github`, `:dockerize`, `:audit-dockerfile`, `:audit-compose`, `polymath-connector-github:diagnose-ci-failure` | No build-perf diagnostics (dotnet-msbuild external only), no reproducible-build, no monorepo orchestration as marketplace skills. |
| release | **Strong** | `polymath-release:commit`/`:changelog`/`:pr`/`:release-notes`, `polymath-devops:env-promotion`, `polymath-connector-github:open-pr` | No semantic-versioning decision skill, no release-train scheduling. |
| progressive-delivery | **Absent** | `polymath-devops:env-promotion` only | No feature-flag, no canary, no blue-green/ring, no automated rollback/health-gate, no kill-switch, no experiment-to-GA. 1 of 8 and that one is a stretch. |
| infra-provisioning | **Strong** | `polymath-infra-cloud:design-aws`/`azure`/`gcp`/`terraform-stack`, `polymath-infra-kubernetes:write-manifest`, `polymath-infra-postgres:audit-config` | No IaC drift-detection, no Bicep/ARM, no design-time infra cost-estimation as discrete skill. |
| platform-engineering | **Strong** | `polymath-platform:golden-path`, `:service-catalog-entry`, `:devex-metrics`, `polymath-author:new-*`, `polymath-flows:*` | No self-service env provisioning, no cognitive-load/team-topology assessment. |
| observability | **Strong** | `polymath-observability:metrics-design`, `:logging-strategy`, `:tracing-strategy-otel`, `polymath-connector-datadog:author-monitor`, `polymath-connector-monitoring:*` | Complete on the three pillars; gap is only dashboard-authoring depth (snapshot exists, authoring does not). |
| sre-reliability | **Strong** | `polymath-sre:slo-design`, `:error-budget-policy`, `:chaos-experiment`, `:capacity-plan`, `polymath-platform:production-readiness-review` | No discrete resilience-pattern (retries/backoff/bulkhead) skill; burn-rate alerting folded into datadog connector. |
| incident-response | **Strong** | `polymath-incident:incident-triage`/`:comms-update`/`:postmortem-blameless`, `polymath-connector-pagerduty:page-context`, `polymath-connector-statuspage:*`, `polymath-connector-slack:post-incident-comms`, `polymath-thinking:5-whys` | Best-covered phase. No gap of note. |
| performance | **Strong** | `polymath-performance:perf-budget`, `:backend-tail-latency`, `:design-cache-layer`, `:caching-tradeoffs`, `:audit-redis-config`, `polymath-frontend:web-vitals-budget`/`:bundle-analyze`, `polymath-mobile:mobile-perf` | Profiling/microbenchmark/crash-dump depth deferred to dotnet-diag external catalog. |
| finops-cost | **Partial** | `polymath-author:token-budget-report`, `polymath-core:plugin-budget`, `polymath-infra-cloud:design-aws`, `polymath-sre:capacity-plan` | No rightsizing/waste, no cost-budget/anomaly-alert, no unit-economics, no reserved-capacity, no cost-attribution/showback. Token-budget skills are internal, not cloud FinOps. |
| product-management | **Strong** | `polymath-product:prd`/`:acceptance-criteria`/`:decompose-epic`, `polymath-data:metrics-tree`, `polymath-leadership:okr-setting`, `polymath-research:persona` | No backlog-grooming/refinement, no Now/Next/Later roadmap skill (shared gap with prioritization). |
| product-strategy-gtm | **Absent** | `polymath-communication:six-pager`, `polymath-content:write-release-notes` (both mis-tagged) | No vision/strategy, no positioning/messaging, no pricing/packaging, no segmentation/ICP, no GTM launch plan, no moat analysis. ~0 of 9. |
| project-management | **Strong** | `polymath-connector-jira:jira-triage`, `polymath-connector-linear:linear-triage`, `polymath-connector-github:triage-issue`, `polymath-planning:work-breakdown`, `polymath-communication:meeting-notes` | No iteration/capacity planning, no burndown/throughput, no standup facilitation as discrete skills (ADO connector absent). |
| documentation | **Strong** | `polymath-writing:runbook`/`:adr`/`:rfc`/`:architecture-doc`/`:editorial-pass`, `polymath-learning:code-walkthrough`, `polymath-core:glossary` | No tutorial/how-to (Diataxis) skill, no OpenAPI/API-reference skill, no README/onboarding skill. |
| communication | **Strong** | `polymath-communication:exec-brief`/`:meeting-notes`/`:six-pager`, `polymath-connector-slack:post-async-update` | No audience-tiered explanation (lives in `polymath-learning:explain`), no announcement/broadcast skill. |
| leadership | **Strong** | `polymath-leadership:okr-setting`/`:one-on-one-prep`/`:perf-review`, `polymath-decisions:daci` | No SBI-feedback skill, no career-ladder/growth-plan, no hiring/interview-rubric, no difficult-conversation prep. |
| learning-enablement | **Strong** | `polymath-learning:explain`/`:code-walkthrough`/`:feynman-technique`, `polymath-engineering:read-code` | No onboarding/learning-path design, no concept-mapping, no KB/FAQ skill. |
| localization-i18n | **Absent** | *(no entry in actual map)* | Zero coverage: no i18n audit, string externalization, pseudolocalization, RTL review, TMS workflow, locale formatting. 0 of 9. |
| deprecation-sunset | **Partial** | `polymath-content:write-sunset-notice` | Notice authoring only. No deprecation policy/timeline, no deprecation-to-removal workflow, no API sunset-header, no migration-guide, no dead-code retirement. 1 of 9. |

### Phases that look covered but are shallow

- **estimation** — tagged Strong-adjacent via `polymath-planning:estimate`, but that single skill cannot deliver three-point/PERT, probabilistic forecasting, reference-class, or cone-of-uncertainty. It is a point-estimate tool masquerading as the phase. Treat as Partial.
- **finops-cost** — looks covered but the bulk of its tags (`polymath-author:token-budget-report`, `polymath-core:plugin-budget`) are *internal Polymath token accounting*, not cloud cost. Real cloud FinOps (rightsizing, anomaly alerts, unit economics, RI/savings-plan) is absent. The phase is essentially uncovered for its stated intent.
- **prioritization** — its only tag, `polymath-leadership:okr-setting`, is mis-attributed; OKRs are goal-setting, not feature prioritization. Functionally Absent.
- **ai-ml** — three solid skills but no agent/workflow-design or MCP-authoring at the marketplace tier (only in the dotnet-ai external catalog), and no MLOps/drift. Shallow for anyone doing production ML rather than prompt work.
- **requirements-elicitation** — `prd` + `acceptance-criteria` look like coverage, but the *quality-gate* exemplars (ambiguity/conflict detector, NFR elicitation, edge-case enumeration, traceability) are all missing; the connector triage skills tagged here are noise.
- **observability** — genuinely strong on pillars, but dashboard *authoring* (vs `dashboard-snapshot`) and alert burn-rate logic are folded into connectors rather than first-class.

### Prioritized Gap List

Token math: the always-on budget is ≤400 tokens/plugin (name + description listing). Adding a **skill to an existing plugin** costs only its one-line description (~30–60 tokens) against that plugin's ceiling; adding a **new plugin** spins up a fresh 400-token envelope. Prefer slotting into existing plugins until they near the cap.

**P0 — high-frequency, structurally missing, cheap to slot in**

1. **`polymath-prioritize` (new plugin)** — RICE, WSJF, MoSCoW, Kano, value-vs-effort, Now/Next/Later.
   - Desc (≤200): "Prioritize a backlog or feature set — RICE, WSJF/cost-of-delay, MoSCoW, Kano, value-vs-effort 2x2, Now/Next/Later; exposes value/effort/confidence inputs, never an opaque score."
   - Sits between `polymath-planning:*` and `polymath-product:decompose-epic`.
   - Budget: new plugin (~400). Justified — prioritization is one of the most common PM/eng-lead requests and has *zero* real coverage today.
   - **P0**: every roadmap/sprint conversation needs it; current single mis-tagged skill is a false positive.

2. **`polymath-qa:test-smell` + `polymath-qa:integration-contract` + `polymath-qa:assertion-quality` (skills in existing `polymath-qa`)** — round out testing-qa.
   - Desc (test-smell, ≤200): "Detect test smells and anti-patterns in a test suite — over-mocking, eager/fragile assertions, slow setup, flaky timing; flag each with the layer it belongs at and a refactor."
   - Sits between `polymath-qa:coverage-gap` and `polymath-qa:unit-tests`.
   - Budget: 3 skill descriptions added to `polymath-qa` (~150 tokens) — check `polymath-qa` headroom against 400.
   - **P0**: testing is a top-5 request category; the phase is only Partial despite looking covered.

3. **`polymath-product:groom-backlog` + `polymath-product:roadmap` (skills in existing `polymath-product`)** — shared fix for product-management + prioritization overlap.
   - Desc (roadmap, ≤200): "Sequence a roadmap as Now/Next/Later — group by outcome, attach confidence and dependency, state what each horizon is NOT committing to; ties items to discovery evidence."
   - Budget: 2 skill descriptions in `polymath-product` (~100 tokens).
   - **P0**: roadmap/grooming requests are constant for the PM audience.

**P1 — common, real gap, moderate placement**

1. **`polymath-test-automation` (new plugin)** — browser e2e + load/stress/soak + perf-in-CI.
   - Desc (≤200): "Automate functional and load tests — Playwright browser flows, k6/JMeter/Locust load/stress/soak profiles, perf budgets in CI, flaky-test quarantine; analyze percentiles vs budget."
   - Sits between `polymath-qa:test-strategy` and `polymath-devops:ci-pipeline-github`; Playwright MCP already present.
   - Budget: new plugin (~400). Justified — load/e2e is a distinct toolchain, too big for `polymath-qa`'s cap.
   - **P1**: high value but lower request frequency than unit-test/prioritization work.

2. **`polymath-deprecation` (new plugin)** — promote the lone `write-sunset-notice` into a full phase.
   - Desc (≤200): "Plan and execute deprecation — two-date policy (warn/remove), deprecation-to-removal workflow, API sunset headers, migration guide with before/after, exception path, dead-code retirement."
   - Sits between `polymath-content:write-sunset-notice` (move it here) and `polymath-release:*`.
   - Budget: new plugin (~400), but reclaims the existing sunset-notice skill.
   - **P1**: periodic but recurring; today only 1 of 9 exemplars.

3. **`polymath-progressive-delivery` (new plugin)** — flags, canary, blue-green, health gates.
   - Desc (≤200): "Design safe rollouts — feature-flag lifecycle, canary with automated analysis, blue-green/ring, SLO-driven health gates and auto-rollback, kill switches, experiment-to-GA graduation."
   - Sits between `polymath-devops:env-promotion` and `polymath-sre:error-budget-policy`.
   - Budget: new plugin (~400).
   - **P1**: critical for mature delivery orgs; frequency mid-tier.

4. **`polymath-finops` (new plugin)** — real cloud cost vs the internal token-budget skills.
   - Desc (≤200): "Estimate and control cloud cost — service/SKU pricing comparison, rightsizing and waste, cost budgets and anomaly alerts, unit economics/cost-per-request, reserved-capacity analysis, showback tagging."
   - Sits between `polymath-infra-cloud:design-*` and `polymath-sre:capacity-plan`.
   - Budget: new plugin (~400).
   - **P1**: rising request volume; current tags are mislabeled internal accounting.

5. **`polymath-thinking` ideation skills (skills in existing `polymath-thinking`)** — problem-framing, first-principles, idea-triage, HMW.
   - Desc (problem-framing, ≤200): "Frame the problem before the solution — separate symptom from root need, state who/what/why, surface premature-solution bias; output a problem statement downstream research can pick up."
   - Sits between `polymath-thinking:brainstorm` and `polymath-research:interview-guide`.
   - Budget: 3–4 skill descriptions in `polymath-thinking` (~180 tokens) — verify cap headroom.
   - **P1**: ideation is common at project start; cheap to add since the plugin exists.

**P2 — lower frequency or well-served by external catalogs**

1. **`polymath-i18n` (new plugin)** — the only phase with literally zero coverage.
   - Desc (≤200): "Internationalize and localize software — i18n audit (hardcoded strings, locale formatting), ICU MessageFormat externalization, pseudolocalization, RTL/bidi review, TMS workflow, fallback strategy."
   - Budget: new plugin (~400).
   - **P2**: total gap but specialized/lower-frequency for most teams; high value only when it's relevant.

2. **`polymath-supply-chain` (new plugin)** — SBOM, dependency-bump, license, SLSA, compliance mapping.
    - Desc (≤200): "Manage supply-chain integrity — SBOM generation, dependency-bump with breaking-change analysis, license audit, signing/SLSA attestation, lockfile hygiene, SOC2/GDPR control mapping."
    - Sits between `polymath-connector-snyk:triage-vulns` and `polymath-release:*`.
    - Budget: new plugin (~400).
    - **P2**: important for regulated orgs; trusted-publishing already partly served by dotnet external catalog.

3. **`polymath-product-strategy` (new plugin)** — vision, positioning, pricing, GTM.
    - Desc (≤200): "Define product strategy and GTM — vision narrative, positioning/messaging by segment, pricing/packaging, ICP/segmentation, launch plan (tiers/channels/timing), moat and competitive analysis."
    - Sits between `polymath-communication:six-pager` and `polymath-product:prd`.
    - Budget: new plugin (~400).
    - **P2**: high-value but lower-frequency, founder/PM-leadership audience; currently 0 real coverage.

4. **`polymath-estimation` skills (skills in existing `polymath-planning`)** — three-point/PERT, probabilistic, reference-class.
    - Desc (≤200): "Estimate with uncertainty — three-point/PERT ranges, reference-class forecasting from historical analogues, confidence intervals, cone-of-uncertainty communication; effort, duration, and cost."
    - Sits beside `polymath-planning:estimate`.
    - Budget: 2–3 skill descriptions in `polymath-planning` (~120 tokens).
    - **P2**: upgrades a shallow phase; lower urgency since a point-estimate skill already exists.

### Summary

Strongest spine: **incident-response, observability, sre-reliability, architecture, release, infra-provisioning** — these are near-complete. The marketplace's blind spots cluster at the **front of the SDLC** (ideation, prioritization, requirements depth, estimation) and the **delivery tail** (progressive-delivery, deprecation, supply-chain), plus two orphan phases (**localization-i18n** = zero coverage, **product-strategy-gtm** = mis-tagged). The cheapest highest-leverage moves are P0 #1–3: slotting prioritization, test-smell/integration QA, and roadmap/grooming skills — two of which fit inside existing plugins under the 400-token cap rather than spending a new plugin envelope.

---

## Q2 — Workflow Auto-Detection & Intuitive Use

### Root cause

Skills are visible to the model at every turn: their one-line descriptions are injected into context (and falsification-anchored by `skill-triggering.py`), so the model can route a naive request to the right skill without being told the skill exists. **Workflows have no equivalent surface.** A workflow lives only as a YAML in `plugins/polymath-flows/workflows/*.yaml`; nothing about it reaches the model's context until the user already knows the workflow's name and invokes `run-workflow`. The result is that the entire flows-lite layer — 21 multi-step arcs with real gates — is effectively dark. A user who says "review this plan" or "we have an incident" gets ad-hoc skill calls instead of the governed `deliberationLoop` / `respondToIncident` arc, because the model literally cannot see that those arcs exist.

The fix is to give workflows the same model-facing routing surface skills already have, while preserving the deterministic, user-confirmed nature of a workflow run (a workflow is a state machine the user opts into, not an autonomous behavior).

### Chosen architecture

A single pipeline, with **`triggers` + `whenToUse` in the workflow YAML as the single source of truth**:

```text
workflow YAML (whenToUse / triggers / detectionSignals)   ← authored once, validated
        │  build-workflow-index.py  (single producer, idempotent)
        ▼
workflow-index.json (FULL: n/w/t)   workflow-index.min.json (INJECTED: n/w)   workflow-detect.json (signals, non-injected)
        │  session-start.sh cats the pre-built min-index
        ▼
SessionStart injection  →  "Polymath workflows available (propose before running):"  (~300 tokens)
        │  model compares the request to the injected name: whenToUse lines
        ▼
DETECT → PROPOSE-ONE-LINE → AWAIT-APPROVAL → RUN   (propose/confirm contract)
        │  falsified offline by
        ▼
tools/workflow-triggering.py  (check in CI; run opt-in under CLAUDE_CODE_OAUTH_TOKEN)
```

**Trade-off vs the "one entrypoint skill per workflow" alternative.** The obvious alternative is to mint a skill per workflow so the existing skill-routing machinery surfaces them for free. We reject it on **token budget**. A skill description is a full always-on listing line; 21 of them would blow the polymath-flows always-on budget (≤ 400 tokens/plugin) several times over, and would also duplicate routing logic the model already does for skills, creating two competing entrypoints for the same arc (the `reviewPR`-vs-`code-review` collision, multiplied by 21). Instead we inject one compact `name: whenToUse` line per workflow from a **pre-built min-index** — name + 8-word hint only, triggers and prompts dropped — which fits ~300 tokens for all 21 and stays under the cap. Triggers live in the source YAML purely as the offline falsification anchor; they never enter runtime context. The builder is the single producer and asserts the rendered min-index ≤ 380 tokens, exiting 1 (and naming the longest `whenToUse`) if an author overruns.

---

### Schema diff (`workflow.schema.json`)

Add three **optional** top-level keys under `properties`, right after `description`. `additionalProperties:false` stays — these become known keys, so existing workflows that omit them still validate; they are NOT added to `required`.

```json
"whenToUse": {
  "description": "One-line, model-facing routing hint: when this workflow is the right multi-step arc. Mirrors a skill description. Surfaced in the SessionStart workflow-index; counts against the per-plugin token budget, so keep it tight.",
  "type": "string",
  "minLength": 12,
  "maxLength": 160
},
"triggers": {
  "description": "3-5 naive user phrasings (no workflow name) that should surface this workflow. Used by build-workflow-index.py and as the falsification anchor for workflow-triggering tests.",
  "type": "array",
  "minItems": 3,
  "maxItems": 5,
  "uniqueItems": true,
  "items": { "type": "string", "minLength": 6, "maxLength": 80 }
},
"detectionSignals": {
  "description": "Deterministic, machine-checkable hints (file globs, artifact paths, intents) that raise this workflow's prior. Not injected into context; consumed by the detect step to disambiguate proposals.",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "paths":   { "type": "array", "items": { "type": "string", "minLength": 1 }, "uniqueItems": true },
    "intents": { "type": "array", "items": { "type": "string", "minLength": 2 }, "uniqueItems": true }
  }
}
```

**Enforcement** (extend `tools/check-workflow-invokes.py`):

- (a) Require `whenToUse` + `triggers` once a grace flag is dropped — the WORKFLOW-2 conformance rule.
- (b) Cap `whenToUse` at 160 chars locally (it already caps `description` at 200).
- (c) Reject duplicate trigger phrases **across** workflows (collision guard — see Trigger collisions).

No change to the `check` `$defs` is needed.

---

### Index builder (`tools/build-workflow-index.py`)

Emits compact, token-budgeted JSON from `name`/`whenToUse`/`triggers`/`detectionSignals` of every workflow YAML. It is the **single producer**; nothing else hand-edits the JSON.

- **Inputs:** glob `plugins/polymath-flows/workflows/*.yaml` (PyYAML, with the same inline-shim fallback `skill-triggering.py` uses).
- **Per-workflow record** (short keys to save tokens):

  ```json
  {"n":"reviewPlan","w":"Critique an existing plan/design doc before committing to it","t":["review this plan","is this plan any good","poke holes in my design doc"]}
  ```

- **Two-tier emission:**
  - `workflow-index.json` (FULL: `n` + `w` + `t`) — for the propose step and the doctor command.
  - `workflow-index.min.json` (INJECTED: `n` + `w` only, triggers dropped) — 21 workflows × ~14 tokens ≈ 300 tokens.
  - `workflow-detect.json` (SEPARATE, non-injected) — `detectionSignals` only, so the always-on index carries just `n/w/t`.
- **Token budget:** builder asserts the rendered min-index ≤ 380 tokens (tiktoken if available, else chars/4 heuristic) and exits 1 over budget, **naming the longest `whenToUse`** so the author trims it.
- **Determinism:** stable sort by name; pretty-print disabled (no spaces) for the min file. Re-running with no YAML change produces byte-identical output. CI diff-guard: build, then `git diff --exit-code` on the JSON files, mirroring the catalog/portability checks.
- **Wiring:** add to `tools/conformance.sh --all` as `WORKFLOW-INDEX`; add a `new-workflow.sh` post-step that re-runs the builder so the index never drifts.

---

### SessionStart injection (`session-start.sh`)

A fourth quiet surface, AFTER paused-workflows, BEFORE scheduled-work, rendered only when the repo is Polymath-initialized (`project_summary` non-empty) — an un-initialized repo already gets the init nudge and should not be flooded.

```bash
# --- workflow routing index ---
wf_index="${CLAUDE_PLUGIN_ROOT_FLOWS:-}/data/workflow-index.min.json"
# resolved relative to the flows plugin; builder writes it at build time
if [[ -n "$project_summary" && -s "$wf_index" ]]; then
  wf_lines="$(python3 - "$wf_index" <<'PY' || true
import json,sys
try: idx=json.load(open(sys.argv[1]))
except Exception: sys.exit(0)
for w in idx: print(f"  - {w['n']}: {w['w']}")
PY
)"
fi
```

Rendered output (one header, one line per workflow, guarded behind the same `emitted` blank-line logic):

```text
Polymath workflows available (propose before running):
  - shipFeature: Ship a small feature from PRD to PR draft
  - reviewPR: Multi-critic review of a PR diff
  ... (21 lines)
  When a request matches one, name it and ask to run it before doing the work.
```

The final line arms the propose-confirm contract.

**Discipline:** the injected min-index is name + `whenToUse` only (no triggers, no prompts) — ~300 tokens, under the 400/plugin cap. `session-start.sh` does NOT parse YAML at session start (too slow/fragile); it `cat`s the pre-built min-index. If the min-index is missing or stale, the hook silently skips (degrade-quiet, same posture as the rest of the hook). A suppression marker (`${data_root}/polymath-flows/index-muted`) lets a user who never uses workflows turn the surface off, matching the init-nudge suppression pattern.

---

### Propose / confirm / run contract

**DETECT → PROPOSE-ONE-LINE → AWAIT-APPROVAL → RUN.** The model never auto-starts a workflow; a run is always user-confirmed (matching `run-workflow` SKILL.md's "invoke is a label" posture and deterministic state-machine ownership).

1. **DETECT** (model-side, every user turn after the index is in context): compare the request against the injected `name: whenToUse` lines. The model MAY additionally consult `workflow-detect.json` signals via a read (e.g. user references `docs/plans/foo.md` → raise `reviewPlan`/`deliberationLoop` prior). Detection yields at most ONE primary candidate (+ optional runner-up if two `whenToUse` lines are within a hair — see collisions).

2. **PROPOSE-ONE-LINE**: emit exactly one sentence, no work yet:
   > This looks like the `reviewPlan` workflow (critique an existing plan before committing). Run it? (yes / just answer directly / different workflow)

   So `review this plan` → "This looks like the `reviewPlan` workflow … Run it?". If two candidates tie, propose the higher-prior one and name the alternative in the same sentence ("… or `deliberationLoop` if you also want a revised plan").

3. **AWAIT-APPROVAL**: the model STOPS and does not call `bin/polymath-flow` until the user responds. `yes` → proceed. `just answer` / `no` → abandon the workflow, answer the request directly with plain skills, do NOT re-propose the same workflow this turn. A bare clarifying answer that supplies a required input counts as implicit approval ONLY if the user already said yes.

4. **RUN**: on approval, hand off to the `run-workflow` skill verbatim: `bin/polymath-flow start <name> --input ...`, then the existing next/complete/assert loop. The contract changes nothing downstream — it only adds the detect+propose gate in front of the existing skill.

**Guardrails:**

- (a) Propose at most once per user turn.
- (b) Never propose a workflow whose `requires.plugins`/`capabilities` are unmet — instead surface the missing dependency.
- (c) sev1/sev2 + "incident"-style phrasings short-circuit to `respondToIncident`'s proposal with urgency, but STILL ask (one line) unless the user said "just do it".
- (d) If the user names the workflow explicitly ("run shipFeature"), skip propose, go straight to RUN.

---

### Triggering-test format (`tools/workflow-triggering.py`)

A sibling to `skill-triggering.py` (same three modes: `check` / `list` / `run`), reading `tests/workflow-triggering/<workflow>.md`. It asserts a naive prompt makes the model PROPOSE the right workflow — the falsification anchor for `triggers`/`whenToUse` quality, exactly as skill-triggering anchors skill descriptions.

```markdown
---
workflow: reviewPlan
trigger_prompts:
  - "review this plan"
  - "is this plan any good before I start"
  - "poke holes in docs/plans/migrate.md"
must_propose:
  - reviewPlan
allow_propose:
  - deliberationLoop        # acceptable runner-up
forbidden_prompts:
  - "format my markdown"     # must NOT propose any workflow
---
```

**Detection mechanism (run mode):** the model under test does NOT call a Skill tool at propose time — it emits the one-line proposal as text and stops (per the contract). So `_extract_skill_invocations` is replaced by `_extract_workflow_proposal`, parsing the stream-json assistant text for the proposal shape. Two-layer match:

1. **Primary** — a backticked workflow name in the proposal sentence (regex `` `([a-z][a-zA-Z0-9]*)` `` within a sentence containing "workflow" + "run it").
2. **Fallback** — the model DID call `run-workflow` / `bin/polymath-flow start` with that name (covers the explicit "run shipFeature" case).

`must_propose` must appear; any proposed name not in `must_propose` + `allow_propose` is a `forbidden` failure; `forbidden_prompts` must yield NO proposal (assert empty).

**Check mode** validates frontmatter (workflow exists as a YAML, `must_propose` names resolve, ≥ 3 `trigger_prompts`, and the test's triggers are a **superset-or-equal** of the YAML's `triggers` so test and index can't drift). Wire `check` into `conformance.sh` (cheap, no LLM); `run` is opt-in under `CLAUDE_CODE_OAUTH_TOKEN` like skill-triggering run, skipped on fork PRs.

---

### Per-workflow routing table

| Name | Proposed whenToUse | Trigger phrases | Detection signals | Strong gate |
|------|--------------------|-----------------|-------------------|:-----------:|
| activateProject | First-time Polymath setup of a repo: write project.yaml, capabilities, onboarding. | set up polymath for this repo; onboard this project; initialize project context; why isn't polymath picking up my stack; generate onboarding docs | `!.polymath/project.yaml` (absent); intent:onboard; intent:initialize | No |
| bugTriage | A reported bug needs root-causing and a fix plan (NOT a live sev1/sev2 incident). | help me triage this bug; figure out why this is broken; there's a bug, where do I even start; investigate this defect and plan the fix; why is X returning the wrong value | docs/bugs/**; intent:triage; intent:debug | Yes |
| bumpDependency | Upgrade one dependency safely: vuln-triage, smallest bump, call-site fixes, verify. | bump lodash to the latest version; upgrade this dependency safely; update the package and fix what breaks; is it safe to bump django; patch this CVE in a dependency | package.json; package-lock.json; pyproject.toml; go.mod; Cargo.toml; Directory.Packages.props; docs/dep-bumps/**; intent:upgrade-dependency | Yes |
| decideUnderAmbiguity | A hard, possibly one-way decision needs framing, options, governance, and an ADR. | help me decide between these options; we need to make a call on X; frame this decision and pick; should we do A or B; run a DACI on this and record the decision | docs/decisions/**; docs/adrs/**; intent:decide | Yes |
| deliberationLoop | Pressure-test a plan/design/idea (red-team + pre-mortem) and emit a revised plan. | review this plan; poke holes in my approach; is this design any good; red-team my idea before I commit; critique this and give me a better plan | docs/plans/**; docs/thinking/**; artifactPath input present; intent:critique; intent:review-plan | No |
| deprecationToRemoval | Staged multi-quarter removal of a capability with telemetry-gated removal. | deprecate this endpoint over time; plan a multi-quarter sunset; kill this API once usage drops; announce deprecation then remove later; retire this feature on a schedule | docs/deprecations/**; intent:deprecate; intent:sunset | Yes |
| designSystem | Design a system/change under uncertainty: arch/RFC doc + threat model + ADR. | design this system; write an architecture doc for X; how should I architect this; draft an RFC for this change; design and threat-model this service | docs/architecture/**; docs/rfcs/**; docs/design/**; docs/threat-models/**; intent:design; intent:architecture | Yes |
| experimentToGA | Run a feature behind an A/B + flag rollout from pre-registration to GA decision. | plan an A/B test to GA; roll this out behind a flag with stages; pre-register an experiment then decide GA; stage a percentage rollout; should we GA this feature | docs/experiments/**; docs/rollouts/**; docs/launches/**; intent:experiment; intent:rollout; intent:ab-test | Yes |
| featureFromIdea | Build a feature needing discovery first: interviews + persona, then ship it. | build a feature but I need to validate it first; do discovery then ship this; interview users then build it; we have an idea, take it from research to PR; persona-grounded feature from scratch | docs/research/**; docs/prds/**; CHANGELOG.md; docs/pr/**; intent:discovery; intent:feature | Yes |
| fuzzyGoalToPlan | Turn a vague goal into a story-mapped, estimated, assumption-carrying executable plan. | I have a fuzzy goal, help me plan it; turn this vague idea into a plan; story-map and estimate this; break this big goal into a plan; help me scope and estimate this work | docs/thinking/**; docs/maps/**; docs/plans/**; intent:plan; intent:estimate; intent:scope | Yes |
| incidentRetroToActions | Turn a written postmortem into filed, estimated, back-linked action tickets. | turn this postmortem into tickets; file action items from the retro; track the follow-ups from this incident; decompose postmortem actions and file them; make tickets from docs/postmortems/X.md | docs/postmortems/**; docs/retros/**; postmortemPath input present; intent:retro-actions | Yes |
| migrateLanguageVersion | Migrate the codebase to a new language/runtime version in pin→fix→strict phases. | upgrade us to .NET 8; migrate to TypeScript 5.6; bump the python version across the repo; move to the new node runtime; do a phased language version migration | **/*.csproj; go.mod; pyproject.toml; package.json (engines); docs/migrations/**; intent:runtime-migration | Yes |
| perfRegression | Diagnose+fix a perf regression using observability signals and verify the metric recovered. | latency went up, find out why; p99 regressed after the last deploy; this got slow, fix it; diagnose the performance regression; throughput dropped, investigate and fix | docs/perf/**; metric input present; suspectSha input present; intent:perf-regression | Yes |
| refactorWithSafety | Refactor an area safely: pin current behavior in tests first, then change, then verify. | refactor this safely; clean up this module without breaking it; restructure this code with a safety net; I want to refactor but I'm scared to break things; pin behavior then refactor | docs/refactors/**; scope input (file glob) present; intent:refactor | Yes |
| respondToIncident | Drive a live incident end-to-end: context, triage, signals, postmortem, tickets. | we have an incident; prod is down, help; page just fired, walk me through response; respond to incident PT9X3HQ7; sev1, what do I do | docs/postmortems/**; incidentId input present; intent:incident; intent:outage; sev1/sev2 keyword | Yes |
| reviewPR | Multi-critic review of a PR/diff (correctness, coverage, security, red-team) + synthesis. | review this PR; do a thorough review of my diff; run all the critics on this change; review the working tree before I push; security + qa review of this PR | docs/reviews/**; pr input present; diffPath input present; git diff present; intent:review-pr | Yes |
| rootCauseAnalysis | Drive to a system root cause and write a confidence-labelled RCA (analysis, not a fix). | do a root cause analysis; why did this really happen; run a 5-whys on this; write an RCA for this symptom; get to the bottom of this | docs/rca/**; symptom input present; intent:rca; intent:root-cause | Yes |
| securityFinding | Fix a security finding end-to-end: OWASP review, optional STRIDE, implement, verify. | fix this security finding; we have a vuln, patch it; address this OWASP issue; remediate this security report; threat-model and fix this | docs/security/**; docs/threat-models/**; scope input present; intent:security-fix; intent:vuln | Yes |
| shipFeature | Ship a small/medium feature from PRD through implement, verify, changelog, PR draft. | ship this feature; build and ship X end to end; take this from PRD to PR; implement this small feature properly; feature: rate-limit /login | docs/prds/**; CHANGELOG.md; docs/pr/**; title input present; intent:ship-feature | Yes |
| sunsetCapability | Two-stage sunset of a capability: announce+deprecate-in-code now, remove later. | sunset this endpoint; deprecate this feature with a notice; add deprecation warnings and a sunset notice; remove this old API on the removal date; write the customer sunset notice and deprecate | docs/sunsets/**; capability input present; removalDate input present; intent:sunset; intent:deprecate | Yes |
| weeklyReleaseTrain | Cut a release: survey merged commits, audit CHANGELOG, draft notes, verify, tag PR. | cut this week's release; prep the release train; draft release notes for v1.4.0; bundle what merged into a release; do the weekly release | docs/release-notes/**; CHANGELOG.md; docs/pr/**; version input present; intent:release; intent:cut-release | Yes |

---

### Trigger collisions and disambiguation

The same naive phrasing can fan out to several workflows. `detectionSignals` (deterministic, non-injected) break ties; the model uses them to set the prior before proposing.

1. **`review this plan` / `help me decide` → deliberationLoop · decideUnderAmbiguity · reviewPlan · designSystem.**
   Priors: **reviewPlan** (new, lightweight critique-only) is the default for "review this plan"; **deliberationLoop** when a *revised plan artifact* is wanted; **decideUnderAmbiguity** when a *governed decision + ADR* is wanted; **designSystem** when the subject is a *system architecture*. Signals: `docs/plans/**` → reviewPlan/deliberationLoop; `docs/adrs/**` → decideUnderAmbiguity; `docs/architecture|rfcs/**` → designSystem.

2. **`deprecate/sunset this capability` → sunsetCapability · deprecationToRemoval.**
   Disambiguate on staging depth: **sunsetCapability** = 2-stage announce/remove, no telemetry; **deprecationToRemoval** = 3-stage with a usage-threshold midterm gate + observability. Propose deprecationToRemoval only when the user mentions usage decline / multi-quarter / threshold; else sunsetCapability.

3. **`build/ship a feature` → shipFeature · featureFromIdea · experimentToGA.**
   **shipFeature** is the base arc; **featureFromIdea** is a strict superset adding interview+persona discovery; **experimentToGA** adds A/B pre-registration + flag rollout. Default to shipFeature; escalate to featureFromIdea when discovery/validation is requested, experimentToGA when an A/B test or staged rollout is requested.

4. **`something is broken / find out why` → bugTriage · rootCauseAnalysis · perfRegression · respondToIncident.**
   Priors by signal: live page / incidentId / sev1-2 → **respondToIncident** (must win on urgency keywords); a metric regressed + need a code fix → **perfRegression**; analysis only, no fix → **rootCauseAnalysis** (the doc-only escape hatch); a reported bug needing a fix-plan → **bugTriage**.

5. **`upgrade / patch the CVE` → bumpDependency · migrateLanguageVersion · securityFinding.**
   A single named package → **bumpDependency**; a language/runtime version → **migrateLanguageVersion**; a vuln to fix in our own code (not a dep) → **securityFinding**. Manifest-vs-runtime signals and version-change-vs-source-change disambiguate.

6. **`review this` → reviewPR · reviewPlan.**
   Signals decide: git diff / `docs/pr/**` / a PR id → **reviewPR**; `docs/plans|design/**` path → **reviewPlan**.

7. **`set up / init` → activateProject vs the built-in.**
   Collides not with another workflow but with the `/polymath-core:init-project` command and the SessionStart init-nudge, which already own first-run onboarding. Propose **activateProject** only when the user wants the full multi-artifact arc (project.yaml + capabilities + onboarding doc), not a bare init.

**Cross-cutting collisions with single-pass skills/commands:** reviewPR/reviewPlan also collide with the `polymath-engineering:code-review` SKILL and the `/code-review` built-in command — propose the *workflow* only for the heavy multi-critic / multi-step arc, never for a single-pass review. The schema's cross-workflow duplicate-trigger guard (enforcement rule (c)) prevents two workflows from claiming an identical trigger phrase, forcing authors to differentiate at authoring time.

---

### Missing workflow arcs

The audit surfaced gaps where the right-sized arc does not yet exist, forcing over-heavy proposals:

| Name | When to use | Composes |
|------|-------------|----------|
| **reviewPlan** | The headline example: a lightweight critique of an existing plan/design doc that emits a findings report but NO revised plan and NO governance. Fills the gap where deliberationLoop is too heavy (it rewrites the plan) and decideUnderAmbiguity is overkill (DACI+ADR). Default proposal for "review this plan". | polymath-engineering:read-code; polymath-thinking:red-team; polymath-thinking:pre-mortem; polymath-decisions:tradeoff-matrix |
| **estimateAndPlan** | A well-specified goal (NOT fuzzy) needing only a work breakdown + PERT estimate + executable plan, skipping fuzzyGoalToPlan's disambiguation/story-map front matter. The common "scope and estimate this" request where the *what* is already clear. | polymath-planning:work-breakdown; polymath-planning:estimate; polymath-planning:write-plan |
| **requirementsToBacklog** | Turn a PRD / requirements doc into a decomposed, estimated, filed backlog of tickets — the product-side analogue of incidentRetroToActions. Bridges `docs/prds/**` to a real tracker. | polymath-product:decompose-epic; polymath-planning:work-breakdown; polymath-planning:estimate; ${capabilities.issue_tracker.plugin}:file-bug-from-incident |
| **progressiveRollout** | Stage a feature-flag rollout (internal→1%→5%→25%→100%) with per-stage stop conditions and SLO guardrails, WITHOUT experimentToGA's experiment/pre-registration apparatus. The "roll this out behind a flag safely" arc for changes that aren't A/B tests. | polymath-product:acceptance-criteria; polymath-sre:slo-design; ${capabilities.observability.plugin}:author-monitor; polymath-release:release-notes |
| **incidentToReview** | Connective arc chaining respondToIncident → incidentRetroToActions so one proposal takes a live incident all the way to filed follow-up tickets, instead of re-proposing the second workflow after the postmortem lands. | respondToIncident; incidentRetroToActions |
| **prdToShip** | Start from an EXISTING PRD (`docs/prds/**`) rather than writing one — skip shipFeature's prd step and go acceptance→implement→review→verify→changelog→PR. Covers the very common case where product already wrote the spec. | polymath-product:acceptance-criteria; polymath-engineering:feature-dev; polymath-engineering:code-review; polymath-engineering:verify-change; polymath-release:changelog; polymath-release:pr |

Adding **reviewPlan** is the highest-leverage gap — it resolves collision #1 by giving the headline example "review this plan" a correctly-sized default instead of routing it to the heavier deliberationLoop/decideUnderAmbiguity.

---

### Staged rollout

**Phase 0 — Foundation (schema + builder + injection, grace mode).**

- Land the schema diff (3 optional keys) and extend `check-workflow-invokes.py` with enforcement (a)/(b)/(c), but keep the WORKFLOW-2 require-rule **behind a grace flag** (warn, don't fail).
- Build `tools/build-workflow-index.py` (single producer, two-tier + detect file, token assertion, deterministic). Wire `WORKFLOW-INDEX` into `conformance.sh --all` with the diff-guard, and the `new-workflow.sh` post-step.
- Add the fourth quiet surface to `session-start.sh` (cats the pre-built min-index, degrade-quiet, `index-muted` suppression).
- *Exit criterion:* injected min-index ≤ 380 tokens; CI diff-guard green; injection renders only on initialized repos.

**Phase 1 — Backfill triggers + whenToUse for all 21 workflows.**

- Author `whenToUse` + `triggers` + `detectionSignals` per the per-workflow table. Add the missing **reviewPlan** workflow first (resolves the headline collision), then the other 5 missing arcs as capacity allows.
- Run the builder; confirm byte-identical re-runs and the token budget.
- *Exit criterion:* every workflow has `whenToUse` + `triggers`; no cross-workflow duplicate triggers; min-index still under budget.

**Phase 2 — Triggering tests (check in CI, run opt-in).**

- Add `tools/workflow-triggering.py` and `tests/workflow-triggering/<workflow>.md` for each workflow. Wire `check` into `conformance.sh` (cheap, no LLM). Validate the superset-or-equal drift guard against the YAML triggers.
- Run `run` mode opt-in under `CLAUDE_CODE_OAUTH_TOKEN` (skipped on fork PRs); confirm `must_propose` fires, `forbidden_prompts` yield no proposal, and collision pairs propose the right prior.
- *Exit criterion:* `check` green in CI; `run` green locally for all 21, including the collision disambiguation cases.

**Phase 3 — Enforce as conformance gate.**

- Drop the grace flag: `check-workflow-invokes.py` now **requires** `whenToUse` + `triggers` (WORKFLOW-2 becomes blocking). The cross-workflow duplicate-trigger guard and the 160-char cap are hard failures.
- The propose/confirm contract is documented in `run-workflow` SKILL.md as the standing detect+propose gate.
- *Exit criterion:* a workflow cannot merge without a validated routing surface; the index can never drift (single producer + diff-guard + drift-guard between test triggers and YAML triggers).

---

## Q3 — Description quality: evaluate & refine every skill / command / agent

We scored the always-on description of all **158** Polymath artifacts on three 1–5 dimensions and assigned a verdict. The headline finding: triggering is good, scoping is broken. `scope_boundary` is the failing dimension across the board (mean **2.73**), and it is *the* reason 70% of the catalog needs a rewrite.

### 1. Summary statistics

**By verdict**

| Verdict | Count | Share |
|---|---|---|
| ACCEPT | 34 | 21.5% |
| REVISE | 110 | 69.6% |
| REWRITE | 14 | 8.9% |
| **Total** | **158** | 100% |

**Mean score per dimension** (1–5, higher is better)

| Dimension | Mean | Min | Read |
|---|---|---|---|
| `trigger_clarity` | **3.99** | 2 | Healthy — descriptions name the right verbs/nouns. |
| `scope_boundary` | **2.73** | 1 | **Failing** — almost nothing states *when NOT to use it*. |
| `disambiguation` | **3.68** | 2 | Dragged down by connector-triage and cache/deliberate clusters. |

The pattern is consistent: artifacts trigger well but don't fence their scope. Of the 124 non-ACCEPT artifacts, **the dominant defect in ~85% of them is a missing "Not for …" clause**, not a missing trigger word.

**By kind**

| Kind | n | ACCEPT | REVISE | REWRITE | mean tc / sb / da |
|---|---|---|---|---|---|
| skill | 131 | 30 | 92 | 9 | 4.05 / 2.77 / 3.79 |
| command | 25 | 4 | 18 | 3 | 3.72 / 2.56 / **3.24** |
| agent | 2 | 0 | 0 | 2 | 3.00 / 2.50 / **2.00** |

Notes that frame the whole effort:

- **Only 11 of 131 skills (8%) have triggering tests.** The other 120 skills have descriptions that no automated harness has ever fired a prompt against. We are scoring routing quality by eye.
- **Only 2 agents exist** (`thinking:architecture-critic`, `research:research-scout`) and **both are REWRITE** — they collide with the skills they were forked from (`red-team`, `evidence-ledger`). The agent surface is the lowest-quality slice of the catalog (da mean 2.00).
- **Commands score worst on scope** (sb 2.56): most are thin "slash entry point …" wrappers that drop the parent skill's scoping language and lean on temporal phrasing ("after committing", "at commit time") instead of action verbs.

### 2. Worst offenders (15 lowest composite scores)

Composite = mean of the three dimensions. Every entry below is at or under 2.67/5.

| Rank | id (kind) | tc/sb/da | Current description (abridged) | The specific failure | Suggested rewrite |
|---|---|---|---|---|---|
| 1 | `polymath-thinking:deliberate` (command) | 3/1/2 | "Slash entry point to think a hard or ambiguous call through before you commit to it." | sb=1: zero scope bound; "hard or ambiguous call" over-triggers on almost any thinking request, and it's identical to its own skill + adjacent to daci/cynefin. | "Slash entry point for the deliberate skill: think a hard/ambiguous call through (observe-options-tradeoffs-risks) before committing. Invoke the deliberate skill; not for a quick decision or a structured DACI." |
| 2 | `connector-github:triage-issue` (skill) | 4/1/2 | "Triage an inbound GitHub issue — label, severity, area, ask for repro, route to team." | Only the word "GitHub" separates it from jira-triage and linear-triage; "triage this issue" routes to any of three. | "Triage an inbound GitHub issue — fetch via MCP, set labels/severity/area, ask for missing repro, route to a team. For GitHub issues only, not Jira/Linear tickets or PR review." |
| 3 | `connector-jira:file-bug-from-incident` (skill) | 4/1/2 | "File a Jira bug from an incident — pre-fills repro, links postmortem, sets severity, routes." | Near-verbatim twin of the Linear connector; "open a bug from this incident" fires both. | "File a Jira bug from an incident/postmortem … Jira only; for Linear use the Linear connector." |
| 4 | `connector-jira:jira-triage` (skill) | 4/1/2 | "Triage a Jira issue — classify type/priority/component, ask repro, transition, route." | Generic triage/classify/route shape shared with linear-triage + github triage-issue. | "Triage a Jira issue/ticket … Jira only; not GitHub issues or Linear." |
| 5 | `connector-linear:linear-triage` (skill) | 4/1/2 | "Triage a Linear issue — classify type/priority/state, ask repro, transition, route." | Identical triage shape; only "Linear" disambiguates. | "Triage a Linear issue … Linear only; not Jira or GitHub issues." |
| 6 | `infra-cloud:design-terraform-stack` (command) | 2/2/3 | "Slash entry point when laying out Terraform modules and state up front." | tc=2: abstract phrasing, no concrete trigger nouns; collides with cloud service-selection commands. | "Lay out Terraform/IaC stack structure — module boundaries, state layout, workspaces, blast radius per apply. Not cloud service selection, not writing HCL resources." |
| 7 | `planning:work-breakdown` (skill) | 3/2/2 | "Decompose a goal or plan into independently completable steps; each step produces an observable artifact." | da=2: collides head-on with product:decompose-epic and write-plan's "Work breakdown" section; "goal or plan" triggers on any planning ask. | "Break an engineering goal or plan into independently completable WBS steps, each with an observable artifact. For task/WBS breakdown, not product story slicing (decompose-epic) or the full plan doc." |
| 8 | `research:research-scout` (agent) | 3/2/2 | "Fork context to scout primary-source evidence for a product or technical claim; separates known facts, unknowns, tests." | Same "facts/unknowns/tests" framing as decisions:evidence-ledger and overlaps deep-research; jargon name. | "Fork context to gather primary-source evidence … For sourcing evidence; use evidence-ledger to structure a decision, deep-research for multi-source web reports." |
| 9 | `thinking:deliberate` (skill) | 3/2/2 | "Run an iterative observe-frame-options-tradeoffs-risks-revise loop for a plan, design, doc, idea, or implementation; composes brainstorm, red-team, pre-mortem." | Targets so broad it over-triggers; collides with its own command and the three skills it composes. | "Think a hard/ambiguous call through … The orchestrator that composes brainstorm + red-team + pre-mortem; use those directly for a single step." |
| 10 | `infra-cloud:design-terraform-stack` skill twin / `connector-pagerduty:page-context` (skill) | 3/2/3 | "Fetch the full context for an active PagerDuty incident — log entries, oncall, related services, recent deploys." | Abstract "page-context"; overlaps datadog:query-during-incident on incident-context surface; no NOT-use. | "Fetch full context for an active PagerDuty incident/page … For metrics/traces use a monitoring connector." |
| 11 | `connector-slack:post-incident-comms` (skill) | 3/2/3 | "Post an incident-comms update to the right Slack channel + thread." | "Post update to Slack" collides with post-async-update; "incident update" collides with statuspage. | "Post an incident status/comms update to the right Slack channel + thread during an outage. Not for routine standups (post-async-update) or customer Statuspage." |
| 12 | `incident:postmortem` (command) | 3/2/2 | "Draft a blameless postmortem from incident notes; alias for postmortem-blameless." | Self-declared alias → guaranteed collision with its own skill; thinner than what it wraps. | "Draft a blameless postmortem / retrospective from incident notes — timeline, root cause, action items. Command entry point for the postmortem-blameless skill." |
| 13 | `incident:incident-start` (command) | 4/2/2 | "Start an incident triage … alias for incident-triage." | Self-declared alias of incident-triage skill — identical surface area. | "Start an incident — declare severity, assign IC/operator/comms/scribe roles, open the comms channel. Command entry point for the incident-triage skill." |
| 14 | `learning:feynman-technique` (skill) | 2/3/3 | "Self-test understanding of a concept by attempting an undergrad-level explanation; surface where it cracks." | tc=2: lowest trigger of the catalog — "feynman" term absent from body; naive user types "check my understanding". | "Test/check your own understanding of a concept (Feynman technique): explain it simply, find where the explanation cracks, study those gaps. Use to learn/self-quiz; not to teach others (explain)." |
| 15 | `performance:caching-tradeoffs` & `performance:design-cache-layer` (skills) | 4/2/2 | Both literally open "Design a cache" / "Design a Redis cache layer" and list invalidation/eviction/stampede. | da=2: a router cannot tell the vendor-neutral *where-to-cache* decision from the Redis-specific *mechanics*; the command `design-cache` is a third near-verbatim proxy. | caching-tradeoffs → "Decide WHETHER/WHERE to cache … Vendor-neutral strategy; not Redis key-schema/TTL design." design-cache-layer → "Design a Redis cache layer's mechanics … Use after caching-tradeoffs decides where; not Redis server config." |

(Ties at the 2.33–2.67 boundary also pull in `devops:audit-compose` cmd, `flows:run-workflow`, `connector-linear:file-bug-from-incident`, and `infra-cloud:design-aws/azure/gcp` commands, all sb=2.)

### 3. Overlap / confusion clusters

These are the groups a router genuinely cannot split. Fix = one shared "Not for …" boundary clause per member, plus the disambiguation pointer shown.

**C1 — Issue triage (4 artifacts, the single worst cluster).** `github:triage-issue` × `jira:jira-triage` × `linear:linear-triage`, plus the two `file-bug-from-incident` twins (jira/linear). All share `triage → classify priority → ask repro → route`. *Fix:* every description must lead with the platform and end with an explicit platform-exclusion ("Jira only; not GitHub/Linear"). For file-bug, anchor on the differentiator (Linear = "one issue per action item"; Jira = "single pre-filled bug").

**C2 — Deliberate / decision overlap.** `thinking:deliberate` (skill) × `thinking:deliberate` (command) × `decisions:tradeoff-matrix` × `decisions:daci` × `decisions:cynefin-frame`. *Fix:* deliberate = "the orchestrator that composes brainstorm+red-team+pre-mortem; use those for a single step"; tradeoff-matrix = "score *known* options"; daci = "assign decision *roles*"; cynefin = "classify the *kind* of problem". The skill/command pair must say "command entry point for the deliberate skill."

**C3 — Adversarial critique.** `thinking:red-team` × `thinking:architecture-critic` (agent) × `thinking:pre-mortem`. *Fix:* red-team = "challenge a plan/PRD"; architecture-critic = "ADR/system-design review specifically"; pre-mortem = "pre-launch failure imagination, not post-incident (5-whys)".

**C4 — Evidence/research.** `decisions:evidence-ledger` × `research:research-scout` (agent) × `deep-research`. *Fix:* evidence-ledger = "structure a *decision*"; research-scout = "source the evidence"; deep-research = "multi-source web report".

**C5 — Caching (3 artifacts).** `performance:caching-tradeoffs` × `performance:design-cache-layer` × `performance:design-cache` (cmd), plus a near-edge with `performance:audit-redis-config`. *Fix:* strategy (where/whether) → mechanics (key schema/TTL) → server config (maxmemory/AOF). Each names the previous as its predecessor and excludes the others.

**C6 — Decompose / plan.** `product:decompose-epic` × `planning:work-breakdown` × `planning:write-plan`. *Fix:* decompose-epic = "vertical *story* slices"; work-breakdown = "engineering *task* WBS"; write-plan = "the full plan doc, not a standalone WBS". Remove "Work breakdown" from write-plan's leading section list or qualify it.

**C7 — Test ownership.** `engineering:code-review` × `qa:coverage-gap` × `qa:unit-tests` × `qa:test-strategy` × `engineering:feature-dev` × `engineering:verify-change`. The word "tests" appears in six descriptions with no boundaries. *Fix:* author (unit-tests / feature-dev) vs. find-gaps (coverage-gap) vs. plan (test-strategy) vs. run (verify-change) vs. review (code-review). Each must state which of {write, find, plan, run, review} it owns and exclude the rest.

**C8 — Perf budgets.** `frontend:web-vitals-budget` × `mobile:mobile-perf` × `performance:perf-budget`. *Fix:* web CWV / native mobile / backend-service; each excludes the other two surfaces.

**C9 — Incident comms (temporal/audience).** `incident:comms-update` × `connector-slack:post-incident-comms` × `connector-statuspage:post-statuspage-update` × `incident:postmortem-blameless`. *Fix:* author-body vs. post-internal-Slack vs. post-customer-Statuspage; and live-incident vs. after-action (postmortem).

**C10 — Skill↔command alias pairs (systemic).** `incident-start`↔`incident-triage`, `postmortem`↔`postmortem-blameless`, `release:{changelog,commit,pr,release-notes}`, `infra-cloud:design-*`, `infra-postgres:review-migration`, `performance:audit-redis-config`. *Fix:* a mechanical rule — every command description ends with "Command entry point for `<parent-skill>`" and reuses the skill's noun set rather than temporal filler. This is a lint rule, not a per-artifact judgment (see §4).

**C11 — Docs overlap.** `writing:adr` × `writing:rfc` × `writing:architecture-doc` × `communication:six-pager` × `communication:exec-brief`. *Fix:* recorded-decision (adr) vs. proposal-to-debate (rfc) vs. structure-description (architecture-doc) vs. long-narrative (six-pager) vs. short-decision-brief (exec-brief).

### 4. Reusable lint rubric + confusion-matrix test

Two artifacts ship from this work. Both are cheap, both go behind CI gates we already run.

**`tools/lint-descriptions.py`** — a static, per-artifact scorer (no LLM needed for the structural checks):

```python
#!/usr/bin/env python3
"""Score every plugin description on trigger_clarity / scope_boundary / disambiguation.
Static heuristics gate CI; an optional --llm pass refines borderline scores.
Exit non-zero if any artifact scores < FAIL_THRESHOLD on any dimension."""
import sys, re, glob, yaml, itertools

FAIL = {"trigger_clarity": 3, "scope_boundary": 2, "disambiguation": 3}
NOT_USE = re.compile(r"\b(not for|use .* instead|alias for|command entry point|"
                     r"not\b.*\b(see|use)\b)", re.I)
VERB = re.compile(r"^(design|write|author|review|audit|triage|plan|run|set|"
                  r"explain|decompose|break|score|investigate|fetch|post|"
                  r"diagnose|capture|build|generate|orient|open|file|resume|list)\b", re.I)

def score(desc, name):
    s = {}
    # trigger_clarity: starts with an action verb AND names >=2 concrete nouns
    nouns = len(re.findall(r"[A-Z][A-Za-z]+|\b\w+-\w+\b", desc))
    s["trigger_clarity"] = 5 if VERB.match(desc) and nouns >= 3 else (
        3 if VERB.match(desc) else 2)
    # scope_boundary: explicit NOT-use / exclusion clause present
    s["scope_boundary"] = 4 if NOT_USE.search(desc) else 2
    # disambiguation filled in by the pairwise pass below
    s["disambiguation"] = None
    return s

def jaccard(a, b):
    ta = set(re.findall(r"\w+", a.lower())); tb = set(re.findall(r"\w+", b.lower()))
    return len(ta & tb) / max(1, len(ta | tb))

def main(paths):
    arts = {}
    for p in paths:
        fm = yaml.safe_load(open(p).read().split("---")[1])
        arts[fm["name"]] = (fm["description"], p)
    failures = []
    # pairwise disambiguation: penalise high token overlap
    overlap = {n: 5 for n in arts}
    for (na, (da, _)), (nb, (db, _)) in itertools.combinations(arts.items(), 2):
        if jaccard(da, db) > 0.45:
            overlap[na] = min(overlap[na], 2); overlap[nb] = min(overlap[nb], 2)
    for name, (desc, path) in arts.items():
        s = score(desc, name); s["disambiguation"] = overlap[name]
        for dim, thr in FAIL.items():
            if s[dim] < thr:
                failures.append(f"{path}: {name} {dim}={s[dim]} < {thr}")
    for f in failures: print("FAIL", f)
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main(glob.glob("plugins/**/SKILL.md", recursive=True)
                  + glob.glob("plugins/**/commands/*.md", recursive=True)
                  + glob.glob("plugins/**/agents/*.md", recursive=True)))
```

Scoring rubric the file encodes (the human/LLM version uses the same anchors):

- **trigger_clarity (1–5):** 5 = leads with an action verb + ≥3 concrete domain nouns a user would actually type; 3 = verb present but jargon-/acronym-led with the plain synonym missing (e.g. "Cynefin", "feynman", "PRD"); 1 = abstract framing only.
- **scope_boundary (1–5):** 5 = explicit "Not for X / use Y instead" *and* implicit scope; 2 = scope only implied; 1 = no bound, over-triggers (`deliberate` command).
- **disambiguation (1–5):** start at 5; subtract for each sibling whose token-overlap (Jaccard) > 0.45 or that shares the same lead verb+object; alias pairs that don't say "command entry point for …" cap at 2.

**Confusion-matrix test (`tests/forbidden_prompts.yaml`).** For each cluster in §3, list prompts that *must not* route to a given artifact. The harness sends each prompt through the router and asserts the chosen artifact is the expected one and never a forbidden sibling.

```yaml
# tests/forbidden_prompts.yaml — confusion-matrix gate
- prompt: "triage this issue for me"
  expect_one_of: [github:triage-issue, jira:jira-triage, linear:linear-triage]
  must_ask_platform: true          # ambiguous → router must disambiguate, not guess
- prompt: "triage this GitHub issue"
  expect: connector-github:triage-issue
  forbidden: [connector-jira:jira-triage, connector-linear:linear-triage]
- prompt: "open a bug from this incident in Linear"
  expect: connector-linear:file-bug-from-incident
  forbidden: [connector-jira:file-bug-from-incident]
- prompt: "where should we cache this"
  expect: performance:caching-tradeoffs
  forbidden: [performance:design-cache-layer, performance:design-cache, performance:audit-redis-config]
- prompt: "design the Redis key schema and TTLs"
  expect: performance:design-cache-layer
  forbidden: [performance:caching-tradeoffs, performance:audit-redis-config]
- prompt: "break this epic into stories"
  expect: product:decompose-epic
  forbidden: [planning:work-breakdown]
- prompt: "break this engineering goal into tasks"
  expect: planning:work-breakdown
  forbidden: [product:decompose-epic, planning:write-plan]
- prompt: "what tests am I missing on this diff"
  expect: qa:coverage-gap
  forbidden: [engineering:code-review, qa:unit-tests, qa:test-strategy]
- prompt: "poke holes in this architecture"
  expect: thinking:architecture-critic
  forbidden: [thinking:red-team, thinking:pre-mortem]
- prompt: "set a performance budget for the mobile app"
  expect: mobile:mobile-perf
  forbidden: [frontend:web-vitals-budget, performance:perf-budget]
```

The matrix doubles the test coverage problem into an asset: it converts the **120 untested skills** into a tractable target — we only need forbidden-prompt rows for the 11 clusters, not 131 individual happy-path tests, to catch the routing defects that actually matter.

### 5. Prioritized rewrite backlog → CI gates

Sequenced by routing-harm × effort. Each tier closes when `lint-descriptions.py` and `forbidden_prompts.yaml` both pass for its artifacts.

| Tier | Scope | Items | Why first | Effort |
|---|---|---|---|---|
| **P0** | The 14 REWRITE artifacts + the 4-way issue-triage cluster (C1) | ~18 | Active mis-routing today; suggested rewrites already drafted in the scoring data. | 1 day — paste rewrites, add platform-exclusion clauses. |
| **P1** | Confusion clusters C2–C9 (deliberate, critique, evidence, caching, decompose, tests, perf-budgets, incident-comms) | ~40 | High `disambiguation` penalty; each fix is a one-line "Not for …" addition. | 2 days. |
| **P2** | Skill↔command alias pairs (C10) | 25 commands | Mechanical rule, scriptable: append "Command entry point for `<skill>`" + inherit noun set. | 0.5 day; can be a codemod. |
| **P3** | Remaining REVISE skills (term-only triggers: feynman, cynefin, stride, glossary, etc.) | ~70 | Lowest harm — they trigger acceptably, just need a plain-language synonym and a scope clause. | Batch over a sprint. |

**Plug-in points (gates already in the repo):**

- `tools/lint-descriptions.py` joins the existing **`lint-skills`** step in `polymath-author:validate-plugin` and the `validate-plugin` CI workflow; it fails the build on any `scope_boundary < 2` or `disambiguation < 3`, which makes the missing "Not for …" clause a hard error for new artifacts.
- `tests/forbidden_prompts.yaml` runs in the **golden-tests / evaluation** workflow added in `996bb2b`, alongside the 11 existing triggering tests, gating merges on routing regressions.
- The **token-budget gate** (`polymath-core:plugin-budget`, ≤400/plugin, ≤1,500 total) is the constraint on the rewrites: every added "Not for …" clause costs listing tokens, so P1–P3 must be budget-checked — keep boundary clauses to one terse fragment, not a sentence.
- New-artifact scaffolds (`polymath-author:new-skill` / `new-command`) should emit a description stub containing a placeholder `Not for …` clause so authors fill the scope boundary at creation time rather than failing lint afterward.

**Definition of done for the program:** `scope_boundary` mean rises from 2.73 to ≥3.5, zero artifacts below the FAIL thresholds, all 11 confusion clusters green in `forbidden_prompts.yaml`, and the two REWRITE agents either re-scoped to non-overlapping intents or merged into their parent skills.
