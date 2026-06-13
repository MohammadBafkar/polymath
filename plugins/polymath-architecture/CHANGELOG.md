# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0]

### Added

- Software-architecture design plugin with eight sibling technique skills:
  `bounded-context-map`, `aggregate-design`, `event-driven-design`,
  `resilience-design`, `service-decomposition`, `distributed-consistency`,
  `integration-design`, `design-patterns-apply`. Each emits a one-page design
  artifact that surfaces the trade-offs. The techniques compose into the
  `designSystem` workflow; documents stay in `polymath-writing`, trade-off
  scoring in `polymath-decisions`, caching in `polymath-performance`.
