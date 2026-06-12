---
prompt: "terraform/main.tf needs the new module wired in, plan the change."
overlay: '{"rules": [{"id": "acmeInfra", "surface": "acme:infra-change", "paths": ["terraform/"], "repo_state": ["*.tf"]}]}'
evidence: '{"*.tf": true}'
must_appear:
  - "acme:infra-change"
  - "repo state"
---
Repo-state boost: the path signal alone scores 2 (below the threshold of
3); the cached `*.tf` evidence adds the +1 soft boost that lifts it over.
The hint's why-line must name "repo state" as a contributing category.
