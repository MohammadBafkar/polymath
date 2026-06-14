# polymath-engineering

Engineering craft for the Polymath marketplace. TDD feature-dev, code review, change verification, codebase orientation.

## What it ships

- Skills: `feature-dev`, `code-review`, `verify-change`, `read-code`, `tech-debt-management`.

`tech-debt-management` runs the debt *portfolio* — inventory, quantify interest vs principal, prioritize paydown against the roadmap — distinct from the `refactorWithSafety` workflow that executes one safe refactor.
- Hooks:
  - `PreToolUse(Write|Edit)` — secret-scan: blocks Write/Edit content containing common credential patterns (writes via Bash/MultiEdit/NotebookEdit are not scanned; the gitleaks CI gate is the catch-all).
  - `PostToolUse(Write|Edit)` — format-if-config: runs the project formatter only when a matching config exists.

## Installation

```bash
claude plugin install polymath-engineering@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
