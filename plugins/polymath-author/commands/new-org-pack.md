---
name: new-org-pack
description: Scaffold a standalone organization pack (company marketplace + conventions plugin + org-defaults copy-in) via new-org-pack.sh. Lives outside this catalog; not a generic plugin (new-plugin).
---

# /new-org-pack

Scaffold an org pack via `${CLAUDE_PLUGIN_ROOT}/bin/new-org-pack.sh <org-name> [target-dir]`. Produces a company-side marketplace with one `<org>-conventions` plugin: an `org-defaults` copy-in skill (detected by `polymath-core:init-project`), a starter `.polymath/` config with a `conventions_docs` role map, and the conventions corpus seeded from `polymath-core`'s skeletons with `[VERIFY: …]` markers.

The pack is the org's own repo — nothing company-specific ever lands in the Polymath catalog. After scaffolding, the org fills in the conventions and pushes the pack to its git host.
