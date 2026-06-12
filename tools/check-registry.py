#!/usr/bin/env python3
"""Registry cross-checks — one subcommand per conformance rule.

  check-registry.py catalog      MANIFEST-3 cross-check
  check-registry.py profiles     PROFILE-1
  check-registry.py stability    STABILITY-1
  check-registry.py aggregates   COUNT-1
  check-registry.py testdirs     TESTDIR-1
  check-registry.py docpaths     DOCPATH-1

catalog — cross-file consistency for the Polymath catalog. Verifies that
.claude-plugin/marketplace.json, every plugin's .claude-plugin/plugin.json,
and registry/polymath-catalog.json all agree on the plugin set and on
per-plugin versions. Also validates the catalog file against
registry/schemas/polymath-catalog.schema.json when jsonschema is installed.
Failure modes this catches that `claude plugin validate --strict` would miss
when the Claude CLI is not on PATH (i.e. in CI without the CLI installed):

  - Plugin listed in marketplace.json but missing from polymath-catalog.json
  - Plugin listed in polymath-catalog.json but missing from marketplace.json
  - marketplace.json entry version != plugin.json version

profiles — validate registry/polymath-profiles.json against the marketplace.
Install profiles (role spines) only help discovery if they never name a
plugin that does not exist. Asserts:

  1. Every plugin listed in any profile (and in `_spine`) is present in
     .claude-plugin/marketplace.json.
  2. No profile redundantly lists a `_spine` plugin (the spine is implicit).
  3. Each profile has a non-empty `title`, `for`, and `plugins`.

Drift-guard so a fold/rename that removes a plugin can't silently leave a
dangling profile reference.

stability — enforce registry/stability-evidence.json against the catalog.
The ledger is the receipt for every status claim in
registry/polymath-catalog.json: a status flip to `stable` on its own is just
a marketing change; the ledger is what proves the plugin has earned the
tier. Enforces:

  1. Ledger validates against
     registry/schemas/stability-evidence.schema.json (when jsonschema is
     installed).
  2. Every plugin in registry/polymath-catalog.json has exactly one ledger
     entry, and vice versa.
  3. target_status is greater-than-or-equal to current catalog status
     on the experimental → beta → stable ladder (deprecated is
     orthogonal and only allowed when current status is deprecated).
  4. Per-status evidence gates:
       - stable: live_bakeoff_run, live_trigger_run, external_user_url,
         promotion_pr, changelog_entry MUST be non-null. For
         integration and infra plugins, distinct_value_url
         MUST also be non-null. evidence_state MUST be `stable` or
         `stable-ready`.
       - beta: evidence_state MUST be `on-disk-skill`,
         `on-disk-foundation`, or `stable-ready`. For
         integration and infra plugins, distinct_value_url
         MUST be non-null (post-Iteration-0 connector/infra policy).
       - experimental: no required fields beyond presence.
       - deprecated: changelog_entry MUST be non-null.
  5. distinct_value_url MUST be null for plugins that are neither
     connector nor infra (it is a field reserved for those categories).

aggregates — COUNT-1: aggregate numbers claimed in README.md (plugin count,
workflow count) are wrapped in `<!-- count:KEY -->…N…<!-- /count -->` marker
comments and recomputed from the filesystem. A marked number that drifts from
the tree fails the build — the 36-vs-37 README drift class can't recur.
Unknown keys fail; a known key with no marker at all fails (so deleting the
markers can't silently un-gate the claim).

testdirs — TESTDIR-1: every directory under tests/skill-triggering/ and
tests/golden/ must exactly match an existing plugin directory name or be
`workflows`. Catches orphan fixture dirs left behind by renames.

docpaths — DOCPATH-1: every relative markdown link target in docs/*.md and
README.md must exist on disk (fenced code blocks are skipped; URLs, anchors,
and placeholder targets containing <>*{} are skipped; CHANGELOG files and
docs/plans/ are exempt by policy — history and plans may reference paths
that no longer or do not yet exist).

All six are wired into tools/conformance.sh --all. Exit code per
subcommand: 0 if all checks pass, 1 otherwise. The three drift gates each
take --self-test, which proves the gate can fail by running its check logic
against inline synthetic bad input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from lib.repo import load_catalog, load_marketplace, plugins_dir, repo_root

ROOT = repo_root()
PLUGINS_DIR = plugins_dir()
CATALOG_SCHEMA = ROOT / "registry" / "schemas" / "polymath-catalog.schema.json"
PROFILES = ROOT / "registry" / "polymath-profiles.json"
LEDGER = ROOT / "registry" / "stability-evidence.json"
LEDGER_SCHEMA = ROOT / "registry" / "schemas" / "stability-evidence.schema.json"


def _schema_errors(instance: dict, schema_path, label: str) -> list[str]:
    """Validate `instance` against the JSON Schema at `schema_path` when
    jsonschema is installed; otherwise note the skip on stderr."""
    try:
        import jsonschema  # type: ignore
    except ImportError:
        print("note: jsonschema not installed; skipping schema validation", file=sys.stderr)
        return []
    schema = json.loads(schema_path.read_text())
    validator = jsonschema.Draft202012Validator(schema)
    return [
        f"{label} schema: {list(err.path)}: {err.message}"
        for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    ]


# ---------------------------------------------------------------------------
# catalog — MANIFEST-3 cross-check
# ---------------------------------------------------------------------------


def catalog_check() -> int:
    errors: list[str] = []

    marketplace = load_marketplace()
    catalog = load_catalog()

    # 1. JSON Schema validation (optional — only if jsonschema is installed).
    errors.extend(_schema_errors(catalog, CATALOG_SCHEMA, "polymath-catalog.json"))

    # 2. Plugin-set agreement.
    marketplace_names = {p["name"] for p in marketplace.get("plugins", [])}
    catalog_names = set(catalog.get("plugins", {}).keys())

    only_in_marketplace = marketplace_names - catalog_names
    only_in_catalog = catalog_names - marketplace_names
    for name in sorted(only_in_marketplace):
        errors.append(f"{name}: listed in marketplace.json but missing from polymath-catalog.json")
    for name in sorted(only_in_catalog):
        errors.append(f"{name}: listed in polymath-catalog.json but missing from marketplace.json")

    # 3. Version agreement between marketplace entry and plugin.json.
    for entry in marketplace.get("plugins", []):
        name = entry["name"]
        market_version = entry.get("version")
        plugin_json = PLUGINS_DIR / name / ".claude-plugin" / "plugin.json"
        if not plugin_json.exists():
            errors.append(f"{name}: plugin.json not found at {plugin_json.relative_to(ROOT)}")
            continue
        try:
            plugin_data = json.loads(plugin_json.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"{name}: plugin.json is not valid JSON: {e}")
            continue
        plugin_version = plugin_data.get("version")
        if market_version != plugin_version:
            errors.append(
                f"{name}: version drift — marketplace.json says {market_version!r}, "
                f"plugin.json says {plugin_version!r}. At install time plugin.json wins "
                f"(calculatePluginVersion precedence). Update the marketplace entry."
            )

    if errors:
        print("check-catalog: FAILED", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1

    print(f"check-catalog: OK — {len(marketplace_names)} plugins agree across "
          f"marketplace.json, every plugin.json, and polymath-catalog.json")
    return 0


# ---------------------------------------------------------------------------
# profiles — PROFILE-1
# ---------------------------------------------------------------------------


def profiles_check() -> int:
    if not PROFILES.exists():
        print("check-profiles: no registry/polymath-profiles.json (skipped)")
        return 0
    market = {p["name"] for p in load_marketplace()["plugins"]}
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


# ---------------------------------------------------------------------------
# stability — STABILITY-1
# ---------------------------------------------------------------------------

# experimental < beta < stable; deprecated is off-ladder.
LADDER = {"experimental": 0, "beta": 1, "stable": 2}

EVIDENCE_FOR_BETA = {"on-disk-skill", "on-disk-foundation", "stable-ready", "stable"}
EVIDENCE_FOR_STABLE = {"stable-ready", "stable"}


def is_conn_or_infra(name: str) -> bool:
    # Detect by artifact, not name prefix (concept plugins dropped the
    # connector-/infra- prefix): an integration plugin ships a .mcp.json; an
    # infra plugin carries capability bindings/ but no .mcp.json. Matches the
    # detection used by INTEGRATION-1/2, MCP-PKG, and sync-integration-policy.
    d = PLUGINS_DIR / name
    return (d / ".mcp.json").exists() or (d / "bindings").is_dir()


def stability_check() -> int:
    errors: list[str] = []

    catalog = load_catalog()
    ledger = json.loads(LEDGER.read_text())

    # 1. Schema validation (optional — only if jsonschema is installed).
    errors.extend(_schema_errors(ledger, LEDGER_SCHEMA, "stability-evidence.json"))

    catalog_names = set(catalog.get("plugins", {}).keys())
    ledger_names = set(ledger.get("entries", {}).keys())

    # 2. Plugin-set agreement.
    for name in sorted(catalog_names - ledger_names):
        errors.append(f"{name}: in registry/polymath-catalog.json but missing from registry/stability-evidence.json")
    for name in sorted(ledger_names - catalog_names):
        errors.append(f"{name}: in registry/stability-evidence.json but missing from registry/polymath-catalog.json")

    # 3 + 4 + 5. Per-entry checks.
    for name in sorted(catalog_names & ledger_names):
        cur = catalog["plugins"][name].get("status")
        entry = ledger["entries"][name]
        target = entry.get("target_status")
        evidence_state = entry.get("evidence_state")
        conn_or_infra = is_conn_or_infra(name)

        # 3. Target status >= current status.
        if cur == "deprecated":
            if target != "deprecated":
                errors.append(
                    f"{name}: current status is `deprecated` but target_status is "
                    f"`{target}`. Deprecated plugins must keep target_status=deprecated."
                )
        else:
            if target == "deprecated":
                # Allowed only if we're explicitly winding the plugin down.
                # We still expect a changelog_entry in that case.
                if not entry.get("changelog_entry"):
                    errors.append(
                        f"{name}: target_status=deprecated requires a changelog_entry "
                        f"naming the replacement / removal date."
                    )
            elif target not in LADDER:
                errors.append(f"{name}: unknown target_status `{target}`")
            elif cur not in LADDER:
                errors.append(f"{name}: unknown current status `{cur}` in catalog")
            elif LADDER[target] < LADDER[cur]:
                errors.append(
                    f"{name}: target_status `{target}` is below current status `{cur}`. "
                    f"Demotion goes through a CHANGELOG entry, not the ledger."
                )

        # 4. Per-status evidence gates.
        live_bakeoff = entry.get("live_bakeoff_run")
        live_trigger = entry.get("live_trigger_run")
        adopter = entry.get("external_user_url")
        promo_pr = entry.get("promotion_pr")
        changelog = entry.get("changelog_entry")
        distinct = entry.get("distinct_value_url")

        if cur == "stable":
            for field, value in [
                ("live_bakeoff_run", live_bakeoff),
                ("live_trigger_run", live_trigger),
                ("external_user_url", adopter),
                ("promotion_pr", promo_pr),
                ("changelog_entry", changelog),
            ]:
                if not value:
                    errors.append(
                        f"{name}: catalog says `stable` but {field} is null in ledger. "
                        f"Status flip without evidence is not allowed."
                    )
            if conn_or_infra and not distinct:
                errors.append(
                    f"{name}: connector/infra plugin marked `stable` but "
                    f"distinct_value_url is null. Per docs/INTEGRATION-POLICY.md the "
                    f"stable bar requires primary-source evidence that Polymath adds "
                    f"workflow / critique / safety value beyond the official surface."
                )
            if evidence_state not in EVIDENCE_FOR_STABLE:
                errors.append(
                    f"{name}: catalog says `stable` but evidence_state is "
                    f"`{evidence_state}` (expected one of {sorted(EVIDENCE_FOR_STABLE)})."
                )
        elif cur == "beta":
            if evidence_state not in EVIDENCE_FOR_BETA:
                errors.append(
                    f"{name}: catalog says `beta` but evidence_state is "
                    f"`{evidence_state}` (expected one of {sorted(EVIDENCE_FOR_BETA)}). "
                    f"Beta requires closed on-disk evidence."
                )
            if conn_or_infra and not distinct:
                errors.append(
                    f"{name}: connector/infra plugin marked `beta` but "
                    f"distinct_value_url is null. Per docs/INTEGRATION-POLICY.md, "
                    f"promotion above experimental requires primary-source "
                    f"distinct-value evidence."
                )
        elif cur == "deprecated":
            if not changelog:
                errors.append(
                    f"{name}: catalog says `deprecated` but changelog_entry is null. "
                    f"Deprecation must be recorded in CHANGELOG."
                )

        # 5. distinct_value_url is reserved for connector/infra plugins.
        if not conn_or_infra and distinct is not None:
            errors.append(
                f"{name}: distinct_value_url is set on a non-connector / non-infra "
                f"plugin. This field is reserved for integration and infra plugins "
                f"per docs/INTEGRATION-POLICY.md."
            )

    if errors:
        print("check-stability-evidence: FAILED", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1

    n = len(catalog_names)
    print(
        f"check-stability-evidence: OK — {n} plugins have evidence ledger entries "
        f"consistent with registry/polymath-catalog.json"
    )
    return 0


# ---------------------------------------------------------------------------
# aggregates — COUNT-1
# ---------------------------------------------------------------------------

COUNT_MARKER_RE = re.compile(
    r"<!--\s*count:([a-z][a-z-]*)\s*-->(.*?)<!--\s*/count\s*-->", re.DOTALL
)
COUNTED_FILES = ("README.md",)


def _computed_counts() -> dict[str, int]:
    """The filesystem truth that README aggregate claims are checked against."""
    plugin_dirs = [
        p for p in PLUGINS_DIR.iterdir()
        if p.is_dir() and p.name.startswith("polymath-")
    ]
    workflows = list((PLUGINS_DIR / "polymath-flows" / "workflows").glob("*.yaml"))
    return {"plugins": len(plugin_dirs), "workflows": len(workflows)}


def _aggregate_errors(
    text: str, label: str, counts: dict[str, int]
) -> tuple[list[str], set[str]]:
    """Check every count-marker span in `text`. The first integer inside the
    span must equal the computed value for its key. Returns (errors, keys seen)."""
    errors: list[str] = []
    seen: set[str] = set()
    for m in COUNT_MARKER_RE.finditer(text):
        key, span = m.group(1), m.group(2)
        if key not in counts:
            errors.append(f"{label}: unknown count key `{key}` (known: {sorted(counts)})")
            continue
        seen.add(key)
        num = re.search(r"\d+", span)
        if not num:
            errors.append(f"{label}: count:{key} span carries no number: {span!r}")
        elif int(num.group()) != counts[key]:
            errors.append(
                f"{label}: count:{key} claims {num.group()} but the tree has "
                f"{counts[key]} — update the marked number"
            )
    return errors, seen


def aggregates_check() -> int:
    counts = _computed_counts()
    errors: list[str] = []

    market = len(load_marketplace().get("plugins", []))
    if market != counts["plugins"]:
        errors.append(
            f"plugins/ holds {counts['plugins']} polymath-* dirs but "
            f"marketplace.json lists {market} (the catalog gate should also be red)"
        )

    seen_all: set[str] = set()
    for rel in COUNTED_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        errs, seen = _aggregate_errors(text, rel, counts)
        errors.extend(errs)
        seen_all |= seen
    for key in sorted(set(counts) - seen_all):
        errors.append(
            f"README.md: no <!-- count:{key} --> marker found — aggregate claims "
            f"must stay marker-wrapped so this gate can see them"
        )

    for e in errors:
        print(f"  FAIL  {e}")
    if errors:
        print(f"check-aggregates: FAILED ({len(errors)} error(s))")
        return 1
    print(
        f"check-aggregates: OK — README count markers match the tree "
        f"({counts['plugins']} plugins, {counts['workflows']} workflows)"
    )
    return 0


def aggregates_self_test() -> int:
    """Prove COUNT-1 can fail: synthetic spans with a wrong number and an
    unknown key must be rejected; correct spans must pass."""
    counts = {"plugins": 37, "workflows": 26}
    bad = (
        "**<!-- count:plugins -->36<!-- /count --> plugins** and "
        "<!-- count:bogus -->7<!-- /count -->"
    )
    good = (
        "<!-- count:plugins -->37<!-- /count --> / "
        "<!-- count:workflows -->26<!-- /count -->"
    )
    errs_bad, _ = _aggregate_errors(bad, "synthetic", counts)
    errs_good, seen_good = _aggregate_errors(good, "synthetic", counts)
    checks = [
        ("wrong marked number rejected", any("claims 36" in e for e in errs_bad)),
        ("unknown count key rejected", any("unknown count key" in e for e in errs_bad)),
        ("correct markers accepted",
         not errs_good and seen_good == {"plugins", "workflows"}),
    ]
    return _self_test_verdict("aggregates", checks)


# ---------------------------------------------------------------------------
# testdirs — TESTDIR-1
# ---------------------------------------------------------------------------

TEST_DIR_BASES = ("tests/skill-triggering", "tests/golden")


def _testdir_errors(dirnames: list[str], allowed: set[str], base: str) -> list[str]:
    return [
        f"{base}/{d}/ matches no plugin directory (and is not `workflows`) — orphan test dir"
        for d in sorted(dirnames)
        if d not in allowed
    ]


def testdirs_check() -> int:
    allowed = {p.name for p in PLUGINS_DIR.iterdir() if p.is_dir()} | {"workflows"}
    errors: list[str] = []
    for base in TEST_DIR_BASES:
        root = ROOT / base
        if not root.is_dir():
            continue
        dirnames = [d.name for d in root.iterdir() if d.is_dir()]
        errors.extend(_testdir_errors(dirnames, allowed, base))

    for e in errors:
        print(f"  FAIL  {e}")
    if errors:
        print(f"check-testdirs: FAILED ({len(errors)} error(s))")
        return 1
    print("check-testdirs: OK — every fixture dir names a real plugin (or `workflows`)")
    return 0


def testdirs_self_test() -> int:
    allowed = {"polymath-core", "polymath-flows", "workflows"}
    checks = [
        ("orphan dir rejected",
         bool(_testdir_errors(["polymath-bogus"], allowed, "tests/golden"))),
        ("plugin dir accepted",
         not _testdir_errors(["polymath-core", "workflows"], allowed, "tests/golden")),
    ]
    return _self_test_verdict("testdirs", checks)


# ---------------------------------------------------------------------------
# docpaths — DOCPATH-1
# ---------------------------------------------------------------------------

DOC_LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
SKIP_TARGET_CHARS = set("<>*{}")


def _strip_fences(text: str) -> str:
    """Drop fenced code blocks and simple inline code spans — example links
    inside code are syntax documentation, not claims. Inline stripping covers
    single-backtick spans without inner backticks; pathological nesting should
    be rewritten in the doc rather than special-cased here."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(re.sub(r"`[^`\n]+`", " ", line))
    return "\n".join(out)


def _docpath_errors(text: str, base_dir, label: str) -> list[str]:
    errors: list[str] = []
    for m in DOC_LINK_RE.finditer(_strip_fences(text)):
        target = m.group(1)
        if not target or target.startswith("#"):
            continue
        if "://" in target or target.startswith("mailto:"):
            continue
        if any(c in target for c in SKIP_TARGET_CHARS):
            continue
        path = target.split("#", 1)[0]
        if not path:
            continue
        if not (base_dir / path).exists():
            errors.append(f"{label}: dead link target `{target}`")
    return errors


def docpaths_check() -> int:
    errors: list[str] = []
    files = sorted(ROOT.glob("docs/*.md")) + [ROOT / "README.md"]
    for f in files:
        if f.name.startswith("CHANGELOG"):
            continue
        errors.extend(
            _docpath_errors(f.read_text(encoding="utf-8"), f.parent,
                            str(f.relative_to(ROOT)))
        )

    for e in errors:
        print(f"  FAIL  {e}")
    if errors:
        print(f"check-docpaths: FAILED ({len(errors)} error(s))")
        return 1
    print(f"check-docpaths: OK — every relative link in {len(files)} doc file(s) resolves")
    return 0


def docpaths_self_test() -> int:
    base = ROOT / "docs"
    checks = [
        ("dead relative link rejected",
         bool(_docpath_errors("see [x](does-not-exist-xyz.md)", base, "synthetic"))),
        ("live relative link accepted",
         not _docpath_errors("see [m](MATURITY.md)", base, "synthetic")),
        ("URL / anchor / placeholder skipped",
         not _docpath_errors(
             "[a](https://example.com) [b](#anchor) [c](docs/prds/<slug>.md)",
             base, "synthetic")),
        ("fenced example links skipped",
         not _docpath_errors("```\n[x](nope-xyz.md)\n```", base, "synthetic")),
    ]
    return _self_test_verdict("docpaths", checks)


# ---------------------------------------------------------------------------
# gates — GATES-1
# ---------------------------------------------------------------------------

GATES_REGISTRY = ROOT / "registry" / "gates.json"
CONFORMANCE = ROOT / "tools" / "conformance.sh"
# Numbered IDs (FOO-1, FOO-BAR-2) plus the established non-numbered gate names.
GATE_ID_RE = re.compile(r"\b[A-Z][A-Z]+(?:-[A-Z0-9]+)*-[0-9]+\b")
GATE_ID_LITERALS = {
    "MCP-PKG", "ROUTE-TRIGGER", "WORKFLOW-TRIGGER",
    "WORKFLOW-INDEX", "SURFACE-INDEX", "CAPABILITY-INDEX",
}


def _script_gate_ids(text: str) -> set[str]:
    ids = set(GATE_ID_RE.findall(text))
    ids |= {lit for lit in GATE_ID_LITERALS if lit in text}
    return ids


def _gates_diff(script_ids: set[str], registry_ids: set[str]) -> list[str]:
    errors: list[str] = []
    for gid in sorted(script_ids - registry_ids):
        errors.append(
            f"gate `{gid}` appears in tools/conformance.sh but has no "
            f"registry/gates.json entry — register it (with a --self-test "
            f"for new gates)"
        )
    for gid in sorted(registry_ids - script_ids):
        errors.append(
            f"gate `{gid}` is registered in registry/gates.json but appears "
            f"nowhere in tools/conformance.sh — stale entry or unwired gate"
        )
    return errors


def gates_check() -> int:
    import shlex
    import subprocess

    errors: list[str] = []
    doc = json.loads(GATES_REGISTRY.read_text(encoding="utf-8"))
    if doc.get("schemaVersion") != 1:
        errors.append(f"registry/gates.json: unsupported schemaVersion {doc.get('schemaVersion')!r}")
    entries = doc.get("gates", [])
    ids = [g.get("id") for g in entries]
    for gid, n in {i: ids.count(i) for i in ids}.items():
        if n > 1:
            errors.append(f"registry/gates.json: duplicate gate id `{gid}`")
    for g in entries:
        for field in ("id", "tool", "invocation", "tier", "verification", "description"):
            if not g.get(field):
                errors.append(f"registry/gates.json: `{g.get('id', '?')}` missing `{field}`")
        if g.get("verification") == "selftest" and not g.get("selftest"):
            errors.append(
                f"registry/gates.json: `{g.get('id')}` claims verification=selftest "
                f"but registers no selftest invocation"
            )

    errors.extend(_gates_diff(_script_gate_ids(CONFORMANCE.read_text(encoding="utf-8")), set(ids)))

    ran = 0
    for g in entries:
        if g.get("verification") != "selftest" or not g.get("selftest"):
            continue
        if g.get("id") == "GATES-1":
            continue  # don't recurse into our own self-test
        proc = subprocess.run(
            shlex.split(g["selftest"]), cwd=ROOT,
            capture_output=True, text=True,
        )
        ran += 1
        if proc.returncode != 0:
            errors.append(
                f"`{g['id']}` self-test failed (exit {proc.returncode}): "
                f"{(proc.stderr or proc.stdout).strip().splitlines()[-1] if (proc.stderr or proc.stdout).strip() else 'no output'}"
            )

    for e in errors:
        print(f"  FAIL  {e}")
    if errors:
        print(f"check-gates: FAILED ({len(errors)} error(s))")
        return 1
    print(
        f"check-gates: OK — {len(entries)} gates registered, bijective with "
        f"conformance.sh; {ran} self-test(s) executed and passing"
    )
    return 0


def gates_self_test() -> int:
    script = "echo MANIFEST-1; echo MCP-PKG; echo NEWGATE-7"
    registry_ok = {"MANIFEST-1", "MCP-PKG", "NEWGATE-7"}
    registry_missing = {"MANIFEST-1", "MCP-PKG"}
    registry_stale = registry_ok | {"GHOST-9"}
    ids = _script_gate_ids(script)
    checks = [
        ("script IDs extracted", ids == {"MANIFEST-1", "MCP-PKG", "NEWGATE-7"}),
        ("unregistered script gate rejected",
         any("no registry/gates.json entry" in e for e in _gates_diff(ids, registry_missing))),
        ("stale registry entry rejected",
         any("appears nowhere" in e for e in _gates_diff(ids, registry_stale))),
        ("bijective sets accepted", not _gates_diff(ids, registry_ok)),
    ]
    return _self_test_verdict("gates", checks)


def _self_test_verdict(name: str, checks: list[tuple[str, bool]]) -> int:
    failures = 0
    for label, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
        failures += 0 if ok else 1
    if failures:
        print(f"check-registry {name} --self-test FAILED ({failures} check(s))",
              file=sys.stderr)
        return 1
    print(f"check-registry {name} --self-test: gate logic correctly rejects synthetic bad input")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Registry cross-checks — one subcommand per conformance rule."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser(
        "catalog",
        help="marketplace.json / plugin.json / polymath-catalog.json agreement (MANIFEST-3)",
    )
    sub.add_parser(
        "profiles",
        help="polymath-profiles.json plugins resolve against the marketplace (PROFILE-1)",
    )
    sub.add_parser(
        "stability",
        help="stability-evidence.json backs every catalog status claim (STABILITY-1)",
    )
    for name, help_text in (
        ("aggregates", "README aggregate counts match the tree (COUNT-1)"),
        ("testdirs", "fixture dirs name real plugins (TESTDIR-1)"),
        ("docpaths", "relative doc links resolve (DOCPATH-1)"),
        ("gates", "gates.json bijective with conformance.sh; selftests run (GATES-1)"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument(
            "--self-test", action="store_true",
            help="prove the gate can fail: run its check logic against "
                 "inline synthetic bad input",
        )

    args = parser.parse_args()
    self_test = getattr(args, "self_test", False)
    if args.cmd == "catalog":
        return catalog_check()
    if args.cmd == "profiles":
        return profiles_check()
    if args.cmd == "stability":
        return stability_check()
    if args.cmd == "aggregates":
        return aggregates_self_test() if self_test else aggregates_check()
    if args.cmd == "testdirs":
        return testdirs_self_test() if self_test else testdirs_check()
    if args.cmd == "docpaths":
        return docpaths_self_test() if self_test else docpaths_check()
    if args.cmd == "gates":
        return gates_self_test() if self_test else gates_check()
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
