# Changelog — polymath-devops

<!-- markdownlint-disable MD024 -->

## [0.11.0]

### Fixed

- `ci-pipeline-github`: the example's `setup-node` pnpm cache ran before pnpm existed; third-party actions pinned by SHA (as the skill demands); `pull_request_target` and `${{ }}` script injection; deploy workflows don't cancel in progress; fork PRs have no OIDC.
- `audit-dockerfile`: HEALTHCHECK uses a binary already in the image (curl advice contradicted `dockerize`).
- `audit-compose`: host-escape findings (privileged, Docker socket, host network/PID, broad caps); When-to-use/Inputs.
- `env-promotion`: promote by digest; rollback depends on backward-compatible migrations.

### Removed

- The `/audit-dockerfile` and `/audit-compose` commands (same-named skills already provide them).

## [0.8.0]

DevOps craft: multi-stage Dockerfile, GitHub Actions pipelines, env-promotion.

### Skills

- **audit-compose** — Audit docker-compose.yaml — image pinning, named volumes, networks, secret injection, depends_on health-conditioning.
- **audit-dockerfile** — Audit a Dockerfile for base-image hygiene, layer order, multi-stage discipline, secret leakage, and missing healthcheck/USER directives.
- **ci-pipeline-github** — Author a GitHub Actions workflow — lint/test/build/deploy with caching, concurrency control, OIDC for cloud auth, minimal permissions.
- **dockerize** — Write a multi-stage Dockerfile — distroless or minimal base, build/runtime split, deterministic layer order, non-root user, no secrets baked in.
- **env-promotion** — Design env-promotion (dev → staging → prod) — one artifact promoted, env-specific config injected, gates between stages, rollback path.

### Commands

- **/audit-compose** — Audit a Docker Compose file before you ship it; command entry point for the audit-compose skill.
- **/audit-dockerfile** — Audit a Dockerfile for base-image, layer order, USER, healthcheck, secrets.
