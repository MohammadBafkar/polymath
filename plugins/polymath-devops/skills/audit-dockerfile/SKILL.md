---
name: audit-dockerfile
description: Audit a Dockerfile for base-image hygiene, layer order, multi-stage discipline, secret leakage, and missing healthcheck/USER directives.
---

# audit-dockerfile

> Find footguns in a Dockerfile before they ship. Output is a categorized review with concrete diffs.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A new Dockerfile or a non-trivial change to an existing one.
- Image size jumped or build is slow.
- A security scanner flagged the image.

## Inputs

- The Dockerfile (required) and its `.dockerignore` (optional — its absence is a finding).
- The runtime target (optional): Kubernetes, ECS, Cloud Run, bare Docker — it decides whether `HEALTHCHECK` matters.
- Scanner output (optional): a Trivy/Grype report that prompted the audit.

## Procedure

0. **Deterministic baseline.** If `hadolint` is available (`hadolint Dockerfile`, or `docker run --rm -i hadolint/hadolint < Dockerfile`), run it first and fold its rule IDs into the findings below; never mark a line clean that it flags without saying why the rule doesn't apply.
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
5. **HEALTHCHECK.** Define one unless the orchestrator handles it (Kubernetes ignores `HEALTHCHECK` and uses probes). Use a binary already in the image — exec form, e.g. `HEALTHCHECK CMD ["/app/healthcheck"]` or the app's own `--health` flag. Don't install `curl` just for this; distroless/slim runtimes don't have it, and it widens the attack surface.
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

  - No HEALTHCHECK directive (image runs under Docker Compose, not k8s).
    Fix: HEALTHCHECK CMD ["node", "healthcheck.js"]   (node is already in the image)

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
