---
name: multi-region-design
description: Design multi-region deployment — active-active vs standby, RPO/RTO, replication and conflicts, routing, failover. Not single-region HA.
---

# multi-region-design

> Going multi-region trades money, latency, and consistency for survivability and locality. Decide what failure you're buying protection from, then pick the cheapest topology that meets the RPO/RTO — and rehearse the failover.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A requirement for regional-outage survival, a stricter availability SLO than one region can give, or lower latency for global users.
- Data residency / sovereignty requires data to stay in specific regions.
- Reviewing an existing "multi-region" setup that has never been failed over.

Not this when: multi-AZ high availability within a region meets the target — `polymath-cloud:design-aws-pattern` / `design-azure-pattern` / `design-gcp-pattern`; or only DR backups are needed — define RPO/RTO, then restore tests (`polymath-sre:chaos-experiment`).

## Inputs

- The driver: SLO (`polymath-sre:slo-design`), RTO/RPO per data class, latency target by user region, residency rules, regulatory constraints, and the cost envelope.
- Current architecture: stateless tiers, datastores and their replication features, queues/streams, caches, DNS/CDN, third-party dependencies and their regionality.
- The consistency needs of each write: what must be globally unique, what can conflict and merge, what may be stale.
- Historical regional incidents and the dependency map (control planes, identity, DNS, CI/CD, secrets).

## Procedure

1. **Justify it with numbers.** Regional outages are rarer than software failures; compare the availability gain to cost and operational complexity. If single-region multi-AZ plus tested backups meets RTO/RPO, stop. Record which failures the design must survive (AZ, region, provider-wide, control plane, bad deploy — multi-region doesn't fix a bad deploy that replicates everywhere).
2. **Set RPO/RTO per data class** (not per system): money movement RPO≈0 (synchronous or no loss), catalog data minutes, analytics hours. RPO ≈ replication lag at failure; RTO = detection + decision + failover + warm-up.
3. **Choose the topology per tier:**
   - **Backup & restore** (RTO hours, RPO hours; cheapest).
   - **Pilot light / warm standby** (RTO minutes–tens of minutes; data replicated, compute scaled down or minimal; scale on failover).
   - **Active-passive hot standby** (RTO minutes; full capacity idle; failover automated or one-button).
   - **Active-active** (RTO≈0 for the surviving regions; both serve traffic). Requires conflict-free data design and traffic partitioning; highest cost and complexity — justify against warm standby.
4. **Design data replication per store** — the hard part:
   - **Single-writer + async replicas**: simple; RPO = lag > 0; promotion needed; cross-region writes pay latency to the leader (or route writes to home region).
   - **Synchronous cross-region commit** (Spanner, CockroachDB, Aurora global with managed switchover): near-zero RPO, but every commit pays inter-region RTT (tens–hundreds of ms); watch quorum availability if a region is lost.
   - **Multi-writer / active-active** (DynamoDB global tables, Cosmos DB multi-region writes, Cassandra multi-DC): conflicts happen — define resolution (last-writer-wins by timestamp loses data; per-field merge, CRDTs, or home-region-per-entity avoid it) and which operations can never be multi-writer (balances, inventory, uniqueness).
   - **Partition by home region** (each user/tenant has one home region for writes; others read replicas or route): avoids conflicts, satisfies residency, makes failover a per-partition decision.
   - **Events/streams**: mirror topics (MirrorMaker 2, Cluster Linking, Event Hubs geo-replication) with consumer-offset translation; plan for duplicates and reordering across the failover boundary (idempotent consumers).
   - **Caches** are rebuilt or regionally local; never the replicated source of truth. **Object storage** uses cross-region replication; note its RPO is not zero.
5. **Traffic routing.** Global DNS (health-checked, low TTL — remember resolvers and clients that ignore TTL), anycast/global load balancer, or CDN origin failover. Define the health check (a *deep* check on dependencies, but not so deep that a minor dependency failure flaps the region), automatic vs human-approved failover (automatic failover of a database can cause split-brain/data loss — require a fencing mechanism), and capacity: can the survivor absorb 100% of traffic (N+1 at region level, often ≥ 50–100% headroom, or planned load shedding)?
6. **Eliminate hidden single-region dependencies**: identity provider, secrets, config, feature flags, CI/CD to deploy the fix, DNS provider, observability, payment/SMS providers, container registries, and any "global" service that's actually homed in one region. Draw the dependency map and mark each regional/global/unknown.
7. **Failover and failback runbook.** Detection → decision criteria and who decides → steps (promote DB, shift traffic, scale up, drain queues) → verification → communication (`polymath-chat:post-statuspage-update`) → failback (re-seed old primary, reverse replication, catch up, switch traffic back in a window). Failback is a second migration — design it, don't assume it.
8. **Rehearse.** Game days with real traffic shift (`polymath-sre:chaos-experiment`); measure actual RTO and data loss, not designed values; test split-brain fencing and the "region comes back with stale data" case. A failover never exercised will not work.
9. **Residency and compliance.** Map data classes to allowed regions; keep PII home-region-only where required; check that logs, backups, analytics copies, and support tooling don't export it; encryption keys per region.
10. **Cost and operations.** Duplicate compute, cross-region data transfer, replicated storage, double observability; the added deploy/config/migration complexity (schema changes across regions, versions skew during rollout); on-call load. State the incremental cost and compare to the cost of the outage it prevents.

## Output

```text
Multi-region design: payments API

Driver: SLO 99.99% (regional outage budget: ~4 min/month); RTO 15 min / RPO 0 for ledger, 5 min for the rest; EU data stays in EU.
Failures covered: region outage, AZ loss. Not covered: bad deploy (canary + rollback — safe-rollout), provider-wide outage.

Topology: active-active for reads/API, single-writer per home region for the ledger.
  Stateless: us-east + eu-west, each sized for 100% of its own traffic + 60% of the other's [VERIFY: load test].
  Ledger: Postgres per region (home-region partitioning by customer.region); sync replica in a second AZ; async cross-region replica for DR (RPO ≈ lag, p99 2 s) → RPO 0 not met cross-region [TBD: decision — accept ~2 s RPO, or use a synchronous-commit engine and pay the commit latency].
  Catalog/prefs: DynamoDB global tables (LWW acceptable; per-field merge for preferences).
  Events: Kafka per region, MirrorMaker 2 mirroring; consumers idempotent; offsets translated on failover.
  Cache: regional, rebuilt on failover.
Routing: global LB with deep health check (DB + queue) hysteresis 3/5; DNS TTL 30 s as fallback; automatic failover for stateless, human-approved promote for ledger with fencing (old primary demoted by revoking its storage credentials).
Hidden dependencies: IdP (global, multi-region), secrets (replicated), feature flags (cached last-known-good), CI/CD (runs from eu-west), SMS provider (single region → fallback provider).
Failover runbook: detect (3 min) → decide (5 min) → promote + shift (5 min) → verify (2 min) = 15 min target; failback in a planned window after re-seed.
Rehearsal: quarterly game day; last result [TBD]. Residency: EU PII only in eu-west stores; logs scrubbed; per-region KMS keys.
Cost: +[TBD: infra delta] (compute ×1.6, inter-region transfer, double observability) vs outage cost [TBD].
Open: [VERIFY: provider rate limits per region], [TBD: ledger RPO decision with finance].
```

## Quality bar

- The need is justified against cheaper options, and the covered failure types are listed (and the uncovered ones).
- RPO/RTO are per data class, and each store's replication model states its real RPO and conflict behavior.
- Hidden single-region dependencies are mapped; survivor capacity is stated.
- Failover has fencing/split-brain handling, a failback plan, and a rehearsal record or schedule.
- Residency and cost are explicit.

## Anti-patterns to avoid

- Active-active by default, without a conflict-resolution design — silent data loss with last-writer-wins on money or inventory.
- A "DR region" that was never failed over, or whose capacity is a fraction of production.
- Automatic database failover without fencing; relying on DNS TTL alone for failover timing.
- Shipping multi-region while identity, secrets, CI/CD, or DNS live in one region.
- Treating multi-region as a substitute for safe deploys.
- Ignoring cross-region latency: synchronous calls between regions in the request path.
