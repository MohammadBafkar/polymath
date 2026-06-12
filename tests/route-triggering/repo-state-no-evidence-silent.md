---
prompt: "terraform/main.tf needs the new module wired in, plan the change."
overlay: '{"rules": [{"id": "acmeInfra", "surface": "acme:infra-change", "paths": ["terraform/"], "repo_state": ["*.tf"]}]}'
expect_silent: true
---
Counter-fixture for repo-state-boost: the identical overlay rule without
any cached evidence stays at score 2 (path only) and must not fire —
proving the boost comes from the evidence cache, not from the
repo_state declaration itself.
