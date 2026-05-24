---
name: write-pytest-test
description: Author idiomatic pytest tests — fixtures, parametrize, monkeypatch; one behavior per test.
---

# write-pytest-test

> Write pytest tests in the project's idiom. Output is test files that run green via the project's runner.

## When to use

- A Python function or behavior is uncovered.
- `polymath-qa:coverage-gap` flagged `MISSING (unit)` items in a Python project.
- A workflow invokes `polymath-lang-python:write-pytest-test`.

## Inputs

- The behavior(s) under test.
- Repo conventions: `pytest.ini` / `pyproject.toml [tool.pytest.ini_options]`, fixture conventions, plugins (`pytest-mock`, `pytest-asyncio`, `hypothesis`, `freezegun`, `respx`).

## Procedure

1. **Detect** test layout: `tests/` directory at repo root vs. `<package>/tests/`. Match the convention.
2. **Detect** async usage: if the unit under test is `async`, mark the test `@pytest.mark.asyncio` and confirm `pytest-asyncio` is configured.
3. **Detect** the assertion idiom: plain `assert` (recommended), or a `pytest.raises` for exceptions.
4. **Name** the test after the behavior: `test_rejects_sixth_login_in_window`. Not `test_login_function`.
5. **Use the standard fixtures** before reaching for `pytest-mock`:
   - `tmp_path` for filesystem.
   - `monkeypatch` for env vars and small attribute substitutions.
   - `capsys` / `capfd` for stdout/stderr.
6. **Parametrize** when the same behavior is asserted across inputs:

   ```python
   @pytest.mark.parametrize("attempts,expected", [(1, True), (5, True), (6, False)])
   def test_rate_limit_threshold(attempts, expected):
       assert allow(attempts) is expected
   ```
7. **Mock at the boundary, not inside**. Use `monkeypatch.setattr` for clock or network seams; use `respx` for HTTPX or `responses` for `requests`. Don't mock other functions in your own module.
8. **Exception path** — assert the *type* and the *message substring*:

   ```python
   with pytest.raises(RateLimitExceeded, match="6th request"):
       allow(6)
   ```

## Output

- Test files under the conventional path.
- Each test runs green via `pytest -q <path>` invoked through `polymath-engineering:verify-change`.

## Anti-patterns to avoid

- `mocker.patch("my_module.helper")` to make a test pass — that's testing the mock, not the code.
- One test asserting five behaviors with five `assert` lines (split it).
- `setUp`/`tearDown` instead of fixtures.
- `time.sleep(...)` in a test to "wait for the event loop".
