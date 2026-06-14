# Changelog — polymath-core

<!-- markdownlint-disable MD024 -->

## [0.8.0]

Foundation: route prompts, load conventions/project context, report plugin budgets, and run SessionStart hooks.

### Skills

- **conventions** — Read Polymath project conventions (commit style, PR shape, plugin layout) when starting a task that touches the marketplace.
- **doctor** — Check the Polymath environment — required and optional tools, and validate any .polymath/project.yaml — reporting PASS/WARN/FAIL and fix hints.
- **glossary** — Define shared vocabulary for Polymath plugins (PRD, ADR, RFC, mustPass, flows-lite); use when terms need disambiguating.
- **initialize-project** — Map a repository to .polymath/project.yaml — capability mapping and onboarding notes for Polymath-aware agents.
- **project-context** — Read .polymath/project.yaml — language, framework, conventions, external skills, skill overrides — so a skill can adapt to this project instead of giving generic guidance.
- **route** — Choose the right Polymath workflow, skill, connector, agent, or external catalog for a user prompt; returns JSON with confidence, evidence, and alternatives.

### Commands

- **/doctor** — Run the doctor preflight on your Polymath environment before first init or when it misbehaves; alias for polymath-core:doctor.
- **/init-project** — Run the initialize-project skill from the CLI to bootstrap a repo's Polymath setup in one command.
- **/plugin-budget** — List current Polymath always-on listing-token cost per plugin and totals; flags overruns vs the ≤400/plugin and ≤1,500 MVP targets.
- **/route** — Run a Router Report before work starts; command entry point for the selector, not the canonical routing procedure.
