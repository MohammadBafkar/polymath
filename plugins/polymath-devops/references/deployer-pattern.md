# The deployer pattern

Polymath ships **no autonomous deployer** — deployment mutates
infrastructure, and flows-lite's contract excludes shell steps that do
(see `docs/WORKFLOW-SCHEMA.md` § 7 and `LIMITATIONS.md`). What ships
instead is this pattern: the existing surfaces composed into a deploy
loop where every mutating step is proposed by an agent and executed by
the team's own pipeline.

## The composition

```text
artifact build            ci capability (.polymath/capabilities.yaml)
        │
        ▼
env promotion design      polymath-devops:env-promotion
  (one artifact, gates    — promote the SAME artifact dev → staging →
   between stages)          prod; env config injected, never rebuilt
        │
        ▼
rollout orchestration     progressiveRollout workflow (flows-lite)
  (flag ramp + SLO        — staged percentages, health gates between
   health gates)            stages, rollback path pinned up front
        │
        ▼
boot verification         appStarts gate (smoke.<lang> recipe in
  (the app actually        .polymath/project.yaml) — tests passing
   serves)                 does not imply the app runs
        │
        ▼
deploy execution          YOUR pipeline (GitHub Actions / Azure
  (the only mutating       Pipelines / Argo / …) — triggered by a
   step)                   human or by CI on the merged change
```

## Division of labor

| Concern | Owner |
| --- | --- |
| What to deploy, in what stages, behind which gates | Agent, via `env-promotion` + `progressiveRollout` — produces the plan and the workflow run |
| Whether the app boots in the target env | `appStarts` gate from the project's `smoke` recipe |
| Actually mutating infrastructure | The team's pipeline, with its own credentials and approvals — never an agent tool call |
| Cloud shape decisions (where it runs) | `polymath-cloud:design-aws/azure/gcp` patterns |
| Manifests / Dockerfiles / CI files | `polymath-kubernetes:write-manifest`, `polymath-devops:dockerize`, `polymath-devops:ci-pipeline-github` — canonical bodies, reviewed like any code |

## Wiring it in a localized repo

1. Declare the `ci` (and `cloud`, if used) capability in
   `.polymath/capabilities.yaml` so workflows resolve the provider.
2. Add a `smoke.<lang>` recipe to `.polymath/project.yaml` — the
   `progressiveRollout` / verification steps gain a real boot check.
3. Encode env-specific reality (cluster names, promotion order, freeze
   windows) in a `deployment` conventions doc (`conventions_docs`), so
   every skill above reads the same source.
4. The pipeline's deploy job stays in your CI config. Agents draft and
   update it (canonical bodies), humans review and merge it, CI runs it.

## Why no autonomous deployer

An agent-driven deploy would need write-scoped cloud credentials inside
the agent loop, idempotent rollback under partial failure, and an audit
chain the team already gets from its pipeline — duplicated worse. The
pattern above keeps agents at the planning/verification edges where they
add leverage, and leaves the mutation in the system that already owns
approvals, secrets, and history.
