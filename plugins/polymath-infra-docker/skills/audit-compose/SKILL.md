---
name: audit-compose
description: Audit docker-compose.yaml — image pinning, named volumes, networks, secret injection, depends_on health-conditioning.
---

# audit-compose

> Spot the patterns in a compose file that bite when you actually run it: floating images, host-mount surprises, secrets in ENV, missing health gates.

## Procedure

1. **`image:` pinning.** Each service should be digest-pinned for production-shaped compose; tag-pinned for dev is fine if the tag is specific (`postgres:16.3`, not `postgres:latest`).
2. **Volumes.** Named volumes over bind mounts unless the bind is deliberate (source code in dev). `volumes: ['/host/path:/container/path']` outside `./` is suspicious.
3. **Networks.** Define explicit networks; the implicit `default` works but services accidentally pick it up. For DB + app separation, two networks (`db_net`, `web_net`) limit lateral exposure.
4. **Secrets.**
   - Use Compose secrets (`secrets:` top-level + `secrets:` per-service) over `environment:` for credentials.
   - `env_file: .env` is fine for dev; in CI/prod surface a warning.
5. **`depends_on`** with `condition: service_healthy` — services must wait until dependents pass healthcheck, not just "started". Plain `depends_on: [db]` only orders startup, not readiness.
6. **`restart:` policy.** Production: `unless-stopped` or `on-failure`. Dev: `no` is fine.
7. **Resource limits.** `deploy.resources.limits` (Swarm) or runtime `cpus:` / `mem_limit:` (compose-direct). Without limits, one container can starve others on the host.
8. **`ports:` exposure.** `127.0.0.1:5432:5432` over `5432:5432` for local-only services. Without the bind address, the port is open to the host's external interfaces.
9. **`profiles:`** for optional services (`profiles: [dev]`); keeps a single compose file from running everything in prod.

## Output

```text
audit-compose

File: docker-compose.yaml (3 services: web, db, redis)

Issues
  - web.image: app:latest                             ✗ floating tag
  - db.image: postgres:16.3                           ✓ tag-pinned (acceptable for dev)
  - web.depends_on: [db]                              ⚠ no health condition
    Fix: depends_on: { db: { condition: service_healthy } }
  - db.ports: "5432:5432"                             ⚠ exposed to host external interface
    Fix: "127.0.0.1:5432:5432"
  - db.environment.POSTGRES_PASSWORD: "secret"        ✗ plain-text in compose
    Fix: use Compose secrets or env_file.
  - No memory limits on any service.
    Fix: deploy.resources.limits.memory per service.

Recommendation: 5 fixes; prod readiness requires all addressed.
```

## Anti-patterns to avoid

- `image: foo:latest`. Reproducibility fail.
- Plain-text credentials in `environment:`. Show up in `docker inspect`.
- `depends_on` without `condition: service_healthy` for stateful deps. Race conditions on startup.
- Single compose file used in dev *and* prod with no `profiles` / overrides.
