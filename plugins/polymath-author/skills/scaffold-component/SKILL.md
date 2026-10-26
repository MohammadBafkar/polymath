---
name: scaffold-component
description: Generate a component/service/module in the CURRENT repo per its conventions — native generator first, infra files from their owning skills, no freehand boilerplate.
---

# scaffold-component

> A new component should look like the team wrote it: the project's
> conventions decide the shape, the stack's own generator produces the
> boilerplate, and infra files come from the skills that own those
> formats. The model's job is composition, not invention.

## When to use

- "Add a new service/module/package/handler like the existing ones."
- A repo with `.polymath/` localization needs a new component that must
  match house conventions.

Not for authoring Polymath plugins/skills (`new-plugin`, `new-skill`,
`new-pack`) — this scaffolds in the *user's* project.

## Inputs

- Component name and kind (service, library, handler, …) — required; ask if absent.
- Where it lives, if the repo has more than one plausible location.

## Procedure

1. **Load the conventions (convention-driven, not vibes).** Read the
   project context (`polymath-core:project-context`): `stack`, then the
   `conventions_docs` roles that govern shape — `knowledge-base`,
   `backend-stack`/`frontend-stack`, `shared-libraries`, `deployment`.
   Mirror an existing sibling component's layout when one exists; name
   per the conventions (treat `[VERIFY: …]` content as unconfirmed).
   No `.polymath/`? Say so and mirror the closest sibling instead.
2. **Tool-spec handoff first.** If the stack has a native generator
   (`dotnet new`, `npm create` / `yarn create`, `cargo new`,
   `django-admin startapp`, `mvn archetype:generate`, a repo-local
   generator named in the conventions docs, …), compose the exact
   command + flags — the spec — and show it with the paths it will
   write. **Run it only after the user confirms**: generators write many
   files and many download packages. Use a dry-run flag first when the
   tool has one. Hand-write only what no tool generates; never
   reimplement a generator's output by hand.
3. **Canonical infra bodies.** For infra files the generator doesn't
   produce, delegate to the skill that owns the format instead of
   freehanding: Dockerfile → `polymath-devops:dockerize`, CI workflow →
   `polymath-devops:ci-pipeline-github`, K8s manifests →
   `polymath-kubernetes:write-manifest` — each already consumes the
   project's `deployment` conventions.
4. **Wire the test scaffold** per `stack.testing` (framework, layout
   mirroring siblings) with one real starter test that runs green through
   the repo's test command — not an empty file.
5. **Create, never overwrite; register additively.** New files must not
   already exist — if a target path exists, stop and show the conflict.
   Registration (solution file, workspace globs, the knowledge-base
   component table) edits existing files: make those edits additive only
   and show each one as a diff.
6. **Close the loop.** If the component adds tools or env vars, update
   `setup` in `.polymath/project.yaml` and regenerate the onboarding
   checklist: `python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/bin/gen-prerequisites.py"
   --out docs/onboarding/prerequisites.md`. Run the repo's build/test once
   to prove the component compiles and its starter test passes.

## Output

```text
scaffold-component: <name> (<kind>)

Generator:   <exact command run>   (confirmed by user; dry-run first: yes/no)
Created:     <path>, <path>, …
Registered:  <file> (+<n> lines, additive)
Infra from:  polymath-devops:dockerize, polymath-devops:ci-pipeline-github
Conventions: <roles applied>; [VERIFY] items honored: <n>
Verified:    <build/test command> → <pass/fail>
Follow-ups:  <open items>
```

## Quality bar

- An existing teammate couldn't tell this component from a hand-built
  one — naming, layout, and registration all match the conventions.
- Boilerplate came from the native generator; infra bodies from their
  owning skills; nothing freehanded that had a canonical source.
- No generator ran without confirmation; nothing overwritten; every
  created path listed in the summary.
- The build/test run after scaffolding is reported, pass or fail.
