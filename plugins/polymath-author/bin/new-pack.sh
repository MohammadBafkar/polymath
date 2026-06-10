#!/usr/bin/env bash
# Scaffold a defaults pack: a standalone marketplace carrying one or more
# conventions plugins that localize Polymath at any scope — organization,
# team, product line, or project archetype.
#
# Usage: /polymath-author:new-pack <pack-name> [target-dir]
#   pack-name: lowercase slug for the scope, e.g. "acme", "payments-team",
#   or "fintech-microservice". target-dir defaults to ./<pack>-polymath-pack.
#
# Two modes:
#   create — target absent/empty: scaffold a fresh pack marketplace with
#            one <pack>-conventions plugin.
#   add    — target already contains .claude-plugin/marketplace.json:
#            add another scope plugin to the existing pack (so one company
#            repo can stack org + team + project-archetype plugins).
#
# Stacking semantics (documented in the generated skill): apply-defaults
# never overwrites existing config or files, so apply the NARROWEST scope
# first; broader packs fill only the remaining gaps; hand-edited repo
# config always wins.
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <pack-name> [target-dir]" >&2
  exit 1
fi

pack="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9-' '-' | sed 's/^-*//; s/-*$//')"
if [[ -z "$pack" ]]; then
  echo "error: pack-name must contain letters/digits" >&2
  exit 1
fi
target="${2:-$PWD/${pack}-polymath-pack}"
plugin="${pack}-conventions"
plugin_dir="$target/plugins/$plugin"

mode="create"
if [[ -f "$target/.claude-plugin/marketplace.json" ]]; then
  mode="add"
  if [[ -e "$plugin_dir" ]]; then
    echo "error: $plugin_dir already exists in this pack" >&2
    exit 1
  fi
elif [[ -e "$target" && -n "$(ls -A "$target" 2>/dev/null)" ]]; then
  echo "error: $target exists, is not empty, and is not a pack (no .claude-plugin/marketplace.json)" >&2
  exit 1
fi

# Locate the convention skeletons: installed layout first (same-marketplace
# symlink dereferenced into this plugin at install time), then the
# marketplace working tree (local development).
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
seed_dir=""
for cand in "$script_dir/../templates/conventions" \
            "$script_dir/../../polymath-core/templates/conventions"; do
  if [[ -d "$cand" ]]; then seed_dir="$(cd "$cand" && pwd)"; break; fi
done

mkdir -p "$target/.claude-plugin" "$target/registry" \
         "$plugin_dir/.claude-plugin" "$plugin_dir/skills/apply-defaults" \
         "$plugin_dir/starter/.polymath/conventions"

write() { # write <path> with __PACK__/__PLUGIN__ substituted from stdin
  sed -e "s/__PACK__/$pack/g" -e "s/__PLUGIN__/$plugin/g" > "$1"
}

if [[ "$mode" == "create" ]]; then
  write "$target/.claude-plugin/marketplace.json" <<'EOF'
{
  "name": "__PACK__",
  "description": "__PACK__ defaults pack for Polymath: conventions corpus and scope defaults, applied per repo by copy-in.",
  "plugins": [
    {
      "name": "__PLUGIN__",
      "source": "./plugins/__PLUGIN__",
      "description": "__PACK__ conventions corpus + apply-defaults copy-in for Polymath localization.",
      "version": "0.1.0",
      "category": "foundation"
    }
  ]
}
EOF

  write "$target/registry/${pack}-catalog.json" <<'EOF'
{
  "plugins": {
    "__PLUGIN__": { "status": "experimental" }
  }
}
EOF
  # Status metadata lives in this sidecar, never in marketplace.json —
  # Claude Code validates manifests strictly and rejects unknown fields.

  write "$target/README.md" <<'EOF'
# __PACK__ Polymath defaults pack

Marketplace carrying conventions plugins for one or more scopes
(organization, team, product line, project archetype). Each plugin ships
an `apply-defaults` copy-in skill. To add another scope plugin to this
pack: run `/polymath-author:new-pack <scope-name> <path-to-this-repo>`.

When a repo uses several scopes, apply the NARROWEST first (project
archetype → team → org): apply-defaults never overwrites, so broader
packs only fill the remaining gaps.
EOF
else
  # add mode: register the new plugin in the existing manifests.
  python3 - "$target" "$plugin" <<'PY'
import json, pathlib, sys
target, plugin = pathlib.Path(sys.argv[1]), sys.argv[2]
mp_path = target / ".claude-plugin" / "marketplace.json"
m = json.loads(mp_path.read_text())
m.setdefault("plugins", []).append({
    "name": plugin,
    "source": f"./plugins/{plugin}",
    "description": f"{plugin[:-len('-conventions')]} conventions corpus + apply-defaults copy-in for Polymath localization.",
    "version": "0.1.0",
    "category": "foundation",
})
mp_path.write_text(json.dumps(m, indent=2) + "\n")
cats = sorted((target / "registry").glob("*-catalog.json"))
if cats:
    c = json.loads(cats[0].read_text())
    c.setdefault("plugins", {})[plugin] = {"status": "experimental"}
    cats[0].write_text(json.dumps(c, indent=2) + "\n")
print(f"registered {plugin} in {mp_path}" + (f" and {cats[0]}" if cats else " (no catalog found)"))
PY
fi

write "$plugin_dir/.claude-plugin/plugin.json" <<'EOF'
{
  "name": "__PLUGIN__",
  "version": "0.1.0",
  "description": "__PACK__ conventions corpus and scope defaults: one install localizes Polymath skills to __PACK__'s stack, rules, and templates.",
  "license": "MIT"
}
EOF

write "$plugin_dir/skills/apply-defaults/SKILL.md" <<'EOF'
---
name: apply-defaults
description: Copy __PACK__'s Polymath defaults into this repo — starter .polymath/ config and the conventions corpus. Run once per repo, before or via polymath-core:init-project.
---

# apply-defaults

> Localize this repo to __PACK__'s conventions by copy-in. The skill name
> `apply-defaults` is a Polymath convention: `polymath-core:init-project`
> detects it and proposes running it first.

## Stacking

When several packs apply to one repo (org + team + project archetype),
run the NARROWEST scope first. This skill never overwrites existing keys
or files, so broader packs fill only the remaining gaps, and hand-edited
repo config always wins.

## Procedure

1. Resolve this plugin's root (the directory containing this skill, two
   levels up — `${CLAUDE_PLUGIN_ROOT}` when available).
2. If the repo has NO `.polymath/project.yaml`: copy
   `starter/.polymath/project.yaml` there. If one EXISTS: merge only the
   keys the repo file does not set — never overwrite repo intent.
3. Copy `starter/.polymath/conventions/` into the repo's
   `.polymath/conventions/` (skip files that already exist).
4. Ensure `conventions_docs` in `.polymath/project.yaml` maps each copied
   doc by role (the starter file already carries the role map).
5. Report what was copied, what was skipped, and the count of open
   `[VERIFY: …]` markers still to confirm.

## What this skill does *not* do

- Never overwrites existing repo config or conventions.
- Never commits — the developer reviews and commits the copied files.
- Pack updates do not propagate automatically: re-run this skill (it
  re-offers only what is missing) after updating the pack.
EOF

write "$plugin_dir/starter/.polymath/project.yaml" <<'EOF'
schemaVersion: 1
# __PACK__ defaults — copied into each repo by __PLUGIN__:apply-defaults.
# Repo-specific values (stack, setup) are added by polymath-core:init-project.
conventions:
  commit_style: conventional-commits   # [VERIFY: confirm __PACK__'s commit style]
conventions_docs:
  knowledge-base: .polymath/conventions/knowledge-base.md
  review-checklist: .polymath/conventions/review-checklist.md
  artifact-matrix: .polymath/conventions/artifact-matrix.md
EOF

write "$plugin_dir/README.md" <<'EOF'
# __PLUGIN__

__PACK__'s Polymath defaults plugin. Installing it gives every repo in
scope a one-command localization path:

1. `claude plugin marketplace add <this-repo-url-or-path>`
2. `claude plugin install __PLUGIN__@<pack-marketplace-name>`
3. In each repo: run `/polymath-core:init-project` (it detects this
   plugin's `apply-defaults` skill and proposes the copy-in), or run
   `/__PLUGIN__:apply-defaults` directly.

## What to fill in

- `starter/.polymath/conventions/*.md` — replace `{{placeholders}}` with
  this scope's reality. Anything inferred and unconfirmed keeps a
  `[VERIFY: …]` marker; consuming skills will not treat marked content as
  authoritative.
- `starter/.polymath/project.yaml` — scope-wide defaults only; repo files
  always win over copied defaults.
- Add stack docs per area (`backend-stack`, `frontend-stack`, `database`,
  `auth`, `deployment`, `shared-libraries`) and register each in the
  starter's `conventions_docs` role map.

## Validation

This pack is gate-shaped for Polymath conventions: manifests are strict
(status lives in `registry/<pack>-catalog.json`, never marketplace.json),
the skill description stays ≤200 chars, and SKILL.md bodies stay ≤500
lines. To run Polymath's own checks against this pack, clone the Polymath
marketplace and point its `tools/conformance.sh` at this tree.
EOF

write "$plugin_dir/CHANGELOG.md" <<'EOF'
# Changelog — __PLUGIN__

## [Unreleased]

### Added

- Initial defaults-pack scaffold: apply-defaults copy-in skill, starter
  `.polymath/` config, conventions corpus skeletons.
EOF

# Seed the conventions corpus from the Polymath skeletons.
if [[ -n "$seed_dir" ]]; then
  for f in knowledge-base.md stack-doc.md artifact-matrix.md review-checklist.md; do
    [[ -f "$seed_dir/$f" ]] && cp "$seed_dir/$f" "$plugin_dir/starter/.polymath/conventions/$f"
  done
  echo "Seeded conventions corpus from $seed_dir"
else
  echo "warning: convention skeletons not found; starter/.polymath/conventions/ left empty" >&2
fi

echo "Scaffolded ($mode) pack plugin at $plugin_dir"
echo "Next steps:"
echo "  1. Fill in plugins/$plugin/starter/.polymath/conventions/*.md (replace placeholders; keep [VERIFY: ...] on unconfirmed items)"
echo "  2. Adjust the starter project.yaml defaults for this scope"
echo "  3. Push to your git host; teammates: claude plugin marketplace add <url>"
