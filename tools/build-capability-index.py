#!/usr/bin/env python3
"""Generate capabilities.json `providerPlugins{}` from per-provider bindings.

Each connector / infra plugin declares the providers it supplies as bindings:

  plugins/<plugin>/bindings/<provider>/binding.json   (schema: binding.schema.json)

This builder is the SINGLE PRODUCER of the `providerPlugins{}` map inside
shared/schemas/capabilities.json. That map used to be hand-maintained and drifted
from reality — the vocabulary advertised ~30 providers while only ~10 were wired,
with no guard. Now a provider is wired iff a binding exists, so the map cannot be
aspirational. `providers[]` stays the curated vocabulary; `providerPlugins{}` is
the generated reality, and the coverage report makes the gap between them explicit.

The providing plugin is DERIVED from the binding's path, so a binding cannot claim
the wrong plugin. This is the authoring data-model only — it does NOT decide how
the MCP server is packaged at runtime (the deferred Phase 2 decision; see
docs/plans/consolidation-and-dispatch.md).

Modes:
  (default)   regenerate providerPlugins{} and write capabilities.json.
  --check     verify on-disk matches a fresh build; exit 1 on drift.
  --strict    BINDING-1: every binding's provider must be in its capability's
              providers[] vocabulary, and no (capability, provider) may be claimed
              by two plugins; exit 1 on violation.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGINS = REPO / "plugins"
CAPABILITIES = REPO / "shared" / "schemas" / "capabilities.json"
SCHEMA_PATH = REPO / "shared" / "schemas" / "binding.schema.json"


def _load_schema() -> dict | None:
    try:
        return json.loads(SCHEMA_PATH.read_text())
    except Exception:
        return None


def collect_bindings() -> tuple[list[dict], list[str]]:
    """Return (bindings, errors). Each binding: provider/capability/plugin/body/where."""
    bindings: list[dict] = []
    errors: list[str] = []
    schema = _load_schema()
    try:
        import jsonschema  # type: ignore
        validator = jsonschema.Draft202012Validator(schema) if schema else None
    except Exception:
        validator = None

    for path in sorted(PLUGINS.glob("*/bindings/*/binding.json")):
        rel = path.relative_to(PLUGINS).parts  # (plugin, 'bindings', provider, 'binding.json')
        plugin, provider_dir = rel[0], rel[2]
        where = str(path.relative_to(REPO))
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"{where}: invalid JSON ({e})")
            continue
        if validator is not None:
            for err in sorted(validator.iter_errors(body), key=lambda e: e.path):
                errors.append(f"{where}: {err.message}")
        if body.get("provider") and body["provider"] != provider_dir:
            errors.append(f"{where}: provider {body['provider']!r} != directory {provider_dir!r}")
        kind = (body.get("transport") or {}).get("kind")
        if kind not in ("mcp", "cli", "skill"):  # enforced even when jsonschema is absent
            errors.append(f"{where}: transport.kind must be one of mcp/cli/skill (got {kind!r})")
        elif kind == "mcp" and not body["transport"].get("server"):
            errors.append(f"{where}: transport.kind=mcp requires transport.server")
        bindings.append({
            "provider": body.get("provider", provider_dir),
            "capability": body.get("capability"),
            "plugin": plugin,
            "body": body,
            "where": where,
        })
    return bindings, errors


def generate(capabilities: dict, bindings: list[dict]) -> tuple[dict, list[str], list[str]]:
    """Return (new_capabilities, strict_errors, coverage_lines)."""
    caps = capabilities["capabilities"]
    strict_errors: list[str] = []
    # (capability, provider) -> plugin, with conflict detection.
    wired: dict[str, dict[str, str]] = {c: {} for c in caps}
    for b in bindings:
        cap, prov, plugin = b["capability"], b["provider"], b["plugin"]
        if cap not in caps:
            strict_errors.append(f"{b['where']}: unknown capability {cap!r}")
            continue
        vocab = caps[cap].get("providers", [])
        if prov not in vocab:
            strict_errors.append(
                f"{b['where']}: provider {prov!r} not in {cap}.providers[] "
                f"(add it to the vocabulary first)"
            )
        prior = wired[cap].get(prov)
        if prior and prior != plugin:
            strict_errors.append(
                f"({cap}, {prov}) claimed by both {prior} and {plugin}"
            )
        wired[cap][prov] = plugin

    new_caps = json.loads(json.dumps(capabilities))  # deep copy
    coverage: list[str] = []
    for cap, entry in new_caps["capabilities"].items():
        vocab = entry.get("providers", [])
        gen = wired.get(cap, {})
        # Order by vocabulary index, then any extras alphabetically.
        ordered = {p: gen[p] for p in vocab if p in gen}
        for p in sorted(k for k in gen if k not in vocab):
            ordered[p] = gen[p]
        entry["providerPlugins"] = ordered
        missing = [p for p in vocab if p not in gen]
        coverage.append(
            f"  {cap}: {len(gen)}/{len(vocab)} providers wired"
            + (f" — aspirational: {', '.join(missing)}" if missing else "")
        )
    return new_caps, strict_errors, coverage


def check_binding_consistency(bindings: list[dict]) -> list[str]:
    """A binding must agree with the plugin it lives in: an `mcp` binding's
    `server` must exist in that plugin's .mcp.json mcpServers, and every
    `userConfigKey` must exist in the plugin's userConfig. This locks the binding
    model to the actual wiring so the two cannot drift (the seam Option-A relies on).
    """
    problems: list[str] = []
    mcp_cache: dict[str, set] = {}
    uc_cache: dict[str, set] = {}
    for b in bindings:
        plugin, body, where = b["plugin"], b["body"], b["where"]
        transport = body.get("transport") or {}
        if transport.get("kind") == "mcp":
            if plugin not in mcp_cache:
                p = PLUGINS / plugin / ".mcp.json"
                try:
                    mcp_cache[plugin] = set(json.loads(p.read_text()).get("mcpServers", {})) if p.exists() else set()
                except Exception:
                    mcp_cache[plugin] = set()
            server = transport.get("server")
            if server and server not in mcp_cache[plugin]:
                problems.append(f"{where}: transport.server {server!r} has no entry in {plugin}/.mcp.json mcpServers")
        for key in body.get("userConfigKeys") or []:
            if plugin not in uc_cache:
                p = PLUGINS / plugin / ".claude-plugin" / "plugin.json"
                try:
                    uc_cache[plugin] = set((json.loads(p.read_text()).get("userConfig") or {})) if p.exists() else set()
                except Exception:
                    uc_cache[plugin] = set()
            if key not in uc_cache[plugin]:
                problems.append(f"{where}: userConfigKey {key!r} not in {plugin} plugin.json userConfig")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate capabilities.json providerPlugins from bindings")
    ap.add_argument("--check", action="store_true", help="verify on-disk matches a fresh build; exit 1 on drift")
    ap.add_argument("--strict", action="store_true", help="BINDING-1: providers must be in vocabulary; no double-claims")
    args = ap.parse_args()

    bindings, errors = collect_bindings()
    if errors:
        for e in errors:
            print(f"build-capability-index: invalid binding: {e}", file=sys.stderr)
        return 1

    capabilities = json.loads(CAPABILITIES.read_text())
    new_caps, strict_errors, coverage = generate(capabilities, bindings)
    strict_errors = strict_errors + check_binding_consistency(bindings)

    if strict_errors:
        if args.strict:
            for e in strict_errors:
                print(f"build-capability-index: BINDING-1: {e}", file=sys.stderr)
            return 1
        for e in strict_errors:
            print(f"build-capability-index: warning: {e}", file=sys.stderr)

    content = json.dumps(new_caps, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if CAPABILITIES.read_text(encoding="utf-8") != content:
            print("build-capability-index: stale (run tools/build-capability-index.py): capabilities.json", file=sys.stderr)
            return 1
        print(f"capability-index OK ({len(bindings)} bindings)")
        for line in coverage:
            print(line)
        return 0

    if args.strict:
        # Enforcement-only: BINDING-1 checks passed above; never write (so `--strict`
        # can't silently regenerate a dirty tree; `--check` is the drift guard).
        print(f"capability-index OK (strict; {len(bindings)} bindings)")
        return 0

    CAPABILITIES.write_text(content, encoding="utf-8")
    print(f"wrote capabilities.json providerPlugins from {len(bindings)} bindings")
    for line in coverage:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
