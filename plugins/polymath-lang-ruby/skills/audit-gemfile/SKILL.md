---
name: audit-gemfile
description: Audit Gemfile + Gemfile.lock — Ruby version, gem version pinning, bundle-audit findings, source URLs, group separation.
---

# audit-gemfile

> Spot rot in Bundler config before it hits CI.

## Procedure

1. **`ruby` directive.** `ruby '3.x.y'` in Gemfile should match the org's supported version, not the local dev version.
2. **Source URLs.** A single `source "https://rubygems.org"` is normal. Multiple sources (`source "https://x.com/private"` per-gem) need a sourced-gem block to avoid the dreaded "gem from multiple sources" lockfile collapse.
3. **Pinning.**
   - `gem "foo", "~> 1.0"` — pessimistic; bumps minor, never major. The usual choice.
   - `gem "foo", "= 1.0.0"` — exact; only with a tracking comment.
   - `gem "foo"` — no constraint; floats to whatever Bundler resolves.
   - `gem "foo", github: "..."` — git source. Acceptable for waiting-on-upstream-PR with a tracking comment; otherwise a supply-chain footgun.
4. **Groups.** Test gems in `group :test`, dev gems in `group :development`. Production builds (`BUNDLE_WITHOUT=development:test`) must not need them.
5. **`bundler-audit`.** Run `bundle-audit check --update`. Surface findings; cross-reference against the gem's reachability.
6. **Gemfile.lock.** Commit it for apps; consider not committing for gems (libraries) so consumers can resolve to their own versions.
7. **`platforms`.** `platforms :ruby` (MRI) vs `platforms :jruby` — be explicit when a gem only works on one.

## Output

```text
audit-gemfile

Ruby:           3.3.0 (matches policy)
Bundler:        2.5.x

Sources
  ✓ Single source: rubygems.org

Pinning issues
  - "thor" pinned to "= 1.2.0" without comment.
  - "puma" no version constraint (floating).

bundler-audit
  - rack 2.2.6 → CVE-2024-xxxxx (DoS via parameter parsing).
    Bump: rack 2.2.8.

Groups
  ✓ rspec-rails, factory_bot in :test.

Recommendation: comment or relax the thor exact-pin; add a ~> constraint
                to puma; bump rack.
```

## Anti-patterns to avoid

- `gem "foo"` with no version. Resolved differently across developer machines.
- Mixing rubygems with private sources without per-gem `source` blocks.
- `:git` deps without a `ref:` pin. Floats to the branch HEAD.
- Ignoring `bundler-audit`. Most Ruby vulns are exploitable through reachable code.
