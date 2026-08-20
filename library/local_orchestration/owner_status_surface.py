"""Render the one page that tells the owner what the Router is doing.

Supervision the owner cannot observe is not supervision. The desktop app was
measured shut to every route the Router could use -- driving the conversation
behind an open tab renders nothing, background agents are not displayed, and a
CLI session has no MCP servers to reach the app's own message channel -- so
this surface lives outside the app: one HTML file the owner keeps open, rewritten
whenever state changes and refreshed by the browser itself. Nothing polls, and
nothing listens on a port.

The rule that shapes every decision here: **a lane that cannot be read must
never look like a lane with nothing in it.** An empty "waiting on you" column
tells the owner they are free to stop watching. If that emptiness came from a
source this module failed to parse, the page has told them something false
about their own work, which is the whole defect this project keeps paying for
(see `modules/tickets/workflow-governance/04-...`). So each source is read
separately, a failure is reported in place, and one broken source never
silences the items its neighbours produced.

This module has no authority. It reads state and renders it; it never claims,
settles, consumes, or repairs anything it displays.
"""

from __future__ import annotations

import html
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from .johnny_root_layout import JohnnyRootLayout

_SURFACE_FILE_NAME = "owner-status.html"
_REFRESH_SECONDS = 30
_MAX_DONE_ITEMS = 25


class LaneKind(str, Enum):
    """The three questions the owner actually asks, in the order they ask them."""

    WAITING = "WAITING"
    WORKING = "WORKING"
    DONE = "DONE"


_LANE_TITLE = {
    LaneKind.WAITING: "等你決定",
    LaneKind.WORKING: "進行中",
    LaneKind.DONE: "已完成",
}
_LANE_SLUG = {
    LaneKind.WAITING: "waiting",
    LaneKind.WORKING: "working",
    LaneKind.DONE: "done",
}
_LANE_EMPTY = {
    LaneKind.WAITING: "沒有事情等你——這是讀得到的來源給出的答案，不是猜的。",
    LaneKind.WORKING: "目前沒有進行中的工作。",
    LaneKind.DONE: "還沒有完成的項目。",
}


class Severity(str, Enum):
    """What kind of thing the owner has to do, which decides how it looks."""

    RELAY = "relay"
    OWNER_HOLDS = "owner-holds"
    CONFIG = "config"
    HOST = "host"


@dataclass(frozen=True, slots=True)
class OwnerAction:
    """One refusal code, said in the owner's language, with the fix."""

    severity: Severity
    category: str
    instruction: str


# Every code that can stop work has to arrive here wearing a different face.
# Four identical grey chips would make the page a list of things that went
# wrong; the owner needs to see, without reading, which one they can fix in
# five seconds and which one means the host is broken.
_OWNER_ACTIONS: dict[str, OwnerAction] = {
    "CANDIDATE_INBOX": OwnerAction(
        Severity.RELAY,
        "要你轉達",
        "這個專案沒有架設 runner，所以沒有人被喚醒，事情只被記下來。"
        "請自己把它轉達給指定的 reviewer。",
    ),
    "BRANCH_HELD_BY_APP_TAB": OwnerAction(
        Severity.OWNER_HOLDS,
        "你開著那個對話",
        "Router 拒絕寫進你正開著的分頁——寫進去你也看不到，而且會和 app "
        "的記憶體歷史打架。關掉那個分頁，或這件事你自己處理。",
    ),
    "REVIEWER_NOT_MAPPED": OwnerAction(
        Severity.CONFIG,
        "路由沒設",
        "這個 reviewer 沒有對應的分支。在 claude-branch-routes.json 補上"
        "一筆路由，它下次就送得到。",
    ),
    "RUNNER_NOT_RUNNING": OwnerAction(
        Severity.CONFIG,
        "runner 沒在跑",
        "訂閱已經登記，但 runner 不在執行中，所以沒有東西在監看 commit。"
        "重新啟動 runner。",
    ),
    "NOT_AUTHENTICATED": OwnerAction(
        Severity.HOST,
        "主機無法驅動",
        "Claude CLI 沒有通過認證。跑 claude setup-token，把拿到的 "
        "sk-ant-oat01- token 設進 CLAUDE_CODE_OAUTH_TOKEN。",
    ),
    "DRIVE_FAILED": OwnerAction(
        Severity.HOST,
        "主機無法驅動",
        "喚醒命令執行失敗。先確認認證仍然有效，再確認 CLI 路徑正確。",
    ),
    "LIVE_SESSION_CHECK_FAILED": OwnerAction(
        Severity.HOST,
        "無法確認安全",
        "無法列出現役對話，所以 Router 不能確定目標分支沒被你開著，"
        "因此拒絕送出。確認 CLI 可執行後會自行恢復。",
    ),
    "APP_CLAIM_CHECK_FAILED": OwnerAction(
        Severity.HOST,
        "無法確認安全",
        "讀不到桌面 app 的對話登記，無法確定目標分支沒有被分頁佔用，"
        "因此拒絕送出。",
    ),
}

_UNKNOWN_ACTION = OwnerAction(
    Severity.HOST,
    "沒有對應指引",
    "這個代碼還沒有寫下處理方式。查 runner log 找出原因，並把處理方式補進"
    "owner_status_surface.py 的對照表。",
)


def owner_action(code: str) -> OwnerAction:
    """Never leave a code bare: an unexplained code is not an instruction."""

    return _OWNER_ACTIONS.get(code, _UNKNOWN_ACTION)


@dataclass(frozen=True, slots=True)
class SurfaceItem:
    """One line the owner reads, carrying only what a source really said."""

    title: str
    identifiers: tuple[tuple[str, str], ...] = ()
    code: str | None = None
    observed_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class UnreadableSource:
    """A source that failed, named in place of the rows it would have carried."""

    label: str
    path: str
    reason: str


@dataclass(frozen=True, slots=True)
class Lane:
    """Items a lane could read, plus every source it could not."""

    kind: LaneKind
    items: tuple[SurfaceItem, ...] = ()
    unreadable: tuple[UnreadableSource, ...] = ()

    @property
    def is_trustworthy(self) -> bool:
        """True only when nothing was hidden by a failure."""

        return not self.unreadable


@dataclass(frozen=True, slots=True)
class OwnerStatusSurface:
    """Everything the page shows, already decided."""

    lanes: tuple[Lane, ...]
    generated_at: datetime


def surface_path(layout: JohnnyRootLayout) -> Path:
    """One owned path, derived like every other; never configured."""

    return layout.base / _SURFACE_FILE_NAME


def _relative(now: datetime, then: datetime) -> str:
    seconds = max(0, int((now - then).total_seconds()))
    if seconds < 90:
        return "剛剛"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} 分鐘前"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} 小時前"
    return f"{hours // 24} 天前"


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _render_item(item: SurfaceItem, now: datetime) -> str:
    parts = ['<article class="item">']
    parts.append('<div class="head">')
    parts.append(f"<h3>{_escape(item.title)}</h3>")
    parts.append("</div>")

    if item.code is not None:
        action = owner_action(item.code)
        parts.append(
            f'<div class="verdict" data-severity="{_escape(action.severity.value)}"'
            f' data-code="{_escape(item.code)}">'
            f'<span class="category">{_escape(action.category)}</span>'
            f'<code class="code">{_escape(item.code)}</code>'
            "</div>"
        )
        parts.append(
            f'<p class="instruction">{_escape(action.instruction)}</p>'
        )

    if item.identifiers:
        parts.append('<dl class="meta">')
        for key, value in item.identifiers:
            parts.append(
                f"<div><dt>{_escape(key)}</dt>"
                f"<dd><code>{_escape(value)}</code></dd></div>"
            )
        parts.append("</dl>")

    if item.observed_at is not None:
        parts.append(
            '<p class="timing">'
            f'<span class="ago">{_escape(_relative(now, item.observed_at))}</span>'
            f'<time datetime="{_escape(item.observed_at.isoformat())}">'
            f'{_escape(item.observed_at.astimezone().strftime("%Y-%m-%d %H:%M"))}'
            "</time></p>"
        )
    parts.append("</article>")
    return "".join(parts)


def _render_unreadable(source: UnreadableSource) -> str:
    return (
        '<article class="unreadable">'
        f"<h3>讀不到：{_escape(source.label)}</h3>"
        "<p>這一欄可能還有你沒看到的事情。"
        "<strong>這不是「沒事」。</strong></p>"
        f'<p class="why">{_escape(source.reason)}</p>'
        f"<code>{_escape(source.path)}</code>"
        "</article>"
    )


def _render_lane(lane: Lane, now: datetime) -> str:
    slug = _LANE_SLUG[lane.kind]
    body: list[str] = [_render_unreadable(source) for source in lane.unreadable]
    body.extend(_render_item(item, now) for item in lane.items)
    if not body:
        body.append(f'<p class="empty">{_escape(_LANE_EMPTY[lane.kind])}</p>')

    count = str(len(lane.items))
    flag = "" if lane.is_trustworthy else '<span class="partial">不完整</span>'
    return (
        f'<section class="lane" data-lane="{slug}">'
        f'<header class="lane-head"><h2>{_escape(_LANE_TITLE[lane.kind])}</h2>'
        f'<span class="count">{count}</span>{flag}</header>'
        f'<div class="lane-body">{"".join(body)}</div>'
        "</section>"
    )


_STYLE = """
:root{
  --bg:#f4f6f9; --panel:#ffffff; --panel-2:#eef1f6; --line:#d8dee8;
  --ink:#111721; --ink-dim:#59636f; --ink-faint:#7d8896;
  --relay:#1f6feb; --owner-holds:#b26a00; --config:#7048c4; --host:#c02b2b;
  --ok:#1f8a4c; --warn-bg:#fff4e5; --warn-line:#e0a04a;
  --mono:ui-monospace,"Cascadia Mono",Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0d1117; --panel:#161b22; --panel-2:#1b212b; --line:#2b333f;
    --ink:#e6ebf2; --ink-dim:#9aa5b4; --ink-faint:#79838f;
    --relay:#589bff; --owner-holds:#e0a13c; --config:#a98bee; --host:#f26d6d;
    --ok:#56c98a; --warn-bg:#2a2113; --warn-line:#7a5c25;
  }
}
:root[data-theme="dark"]{
  --bg:#0d1117; --panel:#161b22; --panel-2:#1b212b; --line:#2b333f;
  --ink:#e6ebf2; --ink-dim:#9aa5b4; --ink-faint:#79838f;
  --relay:#589bff; --owner-holds:#e0a13c; --config:#a98bee; --host:#f26d6d;
  --ok:#56c98a; --warn-bg:#2a2113; --warn-line:#7a5c25;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Segoe UI","Microsoft JhengHei",system-ui,sans-serif;
  font-size:15px;line-height:1.55}
.page{max-width:1400px;margin:0 auto;padding:24px 20px 48px;
  display:flex;flex-direction:column;gap:20px}
.top{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 16px;
  border-bottom:1px solid var(--line);padding-bottom:14px}
h1{font-size:20px;margin:0;letter-spacing:.01em}
.generated{margin:0;color:var(--ink-dim);font-size:13px;
  font-variant-numeric:tabular-nums}
.boards{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));
  align-items:start}
.lane{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  overflow:hidden;min-width:0}
.lane-head{display:flex;align-items:center;gap:10px;padding:11px 14px;
  background:var(--panel-2);border-bottom:1px solid var(--line)}
.lane-head h2{font-size:14px;margin:0;letter-spacing:.04em}
.count{font-family:var(--mono);font-size:12px;color:var(--ink-dim);
  font-variant-numeric:tabular-nums;margin-left:auto}
.partial{font-size:11px;color:#fff;background:var(--host);
  padding:1px 7px;border-radius:999px;letter-spacing:.04em}
.lane-body{display:flex;flex-direction:column;gap:1px;background:var(--line)}
.item,.unreadable,.empty{background:var(--panel);padding:13px 14px;margin:0}
.item{border-left:4px solid var(--line)}
[data-lane="waiting"] .item:has([data-severity="relay"]){border-left-color:var(--relay)}
[data-lane="waiting"] .item:has([data-severity="owner-holds"]){border-left-color:var(--owner-holds)}
[data-lane="waiting"] .item:has([data-severity="config"]){border-left-color:var(--config)}
[data-lane="waiting"] .item:has([data-severity="host"]){border-left-color:var(--host)}
[data-lane="working"] .item{border-left-style:dashed;border-left-color:var(--ink-faint)}
[data-lane="done"] .item{border-left-color:var(--ok)}
.head h3{font-size:14px;margin:0;font-weight:600;text-wrap:balance}
.verdict{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:9px}
.category{font-size:12px;font-weight:700;letter-spacing:.03em;
  padding:2px 9px;border-radius:4px;color:#fff}
[data-severity="relay"] .category{background:var(--relay)}
[data-severity="owner-holds"] .category{background:var(--owner-holds)}
[data-severity="config"] .category{background:var(--config)}
[data-severity="host"] .category{background:var(--host)}
.code{font-family:var(--mono);font-size:11.5px;color:var(--ink-dim);
  letter-spacing:.02em}
.instruction{margin:7px 0 0;font-size:13.5px;color:var(--ink)}
.meta{margin:10px 0 0;display:flex;flex-wrap:wrap;gap:4px 18px}
.meta div{display:flex;gap:6px;align-items:baseline;min-width:0}
.meta dt{font-size:11px;color:var(--ink-faint);letter-spacing:.03em}
.meta dd{margin:0;min-width:0}
.meta code{font-family:var(--mono);font-size:11.5px;color:var(--ink-dim);
  word-break:break-all}
.timing{margin:9px 0 0;display:flex;gap:10px;align-items:baseline;
  font-size:12px;color:var(--ink-faint);font-variant-numeric:tabular-nums}
.ago{color:var(--ink-dim);font-weight:600}
.unreadable{background:var(--warn-bg);border-left:4px solid var(--warn-line)}
.unreadable h3{margin:0;font-size:14px}
.unreadable p{margin:6px 0 0;font-size:13px}
.unreadable .why{color:var(--ink-dim);font-size:12.5px}
.unreadable code{display:block;margin-top:7px;font-family:var(--mono);
  font-size:11.5px;color:var(--ink-dim);overflow-x:auto;white-space:pre}
.empty{color:var(--ink-faint);font-size:13px}
.foot{color:var(--ink-faint);font-size:12px;border-top:1px solid var(--line);
  padding-top:12px}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""


def render(surface: OwnerStatusSurface) -> str:
    """Produce the whole page; the caller writes it, this decides nothing else."""

    now = surface.generated_at
    lanes = "".join(_render_lane(lane, now) for lane in surface.lanes)
    stamp = now.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    trustworthy = all(lane.is_trustworthy for lane in surface.lanes)
    warning = (
        ""
        if trustworthy
        else '<p class="generated"><strong>有欄位讀不到，本頁不完整。</strong></p>'
    )
    return (
        '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta http-equiv="refresh" content="{_REFRESH_SECONDS}">'
        "<title>Johnny Router 狀態</title>"
        f"<style>{_STYLE}</style></head><body>"
        '<main class="page">'
        f'<header class="top"><h1>Johnny Router 狀態</h1>'
        f'<p class="generated">產生於 {_escape(stamp)}'
        f"（每 {_REFRESH_SECONDS} 秒自動重新整理）</p>{warning}</header>"
        f'<section class="boards">{lanes}</section>'
        '<footer class="foot">這一頁只顯示來源真的說過的話。'
        "讀不到的來源會就地標示，不會靜靜地變成空欄位。</footer>"
        "</main></body></html>"
    )


def write_surface(layout: JohnnyRootLayout, surface: OwnerStatusSurface) -> Path:
    """Replace the page atomically; a half-written page is a lying page."""

    path = surface_path(layout)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".html.tmp")
    temporary.write_text(render(surface), encoding="utf-8")
    os.replace(temporary, path)
    return path


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _mtime(path: Path) -> datetime | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    except OSError:
        return None


def _payload_identifiers(payload_path: Path) -> tuple[tuple[str, str], ...]:
    """Enrich from the wake payload when it reads; never drop an item for it."""

    try:
        body = payload_path.read_text(encoding="utf-8")
    except OSError:
        return ()
    wanted = ("project_id", "ticket_reference", "reviewer_ref")
    found: dict[str, str] = {}
    for line in body.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in wanted and value and value != "-":
            found[key] = value
    return tuple((key, found[key]) for key in wanted if key in found)


def _waiting_lane(layout: JohnnyRootLayout) -> Lane:
    from .event_runner import runner_state_path, subscriptions_path
    from .wake_candidate_inbox import candidate_inbox_path, read_candidates

    items: list[SurfaceItem] = []
    unreadable: list[UnreadableSource] = []

    try:
        candidates = read_candidates(layout)
    except Exception as error:
        unreadable.append(
            UnreadableSource(
                "候選收件匣",
                str(candidate_inbox_path(layout)),
                f"{type(error).__name__}: {error}",
            )
        )
    else:
        for candidate in candidates:
            payload = Path(candidate.payload_path)
            identifiers = _payload_identifiers(payload) + (
                ("attempt_id", candidate.attempt_id),
                ("reviewer_task_id", candidate.reviewer_task_id),
            )
            items.append(
                SurfaceItem(
                    title="沒有人被喚醒，只被記下來",
                    identifiers=identifiers,
                    code="CANDIDATE_INBOX",
                    observed_at=_mtime(payload),
                )
            )

    subscriptions = subscriptions_path(layout)
    state_path = runner_state_path(layout)
    if subscriptions.is_file():
        status, failure = _runner_status(state_path)
        if failure is not None:
            unreadable.append(failure)
        elif status != "RUNNING":
            items.append(
                SurfaceItem(
                    title="訂閱已登記，但沒有 runner 在監看",
                    identifiers=(("runner_status", status or "UNKNOWN"),),
                    code="RUNNER_NOT_RUNNING",
                    observed_at=_mtime(subscriptions),
                )
            )
    return Lane(LaneKind.WAITING, tuple(items), tuple(unreadable))


def _runner_status(state_path: Path) -> tuple[str | None, UnreadableSource | None]:
    if not state_path.is_file():
        return None, None
    try:
        parsed = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return None, UnreadableSource(
            "runner 狀態", str(state_path), f"{type(error).__name__}: {error}"
        )
    if not isinstance(parsed, dict):
        return None, UnreadableSource(
            "runner 狀態", str(state_path), "狀態檔不是一個物件"
        )
    value = parsed.get("status")
    return (value if isinstance(value, str) else None), None


def _working_lane(layout: JohnnyRootLayout) -> Lane:
    from .event_runner import RunnerSubscriptionFile, runner_state_path
    from .event_runner import subscriptions_path

    path = subscriptions_path(layout)
    if not path.is_file():
        return Lane(LaneKind.WORKING)

    status, failure = _runner_status(runner_state_path(layout))
    unreadable = [failure] if failure is not None else []
    if status != "RUNNING":
        return Lane(LaneKind.WORKING, (), tuple(unreadable))

    try:
        parsed = RunnerSubscriptionFile.model_validate_json(
            path.read_text(encoding="utf-8")
        )
    except Exception as error:
        unreadable.append(
            UnreadableSource(
                "runner 訂閱", str(path), f"{type(error).__name__}: {error}"
            )
        )
        return Lane(LaneKind.WORKING, (), tuple(unreadable))

    observed = _mtime(path)
    items = tuple(
        SurfaceItem(
            title="正在監看這個專案的 commit",
            identifiers=(
                ("project_id", str(spec.preparation.registration_request.project_id)),
                (
                    "subscription_id",
                    str(spec.preparation.registration_request.subscription_id),
                ),
                ("repository_root", spec.repository_root),
            ),
            observed_at=observed,
        )
        for spec in parsed.subscriptions
    )
    return Lane(LaneKind.WORKING, items, tuple(unreadable))


def _done_lane(layout: JohnnyRootLayout) -> Lane:
    from .review_return import read_returns, returns_path
    from .review_return_consumption import consumed_path, read_consumed

    unreadable: list[UnreadableSource] = []
    verdicts: dict[str, str] = {}
    try:
        for record in read_returns(layout):
            verdicts[record.handoff_id] = str(getattr(record.verdict, "value", record.verdict))
    except Exception as error:
        unreadable.append(
            UnreadableSource(
                "審查回傳", str(returns_path(layout)), f"{type(error).__name__}: {error}"
            )
        )

    try:
        consumed = read_consumed(layout)
    except Exception as error:
        unreadable.append(
            UnreadableSource(
                "已消費的回傳",
                str(consumed_path(layout)),
                f"{type(error).__name__}: {error}",
            )
        )
        return Lane(LaneKind.DONE, (), tuple(unreadable))

    observed = _mtime(consumed_path(layout))
    items: list[SurfaceItem] = []
    for marker in consumed[-_MAX_DONE_ITEMS:]:
        verdict = verdicts.get(marker.handoff_id)
        identifiers = [
            ("project_id", str(marker.project_id)),
            ("reviewer_ref", str(marker.reviewer_ref)),
            ("receipt_id", str(marker.receipt_id)),
        ]
        if verdict is not None:
            identifiers.insert(0, ("verdict", verdict))
        items.append(
            SurfaceItem(
                title="審查結果已轉為 Router 事件",
                identifiers=tuple(identifiers),
                observed_at=observed,
            )
        )
    return Lane(LaneKind.DONE, tuple(items), tuple(unreadable))


def collect(layout: JohnnyRootLayout) -> OwnerStatusSurface:
    """Read every source independently; one failure never silences the rest."""

    return OwnerStatusSurface(
        lanes=(
            _waiting_lane(layout),
            _working_lane(layout),
            _done_lane(layout),
        ),
        generated_at=_now(),
    )


def publish(layout: JohnnyRootLayout) -> Path:
    """Collect current state and replace the page. The whole public entry."""

    return write_surface(layout, collect(layout))


__all__ = [
    "Lane",
    "LaneKind",
    "OwnerAction",
    "OwnerStatusSurface",
    "Severity",
    "SurfaceItem",
    "UnreadableSource",
    "collect",
    "owner_action",
    "publish",
    "render",
    "surface_path",
    "write_surface",
]
