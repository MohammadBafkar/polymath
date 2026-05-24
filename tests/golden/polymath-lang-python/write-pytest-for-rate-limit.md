---
plugin: polymath-lang-python
scenario: write-pytest-for-rate-limit
expect:
  invoked:
    - polymath-lang-python:write-pytest-test
  output_matches:
    - "def test_"
    - "pytest.raises"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 120
---

# Prompt

> Write a pytest test for this rate limiter.

```python
# api/rate_limit.py
class RateLimitExceeded(Exception): ...

class RateLimiter:
    def __init__(self, max_per_window: int = 5, window_seconds: int = 60) -> None:
        self.max_per_window = max_per_window
        self.window_seconds = window_seconds
        self._buckets: dict[str, list[float]] = {}

    def allow(self, key: str, now: float) -> bool:
        bucket = [t for t in self._buckets.get(key, []) if now - t < self.window_seconds]
        if len(bucket) >= self.max_per_window:
            self._buckets[key] = bucket
            return False
        bucket.append(now)
        self._buckets[key] = bucket
        return True
```

Use polymath-lang-python:write-pytest-test. Cover: the happy path,
the threshold (6th request in the window), and that requests
outside the window are allowed again.

# Acceptance

- At least 3 distinct `def test_*` functions or one `@pytest.mark.parametrize`
  that covers the three behaviors.
- Test names describe behavior, not implementation.
- No `time.sleep` to wait for the window — the clock is injected via `now`.
- No mocking of internal collaborators.
