---
plugin: polymath-devops
scenario: dockerize-go-service
expect:
  invoked:
    - polymath-devops:dockerize
  output_matches:
    - "FROM golang"
    - "distroless"
    - "USER"
    - "(CGO_ENABLED=0|GOOS=linux)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Write a Dockerfile for our Go refund service.

Use polymath-devops:dockerize. Service is a Go 1.22 HTTP API. The
binary listens on :8080 and serves `/healthz`. We want the
smallest safe runtime image.

# Acceptance

- Multi-stage Dockerfile: a Go build stage + a distroless (or scratch)
  runtime stage.
- Runtime stage has `USER` set to a non-root UID.
- Layer order: go.mod/go.sum copied before source for cache efficiency.
- No `apt-get install` in the runtime stage.
- `org.opencontainers.image.source` label present.
