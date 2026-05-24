# polymath-engineering

Engineering craft for the Polymath marketplace. TDD feature-dev, code review, change verification, codebase orientation.

## What it ships

- Skills: `feature-dev`, `code-review`, `verify-change`, `read-code`.
- Hooks:
  - `PreToolUse(Write|Edit)` — secret-scan: blocks edits containing common credential patterns.
  - `PostToolUse(Write|Edit)` — format-if-config: runs the project formatter only when a matching config exists.

## Installation

```bash
claude plugin install polymath-engineering@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
