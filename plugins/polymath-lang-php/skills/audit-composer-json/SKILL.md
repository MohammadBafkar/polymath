---
name: audit-composer-json
description: Audit composer.json + composer.lock — PHP version, dependency pin discipline, Roave/SecurityAdvisories, autoload sanity, require vs require-dev separation.
---

# audit-composer-json

> Spot rot in Composer config before a `composer install` flips a contributor over.

## Procedure

1. **`require.php`.** Pin to the minimum supported runtime, e.g. `"php": ">=8.2"`. Mismatched between modules → silent failures on older runtimes.
2. **Pin discipline.**
   - `^1.2` (caret) — usual SemVer. Default.
   - `~1.2` (tilde) — minor floats, patch caps. Use when SemVer is unreliable.
   - `1.2.3` (exact) — only with a tracking comment.
   - `dev-main` — branch deps. Acceptable for shared monorepos with a `branch-alias`; never in published packages.
3. **`require-dev` separation.** Test gear (`phpunit/phpunit`, `mockery/mockery`, `phpstan/phpstan`) must live in `require-dev`. Anything in `require` ships to production.
4. **Security advisories.** Add `roave/security-advisories` as `dev-main` in `require-dev` — refuses install if any required package matches a known advisory. Cheap and effective.
5. **Autoload.** `autoload.psr-4` should map a single namespace to a single directory. Mixed-namespace dirs work but cripple `composer dump-autoload --optimize`.
6. **`scripts`.** A `test` / `lint` / `analyse` script convention helps. CI should run the *script*, not the underlying tool — keeps CI and local in sync.
7. **`composer.lock`** — commit it for applications; for libraries, ignore (consumers resolve their own).
8. **`config.platform.php`** — pin the PHP version Composer assumes when resolving deps, even when the local CLI differs. Stops "works on my machine" issues.

## Output

```text
audit-composer-json

PHP requirement:  ">=8.2"  (matches policy)
config.platform.php: 8.2 (good — pinned for resolution)

Sections
  ✓ require: 8 packages, all using ^ or ~ caret pinning.
  ✗ phpstan/phpstan is in `require` instead of `require-dev`.

Security advisories
  ✗ roave/security-advisories not in require-dev. Add it:
      composer require --dev roave/security-advisories:dev-main

Autoload
  ✓ Single PSR-4 mapping per namespace.

composer.lock
  ✓ committed (this is an application).

Recommendation: move phpstan/phpstan to require-dev, add
                roave/security-advisories.
```

## Anti-patterns to avoid

- `"php": "*"`. Resolves anywhere; runtime surprises.
- `"foo/bar": "*"` floating dep. Reproducibility footgun.
- Test gear in `require`. Adds load to production autoload.
- Missing `roave/security-advisories`. Cheapest improvement available.
