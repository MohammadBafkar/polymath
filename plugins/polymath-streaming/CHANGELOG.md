# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0]

### Added

- Data & streaming engineering plugin (whetstone-coverage program, P3) with four
  sibling skills: `streaming-design` (topology + delivery semantics),
  `data-pipeline` (ETL/ELT, idempotent backfills, data quality), `data-modeling`
  (dimensional/lakehouse, fact grain, SCD), `stream-processing` (windowing,
  watermarks, bounded state, exactly-once). Each declares a soft-tier
  `routing.yaml`. The engineering counterpart to `polymath-data`'s analytics and
  to `polymath-architecture:event-driven-design`.
