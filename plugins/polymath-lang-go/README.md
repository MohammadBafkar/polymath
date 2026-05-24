# polymath-lang-go

Go craft for the Polymath marketplace.

## What it ships

- Skills:
  - `write-go-test` — table-driven + `t.Run` + `t.Cleanup`; stdlib `httptest`/`iotest`/`fstest` over hand-rolled fakes.
  - `audit-go-mod` — toolchain drift, indirect bloat, `replace` cleanliness, `govulncheck`-reachable findings.
- Commands: `/polymath-lang-go:test`, `/polymath-lang-go:audit`.

## Installation

```bash
claude plugin install polymath-lang-go@polymath
```

## Dependencies

- `polymath-core`
- `polymath-engineering`

## License

Apache-2.0.
