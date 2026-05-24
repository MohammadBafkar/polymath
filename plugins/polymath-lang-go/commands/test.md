---
description: Author or extend a Go test file for the behavior(s) you describe.
---

Invoke `polymath-lang-go:write-go-test` for the behavior(s) the user describes.

Inputs you should gather from context:
- The function or method under test (file path + signature).
- Whether the package uses `_test` (black-box) or in-package tests.
- The assertion library in use (stdlib vs testify); match the prevailing style.

After writing the test:
- Run `go test ./...` and surface any failures.
- Run `go test -race ./...` if the code under test touches goroutines.
