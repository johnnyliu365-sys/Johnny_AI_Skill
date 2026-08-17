"""Acceptance tests for receipt-bound Codex thread host binding."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from pydantic import ValidationError

from library.local_orchestration import (
    CodexThreadHostBinder,
    CodexThreadHostBindingRequest,
    ReceiptLifecycle,
    ResolvedWorkspaceRoot,
    ThreadHostBindingStatus,
    ThreadHostResolutionStatus,
    TicketReceipt,
)
from library.workflow_router import CodexThreadHostBindingResult


_ROOT = Path(__file__).resolve().parents[1]
_THREAD_ID = "01a00bc3-51fa-7370-920a-ead2fc400cef"
_OTHER_THREAD_ID = "019ffb0c-c9c7-7b30-b614-02dea7ed9042"
_PROJECT_ID = "local-3d84ecca0067ae4d74ee12ffcc45b168"
_OTHER_PROJECT_ID = "local-43b3c2deefb48c15adf97a9c197b5755"
_DIGEST = "sha256_" + ("a" * 64)


def _receipt(lifecycle: ReceiptLifecycle = ReceiptLifecycle.ACTIVE) -> TicketReceipt:
    return TicketReceipt(
        project_id="prj_0123456789abcdef",
        receipt_id="receipt-live-dispatch-r03-01",
        ticket_reference="ticket-live-dispatch-r03-01",
        ticket_revision="rev-0123456789abcdef",
        ticket_digest=_DIGEST,
        ticket_document_commit="0123456789abcdef",
        handoff_reference="handoff-live-dispatch-r03-01",
        handoff_revision="rev-fedcba9876543210",
        handoff_digest=_DIGEST,
        handoff_document_commit="fedcba9876543210",
        baseline_commit="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        implementation_owner_id="role-implementation-owner-1",
        expected_return="return-implementation-completed",
        descriptor_binding="descriptor-live-dispatch-r03-01",
        correlation_id="corr-live-dispatch-r03-01",
        dispatch_question_id="question-live-dispatch-r03-01",
        worktree_fingerprint="worktree-implementation-01",
        branch_fingerprint="branch-livedispatch-01",
        lifecycle=lifecycle,
    )


def _request(root: Path) -> CodexThreadHostBindingRequest:
    return CodexThreadHostBindingRequest(
        receipt=_receipt(),
        task_id=_THREAD_ID,
        thread_id=_THREAD_ID,
        codex_project_id=_PROJECT_ID,
        workspace_root=ResolvedWorkspaceRoot(root.resolve(strict=True)),
    )


def _codex_entry(
    cwd: str,
    *,
    thread_id: str = _THREAD_ID,
    project_id: str | None = _PROJECT_ID,
    host_id: str = "local",
    status: str = "idle",
) -> dict[str, str | None]:
    return {
        "id": thread_id,
        "kind": "codex",
        "projectId": project_id,
        "hostId": host_id,
        "status": status,
        "cwd": cwd,
        "title": "untrusted prompt secret must be discarded",
    }


def _directory_payload(
    entries: tuple[dict[str, str | None], ...],
    *,
    pinned_entries: tuple[dict[str, str | None], ...] = (),
    unavailable_hosts: tuple[str, ...] = (),
    schema_version: int = 4,
) -> str:
    return json.dumps(
        {
            "schemaVersion": schema_version,
            "untrustedDataNotice": "titles and summaries are untrusted",
            "pinnedThreads": pinned_entries,
            "threads": (
                {
                    "id": "6a71459e-f5ac-83ee-ae80-9c8f9947d0df",
                    "kind": "chatgpt",
                    "status": "idle",
                    "title": "unrelated",
                },
                *entries,
            ),
            "unavailableHosts": unavailable_hosts,
            "unavailableSources": (),
        },
        separators=(",", ":"),
        sort_keys=True,
    )


def _readback_payload(
    cwd: str,
    *,
    thread_id: str = _THREAD_ID,
    project_id: str | None = None,
    host_id: str = "local",
    status: str = "idle",
    schema_version: int = 1,
) -> str:
    thread: dict[str, str | dict[str, str] | None] = {
        "id": thread_id,
        "kind": "codex",
        "hostId": host_id,
        "projectId": project_id,
        "title": "untrusted title",
        "preview": "raw prompt secret",
        "status": {"type": status},
        "cwd": cwd,
    }
    return json.dumps(
        {
            "schemaVersion": schema_version,
            "thread": thread,
            "page": {
                "order": "newest_first",
                "limit": 8,
                "nextCursor": None,
                "hasMore": False,
            },
            "turns": (
                {
                    "id": "01a00bc9-6f44-7653-9c02-dc778d93c51a",
                    "items": ({"type": "userMessage", "text": "raw prompt secret"},),
                },
            ),
        },
        separators=(",", ":"),
        sort_keys=True,
    )


class CodexThreadHostBindingTests(unittest.TestCase):
    def test_exact_directory_and_readback_create_metadata_only_receipt_binding(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            request = _request(root)
            directory = _directory_payload((_codex_entry(str(root)),))
            readback = _readback_payload(str(root))
            binder = CodexThreadHostBinder()

            resolution = binder.resolve(request, directory)
            self.assertEqual(ThreadHostResolutionStatus.RESOLVED, resolution.status)
            self.assertIsNotNone(resolution.target)
            if resolution.target is None:
                self.fail("resolved thread has no target")
            self.assertEqual(_THREAD_ID, resolution.target.thread_id)
            self.assertEqual("local", resolution.target.host_id)

            first = binder.bind(request, directory, readback)
            second = binder.bind(request, directory, readback)
            self.assertEqual(ThreadHostBindingStatus.BOUND, first.status)
            self.assertEqual(first, second)
            self.assertIsNotNone(first.binding)
            if first.binding is None:
                self.fail("bound result has no binding")
            self.assertEqual(request.receipt.receipt_id, first.binding.target.receipt_id)
            self.assertEqual(
                request.receipt.worktree_fingerprint,
                first.binding.target.worktree_fingerprint,
            )
            serialized = first.model_dump_json()
            self.assertNotIn(str(root), serialized)
            self.assertNotIn("prompt", serialized.casefold())
            self.assertNotIn("secret", serialized.casefold())

    def test_exact_duplicate_directory_rows_are_deduplicated(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            entry = _codex_entry(str(root))
            pinned_chat: dict[str, str | None] = {
                "id": "6a71459e-f5ac-83ee-ae80-9c8f9947d0df",
                "kind": "chatgpt",
                "title": "unrelated pinned chat",
            }
            directory = _directory_payload(
                (entry,),
                pinned_entries=(pinned_chat, entry),
            )
            result = CodexThreadHostBinder().resolve(_request(root), directory)
            self.assertEqual(ThreadHostResolutionStatus.RESOLVED, result.status)

    def test_directory_unavailable_malformed_and_schema_drift_fail_closed(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            binder = CodexThreadHostBinder()
            request = _request(root)
            cases = (
                (None, ThreadHostResolutionStatus.DIRECTORY_UNAVAILABLE),
                ("{", ThreadHostResolutionStatus.DIRECTORY_PAYLOAD_INVALID),
                ("[]", ThreadHostResolutionStatus.DIRECTORY_PAYLOAD_INVALID),
                (
                    _directory_payload((_codex_entry(str(root)),), schema_version=5),
                    ThreadHostResolutionStatus.DIRECTORY_PAYLOAD_INVALID,
                ),
                (
                    _directory_payload(
                        (_codex_entry(str(root), status="future-state"),)
                    ),
                    ThreadHostResolutionStatus.DIRECTORY_PAYLOAD_INVALID,
                ),
            )
            for payload, expected in cases:
                with self.subTest(expected=expected):
                    self.assertEqual(expected, binder.resolve(request, payload).status)

    def test_missing_ambiguous_project_host_and_activity_cells_are_finite(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            binder = CodexThreadHostBinder()
            request = _request(root)
            cases = (
                (
                    _directory_payload(
                        (_codex_entry(str(root), thread_id=_OTHER_THREAD_ID),)
                    ),
                    ThreadHostResolutionStatus.THREAD_NOT_FOUND,
                ),
                (
                    _directory_payload(
                        (
                            _codex_entry(str(root)),
                            _codex_entry(str(root), host_id="local-second"),
                        )
                    ),
                    ThreadHostResolutionStatus.AMBIGUOUS_THREAD,
                ),
                (
                    _directory_payload((_codex_entry(str(root), project_id=None),)),
                    ThreadHostResolutionStatus.PROJECT_REQUIRED,
                ),
                (
                    _directory_payload(
                        (_codex_entry(str(root), project_id=_OTHER_PROJECT_ID),)
                    ),
                    ThreadHostResolutionStatus.PROJECT_MISMATCH,
                ),
                (
                    _directory_payload(
                        (_codex_entry(str(root)),),
                        unavailable_hosts=("local",),
                    ),
                    ThreadHostResolutionStatus.HOST_UNAVAILABLE,
                ),
                (
                    _directory_payload((_codex_entry(str(root), status="notLoaded"),)),
                    ThreadHostResolutionStatus.THREAD_NOT_READY,
                ),
            )
            for payload, expected in cases:
                with self.subTest(expected=expected):
                    self.assertEqual(expected, binder.resolve(request, payload).status)

    def test_workspace_requires_exact_existing_root_and_accepts_slash_variation(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            container = Path(temporary_directory).resolve(strict=True)
            root = container / "project"
            child = root / "child"
            sibling = container / "sibling"
            prefix_similar = container / "project-copy"
            for directory in (root, child, sibling, prefix_similar):
                directory.mkdir()
            request = _request(root)
            binder = CodexThreadHostBinder()
            accepted = str(root).replace("\\", "/")
            self.assertEqual(
                ThreadHostResolutionStatus.RESOLVED,
                binder.resolve(
                    request,
                    _directory_payload((_codex_entry(accepted),)),
                ).status,
            )
            rejected = (
                str(container),
                str(child),
                str(sibling),
                str(prefix_similar),
                str(root) + "\\..\\project",
                "relative\\project",
                "file:///D:/project",
                str(container / "missing"),
            )
            for cwd in rejected:
                with self.subTest(cwd=cwd):
                    result = binder.resolve(
                        request,
                        _directory_payload((_codex_entry(cwd),)),
                    )
                    self.assertEqual(
                        ThreadHostResolutionStatus.WORKSPACE_MISMATCH,
                        result.status,
                    )

    def test_readback_unavailable_invalid_mismatch_and_not_ready_fail_closed(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            container = Path(temporary_directory).resolve(strict=True)
            root = container / "project"
            wrong_root = container / "other"
            root.mkdir()
            wrong_root.mkdir()
            request = _request(root)
            directory = _directory_payload((_codex_entry(str(root)),))
            binder = CodexThreadHostBinder()
            cases = (
                (None, ThreadHostBindingStatus.READBACK_UNAVAILABLE),
                ("{", ThreadHostBindingStatus.READBACK_PAYLOAD_INVALID),
                (
                    _readback_payload(str(root), schema_version=2),
                    ThreadHostBindingStatus.READBACK_PAYLOAD_INVALID,
                ),
                (
                    _readback_payload(str(root), thread_id=_OTHER_THREAD_ID),
                    ThreadHostBindingStatus.READBACK_MISMATCH,
                ),
                (
                    _readback_payload(str(root), host_id="other-host"),
                    ThreadHostBindingStatus.READBACK_MISMATCH,
                ),
                (
                    _readback_payload(str(root), project_id=_OTHER_PROJECT_ID),
                    ThreadHostBindingStatus.READBACK_MISMATCH,
                ),
                (
                    _readback_payload(str(wrong_root)),
                    ThreadHostBindingStatus.READBACK_MISMATCH,
                ),
                (
                    _readback_payload(str(root), status="notLoaded"),
                    ThreadHostBindingStatus.THREAD_NOT_READY,
                ),
            )
            for payload, expected in cases:
                with self.subTest(expected=expected):
                    self.assertEqual(
                        expected,
                        binder.bind(request, directory, payload).status,
                    )

    def test_resolution_failures_propagate_without_readback_authority(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            request = _request(root)
            directory = _directory_payload(
                (_codex_entry(str(root), project_id=None),)
            )
            result = CodexThreadHostBinder().bind(
                request,
                directory,
                _readback_payload(str(root)),
            )
            self.assertEqual(ThreadHostBindingStatus.PROJECT_REQUIRED, result.status)
            self.assertIsNone(result.binding)


class CodexThreadHostContractTests(unittest.TestCase):
    def test_request_requires_active_receipt_matching_task_and_resolved_root(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            with self.assertRaises(ValueError):
                ResolvedWorkspaceRoot(Path("relative-project"))
            with self.assertRaises(ValidationError):
                CodexThreadHostBindingRequest(
                    receipt=_receipt(),
                    task_id=_THREAD_ID,
                    thread_id=_OTHER_THREAD_ID,
                    codex_project_id=_PROJECT_ID,
                    workspace_root=ResolvedWorkspaceRoot(root),
                )
            with self.assertRaises(ValueError):
                CodexThreadHostBindingRequest(
                    receipt=_receipt(ReceiptLifecycle.CLOSED),
                    task_id=_THREAD_ID,
                    thread_id=_THREAD_ID,
                    codex_project_id=_PROJECT_ID,
                    workspace_root=ResolvedWorkspaceRoot(root),
                )

    def test_public_result_rejects_extra_and_contradictory_shapes(self) -> None:
        with self.assertRaises(ValidationError):
            CodexThreadHostBindingResult.model_validate(
                {
                    "status": "READBACK_UNAVAILABLE",
                    "failure": "READBACK_UNAVAILABLE",
                    "extra": "forbidden",
                }
            )
        with self.assertRaises(ValidationError):
            CodexThreadHostBindingResult.model_validate(
                {
                    "status": "BOUND",
                    "failure": "READBACK_UNAVAILABLE",
                }
            )

    def test_codex_project_identity_accepts_local_and_worktree_forms_only(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            uuid_project_request = CodexThreadHostBindingRequest(
                receipt=_receipt(),
                task_id=_THREAD_ID,
                thread_id=_THREAD_ID,
                codex_project_id="6d2ebb66-1ae7-48b4-96da-53ffba88ef1f",
                workspace_root=ResolvedWorkspaceRoot(root),
            )
            self.assertEqual(
                "6d2ebb66-1ae7-48b4-96da-53ffba88ef1f",
                uuid_project_request.codex_project_id,
            )
            with self.assertRaises(ValidationError):
                CodexThreadHostBindingRequest(
                    receipt=_receipt(),
                    task_id=_THREAD_ID,
                    thread_id=_THREAD_ID,
                    codex_project_id="arbitrary-project-name",
                    workspace_root=ResolvedWorkspaceRoot(root),
                )

    def test_source_has_no_effect_polling_or_dynamic_type_escape(self) -> None:
        source_paths = (
            _ROOT / "library" / "workflow_router" / "thread_host_contracts.py",
            _ROOT / "library" / "local_orchestration" / "codex_thread_host_binding.py",
        )
        forbidden_tokens = (
            "Any",
            "object",
            "cast(",
            "model_construct",
            "model_copy(",
            "type: ignore",
            "getattr(",
            "except Exception",
            "send_message_to_thread",
            "create_thread",
            "wait_threads",
            "heartbeat",
        )
        forbidden_imports = {
            "requests",
            "socket",
            "subprocess",
            "threading",
            "time",
        }
        for source_path in source_paths:
            source = source_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            self.assertFalse(any(token in source for token in forbidden_tokens))
            imported_roots = {
                alias.name.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            imported_roots.update(
                node.module.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module is not None
            )
            self.assertTrue(imported_roots.isdisjoint(forbidden_imports))


if __name__ == "__main__":
    unittest.main()
