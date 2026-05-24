---
plugin: polymath-lang-ruby
scenario: write-rspec
expect:
  invoked:
    - polymath-lang-ruby:write-rspec-test
  output_matches:
    - "(describe|context|it)"
    - "(let|subject)"
    - "(instance_double|raise_error|expect)"
timeout_seconds: 60
---

# Prompt

> Write RSpec specs for `RefundParser#parse_refund(input)` that
> raises `RefundError::Empty` on empty input.

Use polymath-lang-ruby:write-rspec-test.

# Acceptance

- describe / context / it nesting is correct.
- subject or let used for fixtures.
- instance_double over bare double when mocking a collaborator.
- One behavior per it block.
