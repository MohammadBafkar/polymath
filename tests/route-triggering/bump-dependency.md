---
prompt: "Upgrade the dependency lodash in package.json to the latest and fix any call-sites."
must_appear:
  - "polymath-flows:run-workflow bumpDependency"
---
A manifest path (package.json) plus an upgrade intent is the bumpDependency signal.
