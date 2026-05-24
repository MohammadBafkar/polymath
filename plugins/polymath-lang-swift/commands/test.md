---
description: Author or extend a Swift test (XCTest or Swift Testing) for the behavior(s) you describe.
---

Invoke `polymath-lang-swift:write-xctest`.

Inputs to gather from context:
- The type / function under test (file + signature).
- Which framework the testTarget uses (XCTest vs Testing).
- async patterns in use (concurrency / Combine).

After writing, run `swift test` and surface any failures.
