---
name: write-rspec-test
description: Author idiomatic RSpec — describe/context/it nesting, let/subject for fixtures, shared_examples for cross-class behavior; one behavior per it.
---

# write-rspec-test

> Write RSpec specs that read top-to-bottom and fail with a meaningful message. `describe` for the unit, `context` for the situation, `it` for the behavior.

## When to use

- A Ruby method / class lacks tests.
- `polymath-qa:coverage-gap` flagged a Ruby gem or Rails app.
- A workflow invokes `polymath-lang-ruby:write-rspec-test`.

## Procedure

1. **Detect setup.** `Gemfile` for RSpec version + add-ons (`rspec-rails`, `factory_bot`, `webmock`, `vcr`). Match the prevailing style.
2. **File layout** — `app/models/refund.rb` → `spec/models/refund_spec.rb` for Rails; for a gem, `lib/foo.rb` → `spec/foo_spec.rb`.
3. **Skeleton.**
   ```ruby
   RSpec.describe RefundParser do
     subject(:parser) { described_class.new }

     describe "#parse_refund" do
       context "with empty input" do
         it "raises RefundError::Empty" do
           expect { parser.parse_refund("") }.to raise_error(RefundError::Empty)
         end
       end

       context "with valid input" do
         let(:input) { "42.00 USD" }

         it "returns a Refund with the right amount" do
           expect(parser.parse_refund(input).amount).to eq(42_00)
         end
       end
     end
   end
   ```
4. **`let` vs `let!`.** `let` is lazy (call to evaluate); `let!` evaluates before each test. Prefer `let` unless the setup must run for ordering.
5. **`subject`** — implicit subject is fine when the class has a no-arg constructor; for non-trivial setup, use `subject(:explicit_name)` and reference by name in the `it` block.
6. **`shared_examples`** for behaviors that span multiple classes (e.g. "behaves like a money serializer"). Pulls in via `it_behaves_like "money serializer"`.
7. **Mocks + stubs.** `instance_double(ClassName)` over `double()` — verifies the method signature against the actual class. `allow(double).to receive(:foo).and_return(bar)` for stubs; `expect(double).to receive(:foo)` for assertions on calls.
8. **Time.** `ActiveSupport::Testing::TimeHelpers` (Rails) or `Timecop` (gem). Never hard-code `Time.now`.
9. **Rails-specific.** `request` specs over `controller` specs (controller specs are deprecated in current RSpec-Rails). `system` specs (Capybara) for end-to-end; one feature per spec.

## Quality bar

- `it` description completes the sentence "it …".
- One assertion per `it` for clarity; multiple acceptable for inseparable invariants.
- `instance_double` over bare `double`.
- `let` over instance variables in `before` blocks.

## Anti-patterns to avoid

- `before(:all)` for mutable shared state. Per-test isolation breaks.
- `expect(x).to be_truthy` when you mean `eq(true)`. Truthy-ness is broader than truth.
- `allow_any_instance_of(Foo)`. Brittle; refactor toward dependency injection.
- A single `it` with five assertions exploring five behaviors. Split.
