# ADR-011 PROPOSAL: Enterprise Security Baseline

**Status:** IMPLEMENTED — baseline modules landed, awaiting Council ratification for production hardening  
**Date:** 2026-06-12  
**Author:** Deep-Tech Research Swarm  
**Depends On:** ADR-001 (Consensus), ADR-002 (Topology), ADR-004 (Memory)  
**Scope:** All blocks — Framework, Memory, Consensus, Cognition, Perception, Generation  
**Affected Components:** Authentication, authorization, encryption, audit logging, secret management, API security

---

## 1. Context

ACN is moving from research architecture toward enterprise deployment. Before any block reaches production, the system must satisfy baseline security requirements common to enterprise SaaS and on-premise deployments:

- **Identity:** Who is accessing the system?
- **Authorization:** What can they do?
- **Encryption:** How is data protected at rest and in transit?
- **Audit:** What happened, when, and who did it?
- **Secrets:** How are keys, tokens, and credentials managed?
- **Tenant isolation:** How do we prevent cross-tenant data leakage?
- **Availability:** How do we prevent abuse via rate limiting and resource controls?

This ADR defines the security baseline that every production-bound component must implement.

---

## 2. Problem Statement

How do we make ACN secure enough for enterprise deployment when:

1. Multiple agents with their own memory and reasoning must operate in a shared cluster
2. Different users, teams, or organizations may share the same deployment
3. Agents can autonomously take actions, access memory, and communicate across the network
4. Auditability is required for compliance (SOC 2, ISO 27001, GDPR, HIPAA-adjacent)
5. Credentials for LLM providers, databases, and infrastructure must not be hardcoded
6. A compromised single agent must not compromise the entire network

---

## 3. Options Considered

### Option A: External Identity Provider (OIDC/OAuth2) + Internal RBAC

**Mechanism:** Delegate authentication to an external provider (Keycloak, Auth0, Okta, Entra ID). ACN maintains an internal RBAC system that maps provider identities to roles.

**Pros:**
- Industry standard — integrates with enterprise SSO
- No password storage in ACN
- Supports MFA via the identity provider
- Easy revocation at the IdP level

**Cons:**
- Adds operational dependency on IdP
- Requires token validation on every request
- More complex local/dev setup

### Option B: API-Key-Only Authentication

**Mechanism:** Every client (user, service, agent) uses long-lived API keys.

**Pros:**
- Simple to implement
- Easy for machine-to-machine communication
- Works offline / air-gapped

**Cons:**
- Key rotation is painful
- No SSO/MFA integration
- Hard to attribute actions to human users
- Poor enterprise adoption

### Option C: mTLS + Service Mesh

**Mechanism:** Every service and agent authenticates using mutual TLS certificates.

**Pros:**
- Strong service-to-service authentication
- Encryption in transit by default
- Works well in Kubernetes / Istio environments

**Cons:**
- Complex certificate management
- Doesn't solve human user authentication
- Overhead for agent-to-agent communication

---

## 4. Evaluation Criteria

| Criterion | Weight | OIDC+RBAC | API-Key-Only | mTLS+Mesh |
|-----------|--------|-----------|--------------|-----------|
| Enterprise SSO | Critical | ✅ | ❌ | ⚠️ Service only |
| Air-gapped support | High | ⚠️ Need local IdP | ✅ | ✅ |
| Operational simplicity | High | ⚠️ | ✅ | ❌ |
| Service-to-service auth | Critical | ⚠️ Tokens | ✅ API keys | ✅ mTLS |
| Auditability | Critical | ✅ User attribution | ⚠️ Key attribution | ⚠️ Cert attribution |
| Agent autonomy | High | ✅ Scoped tokens | ⚠️ Shared keys | ✅ Certs |

---

## 5. Tentative Recommendation

**Proposed: Hybrid — OIDC/OAuth2 for humans + API keys for service/agent identities + mTLS encouraged for service mesh deployments**

**Rationale:**

1. **Human users authenticate via OIDC**
   - SSO integration with enterprise providers
   - Short-lived access tokens (15 min) + refresh tokens
   - MFA delegated to IdP

2. **Services and agents authenticate via scoped API keys**
   - Each agent gets its own key with limited scope
   - Keys are hashed before storage (bcrypt/Argon2)
   - Automatic rotation policy (90 days default)

3. **Service-to-service communication uses mTLS where possible**
   - Optional but recommended in Kubernetes/Istio environments
   - Falls back to signed JWT service tokens in simpler deployments

4. **Internal RBAC maps identities to roles**
   - Roles: `admin`, `operator`, `researcher`, `agent`, `viewer`, `auditor`
   - Permissions are resource-scoped: `memory:<tenant>:read`, `agent:<id>:execute`
   - Role assignments stored in configuration, changeable without code deploy

5. **Encryption**
   - In transit: TLS 1.3 minimum
   - At rest: AES-256-GCM for sensitive memory traces and credentials
   - Key encryption keys (KEKs) separated from data encryption keys (DEKs)

6. **Audit logging**
   - Every authentication, authorization decision, memory access, and agent action is logged
   - Logs are append-only and tamper-evident (hash chain)
   - Structured JSON format with trace IDs

7. **Tenant isolation**
   - Every memory trace, agent, and resource is tagged with a `tenant_id`
   - RBAC enforces tenant boundaries at the repository/service layer
   - Shared semantic memory is read-only for tenants unless explicitly contributed

---

## 6. Integration with Other ADRs

| ADR | Integration Point |
|-----|-------------------|
| ADR-001 (Consensus) | Consensus votes are signed and auditable; bad actors lose authorization |
| ADR-002 (Topology) | Service identity tied to topology node identity |
| ADR-004 (Memory) | Memory traces carry tenant_id, owner_id, and encryption metadata |
| ADR-007 (Trust) | Trust boundaries enforced by RBAC + mTLS |

---

## 7. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| OIDC unavailable in air-gapped environments | Medium | High | Ship with embedded Keycloak / Dex as fallback |
| Key rotation breaks running agents | Medium | High | Graceful rotation with overlapping validity windows |
| Audit log volume overwhelms storage | High | Medium | Sampling + async shipping + retention policies |
| RBAC misconfiguration exposes tenant data | Medium | Critical | Default-deny policy + automated tests + access review |
| mTLS certificate expiry | Medium | High | Automated cert rotation + expiry alerts |

---

## 8. Open Questions for Council Deliberation

1. Should agents have their own OIDC identities, or are API keys sufficient?
2. What is the default tenant model — single-tenant with namespace isolation, or true multi-tenant?
3. Which encryption library — Python `cryptography`, AWS KMS integration, HashiCorp Vault?
4. How long should audit logs be retained? 30/90/365 days? Configurable per tenant?
5. Should we support Bring Your Own Key (BYOK) for encryption?

---

## 9. Implementation Notes

The security baseline has been implemented in `acn/src/security/` with 45 unit tests in `acn/tests/security/`:

| Module | Purpose |
|--------|---------|
| `identity.py` | Typed identity model for humans, services, agents, and system actors |
| `rbac.py` | Role-based access control with predefined enterprise roles and tenant scoping |
| `api_key.py` | API key lifecycle: create, hash (Argon2id/PBKDF2), validate, rotate, revoke |
| `audit.py` | Append-only tamper-evident audit log with hash-chain verification |
| `encryption.py` | Envelope encryption (Fernet/AES-128-CBC-HMAC) with per-tenant DEKs |
| `rate_limit.py` | Sliding-window rate limiter with per-key overrides |
| `config.py` | Environment-driven security configuration |
| `manager.py` | Composed `SecurityManager` facade for authenticate/authorize/audit/encrypt/rate-limit |

Key design decisions realized:
- **Private memory stays private**: security layer does not alter memory ownership; it adds tenant-scoped authorization.
- **API keys are hashed, not stored**: only Argon2id hashes retained; PBKDF2 fallback for minimal environments.
- **Audit log is tamper-evident**: each event hashes the previous chain hash.
- **Default-deny RBAC**: no role grants permission → access denied.
- **Fail-closed configuration**: missing master key raises at encryption manager initialization.

Dependencies added: `cryptography`, `argon2-cffi`.

---

## 10. References

- NIST SP 800-207 (Zero Trust Architecture)
- OAuth 2.0 + OIDC specifications
- OWASP Top 10 2025
- SOC 2 Common Criteria
- HashiCorp Vault security model

---

*This is a PROPOSAL, not a final decision. No production code shall be written until the Council of Ten reaches documented consensus on this ADR.*
