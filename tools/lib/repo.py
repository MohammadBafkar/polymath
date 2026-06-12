"""Repo-layout discovery shared by the tools entrypoints.

Single home for the path constants (repo root, marketplace, catalog,
plugins dir) and iteration patterns (the sorted plugin-directory walk,
the SKILL.md glob) so each tool stops re-deriving them by hand.
"""
from __future__ import annotations

import json
import pathlib
from collections.abc import Iterator


def repo_root() -> pathlib.Path:
    """The repository root (tools/lib/repo.py -> parents[2])."""
    return pathlib.Path(__file__).resolve().parents[2]


def plugins_dir() -> pathlib.Path:
    """plugins/ under the repo root."""
    return repo_root() / "plugins"


def iter_plugins() -> Iterator[pathlib.Path]:
    """Yield every plugin directory under plugins/, sorted by name — the
    iteration pattern of check-readme-inventory.py and conformance.sh."""
    for p in sorted(plugins_dir().iterdir()):
        if p.is_dir():
            yield p


def iter_skills() -> Iterator[pathlib.Path]:
    """Yield every plugins/*/skills/*/SKILL.md path, sorted — the discovery
    pattern of lint-descriptions.py."""
    for plugin in iter_plugins():
        yield from sorted(plugin.glob("skills/*/SKILL.md"))


def load_marketplace() -> dict:
    """Parsed .claude-plugin/marketplace.json (the Claude-facing catalog)."""
    return json.loads((repo_root() / ".claude-plugin" / "marketplace.json").read_text())


def load_catalog() -> dict:
    """Parsed registry/polymath-catalog.json (the Polymath-side catalog)."""
    return json.loads((repo_root() / "registry" / "polymath-catalog.json").read_text())
