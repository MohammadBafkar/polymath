# polymath-performance

Performance craft for the Polymath marketplace.

## What it ships

- Skills: `perf-budget`, `backend-tail-latency`, `caching-tradeoffs`, `design-cache-layer`, `audit-redis-config`, `app-profiling`, `high-load-io-design`, `http-edge-caching`.
- Commands: `/design-cache` (alias over `design-cache-layer`). `audit-redis-config` is invoked directly as `/polymath-performance:audit-redis-config`.

`app-profiling` finds CPU/memory/allocation hot spots with flame graphs; `high-load-io-design` sizes pools and workers for IO-bound services with a tested Little's-law calculator (`scripts/concurrency.py`); `http-edge-caching` covers `Cache-Control`, cache keys, CDN purge, and personalized-content safety. Database performance lives in `polymath-database`; system-level design in `polymath-scalability`.

## Installation

```bash
claude plugin install polymath-performance@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
