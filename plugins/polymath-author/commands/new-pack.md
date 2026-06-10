---
name: new-pack
description: Scaffold a defaults pack (standalone marketplace + conventions plugin + apply-defaults copy-in) for any scope — org, team, or project archetype — via new-pack.sh. Not a generic plugin (new-plugin).
---

# /new-pack

Scaffold a defaults pack via `${CLAUDE_PLUGIN_ROOT}/bin/new-pack.sh <pack-name> [target-dir]`. The pack name is any scope slug — `acme`, `payments-team`, `fintech-microservice`. Produces a standalone marketplace with a `<pack>-conventions` plugin: an `apply-defaults` copy-in skill (detected by `polymath-core:init-project`), a starter `.polymath/` config with a `conventions_docs` role map, and the conventions corpus seeded from `polymath-core`'s skeletons with `[VERIFY: …]` markers.

Run it again with an existing pack as `target-dir` to ADD another scope plugin (org + team + archetype stack in one repo). Stacking rule: apply the narrowest scope first — apply-defaults never overwrites, so broader packs fill only the gaps. Nothing scope-specific ever lands in the Polymath catalog.
