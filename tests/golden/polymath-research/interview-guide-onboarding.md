---
plugin: polymath-research
scenario: interview-guide-onboarding
expect:
  invoked:
    - polymath-research:interview-guide
  artifacts:
    - "docs/research/why-do-new-teams-bounce-in-week-1-guide.md"
  output_matches:
    - "(last time|specific)"
    - "(Avoid|hypothetical)"
    - "(Recruit|target)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 120
---

# Prompt

> Write an interview guide for our onboarding research.

Use polymath-research:interview-guide. Research question: "Why do new teams
bounce in their first week?" Audience: engineering managers at 20–100-person
startups who signed up in the last 90 days.

# Acceptance

- docs/research/<slug>-guide.md exists with InterviewGuide frontmatter.
- Every question references the past or asks for specifics. Zero hypotheticals.
- Recruit section includes 2–3 screener questions.
- Target N ≥ 5.
- "Avoid" list is present (no "would you", no rating scales, no pitch).
