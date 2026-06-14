# Security

## Reporting a vulnerability

Report suspected vulnerabilities privately via GitHub's **"Report a
vulnerability"** flow (repository → Security → Advisories → Report a
vulnerability). Please do not open a public issue for a security report.
Include a minimal reproduction and the affected file/commit.

## The flows-lite shell trust boundary

`plugins/polymath-flows/bin/polymath-flow` runs a shell for two kinds of
check, both of which can reference content that travels with a checkout:

- **`appStarts`** boot-verification executes the `smoke.<lang>.start`
  command read from `.polymath/project.yaml`.
- **`command` / `commandSucceeds`** mustPass and guard checks run a
  workflow-authored command.

Because cloning an untrusted repository and running a workflow could
otherwise execute attacker-authored shell with no confirmation, the runner
enforces a trust boundary:

- **Marketplace workflows are trusted.** A workflow that ships from the
  installed plugin tree is reviewed content; its `command` checks run.
- **Project/user-layer workflows and the project smoke recipe are not.**
  They run a shell only when the repo opts in with a `.polymath/trust`
  marker file (or the `POLYMATH_ALLOW_SHELL=1` environment variable).
  Without the opt-in, `appStarts` is skipped (reported as not-applicable)
  and project/user-layer `command` checks are refused.
- **Substituted values are never trusted.** A `${inputs.*}`,
  `${project.*}`, or `${capabilities.*}` value that contains a shell
  metacharacter is refused rather than interpolated into a shell command,
  so a crafted `--input` or project value cannot inject syntax even inside
  a trusted workflow's command.

To enable boot-verification or local-workflow shell checks in a repo you
trust:

```bash
# opt this repo in (one-time)
mkdir -p .polymath && touch .polymath/trust
# or, per-invocation:
POLYMATH_ALLOW_SHELL=1 polymath-flow start <workflow>
```

## Other deterministic guardrails

- A pinned **gitleaks** gate (`SECRET-1`) scans every PR for committed
  credentials.
- A `PreToolUse` **secret-scan** hook blocks `Write`/`Edit` payloads
  containing common credential patterns (a backstop, not a permission
  slip; see `docs/CONTRIBUTING.md`).
