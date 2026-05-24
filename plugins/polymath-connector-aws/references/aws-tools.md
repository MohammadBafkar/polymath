# AWS CLI reference

This connector wraps the local `aws` CLI; no remote MCP. Authentication is the user's existing AWS profile (config + credentials in `~/.aws/`). Polymath never reads or stores AWS credentials directly.

## Profile model

- Per-account profile preferred (`prod-payments`, `staging-payments`).
- Avoid the `default` profile for non-trivial work.
- Use SSO profiles (`aws sso login --profile prod-payments`) where the org supports it.

## Read-side commands used

- `aws s3api get-bucket-location / get-bucket-policy / get-public-access-block`
- `aws rds describe-db-instances / describe-db-clusters`
- `aws lambda get-function / list-versions-by-function`
- `aws ec2 describe-instances / describe-security-groups`
- `aws iam get-role / get-policy / simulate-principal-policy / simulate-custom-policy`
- `aws dynamodb describe-table`
- `aws cloudtrail lookup-events`
- `aws ce get-cost-and-usage`

## What this connector does NOT do

- It does not run mutating commands (`put-*`, `update-*`, `delete-*`, `create-*`). Mutation is delegated to `polymath-infra-aws` (write-side IaC) or to an operator running the command directly.
- It does not issue temporary credentials. Profile + SSO is the model.
- It does not cross accounts. Each inspection runs against one profile; cross-account analysis is multiple invocations.

## Common pitfalls

- ARNs without a region (`arn:aws:s3:::bucket-name`) mask the bucket's actual region; resolve via `get-bucket-location` before continuing.
- IAM policy *text* is not the same as effective permissions. SCPs, permission boundaries, and resource-based policies all intervene. Use `simulate-principal-policy` for the real answer.
- CloudTrail is eventually consistent (~15 min lag) and excludes data-plane events on most services. Surface this caveat.
- `aws ce` (Cost Explorer) has a $0.01/request cost and a 24h latency. Cache short-term.
