"""load_yaml(): PyYAML when importable, flat fallback parser otherwise.

The fallback consolidates the shim that was duplicated across the skill,
workflow, and route triggering entrypoints (now the subcommands of
tools/triggering.py). It parses only the flat shape those tools'
frontmatter actually uses:

  - top-level ``key: value`` scalar lines (surrounding quotes stripped;
    ``true``/``false`` read as booleans, per the route variant's
    ``_scalar``)
  - ``key:`` followed by ``- item`` list lines
  - blank lines and ``#`` comments skipped

Where the three originals disagreed, the union was taken: boolean scalar
conversion and any-indent list items come from the route variant; the
top-level-keys-only guard (indented ``key: value`` lines are dropped, not
promoted to top level) comes from the skill/workflow variant because
promotion misreads nested mappings.

KNOWN LIMITATIONS — kept deliberately; consumers rely on these reading
quietly rather than raising, so do NOT "fix" them here:

  - Block scalars are NOT folded: ``key: >`` (or ``|``) reads as the
    literal one-character string ">" / "|" and the indented continuation
    lines are dropped. (PyYAML would fold them into the real string.)
  - Flow-style collections are NOT parsed: ``routing: {mode: hint}``
    reads as the literal string "{mode: hint}", not a nested mapping.
  - Nested block mappings are NOT parsed: indented ``key: value`` lines
    (other than list items) are dropped.

When PyYAML *is* importable none of the above applies — load_yaml() is
then exactly yaml.safe_load. Tests that pin the fallback behavior call
fallback_load_yaml() directly.
"""
from __future__ import annotations

from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # fallback_load_yaml takes over


def load_yaml(text: str) -> Any:
    """Parse YAML `text` — yaml.safe_load when PyYAML is importable,
    fallback_load_yaml otherwise."""
    if yaml is not None:
        return yaml.safe_load(text)
    return fallback_load_yaml(text)


def _scalar(v: str) -> Any:
    v = v.strip().strip('"').strip("'")
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    return v


def fallback_load_yaml(text: str) -> dict[str, Any]:
    """Minimal flat parser — supports the tools' frontmatter shape only.

    Always returns a dict (never a top-level list / scalar document). See
    the module docstring for the kept limitations.
    """
    result: dict[str, Any] = {}
    current_key: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- ") and current_key is not None:
            result.setdefault(current_key, []).append(_scalar(line.lstrip()[2:]))
            continue
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if val == "":
                current_key = key
                result[key] = []
            else:
                current_key = None
                result[key] = _scalar(val)
    return result
