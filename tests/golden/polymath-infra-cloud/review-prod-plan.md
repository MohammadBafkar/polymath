---
plugin: polymath-infra-cloud
scenario: review-prod-plan
expect:
  invoked:
    - polymath-infra-cloud:plan-review
  output_matches:
    - "(destroy|replace|destructive)"
    - "(aws_db_instance|aws_s3_bucket|aws_iam_)"
    - "(drift|sensitive|recommendation)"
timeout_seconds: 90
---

# Prompt

> Review tfplan.json against the prod workspace. The PR claims to
> bump an RDS engine version and add two security group rules.

Use polymath-infra-cloud:plan-review.

# Acceptance

- Every destructive action explicitly named (address + risk + gate).
- An RDS replacement is flagged as destructive (state loss without snapshot).
- Drift is separated from intentional change.
- Explicit recommendation: apply-ok / apply-with-approval / needs-rework / block.
