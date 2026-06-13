# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0]

### Added

- Infrastructure-as-Code authoring plugin (whetstone-coverage program, P4) with three
  sibling skills: `terraform-module` (reusable module interface design),
  `terraform-state` (backend/locking/isolation/drift/state-surgery), and
  `policy-as-code` (OPA/Sentinel/Checkov guardrails enforced pre-apply). Each declares
  a soft-tier `routing.yaml`. Plan/diff review intentionally stays in
  `polymath-cloud:plan-review` (no duplication).
