# polymath-deprecation

Deprecation craft: retire a capability on a contract, not a surprise — a staged plan plus the consumer migration path.

## What it ships

- Skills:
  - `deprecation-plan` — two dates (warn + remove), telemetry-gated removal, comms cadence, exception path, in-product markers.
  - `migration-guide` — consumer upgrade steps with before/after examples, ordered steps, gotchas, and rollback.

## Why it exists

The audit found deprecation covered only by `polymath-content:write-sunset-notice` (the customer notice) and the `deprecationToRemoval` / `sunsetCapability` workflows — no skill that *plans* the lifecycle or writes the *consumer migration path*. This plugin fills both, and the workflows can invoke it.

## Installation

```bash
claude plugin install polymath-deprecation@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
