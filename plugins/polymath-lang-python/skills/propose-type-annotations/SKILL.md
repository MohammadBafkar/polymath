---
name: propose-type-annotations
description: Add modern type annotations (X | None, list[X]) to changed Python; mypy/pyright-clean.
---

# propose-type-annotations

> Add type annotations to functions and methods. Use modern syntax. Stay strict enough for the project's type checker.

## When to use

- A diff adds untyped Python functions.
- The repo runs mypy or pyright and the change would regress strictness.
- A workflow invokes `polymath-lang-python:propose-type-annotations`.

## Inputs

- The Python file(s) in the diff.
- The repo's type-checker config (`mypy.ini`, `pyproject.toml [tool.mypy]`, `pyrightconfig.json`).

## Procedure

1. **Detect the Python version**. Modern syntax requires:
   - `X | Y` over `Union[X, Y]` — Python 3.10+.
   - `list[X]` / `dict[K, V]` — Python 3.9+.
   - For older targets, fall back to `Optional[X]` / `List[X]` from `typing`.
2. **Annotate inputs and return type for every public callable.** Internal helpers can use inference where the type is obvious.
3. **Prefer Protocol over Union of concrete classes.** "Anything with .read()" is a `Protocol`, not `IO[bytes] | BinaryIO`.
4. **Generics**: name the type variable (`T`) and constrain it when meaningful (`T = TypeVar("T", bound=Comparable)`).
5. **Optional vs default**: `def f(x: int | None = None)` — annotate the union explicitly, don't rely on `None` default to imply optionality.
6. **`Any` is a last resort**. If unavoidable, leave a one-line comment with why: `# noqa: ANN401  reason: third-party returns Any`.
7. **Run the type checker** scoped to the diff:

   ```bash
   mypy $(git diff --name-only HEAD~1 HEAD -- '*.py')
   # or
   pyright $(git diff --name-only HEAD~1 HEAD -- '*.py')
   ```

8. **Don't introduce new `# type: ignore`** without a justifying comment.

## Output

A patched file with annotations added, plus a summary:

```text
Annotations added: 12 functions, 4 methods.
- 3 used Protocol (file readers, JSON-like, …).
- 1 used TypeVar (generic `pluck<T>`).
- 0 new `Any` introduced; 0 new `type: ignore`.
Type-checker run on the diff: clean.
```

## Anti-patterns to avoid

- Annotating every internal local variable.
- `Any` for things you didn't bother to figure out.
- Importing `typing.List`/`typing.Dict` on Python 3.9+ (use built-in generics).
- Annotating `self` / `cls` (don't).
