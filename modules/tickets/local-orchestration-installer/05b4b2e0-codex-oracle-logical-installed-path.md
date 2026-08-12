# 05B4B2E0 — Codex Oracle Logical Installed Path

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 staging evidence seam |
| State | `IN_PROGRESS / DISPATCH_CONFIRMED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E0-01` / O1-O8 |
| Dependency | 05S4 integrated by `4af381c`; B2C/B2D integrated by `af3a95a` / `9769a75` |
| Planned owner | Task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation`; no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## One observable outcome

Make the 05S4 disposable oracle persist and return the exact logical Windows
installed path observed by `plugin add`, while keeping its internal physical
payload locator relative to the disposable `CODEX_HOME`. This closes the
current evidence gap: the oracle can prove physical payload truth, but its
plugin-add response currently returns `plugins/<plugin-id>.json`, which cannot
satisfy the integrated registration proof's canonical absolute-path contract.

## Frozen design

- Add required `plugin_installed_path: str` to `OracleIdentity` and required
  `installed_path: str` to `OraclePluginRecord`. These are logical host
  observations, not filesystem authorities.
- Validate a logical path as a normalized, drive-qualified Windows absolute
  path with no URI form, NUL, encoded separator, traversal component, trailing
  separator or slash ambiguity. E1 will later bind its exact value to the
  canonical registration locator; E0 must not import or guess a registration
  request.
- Persist `installed_path` in oracle state and include it in the exact plugin
  payload bytes/digest. `PLUGIN_ADD` must return that persisted field as
  `installedPath`.
- Keep `locator == plugins/<plugin-id>.json` as the only disposable physical
  locator. State/payload traversal, topology and digest checks continue to use
  `locator`, never the logical Windows path.
- Update default identity and foreign-plugin fixtures explicitly. No optional
  field, migration fallback or historical state reuse is allowed; an old or
  malformed state fails closed.
- No adapter, registration/compensation composition, receipt, real Codex or
  target-project behavior belongs to this ticket.

## Acceptance Closure Set

| ID | Finite completion rule |
| --- | --- |
| `O1` | First red proves the integrated oracle lacks the required logical installed-path contract or returns its physical locator as `installedPath`; production staging files remain unchanged during red. |
| `O2` | An exact logical Windows path survives `OracleIdentity -> command JSON -> persisted OraclePluginRecord -> exact payload/digest -> CodexPluginAdd.installedPath` without normalization or substitution. |
| `O3` | The separate physical locator remains exactly `plugins/<plugin-id>.json` below the leased oracle payload root; the logical path is never joined to, opened, created, removed or traversed as a filesystem path. |
| `O4` | Relative, URI, encoded-separator, traversal, slash-ambiguous, trailing-separator, drive-missing, NUL and constructed malformed logical paths fail closed before mutation or return the existing finite oracle block. State and payload bytes remain unchanged. |
| `O5` | Changing only persisted/payload logical installed path breaks exact state/payload validation or digest verification; old-schema and extra-field state also fail closed. |
| `O6` | Foreign plugin seeding and owned add/list/remove/absence continue to preserve foreign records and payloads with their explicit logical installed paths. Existing 05S4 behaviors remain green. |
| `O7` | Source adds no `Any`, `type: ignore`, broad catch, optional/`None` authority, dynamic lookup or historical-source reuse. It performs no live Codex, host, network, target-project, package, push, release or deployment effect. `XSS_NOT_APPLICABLE`. |
| `O8` | Independently reverse logical-path response binding, state/payload retention, digest coverage and physical/logical separation. Each named committed test turns red and exact blobs restore; focused/full unittest, strict full-tree mypy, in-memory compile, source/scope/diff/ancestry/topology and residue checks pass. |

## Exact source and return

Writable implementation paths only:

1. `tests/staging/codex_lifecycle_oracle/contracts.py`
2. `tests/staging/codex_lifecycle_oracle/oracle.py`
3. `tests/staging/codex_lifecycle_oracle/oracle_child.py`
4. `tests/test_codex_lifecycle_oracle.py`

All production library source and all other tests remain read-only. No numeric
line limit is an acceptance criterion. Return one exact four-path
implementation commit, then one `doc/WorkProgressReport.md`-only handoff
reserved as `PRG-20260813-266`.

No E1-E6/05C/package work, live Codex, real host/filesystem, target-project,
other Agent, review/integration, push, release or deployment is authorized.

## Initial independent review and bounded correction

Implementation `f79696241a828e1d523370d6b03ff0c6ed45355c` and docs-only
handoff `05b65bce17be0dbab7aeefc8118ad8d37e3d5bce` are
`CHANGES_REQUESTED / SAME_CLOSURE_CORRECTION`.

- `CR-157 / IMPLEMENTATION_DEFECT / O2-O6-O8`: `_exact_plugin()` does not bind
  the required logical installed path. A remove command carrying a different
  valid path deletes the installed plugin instead of returning the finite
  existing block with zero mutation.
- `CR-158 / IMPLEMENTATION_DEFECT / O4-O8`: both path validators accept a
  Win32-ambiguous segment ending in a space or period, contrary to the frozen
  normalized-path rule.

Revision 02 retains the same closure, owner, worktree, branch, allocation,
receipt and correlation. Add named regressions for both findings, make the
exact plugin identity include `installed_path`, reject segment-ending space or
period in the parent and child validators, and independently reverse both new
guards. Only the original four implementation files plus a later WPR-only
handoff may change. No new branch or worktree is allowed.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2E0-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2e0_20260813` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e0_20260813` / `rcpt_local_orchestration_install_05b4b2e0_20260813` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e0-20260813` / `q-local-orchestration-install-05b4b2e0-20260813` |
| Side context | `scx-local-orchestration-install-05b4b2e0-20260813-01` |
| Owner / lane | Existing task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; `workflow-implementation`; later create only `codex/implementation-codex-oracle-logical-path-05b4b2e0` from the exact dispatch commit. |

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `0a71cc6d046a5ead8e5157b42c86fb38e28f0363`; exact O1-O8; `XSS_NOT_APPLICABLE` |
| Delivery authority | Project-owner standing instruction to continue approved work; `IMPLEMENTATION_DISPATCH_CONFIRMED` for this ticket only |
| Lane readback | Task is idle; existing `workflow-implementation` is clean at exact submitted HEAD `09467cd8b8a9f652648e8383750fa36d190a41fd`; no tracked/ignored/cache residue; exactly three existing worktrees; target branch absent |
| Branch | Create only `codex/implementation-codex-oracle-logical-path-05b4b2e0` from the exact dispatch-registry commit in the same worktree; no new worktree |
| Binding | `hnd_local_orchestration_install_05b4b2e0_20260813`; `aln_local_orchestration_install_05b4b2e0_20260813`; `rcpt_local_orchestration_install_05b4b2e0_20260813`; `corr-local-orchestration-install-05b4b2e0-20260813`; `q-local-orchestration-install-05b4b2e0-20260813`; `scx-local-orchestration-install-05b4b2e0-20260813-01` |

This is the single dispatch. Only the exact four implementation paths and a
later WPR-only `PRG-20260813-267` are writable in this lane.
