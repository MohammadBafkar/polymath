---
name: propose-nullable-references
description: Roll out nullable reference types file-by-file; annotate signatures, fix warnings, avoid `!`.
---

# propose-nullable-references

> Enable nullable reference types in C# and resolve the warnings incrementally.

## When to use

- A project sets `<Nullable>disable</Nullable>` or omits it and you want to turn it on.
- A single file already has `#nullable enable` at the top and needs annotations.
- A workflow invokes `polymath-lang-dotnet:propose-nullable-references`.

## Inputs

- Project file (`.csproj`).
- The set of files to annotate (default: all `.cs` in the project, or just the diff).

## Procedure

1. **Choose the rollout shape**:
   - **Per-project**: `<Nullable>enable</Nullable>` in `.csproj`. Fix every warning across the project.
   - **Per-file**: `#nullable enable` at the top of one file. Keeps the surface small.
   - **Annotations-only**: `<Nullable>annotations</Nullable>` — public API signatures are annotated, but no warnings emitted yet. Good intermediate state for a library.
2. **Annotate** every public signature first:
   - Reference types that can be null → `string?`, `User?`.
   - Reference types that the contract says never null → `string`, `User`.
   - Generic constraints: `where T : notnull` when the type parameter is non-null.
3. **Fix warnings in this order**:
   - Constructor: ensure non-nullable fields are initialized.
   - Properties: use `required` (C# 11+) or initialize in constructor; otherwise mark `string?`.
   - Methods: `[return: NotNullIfNotNull(nameof(x))]`, `[NotNullWhen(true)]` for try-patterns.
4. **`!` is a last resort**. Use it only when:
   - An external API genuinely returns non-null but isn't annotated.
   - A control-flow narrowing the compiler can't see is verified by another mechanism.
   In both cases, leave a one-line comment with the reason.
5. **Don't fight the compiler**. A warning often means the type model and the runtime invariants disagree. Fixing the type model is usually the right move.

## Output

A patched project (or files) plus a summary:

```text
Nullable rollout for src/Refunds:
  - Mode: <Nullable>enable</Nullable> at project level.
  - 47 warnings before, 0 after.
  - 4 `!` operators introduced; each has a comment.
  - 3 fields converted to `required`.
  - 2 method signatures gained [NotNullWhen]/[NotNullIfNotNull].
```

## Anti-patterns to avoid

- `!` everywhere to silence warnings without thinking.
- Enabling Nullable in a giant PR with no plan.
- Marking everything `?` "just in case" — that defeats the point.
