#!/usr/bin/env bash
# Scaffold an organization pack: a standalone company marketplace with one
# conventions plugin that localizes Polymath for every repo in the org.
#
# Usage: /polymath-author:new-org-pack <org-name> [target-dir]
#   org-name: lowercase slug, e.g. "acme". target-dir defaults to
#   ./<org>-polymath-pack. The pack is vendor-neutral Polymath machinery;
#   the org fills in its own conventions — nothing org-specific ships in
#   the Polymath catalog itself.
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <org-name> [target-dir]" >&2
  exit 1
fi

org="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9-' '-' | sed 's/^-*//; s/-*$//')"
if [[ -z "$org" ]]; then
  echo "error: org-name must contain letters/digits" >&2
  exit 1
fi
target="${2:-$PWD/${org}-polymath-pack}"
plugin="${org}-conventions"

if [[ -e "$target" && -n "$(ls -A "$target" 2>/dev/null)" ]]; then
  echo "error: $target exists and is not empty" >&2
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

plugin_dir="$target/plugins/$plugin"
mkdir -p "$target/.claude-plugin" "$target/registry" \
         "$plugin_dir/.claude-plugin" "$plugin_dir/skills/org-defaults" \
         "$plugin_dir/starter/.polymath/conventions"

write() { # write <path> with __ORG__/__PLUGIN__ substituted from stdin
  sed -e "s/__ORG__/$org/g" -e "s/__PLUGIN__/$plugin/g" > "$1"
}

write "$target/.claude-plugin/marketplace.json" <<'EOF'
{
  "name": "__ORG__",
  "description": "__ORG__'s Polymath organization pack: conventions corpus and org defaults for every repo.",
  "plugins": [
    {
      "name": "__PLUGIN__",
      "source": "./plugins/__PLUGIN__",
      "description": "__ORG__ conventions corpus + org-defaults copy-in for Polymath localization.",
      "version": "0.1.0",
      "category": "foundation"
    }
  ]
}
EOF

write "$target/registry/${org}-catalog.json" <<'EOF'
{
  "plugins": {
    "__PLUGIN__": { "status": "experimental" }
  }
}
EOF
# Status metadata lives in this sidecar, never in marketplace.json —
# Claude Code validates manifests strictly and rejects unknown fields.

write "$plugin_dir/.claude-plugin/plugin.json" <<'EOF'
{
  "name": "__PLUGIN__",
  "version": "0.1.0",
  "description": "__ORG__ conventions corpus and org defaults: one install localizes Polymath skills to __ORG__'s stack, rules, and templates.",
  "license": "MIT"
}
EOF

write "$plugin_dir/skills/org-defaults/SKILL.md" <<'EOF'
---
name: org-defaults
description: Copy __ORG__'s Polymath defaults into this repo — starter .polymath/ config and the conventions corpus. Run once per repo, before or via polymath-core:init-project.
---

# org-defaults

> Localize this repo to __ORG__'s conventions by copy-in. The skill name
> `org-defaults` is a Polymath convention: `polymath-core:init-project`
> detects it and proposes running it first.

## Procedure

1. Resolve this plugin's root (the directory containing this skill, two
   levels up — `${CLAUDE_PLUGIN_ROOT}` when available).
2. If the repo has NO `.polymath/project.yaml`: copy
   `starter/.polymath/project.yaml` there. If one EXISTS: merge only the
   org keys the repo file does not set — never overwrite repo intent.
3. Copy `starter/.polymath/conventions/` into the repo's
   `.polymath/conventions/` (skip files that already exist).
4. Ensure `conventions_docs` in `.polymath/project.yaml` maps each copied
   doc by role (the starter file already carries the role map).
5. Report what was copied, what was skipped, and the count of open
   `[VERIFY: …]` markers the org still needs to confirm.

## What this skill does *not* do

- Never overwrites existing repo config or conventions.
- Never commits — the developer reviews and commits the copied files.
- Org updates do not propagate automatically: re-run this skill (it
  re-offers only what is missing) after updating the pack.
EOF

write "$plugin_dir/starter/.polymath/project.yaml" <<'EOF'
schemaVersion: 1
# __ORG__ org defaults — copied into each repo by __PLUGIN__:org-defaults.
# Repo-specific values (stack, setup) are added by polymath-core:init-project.
conventions:
  commit_style: conventional-commits   # [VERIFY: confirm __ORG__'s commit style]
conventions_docs:
  knowledge-base: .polymath/conventions/knowledge-base.md
  review-checklist: .polymath/conventions/review-checklist.md
  artifact-matrix: .polymath/conventions/artifact-matrix.md
EOF

write "$plugin_dir/README.md" <<'EOF'
# __PLUGIN__

__ORG__'s Polymath organization pack. Installing it gives every repo a
one-command localization path:

1. `claude plugin marketplace add <this-repo-url-or-path>`
2. `claude plugin install __PLUGIN__@__ORG__`
3. In each repo: run `/polymath-core:init-project` (it detects this pack's
   `org-defaults` skill and proposes the copy-in), or run
   `/__PLUGIN__:org-defaults` directly.

## What to fill in

- `starter/.polymath/conventions/*.md` — replace `{{placeholders}}` with
  __ORG__'s reality. Anything inferred and unconfirmed keeps a
  `[VERIFY: …]` marker; consuming skills will not treat marked content as
  authoritative.
- `starter/.polymath/project.yaml` — org-wide defaults only; repo files
  always win over copied defaults.
- Add stack docs per area (`backend-stack`, `frontend-stack`, `database`,
  `auth`, `deployment`, `shared-libraries`) and register each in the
  starter's `conventions_docs` role map.

## Validation

This pack is gate-shaped for Polymath conventions: manifests are strict
(status lives in `registry/__ORG__-catalog.json`, never marketplace.json),
the skill description stays ≤200 chars, and SKILL.md bodies stay ≤500
lines. To run Polymath's own checks against this pack, clone the Polymath
marketplace and point its `tools/conformance.sh` at this tree.
EOF

write "$plugin_dir/CHANGELOG.md" <<'EOF'
# Changelog — __PLUGIN__

## [Unreleased]

### Added

- Initial org pack scaffold: org-defaults copy-in skill, starter
  `.polymath/` config, conventions corpus skeletons.
EOF

write "$target/README.md" <<'EOF'
# __ORG__ Polymath pack

Company-side marketplace carrying `__PLUGIN__`. See
`plugins/__PLUGIN__/README.md` for setup and what to fill in.
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

echo "Scaffolded org pack at $target"
echo "Next steps:"
echo "  1. Fill in plugins/$plugin/starter/.polymath/conventions/*.md (replace placeholders; keep [VERIFY: ...] on unconfirmed items)"
echo "  2. Adjust the starter project.yaml org defaults"
echo "  3. Push to the org's git host; teammates: claude plugin marketplace add <url>"
