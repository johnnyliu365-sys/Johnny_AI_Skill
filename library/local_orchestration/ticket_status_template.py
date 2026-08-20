"""Render Owner ticket status from an already-built document map.

This file intentionally does not parse files or git; those facts are passed in as a
`dict` by `ticket_status_pipeline.py`.
"""

from __future__ import annotations

import html
import json
from datetime import datetime
from typing import Any


def _escape(value: Any) -> str:
    """Escape any value as plain text."""

    return html.escape(str(value), quote=True)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _format_time(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return _text(value)
        return parsed.strftime("%Y-%m-%d %H:%M")
    return _text(value)


def _state_display(state: str) -> str:
    if state == "NEEDS_OWNER":
        return "等你決定"
    if state == "DONE":
        return "已完成"
    return "進行中"


def _escape_or_empty(value: Any, fallback: str = "—") -> str:
    if value is None:
        return fallback
    return _text(value)

def _ticket_row(ticket: dict[str, Any]) -> str:
    ticket_id = _escape(_text(ticket.get("id", ""), "—"))
    module = _escape(_text(ticket.get("module", ""), "—"))
    title = _escape(_text(ticket.get("title", ""), "未命名"))
    state = _text(ticket.get("state", ""), "IN_PROGRESS")
    why_waiting = _escape(_text(ticket.get("why_waiting")))
    ticket_path = _escape(_text(ticket.get("ticket_path", ""), "—"))
    handoff_command = _escape(_text(ticket.get("handoff_command", ""), ""))

    head_states = {
        "NEEDS_OWNER": ("need", "need"),
        "DONE": ("done", "done"),
        "IN_PROGRESS": ("open", "open"),
    }
    state_class, state_id = head_states.get(state, ("open", "open"))

    commit = _as_dict(ticket.get("commit"))
    release = ticket.get("released_in")

    if commit:
        commit_sha = _escape(_text(commit.get("sha"), "—"))
        commit_subject = _escape(_text(commit.get("subject"), ""))
    else:
        commit_sha = "—"
        commit_subject = "未完成提交"

    if release is None:
        release_version = "未發行"
        release_subject = "—"
    else:
        release_map = _as_dict(release)
        release_version = _escape(_text(release_map.get("version"), "—"))
        release_subject = _escape(_text(release_map.get("commit"), ""))

    stages = _as_list(ticket.get("stages"))
    if not stages:
        stages_html = (
            '<span class="st" data-s="open">尚未定義</span>'
        )
    else:
        blocks = []
        for stage in stages:
            stage_obj = _as_dict(stage)
            ref = _escape(_text(stage_obj.get("ref", ""), "—"))
            label = _escape(_text(stage_obj.get("label", ""), ""))
            stage_state = _escape(_text(stage_obj.get("state", ""), "OPEN"))
            display = f"{ref} {label}".strip()
            if not display:
                display = ref
            sclass = "done" if stage_state == "DONE" else "open"
            blocks.append(f'<span class="st" data-s="{sclass}">{display}</span>')
        stages_html = "".join(blocks)

    why_block = (
        f'<div class="why"><b>為什麼等你：</b>{why_waiting}</div>'
        if state == "NEEDS_OWNER" and why_waiting
        else ""
    )

    return f"""
    <article class="ticket" data-state="{_escape(state)}">
      <div class="who">
        <div class="id">{ticket_id} · {module}</div>
        <p class="name">{title}</p>
      </div>
      <span class="badge" data-state="{state_class}">{_state_display(state)}</span>
      <div class="stages">
        <span class="lab">階段</span>
        {stages_html}
      </div>
      {why_block}
      <div class="where">
        <div class="cell">
          <span class="lab">停在</span>
          <span class="val">{commit_sha}</span>
          <span class="sub">{commit_subject}</span>
        </div>
        <div class="cell">
          <span class="lab">發佈</span>
          <span class="val">{release_version}</span>
          <span class="sub">{release_subject}</span>
        </div>
        <div class="cell">
          <span class="lab">工單</span>
          <span class="sub">{ticket_path}</span>
        </div>
      </div>
      <div class="handoff"><span class="lab">接手命令</span>
        <code>{handoff_command}</code>
      </div>
    </article>
    """


def _unreadable(unreadable: list[Any]) -> str:
    if not unreadable:
        return ""
    rows: list[str] = []
    for item in unreadable:
        block = _as_dict(item)
        rows.append(
            "<li>"
            f"<strong>{_escape(_text(block.get('label', ''))}</strong>："
            f"{_escape(_text(block.get('path', ''))}｜{_escape(_text(block.get('reason', '')))}"
            "</li>"
        )
    return f"""
    <section class="unread-banner" aria-live="polite">
      <h2>無法完整讀取來源</h2>
      <p>部分工單未被讀到，以下資料不是空白，而是待修正。</p>
      <ul>{''.join(rows)}</ul>
    </section>
    """


_STYLE = """
:root{
  --bg:#f2f3f5;
  --bg-dark:#0f1216;
  --card:#ffffff;
  --card-dark:#171b21;
  --strip:#e9ebef;
  --strip-dark:#1d222a;
  --line:#d5d9e0;
  --line-dark:#2c333d;
  --ink:#12161c;
  --ink-dark:#e8ecf1;
  --dim:#5c6672;
  --dim-dark:#98a2ad;
  --faint:#858e9a;
  --faint-dark:#7a848f;
  --accent:#3a4fb8;
  --accent-dark:#8b9bf0;
  --need:#b4690e;
  --need-dark:#e3a544;
  --done:#1d7a4a;
  --open:#6b7683;
  --done-dark:#4fbe86;
  --open-dark:#7d8794;
  --need-bg:#fdf3e3;
  --need-bg-dark:#2b2313;
  --mono:ui-monospace,"Cascadia Mono",Consolas,monospace;

  --surface-bg:var(--bg);
  --surface-card:var(--card);
  --surface-strip:var(--strip);
  --surface-line:var(--line);
  --surface-ink:var(--ink);
  --surface-dim:var(--dim);
  --surface-faint:var(--faint);
  --surface-accent:var(--accent);
  --surface-need:var(--need);
  --surface-need-bg:var(--need-bg);
  --surface-done:var(--done);
  --surface-open:var(--open);
}
:root[data-theme="dark"]{
  --surface-bg:var(--bg-dark);
  --surface-card:var(--card-dark);
  --surface-strip:var(--strip-dark);
  --surface-line:var(--line-dark);
  --surface-ink:var(--ink-dark);
  --surface-dim:var(--dim-dark);
  --surface-faint:var(--faint-dark);
  --surface-accent:var(--accent-dark);
  --surface-need:var(--need-dark);
  --surface-need-bg:var(--need-bg-dark);
  --surface-done:var(--done-dark);
  --surface-open:var(--open-dark);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    --surface-bg:var(--bg-dark);
    --surface-card:var(--card-dark);
    --surface-strip:var(--strip-dark);
    --surface-line:var(--line-dark);
    --surface-ink:var(--ink-dark);
    --surface-dim:var(--dim-dark);
    --surface-faint:var(--faint-dark);
    --surface-accent:var(--accent-dark);
    --surface-need:var(--need-dark);
    --surface-need-bg:var(--need-bg-dark);
    --surface-done:var(--done-dark);
    --surface-open:var(--open-dark);
  }
}
*{box-sizing:border-box}
body{margin:0;overflow-x:hidden;background:var(--surface-bg);color:var(--surface-ink);
  font-family:"Segoe UI","Microsoft JhengHei",system-ui,sans-serif;
  font-size:15px;line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding:22px 18px 44px;display:flex;flex-direction:column;gap:16px}
.top{display:flex;flex-wrap:wrap;align-items:center;gap:12px}
.bar{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 20px;background:var(--surface-strip);border:1px solid var(--surface-line);border-radius:7px;padding:11px 14px}
.bar h1{font-size:16px;margin:0;letter-spacing:.02em;margin-right:auto}
.bar .kv{font-size:12.5px;color:var(--surface-dim);font-variant-numeric:tabular-nums}
.bar .kv b{color:var(--surface-ink);font-weight:600}
.bar code{font-family:var(--mono);font-size:12px;color:var(--surface-accent)}
.toolbar{margin-left:auto;display:flex;align-items:center;gap:7px}
select{border-radius:999px;border:1px solid var(--surface-line);padding:4px 9px;background:var(--surface-card);color:var(--surface-ink);font:inherit}

.ticket{background:var(--surface-card);border:1px solid var(--surface-line);border-radius:7px;padding:14px 15px;display:grid;gap:11px;grid-template-columns:minmax(0,1fr) auto;align-items:start}
.ticket[data-state="NEEDS_OWNER"]{border-color:var(--surface-need)}
.ticket[data-state="DONE"]{border-color:var(--surface-done)}
.ticket[data-state="IN_PROGRESS"]{border-color:var(--surface-line)}
.who{grid-column:1;min-width:0}
.id{font-family:var(--mono);font-size:11.5px;color:var(--surface-faint);letter-spacing:.06em}
.name{font-size:15px;font-weight:600;margin:1px 0 0;text-wrap:balance}
.badge{grid-column:2;grid-row:1;justify-self:end;font-size:12px;font-weight:700;padding:3px 10px;border-radius:4px;white-space:nowrap;color:#fff}
.badge[data-state="need"]{background:var(--surface-need)}
.badge[data-state="done"]{background:var(--surface-done)}
.badge[data-state="open"]{background:var(--surface-open)}
.stages{grid-column:1 / -1;display:flex;flex-wrap:wrap;gap:5px;align-items:center}
.stages .lab{font-size:11px;color:var(--surface-faint);margin-right:3px;letter-spacing:.05em}
.st{font-family:var(--mono);font-size:11px;padding:2px 7px;border-radius:3px;border:1px solid var(--surface-line);color:var(--surface-dim)}
.st[data-s="done"]{background:var(--surface-done);border-color:var(--surface-done);color:#fff}
.st[data-s="open"]{border-color:var(--surface-need);color:var(--surface-need);font-weight:700}

.where{grid-column:1 / -1;display:flex;flex-wrap:wrap;gap:6px 22px;border-top:1px dashed var(--surface-line);padding-top:10px}
.cell{min-width:0}
.cell .lab{display:block;font-size:11px;color:var(--surface-faint);letter-spacing:.05em}
.cell .val{font-family:var(--mono);font-size:12.5px;color:var(--surface-ink)}
.cell .sub{font-size:12px;color:var(--surface-dim);word-break:break-all}

.handoff{grid-column:1 / -1;background:var(--surface-strip);border:1px solid var(--surface-line);border-radius:5px;padding:8px 10px}
.handoff .lab{font-size:11px;color:var(--surface-faint);letter-spacing:.05em}
.handoff code{display:block;margin-top:3px;font-family:var(--mono);font-size:12.5px;color:var(--surface-ink);white-space:pre}
.why{grid-column:1 / -1;background:var(--surface-need-bg);border:1px solid var(--surface-need);border-radius:5px;padding:9px 11px;font-size:13px}
.why b{color:var(--surface-need)}

.unread-banner{border:1px solid #ff6b6b;background:#fee; border-radius:7px;padding:12px;overflow-wrap:anywhere}
.unread-banner h2{margin:0 0 5px;font-size:16px}
.unread-banner p{margin:0 0 8px}
.unread-banner ul{margin:0;padding-left:18px}
.unread-banner li{margin:4px 0;color:var(--surface-ink)}

.foot{color:var(--surface-faint);font-size:12px;border-top:1px solid var(--surface-line);padding-top:11px}
@media (max-width:640px){
  .ticket{grid-template-columns:1fr}
  .badge{grid-column:1;grid-row:auto;justify-self:start}
}
"""


def render(document: dict[str, Any]) -> str:
    """Render ticket status surface from `document`."""

    doc = _as_dict(document)
    head = _as_dict(doc.get("head"))
    release = _as_dict(doc.get("release")) if doc.get("release") else {}
    rollback = _as_dict(doc.get("rollback"))

    generated_at = _format_time(doc.get("generated_at"))
    branch = _escape(_text(head.get("branch"), "—"))
    head_sha = _escape(_text(head.get("commit"), "—"))
    release_version = _escape(_text(release.get("version"), "—"))
    release_sha = _escape(_text(_as_dict(release).get("commit"), "—"))
    rollback_sha = _escape(_text(rollback.get("commit"), "—"))

    tickets = _as_list(doc.get("tickets"))
    rows = "".join(_ticket_row(_as_dict(ticket)) for ticket in tickets)
    unreadable_block = _unreadable(_as_list(doc.get("unreadable")))
    unreadable_note = (
        f'<p class="bar" role="status" aria-live="polite">無法完整讀取：{len(_as_list(doc.get("unreadable")))} 項。</p>'
        if _as_list(doc.get("unreadable"))
        else ""
    )

    return (
        '<!doctype html>'
        '<html lang="zh-Hant">'
        "<head>"
        '<meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width,initial-scale=1"/>'
        "<title>Johnny 工單狀態</title>"
        f"<style>{_STYLE}</style>"
        "</head>"
        "<body>"
        '<main class="wrap">'
        '<div class="bar">'
        "<h1>Johnny 工單狀態</h1>"
        f'<span class="kv">主分支 <code>{branch}</code> · {head_sha}</span>'
        f'<span class="kv">版本 <b>{release_version}</b> <code>{release_sha}</code></span>'
        f'<span class="kv">回滾點 <code>{rollback_sha}</code></span>'
        f'<span class="kv">更新於 <b>{generated_at}</b></span>'
        '<span class="toolbar"><label for="theme-select">介面主題</label>'
        '<select id="theme-select"><option value="system">系統</option><option value="light">淺色</option>'
        '<option value="dark">深色</option></select></span>'
        "</div>"
        f"{unreadable_note}"
        f"{unreadable_block}"
        f"{rows}"
        '<p class="foot">每一列都來自 git 與工單檔本身。讀不到的來源會就地標示。</p>'
        "</main>"
        "<script>"
        "const key='ticket-status-theme';"
        "const root=document.documentElement;"
        "const select=document.getElementById('theme-select');"
        "const saved=localStorage.getItem(key)||'system';"
        "select.value=saved;"
        "if(saved==='system'){root.removeAttribute('data-theme');}else{root.setAttribute('data-theme',saved);}"
        "select.addEventListener('change',(event)=>{const mode=event.target.value;"
        "if(mode==='system'){localStorage.setItem(key,'system');root.removeAttribute('data-theme');}"
        "else{localStorage.setItem(key,mode);root.setAttribute('data-theme',mode);}});"
        "</script>"
        "</body></html>"
    )


def _as_json(document: Any) -> dict[str, Any]:
    if isinstance(document, (str, bytes, bytearray)):
        try:
            parsed = json.loads(document)
            return _as_dict(parsed)
        except (TypeError, ValueError):
            return {}
    return _as_dict(document)


__all__ = ["render"]
