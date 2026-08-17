"""Acceptance tests for one-shot receipt-bound Codex thread dispatch."""

from __future__ import annotations

import ast
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Event, Lock
import unittest

from pydantic import ValidationError

from library.local_orchestration import (
    ApprovedDispatchArtifactRecord,
    ApprovedDispatchArtifactRegisterRequest,
    CodexThreadActivity,
    CodexThreadDispatchClaimRequest,
    CodexThreadDispatchCommand,
    CodexThreadDispatchCoordinator,
    CodexThreadDispatchEffectResult,
    CodexThreadDispatchEffectStatus,
    CodexThreadDispatchRequest,
    CodexThreadDispatchStatus,
    CodexThreadHostBinding,
    CodexThreadHostProbeTarget,
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
    LiveDispatchMetadataStore,
    ReceiptLifecycle,
    ThreadDispatchAttemptStore,
    TicketReceipt,
    TicketReceiptIssueRequest,
    dispatch_claim_identity,
    derive_thread_host_binding_digest,
)


_ROOT = Path(__file__).resolve().parents[1]
_CHECKPOINT_NAME = "live-dispatch-metadata-v1.json"
_DIGEST = "sha256_" + ("a" * 64)
_READBACK_DIGEST = "sha256_" + ("b" * 64)
_THREAD_ID = "019ffb0c-c9c7-7b30-b614-02dea7ed9042"
_PROJECT_ID = "6d2ebb66-1ae7-48b4-96da-53ffba88ef1f"


def _receipt(
    lifecycle: ReceiptLifecycle = ReceiptLifecycle.ACTIVE,
    correlation_id: str = "corr-thread-dispatch-r03-01",
) -> TicketReceipt:
    return TicketReceipt(
        project_id="prj_0123456789abcdef",
        receipt_id="receipt-thread-dispatch-r03-01",
        ticket_reference="ticket-thread-dispatch-r03-01",
        ticket_revision="rev-0123456789abcdef",
        ticket_digest=_DIGEST,
        ticket_document_commit="0123456789abcdef",
        handoff_reference="handoff-thread-dispatch-r03-01",
        handoff_revision="rev-fedcba9876543210",
        handoff_digest=_DIGEST,
        handoff_document_commit="fedcba9876543210",
        implementation_owner_id="role-implementation-owner-1",
        expected_return="return-implementation-completed",
        descriptor_binding="descriptor-thread-dispatch-r03-01",
        correlation_id=correlation_id,
        dispatch_question_id="question-thread-dispatch-r03-01",
        worktree_fingerprint="worktree-implementation-01",
        branch_fingerprint="branch-livedispatch-01",
        lifecycle=lifecycle,
    )


def _binding(
    receipt: TicketReceipt,
    *,
    ticket_reference: str | None = None,
) -> CodexThreadHostBinding:
    target = CodexThreadHostProbeTarget(
        router_project_id=receipt.project_id,
        ticket_reference=ticket_reference or receipt.ticket_reference,
        receipt_id=receipt.receipt_id,
        task_id=_THREAD_ID,
        thread_id=_THREAD_ID,
        host_id="local",
        codex_project_id=_PROJECT_ID,
        worktree_fingerprint=receipt.worktree_fingerprint,
        branch_fingerprint=receipt.branch_fingerprint,
        activity=CodexThreadActivity.IDLE,
        directory_observation_digest=_DIGEST,
    )
    return CodexThreadHostBinding(
        target=target,
        readback_observation_digest=_READBACK_DIGEST,
        binding_digest=derive_thread_host_binding_digest(
            target,
            _READBACK_DIGEST,
        ),
    )


def _request(
    *,
    attempt_id: str = "attempt-thread-dispatch-01",
    receipt: TicketReceipt | None = None,
) -> CodexThreadDispatchRequest:
    exact_receipt = receipt or _receipt()
    return CodexThreadDispatchRequest(
        attempt_id=attempt_id,
        receipt=exact_receipt,
        binding=_binding(exact_receipt),
    )


def _store(
    root: Path,
    *,
    receipt: TicketReceipt | None = None,
    seed_receipt: bool = True,
) -> ThreadDispatchAttemptStore:
    boundary = LiveDispatchMetadataBoundary(
        JohnnyMetadataRoot(root.resolve(strict=True))
    )
    if seed_receipt:
        canonical = receipt or _receipt()
        artifact = ApprovedDispatchArtifactRecord(
            project_id=canonical.project_id,
            ticket_reference=canonical.ticket_reference,
            ticket_revision=canonical.ticket_revision,
            ticket_digest=canonical.ticket_digest,
            ticket_document_commit=canonical.ticket_document_commit,
            handoff_reference=canonical.handoff_reference,
            handoff_revision=canonical.handoff_revision,
            handoff_digest=canonical.handoff_digest,
            handoff_document_commit=canonical.handoff_document_commit,
            implementation_owner_id=canonical.implementation_owner_id,
            expected_return=canonical.expected_return,
            descriptor_binding=canonical.descriptor_binding,
        )
        metadata_store = LiveDispatchMetadataStore(boundary)
        metadata_store.register_artifact(
            ApprovedDispatchArtifactRegisterRequest(artifact=artifact)
        )
        metadata_store.issue_receipt(
            TicketReceiptIssueRequest(
                artifact_identity=artifact.identity,
                ticket_revision=canonical.ticket_revision,
                ticket_digest=canonical.ticket_digest,
                ticket_document_commit=canonical.ticket_document_commit,
                handoff_revision=canonical.handoff_revision,
                handoff_digest=canonical.handoff_digest,
                handoff_document_commit=canonical.handoff_document_commit,
                receipt_id=canonical.receipt_id,
                expected_return=canonical.expected_return,
                descriptor_binding=canonical.descriptor_binding,
                correlation_id=canonical.correlation_id,
                dispatch_question_id=canonical.dispatch_question_id,
                worktree_fingerprint=canonical.worktree_fingerprint,
                branch_fingerprint=canonical.branch_fingerprint,
            )
        )
    return ThreadDispatchAttemptStore(boundary)


class RecordingPort:
    def __init__(
        self,
        effect: CodexThreadDispatchEffectResult,
        checkpoint_path: Path | None = None,
    ) -> None:
        self.effect = effect
        self.checkpoint_path = checkpoint_path
        self.commands: list[CodexThreadDispatchCommand] = []
        self.lifecycle_seen_during_send: str | None = None

    def send(
        self,
        command: CodexThreadDispatchCommand,
    ) -> CodexThreadDispatchEffectResult:
        self.commands.append(command)
        if self.checkpoint_path is not None:
            checkpoint = json.loads(
                self.checkpoint_path.read_text(encoding="utf-8")
            )
            attempts = checkpoint["dispatch_attempts"]
            self.lifecycle_seen_during_send = attempts[0]["lifecycle"]
        return self.effect


class RaisingPort:
    def __init__(self) -> None:
        self.calls = 0

    def send(
        self,
        command: CodexThreadDispatchCommand,
    ) -> CodexThreadDispatchEffectResult:
        del command
        self.calls += 1
        raise RuntimeError("untrusted host detail")


class TrapPort:
    def __init__(self) -> None:
        self.calls = 0

    def send(
        self,
        command: CodexThreadDispatchCommand,
    ) -> CodexThreadDispatchEffectResult:
        del command
        self.calls += 1
        raise AssertionError("replayed dispatch reached the host")


class BlockingPort:
    def __init__(self) -> None:
        self.started = Event()
        self.release = Event()
        self._lock = Lock()
        self.calls = 0

    def send(
        self,
        command: CodexThreadDispatchCommand,
    ) -> CodexThreadDispatchEffectResult:
        del command
        with self._lock:
            self.calls += 1
        self.started.set()
        if not self.release.wait(timeout=10):
            raise RuntimeError("test release timeout")
        return CodexThreadDispatchEffectResult(
            status=CodexThreadDispatchEffectStatus.HOST_ACCEPTED,
            delivery_reference="delivery-thread-dispatch-01",
        )


class DerivedEffectResult(CodexThreadDispatchEffectResult):
    """An exact-shaped subclass that cannot cross the host boundary."""


_CHILD_CLAIM_SCRIPT = """
from pathlib import Path
import sys
from library.local_orchestration import (
    CodexThreadDispatchClaimRequest,
    CodexThreadDispatchRequest,
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
    ThreadDispatchAttemptStore,
    dispatch_claim_identity,
)
request = CodexThreadDispatchRequest.model_validate_json(sys.argv[2], strict=True)
store = ThreadDispatchAttemptStore(
    LiveDispatchMetadataBoundary(JohnnyMetadataRoot(Path(sys.argv[1]).resolve(strict=True)))
)
result = store.claim_dispatch_attempt(
    CodexThreadDispatchClaimRequest(identity=dispatch_claim_identity(request))
)
print(result.status.value)
"""


class CodexThreadDispatchTests(unittest.TestCase):
    def test_claim_precedes_one_host_effect_and_terminal_result_is_durable(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            checkpoint_path = root / _CHECKPOINT_NAME
            port = RecordingPort(
                CodexThreadDispatchEffectResult(
                    status=CodexThreadDispatchEffectStatus.HOST_ACCEPTED,
                    delivery_reference="delivery-thread-dispatch-01",
                ),
                checkpoint_path,
            )
            request = _request()
            result = CodexThreadDispatchCoordinator(_store(root), port).dispatch(
                request
            )

            self.assertEqual(CodexThreadDispatchStatus.HOST_ACCEPTED, result.status)
            self.assertEqual(1, len(port.commands))
            self.assertEqual("CLAIMED", port.lifecycle_seen_during_send)
            command = port.commands[0]
            self.assertEqual(_THREAD_ID, command.thread_id)
            self.assertEqual("local", command.host_id)
            self.assertIn("protocol=CODEX_THREAD_DISPATCH_V1\n", command.prompt)
            self.assertIn("receipt_id=" + request.receipt.receipt_id, command.prompt)
            self.assertNotIn("C:\\", command.prompt)

            serialized = checkpoint_path.read_bytes()
            self.assertNotIn(b'"prompt"', serialized)
            self.assertNotIn(str(root).encode("utf-8"), serialized)
            trap = TrapPort()
            repeated = CodexThreadDispatchCoordinator(
                _store(root), trap
            ).dispatch(request)
            self.assertEqual(
                CodexThreadDispatchStatus.HOST_ACCEPTED,
                repeated.status,
            )
            self.assertEqual(0, trap.calls)

    def test_host_exception_is_durably_uncertain_and_never_retried(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            request = _request()
            raising = RaisingPort()
            first = CodexThreadDispatchCoordinator(
                _store(root), raising
            ).dispatch(request)
            self.assertEqual(
                CodexThreadDispatchStatus.EFFECT_UNCERTAIN,
                first.status,
            )
            self.assertEqual(1, raising.calls)
            self.assertNotIn("untrusted host detail", first.model_dump_json())

            trap = TrapPort()
            repeated = CodexThreadDispatchCoordinator(
                _store(root), trap
            ).dispatch(request)
            self.assertEqual(
                CodexThreadDispatchStatus.EFFECT_UNCERTAIN,
                repeated.status,
            )
            self.assertEqual(0, trap.calls)

    def test_no_effect_and_malformed_effect_are_finite_and_non_retryable(self) -> None:
        effects = (
            (
                CodexThreadDispatchEffectResult(
                    status=CodexThreadDispatchEffectStatus.NO_EFFECT
                ),
                CodexThreadDispatchStatus.NO_EFFECT,
            ),
            (
                DerivedEffectResult(
                    status=CodexThreadDispatchEffectStatus.HOST_ACCEPTED,
                    delivery_reference="delivery-thread-dispatch-derived",
                ),
                CodexThreadDispatchStatus.EFFECT_UNCERTAIN,
            ),
        )
        for index, (effect, expected) in enumerate(effects, start=1):
            with self.subTest(expected=expected):
                with TemporaryDirectory() as temporary_directory:
                    root = Path(temporary_directory).resolve(strict=True)
                    port = RecordingPort(effect)
                    request = _request(
                        attempt_id=f"attempt-thread-dispatch-0{index}"
                    )
                    result = CodexThreadDispatchCoordinator(
                        _store(root), port
                    ).dispatch(request)
                    self.assertEqual(expected, result.status)
                    self.assertEqual(1, len(port.commands))
                    trap = TrapPort()
                    repeated = CodexThreadDispatchCoordinator(
                        _store(root), trap
                    ).dispatch(request)
                    self.assertEqual(expected, repeated.status)
                    self.assertEqual(0, trap.calls)

    def test_concurrent_reentry_calls_the_host_once(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            request = _request()
            port = BlockingPort()
            coordinator = CodexThreadDispatchCoordinator(_store(root), port)
            with ThreadPoolExecutor(max_workers=1) as executor:
                first_future = executor.submit(coordinator.dispatch, request)
                self.assertTrue(port.started.wait(timeout=10))
                second = CodexThreadDispatchCoordinator(
                    _store(root), port
                ).dispatch(request)
                port.release.set()
                first = first_future.result(timeout=10)
            self.assertEqual(CodexThreadDispatchStatus.HOST_ACCEPTED, first.status)
            self.assertEqual(
                CodexThreadDispatchStatus.EFFECT_UNCERTAIN,
                second.status,
            )
            self.assertEqual(1, port.calls)

    def test_different_attempt_for_same_receipt_conflicts_before_host(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            accepted = RecordingPort(
                CodexThreadDispatchEffectResult(
                    status=CodexThreadDispatchEffectStatus.HOST_ACCEPTED,
                    delivery_reference="delivery-thread-dispatch-01",
                )
            )
            first = CodexThreadDispatchCoordinator(
                _store(root), accepted
            ).dispatch(_request())
            self.assertEqual(CodexThreadDispatchStatus.HOST_ACCEPTED, first.status)

            trap = TrapPort()
            conflict = CodexThreadDispatchCoordinator(
                _store(root), trap
            ).dispatch(_request(attempt_id="attempt-thread-dispatch-02"))
            self.assertEqual(
                CodexThreadDispatchStatus.ATTEMPT_CONFLICT,
                conflict.status,
            )
            self.assertEqual(0, trap.calls)

    def test_claim_survives_process_exit_and_restart_never_retries(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            request = _request()
            _store(root, receipt=request.receipt)
            completed = subprocess.run(
                (
                    sys.executable,
                    "-B",
                    "-c",
                    _CHILD_CLAIM_SCRIPT,
                    str(root),
                    request.model_dump_json(),
                ),
                cwd=_ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=20,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("CLAIMED", completed.stdout.strip())

            trap = TrapPort()
            recovered = CodexThreadDispatchCoordinator(
                _store(root), trap
            ).dispatch(request)
            self.assertEqual(
                CodexThreadDispatchStatus.EFFECT_UNCERTAIN,
                recovered.status,
            )
            self.assertEqual(0, trap.calls)

    def test_corrupt_checkpoint_fails_before_host_and_is_unchanged(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            checkpoint = root / _CHECKPOINT_NAME
            corrupt = b'{"schema_revision":'
            checkpoint.write_bytes(corrupt)
            trap = TrapPort()
            result = CodexThreadDispatchCoordinator(
                _store(root, seed_receipt=False), trap
            ).dispatch(_request())
            self.assertEqual(
                CodexThreadDispatchStatus.STORAGE_UNAVAILABLE,
                result.status,
            )
            self.assertEqual(0, trap.calls)
            self.assertEqual(corrupt, checkpoint.read_bytes())

    def test_missing_canonical_receipt_fails_before_host(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            trap = TrapPort()
            result = CodexThreadDispatchCoordinator(
                _store(root, seed_receipt=False), trap
            ).dispatch(_request())
            self.assertEqual(
                CodexThreadDispatchStatus.RECEIPT_UNAVAILABLE,
                result.status,
            )
            self.assertEqual(0, trap.calls)

        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            altered = _receipt(correlation_id="corr-thread-dispatch-altered")
            trap = TrapPort()
            result = CodexThreadDispatchCoordinator(
                _store(root), trap
            ).dispatch(_request(receipt=altered))
            self.assertEqual(
                CodexThreadDispatchStatus.RECEIPT_UNAVAILABLE,
                result.status,
            )
            self.assertEqual(0, trap.calls)


class CodexThreadDispatchContractTests(unittest.TestCase):
    def test_request_rejects_closed_receipt_and_mismatched_binding(self) -> None:
        closed = _receipt(ReceiptLifecycle.CLOSED)
        with self.assertRaises(ValidationError):
            CodexThreadDispatchRequest(
                attempt_id="attempt-thread-dispatch-closed",
                receipt=closed,
                binding=_binding(closed),
            )
        receipt = _receipt()
        with self.assertRaises(ValidationError):
            CodexThreadDispatchRequest(
                attempt_id="attempt-thread-dispatch-mismatch",
                receipt=receipt,
                binding=_binding(
                    receipt,
                    ticket_reference="ticket-thread-dispatch-other",
                ),
            )

    def test_claim_and_effect_shapes_reject_extra_or_contradictory_state(self) -> None:
        request = _request()
        identity = dispatch_claim_identity(request)
        with self.assertRaises(ValidationError):
            CodexThreadDispatchClaimRequest.model_validate(
                {"identity": identity.model_dump(), "extra": "forbidden"}
            )
        with self.assertRaises(ValidationError):
            CodexThreadDispatchEffectResult(
                status=CodexThreadDispatchEffectStatus.NO_EFFECT,
                delivery_reference="delivery-thread-dispatch-invalid",
            )
        with self.assertRaises(ValidationError):
            CodexThreadDispatchEffectResult(
                status=CodexThreadDispatchEffectStatus.HOST_ACCEPTED
            )

    def test_source_has_no_polling_heartbeat_or_direct_host_capability(self) -> None:
        source_paths = (
            _ROOT
            / "library"
            / "workflow_router"
            / "thread_dispatch_contracts.py",
            _ROOT
            / "library"
            / "local_orchestration"
            / "codex_thread_dispatch.py",
        )
        forbidden_tokens = (
            "Any",
            "object",
            "cast(",
            "model_construct",
            "model_copy(",
            "type: ignore",
            "getattr(",
            "create_thread",
            "wait_threads",
            "heartbeat",
            "polling",
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
