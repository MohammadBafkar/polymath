"""Frontmatter parsing shared by the tools entrypoints.

parse_frontmatter() consolidates the parsers that were copy-pasted across
check-agents.py, lint-descriptions.py, check-command-overlap.py, and the
triggering entrypoints (now tools/triggering.py). It ports the most robust
combination: the fenced-block regex from the skill-triggering variant
(tightened to horizontal whitespace on the fences so trailing blank lines
stay in the body, and additionally accepting a closing fence at
end-of-file) with the PyYAML-or-shim loader (yamlshim.load_yaml),
degrading like check-agents.py — bad YAML never raises, it reads as an
empty mapping.

Contract:
  - no frontmatter (text doesn't open with a ``---`` fence)  -> ({}, text)
  - unterminated fence (no closing ``---`` line)             -> ({}, text)
  - non-mapping or unparseable frontmatter                   -> ({}, body)
  - otherwise                                                -> (mapping, body)

Without PyYAML the meta dict comes from yamlshim's flat fallback parser —
yaml-ish ``key: value`` lines and ``- `` list items only; see yamlshim for
its documented (and deliberately kept) limitations.
"""
from __future__ import annotations

import re

from .yamlshim import load_yaml

# Opening fence at byte 0, closing fence on its own line; both tolerate
# trailing spaces/tabs, and the closing fence may end the file.
FRONTMATTER_RE = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*(?:\n|$)", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split markdown `text` into (frontmatter mapping, body)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    body = text[m.end():]
    try:
        meta = load_yaml(m.group(1))
    except Exception:
        return {}, body
    if not isinstance(meta, dict):
        return {}, body
    return meta, body
