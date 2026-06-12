"""Shared library for the tools/ entrypoints.

Single home for the helpers that were historically copy-pasted across the
tools: frontmatter parsing, the no-PyYAML YAML shim, token estimation,
description similarity, and repo-layout discovery. Import via either name:

    from lib import frontmatter          # sys.path includes tools/
    from tools.lib import frontmatter    # sys.path includes the repo root

Modules use intra-package relative imports so both spellings work.
Stdlib-only; PyYAML is optional (yamlshim falls back to a flat parser).
"""
