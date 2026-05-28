---
name: audit-dockerfile
description: Audit a Dockerfile for base-image hygiene, layer order, multi-stage discipline, secret leakage, and missing healthcheck/USER directives.
---

# audit-dockerfile

> Find footguns in a Dockerfile before they ship. Output is a categorized review with concrete diffs.

## When to use

- A new Dockerfile or a non-trivial change to an existing one.
- Image size jumped or build is slow.
- A security scanner flagged the image.

## Procedure

1. **Base image.**
   - Prefer **digest-pinned** `FROM image@sha256:…` for production builds. Tag-pinned (`alpine:3.19`) floats on each rebuild.
   - Avoid `:latest`. Refuse to approve.
   - Distroless or slim variants where the runtime allows (smaller attack surface).
2. **Multi-stage.** Use builder + runtime stages. The final stage should not include compilers, package managers, or dev deps.
3. **Layer order.** Cacheable layers first:
   ```dockerfile
   COPY package.json package-lock.json ./
   RUN npm ci
   COPY . .
   ```
   Reversing this invalidates the `npm ci` cache on every source edit.
4. **USER directive.** Final stage must `USER non-root` (numeric UID or named). Running as root is a common scanner finding.
5. **HEALTHCHECK.** Define one unless the orchestrator (k8s) handles it externally. `CMD curl -fsS http://localhost:PORT/health || exit 1` is the usual shape.
6. **Secrets.**
   - No `ENV SECRET=…` for build-time secrets. Use `--secret` mount (BuildKit).
   - No `COPY .env .` ever.
   - `ARG` values appear in image history — never sensitive.
7. **`COPY` discipline.**
   - `COPY src/ ./src/` over `COPY . .` (avoids accidental `node_modules` / `.git` inclusion).
   - `.dockerignore` should exist and exclude `.git`, `node_modules`, build artifacts, OS junk.
8. **`RUN` cleanup.** Single `RUN` with `&& apt-get clean && rm -rf /var/lib/apt/lists/*` style. Multiple `RUN` install lines leave layers full of cached package metadata.
9. **`ENTRYPOINT` vs `CMD`.** ENTRYPOINT for the binary; CMD for default args. JSON-form (`["bin", "arg"]`) over shell-form to avoid signal-handling surprises.
10. **EXPOSE.** Cosmetic; orchestrators ignore it. Keep for documentation.

## Output

```text
audit-dockerfile

File: Dockerfile (multi-stage, 2 stages)

Issues
  - FROM node:20 (tag-pinned, floats)
    Fix: FROM node:20@sha256:<digest>

  - Final stage runs as root.
    Fix: add `USER node` (or numeric UID 1000) before CMD.

  - COPY . . (line 18) pulls in .git + node_modules.
    Fix: COPY src/ ./src/ + COPY package.json ./ + .dockerignore.

  - No HEALTHCHECK directive.
    Fix: HEALTHCHECK CMD curl -fsS http://localhost:3000/health || exit 1

  - Three separate RUN apt-get install lines.
    Fix: combine into one RUN with apt-get clean tail.

Recommendation: 5 fixes; image size reduction estimated ~120MB.
```

## Quality bar

- Base image digest-pinned (or explicit decision to tag-pin with rationale).
- Final stage runs as non-root.
- Healthcheck present unless orchestrator handles it.
- No secrets in ENV / ARG / COPY of source files.
- `.dockerignore` reviewed alongside.

## Anti-patterns to avoid

- `FROM ubuntu:latest`. Floats.
- `ADD https://…` to fetch remote files. Cache-unfriendly + verifies poorly.
- `RUN curl … | bash`. Pipe-to-shell from a Dockerfile is supply-chain risk.
- `USER root` in the final stage with a comment "we'll fix later". Don't ship.
