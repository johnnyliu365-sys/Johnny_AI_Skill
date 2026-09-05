# ENV-MSIX-01 — Provisioning convergence review

| Field | Value |
| --- | --- |
| Artifact ID / kind / revision | `REVIEW-ENV-MSIX-01-20260905` / `OPERATIONAL_READINESS_REVIEW` / `01` |
| Date / conclusion | `2026-09-05 (Asia/Taipei)` / `BLOCKED / CONVERGENCE_REVIEW_REQUIRED` |
| Action / closure | [ENV-MSIX-01](../../../modules/tickets/local-orchestration-installer/env-msix-01-disposable-hyper-v.md) / `CLOSURE-ENV-MSIX-01/01` |
| Initial candidate | `15ca43c29307850b8037ff9c11fcc983b3826fb0` |
| Correction candidate / leaf digest | `7e249dcfc5d722c79f6c1a4f3a1109229ccc4484` / `4f9936c518cd7a05015f724096e4fd2f3d539530d3524182067ff13709b3340c` |
| Final reviewer / helper | Current-session operator / reused Terra-xhigh read-only adversarial helper; no implementation lane or delegated verdict |
| Effect result | VM creation recipe NOT EXECUTED; no test certificate creation/import, host trust change, package operation, host registration, push or release |

## Findings and independent disposition

| Finding | Closure binding / category | Evidence and disposition |
| --- | --- | --- |
| ENV-F1: unobservable partial root admission | Item 5, `ERROR_PARTIAL_FAILURE / OBSERVABILITY`; operational recipe defect | Initial candidate could create the root then fail ACL admission before acquiring result-write authority. Correction introduced pre-creation phase tracking, parent-observed exit 43 for unproved ownership, and exit 44 for failed result delivery. Reviewer inspected those branches: CLOSED by correction, static evidence only; no privileged fault injection was performed. |
| ENV-F2: elevated module search includes user-writable locations | Items 1–2 and the recipe's explicit no-writable-script elevation boundary, `AUTHORIZATION / DEPLOYMENT_READINESS`; operational recipe defect | Correction candidate line 84 imports `Hyper-V` by name, before `try` and before admission checks. A competing user module can therefore be selected by inherited module discovery; failures also precede the declared result handling. Reviewer independently confirmed the search-path premise below. OPEN / BLOCKING; no hostile module was created or executed. |

Both helper returns were received in the existing session. The operator accepts
ENV-F2 as a flaw in the operator-authored recipe, not insufficient owner VM authority,
a missing runner, a product MSIX limitation or an implementer's performance problem.
The second review does not retroactively become approval because ENV-F1 closed.

## Independent read-only evidence

The fresh Windows PowerShell process was invoked without a profile:

```powershell
& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoLogo -NoProfile -NonInteractive -Command '$env:PSModulePath -split ";"'
```

Unfiltered output:

```text
C:\Users\GameBoy\Documents\WindowsPowerShell\Modules
C:\Program Files\WindowsPowerShell\Modules
C:\Windows\system32\WindowsPowerShell\v1.0\Modules
```

Microsoft documents CurrentUser search paths and name-based module discovery in
[about_PSModulePath](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_psmodulepath?view=powershell-7.4),
including Windows PowerShell 5.1's locations. The risk conclusion is an inference
from that behavior and this recipe, not a claim that this workstation is compromised.
The earlier administrator `Get-VMHost` probe's exit 0 proves access, not trusted
module identity; it must not be promoted into provenance evidence.

Read-only filesystem discovery found these Windows manifests:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Hyper-V\1.1\Hyper-V.psd1
C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Hyper-V\2.0.0.0\Hyper-V.psd1
```

Their presence is not yet admission of either version or its transitive executable
dependencies. No system/user module, module search path, profile, group membership
or certificate store was modified. The exact correction recipe passed a parse-only
Windows PowerShell 5.1 check (`WINDOWS_POWERSHELL_51_PARSE_PASS`, exit 0); parsing is
neither execution nor security qualification.

## Media disposition

The official Windows evaluation ISO download completed independently of VM admission.
The downloader exited 0 after checking the full file against the size and the
independently read official Microsoft hash bound in the action. Unfiltered output:

```text
ISO_VERIFIED_SHA256=89626da8fdfdd8d03c31bc911bc525145c9e07e3a5f1c299e0645f0ab7e38096
ISO_VERIFIED_BYTES=7335473152
```

The verified media remains in the declared user-local cache. This is acquisition
evidence only; the protected-copy check is still required before future attachment.
No media is attached and no VM was started by this action.

## Convergence and next decision

[CodeReview section 5](../../../CodeReview.md#5-結論與收斂) allows one initial plus
one correction review for a Closure revision. Both are exhausted with ENV-F2 open.
No third correction, new helper, silent alternative provisioning method or automatic
cleanup is admitted. Preserve both candidate commits and the rejected recipe.

The smallest proposed continuation is an **owner-scoped single-use override** for
ENV-F2 only, as allowed by the ticket-set continuation rule: bind the protected OS
PowerShell/module identity, eliminate writable-location discovery and implicit
autoload across the elevated command's dependencies, and include bootstrap failures
in the independent failure carrier. Prove rejection of an untrusted resolution
without running hostile code elevated, then perform one complete bounded review.
This is a proposal, not a corrected recipe or an approved executable closure. Do not
split this small operational fix into a new product framework or weaken isolation.

The existing authorization for exactly one disposable VM and guest-only test trust
remains valid. The additional owner decision concerns this single review-limit
exception, not renewed permission for the same VM. Only an approved corrected
recipe and verified media may resume the original effect. Another blocking return
stops again; it does not start an indefinite correction loop.

Return: `ACTION_COMPLETED` for evidence recording; VM provisioning remains
`BLOCKED / CONVERGENCE_REVIEW_REQUIRED`. Continuation: `WAIT_FOR_HUMAN` for the
named single-use override. No Windows or MSIX lifecycle qualification is claimed.
