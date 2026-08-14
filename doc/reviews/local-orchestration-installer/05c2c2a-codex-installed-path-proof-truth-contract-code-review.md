# Ticket 05C2C2A Codex Installed-Path Proof Truth Contract Code Review

## Initial decision

| Field | Evidence |
| --- | --- |
| Verdict | `CHANGES_REQUESTED / EVIDENCE_DEFECT` |
| Ticket / closure | `05c2c2a-codex-installed-path-proof-truth-contract`; `CLOSURE-LOCAL-INSTALL-T05C2C2A-01`; T1-T7 revision 01 |
| Reviewed handoff | Implementation `d407937d03e7dba49cf066599ac9d5c43e9b3624`; WPR-only handoff `6695b146b28d33faeb341f32c92c79bd2b82e66e` / PRG-410 |
| Immutable export | PASS. Exact handoff TAR SHA-256 `FE360CA2D0DC3E114C2626E7BDFBAAE4429204D23B28CE50E28986A403EFF4BB`; implementation parent is the exact dispatch `3ee3187693aca67630372492c08177560a30420e`, and the implementation changes exactly the four frozen paths. |
| Independent verification | Focused `52/52`; full serial `512/512`; strict `mypy --strict --explicit-package-bases --no-incremental` over `148` files; in-memory compile `148` files; exact ancestry, four-path implementation scope, WPR-only handoff scope, clean worktree and exactly three-worktree topology pass. |
| Adversarial probes | PASS. Ordinary exact `True`/`False` construction and JSON round-trip retain built-in `bool`; `0`, `1`, `-1`, floats, strings, empty values, `None` and containers are rejected. Exact true remains proved absence, exact false remains residue, and mismatched/malformed states remain non-authorizing. |
| Reverse evidence | PASS. Three independent in-memory reversals made the T1 literal contract, direct compensation false/residue mapping and receipt-removal false/residue mapping red, then restored all three governing tests green without modifying either repository worktree. |
| XSS / effect boundary | `XSS_NOT_APPLICABLE`. Typed Python proof contract and tests only; no Browser, WebView, HTML/DOM, JavaScript, bridge, live Codex/host, target-project, network, package/install, push, release or deployment effect. |

## Finding

### CR-177 — submitted exact file hashes do not identify the reviewed implementation

- Classification: `EVIDENCE_DEFECT` against T7 and the frozen WPR-only handoff requirement.
- PRG-410 claims four SHA-256 values which do not match the files exported
  from implementation `d407937d03e7dba49cf066599ac9d5c43e9b3624`.
- Reviewer readback produced these exact values:
  - `library/local_orchestration/codex_compensation_port.py`:
    `F899D685278132238BF79EFBEC2013CA34E495DA632E6FB35450CDE843A87ECE`
  - `tests/test_codex_compensation_port.py`:
    `845E6BBB5D46ED2FF9A87FC01A27FBB76C5E05D0529AF9E2894CB15FD0160FF1`
  - `tests/test_codex_compensation_composition.py`:
    `69D7F71C44ADBBE700EE2CF5439C737D611C16BB33701990A741094D7D55126B`
  - `tests/test_codex_receipt_removal_composition.py`:
    `66CDDDD1288720124C02DA409939A76E0CAD181811B39E63270902485537B545`
- Correction is evidence-only: append one WPR record which explicitly
  supersedes only PRG-410's `Exact file hashes` row with these four values.
  Source, tests, PRG-410 and prior commits remain immutable.

## CodeReview.md assessment

| Category | Result |
| --- | --- |
| Functionality / specification | PASS. The strict proof predicate is truthful for both exact states and existing consumers preserve their frozen finite mapping. |
| Clarity / P0 typing | PASS. Production changes only `Literal[True]` to strict-config `bool`; no `Any`, `type: ignore`, optional port, internal widening or dynamic lookup is introduced. |
| Security / identity / paths | PASS. The manifest remains mandatory and exact; false is residue, not authority. Foreign or malformed manifests cannot confirm absence. |
| Boundary / exceptions | PASS. Pydantic strict validation rejects non-bool truth cells; no new effect or exception suppression exists. |
| Tests / truthfulness | `CHANGES_REQUESTED`. Executable evidence passes, but the submitted four-hash provenance row is false and therefore cannot close T7. |
| Compatibility / maintainability | PASS. Public names and the five-operation port surface remain unchanged; valid consumers no longer require construction bypass. |
| Scope / resource fit | PASS. Exactly four frozen implementation paths and one WPR-only handoff were committed; `STANDARD`, one owner and no helper remain appropriate. |

The implementation is not being rejected or rewritten. CR-177 is the single
blocking item in this closure revision, and only an additive WPR-only evidence
correction at reserved PRG-20260814-413 on the same
owner/worktree/branch/allocation/receipt is authorized.

## Reviewer evidence-frame correction and final decision

| Field | Evidence |
| --- | --- |
| Verdict | `APPROVED / READY_TO_MERGE`; the initial `CHANGES_REQUESTED` decision and CR-177 are superseded by this reviewer correction. |
| Cause | The reviewer compared three distinct byte frames without labeling them: mixed-EOL Windows checkout bytes, Git-for-Windows archive bytes normalized to CRLF, and canonical LF Git blobs. Different SHA-256 values across those frames do not show a changed implementation. |
| Submitted evidence | PASS. In the clean owner worktree, all four checked-out SHA-256 values exactly equal PRG-410. PRG-410 accurately reports its submitted worktree frame. |
| Immutable commit identity | PASS. The four Git blob IDs at implementation `d407937d03e7dba49cf066599ac9d5c43e9b3624` are respectively `a160355be24bab4ab8ff2623293c49f4fbbb5011`, `fa9989c5ce6828f40e84f20b543881cfc62d6f13`, `d19d6a7cd3e723fe10cc0683adf2445c18b8ffc1`, and `c75d3be8b042a5699584e77b1c6dc3948868e045`. The owner branch retains those exact blobs. |
| Raw blob SHA-256 | Canonical LF Git-blob bytes are respectively `072F6F72ED2014DFD079D9F9B3E13D3E25A26507142E7D772C5C6D0382234153`, `9958B97CFC1A74E0F164C07662960FF7C0FCBEC7CF873409F6C7E90485DCA53F`, `AE5FC1F8B36FDF3EE86654E47AF759E31D098021FD3ADCC325E9A014FC66B254`, and `D3871C450078A24EB1C716175380FD3867531A3E9A6035EF4CC773BE6079AECE`. |
| Invalid correction stopped | Owner steer returned `HALT / REVIEWER_EVIDENCE_FRAME_MISMATCH` after merge `50f151c0ec6e9abec9b4c13bdf65e702d97d468e`; no PRG-413 or evidence-correction commit was created, and tracked/ignored porcelain remained empty. |
| Final closure | T1-T7, P0 typing, executable evidence, exact scope and immutable blob identity pass. No blocking finding remains. |

The four hashes originally frozen under CR-177 are retained above only as the
historical archive-frame evidence that exposed the reviewer mistake; they do
not supersede PRG-410. Future provenance should label its byte frame explicitly,
but that nonblocking hardening does not alter this ticket's frozen closure.
