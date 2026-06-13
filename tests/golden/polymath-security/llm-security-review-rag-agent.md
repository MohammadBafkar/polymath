---
plugin: polymath-security
scenario: llm-security-review-rag-agent
expect:
  invoked:
    - polymath-security:llm-security-review
  output_matches:
    - "(indirect|prompt injection)"
    - "(insecure output|output handling|XSS|SSRF)"
    - "(excessive agency|propose|authorize|confirm)"
  not_invoked:
    - polymath-security:owasp-review
timeout_seconds: 120
---

# Prompt

> Do a security review of our support assistant: it answers from a RAG
> index of customer docs and can call a refund tool. Untrusted ticket
> text and retrieved docs both go into the prompt, and its answer is
> rendered as HTML in the agent console.

Use polymath-security:llm-security-review.

# Acceptance

- Indirect prompt injection via retrieved docs / ticket text is assessed, not just direct injection.
- Insecure output handling flagged: HTML rendering of model output → XSS risk.
- Excessive agency flagged: the refund tool must not be authorized by model output alone (propose-vs-authorize).
- Findings map to OWASP-LLM categories with severity + mitigation + owner.
