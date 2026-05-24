---
description: Audit go.mod / go.sum for toolchain drift, indirect bloat, vulnerable versions, and stale replace directives.
---

Invoke `polymath-lang-go:audit-go-mod`.

Output expected: a categorized audit covering toolchain pinning, direct/indirect ratio, replace directives, govulncheck-reachable findings, and concrete bump commands.
