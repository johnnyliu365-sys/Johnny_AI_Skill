"""Turn the ticket status document into the one page the owner opens.

This module is the *page*, and nothing else. It reads no git, parses no ticket,
decides no ticket's state and writes no file. It receives the document the
pipeline produced -- plain JSON-shaped `dict`, stdlib types only -- and returns
the HTML string. Everything it knows, it was told.

Three rules shape every line below.

**Every string in the document is untrusted.** Titles come from files and
commit subjects come from `git log`; both are written by whoever last touched
the repository. A subject containing `<script>` renders as those characters,
never as markup, and that holds inside attribute values too, which is where
escaping is usually forgotten.

**Every nullable field will actually be null.** A ticket opened five minutes
ago has no commit, no release, and no stages. It must still render as a
complete row, and the absences must be *stated* rather than left as gaps --
"no commit yet" is a real answer, an empty space is an ambiguous one.

**A short list must never be short because something failed to parse.** When
`unreadable` is non-empty the page says so above the tickets, with a count, on
an inverted slab that no state row wears. An owner who glances at a short page
and sees no `NEEDS_OWNER` row will stop watching; if one of the sources that
failed held a ticket waiting on them, a page that stayed calm about it has
done more damage than no page at all. That is the defect in
`modules/tickets/workflow-governance/04-...` wearing a new costume, and family
C of the pitfall register is the rest of its wardrobe.

The layout and density come from `v2-approved-mockup.html`. The palette is the
owner's revision of it: they split "finished" from "accepted", fixed DONE to a
yellow ground, REJECTED to red and APPROVED to blue, and left the other two to
this module. NEEDS_OWNER therefore moved out of the mockup's amber, which sat
fourteen degrees of hue from the new yellow and would have made the two states
that matter most look alike. The unreadable slab moved off amber for the same
reason, and onto no hue at all, so it can never be read as a sixth state.
"""

from __future__ import annotations

import html
from datetime import datetime

_PAGE_TITLE = "Johnny 工單狀態"

# Five states, because finished is not accepted. DONE is work waiting for a
# verdict; APPROVED and REJECTED are the two verdicts. Collapsing DONE into
# APPROVED would hide the queue of work waiting on a review nobody has done,
# which is the whole reason the owner split them.
_STATE = {
    "NEEDS_OWNER": ("needs-owner", "等你決定"),
    "REJECTED": ("rejected", "未通過／須修正"),
    "DONE": ("done", "完成"),
    "IN_PROGRESS": ("in-progress", "進行中"),
    "APPROVED": ("approved", "已通過"),
}

# The two states a human has to clear. The contract requires a reason for both,
# so the block is drawn for both -- and says so when the reason is missing,
# rather than showing a row that says work failed without saying what to fix.
_REASON_STATES = ("NEEDS_OWNER", "REJECTED")
_WHY_LABEL = {"NEEDS_OWNER": "為什麼等你：", "REJECTED": "為什麼沒通過："}
_NO_REASON = "這一列沒有附原因。照契約這不該發生，請直接開工單檔確認。"

_STAGE_SLUG = {"DONE": "done", "OPEN": "open"}

# Absences the page states out loud rather than leaving as a gap.
_NO_TICKETS = "沒有工單——這是讀得到的來源給出的答案，不是猜的。"
_NO_COMMIT = "尚未有 commit"
_NO_STAGES = "尚未列出階段"
_NO_RELEASE = "尚未發行"
_NO_ROLLBACK = "尚無回滾點"

_FOOT = "每一列都來自 git 與工單檔本身。讀不到的來源會就地標示，不會靜靜地變成空白。"


def _esc(value: object) -> str:
    """Everything from the document goes through here, attributes included."""

    return html.escape("" if value is None else str(value), quote=True)


def _mapping(value: object) -> dict:
    """A nullable object field is a missing field, not a crash."""

    return value if isinstance(value, dict) else {}


def _sequence(value: object) -> list:
    return list(value) if isinstance(value, (list, tuple)) else []


def _text(value: object) -> str:
    return "" if value is None else str(value)


def _stamp(raw: object) -> tuple[str, str]:
    """Return (machine, human); the exact ISO text survives in the attribute.

    The offset the pipeline wrote is the offset displayed. Converting to this
    process's local zone would make the page say a different time depending on
    which machine rendered it, which is not a property a status page may have.
    """

    text = _text(raw)
    try:
        moment = datetime.fromisoformat(text)
    except (TypeError, ValueError):
        return text, text
    return text, moment.strftime("%Y-%m-%d %H:%M")


def _bar(document: dict) -> str:
    """The one strip that answers "which tree am I looking at"."""

    head = _mapping(document.get("head"))
    release = _mapping(document.get("release"))
    rollback = _mapping(document.get("rollback"))
    machine, human = _stamp(document.get("generated_at"))

    parts = [f'<div class="bar"><h1>{_esc(_PAGE_TITLE)}</h1>']
    parts.append(
        f'<span class="kv">{_esc(head.get("branch"))} '
        f'<code>{_esc(head.get("commit"))}</code></span>'
    )
    if release:
        parts.append(
            f'<span class="kv">發行 <b>{_esc(release.get("version"))}</b> '
            f'<code>{_esc(release.get("commit"))}</code></span>'
        )
    else:
        parts.append(f'<span class="kv">發行 <b>{_esc(_NO_RELEASE)}</b></span>')
    if rollback:
        parts.append(
            f'<span class="kv">回滾點 <code>{_esc(rollback.get("commit"))}</code></span>'
        )
    else:
        parts.append(f'<span class="kv">回滾點 <b>{_esc(_NO_ROLLBACK)}</b></span>')
    parts.append(
        '<span class="kv">更新於 <b>'
        f'<time datetime="{_esc(machine)}">{_esc(human)}</time></b></span>'
    )
    parts.append("</div>")
    return "".join(parts)


def _unreadable(sources: list) -> str:
    """The block that outranks the layout. Empty list, no block; never silent."""

    if not sources:
        return ""
    rows = []
    for source in sources:
        source = _mapping(source)
        rows.append(
            "<li>"
            f'<span class="src">{_esc(source.get("label"))}</span>'
            f'<code>{_esc(source.get("path"))}</code>'
            f'<span class="reason">{_esc(source.get("reason"))}</span>'
            "</li>"
        )
    return (
        f'<section class="unreadable" data-unreadable="{len(sources)}">'
        f"<h2>有 {len(sources)} 個來源讀不到，本頁不完整。</h2>"
        "<p>下面的工單清單短，可能是因為這些來源讀不到，"
        "<strong>不是因為沒事</strong>。少掉的工單裡可能就有在等你的。</p>"
        f'<ul>{"".join(rows)}</ul>'
        "</section>"
    )


def _stages(stages: list) -> str:
    chips = []
    for stage in stages:
        stage = _mapping(stage)
        ref = _text(stage.get("ref")).strip()
        label = _text(stage.get("label")).strip()
        caption = f"{ref} {label}".strip() if label else ref
        slug = _STAGE_SLUG.get(_text(stage.get("state")), "unknown")
        chips.append(f'<span class="st" data-s="{_esc(slug)}">{_esc(caption)}</span>')
    if not chips:
        chips.append(f'<span class="none">{_esc(_NO_STAGES)}</span>')
    return f'<div class="stages"><span class="lab">階段</span>{"".join(chips)}</div>'


def _where(ticket: dict) -> str:
    """Where the ticket stands. The commit cell is always drawn, even empty."""

    commit = _mapping(ticket.get("commit"))
    cells = []
    if commit:
        cells.append(
            '<div class="cell"><span class="lab">停在</span>'
            f'<span class="val">{_esc(commit.get("sha"))}</span>'
            f'<span class="sub">{_esc(commit.get("subject"))}</span></div>'
        )
    else:
        cells.append(
            '<div class="cell"><span class="lab">停在</span>'
            f'<span class="val" data-empty="yes">{_esc(_NO_COMMIT)}</span></div>'
        )
    released = ticket.get("released_in")
    if released:
        cells.append(
            '<div class="cell"><span class="lab">已發行於</span>'
            f'<span class="val">{_esc(released)}</span></div>'
        )
    path = ticket.get("ticket_path")
    if path:
        cells.append(
            '<div class="cell"><span class="lab">工單</span>'
            f'<span class="sub">{_esc(path)}</span></div>'
        )
    return f'<div class="where">{"".join(cells)}</div>'


def _why(state: str, reason: object) -> str:
    """The reason block, drawn for every state the contract requires one for.

    A REJECTED row that names no correction is the same defect as a calm page
    over an unread file: it tells the owner something failed and leaves them
    without the one thing they need to act. The pipeline refuses to emit that,
    so this states the gap loudly if one ever arrives anyway.
    """

    text = _text(reason).strip()
    if not text and state not in _REASON_STATES:
        return ""
    label = _WHY_LABEL.get(state, "為什麼：")
    if not text:
        return (
            f'<div class="why" data-missing="yes"><b>{_esc(label)}</b>'
            f"{_esc(_NO_REASON)}</div>"
        )
    return f'<div class="why"><b>{_esc(label)}</b>{_esc(text)}</div>'


def _ticket(ticket: object) -> str:
    ticket = _mapping(ticket)
    state = _text(ticket.get("state"))
    slug, caption = _STATE.get(state, ("unknown", state or "未標示狀態"))
    need = "yes" if state in _REASON_STATES else "no"

    identity = " · ".join(
        part
        for part in (_text(ticket.get("id")).strip(), _text(ticket.get("module")).strip())
        if part
    )

    parts = [
        f'<article class="ticket" data-state="{_esc(slug)}" data-need="{need}">'
    ]
    parts.append(
        f'<div class="who"><div class="id">{_esc(identity)}</div>'
        f'<p class="name">{_esc(ticket.get("title"))}</p></div>'
    )
    parts.append(f'<span class="badge" data-state="{_esc(slug)}">{_esc(caption)}</span>')
    parts.append(_stages(_sequence(ticket.get("stages"))))
    parts.append(_why(state, ticket.get("why_waiting")))
    parts.append(_where(ticket))

    handoff = ticket.get("handoff_command")
    if handoff:
        parts.append(
            '<div class="handoff"><span class="lab">要接手就把這行給對話</span>'
            f"<code>{_esc(handoff)}</code></div>"
        )
    parts.append("</article>")
    return "".join(parts)


# Ported from v2-approved-mockup.html. Every colour is a token on bare :root;
# the two dark blocks redefine those tokens and introduce none of their own, so
# light, dark, and the unstamped "system" state all resolve to a real value.
_STYLE = """
:root{
  --bg:#f2f3f5; --card:#ffffff; --strip:#e9ebef; --line:#d5d9e0;
  --ink:#12161c; --dim:#5c6672; --faint:#858e9a;
  --accent:#3a4fb8;
  --need:#8e2fb0; --need-bg:#f9ecfd;
  --rejected:#c0271f; --rejected-bg:#fdeceb;
  --done:#d9ae0f; --done-bg:#f7e496; --done-ink:#3a2c00;
  --approved:#2563c4;
  --open:#6b7683;
  --stage-done:#1d7a4a; --stage-open:#b4690e;
  --badge-ink:#ffffff;
  --alarm:#1b1f27; --alarm-ink:#f4f6f9; --alarm-dim:#aab4c0;
  --mono:ui-monospace,"Cascadia Mono",Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0f1216; --card:#171b21; --strip:#1d222a; --line:#2c333d;
    --ink:#e8ecf1; --dim:#98a2ad; --faint:#7a848f;
    --accent:#8b9bf0;
    --need:#dd9bf0; --need-bg:#2e1638;
    --rejected:#f08a8a; --rejected-bg:#3a1c1c;
    --done:#e3b53d; --done-bg:#3a300f; --done-ink:#241b00;
    --approved:#7fb0f8;
    --open:#7d8794;
    --stage-done:#4fbe86; --stage-open:#e3a544;
    --badge-ink:#12161c;
    --alarm:#e9edf3; --alarm-ink:#12161c; --alarm-dim:#545d69;
  }
}
:root[data-theme="dark"]{
  --bg:#0f1216; --card:#171b21; --strip:#1d222a; --line:#2c333d;
  --ink:#e8ecf1; --dim:#98a2ad; --faint:#7a848f;
  --accent:#8b9bf0;
  --need:#dd9bf0; --need-bg:#2e1638;
  --rejected:#f08a8a; --rejected-bg:#3a1c1c;
  --done:#e3b53d; --done-bg:#3a300f; --done-ink:#241b00;
  --approved:#7fb0f8;
  --open:#7d8794;
  --stage-done:#4fbe86; --stage-open:#e3a544;
  --badge-ink:#12161c;
  --alarm:#e9edf3; --alarm-ink:#12161c; --alarm-dim:#545d69;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Segoe UI","Microsoft JhengHei",system-ui,sans-serif;
  font-size:15px;line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding:22px 18px 44px;
  display:flex;flex-direction:column;gap:16px}

.bar{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 20px;
  background:var(--strip);border:1px solid var(--line);border-radius:7px;
  padding:11px 14px}
.bar h1{font-size:16px;margin:0;letter-spacing:.02em;margin-right:auto}
.bar .kv{font-size:12.5px;color:var(--dim);font-variant-numeric:tabular-nums}
.bar .kv b{color:var(--ink);font-weight:600}
.bar code{font-family:var(--mono);font-size:12px;color:var(--accent)}

/* Inverted slab on purpose. Every state row is a light card on a light ground
   (or dark on dark); this is the only element that flips, so it cannot be
   mistaken for a sixth state, and it stays unmistakable beside a yellow DONE
   row without spending one of the five state hues. */
.unreadable{background:var(--alarm);color:var(--alarm-ink);
  border:1px solid var(--alarm);border-radius:7px;padding:13px 15px}
.unreadable h2{font-size:14px;margin:0;color:var(--alarm-ink);
  letter-spacing:.02em}
.unreadable p{margin:6px 0 0;font-size:13px;color:var(--alarm-ink)}
.unreadable strong{color:var(--alarm-ink);text-decoration:underline;
  text-underline-offset:3px}
.unreadable ul{margin:9px 0 0;padding:0;list-style:none;
  display:flex;flex-direction:column;gap:6px}
.unreadable li{display:flex;flex-wrap:wrap;gap:2px 12px;align-items:baseline;
  min-width:0}
.unreadable .src{font-size:13px;font-weight:600;color:var(--alarm-ink)}
.unreadable code{font-family:var(--mono);font-size:11.5px;
  color:var(--alarm-dim);word-break:break-all}
.unreadable .reason{font-size:12.5px;color:var(--alarm-dim)}

.ticket{background:var(--card);border:1px solid var(--line);border-radius:7px;
  padding:14px 15px;display:grid;gap:11px;
  grid-template-columns:minmax(0,1fr) auto;align-items:start}
/* Three row treatments, so the five states separate at a glance: an edge bar
   for the two a human must clear, a filled ground for finished-awaiting-verdict,
   and a plain card for the two that want nothing. */
.ticket[data-state="needs-owner"]{border-color:var(--need);
  box-shadow:inset 3px 0 0 var(--need)}
.ticket[data-state="rejected"]{border-color:var(--rejected);
  box-shadow:inset 3px 0 0 var(--rejected)}
.ticket[data-state="done"]{background:var(--done-bg);border-color:var(--done)}

.who{grid-column:1;min-width:0}
.id{font-family:var(--mono);font-size:11.5px;color:var(--faint);
  letter-spacing:.06em}
.name{font-size:15px;font-weight:600;margin:1px 0 0;text-wrap:balance}
.badge{grid-column:2;grid-row:1;justify-self:end;font-size:12px;font-weight:700;
  padding:3px 10px;border-radius:4px;white-space:nowrap;
  background:var(--open);color:var(--badge-ink)}
.badge[data-state="needs-owner"]{background:var(--need)}
.badge[data-state="rejected"]{background:var(--rejected)}
/* Yellow is too light to carry white text on either ground, so this badge
   brings its own ink rather than losing its edge. */
.badge[data-state="done"]{background:var(--done);color:var(--done-ink)}
.badge[data-state="in-progress"]{background:var(--open)}
.badge[data-state="approved"]{background:var(--approved)}

.stages{grid-column:1 / -1;display:flex;flex-wrap:wrap;gap:5px;align-items:center}
.stages .lab{font-size:11px;color:var(--faint);margin-right:3px;
  letter-spacing:.05em}
.stages .none{font-size:11px;color:var(--faint)}
.st{font-family:var(--mono);font-size:11px;padding:2px 7px;border-radius:3px;
  border:1px solid var(--line);color:var(--dim)}
/* Stage chips are their own vocabulary: a stage being finished says nothing
   about the ticket's verdict, so they keep their own two tokens rather than
   borrowing a state colour and turning a DONE row yellow-on-yellow. */
.st[data-s="done"]{background:var(--stage-done);border-color:var(--stage-done);
  color:var(--badge-ink)}
.st[data-s="open"]{border-color:var(--stage-open);color:var(--stage-open);
  font-weight:700}

.where{grid-column:1 / -1;display:flex;flex-wrap:wrap;gap:6px 22px;
  border-top:1px dashed var(--line);padding-top:10px}
.cell{min-width:0}
.cell .lab{display:block;font-size:11px;color:var(--faint);letter-spacing:.05em}
.cell .val{font-family:var(--mono);font-size:12.5px;color:var(--ink)}
.cell .val[data-empty="yes"]{font-family:inherit;color:var(--faint)}
.cell .sub{font-size:12px;color:var(--dim)}

.handoff{grid-column:1 / -1;background:var(--strip);border:1px solid var(--line);
  border-radius:5px;padding:8px 10px;overflow-x:auto}
.handoff .lab{font-size:11px;color:var(--faint);letter-spacing:.05em}
.handoff code{display:block;margin-top:3px;font-family:var(--mono);
  font-size:12.5px;color:var(--ink);white-space:pre}

.why{grid-column:1 / -1;background:var(--strip);border:1px solid var(--line);
  border-radius:5px;padding:9px 11px;font-size:13px;color:var(--ink)}
.why b{color:var(--ink)}
[data-state="needs-owner"] .why{background:var(--need-bg);border-color:var(--need)}
[data-state="needs-owner"] .why b{color:var(--need)}
[data-state="rejected"] .why{background:var(--rejected-bg);
  border-color:var(--rejected)}
[data-state="rejected"] .why b{color:var(--rejected)}
.why[data-missing="yes"]{font-style:italic}

.empty{margin:0;color:var(--faint);font-size:13px}
.foot{color:var(--faint);font-size:12px;border-top:1px solid var(--line);
  padding-top:11px}
@media (max-width:640px){
  .ticket{grid-template-columns:1fr}
  .badge{grid-column:1;grid-row:auto;justify-self:start}
}
"""


def render(document: dict) -> str:
    """Render the whole page. Pure: same document in, same bytes out.

    The order of `tickets` is the pipeline's promise (NEEDS_OWNER first) and is
    reproduced exactly. Re-sorting here would put two different orderings in
    the system and make the contract untestable from either side.
    """

    document = _mapping(document)
    tickets = _sequence(document.get("tickets"))
    unreadable = _sequence(document.get("unreadable"))

    body = [_bar(document)]
    banner = _unreadable(unreadable)
    if banner:
        body.append(banner)
    body.extend(_ticket(ticket) for ticket in tickets)
    if not tickets and not unreadable:
        # Genuinely empty, and only ever said when nothing failed to parse.
        body.append(f'<p class="empty">{_esc(_NO_TICKETS)}</p>')
    body.append(f'<p class="foot">{_esc(_FOOT)}</p>')
    blocks = "\n".join(body)

    return (
        '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{_esc(_PAGE_TITLE)}</title>"
        f"<style>{_STYLE}</style></head><body>"
        f'<div class="wrap">{blocks}</div>'
        "</body></html>"
    )
