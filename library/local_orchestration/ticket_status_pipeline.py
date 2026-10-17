"""Answer, from the repository itself, where every tracked ticket stands.

The owner's question is small and precise: which ticket is at which stage,
which commit does it stand at, and what do I hand a conversation if I take it
over. Everything here exists to answer that from facts rather than from
recollection.

Two rules decide the whole design.

**A ticket's state is declared, never inferred.** Each tracked ticket carries a
```johnny-status``` block; this module reads that block and nothing else. It
does not parse the English in a State row, because a sentence like "R2/R3
landed; R4 open" is a summary written for a human and reading it as data is how
a page ends up confidently wrong about work the owner is depending on.
Child and Finding metadata may reject an inconsistent declared APPROVED row as
unreadable; it never promotes or infers another ticket state.

**Absent and broken are different answers.** A ticket file with no block has
not opted in to this surface and is simply not listed. A file whose block is
present but will not parse is reported in `unreadable`, with its path and the
reason — because that one *was* meant to be on the page, and a list that is
short because a file broke is the failure this surface exists to prevent.

The document this produces is plain stdlib types. The template that renders it
is a separate module owned by someone else; neither imports the other.
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

_BLOCK = re.compile(r"```johnny-status\r?\n(.*?)```", re.DOTALL)
_NULL = "-"
_TICKETS_RELATIVE = Path("modules") / "tickets"
_SKIPPED_STEMS = frozenset({"README", "TEMPLATE", "README.TEMPLATE", "PITFALL-REGISTER"})

# The lifecycle the owner actually runs: work finishes, then it is reviewed,
# and "finished" is not "accepted". DONE means the work is done and waiting for
# a verdict; APPROVED and REJECTED are the two verdicts. Collapsing DONE into
# APPROVED would hide the queue of things waiting on a review nobody has done.
_TICKET_STATES = (
    "NEEDS_OWNER",
    "REJECTED",
    "DONE",
    "IN_PROGRESS",
    "APPROVED",
)
_LEGACY_STAGE_STATES = ("DONE", "OPEN")
_EVIDENCE_STAGE_STATES = ("DONE", "OPEN", "NOT_VERIFIED")
_STAGE_REQUIREMENTS = ("REQUIRED", "OPTIONAL")
_TICKET_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,63}\Z")
_CHILD_REQUIREMENTS = ("REQUIRED", "OPTIONAL")
_FINDING_STATES = ("OPEN", "CLOSED")
_EVIDENCE_REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/#-]{0,127}\Z")
_SCALAR_KEYS = frozenset(
    {"id", "title", "state", "reason", "released_in", "commit"}
)
_REQUIRED_KEYS = ("id", "title", "state")
_REASON_REQUIRED = frozenset({"NEEDS_OWNER", "REJECTED"})
_STATE_ORDER = {name: index for index, name in enumerate(_TICKET_STATES)}


def _git(repository_root: Path, *arguments: str) -> str | None:
    """Run git for one fact. Bytes in, UTF-8 out: paths here carry CJK."""

    try:
        completed = subprocess.run(
            ("git", *arguments),
            cwd=str(repository_root),
            capture_output=True,
            shell=False,
            timeout=30,
        )
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.decode("utf-8", errors="replace").strip()


def find_status_block(text: str) -> str | None:
    """Return the declared block, or None when the file never opted in."""

    match = _BLOCK.search(text)
    return None if match is None else match.group(1)


def parse_status_block(body: str) -> dict[str, object]:
    """Read one declared block. Anything unexpected raises rather than guesses."""

    scalars: dict[str, str] = {}
    stages: list[dict[str, str | None]] = []
    children: list[dict[str, str]] = []
    findings: list[dict[str, str | None]] = []
    stage_format: int | None = None
    evidence_stage_refs: set[str] = set()
    child_ids: set[str] = set()
    finding_ids: set[str] = set()
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"每一行都要是 key = value：{line!r}")
        key, value = (part.strip() for part in line.split("=", 1))
        if key == "stage":
            fields = [field.strip() for field in value.split("|")]
            if len(fields) not in (3, 5):
                raise ValueError(
                    "stage 要寫成 ref | label | state 或 "
                    "ref | label | state | requirement | evidence-ref："
                    f"{value!r}"
                )
            current_format = len(fields)
            if stage_format is not None and stage_format != current_format:
                raise ValueError("舊三欄 stage 與新五欄 stage 不可混用")
            stage_format = current_format
            if current_format == 3:
                ref, label, state = fields
                requirement = None
                evidence_ref = None
            else:
                ref, label, state, requirement, evidence_ref = fields
            if not ref:
                raise ValueError("stage 的 ref 不能是空的")
            allowed_states = (
                _LEGACY_STAGE_STATES
                if current_format == 3
                else _EVIDENCE_STAGE_STATES
            )
            if state not in allowed_states:
                raise ValueError(f"stage 狀態只能是 {allowed_states}：{state!r}")
            if current_format == 3:
                stages.append({"ref": ref, "label": label, "state": state})
            else:
                if requirement not in _STAGE_REQUIREMENTS:
                    raise ValueError(
                        f"stage 必要性只能是 {_STAGE_REQUIREMENTS}：{requirement!r}"
                    )
                if ref in evidence_stage_refs:
                    raise ValueError(f"五欄 stage ref 不可重複：{ref!r}")
                evidence_stage_refs.add(ref)
                if state == "DONE":
                    if evidence_ref is None or not _EVIDENCE_REF.fullmatch(evidence_ref):
                        raise ValueError(
                            "DONE stage 必須提供受限格式 evidence-ref"
                        )
                elif evidence_ref != _NULL:
                    raise ValueError("未完成 stage 的 evidence-ref 必須是 '-'")
                stages.append(
                    {
                        "ref": ref,
                        "label": label,
                        "state": state,
                        "requirement": requirement,
                        "evidence_ref": None if evidence_ref == _NULL else evidence_ref,
                    }
                )
            continue
        if key == "child":
            fields = [field.strip() for field in value.split("|")]
            if len(fields) != 2:
                raise ValueError("child 要寫成 ticket-id | REQUIRED|OPTIONAL")
            child_id, requirement = fields
            if not _TICKET_ID.fullmatch(child_id):
                raise ValueError(f"child ticket-id 格式無效：{child_id!r}")
            if requirement not in _CHILD_REQUIREMENTS:
                raise ValueError(
                    f"child 必要性只能是 {_CHILD_REQUIREMENTS}：{requirement!r}"
                )
            if child_id in child_ids:
                raise ValueError(f"child ticket-id 不可重複：{child_id!r}")
            child_ids.add(child_id)
            children.append({"id": child_id, "requirement": requirement})
            continue
        if key == "finding":
            fields = [field.strip() for field in value.split("|")]
            if len(fields) != 4:
                raise ValueError(
                    "finding 要寫成 id | owner | OPEN|CLOSED | disposition/evidence-ref"
                )
            finding_id, owner, finding_state, disposition_ref = fields
            if not _TICKET_ID.fullmatch(finding_id):
                raise ValueError(f"finding id 格式無效：{finding_id!r}")
            if finding_id in finding_ids:
                raise ValueError(f"finding id 不可重複：{finding_id!r}")
            finding_ids.add(finding_id)
            if not owner or owner == "-" or len(owner) > 80 or not all(
                character.isprintable() for character in owner
            ):
                raise ValueError("finding 必須保留有效責任人")
            if finding_state not in _FINDING_STATES:
                raise ValueError(
                    f"finding 狀態只能是 {_FINDING_STATES}：{finding_state!r}"
                )
            if finding_state == "OPEN":
                if disposition_ref != _NULL:
                    raise ValueError("OPEN finding 的去向必須是 '-'")
                finding_ref = None
            else:
                if not _EVIDENCE_REF.fullmatch(disposition_ref):
                    raise ValueError(
                        "CLOSED finding 必須提供受限格式 disposition/evidence-ref"
                    )
                finding_ref = disposition_ref
            findings.append(
                {
                    "id": finding_id,
                    "owner": owner,
                    "state": finding_state,
                    "disposition_ref": finding_ref,
                }
            )
            continue
        if key not in _SCALAR_KEYS:
            # A typo here would silently drop a field, so it is an error and
            # not something to skip past.
            raise ValueError(f"不認得的欄位 {key!r}")
        if key in scalars:
            raise ValueError(f"欄位 {key!r} 出現兩次")
        scalars[key] = value

    for key in _REQUIRED_KEYS:
        if not scalars.get(key):
            raise ValueError(f"缺少必要欄位 {key!r}")
    state = scalars["state"]
    if state not in _TICKET_STATES:
        raise ValueError(f"state 只能是 {_TICKET_STATES}：{state!r}")

    why = scalars.get("reason", _NULL)
    reason = None if why in ("", _NULL) else why
    # A row that says someone is blocked without saying on what is a row the
    # owner cannot act on, so both states that block demand their reason.
    if state in _REASON_REQUIRED and reason is None:
        raise ValueError(f"state 是 {state} 就必須寫 reason")
    if state not in _REASON_REQUIRED and reason is not None:
        raise ValueError(f"state 是 {state} 不該寫 reason")
    if state == "APPROVED" and stage_format == 5:
        blocked: list[str] = []
        for stage in stages:
            if stage["requirement"] == "REQUIRED" and stage["state"] != "DONE":
                blocked.append(str(stage["ref"]))
        if blocked:
            raise ValueError(
                "APPROVED 不可有未完成的 REQUIRED stage：" + ", ".join(blocked)
            )

    released = scalars.get("released_in", _NULL)
    named = scalars.get("commit", _NULL)
    return {
        "declared_commit": None if named in ("", _NULL) else named,
        "id": scalars["id"],
        "title": scalars["title"],
        "state": state,
        "reason": reason,
        "stages": stages,
        "children": children,
        "findings": findings,
        "released_in": None if released in ("", _NULL) else released,
    }


def discover_ticket_files(repository_root: Path) -> tuple[Path, ...]:
    """Every ticket markdown file, registries and templates excluded."""

    root = repository_root / _TICKETS_RELATIVE
    if not root.is_dir():
        return ()
    found = [
        path
        for path in sorted(root.rglob("*.md"))
        if path.stem not in _SKIPPED_STEMS
    ]
    return tuple(found)


def _named_commit(repository_root: Path, sha: str) -> dict[str, str] | None:
    """Resolve a declared commit. A sha that does not resolve is not a commit.

    Falling back silently here would hand the owner a handoff command built
    from a typo, which fails only once they are already depending on it.
    """

    line = _git(repository_root, "log", "-1", "--format=%h%x1f%s", sha)
    if not line or "\x1f" not in line:
        return None
    resolved, subject = line.split("\x1f", 1)
    return {"sha": resolved, "subject": subject}


def _last_commit(repository_root: Path, path: Path) -> dict[str, str] | None:
    """Where the file was last touched; used only when none is declared."""

    relative = path.relative_to(repository_root).as_posix()
    line = _git(
        repository_root, "log", "-1", "--format=%h%x1f%s", "--", relative
    )
    if not line or "\x1f" not in line:
        return None
    sha, subject = line.split("\x1f", 1)
    return {"sha": sha, "subject": subject}


def _head(repository_root: Path) -> dict[str, str]:
    return {
        "branch": _git(repository_root, "rev-parse", "--abbrev-ref", "HEAD") or "-",
        "commit": _git(repository_root, "rev-parse", "--short", "HEAD") or "-",
    }


def _newest_tag(repository_root: Path, pattern: str, sort: str) -> str | None:
    listing = _git(repository_root, "tag", "--list", pattern, "--sort", sort)
    if not listing:
        return None
    return listing.splitlines()[0].strip() or None


def _tag_commit(repository_root: Path, tag: str) -> str | None:
    return _git(repository_root, "rev-parse", "--short", f"{tag}^{{commit}}")


def _project_children_and_findings(
    tickets: list[dict[str, object]], unreadable: list[dict[str, str]]
) -> list[dict[str, object]]:
    """Resolve opt-in relationships for display without granting closure authority."""

    by_id: dict[str, list[dict[str, object]]] = {}
    by_path: dict[str, dict[str, object]] = {}
    for ticket in tickets:
        ticket_id = str(ticket["id"])
        path = str(ticket["ticket_path"])
        by_id.setdefault(ticket_id, []).append(ticket)
        by_path[path] = ticket

    edges: dict[str, list[str]] = {path: [] for path in by_path}
    direct_errors: dict[str, list[str]] = {}
    for path, ticket in by_path.items():
        children = ticket.get("children", [])
        if not isinstance(children, list):
            continue
        for child in children:
            if not isinstance(child, dict):
                continue
            child_id = str(child.get("id", ""))
            matches = by_id.get(child_id, [])
            if len(matches) == 1:
                child_path = str(matches[0]["ticket_path"])
                if child_path == path:
                    direct_errors.setdefault(path, []).append(
                        f"子票 {child_id} 不可指向自己"
                    )
                else:
                    edges[path].append(child_path)

    # A cycle invalidates only its participating opted-in tickets. Unrelated
    # tickets remain available on the page.
    visiting: list[str] = []
    visited: set[str] = set()
    cycle_paths: set[str] = set()

    def visit(path: str) -> None:
        if path in visited:
            return
        if path in visiting:
            cycle_paths.update(visiting[visiting.index(path) :])
            return
        visiting.append(path)
        for child_path in edges[path]:
            visit(child_path)
        visiting.pop()
        visited.add(path)

    for path in edges:
        visit(path)
    for path in cycle_paths:
        direct_errors.setdefault(path, []).append("子票關聯形成循環")

    child_views: dict[str, list[dict[str, object]]] = {}
    for path, ticket in by_path.items():
        view: list[dict[str, object]] = []
        children = ticket.get("children", [])
        if isinstance(children, list):
            for child in children:
                if not isinstance(child, dict):
                    continue
                child_id = str(child.get("id", ""))
                requirement = str(child.get("requirement", ""))
                matches = by_id.get(child_id, [])
                projected_path: str | None
                child_title: object
                if not matches:
                    child_state = "UNKNOWN"
                    child_title = None
                    projected_path = None
                    if requirement == "REQUIRED":
                        direct_errors.setdefault(path, []).append(
                            f"必要子票 {child_id} 不在本次讀取集合中"
                        )
                elif len(matches) > 1:
                    child_state = "AMBIGUOUS"
                    child_title = None
                    projected_path = None
                    if requirement == "REQUIRED":
                        direct_errors.setdefault(path, []).append(
                            f"必要子票 {child_id} 對應多筆工單"
                        )
                else:
                    resolved = matches[0]
                    child_state = str(resolved["state"])
                    child_title = resolved["title"]
                    resolved_path = resolved["ticket_path"]
                    if isinstance(resolved_path, str):
                        projected_path = resolved_path
                    else:
                        projected_path = None
                        direct_errors.setdefault(path, []).append(
                            f"子票 {child_id} 缺少可讀路徑"
                        )
                    if projected_path in cycle_paths:
                        child_state = "UNREADABLE"
                view.append(
                    {
                        "id": child_id,
                        "requirement": requirement,
                        "state": child_state,
                        "title": child_title,
                        "ticket_path": projected_path,
                    }
                )
        child_views[path] = view

    invalid_paths = set(direct_errors)
    # Approval must not survive a required child that is incomplete or whose
    # own projection is invalid. Iteration propagates that condition upward.
    changed = True
    while changed:
        changed = False
        for path, ticket in by_path.items():
            if str(ticket["state"]) != "APPROVED" or path in invalid_paths:
                continue
            for child in child_views[path]:
                if child["requirement"] != "REQUIRED":
                    continue
                required_child_path = child["ticket_path"]
                if child["state"] != "APPROVED" or (
                    isinstance(required_child_path, str)
                    and required_child_path in invalid_paths
                ):
                    direct_errors.setdefault(path, []).append(
                        f"必要子票 {child['id']} 尚未投影為有效 APPROVED"
                    )
                    invalid_paths.add(path)
                    changed = True
                    break
            if path in invalid_paths:
                continue
            findings = ticket.get("findings", [])
            if isinstance(findings, list) and any(
                isinstance(finding, dict) and finding.get("state") == "OPEN"
                for finding in findings
            ):
                direct_errors.setdefault(path, []).append(
                    "APPROVED 工單仍有 OPEN Finding"
                )
                invalid_paths.add(path)
                changed = True

    visible: list[dict[str, object]] = []
    for path, ticket in by_path.items():
        if path in invalid_paths:
            reasons = list(dict.fromkeys(direct_errors.get(path, [])))
            unreadable.append(
                {
                    "label": str(ticket["id"]),
                    "path": path,
                    "reason": "；".join(reasons) or "父項／Finding 投影無效",
                }
            )
            continue
        projected = dict(ticket)
        projected["children"] = child_views[path]
        for child in child_views[path]:
            projected_child_path = child.get("ticket_path")
            if (
                isinstance(projected_child_path, str)
                and projected_child_path in invalid_paths
            ):
                child["state"] = "UNREADABLE"
        visible.append(projected)
    return visible


def build_document(repository_root: Path) -> dict[str, object]:
    """Produce the whole document the template renders. Facts only."""

    tickets: list[dict[str, object]] = []
    unreadable: list[dict[str, str]] = []
    head = _head(repository_root)

    for path in discover_ticket_files(repository_root):
        relative = path.relative_to(repository_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as error:
            unreadable.append(
                {
                    "label": relative,
                    "path": relative,
                    "reason": f"讀不到檔案：{type(error).__name__}",
                }
            )
            continue
        block = find_status_block(text)
        if block is None:
            # Never opted in. Not an error, and not something to report as one.
            continue
        try:
            declared = parse_status_block(block)
        except ValueError as error:
            unreadable.append(
                {"label": relative, "path": relative, "reason": str(error)}
            )
            continue

        named = declared.pop("declared_commit")
        if named is None:
            commit = _last_commit(repository_root, path)
        else:
            if not isinstance(named, str):
                raise ValueError("declared_commit 必須是字串")
            commit = _named_commit(repository_root, named)
            if commit is None:
                unreadable.append(
                    {
                        "label": relative,
                        "path": relative,
                        "reason": f"宣告的 commit {named!r} 在這個 repo 找不到",
                    }
                )
                continue
        anchor = commit["sha"] if commit is not None else head["commit"]
        declared.update(
            {
                "module": path.parent.name,
                "commit": commit,
                "ticket_path": relative,
                "handoff_command": f"git show {anchor} -- {relative}",
            }
        )
        tickets.append(declared)

    tickets = _project_children_and_findings(tickets, unreadable)
    tickets.sort(key=lambda item: (_STATE_ORDER[str(item["state"])], str(item["id"])))

    release_tag = _newest_tag(repository_root, "v*", "-v:refname")
    rollback_tag = _newest_tag(repository_root, "rollback-pre-*", "-refname")
    release = None
    if release_tag is not None:
        release_commit = _tag_commit(repository_root, release_tag)
        if release_commit is not None:
            release = {"version": release_tag, "commit": release_commit}
    rollback = None
    if rollback_tag is not None:
        rollback_commit = _tag_commit(repository_root, rollback_tag)
        if rollback_commit is not None:
            rollback = {"commit": rollback_commit}

    return {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(
            timespec="seconds"
        ),
        "head": head,
        "release": release,
        "rollback": rollback,
        "tickets": tickets,
        "unreadable": unreadable,
    }


__all__ = [
    "build_document",
    "discover_ticket_files",
    "find_status_block",
    "parse_status_block",
]
