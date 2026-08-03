# ADR-20260804-001｜Private Router SaaS control plane

- Date: `2026-08-04 (Asia/Taipei)`
- State: `ACCEPTED`
- Decision maker: project owner
- Related specification: `SPEC-AI-WORKFLOW-PRIVATE-ROUTER-SAAS-20260804-01KZ49YM6HA658QF7ME2A5BR26` (`APPROVED`)
- Related change: `CHG-20260804-008`

## Context and Problem

A local, delivered skill can be inspected, copied, modified, or retained after removal. The project owner requires the core Router policy, Profile, scoring, and decision logic to remain private while customer source, Context, and prompts remain on the customer's machine.

## Decision

Adopt a private Router SaaS control plane. The local plugin is a thin client that sends only strict pseudonymous metadata, account-scoped salted revision digests, typed events, entitlement mode, and structured redacted summaries. The private service returns a typed decision and product-language next action. It does not receive raw customer source, document content, paths, URIs, prompts, secrets, PII, or ContextPacket data.

The external product language abstracts internal workflow terms. It may not obscure material data handling, payment, permission, or blocker information. Naming is not a security mechanism.

## Alternatives and Tradeoffs

| Alternative | Decision |
| --- | --- |
| Local-only perpetual license | Rejected: the customer receives the core logic and updates cannot be reliably controlled. |
| Local binary/obfuscation | Rejected: raises reverse-engineering cost but does not preserve a trade secret and degrades auditability. |
| Full source/context upload for server-side routing | Rejected: violates the product's privacy boundary and creates unacceptable data custody. |
| Private SaaS Router with metadata-only request | Accepted: protects the server-held core while keeping customer raw content local; sacrifices semantic accuracy and adds service responsibility. |

## Consequences, Risks, and Recovery

- The product is now a SaaS control plane, even though it does not host models or target projects.
- The local client cannot be trusted to prove metadata truthfulness and a user can bypass the product by not using it; the service only gates its own capability route.
- Service unavailability, malformed response, or missing entitlement must fail closed.
- A future MVP must decide the identity, hosting, data region, retention, payment, and legal controls before public operation.
- Recovery is to remove the optional Router client integration and revert to the static plugin release; customer projects remain independently runnable.

## Revision / Supersession Record

- No supersession at initial acceptance.
