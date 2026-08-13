# Ticket 05B4B2E2 Codex Registration Oracle Adapter Code Review

## Revision-02 terminal review

`APPROVED / GUARDED_INTEGRATION_READY`

The exact rebound return is implementation `b3b50a02a48e7bb8e175200b45e8311e0895f878`
and WPR-only handoff `cc436c28782fb47e10de81e7bfbe3fa8e1b555cb`.
The handoff's first parent is the implementation commit, which descends from
the immutable E2 handoff through correction candidate `d3569f24…`; the net
implementation scope remains exactly the two frozen adapter/test paths.

### Revision-02 verification

| Gate | Reviewer result |
| --- | --- |
| R1-R8 | PASS. Independent immutable export passed focused `14/14`, full serial `402/402`, strict mypy `134/134` files and in-memory compile `134/134` files. `git diff --check`, ancestry, exact two-path scope, topology and residue readbacks passed. |
| CR-162 | PASS. Direct construction without the private capability raises before admission/effect. Removing the token gate made the named test fail with `TypeError not raised`; the exact committed blob was restored. |
| CR-163 | PASS. Constructed/injected bound state and incomplete lease return finite rejection. Reviewer probes additionally rejected lease/binding subclasses plus nested extra/missing identity state `4/4`; a caller equality bomb was not executed. Bypassing the exact bound-state gate made the named child test fail with exit `3`; the exact committed blob was restored. |
| CR-164 | PASS. Exact block, malformed/wrong-surface evidence and valid version mismatch map respectively to `COMMAND_FAILED`, `MALFORMED_OUTPUT` and `UNSUPPORTED_CLI`. Collapsing the classification gate made the named child test fail with exit `6`; the exact committed blob was restored. |
| Strong typing / dependencies | PASS. No `Any`, `type: ignore`, dynamic member lookup, callable port or new dependency occurs in the frozen paths. The additive `b3b50a02…` change only narrows the CR-162 test union before direct construction. |
| CodeReview category 1 | PASS / not newly applicable. No prefix-based authorization or routing comparison was introduced; path/identity acceptance uses exact rebuilt typed values, and existing mismatch tests remain green. |
| CodeReview category 3 | PASS. Factory construction, exact request admission and same-instance proof state gate all protected operations before oracle effects; direct-constructor reversal proves the authority check is observable. |
| CodeReview category 7 | PASS. R1-R8 and CR-162/163/164 map to named observable tests; all three correction gates independently turned red when reversed and returned green after exact re-export. |
| CodeReview category 8 | `XSS_NOT_APPLICABLE`. The ticket adds no Browser, WebView, HTML/DOM renderer, JavaScript context or privileged bridge. |
| CodeReview category 9 | PASS. Product readback reports project `6d2ebb66-1ae7-48b4-96da-53ffba88ef1f`, task `019ffb0c-c9c7-7b30-b614-02dea7ed9042` and active root `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`; canonical Git root/git-dir and opaque workspace binding independently match the permanent owner worktree. |

No unresolved blocking finding remains. The earlier `CHANGES_REQUESTED`
decision below is retained as immutable review history; CR-162, CR-163 and
CR-164 are closed by this revision-02 terminal review.

## Review decision

`CHANGES_REQUESTED`

The submitted behavior suites pass, but reviewer adversarial probes found one
factory-authority bypass, one non-finite constructed-input path, and one false
preflight classification. R2-R3 are not closed.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / closure | `05b4b2e2-codex-registration-oracle-adapter`; `CLOSURE-LOCAL-INSTALL-T05B4B2E2-02`; R1-R8 |
| Owner / branch | Task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation`; `codex/implementation-codex-registration-oracle-adapter-05b4b2e2` |
| Chain | Dispatch `ace86099bc3582dbd8642662b0c937867b3e7d1f` -> implementation `b3894f33b5e050d495e4fde1e39aec0c32bfb0be` -> docs-only handoff `699cba8f1b844552a9b36baf926613594542ed4b` |
| Scope | Implementation adds exactly the two authorized staging adapter/test paths; handoff is WPR-only; submitted lane is clean. |

## Closure verification

| Gate | Result |
| --- | --- |
| R1 | PASS: missing-module first red and staging-only two-path scope are recorded. |
| R2 | FAIL / CR-162 and CR-163: direct `CodexRegistrationOracleAdapter(lease, oracle, bound)` bypasses the factory logical-root/authority gate and is admitted by `admit_codex_registration_port`; `OracleIdentityBound.model_construct()` escapes as `AttributeError` instead of finite adapter rejection. |
| R3 | FAIL / CR-164: `fresh_preflight` maps every oracle block/malformed response/version mismatch to `UNSUPPORTED_CLI`, creating a false version diagnosis. |
| R4-R7 | PASS for the committed ordinary/child matrix: exact add/proof sequence, foreign request zero-effect, fresh-list proof, fixed child root and parent-environment preservation behave as specified. |
| R8 | PASS for the four submitted reversals, but R2-R3 reviewer probes require additive correction evidence. Reviewer independently reran focused 11/11 and full 399/399 from the exact handoff snapshot. |
| XSS | `XSS_NOT_APPLICABLE`: no Browser, WebView, HTML/DOM renderer, JavaScript execution context, or privileged bridge exists. |

## Required correction

Same ticket, owner, worktree, branch, allocation and receipt. Add one source/test
correction commit, then one WPR-only handoff:

1. Make construction capability-safe: only the module-private factory authority
   may construct a usable adapter. A direct constructor call must fail before it
   can be admitted or invoke the oracle. Do not rely on a naming convention.
2. Recursively and finitely reject constructed/missing/extra/injected lease and
   bound identity states without caller-controlled attribute/equality/hash/repr/
   serialization execution or leaked exception text.
3. In fresh preflight, map an exact `OracleBlocked` to
   `CodexBlockReason.COMMAND_FAILED`, malformed/wrong-surface accepted evidence
   to `CodexBlockReason.MALFORMED_OUTPUT`, and only an exact valid VERSION value
   different from the retained expected version to `UNSUPPORTED_CLI`.
4. Add named tests for direct-constructor authority bypass, constructed binding
   finite rejection, and the three preflight classifications. Reverse the
   constructor token gate and the block/malformed/version distinction, restore
   exact blobs, and rerun the existing R1-R8 verification set.

No production edit, new worktree/branch, broad cleanup, staging push,
package/build/install, live Codex, target-project write, release, or deployment
is authorized.
