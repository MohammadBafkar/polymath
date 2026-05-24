# polymath-infra-docker

Docker craft for the Polymath marketplace.

## What it ships

- Skills:
  - `audit-dockerfile` — base-image discipline, multi-stage layout, USER, HEALTHCHECK, secret leakage, `.dockerignore`.
  - `audit-compose` — image pinning, named volumes, networks, secrets, `depends_on` health-conditioning, port binding, profiles.
- Commands: `/polymath-infra-docker:audit-dockerfile`, `/polymath-infra-docker:audit-compose`.

## Installation

```bash
claude plugin install polymath-infra-docker@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
