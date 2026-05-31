---
name: new-skill
description: Scaffold the SKILL.md and directories for a new skill inside an existing plugin via new-skill.sh. Not a whole plugin.
---

# /new-skill

Scaffold a new skill via `${CLAUDE_PLUGIN_ROOT}/bin/new-skill.sh <plugin> <skill>`. The vendored scaffolder walks up from the cwd to find the caller's marketplace root. Then expand the SKILL.md against the [skill style guide](../references/skill-style-guide.md) and review with `polymath-author:skill-author-critic` before committing.
