---
description: Author or extend a JUnit 5 test for the behavior(s) you describe.
---

Invoke `polymath-lang-java:write-junit5-test`.

Inputs to gather from context:
- The class / method under test (file path + signature).
- Build tool (Maven vs Gradle) and assertion library (AssertJ vs Hamcrest).
- Mockito vs hand-rolled fakes.

After writing the test:
- Run the test (`mvn test` or `./gradlew test`) and surface any failures.
- If a parameterized space is large, verify with `--info` that all cases ran.
