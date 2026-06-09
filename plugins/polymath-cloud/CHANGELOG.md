# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added the `plan-review` skill — a CLI-only Terraform review skill (no MCP server) that reads a `terraform plan` and flags destructive actions, drift, and unsafe diffs before apply; it lives with the IaC design skills. Tool reference at `skills/plan-review/references/terraform-tools.md`.

### Changed

- `cloud-cost-review` skill folded in from the former `polymath-finops` plugin — cloud cost is a property of the cloud-pattern choice.

## [0.1.0]

### Added

- Cloud-design plugin with four sibling skills:
  `design-aws-pattern`, `design-gcp-pattern`, `design-azure-pattern`,
  `design-stack-composition` (Terraform). Projects pick a cloud once
  in `.polymath/project.yaml`; the skills adapt.
