---
name: crypto-review
description: Review a cryptography choice — encryption at rest/in transit, key management + rotation, algorithm/mode selection, and common foot-guns (IV reuse, ECB, home-rolled crypto).
---

# crypto-review

> Don't invent crypto, and don't configure it from a blog post. Use vetted primitives at safe defaults, and put the hard problem — key management — at the center, not the algorithm.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Choosing or reviewing how data is encrypted, signed, hashed, or how keys are managed.
- A design mentions encryption and you need to confirm it's not subtly broken.
- A workflow invokes `polymath-security:crypto-review`.

Not this when: you are designing auth tokens/sessions (`auth-design`) or doing a general code review (`owasp-review`). This focuses on the cryptographic choices and key lifecycle.

## Inputs

- What's being protected (data at rest, in transit, secrets, passwords), against whom, and any compliance requirement.

## Procedure

1. **Encryption in transit**: TLS 1.2+ (prefer 1.3), strong cipher suites, valid certs with rotation/automation, HSTS; mTLS for service-to-service where warranted. No plaintext internal hops "because it's internal".
2. **Encryption at rest**: use authenticated encryption (AES-GCM or ChaCha20-Poly1305); never ECB; never reuse a nonce/IV with the same key; envelope-encrypt with a KMS-managed data key.
3. **Key management — the core**: keys in a KMS/HSM, never in code/config/repo; separate keys per purpose/environment; define rotation cadence and how rotation re-wraps data; least-privilege key access; audit key use. Most "encryption" failures are key-handling failures.
4. **Hashing & passwords**: passwords with a memory-hard KDF (argon2id/scrypt/bcrypt) + per-user salt — never fast hashes (MD5/SHA-1/unsalted SHA-256). Integrity with SHA-256+/HMAC.
5. **Randomness**: cryptographically secure RNG for keys/tokens/IVs/salts — never `rand()`/`Math.random`.
6. **Signatures/certs** where authenticity matters; pin algorithms; reject downgrade.
7. **Flag the foot-guns**: home-rolled crypto, deprecated algorithms (DES/RC4/MD5/SHA-1), ECB mode, static IVs, hardcoded keys, missing rotation, secrets in logs.
8. **Crypto-agility**: version the scheme so an algorithm can be retired without a data-loss event. For data that must stay confidential for years, plan for post-quantum key exchange (hybrid TLS groups such as X25519MLKEM768 where your stack supports them) — recorded traffic can be decrypted later.

## Output

```text
Crypto review: refund-service (PCI scope: card tokens at rest)

In transit:   TLS 1.3 at the edge (1.2 minimum), HSTS; mTLS service-to-service via the mesh     OK
At rest:      AES-256-GCM, envelope-encrypted: data key per tenant, wrapped by KMS key `refunds-kek`   OK
Key mgmt:     KMS (separate keys per env + purpose); rotation 365d with re-wrap job; decrypt limited to refund-worker role; CloudTrail audit   OK
Passwords:    n/a (SSO only)
Randomness:   refund tokens from secrets.token_urlsafe(32)   OK

Findings (worst first):
  [HIGH]   src/crypto/legacy.py:14 — AES-CBC with a static IV for export files → AES-GCM with a random 96-bit nonce per file
  [MEDIUM] config/prod.yaml:31 — webhook HMAC secret committed → move to the vault; rotate it now (assume exposed)
  [LOW]    no algorithm/version byte on stored ciphertext → prefix a scheme version for crypto-agility

Agility:      ciphertext versioned after the fix; hybrid X25519MLKEM768 at the edge when the LB supports it (records kept 7 years)
```

## Quality bar

- Only vetted primitives at safe defaults; authenticated encryption for data at rest; no ECB / nonce reuse.
- Keys live in a KMS/HSM with stated rotation and least-privilege access — never in the repo.
- Passwords use a memory-hard salted KDF; CSPRNG used for all secrets/IVs.
- Deprecated algorithms and home-rolled crypto are flagged.
