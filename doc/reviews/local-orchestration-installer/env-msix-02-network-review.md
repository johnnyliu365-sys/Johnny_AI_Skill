# ENV-MSIX-02 — Temporary activation network operational review

| Field | Value |
| --- | --- |
| Artifact / kind / revision | `REVIEW-ENV-MSIX-02-20260906` / `OPERATIONAL_READINESS_REVIEW` / `02` |
| Candidate / baseline | `1b4e80c0ac3c1cd06948c5f6d569218a9cb45de1` / `b140e5bf3d47d0e1a3736dd87340c1e693ff70de` |
| Ticket / digest | [ENV-MSIX-02](../../../modules/tickets/local-orchestration-installer/env-msix-02-temporary-evaluation-activation.md), revision 02; `80da6236da12b2524b84d602824d5be79e3c84bb35a545269d1fed730feff28a` |
| Closure / authority | `CLOSURE-ENV-MSIX-02/01`; owner's 2026-09-06 temporary VM activation-network grant |
| Reviewer conclusion | `APPROVED / NETWORK_CONNECTED / OWNER_GUEST_ACTIVATION_REQUIRED` |
| Runtime/bootstrap source | ENV-MSIX-01 marked bootstrap at `f3e77eed6da2fa85b2e115508776f1b3dc311c74`; no provisioning body |
| Scope | Current-session operator only; no product implementation, host trust, release or push |

## Independent disposition

The mandatory existing Terra/xhigh helper returned FINDINGS on both initial and
correction candidates. This report does **not** relabel its return NO_FINDINGS.
The parent independently classifies findings under CodeReview section 4 and owns
the final operational admission.

1. **ENV2-F1 / IMPLEMENTATION_DEFECT — closed.** Initial candidate `15eedd726e3fa1d23f80170b6381498ecf4fa2c0`
   used one fixed disconnect report, blocking replay/recovery at CreateNew.
   Revision 02 requires a fresh typed observation GUID. The native-file tests below
   retain prior files, reject the same GUID with zero fake effects, repeat the
   already-disconnected observation with a new GUID, inject report-write failure
   (exit 44), and then obtain a new successful disconnect record. This was the one
   bounded correction; no additional correction is authorized.
2. **ENV2-F2 / OUT_OF_SCOPE_HARDENING — reproduced, not fixed.** ValidateSet accepts
   mixed case, and `-Action Disconnect` with an empty GUID reaches a disconnect
   through the fallback branch. The fake reproduction is retained below. This would
   be a blocking defect in a callable general-purpose network API. It is **not an
   admitted input** to this operational record: frozen closure 2 allows only the
   literal terminal `Invoke-LabNetworkAction CONNECT`, or the literal uppercase
   `Invoke-LabNetworkAction -Action DISCONNECT -DisconnectAttempt <fresh-guid>`.
   The privileged child receives the exact committed bootstrap/body plus one of
   those terminals; it exposes no API, stdin command channel, module export,
   argument forwarding, provider input or persistent service. Action text is not
   supplied by the owner or another agent. Non-allowlisted terminal text must not
   be submitted. Under that already-frozen invocation boundary, this case cannot
   occur without changing the admitted script itself. No closure or trust boundary
   is weakened, and no third correction is performed. Any future reuse as an
   API/tool must first replace the action-string convention with a closed enum or
   exact validation, and undergo its own review.

## Verification and applicability

- Actual protected-OS preflight used the reviewed bootstrap, exited 0, and emitted
  the fresh exact VM/adapter and existing-switch metadata in
  `C:\ProgramData\JohnnyActivationPreflight-20260906-8056c424.json`.
  The earlier exit-46 probe refused before network effects at an unexpectedly
  expanded VM-root ACL. ACL provenance remains unproved; no ACL relaxation or
  VM-root write is part of this action.
- Sixteen unmutated candidate cases meet their expected results; one independent
  VM-name-guard reverse mutation is RED and exact restoration is GREEN. A separate
  mixed-case probe reproduces ENV2-F2; it is not counted as a passing safety test.
- The harness shadows all Hyper-V effect/read commands with in-memory fake
  functions. It runs under a normal token and never elevates or connects a VM.
  Its native CreateNew files live in a fresh temporary directory, with ordinary
  user permissions. Thus the carrier-collision behavior is real, but the test does
  **not** pretend to prove the production protected-file ACL or real connectivity.
  The protected FileStream constructor/ACL was separately exercised by the actual
  preflight result creation; fresh native post-effect observation remains required.
- Exact unmodified CONNECT composition is 25,768 encoded characters and parses in
  Windows PowerShell 5.1. The parser receives its source via stdin; the elevated
  effect uses the bound EncodedCommand, never a writable external script.
- Closure 1/2: wrong VM, adapter, switch, initial state and integrations refuse;
  source/pins and fixed uppercase composition are inspected independently.
  Closure 3/4: trusted bootstrap/protected reporter, effect/readback failures,
  single rollback and unresolved recovery all remain explicit.
  Closure 5/6: guest activation is owner-executed, with no guest credentials,
  remote shell, polling, automatic wake or claimed activation result.
  Closure 7: fresh observation/replay/failed-carrier recovery tests below; actual
  final disconnect readback is still pending.
- Alternatives: continued offline activation is not demonstrated; creating a new
  external switch/NAT or expanding sharing is unnecessary and excluded. Reuse the
  observed existing Default Switch only. Ordinary switch connectivity is not a
  destination firewall; incidental guest traffic during the window is possible.
- SQL/data migration, tenant/RLS, product UI/XSS, production accounts, application
  rollback, package update/removal, signing and deployment are excluded by the
  ticket's environment-only scope. No product suite or MSIX-readiness claim is made.

## Reproducible reviewer command

Run from the repository in a normal, non-elevated PowerShell session. This diagnostic
creates only a fresh temporary output directory/files and starts short-lived normal
PowerShell children. It never invokes real Hyper-V commands after importing modules.
The source pin and projections are explicit; no files are deleted.

```powershell
$ErrorActionPreference='Stop'
$pin='1b4e80c0ac3c1cd06948c5f6d569218a9cb45de1'
$leaf=(git show ($pin+':modules/tickets/local-orchestration-installer/env-msix-02-temporary-evaluation-activation.md')) -join [char]10
$body=[regex]::Match($leaf,'(?s)\x60{3}powershell\n(.*?)\n\x60{3}').Groups[1].Value
$old=(git show 'f3e77eed6da2fa85b2e115508776f1b3dc311c74:modules/tickets/local-orchestration-installer/env-msix-01-disposable-hyper-v.md') -join [char]10
$oldBody=[regex]::Match($old,'(?s)\x60{3}powershell\n(.*?)\n\x60{3}').Groups[1].Value
$end=$oldBody.IndexOf('# ENV_F2_BOOTSTRAP_END')
$bootstrap=$oldBody.Substring(0,$end+'# ENV_F2_BOOTSTRAP_END'.Length)
$testRoot=Join-Path ([IO.Path]::GetTempPath()) ('johnny-env2-review-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testRoot | Out-Null
"TEST_ROOT=$testRoot"
$openLine='        $stream = [IO.FileStream]::new($reportPath,[IO.FileMode]::CreateNew,[Security.AccessControl.FileSystemRights]::Write,[IO.FileShare]::None,4096,[IO.FileOptions]::WriteThrough,$fileSecurity)'
if (-not $body.Contains($openLine)) { throw 'OUTPUT_SEAM_MISSING' }
$projected=$body.Replace($openLine,'        $stream = [IO.File]::Open($reportPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)')
$projected=$projected.Replace('C:\ProgramData\JohnnyActivationNetwork-20260906-',($testRoot+'\report-'))
$projected=$projected.Replace('$stream.Flush($true)','$stream.Flush($true); [Console]::WriteLine(($result | ConvertTo-Json -Compress))')
$projected=$projected.Replace('    exit $code','    [Console]::WriteLine("FAKE_EFFECTS connect="+$script:connectCount+" disconnect="+$script:disconnectCount); exit $code')
$fake=@'
$script:connectCount=0
$script:disconnectCount=0
$script:mockVm=[pscustomobject]@{Name='Johnny-MSIX-Lab-20260905';State='Running'}
$script:mockAdapter=[pscustomobject]@{Id='Microsoft:7701B26B-5B5A-42C0-B1E1-36D34DFDAA46\6BF8439D-9DE5-48C6-83E2-A368C38F8648';Connected=$false;SwitchId=$null}
$script:mockSwitch=[pscustomobject]@{Name='Default Switch';SwitchType='Internal';Id=[guid]'c08cb7b8-9b3c-408e-8e30-5e16a3aeb444'}
function Get-VM { param($Id) return $script:mockVm }
function Get-VMNetworkAdapter { param($VM) return $script:mockAdapter }
function Get-VMIntegrationService { param($VM) return [pscustomobject]@{Enabled=($script:caseName -eq 'integrations_enabled')} }
function Get-VMSwitch { param($Id) if ($script:caseName -eq 'disconnect_missing_switch') {throw 'SWITCH_MISSING'}; return $script:mockSwitch }
function Connect-VMNetworkAdapter {
 param($VMNetworkAdapter,$VMSwitch,$Confirm)
 $script:connectCount++
 $script:mockAdapter.Connected=$true
 $script:mockAdapter.SwitchId=$script:mockSwitch.Id
 if ($script:caseName -in @('connect_failure','rollback_failure')) {throw 'SIMULATED_CONNECT_FAILURE'}
 if ($script:caseName -eq 'bad_readback') {$script:mockAdapter.SwitchId=[guid]::Empty}
}
function Disconnect-VMNetworkAdapter {
 param($VMNetworkAdapter,$Confirm)
 $script:disconnectCount++
 if ($script:caseName -eq 'rollback_failure') {throw 'SIMULATED_DISCONNECT_FAILURE'}
 $script:mockAdapter.Connected=$false
 $script:mockAdapter.SwitchId=$null
}
switch ($script:caseName) {
 'wrong_vm' {$script:mockVm.Name='OtherVM'}
 'mutation_wrong_vm' {$script:mockVm.Name='OtherVM'}
 'wrong_adapter' {$script:mockAdapter.Id='OtherAdapter'}
 'already_connected' {$script:mockAdapter.Connected=$true;$script:mockAdapter.SwitchId=$script:mockSwitch.Id}
 'wrong_switch' {$script:mockSwitch.Name='WSL'}
 'disconnect_missing_switch' {$script:mockVm.State='Off';$script:mockAdapter.Connected=$true;$script:mockAdapter.SwitchId=$script:mockSwitch.Id}
}
'@
$repeatGuid=[guid]::NewGuid()
$failureGuid=[guid]::NewGuid()
$cases=@(
 @('connect_success','CONNECT',0,'CONNECTED_OWNER_ACTIVATION_REQUIRED',[guid]::Empty),
 @('wrong_vm','CONNECT',42,'BLOCKED',[guid]::Empty),
 @('wrong_adapter','CONNECT',42,'BLOCKED',[guid]::Empty),
 @('already_connected','CONNECT',42,'BLOCKED',[guid]::Empty),
 @('wrong_switch','CONNECT',42,'BLOCKED',[guid]::Empty),
 @('integrations_enabled','CONNECT',42,'BLOCKED',[guid]::Empty),
 @('connect_failure','CONNECT',42,'BLOCKED_DISCONNECTED',[guid]::Empty),
 @('bad_readback','CONNECT',42,'BLOCKED_DISCONNECTED',[guid]::Empty),
 @('rollback_failure','CONNECT',42,'RECOVERY_REQUIRED',[guid]::Empty),
 @('disconnect_already_offline','DISCONNECT',0,'DISCONNECTED_ACTIVATION_SEPARATE',$repeatGuid),
 @('disconnect_missing_switch','DISCONNECT',0,'DISCONNECTED_ACTIVATION_SEPARATE',[guid]::NewGuid()),
 @('disconnect_fresh_observation','DISCONNECT',0,'DISCONNECTED_ACTIVATION_SEPARATE',[guid]::NewGuid()),
 @('disconnect_guid_replay','DISCONNECT',42,'',$repeatGuid),
 @('disconnect_carrier_failure','DISCONNECT',44,'',$failureGuid),
 @('disconnect_after_failed_carrier','DISCONNECT',0,'DISCONNECTED_ACTIVATION_SEPARATE',[guid]::NewGuid()),
 @('mutation_wrong_vm','CONNECT',42,'BLOCKED',[guid]::Empty),
 @('restored_wrong_vm','CONNECT',42,'BLOCKED',[guid]::Empty),
 @('outside_scope_mixed_case','Disconnect',0,'DISCONNECTED_ACTIVATION_SEPARATE',[guid]::Empty)
)
foreach ($case in $cases) {
 $caseBody=$projected
 if ($case[1] -ceq 'CONNECT') {
  $caseBody=$caseBody.Replace("'-01.json'","'-$($case[0]).json'")
 }
 if ($case[0] -eq 'mutation_wrong_vm') {
  $guard='        if ($boundVm.Name -cne ''Johnny-MSIX-Lab-20260905'') { throw ''VM_IDENTITY_MISMATCH'' }'
  if (-not $caseBody.Contains($guard)) {throw 'MUTATION_SEAM_MISSING'}
  $caseBody=$caseBody.Replace($guard,'        # reverse mutation: VM name guard removed')
 }
 if ($case[0] -eq 'disconnect_carrier_failure') {
  $caseBody=$caseBody.Replace('            $stream.Write($bytes,0,$bytes.Length)','            $stream.Dispose(); $stream.Write($bytes,0,$bytes.Length)')
 }
 $caseName=$case[0]
 if ($caseName -eq 'restored_wrong_vm') {$caseName='wrong_vm'}
 $scriptText=$bootstrap+[char]10+'$script:caseName='''+$caseName+''' '+[char]10+$fake+[char]10+$caseBody+[char]10+'Invoke-LabNetworkAction -Action '+$case[1]+" -DisconnectAttempt '"+$case[4].ToString()+"'"
 $encoded=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($scriptText))
 $raw=(& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoLogo -NoProfile -NonInteractive -EncodedCommand $encoded 2>&1 | Out-String).Trim()
 $actual=$LASTEXITCODE
 "CASE=$($case[0]) EXPECT_EXIT=$($case[2]) ACTUAL_EXIT=$actual"
 $raw
 $pass=($actual -eq $case[2] -and ($case[3] -eq '' -or $raw.Contains('"Status":"'+$case[3]+'"')))
 if ($case[0] -eq 'mutation_wrong_vm') {if ($pass) {throw 'ZERO_RED_MUTATION'}; 'EXPECTED_RED'}
 elseif (-not $pass) {throw "FAILED:$($case[0])"}
 elseif ($case[0] -eq 'outside_scope_mixed_case') {'REPRODUCED_HELPER_CASE_OUTSIDE_FIXED_TERMINAL'}
 else {'GREEN'}
}
$exact=$bootstrap+[char]10+$body+[char]10+'Invoke-LabNetworkAction CONNECT'
$exactB64=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($exact))
"EXACT_ENCODED_LENGTH=$($exactB64.Length)"
$parser='$s=[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('''+$exactB64+'''));$e=$null;$t=$null;[Management.Automation.Language.Parser]::ParseInput($s,[ref]$t,[ref]$e)|Out-Null;if($e.Count){exit 2};[Console]::WriteLine(''EXACT_PS51_PARSE_PASS'');exit 0'
$psi=[Diagnostics.ProcessStartInfo]::new()
$psi.FileName='C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$psi.Arguments='-NoLogo -NoProfile -NonInteractive -Command -'
$psi.UseShellExecute=$false
$psi.CreateNoWindow=$true
$psi.RedirectStandardInput=$true
$psi.RedirectStandardOutput=$true
$psi.RedirectStandardError=$true
$p=[Diagnostics.Process]::Start($psi)
$p.StandardInput.WriteLine($parser)
$p.StandardInput.Close()
$p.StandardOutput.ReadToEnd()
$p.StandardError.ReadToEnd()
$p.WaitForExit()
"PARSE_EXIT=$($p.ExitCode)"
if ($p.ExitCode -ne 0) {throw 'PARSE_FAILED'}
"RETAINED_TEST_FILES=$(@(Get-ChildItem -LiteralPath $testRoot -File).Count)"

```

## Unreduced candidate verification output

```text
TEST_ROOT=C:\Users\GameBoy\AppData\Local\Temp\johnny-env2-review-c5efc9b55b9e4471a44a01cc45486672
CASE=connect_success EXPECT_EXIT=0 ACTUAL_EXIT=0
{"Action":"CONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"00000000-0000-0000-0000-000000000000","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"CONNECTED_OWNER_ACTIVATION_REQUIRED","Connected":true,"Failure":null,"TimestampUtc":"2026-09-05T19:57:19.2520977Z"}
FAKE_EFFECTS connect=1 disconnect=0
GREEN
CASE=wrong_vm EXPECT_EXIT=42 ACTUAL_EXIT=42
{"Action":"CONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"00000000-0000-0000-0000-000000000000","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"BLOCKED","Connected":null,"Failure":"VM_IDENTITY_MISMATCH","TimestampUtc":"2026-09-05T19:57:22.2155258Z"}
FAKE_EFFECTS connect=0 disconnect=0
GREEN
CASE=wrong_adapter EXPECT_EXIT=42 ACTUAL_EXIT=42
{"Action":"CONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"00000000-0000-0000-0000-000000000000","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"BLOCKED","Connected":null,"Failure":"ADAPTER_IDENTITY_MISMATCH","TimestampUtc":"2026-09-05T19:57:25.2242824Z"}
FAKE_EFFECTS connect=0 disconnect=0
GREEN
CASE=already_connected EXPECT_EXIT=42 ACTUAL_EXIT=42
{"Action":"CONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"00000000-0000-0000-0000-000000000000","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"BLOCKED","Connected":null,"Failure":"INITIAL_STATE_MISMATCH","TimestampUtc":"2026-09-05T19:57:28.2838179Z"}
FAKE_EFFECTS connect=0 disconnect=0
GREEN
CASE=wrong_switch EXPECT_EXIT=42 ACTUAL_EXIT=42
{"Action":"CONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"00000000-0000-0000-0000-000000000000","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"BLOCKED","Connected":null,"Failure":"SWITCH_IDENTITY_MISMATCH","TimestampUtc":"2026-09-05T19:57:31.0705699Z"}
FAKE_EFFECTS connect=0 disconnect=0
GREEN
CASE=integrations_enabled EXPECT_EXIT=42 ACTUAL_EXIT=42
{"Action":"CONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"00000000-0000-0000-0000-000000000000","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"BLOCKED","Connected":null,"Failure":"INTEGRATION_STATE_MISMATCH","TimestampUtc":"2026-09-05T19:57:34.0339197Z"}
FAKE_EFFECTS connect=0 disconnect=0
GREEN
CASE=connect_failure EXPECT_EXIT=42 ACTUAL_EXIT=42
{"Action":"CONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"00000000-0000-0000-0000-000000000000","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"BLOCKED_DISCONNECTED","Connected":false,"Failure":"SIMULATED_CONNECT_FAILURE","TimestampUtc":"2026-09-05T19:57:36.9203146Z"}
FAKE_EFFECTS connect=1 disconnect=1
GREEN
CASE=bad_readback EXPECT_EXIT=42 ACTUAL_EXIT=42
{"Action":"CONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"00000000-0000-0000-0000-000000000000","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"BLOCKED_DISCONNECTED","Connected":false,"Failure":"CONNECT_READBACK_MISMATCH","TimestampUtc":"2026-09-05T19:57:39.8872990Z"}
FAKE_EFFECTS connect=1 disconnect=1
GREEN
CASE=rollback_failure EXPECT_EXIT=42 ACTUAL_EXIT=42
{"Action":"CONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"00000000-0000-0000-0000-000000000000","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"RECOVERY_REQUIRED","Connected":null,"Failure":"SIMULATED_CONNECT_FAILURE","TimestampUtc":"2026-09-05T19:57:44.0003657Z"}
FAKE_EFFECTS connect=1 disconnect=1
GREEN
CASE=disconnect_already_offline EXPECT_EXIT=0 ACTUAL_EXIT=0
{"Action":"DISCONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"43814271-2d7f-4adb-a3ce-be4205e59775","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"DISCONNECTED_ACTIVATION_SEPARATE","Connected":false,"Failure":null,"TimestampUtc":"2026-09-05T19:57:46.8630860Z"}
FAKE_EFFECTS connect=0 disconnect=1
GREEN
CASE=disconnect_missing_switch EXPECT_EXIT=0 ACTUAL_EXIT=0
{"Action":"DISCONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"1ab739c1-cf17-4318-9f9d-cf87d1fd302d","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"DISCONNECTED_ACTIVATION_SEPARATE","Connected":false,"Failure":null,"TimestampUtc":"2026-09-05T19:57:49.5576449Z"}
FAKE_EFFECTS connect=0 disconnect=1
GREEN
CASE=disconnect_fresh_observation EXPECT_EXIT=0 ACTUAL_EXIT=0
{"Action":"DISCONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"bf135c62-6d04-41b8-b600-131ea916f5f5","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"DISCONNECTED_ACTIVATION_SEPARATE","Connected":false,"Failure":null,"TimestampUtc":"2026-09-05T19:57:52.5154603Z"}
FAKE_EFFECTS connect=0 disconnect=1
GREEN
CASE=disconnect_guid_replay EXPECT_EXIT=42 ACTUAL_EXIT=42
FAKE_EFFECTS connect=0 disconnect=0
GREEN
CASE=disconnect_carrier_failure EXPECT_EXIT=44 ACTUAL_EXIT=44
FAKE_EFFECTS connect=0 disconnect=1
GREEN
CASE=disconnect_after_failed_carrier EXPECT_EXIT=0 ACTUAL_EXIT=0
{"Action":"DISCONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"124a29d6-66c9-4a7d-9e4f-f58a9e548470","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"DISCONNECTED_ACTIVATION_SEPARATE","Connected":false,"Failure":null,"TimestampUtc":"2026-09-05T19:58:01.7418625Z"}
FAKE_EFFECTS connect=0 disconnect=1
GREEN
CASE=mutation_wrong_vm EXPECT_EXIT=42 ACTUAL_EXIT=0
{"Action":"CONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"00000000-0000-0000-0000-000000000000","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"CONNECTED_OWNER_ACTIVATION_REQUIRED","Connected":true,"Failure":null,"TimestampUtc":"2026-09-05T19:58:04.6321421Z"}
FAKE_EFFECTS connect=1 disconnect=0
EXPECTED_RED
CASE=restored_wrong_vm EXPECT_EXIT=42 ACTUAL_EXIT=42
{"Action":"CONNECT","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"00000000-0000-0000-0000-000000000000","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"BLOCKED","Connected":null,"Failure":"VM_IDENTITY_MISMATCH","TimestampUtc":"2026-09-05T19:58:07.4685840Z"}
FAKE_EFFECTS connect=0 disconnect=0
GREEN
CASE=outside_scope_mixed_case EXPECT_EXIT=0 ACTUAL_EXIT=0
{"Action":"Disconnect","Correlation":"EVAL-ACTIVATE-20260906-01","DisconnectAttempt":"00000000-0000-0000-0000-000000000000","VMId":"7701b26b-5b5a-42c0-b1e1-36d34dfdaa46","Status":"DISCONNECTED_ACTIVATION_SEPARATE","Connected":false,"Failure":null,"TimestampUtc":"2026-09-05T19:58:10.3259342Z"}
FAKE_EFFECTS connect=0 disconnect=1
REPRODUCED_HELPER_CASE_OUTSIDE_FIXED_TERMINAL
EXACT_ENCODED_LENGTH=25768
EXACT_PS51_PARSE_PASS


PARSE_EXIT=0
RETAINED_TEST_FILES=17

```

## Return

`ACTION_COMPLETED`: operational review only. `AUTO_CONTINUE` to the one exact
uppercase CONNECT composition under the existing owner grant, followed by
`WAIT_FOR_HUMAN / OWNER_GUEST_ACTIVATION_REQUIRED`. Either guest success or failure
routes to the exact uppercase DISCONNECT with a fresh observation GUID. No live
network/activation effect has occurred at this admission record.

## Actual CONNECT result after admission

Admission commit `d9d4bb2a9456dedf2f5f807f93f3d2e4da8a9511` was clean before effect.
The operator submitted the exact reviewed bootstrap and revision-02 action block,
plus literal `Invoke-LabNetworkAction CONNECT`, through the specified hidden UAC
Windows PowerShell process. No action string was taken from user/provider input.

```text
NETWORK_CONNECT_SOURCE_SHA256=7ca2adbbc3cd2d0f48b8dac809152a4e1a76c6b2299681c8b16fef431a11eee5
NETWORK_CONNECT_EXIT=0
{
    "Action":  "CONNECT",
    "Correlation":  "EVAL-ACTIVATE-20260906-01",
    "DisconnectAttempt":  "00000000-0000-0000-0000-000000000000",
    "VMId":  "7701b26b-5b5a-42c0-b1e1-36d34dfdaa46",
    "Status":  "CONNECTED_OWNER_ACTIVATION_REQUIRED",
    "Connected":  true,
    "Failure":  null,
    "TimestampUtc":  "2026-09-05T20:00:41.5040131Z"
}
RESULT_RAW_SHA256=32e6f14ac7d37a2f3ae989f904e4b84c0dda33f925c6f6b29861a8902dfdfb92
```

Result: `C:\ProgramData\JohnnyActivationNetwork-20260906-connect-01.json`.
The parent independently read Action, Correlation, VMId, Status, Connected, Failure
and the raw file hash. This proves the adapter-to-switch connection at that readback,
not guest Internet reachability, successful activation or MSIX readiness.

Current continuation: `WAIT_FOR_HUMAN / OWNER_GUEST_ACTIVATION_REQUIRED`. The owner
has the guest-only `/ato` and `/xpr` commands. No guest password is requested or
captured. On either success or failure, execute the bound uppercase DISCONNECT with
a fresh observation GUID and read its exact result; do not rerun CONNECT. Networking
is currently enabled for this temporary window; no final-disconnection claim is made.
