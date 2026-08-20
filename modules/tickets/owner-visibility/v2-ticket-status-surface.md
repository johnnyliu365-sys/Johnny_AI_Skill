# V2 — Ticket Status Surface

| Field | Value |
| --- | --- |
| State | `OPEN` — split between two owners who work in parallel against one contract |
| Baseline | `main` at `c1bb040` (v0.4.5 released) |
| Workload | `STANDARD`; Python 3.11 strict, TDD, reverse mutation required |
| Supersedes | V1's content. V1 built a *worker* board; the owner asked for a *ticket* board. V1's mechanisms survive, its three lanes do not |
| Design | Approved by the owner: [`v2-approved-mockup.html`](v2-approved-mockup.html) |

## One outcome

The owner opens one page and can answer, without a terminal and without
reading a ticket file: **which ticket is at which stage, which commit it stands
at, and — if they have to take over — exactly what to hand a conversation.**

## Ownership split

The two halves meet at one document and never touch each other's files.

| Half | Owner | Files |
| --- | --- | --- |
| **UI** — the page | UI implementation owner (this ticket) | `library/local_orchestration/ticket_status_template.py` + its tests |
| **Pipeline** — the facts | Control plane | `library/local_orchestration/ticket_status_pipeline.py` + its tests |

The pipeline produces a plain `dict` (JSON-shaped, stdlib types only). The
template turns that dict into the page. Neither imports the other; the contract
below is the whole interface, so both halves can be built at the same time.

## The contract

A worked example of the exact document is committed beside this ticket:
[`v2-document-sample.json`](v2-document-sample.json). It carries real values
from this repository, so a renderer built against it is being tested on the
data it will actually receive.

```text
document
├─ generated_at   str   ISO 8601 with offset
├─ head           {branch: str, commit: str}
├─ release        {version: str, commit: str} | null
├─ rollback       {commit: str} | null
├─ tickets        [ticket, …]        ordered: NEEDS_OWNER first, then the rest
└─ unreadable     [{label, path, reason}, …]   sources that could not be read

ticket
├─ id              str        e.g. "V1", "E14"
├─ module          str        the ticket folder
├─ title           str
├─ state           "NEEDS_OWNER" | "IN_PROGRESS" | "DONE"
├─ why_waiting     str | null   present exactly when state is NEEDS_OWNER
├─ stages          [{ref: str, label: str, state: "DONE"|"OPEN"}, …]
├─ commit          {sha: str, subject: str} | null
├─ released_in     str | null
├─ ticket_path     str
└─ handoff_command str        ready to copy, nothing to fill in
```

Rules the template must honour:

- Every string in the document is **untrusted text** and must be escaped. Ticket
  titles and commit subjects come from files and from git; a subject containing
  `<script>` must render as characters, never as markup.
- Any field documented as nullable **will** be null in practice. A ticket with
  no commit yet, no release, and no stages must still render as a complete row.
- `unreadable` is not decoration. When it is non-empty the page must say so
  where the owner cannot miss it, because a short ticket list that is short
  *because a file would not parse* is the one failure this surface exists to
  prevent. See the note at the foot of this ticket.

## Scope for the UI owner

Start from `v2-approved-mockup.html` — the owner has already approved that
layout, palette, and density. Do not redesign it. Port it into
`ticket_status_template.py` as:

```python
def render(document: dict) -> str: ...
```

Requirements:

| Ref | Requirement | Evidence required |
| --- | --- | --- |
| V2-U1 | `render` reproduces the approved layout from the sample document | A cell that renders `v2-document-sample.json` and asserts the id, stage refs, commit sha and handoff command all appear |
| V2-U2 | Untrusted text is escaped | A cell rendering a title and a commit subject containing `<script>` and `"` and asserting neither reaches the output as markup |
| V2-U3 | Every nullable field may be null | A cell rendering a ticket with `commit`, `released_in`, `why_waiting` null and empty `stages`, asserting it still produces a complete row and does not raise |
| V2-U4 | A non-empty `unreadable` list is stated prominently | A cell asserting the page says so, and a reverse mutation that drops the block turns it red |
| V2-U5 | `NEEDS_OWNER` reads differently from `DONE` without reading words | Structural assertion on the distinguishing attribute or class, not on prose |
| V2-U6 | Stdlib only | An AST cell asserting no third-party import, matching `tests/test_owner_status_surface.py::DependencyTests` |
| V2-U7 | Light, dark, and the unstamped "system" state all resolve | Every colour defined as a token on bare `:root`; no colour whose only definition sits inside a media query or `[data-theme]` block; `body` paints an explicit token background |

Also required, and cheap: the page must open correctly by double-click from
Explorer (`file://`), so no build step, no fetch, no ES modules, and every
style inline.

Out of scope for the UI owner: reading git, parsing tickets, deciding a
ticket's state, or writing the file to disk. Those are the pipeline's, and
touching them will collide with work happening in parallel.

## Scope for the pipeline owner (control plane)

Produce the document from real sources, and never infer a status from prose.

The state of a ticket must come from a **declared, machine-readable block** in
the ticket file itself, not from parsing English sentences in its State row. A
ticket without that block is reported in `unreadable` — it is never guessed at.
This is the same rule the wake channel lives by: read what the source actually
said, or say you could not.

Commit and subject come from `git log -1` over the ticket's own path, so
"where does this stand" is answered by the repository rather than by a human
remembering to update a line.

## The rule that outranks the layout

**A short list must never be short because something failed to parse.**

If the pipeline cannot read three ticket files, the page shows the tickets it
could read *and* says plainly that three are missing and why. An owner who
glances at a five-row page and sees no `NEEDS_OWNER` row will stop watching;
if two of the missing three were waiting on them, this page has done more
damage than no page at all.

This is the same defect as
`modules/tickets/workflow-governance/04-skill-implies-a-runtime-that-may-not-exist.md`,
where narrating an unperformed wake cost the owner their trust in the system.
Read `modules/tickets/PITFALL-REGISTER.md` before starting; family C is this
failure in its other costumes.

## 狀態宣告

這個區塊是工單狀態頁唯一讀取的來源。改狀態就改這裡；不要期待任何工具去讀上面的英文句子。

```johnny-status
id = V2
title = 工單狀態頁
state = IN_PROGRESS
stage = D | 設計核准 | DONE
stage = U | UI 樣板 | OPEN
stage = P | 資料管線 | OPEN
stage = W | 接線 | OPEN
```
