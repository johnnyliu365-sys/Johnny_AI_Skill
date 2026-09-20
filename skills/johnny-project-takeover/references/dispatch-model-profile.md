# Bundled dispatch model profile

Profile ID: `JOHNNY-DISPATCH-DEFAULTS`, revision `01` (2026-09-20).
This is versioned selection data, not role authority or proof that a model can run.
Read it before selecting an implementation or review model on either supported host.

## Resolve before dispatch

1. An admitted ticket's exact approved profile binding wins. Resolve that reference;
   a missing, stale or conflicting explicit binding is `HALT / ROUTE_REFERENCE_INVALID`
   and must not fall back to these defaults.
2. For an unbound/new ticket, use the target's approved project profile if one exists.
   Otherwise use this bundled registry as the default proposal and bind the resulting
   profile revision to the ticket through normal admission. The reviewer records this binding
   in the target's next ticket/profile artifact; the human approves it with the normal
   ticket/profile approval (`APPROVAL_GRANTED`), not a second file-creation ceremony.
   Do not demand that the target
   contain a copy of Johnny's development runbook or invent a profile from memory.
3. Check the selected provider/model/effort against the host's actual offered capability.
   Use the host's exact model identifier in the dispatch call, with explicit effort where
   supported. An advertised configuration is not credential or execution evidence.
4. Missing file, unconfigured host mapping and unavailable model are different failures.
   Report the unresolved reference, missing mapping or unsupported capability respectively.
   Do not call all three a missing profile file, silently elevate, inherit an unspecified
   parent model, switch providers or implement the ticket in the reviewer as a fallback.

Defaults are not a machine-global override and do not approve a ticket. Target profile
data may override them only through its existing owner-approved process. Do not copy
this governance text into a target or host-user instruction file.

## Codex registry

These semantic intents preserve the previously approved project mapping. Resolve display
names to the exact model IDs offered by the host; this table does not assert availability.

| Profile | Model / effort intent | Permitted use |
| --- | --- | --- |
| `decision-support` | Sol / high | Initial project review or requirement changes needing complex-decision analysis |
| `ticket-review` | Terra / xhigh | Normal ticket preparation and independent ticket review |
| `implementation-standard` | Luna / xhigh | Normal single-ticket implementation |
| `implementation-elevated` | Terra / xhigh | One indivisible ticket after an approved hard-ticket assessment |
| `elevated-review` | Sol / high | Review of that same elevated implementation ticket only |

The human is `ARCHITECTURE_OWNER`. A model's capability never grants owner authority.
The reviewer's verified capability rank must not be lower than the implementer's.
Try valid decomposition before elevation. An elevation requires the exact ticket's
`HardTicketAssessment`, including the named capability gap; it is not a global switch.
No further fallback is implied when the bounded implementation/review cycle is exhausted.

## Claude Code mapping

The same semantic profiles and reviewer-strength rule apply. This revision does **not**
invent a Claude model/effort tuple: the previously superseded provider-specific mapping
is not a default. Resolve an approved Claude project/host profile and verify the exact
host capabilities and credential state before selecting it. If none is registered,
report **host mapping unconfigured**, state the missing semantic-role bindings and ask
the owner to select them from observed host capabilities. The bundled profile file is
present; lack of a configured Claude tuple is not a file-delivery defect. Emit the existing
`EXTERNAL_DECISION_REQUIRED` event with `WAIT_FOR_HUMAN`; resume on `OWNER_INPUT_PROVIDED`
and apply the same normal profile approval. Do not invent a new runtime blocker enum.

Provider/model/effort values belong in profile data supplied to a resolver, never embedded
in resolver or hook source. Installing a CLI is not proof of authentication or capability.

## Lifetime and ownership

The current reviewer owns delegation, completion waiting, review and integration. Reuse
the ticket-bound implementation owner when available; do not create replacement owners
merely to inspect progress. A new host seat is needed only when that owner is unavailable.

Same-lifetime dispatch binds the exact ticket, admitted profile, clean baseline and
repository-contained worktree/branch; delegate, wait for completion, review, then route
through the integration gate. Runner, queue, receipt, descriptor, host gateway and
workspace/profile readback are `NOT_REQUIRED` on this direct route. Their absence must
not block it. Cross-lifetime handoffs retain their receipt-bound controls under
[router-control](router-control.md); an unarmed wake is not a delivered event.

Dispatch only the admitted identifiers and necessary bounded resume state. Resolve scope,
checks and return obligations from the current authority, not a duplicate prompt. The
ticket determines commit ownership; no particular project's no-commit exception becomes
a universal default. The implementation owner cannot delegate or approve integration.

## Provenance

The Codex values and elevation rules preserve the repository's model-profile revision 03
(2026-08-29). The owner requested an installed default on 2026-09-20 after an agent could
not locate the model file. This moves the canonical data into the shipped skill tree;
the development runbook is a pointer only. Publication and installed-host qualification
are separate from this source correction.
