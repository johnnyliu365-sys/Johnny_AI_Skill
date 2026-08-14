# 05C2C3 — Codex Oracle Marketplace Source Truth

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06, AC-07 and AC-08 |
| Change / Context | `CHG-20260808-011` / `doc/context/local-orchestration-installer/main.md`; non-requirement-changing staging-evidence defect |
| Revision | `01` |
| State | `CORRECTION_IN_PROGRESS / DISPATCHED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C2C3-01` / S1-S7 |
| Dependency | 05C2C1 guarded merge `fffbc616ee1870b69845cbcecf37a98e842106d3`; 05C2C2 guarded merge `bc97a42638540cb56e0b2b0c716bd93ddeb5dbba` |
| Profile / resource | `STANDARD`; one implementation owner, no helper; exact two-path staging-only correction |
| XSS | `XSS_NOT_APPLICABLE`: typed Python child protocol fixture and tests only; no renderer or JavaScript context |
| Implementation language | Python 3.11 with explicit strict Pydantic/domain types and full-tree `mypy --strict`; no numeric line limit |

## Defect boundary

The integrated 05C3 dependency probe proves plugin and installed-path presence
as `RESIDUE`, but marketplace presence as `MISMATCH`. The real oracle response
currently hard-codes `marketplaceSource.value = "oracle-source"`; the exact
receipt-bound manifest carries the admitted relative source locator
`marketplaces/<marketplace>`. 05C2B therefore correctly returns
`PRE_REMOVAL_EVIDENCE_INVALID` before either removal.

This ticket corrects only staging-oracle evidence. It does not change the
product compensation observer, receipt, removal order, public outcome or SPEC.

## Frozen responsibility S1-S7

| Gate | Required observable behavior |
| --- | --- |
| S1 — exact owned source | A validated owned marketplace record whose locator is exactly `marketplaces/<name>.json` is listed as `CodexMarketplaceSource(type="local", value="marketplaces/<name>")`. The source is derived from that exact persisted locator, never from a hard-coded token, process environment, absolute root or caller hook. |
| S2 — exact foreign source | Every admitted foreign marketplace entry independently derives its own relative source from its own validated locator. Owned and foreign order/cardinality/data/payloads remain unchanged; no filtering or prefix match is allowed. |
| S3 — finite invalid state | Missing, non-string, wrong-prefix, suffix, casing, URL-encoded, traversal, empty, extra or otherwise invalid persisted locators remain `OracleBlocked / STATE_INVALID` before a partial marketplace-list response. No state or payload byte may change. |
| S4 — compensation truth | Feeding the real owned list and exact integrated manifest through `observe_codex_compensation_operation(LIST_MARKETPLACES, ...)` yields `CodexMarketplaceProof / RESIDUE`; after exact owned removal it yields `PROVED_ABSENT`. Foreign prefix-similar entries do not become owned residue. |
| S5 — preserved protocol surface | Marketplace-list discriminator, exact `CodexMarketplaceList`/entry/source admission, child argv, bounded process behavior, state/payload preservation and all existing failure mappings remain unchanged. |
| S6 — P0 strong type | New or changed variables, parameters, returns and fixtures use named explicit types; dynamic data is validated at the JSON/child boundary. No `Any`, `type: ignore`, implicit/untyped contract, optional port, dynamic lookup, broad catch/clear or historical-source copy. |
| S7 — reversals and evidence | Independently reverse the relative-source derivation to the old hard-coded value, derive it from absolute `root`, and filter the prefix-similar foreign entry. Each governing named test must turn red, then exact bytes restore. Focused tests, full serial suite, strict full-tree mypy, in-memory compile, source sentinel, exact scope/diff/ancestry/topology and zero tracked/ignored/cache/runtime residue must pass. |

## Exact writable scope

- `tests/staging/codex_lifecycle_oracle/oracle_child.py`
- `tests/test_codex_lifecycle_oracle.py`

No production `library/` file, adapter, receipt/removal source, other test,
export, document or target project is writable in the implementation commit.

## First red and completion

The first red must execute the real owned marketplace add/list path and show
that the returned source is `oracle-source` instead of the exact persisted
relative locator. A unit that merely asserts a new helper/module exists is not
sufficient. Completion is one implementation commit changing exactly the two
paths above, followed by one WPR-only handoff commit at the PRG reserved by the
dispatch registry. Independent review and guarded integration remain required
before 05C3 may be refrozen.

## Binding reservation

| Field | Value |
| --- | --- |
| Workspace / handoff | `wsb_local_orchestration_install_05c2c3_20260814_01` / `hnd_local_orchestration_install_05c2c3_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05c2c3_20260814` / `rcpt_local_orchestration_install_05c2c3_20260814` |
| Correlation / question | `corr-local-orchestration-install-05c2c3-20260814` / `q-local-orchestration-install-05c2c3-20260814` |
| Side context | `scx-local-orchestration-install-05c2c3-20260814-01` |
| Authority | Standing project-owner auto-continue `PRG-20260809-042`; this reservation is not dispatch authority. |

## Exact dispatch registry

| Field | Value |
| --- | --- |
| Ticket schema gate | `PASS`: revision-01 freezes S1-S7, real add/list first red, strict Python typing, exact two-path scope, one owner/no helper, `XSS_NOT_APPLICABLE`, reversals and a unique binding. |
| Authority / reviewer | Standing project-owner auto-continue `PRG-20260809-042`; sole reviewer/orchestrator task `019fb935-bbe1-7f71-8b4b-58ba20c81626`. |
| Exact implementation owner | Existing task `019ffb0c-db88-7303-895c-aecfadde7c8d`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementer-2`; new branch `codex/implementation-codex-oracle-marketplace-source-truth-05c2c3` in that same worktree; no helper/subagent/second owner. |
| Lane readback | Idle clean lane at `codex/implementation-codex-installed-path-proof-truth-05c2c2a` / `50f151c0ec6e9abec9b4c13bdf65e702d97d468e`; no tracked/ignored residue; exactly three worktrees. That head is an exact ancestor of the dispatch baseline and the target branch does not yet exist. |
| Baseline admission | From the exact control commit carrying this registry, create the named branch in the same permanent worktree. Do not merge/copy a historical implementation branch or create another worktree; never reset, rebase, amend, force or stash. |
| Binding | Workspace `wsb_local_orchestration_install_05c2c3_20260814_01`; handoff `hnd_local_orchestration_install_05c2c3_20260814`; allocation `aln_local_orchestration_install_05c2c3_20260814`; receipt `rcpt_local_orchestration_install_05c2c3_20260814`; correlation `corr-local-orchestration-install-05c2c3-20260814`; question `q-local-orchestration-install-05c2c3-20260814`; side context `scx-local-orchestration-install-05c2c3-20260814-01`. |
| Return | One implementation commit changing exactly the two frozen paths, then append only reserved `PRG-20260814-423` in one WPR-only handoff commit. Independent review remains reviewer-owned. |

This registry converts the reservation into exact implementation authority only
for S1-S7. Any schema, baseline, lane, scope or effect mismatch must return a
typed `HALT` before source/test mutation.

## Independent review

Implementation `8de9e60a59645fdf4fc7e6b298be3bcd70b06789` passes S1-S7,
P0 strong typing, the real receipt-to-removal disposable probe and independent
runtime reversals. Review `CR-179` is limited to one `EVIDENCE_DEFECT`: the
PRG-423 handoff was inserted before later historical records instead of being
appended at the physical end of `WorkProgressReport.md`.

The implementation and tests are approved as submitted. The same owner,
permanent worktree, branch, allocation, receipt and correlation must append a
new canonical WPR-only handoff at the end of the file. PRG-423 and every prior
commit remain immutable; no source, test or prior WPR line may be changed.

## CR-179 correction dispatch registry

| Field | Value |
| --- | --- |
| Review baseline | `fab2fbc341cb8c32736b9fdfc89cf9d25f04d165`; CR-179 authorizes evidence placement correction only. |
| Owner / lane | Existing owner task `019ffb0c-db88-7303-895c-aecfadde7c8d`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementer-2`; existing branch `codex/implementation-codex-oracle-marketplace-source-truth-05c2c3`; no helper, new branch or new worktree. |
| Binding | Retain workspace `wsb_local_orchestration_install_05c2c3_20260814_01`, handoff `hnd_local_orchestration_install_05c2c3_20260814`, allocation `aln_local_orchestration_install_05c2c3_20260814`, receipt `rcpt_local_orchestration_install_05c2c3_20260814`, correlation `corr-local-orchestration-install-05c2c3-20260814`, question `q-local-orchestration-install-05c2c3-20260814` and side context `scx-local-orchestration-install-05c2c3-20260814-01`. |
| Merge admission | Merge the exact control commit carrying this registry into the existing branch without reset, rebase, amend, force, stash or historical-source copy. Only the predicted append-only `doc/WorkProgressReport.md` overlap may be resolved; preserve PRG-423, PRG-424 and PRG-425 exactly once. |
| Correction | After the merge, append only reserved PRG-20260814-426 at physical EOF in one new WPR-only commit. State that PRG-426 is the canonical integration handoff and that PRG-423 remains immutable historical evidence whose placement alone is superseded. |
| Immutable source | `oracle_child.py` blob `86edacbbb43a36475071c5494b8c4e0cc2b81f60` and direct-test blob `d897552e65c506e49132b82e1eaccdf8f4004d37` must remain exact. No source/test/ticket/review or previous WPR line may change. |
| Verification | Read back the two exact blobs, physical EOF, unique PRG-423 through PRG-426 headings, clean tracked/ignored status, exactly three worktrees and zero cache/runtime residue. Executable suites are not rerun because no executable blob may change. |

Any mismatch returns typed `HALT`; otherwise return the history-preserving
merge commit and the WPR-only PRG-426 correction commit for terminal review.

## Forbidden effects

No new branch/worktree before an exact dispatch registry; no helper/subagent;
no live Codex/home/config, target-project, network, push/staging publication,
package/build/install, Secret, release or deployment effect.
