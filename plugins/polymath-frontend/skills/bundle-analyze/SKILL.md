---
name: bundle-analyze
description: Find the biggest bytes in a JavaScript bundle and propose the cheapest cut; uses the bundler's report rather than guessing.
---

# bundle-analyze

> Read the bundler's stats output, identify the top contributors to bundle size, and propose one specific cut.

## When to use

- A bundle has grown materially and we don't know why.
- A new dependency is being added; want to know its cost.
- A workflow needs a "what should we remove?" answer.

## Inputs

- A bundler stats file. Detect from these signals:
  - **Vite / Rollup**: `dist/stats.html` or `--mode=production --report` output.
  - **Webpack**: `stats.json` from `webpack --json`.
  - **Next.js**: `.next/analyze/*.html` from `@next/bundle-analyzer`.
  - **esbuild**: `--metafile=meta.json`.
- The route(s) the bundle serves.

## Procedure

1. Read the stats. If only `dist/` exists, ask the user to enable the bundler's stats output.
2. List the top 10 contributors by **gzipped** size. Treebar/list ranking is fine.
3. For each top contributor, classify:
   - **Necessary** — load-bearing for the route.
   - **Polyfill** — verify the target browsers actually need it.
   - **Vendor bloat** — uses 10% of a library but ships 100% of it.
   - **Dupe** — same library appearing twice with different versions (look at the dependency tree).
   - **Dev-only leak** — should not be in prod (`process.env.NODE_ENV`, debug builds, source maps shipped).
4. Pick the **single highest-leverage cut**. Cheaper-to-do beats potentially-larger savings.

## Output

```text
Bundle analysis: <route>

Top 10 (gzipped):
  1. moment (62 KB)             — Vendor bloat (using formatDate only)
  2. lodash (38 KB)             — Vendor bloat (deep-imports cost; tree-shake or use lodash-es)
  3. react-icons (24 KB)        — Necessary
  ...

Highest-leverage cut:
  Replace `moment` with `Intl.DateTimeFormat` for the two call sites in
  src/utils/date.ts. Estimated savings: 60+ KB gzipped.
  Risk: low (no timezone math used).
```

## Anti-patterns to avoid

- "Adopt webpack 5 / vite / X" — micro-optimization vs. picking the right cut.
- Cutting dev dependencies (they don't ship).
- Premature code-splitting before identifying the actual heavy chunk.
