---
name: owasp-review
description: Review a code diff against the current OWASP Top 10; report findings keyed to file:line with severity (high/medium/low) and a fix recommendation.
---

# owasp-review

> Pair with `polymath-engineering:code-review` on the security axis. Output is findings, not a tutorial.

## When to use

- A workflow's `reviewPR` invokes this as a fanout sibling.
- The diff touches AuthN/AuthZ, input parsing, file I/O, network calls, or DB queries.
- The user says "security review this".

## Inputs

- The diff (current `git diff` or PR diff).
- The PRD if available (gives intended trust boundary).

## OWASP Top 10 lens

Walk the diff under each category of the **OWASP Top 10:2025** (released November 2025). Cite the edition in the output; if a team still reports against 2021, map the categories (2021's SSRF now sits under A01, Vulnerable Components under A03).

| # | Category | Diff signals to look for |
| - | -------- | ------------------------ |
| A01 | Broken Access Control (incl. SSRF) | Missing AuthZ check on new endpoint; permission checked client-side; IDOR (user-supplied IDs unfiltered); outbound HTTP to a user-supplied URL/host without an allow-list or DNS-rebinding defense. |
| A02 | Security Misconfiguration | Permissive CORS; debug endpoints in prod; default credentials; verbose error pages; overly broad cloud/IAM settings in the diff. |
| A03 | Software Supply Chain Failures | New dependency pinned to a known-vulnerable version; floating versions; transitive bumps without justification; CI fetching unpinned/unsigned tools or actions. |
| A04 | Cryptographic Failures | Hardcoded secrets; rolling-your-own crypto; predictable IVs; weak hashes for passwords. |
| A05 | Injection | String-concatenated SQL / shell / LDAP / XPath; HTML built without escaping (XSS); template injection; unsanitized input reaching an LLM prompt that drives actions. |
| A06 | Insecure Design | Missing rate limit on auth or expensive endpoints; trust-on-first-use; business-logic abuse paths. |
| A07 | Authentication Failures | Predictable session tokens; missing MFA path; brute-forceable credential flow; session not rotated on login. |
| A08 | Software or Data Integrity Failures | Untrusted deserialization; missing signature on update artifacts; unverified data used for security decisions. |
| A09 | Security Logging and Alerting Failures | Sensitive data logged; AuthN failures not logged; no audit trail or alert for AuthZ-relevant changes. |
| A10 | Mishandling of Exceptional Conditions | Fail-open error handling (an exception skips the auth check); swallowed errors; unchecked return values; stack traces or internals returned to the client. |

## Procedure

1. Read the diff, plus the code it calls into where a trust boundary is crossed.
2. For each category above, scan for the listed signals.
3. **Trace before you report**: follow each candidate from an attacker-controlled source to the dangerous sink. A pattern match without a reachable path is a question for the author, not a finding.
4. For every confirmed hit:
   - Cite file:line.
   - Classify severity: **high** (exploitable now), **medium** (requires another precondition), **low** (defense-in-depth nit).
   - Propose a concrete fix.

## Output

```text
OWASP review (Top 10:2025):

A05 Injection (high)
  - api/search.py:42 — query built via f-string with user input.
    Fix: use parameterized SQL.

A01 Broken Access Control (medium)
  - api/refund.py:18 — /refund/<order_id> reads any order; no
    ownership check.
    Fix: verify order.user_id == request.user_id before reading.

(No findings: A02, A03, A04, A06, A07, A08, A09, A10.)
```

## Quality bar

- No finding without a file:line citation.
- No category without a verdict — either a finding or an explicit "no findings" line.
- "Fix" is concrete, not a link to the OWASP wiki.
