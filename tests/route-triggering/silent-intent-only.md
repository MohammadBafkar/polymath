---
prompt: "I think we should probably review our approach to caching at some point."
expect_silent: true
---
Contains the word "review" but NO hard signal (no URL, path, diff, or id key).
Intent-only must never fire — this is the core false-positive guard.
