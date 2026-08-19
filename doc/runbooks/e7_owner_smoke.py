"""E7 owner smoke: set up a disposable repository, then deliver a real wake.

Run from a checkout of this repository. Everything it creates lives in one
disposable directory that the last step removes.

This script is the control plane acting as dispatch authority: it issues the
ticket receipt directly through the metadata store, which is exactly what a
dispatcher does. It lives under `doc/`, outside the payload roots, so nothing
here ships in the installed runtime — the runtime may only ever verify a
receipt, never mint one.

    py -3.11 doc/runbooks/e7_owner_smoke.py setup
    py -3.11 doc/runbooks/e7_owner_smoke.py handoff
    py -3.11 doc/runbooks/e7_owner_smoke.py check
    py -3.11 doc/runbooks/e7_owner_smoke.py cleanup
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from library.local_orchestration.johnny_root_layout import (  # noqa: E402
    JohnnyRootLayout,
)
from library.local_orchestration.live_dispatch_metadata_boundary import (  # noqa: E402
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
)
from library.local_orchestration.subscription_builder import (  # noqa: E402
    SubscriptionBuildStatus,
    SubscriptionInputs,
    build_subscription,
)
from library.local_orchestration.wake_capability import (  # noqa: E402
    wake_config_path,
)
from library.workflow_router.role_supervision_contracts import (  # noqa: E402
    HandoffLeafBody,
    ImplementationTerminalKind,
    seal_handoff_leaf,
)
from library.workflow_router.supervision_policy import SupervisionClass  # noqa: E402
from tests.test_role_wake_composition import _receipt  # noqa: E402
from tests.test_runner_receipt_seeding import (  # noqa: E402
    _issue_receipt_fixture,
)

_STAGE = Path(tempfile.gettempdir()) / "johnny-e7-owner-smoke"
_REPOSITORY = _STAGE / "disposable-repo"
_JOHNNY_ROOT = _STAGE / "johnny-root"
_WAKE_PROOF = _STAGE / "wake-delivered.json"
_STATE = _STAGE / "smoke-state.json"

_EXACT_REF = "refs/heads/main"
_RESERVED_LEAF = (
    "doc/handoffs/2026/e7-smoke/ticket-e7-smoke-001/handoff-e7-smoke-001.json"
)
_SPEC_REF = "spec-e7-smoke"
_SPEC_REVISION = "rev-1111111111111111"
_SOURCE_ROLE = "role-implementation-owner"
_REVIEWER_ROLE = "role-supervisor-reviewer"
_REVIEWER_TASK_REF = "task-e7-smoke-reviewer"
_REVIEWER_TASK_ID = "3f2b1c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d"


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=True,
        capture_output=True,
        shell=False,
    )
    return completed.stdout.decode("utf-8", errors="replace").strip()


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "--all")
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_AUTHOR_NAME": "e7-smoke",
            "GIT_AUTHOR_EMAIL": "e7@example.invalid",
            "GIT_COMMITTER_NAME": "e7-smoke",
            "GIT_COMMITTER_EMAIL": "e7@example.invalid",
        }
    )
    subprocess.run(
        ("git", "-C", str(root), "commit", "--quiet", "-m", message),
        check=True,
        capture_output=True,
        env=environment,
        shell=False,
    )
    return _git(root, "rev-parse", "HEAD")


def _delete_tree(path: Path) -> None:
    def onerr(func, target, exc):  # type: ignore[no-untyped-def]
        Path(target).chmod(stat.S_IWRITE)
        func(target)

    shutil.rmtree(path, onerror=onerr)


def _layout() -> JohnnyRootLayout:
    return JohnnyRootLayout(base=_JOHNNY_ROOT.resolve())


def setup() -> int:
    if _STAGE.exists():
        print(f"stage already exists, run cleanup first: {_STAGE}")
        return 2
    _REPOSITORY.mkdir(parents=True)
    _JOHNNY_ROOT.mkdir(parents=True)

    _git(_REPOSITORY, "init", "--quiet", "--initial-branch=main")
    (_REPOSITORY / "README.md").write_text("e7 smoke\n", encoding="utf-8")
    baseline = _commit(_REPOSITORY, "baseline")

    layout = _layout()
    layout.queue_root.mkdir(parents=True, exist_ok=True)

    # The wake command is what makes this smoke honest: it is a real host
    # command, and it writes the payload it was handed. A file appearing at
    # _WAKE_PROOF is proof a wake was delivered, not that one was recorded.
    wake_config_path(layout).parent.mkdir(parents=True, exist_ok=True)
    wake_config_path(layout).write_text(
        json.dumps(
            {
                "schema_version": 1,
                "command": [
                    sys.executable,
                    "-c",
                    "import pathlib,sys;"
                    f"pathlib.Path(r'{_WAKE_PROOF}').write_text("
                    "pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'),"
                    "encoding='utf-8')",
                    "{payload_file}",
                ],
                "reviewer_ref": _REVIEWER_ROLE,
                "timeout_seconds": 60,
            }
        ),
        encoding="utf-8",
    )

    receipt = _receipt().model_copy(update={"baseline_commit": baseline})
    metadata_root = layout.queue_root / "metadata"
    metadata_root.mkdir(parents=True, exist_ok=True)
    # Control plane acting as dispatch authority.
    _issue_receipt_fixture(
        LiveDispatchMetadataBoundary(JohnnyMetadataRoot(metadata_root.resolve())),
        receipt,
    )

    status, failure = build_subscription(
        layout,
        receipt,
        SubscriptionInputs(
            repository_root=str(_REPOSITORY),
            event_source_ref="event-source-e7-smoke-001",
            subscription_id="subscription-e7-smoke-001",
            exact_git_ref=_EXACT_REF,
            reserved_handoff_ref=_RESERVED_LEAF,
            spec_ref=_SPEC_REF,
            spec_revision=_SPEC_REVISION,
            source_role_ref=_SOURCE_ROLE,
            reviewer_ref=_REVIEWER_ROLE,
            reviewer_task_ref=_REVIEWER_TASK_REF,
            reviewer_task_id=_REVIEWER_TASK_ID,
            reviewer_host_id="local",
            lease_id="lease-e7-smoke-001",
            supervision_class=SupervisionClass.LUNA_XHIGH_DEFAULT,
        ),
    )
    if status is not SubscriptionBuildStatus.WRITTEN:
        print(f"subscription refused: {failure}")
        return 2

    _STATE.write_text(
        json.dumps({"baseline": baseline, "receipt_id": receipt.receipt_id}),
        encoding="utf-8",
    )
    print("SETUP OK")
    print(f"  disposable repository : {_REPOSITORY}")
    print(f"  disposable Johnny root: {_JOHNNY_ROOT}")
    print(f"  baseline commit       : {baseline}")
    print()
    print("Next, start the runner in this same shell:")
    print(f'  set JOHNNY_ROOT={_JOHNNY_ROOT}')
    print(f'  py -3.11 -m library.local_orchestration.event_runner_main')
    print()
    print("Then, in a second shell, run the handoff step.")
    return 0


def handoff() -> int:
    state = json.loads(_STATE.read_text(encoding="utf-8"))
    baseline = state["baseline"]

    (_REPOSITORY / "worklog.txt").write_text("implementation\n", encoding="utf-8")
    result_commit = _commit(_REPOSITORY, "implementation result")

    receipt = _receipt().model_copy(update={"baseline_commit": baseline})
    body = HandoffLeafBody(
        handoff_id="handoff-e7-smoke-001",
        schema_revision="handoff-leaf-v1",
        project_id=receipt.project_id,
        spec_ref=_SPEC_REF,
        spec_revision=_SPEC_REVISION,
        ticket_ref=receipt.ticket_reference,
        ticket_revision=receipt.ticket_revision,
        router_receipt_ref=receipt.receipt_id,
        source_role_ref=_SOURCE_ROLE,
        source_task_ref=receipt.implementation_owner_id,
        target_role_ref=_REVIEWER_ROLE,
        target_task_ref=_REVIEWER_TASK_REF,
        worktree_ref=receipt.worktree_fingerprint,
        branch_ref=receipt.branch_fingerprint,
        baseline_commit=baseline,
        result_commit=result_commit,
        correlation_id=receipt.correlation_id,
        terminal_kind=ImplementationTerminalKind.COMPLETED,
        previous_handoff_ref=None,
        supersedes_ref=None,
        evidence_refs=("evidence-e7-owner-smoke",),
    )
    leaf = _REPOSITORY / _RESERVED_LEAF
    leaf.parent.mkdir(parents=True, exist_ok=True)
    leaf.write_text(seal_handoff_leaf(body).model_dump_json(), encoding="utf-8")
    handoff_commit = _commit(_REPOSITORY, "handoff")

    print("HANDOFF COMMITTED")
    print(f"  result commit : {result_commit}")
    print(f"  handoff commit: {handoff_commit}")
    print()
    print("Now run the check step; the runner should have woken the reviewer.")
    return 0


def check() -> int:
    """Require a real wake payload, not the capability probe's own payload.

    `probe_wake_capability` proves the channel by running the declared command
    for real, with a disposable payload. That run writes this same file, so a
    file existing is not evidence of a wake: only a `ROLE_WAKE_V1` payload is.
    """

    runner_state = _layout().queue_root / "runner-state.json"
    if not _WAKE_PROOF.is_file():
        print("NO WAKE OBSERVED")
        print(f"  expected proof file: {_WAKE_PROOF}")
        if runner_state.is_file():
            print(f"  runner state: {runner_state.read_text(encoding='utf-8')}")
        return 2

    payload = _WAKE_PROOF.read_text(encoding="utf-8")
    if "ROLE_WAKE_V1" not in payload:
        print("ONLY THE CAPABILITY PROBE HAS RUN, NO WAKE YET")
        print(f"  payload: {payload.strip()}")
        if runner_state.is_file():
            print(f"  runner state: {runner_state.read_text(encoding='utf-8')}")
        return 2

    action = next(
        (
            line.split("=", 1)[1]
            for line in payload.splitlines()
            if line.startswith("action=")
        ),
        "?",
    )
    print("WAKE DELIVERED")
    print(f"  action: {action}")
    if action != "REVIEW_HANDOFF":
        print(
            "  NOTE: this is not the handoff-driven wake. A SUPERVISION_DEADLINE\n"
            "        action here means the deadline expired before the handoff\n"
            "        landed; check that started_at_ms is the host's monotonic ms."
        )
    print(f"  payload:\n{payload}")
    return 0


def cleanup() -> int:
    if _STAGE.exists():
        _delete_tree(_STAGE)
    print(f"REMOVED {_STAGE}" if not _STAGE.exists() else "REMOVAL FAILED")
    return 0 if not _STAGE.exists() else 2


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    actions = {
        "setup": setup,
        "handoff": handoff,
        "check": check,
        "cleanup": cleanup,
    }
    action = actions.get(command)
    if action is None:
        print(__doc__)
        return 2
    return action()


if __name__ == "__main__":
    raise SystemExit(main())
