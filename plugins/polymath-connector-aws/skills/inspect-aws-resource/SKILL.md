---
name: inspect-aws-resource
description: Inspect an AWS resource by ARN — describe, surface effective permissions, recent CloudTrail events, cost ping. Read-only.
---

# inspect-aws-resource

> Stop guessing what an AWS resource looks like in prod. Given an ARN, produce: its current state, who can touch it, what changed it last, and what it costs. Read-only — never writes.

## When to use

- An incident points at a specific resource and the on-call needs the facts fast.
- A PRD says "store in s3://example-prod-uploads" and you want to know it exists, who can write, and how much it holds.
- A compliance review is happening on a single resource.

## Inputs

- ARN (required) — must be a fully-qualified ARN (`arn:aws:s3:::bucket-name`, `arn:aws:rds:us-east-1:123456789012:db:refund-primary`, etc).
- Profile + region (optional) — fall back to `userConfig.awsProfile` + `userConfig.awsRegion`.

## Procedure

1. **Parse the ARN.** Extract service + region + account + resource segment. Refuse to operate without all four (an unqualified ARN is a dangerous default).
2. **Describe via the service's describe call.** Map ARN service prefix to the right command:
   - `s3` → `aws s3api get-bucket-location` + `aws s3api get-bucket-policy` + `aws s3api get-public-access-block`.
   - `rds` → `aws rds describe-db-instances --db-instance-identifier <id>`.
   - `lambda` → `aws lambda get-function --function-name <name>`.
   - `ec2` (`instance/`) → `aws ec2 describe-instances --instance-ids <id>`.
   - `iam` → `aws iam get-role` / `get-user` / `get-policy`.
   - `dynamodb` → `aws dynamodb describe-table --table-name <name>`.
3. **Effective permissions.** For resources that carry a policy (S3 bucket, Lambda, IAM role, KMS key), run `aws iam simulate-principal-policy` against the principal of interest (current caller by default). Report the action × resource matrix.
4. **Recent CloudTrail events.** `aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=<resource> --max-results 10`. Surface event name + caller + timestamp.
5. **Cost ping.** For resource types Cost Explorer can group by (S3 bucket, RDS instance, Lambda), call `aws ce get-cost-and-usage` filtered to the resource. Skip for resources without per-resource cost attribution.
6. **Output** a one-screen summary with the resource state, principals with write access, last 5 mutating events, and 7-day cost.

## Output

```text
inspect-aws-resource

ARN:          arn:aws:s3:::example-prod-uploads
Region:       us-east-1 (bucket actual region: us-east-1)
Profile:      example-prod (account 123456789012)

State
  Created:     2024-06-12
  Versioning:  Enabled
  Encryption:  SSE-KMS (key arn:aws:kms:.../...)
  Public:      blocked (PublicAccessBlock all true)

Effective write principals (s3:PutObject)
  - arn:aws:iam::123456789012:role/UploadIngestor                ALLOW
  - arn:aws:iam::123456789012:role/AnalyticsEtl                  ALLOW
  - everyone else                                                DENY

Recent CloudTrail (last 24h)
  - 2026-05-23 14:02 PutBucketPolicy by arn:aws:iam::.../alex
  - 2026-05-23 09:14 PutObject by arn:aws:iam::.../UploadIngestor (200×)

Cost (7d)
  - storage:        $48.20
  - requests (put): $0.12
  - data transfer:  $0.00
```

## Quality bar

- ARN is fully qualified. Service + account + region all present.
- Read-only. No `put`, no `update`, no `delete` calls.
- Effective permissions reported by principal, not "policy text".
- CloudTrail events scoped to mutating actions, not list-/describe-.

## Anti-patterns to avoid

- Querying by name without an ARN. Names collide across accounts/regions.
- Reporting a bucket policy as JSON without resolving who can actually do what. Policy text is hard to read; the simulator is the contract.
- Mixing accounts. Each call must run with the profile matching the ARN's account; refuse if the active profile's account does not match.
- Trusting "PublicAccessBlock" alone for S3 visibility. Cross-check with the bucket policy + ACLs.
