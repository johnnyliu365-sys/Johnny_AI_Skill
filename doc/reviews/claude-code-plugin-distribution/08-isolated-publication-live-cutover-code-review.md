# Ticket 08 code review — isolated publication live cutover

| Field | Value |
| --- | --- |
| Ticket / closure | `claude-code-plugin-distribution/08-isolated-publication-live-cutover` / `CLOSURE_01` |
| Reviewer profile | Terra / `xhigh` |
| Source baseline / candidate | `3089b460f312e4401e7e1e47e533a407f1be3bf7` / `c4a08809868997ac5968e6d242652e050b54145e` |
| Reviewer pin commit | `1a536fb781644d79a5b34735839f48a1c5e8c1fa` |
| Generated root | `758a7187f6cee5dbb231cd85fe2c4f5d3e03f4b3` |
| Verdict | `BLOCKED / TICKET_DEFECT / UPSTREAM_CLOSURE_CONTRACT` |

## Admission and pre-effect evidence

The candidate descended from the reviewed baseline, touched exactly the six declared paths, and
the ticket leaf/registry owner-authority state was reconciled before effect admission. Its source
review passed. The reviewer confirmed the authorized publication repository was absent, created
it public with default branch `main`, and read back an empty ref set. The temporary development
raw ref was absent.

The generator produced and reproduced the exact parentless root above, and wrote the permitted
marketplace pin in reviewer commit `1a536fb7`. Generator verification passed. No SHA was hand
edited.

## Blocking L2 result

The Ticket 06 repository closure check for the generated root returned
`PublicationClosureStatus.TREE_MISMATCH`, with the sole mismatch
`.claude-plugin/marketplace.json`. `write_publication_commit()` deliberately neutralizes its
self-referential pin carrier while constructing the root; `payload_from_manifest()` subsequently
expects the live candidate's generated pin blob, and the closure checker has no symmetric
pin-carrier treatment. L2 therefore cannot become `VERIFIED` for the required artifact.

This is a defect in the upstream closure contract. Ticket 08 forbids modifying the closure module
or weakening L2, so a reviewer may not continue to remote `main`/tag publication, candidate raw
ref push, isolated Claude install, source integration or source-main push.

## External-state readback

The authorized publication repository exists but remains empty. No payload, `main`, release tag
or temporary development ref was pushed. No Claude CLI/cache action occurred. Development
`main` remains `3089b460f312e4401e7e1e47e533a407f1be3bf7`. The only external action was the
authorized creation of the empty public repository; deletion is not implied by the authority and
was not attempted.

## CLOSURE 02 live-cutover evidence — blocked L4

The candidate `055d4d2478103420bc69ec7e46f6ddfc921fb0e5` descended from its re-admitted
development baseline `136bc2c6807de3b898fc2144a061ecc531e39af9`, changed exactly the six
admitted source paths, and generated root
`b52215eb3ee5dfa101e65c189441e62c20ca45e6`. The focused closure suite passed with 121 tests
and 582 subtests, strict mypy passed, and the generator's verify-only readback passed.

The reviewer then published that root to the authorized public repository's `main` and immutable
`plugin-v0.4.10` tag using the ticket-07 plan, read back both refs at that exact root, and
independently verified the remote root/tree/ref closure. The candidate was pushed only to its
authorized temporary raw ref. A fresh disposable `CLAUDE_CONFIG_DIR` installed the plugin from
the immutable raw candidate descriptor; marketplace and installed-plugin readback reported
`johnny-ai-skill` enabled at version `0.4.10`, with checkout `HEAD` equal to the generated root.

L4 is nevertheless red. The actual installed clone exposes these refs at that root:
`refs/heads/main`, `refs/remotes/origin/main`, `refs/remotes/origin/HEAD` and
`refs/tags/plugin-v0.4.10`; the third is a normal symbolic ref to
`refs/remotes/origin/main`. `verify_installed_plugin_cache()` returns
`INSTALLED_REF_SET_INVALID`, because its parser treats any symbolic ref as invalid before tree
closure can run. This is not a safe success: Ticket 08 requires every actual cache ref and
reachable commit to be accepted and independently reverse-mutated.

Ticket 08 forbids the required module, so the reviewer did not integrate the candidate or push
development `main`. The public publication `main`/tag and temporary candidate ref are retained
as authorized, read-back external state; no ref was moved or deleted. The correct continuation
is a separate bounded corrective ticket for the installed-cache closure contract, followed by a
fresh Ticket 08 re-admission and complete L1–L6 readback.
