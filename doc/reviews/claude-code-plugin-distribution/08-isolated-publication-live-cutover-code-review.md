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
