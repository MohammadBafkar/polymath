#!/usr/bin/env python3
"""PROFILE-1: validate registry/polymath-profiles.json against the marketplace.

Install profiles (role spines) only help discovery if they never name a plugin
that does not exist. This checker asserts:

  1. Every plugin listed in any profile (and in `_spine`) is present in
     .claude-plugin/marketplace.json.
  2. No profile redundantly lists a `_spine` plugin (the spine is implicit).
  3. Each profile has a non-empty `title`, `for`, and `plugins`.

Drift-guard so a fold/rename that removes a plugin can't silently leave a
dangling profile reference. Wired into tools/conformance.sh as PROFILE-1.

Exit code: 0 if all checks pass, 1 otherwise.
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
PROFILES = REPO / "registry" / "polymath-profiles.json"


def main() -> int:
    if not PROFILES.exists():
        print("check-profiles: no registry/polymath-profiles.json (skipped)")
        return 0
    market = {p["name"] for p in json.loads(MARKETPLACE.read_text())["plugins"]}
    doc = json.loads(PROFILES.read_text())
    spine = set(doc.get("_spine", []))
    profiles = doc.get("profiles", {})

    errors: list[str] = []

    for p in spine:
        if p not in market:
            errors.append(f"_spine names unknown plugin: {p}")

    for name, prof in profiles.items():
        for field in ("title", "for", "plugins"):
            if not prof.get(field):
                errors.append(f"profile {name!r}: missing/empty `{field}`")
        for p in prof.get("plugins", []):
            if p not in market:
                errors.append(f"profile {name!r}: unknown plugin {p!r}")
            if p in spine:
                errors.append(f"profile {name!r}: redundantly lists spine plugin {p!r}")

    for e in errors:
        print(f"  FAIL  {e}")
    if errors:
        print(f"check-profiles: FAILED ({len(errors)} error(s))")
        return 1
    print(f"check-profiles: OK — {len(profiles)} profile(s), all plugins resolve against the marketplace")
    return 0


if __name__ == "__main__":
    sys.exit(main())
