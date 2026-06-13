# Close Whetstone coverage gaps

## What

Bring Polymath's operational surface up to the technical and process domains that the
Whetstone roadmaps (`MohammadBafkar/whetstone`) treat as core engineering competency, where
today Polymath has **no skill, flow, or expertise** to do the work. This is a master program
plan: each phase below decomposes into its own PR series when started. The deliverable is
**do-the-work skills, flows, and loops** — not curriculum.

P1 (a new `polymath-architecture` plugin) is fully specified because it is the single largest
gap and the agreed starting point. Later phases are scoped, not fully decomposed, and a
deferral registry holds the genuinely specialized or learning-only roadmaps so the program
does not degenerate into "one plugin per roadmap."

## Why

A gap audit of Polymath's 37 plugins / 26 flows against Whetstone's ~120 roadmaps (2026-06-13)
found whole roadmap groups with zero operational coverage, ranked by leverage:

1. **`40-Architecture-and-Design` (18 roadmaps) has no home.** Polymath can *write* an ADR
   (`polymath-writing`) and *pick a cloud stack* (`polymath-cloud`) but cannot *do the design*:
   DDD, event-driven, distributed-systems, resilience, service decomposition, integration
   patterns. The `designSystem` workflow orchestrates documentation around an empty center.
2. **`polymath-ai` is 3 skills (`eval-plan`, `prompt-engineer`, `rag-design`) against a
   25-roadmap AI/ML curriculum** — and Polymath is itself an agent system. No agent-design,
   eval loop, LLM guardrails/cost, or LLM-security review.
3. **`50-Data-and-Streaming` (Kafka/streaming, data engineering) has no plugin.** `polymath-data`
   is analytics (SQL, experiments, metrics), not data/stream engineering. This is the operational
   pair to the event-driven architecture gap.
4. **`80-Security` covers 3 of 13 roadmaps.** Missing: Auth, Compliance, Cryptography, DevSecOps,
   LLM-Security. **IaC authoring** (`60-Infrastructure-as-Code`) exists only as a single
   `design-terraform-stack` skill inside `polymath-cloud`.
5. **Operating-mechanism + people-leadership loops** are partial: capacity *forecasting*,
   on-call/ops design, architecture-review *governance*, API-versioning, migration playbooks,
   tech-debt management, and the hiring/conflict/coaching skills have no surface.

Full audit lives in the conversation that produced this plan; the per-plugin gap table is the
authority for the work breakdown below.

## Selection criteria (what becomes a surface, what does not)

A Whetstone roadmap earns a Polymath skill only if it is **operational** (you *do* it, not learn
it), **artifact-producing** (emits a design/plan/review, not prose), and **recurring** (shows up
across normal product work). Applied:

- **Out of scope — learning, not operational:** DSA, per-language deep-dives (`20-*`),
  Computer-Science-Basics (compilers/OS/architecture), Interview-Prep & Compensation (`120-*`),
  English (`130-*`), ML-Mathematics, Capstones, Game-Development. Not counted as gaps.
- **No duplication of existing surfaces:** Caching → `polymath-performance` (`caching-tradeoffs`,
  `design-cache-layer`); trade-off scoring → `polymath-decisions:tradeoff-matrix`; arch *docs* →
  `polymath-writing` (`adr`, `architecture-doc`, `rfc`); cloud infra stack →
  `polymath-cloud:design-stack-composition`. New skills *invoke* these, they do not re-implement them.
- **Specialized / low-frequency → Deferral registry**, reopened on measured demand: Formal-Methods,
  CRDTs, Cell-Based-Architecture, deep Consensus, Computer-Vision/Deep-Learning/RL/Time-Series,
  Recommender-Systems, Penetration-Testing, Zero-Trust, M&A-Due-Diligence, Model-Fine-Tuning.

## Locked decisions

- New plugins are born `status: experimental` in `registry/polymath-catalog.json`, gated by
  routing + profiles, **never forced always-on**. Adding plugins must not raise the default
  recommended set's always-on cost; the ≤400 tokens/plugin and aggregate budget gates hold
  (`polymath-author:token-budget-report`).
- Every new skill ships a `routing.yaml` and is declared in `registry/routing-coverage.json`
  (SURFACE-1 declare-or-exempt). New surfaces are born declared via the scaffolder stubs.
- The router precision invariants are non-negotiable: MIN_SCORE=3, hard-signal firing,
  ROUTE-EVAL misroutes==0 / FP==0. Each hard-tier surface lands with a deterministic fixture.
- Authoring goes through the existing scaffolders — `polymath-author:new-plugin`,
  `:new-skill`, `:new-workflow` — then `:validate-plugin` + `:skill-author-critic` before merge.
  No hand-rolled plugin trees.
- `polymath-architecture` supplies *technique* skills; `polymath-writing` keeps the *documents*;
  `polymath-decisions` keeps the *scoring*. The `designSystem` workflow is rewired to compose the
  new technique skills rather than absorbing them.

## P1 — `polymath-architecture` (fully specified)

A new plugin of design-*technique* skills covering `40-Architecture-and-Design`. Depends on
`polymath-core`, `polymath-decisions`, `polymath-writing`, `polymath-thinking`. Each skill takes a
plain-English design situation and emits a one-page design artifact that surfaces trade-offs.

| Skill | Whetstone roadmap(s) | Input → Output |
|---|---|---|
| `bounded-context-map` | DDD L01–L02, L06 (Bounded-Contexts, Context-Mapping, DDD-at-Scale) | Domain description / monolith → bounded-context map with context-mapping relationships (partnership, customer-supplier, conformist, anti-corruption layer, shared-kernel) + per-context ubiquitous-language glossary |
| `aggregate-design` | DDD L03–L05 (Aggregate-Design-Rules, Entities, tactical patterns) | A context's domain rules → aggregate boundaries, entities vs value-objects, invariants enforced per aggregate, transaction/consistency boundaries, reference-by-id rules |
| `event-driven-design` | EDA L01–L05, Integration messaging, Resilience (Dual-Write) | A workflow spanning services → event catalog + schemas, choreography vs orchestration choice, saga + compensation design, outbox to kill the dual-write, idempotent-consumer contract |
| `resilience-design` | Resilience-Patterns, Microservices resiliency | A dependency/call path → selected patterns (timeout, retry+backoff+jitter, circuit breaker, bulkhead, fallback, load-shed) with parameters, how they compose, and a failure-mode table |
| `service-decomposition` | Microservices, Monolith-Patterns, Refactoring-at-Scale | A monolith or proposed split → seam analysis, candidate boundaries by subdomain/capability, strangler-fig sequence, what stays monolith, characterization-test plan |
| `distributed-consistency` | Distributed-Systems, Consensus-Algorithms | A cross-node data operation → consistency model (strong/eventual/causal), CAP/PACELC trade, idempotency + dedup strategy, and when consensus (Raft/quorum) is warranted vs simpler |
| `integration-design` | Integration-Patterns, Microservices (gateway/BFF), Hexagonal (ports/adapters) | Two systems to connect → sync vs async, gateway/BFF placement, anti-corruption layer, contract (schema + versioning), backpressure handling |
| `design-patterns-apply` | Design-Patterns-Principles L02–L09 (SOLID, GoF, Anti-Patterns) | A design sketch → SOLID/GoF pattern selection at design time, anti-pattern flags. Boundary: design-time selection, distinct from `polymath-engineering:code-review`'s line-level review |

**Composed, not absorbed:** Hexagonal ports/adapters folds into `integration-design` +
`service-decomposition`; CQRS rides inside `event-driven-design` for v1; System-Design end-to-end
stays the `designSystem` workflow, now invoking the eight skills above plus existing
writing/cloud/security/decisions surfaces.

**Architecture deferral (reopen on demand):** dedicated `cqrs-design` (split from
`event-driven-design`), `crdt-design`, `cell-based-architecture`, `formal-methods` (TLA+/model
checking), deep `consensus-protocol` selection beyond what `distributed-consistency` covers.

## Approach (phases after P1)

- **P2 — AI/agents depth.** Extend `polymath-ai`: `agent-design` (ReAct/reflexion/plan-execute,
  memory, tool/function-calling, multi-agent orchestration), `llm-guardrails` (input validation,
  output filtering, prompt-injection defense), `llm-cost-latency` (cost analysis, prompt caching,
  model routing/fallback, batching); evolve `eval-plan` into an `evalDrivenDevelopment` loop
  (offline + online evals, regression sets, LLM-judge calibration). Place `llm-security-review`
  (OWASP-LLM-Top-10, prompt injection, RAG security) — decide P2 vs P4. New flow:
  `evalDrivenDevelopment`. Defer MLOps/fine-tuning/recommenders/CV/DL/RL.
- **P3 — Streaming + data engineering.** New `polymath-streaming` plugin (or `polymath-data`
  extension): `streaming-design` (Kafka/Pulsar topology, partitioning, delivery semantics,
  consumer groups, backpressure), `data-pipeline` (ETL/ELT, batch vs stream, orchestration,
  idempotent backfills), `data-modeling` (dimensional/normalized/lakehouse, schema evolution),
  `stream-processing` (windowing, stateful processing, CEP). New flow: `dataPipelineBuild`.
  Operational pair to P1's `event-driven-design`.
- **P4 — Security breadth + IaC.** Extend `polymath-security`: `auth-design` (OAuth2/OIDC,
  JWT/session, RBAC/ABAC, SSO), `compliance-mapping` (SOC2/GDPR/ISO control + evidence),
  `devsecops-pipeline` (SAST/DAST/SCA/secret-scan CI gates), `crypto-review` (key mgmt,
  at-rest/in-transit, algorithm choice). New `polymath-iac` plugin (or `polymath-cloud`
  extension): `terraform-module`, `terraform-state` (backends, drift, import), `policy-as-code`
  (OPA/Sentinel), `iac-review`. Defer Zero-Trust, Penetration-Testing.
- **P5 — Operating mechanisms + people leadership.** `api-versioning` (versioning approach,
  consumer-driven contracts, breaking-change mgmt — `polymath-release` or `polymath-backend`);
  `tech-debt-management` (debt inventory + quantified paydown prioritization); extend
  `polymath-sre:capacity-plan` with `demand-forecast` (forecasting/growth/seasonal); `oncall-design`
  + ops-review (On-Call-and-Operational-Excellence); extend
  `polymath-writing:architecture-review-facilitation` with review-board/criteria governance;
  `polymath-leadership`: `hiring-loop` (interview design → debrief → calibrated decision),
  `conflict-mediation`, `coaching-plan`. New flows/loops: `architectureReview`,
  `migrationPlaybook` (assessment → strangler → data-migration → cutover → rollback → multi-team),
  `capacityReview`, `gameDay` (wraps `polymath-sre:chaos-experiment`), `hiringLoop`,
  `techDebtPaydown`.

## Work breakdown

1. **P1**: scaffold `polymath-architecture` via `new-plugin.sh`; author the 8 SKILL.md files
   (frontmatter desc ≤200 chars + procedure + output contract) via `new-skill.sh`; each with a
   `routing.yaml` (hard-tier signals where unambiguous, e.g. "bounded context", "saga", "circuit
   breaker", "strangler"; soft otherwise).
2. **P1**: register the plugin — `.claude-plugin/marketplace.json` plugins[], catalog
   `status: experimental`, `registry/routing-coverage.json` declarations,
   `registry/polymath-profiles.json` (architecture-relevant profiles); rebuild indexes
   (`build-catalog.py`, `build-capability-index.py`, `build-surface-index.py`).
3. **P1**: rewire the `designSystem` workflow to invoke the new technique skills; add
   `bounded-context-map → aggregate-design → event-driven-design` as a composable arc;
   `build-workflow-index.py` + `check-workflow-invokes.py` green.
4. **P1**: add deterministic ROUTE-EVAL fixtures for each hard-tier architecture surface; confirm
   precision==1.0 / FP==0 on the grown corpus; `token-budget-report` shows plugin ≤400 and
   aggregate within target; `validate-plugin` + `skill-author-critic` ACCEPT on all 8; update
   root README counts (37→38 plugins, skill total) under the COUNT-1 gate.
5. **P2**: AI/agents skills + `evalDrivenDevelopment` flow; same register/route/validate/budget
   loop as steps 1–4; CONFUSION-1 boundary notes vs existing `prompt-engineer`/`rag-design`/`eval-plan`.
6. **P3**: `polymath-streaming` (or `polymath-data` extension) + `dataPipelineBuild` flow; register/
   route/validate/budget loop.
7. **P4**: `polymath-security` extension skills + `polymath-iac` plugin; place `llm-security-review`;
   register/route/validate/budget loop; new security gate composable into `reviewPR`.
8. **P5**: operating-mechanism skills + people-leadership skills + the five new flows; register/
   route/validate/budget loop; mark mature surfaces `experimental → beta` once route-eval and
   adoption evidence support it.

Each phase's register/route/validate/budget loop is identical and is the per-PR checklist:
scaffold → author → `routing.yaml` + `routing-coverage.json` → marketplace + catalog + profiles →
rebuild indexes → ROUTE-EVAL fixtures (precision==1.0/FP==0) → `token-budget-report` (≤400/plugin) →
`validate-plugin` + `skill-author-critic` → `conformance.sh` + `validate-all.sh` green →
README counts under COUNT-1.

## Risks

- **Always-on token blowout** as plugin count grows (38→~42) → new plugins born `experimental`,
  profile/routing-gated, never default-recommended; ≤400/plugin + aggregate budget gates enforced
  per PR; tiered injection (existing) keeps the listing bounded.
- **Router precision regression** from many new overlapping surfaces (e.g. `event-driven-design`
  vs `integration-design` vs `streaming-design`) → hard-tier-only coverage ratchet, per-surface
  deterministic fixtures, CONFUSION-1 advisory on runtime-tieable pairs, explicit boundary notes
  in each SKILL.md "When to use / Not this when".
- **Building ahead of need** (the program becomes a plugin-per-roadmap sprawl) → selection
  criteria + deferral registry are gates, not suggestions; P3–P5 only start when P1/P2 have shipped
  and route-eval shows the new surfaces actually fire on real prompts.
- **Overlap with existing surfaces** silently duplicating work → the "no duplication" locked
  decision; new skills invoke `tradeoff-matrix`/`caching-tradeoffs`/`architecture-doc` rather than
  re-implement; `check-command-overlap.py` + `lint-descriptions.py` in CI.

## Verification

- **P1 exit:** `polymath-architecture` validates strict; 8 skills ROUTE-EVAL-clean (misroutes==0,
  FP==0) with fixtures; `token-budget-report` ≤400; `designSystem` invokes the new skills and
  passes `check-workflow-invokes`; root counts recomputed under COUNT-1; `validate-all.sh` green.
- **Per later phase:** same gate set; plugin/skill registered, routable, budgeted, validated;
  new flows pass `polymath-flow validate` with per-step artifact contracts.
- **Program-level:** ROUTE-EVAL precision stays 1.0 / FP 0 across the grown corpus at every merge;
  no default-recommended profile's always-on listing regresses.

## Deferral registry

- **Specialized architecture:** `cqrs-design` (split), `crdt-design`, `cell-based-architecture`,
  `formal-methods`, deep `consensus-protocol` — reopen when a real design needs them.
- **Specialized AI/ML:** MLOps lifecycle, model fine-tuning, recommender-systems, computer-vision,
  deep-learning, RL, time-series — reopen when the user/an adopter ships ML, not just LLM apps.
- **Specialized security:** Zero-Trust-Architecture, Penetration-Testing — engagement-shaped;
  reopen on a real audit/pentest need.
- **Out of scope permanently (learning, not operational):** DSA, per-language deep-dives,
  CS-Basics, interview/compensation prep, English, ML-mathematics, capstones, game-development.

## Implementation status

Plan authored 2026-06-13; execution in progress same day.

- **P1 polymath-architecture** — Status: **done.** New plugin (status `experimental`) with 8 technique skills (`bounded-context-map`, `aggregate-design`, `event-driven-design`, `resilience-design`, `service-decomposition`, `distributed-consistency`, `integration-design`, `design-patterns-apply`), each with a soft-tier `routing.yaml`. Registered in marketplace.json + catalog + stability-evidence; added to the `staff` profile (budget 2150→2550, measured 2344). 2 golden fixtures. Root README plugins 37→38. Indexes regenerated (surface-index 54→62 surfaces, route-metrics, catalog). Verification: `conformance.sh --all` green; `validate-all.sh` green; ROUTE-EVAL-1 PASS (precision 1.0, false-positives 0/12); route-hint fires `event-driven-design` on a saga/outbox prompt. Deviation from plan: did **not** rewire the `designSystem` workflow — forcing DDD/event-driven steps into a generic system-design flow would break its generality and `mustPass` artifact gates; the skills route independently instead.
- **P2 AI/agents depth** — Status: **done.** Extended `polymath-ai` (0.3.0→0.4.0) with `agent-design`, `llm-guardrails`, `llm-cost-latency`, each with a soft-tier `routing.yaml`; README/CHANGELOG/marketplace updated; 1 new golden fixture (`agent-design-support-triage`). Indexes regenerated (65 surfaces). Verification: conformance OK, DESC-1/DOCS-2/SURFACE-INDEX/catalog green, ROUTE-EVAL-1 PASS (precision 1.0, FP 0). Decision: `llm-security-review` deferred to P4 (lands in `polymath-security` alongside `owasp-review`/`stride-threat-model`, referencing `llm-guardrails` for the controls). MLOps/fine-tuning/recommenders/CV/DL/RL remain in the deferral registry.
- **P3 streaming + data engineering** — Status: **done.** Decision: a **new `polymath-streaming` plugin** (not a `polymath-data` extension) — data/streaming *engineering* is distinct from `polymath-data`'s analytics. Four skills (`streaming-design`, `data-pipeline`, `data-modeling`, `stream-processing`), each with a soft-tier `routing.yaml`; registered in marketplace.json + catalog (`experimental`) + stability-evidence; 1 golden fixture. Root README plugins 38→39. Indexes regenerated (69 surfaces). Verification: conformance OK, catalog/stability/aggregates/routing/DESC-1/DOCS-2/SURFACE-INDEX/CATALOG green, ROUTE-EVAL-1 PASS.
- **P4 security breadth + IaC** — Status: **done.** Extended `polymath-security` (0.4.0→0.5.0) with `auth-design`, `compliance-mapping`, `devsecops-pipeline`, `crypto-review`, `llm-security-review` (P2's deferred LLM-security audit landed here, referencing `polymath-ai:llm-guardrails`); new `polymath-iac` plugin (`terraform-module`, `terraform-state`, `policy-as-code`). Decision: dropped the planned `iac-review` skill — `polymath-cloud:plan-review` already does exactly that (no-duplication rule); `polymath-iac` README points to it. Each skill has a soft-tier `routing.yaml`; registered; 2 golden fixtures. Root README 39→40. Verification: conformance OK, budgets ok (security 352, iac 132), ROUTE-EVAL-1 PASS. Deferred: Zero-Trust, Penetration-Testing.
- **P5 operating mechanisms + leadership** — Status: **done.** Seven skills across existing plugins: `polymath-backend:api-versioning` (placed here, not `release`, which was at 393/400 budget), `polymath-engineering:tech-debt-management`, `polymath-sre:demand-forecast` + `oncall-design`, `polymath-leadership:hiring-loop` + `conflict-mediation` + `coaching-plan`. Each with a soft-tier `routing.yaml`; READMEs/versions/CHANGELOGs/marketplace updated; 2 golden fixtures. Consequence handled: adding skills to profile-member plugins raised profile always-on costs — `backend` profile budget 1950→2250, `staff` 2550→2650 (reviewed, per the budget-note). Deferred: a dedicated arch-review-governance skill (existing `architecture-review-facilitation` is close); the new flows (`architectureReview`, `migrationPlaybook`, `capacityReview`, `gameDay`, `hiringLoop`, `evalDrivenDevelopment`, `dataPipelineBuild`) — see below.

## Final verification (2026-06-13)

Whole program green through both entry points: `tools/conformance.sh --all` → `conformance: OK`; `tools/validate-all.sh` → `validate-all: OK` (marketplace `claude plugin validate --strict` passes). ROUTE-EVAL-1 PASS throughout (token precision 1.0, false-positives 0/12 — the locked invariant held across all 30 new surfaces). Totals: **37→40 plugins**, **153→183 skills**, **54→84 declared routable surfaces** (67/183 skills deterministically routable), 6 new golden fixtures. Per-plugin always-on budgets all ≤400 (max: architecture 380, security 352).

**Skills delivered** (30): architecture ×8, ai ×3, streaming ×4, security ×5, iac ×3, backend ×1, engineering ×1, sre ×2, leadership ×3.

**Deviations from plan, with rationale:**
- `designSystem` workflow **not** rewired (P1) — forcing DDD/event-driven steps into a generic system-design flow breaks its generality and `mustPass` gates; the techniques route independently.
- `iac-review` **dropped** (P4) — duplicates `polymath-cloud:plan-review` (no-duplication rule).
- **Flows: 6 of the 7 shipped** (follow-up turn, 2026-06-13). New workflows composing the new skills: `techDebtPaydown` (identify → plan → pin → address → verify → review — the explicit ask), `dataPipelineBuild`, `evalDrivenDevelopment`, `migrationPlaybook`, `gameDay`, `capacityReview`. Each ships a `workflows/*.yaml` (validates via `polymath-flow validate`), a `routing/*.yaml` (paths + intents + `alt` to the sibling skill, no regex — avoids collision), and a `workflow-triggering` test. **`hiringLoop` skipped** — the `hiring-loop` *skill* already runs the full scorecard→stages→debrief loop, so a wrapping workflow would be a thin single-step shim. **`architectureReview` skipped** — it would overlap the existing `designSystem` workflow. Both skips recorded here.

## Final verification — workflows (2026-06-13, follow-up)

Whole marketplace green again with workflows added: `conformance.sh --all` OK, `validate-all.sh` OK. 26→**32 workflows**; WORKFLOW-INDEX OK (tier A 16 / tier B 16, ~395 ≤ 400 injection tokens — the 6 new flows landed in Tier B, budget held); WORKFLOW-TRIGGER OK; PROMOTION-2 OK (all `invoke:` targets resolve); ROUTE-EVAL-1 PASS (precision 1.0, FP 0); HINT-BUDGET OK. 90 declared routable surfaces (was 84). Route-hint verified: a tech-debt prompt proposes `techDebtPaydown` (workflow) with `tech-debt-management` (skill) as the lighter alternative.

## Deferred (now-tracked follow-up work)

- **`hiringLoop` / `architectureReview` workflows** — intentionally not shipped (rationale above); reopen only if a wrapping arc proves needed beyond the existing skill/workflow.
- **Specialized skills** from the deferral registry below (CQRS/CRDTs/Formal-Methods; MLOps/fine-tuning/recommenders/CV/DL/RL; Zero-Trust/Pentest; arch-review governance).
- **Promotion to `beta`**: all new surfaces are `experimental` with `pre-evidence` ledger entries; promotion needs a skill-triggering test + bakeoff case per plugin (STABILITY-1), plus a live workflow-triggering run for the new flows.
