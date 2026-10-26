---
name: auth-design
description: Design authentication/authorization — OAuth2/OIDC flow choice, JWT vs opaque/session tokens, RBAC vs ABAC, SSO, token lifetime/refresh/revocation.
---

# auth-design

> Authentication proves who; authorization decides what. Conflating them, or hand-rolling either, is where breaches live. Pick standard flows and name where the token can be revoked.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Designing login, API auth, service-to-service auth, or an authorization model.
- Choosing between session cookies and tokens, or between RBAC and ABAC.
- A workflow invokes `polymath-security:auth-design`.

Not this when: you are threat-modeling a whole system (`stride-threat-model`) or reviewing a diff for vulns (`owasp-review`). This skill designs the authN/authZ mechanism itself.

## Inputs

- Who authenticates (users, services, third parties), the clients (web/mobile/SPA/server), and the resources to protect.
- Compliance/SSO constraints.

## Procedure

1. **Separate authN from authZ.** Decide each independently; document both.
2. **Pick the OAuth2/OIDC flow** by client type: Authorization Code + PKCE for web/SPA/mobile (never implicit), Client Credentials for service-to-service, Device Code for input-constrained. Use OIDC when you need identity (id_token), OAuth2 alone for delegated access. Don't invent a flow.
3. **Token strategy**: session cookie (server-side state, easy revocation) vs JWT (stateless, scales, but hard to revoke). If JWT: short access-token TTL + refresh token, `aud`/`iss`/`exp` validated, signature alg pinned (no `alg:none`), and a revocation story (short TTL + denylist or rotation). Rotate refresh tokens on every use and revoke the family on reuse (theft detection); for high-value APIs, sender-constrain tokens (DPoP or mTLS) so a stolen bearer token is useless. Never store tokens in `localStorage` in a browser app — prefer a backend-for-frontend with `HttpOnly` cookies.
4. **Session security** (if cookies): `HttpOnly`, `Secure`, `SameSite`, rotation on privilege change, idle + absolute timeout, fixation protection.
5. **Authorization model**: RBAC (roles→permissions) for simple/stable; ABAC (attributes/policy) when access depends on context/ownership/relationship. Enforce server-side at the resource; never trust client-supplied roles.
6. **SSO / federation**: SAML or OIDC to the IdP; map IdP claims to local roles; handle JIT provisioning and deprovisioning.
7. **Secrets & rotation**: client secrets/keys in a vault, rotated; MFA where the risk warrants — phishing-resistant (passkeys/WebAuthn) for admins and high-value accounts; account-recovery path designed (a common bypass).
8. **Name the failure modes**: token theft, replay, privilege escalation, IDOR — and the control for each.

## Output

```text
Auth design: merchant dashboard + public refunds API

AuthN
  web dashboard (SPA)   OIDC Authorization Code + PKCE via a backend-for-frontend; HttpOnly, Secure, SameSite=Lax session cookie
  public API clients    OAuth2 Client Credentials; JWT access token, 10 min TTL
  service-to-service    mTLS (mesh identities); no shared secrets
Tokens
  access JWT: RS256 pinned, iss/aud/exp validated; revocation = 10 min TTL + jti denylist for emergencies
  refresh: rotated on every use; reuse revokes the whole family
AuthZ
  model: RBAC for staff (admin, support, viewer) + ownership check (ABAC) on every merchant resource
  enforced at: the API resource handlers — never from client-supplied roles
SSO: Okta via OIDC; groups → roles mapping in config; JIT provisioning; deprovision via SCIM
Secrets: client secrets in Vault, rotated 90d; admins require WebAuthn passkeys

Threat → control
  token theft           short TTL + refresh rotation + DPoP for the refunds API
  replay                jti + exp; nonces on the OIDC flow
  privilege escalation  server-side role check; role changes audited and alerted
  IDOR                  ownership check on every merchant_id path parameter
```

## Quality bar

- AuthN and authZ are designed separately and both enforced server-side.
- Standard OAuth2/OIDC flows are used (Auth Code + PKCE for public clients; no implicit; no `alg:none`).
- JWTs validate `iss`/`aud`/`exp`/signature and have a revocation story; sessions set the secure cookie flags.
- Token theft, replay, and privilege escalation each have a named control.
