---
artifact: ArchitectureDoc
schemaVersion: 0.1
title: "{{title}}"
owner: "{{owner}}"
created: "{{date}}"
model: c4
---

# Architecture: {{title}}

C4 model layers: System Context → Containers → Components → Code (last
omitted for most docs).

## Purpose

What system this document describes, who needs to read it, and what
decisions it should ground.

## System context (C4 L1)

The system in relation to its users and the external systems it depends on
or serves.

```mermaid
flowchart LR
  user[/"User"/]
  sys[("This system")]
  ext1[("External system A")]
  user -->|HTTPS| sys
  sys -->|gRPC| ext1
```

## Containers (C4 L2)

The deployable units (services, databases, queues, frontends) and how they
communicate.

```mermaid
flowchart TB
  web[Web app]
  api[API service]
  db[(Database)]
  q[Queue]
  web --> api --> db
  api --> q
```

| Container | Tech | Responsibility | Persistence |
| --------- | ---- | -------------- | ----------- |
| Web app | … | … | none |
| API service | … | … | none |
| Database | … | … | … |

## Components (C4 L3)

Inside the most interesting container. Show the major modules and how they
collaborate.

## Cross-cutting concerns

- AuthN / AuthZ
- Observability (logs, metrics, traces — link to runbooks)
- Data classification
- Failure modes and degraded states

## References

- PRD: `{{prd_link}}`
- ADRs: ADR-…, ADR-…
