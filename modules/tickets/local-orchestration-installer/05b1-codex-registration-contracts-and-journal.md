# 05B1 — Codex Registration Contracts and Attempt Journal

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 registration seam |
| Parent evidence | Terminal 05B revision-02 review `24227ac`; CR-98 through CR-104 remain immutable evidence |
| State | `CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED` — final initial review `CR-128` through `CR-132` |
| Dependency | 05A plus 05S1-05S4 independently approved and integrated by `b22c6c4`, `504a3ec`, `6e24e06`, `43a1639` and `4af381c` |
| Implementation owner | Task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation` worktree and branch only |
| Acceptance owner | Independent control-plane reviewer; no implementation writes |
| Language | Python 3.11, strict Pydantic and mypy |
| Binding | `hnd_local_orchestration_install_05b1_20260811` / `aln_local_orchestration_install_05b1_20260811` / `rcpt_local_orchestration_install_05b1_20260811` / `corr-local-orchestration-install-05b1-20260811` / `q-local-orchestration-install-05b1-20260811` / `scx-local-orchestration-install-05b1-20260811-01` |

## One outcome

Provide the strict production contract boundary that later registration and
compensation tickets must consume. The boundary carries the real observed
marketplace/plugin add fields into one manifest-proof request, emits a distinct
metadata-only receipt only from an exact proof, and models current-attempt
marketplace/plugin authority as a finite journal. It performs no command,
filesystem, registration, removal, list, absence or target-project effect.

## Exact source boundary

Only these paths may change:

1. `library/local_orchestration/codex_registration_contracts.py` — new.
2. `tests/test_codex_registration_contracts.py` — new.
3. `library/local_orchestration/__init__.py` — export only the new public
   contract surface.

All existing production/test files, including 05A and 05S1-05S4, are read-only.
Rejected Ticket-05/05B branch source may be inspected only through the existing
review findings and must not be copied, cherry-picked or imported. No numeric
line target is an acceptance criterion; responsibility, readability, strict
types, finite behavior and exact scope are.

## Frozen acceptance closure — `CLOSURE-LOCAL-INSTALL-T05B1-01`

| ID | Required first-red and green behavior |
| --- | --- |
| `C1` — strict observed add DTOs | Use named values including `CodexObservedAbsolutePath` and `CodexAuthPolicy`, not raw path/policy strings. Marketplace observation requires exact nonblank `marketplaceName`, absolute `installedRoot` and strict boolean `alreadyAdded`. Plugin observation requires exact nonblank `pluginId`, `name`, `marketplaceName`, `version`, absolute `installedPath` and `authPolicy`. Missing, extra, null, blank, wrong-type, relative, URI, traversal and container inputs fail before any authority object exists. |
| `C2` — proof request and receipt separation | One frozen `CodexRegistrationProofRequest` contains the exact current `CodexPreflightRequest` plus both observed add DTOs. Required non-null `CodexRegistrationProofPort` accepts only that request. A separate frozen `CodexRegistrationReceipt` contains installation, canonical root, marketplace, plugin, CLI version, owned relative source/installed locators, named auth policy and digest, but no absolute path. |
| `C3` — exact proof construction | A named pure constructor revalidates request, observations and proof recursively. It returns the receipt only when installation/root/marketplace/plugin/version/source locator/installed locator/auth policy/digest and observed absolute paths all bind through the proof. Clone, casing, prefix, absolute/relative, locator, version, policy or digest mismatch returns a finite named rejection and no receipt. A proof fake that derives only from the request must fail foreign observed-root/path/auth probes. |
| `C4` — finite current-attempt journal | Separate marketplace/plugin states are exactly `NOT_ATTEMPTED`, `MAY_EXIST`, `OWNED`, `PREEXISTING`. The frozen journal forbids impossible ordering and exposes plugin-before-marketplace unresolved authority only for `MAY_EXIST`/`OWNED`. `PREEXISTING` and `NOT_ATTEMPTED` never grant removal authority. Malformed, constructed, replayed or cross-request journal values fail closed. |

## Required tests and review matrix

- `T1 / C1`: table every missing/extra/null/blank/wrong-type and path-boundary
  cell for both observations; include strict boolean and case/prefix variants.
- `T2 / C2-C3`: exact proof-to-receipt success plus one mismatch cell for every
  bound identity/path/version/policy/digest field. Explicitly prove foreign
  observed `installedRoot`, `installedPath` and `authPolicy` cannot succeed.
- `T3 / C4`: table all legal states, impossible ordering, pre-existing
  marketplace, plugin-before-marketplace and plugin-first unresolved ordering.
- `T4`: strict Pydantic extra/null/constructed/replay checks, reverse mutations
  for observed-field proof and pre-existing removal authority, complete/full
  unittest, strict full-tree mypy with external removed cache, in-memory
  compile, source/scope/diff and zero-residue readback.

CodeReview.md classes 1, 2, 3, 5, 6 and 7 apply. No `Any`, `type: ignore`,
optional/`None` effect port, generic action string, broad catch/clear, raw
exception/output persistence, caller-synthesized success or compressed
multi-statement production line is allowed.

## Explicit non-goals and return

05B1 does not run Codex, use the 05S4 oracle, classify process failures,
perform compensation, expose registration success, implement 05C removal, edit
live Codex configuration, access a target project, network, Secret, package,
push, release or deploy. Those behaviors remain in later 05B2-05B4 tickets.

Return one implementation commit containing exactly the three authorized paths
and one docs-only commit changing only `doc/WorkProgressReport.md`. The
implementation owner makes no review, integration or downstream dispatch
decision. Any contract conflict returns typed `CHANGE_DETECTED`; any unsafe
baseline or missing authority returns typed `HALT`.

## Initial independent review

Implementation `fbedefcef113ff1a85e5709ea80c205c54ff85eb` and docs-only
handoff `6969d4412d0391684739890e4fc3e5451d4ed6c0` have valid ancestry,
exact source/docs scope and a clean implementation worktree. A fresh immutable
export passed focused 4/4, full 209/209, strict full-tree mypy and in-memory
compile over 104 Python files.

The review nevertheless returns `CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED`:

- `CR-128 / TICKET_DEFECT`: C2/C3 name a request-owned auth policy but the
  frozen request has no expected-policy authority separate from observed
  `authPolicy`; a request-only fake produced a receipt for `foreign-policy`.
- `CR-129 / EVIDENCE_DEFECT`: the committed request-only auth fake changes the
  proof after reading a trusted request and therefore never exercises the
  required foreign observed-auth request.
- `CR-130 / TICKET_DEFECT`: CodeReview.md class 6 applies, but C3/T4 do not
  choose finite rejection versus propagation for proof-port failure; an
  injected `RuntimeError` currently escapes.
- `CR-131 / IMPLEMENTATION_DEFECT`: the journal accepts impossible downstream
  plugin states while marketplace is still `MAY_EXIST` or is already
  `PREEXISTING`; T3 incorrectly labels those cells legal.
- `CR-132 / EVIDENCE_DEFECT`: committed T1/T2 do not include the complete
  seven-cell path matrix or the required null/wrong proof-port cases.

No correction or integration is authorized until the control plane refreezes
the finite expected-policy, exception and legal-journal contracts. The same
ticket, implementation owner, worktree, branch, allocation and valid receipt
remain bound; no replacement lane is permitted.
