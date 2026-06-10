---
name: dockerize
description: Write a multi-stage Dockerfile — distroless or minimal base, build/runtime split, deterministic layer order, non-root user, no secrets baked in.
---

# dockerize

> Write a Dockerfile that's small, fast to rebuild, and safe to run.

## When to use

- A new service needs a container image.
- An existing Dockerfile is bloated, slow, or runs as root.

## Inputs

- Language + framework.
- Build artifact shape (compiled binary, JS bundle, Python module).
- Runtime needs (does it need `bash`, `curl`, `ca-certificates`? Often: no.).

## Project localization

Before the procedure, resolve the project snapshot — glob
`~/.claude/plugins/data/*/polymath-core/project-context.json` (newest
wins; absent → skip and use built-in defaults). Then apply (contract:
`polymath-core:project-context`):

- `conventions_docs`: read role `deployment` — approved base images,
  registries, and hosting targets there override the generic choices
  below.

## Procedure

1. **Multi-stage** always. Stage 1 builds; stage 2 runs.
2. **Base images**:
   - **Builder stage**: the official language image with the toolchain (e.g. `golang:1.22-alpine`, `node:20-alpine`, `python:3.12-slim`).
   - **Runtime stage**: pick from smallest to most flexible:
     - **`scratch`** — Go static binaries, Rust musl. Cheapest.
     - **`gcr.io/distroless/static`** / `base` / `cc` — no shell, no package manager. Recommended for compiled languages.
     - **`-slim`** (debian-slim, python-slim) — for languages needing libc + a tiny userspace.
     - **`-alpine`** — only if you've validated musl compatibility (Python wheels often don't).
3. **Layer order** — most-cacheable first:
   1. Copy dependency manifests (`go.mod`, `package.json`, `requirements.txt`).
   2. Resolve dependencies.
   3. Copy source.
   4. Build.
4. **User** — runtime stage runs as a non-root user with a fixed UID (e.g. `USER 65532:65532`). Distroless has `nonroot` baked in.
5. **No secrets** in `ENV` or `ARG`. Use BuildKit secret mounts at build time; runtime secrets via your secret manager.
6. **HEALTHCHECK** if the orchestrator doesn't supply one. Keep it cheap (< 1s, no DB calls).
7. **Labels** — `org.opencontainers.image.source`, `.version`, `.revision`. Lets the registry tie images back to a commit.

## Output

```dockerfile
# syntax=docker/dockerfile:1.7

FROM golang:1.22-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go mod download
COPY . .
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/refund ./cmd/refund

FROM gcr.io/distroless/static-debian12:nonroot
WORKDIR /
COPY --from=build /out/refund /refund
USER 65532:65532
ENTRYPOINT ["/refund"]

LABEL org.opencontainers.image.source="https://github.com/example/refund-service"
LABEL org.opencontainers.image.version="0.1.0"
```

## Quality bar

- Runtime image < 100 MB for a Go service; < 200 MB for Node; < 250 MB for Python-slim.
- `USER` is set; not running as root.
- No `apt-get install curl bash` "just in case".
- `.dockerignore` excludes `.git`, `node_modules`, build outputs.

## Anti-patterns to avoid

- Single-stage build copying source + toolchain into prod image.
- `FROM ubuntu:latest` for a Go binary.
- `RUN apt-get update && apt-get install` without `--no-install-recommends` and cleanup.
- Baking secrets via `ARG` (they remain in the image layer history).
