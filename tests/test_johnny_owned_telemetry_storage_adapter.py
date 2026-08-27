"""High-assurance acceptance tests for the private lock-bound telemetry adapter."""

from __future__ import annotations

import ast
import hashlib
import json
import multiprocessing
import os
import unittest
from multiprocessing.synchronize import Event
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import library.local_orchestration.telemetry_storage.johnny_owned_adapter as adapter_module
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.telemetry_storage.contracts import (
    AppendTelemetryStorageRequest,
    CompletedAppendResponse,
    CompletedDetachResponse,
    CompletedReadResponse,
    CompletedUninstallResponse,
    CompletedValidateResponse,
    NoRecordTelemetryStorageRequest,
    TelemetryStorageDecision,
    TelemetryStorageFailure,
    TelemetryStorageLifecycle,
    TelemetryStorageLockAcquire,
    TelemetryStorageLockAcquired,
    TelemetryStorageLockContended,
    TelemetryStorageLockPort,
    TelemetryStorageLockRelease,
    TelemetryStorageLockReleaseFailed,
    TelemetryStorageLockReleased,
    TelemetryStorageLockRequest,
    TelemetryStorageLockToken,
    TelemetryStorageOperation,
    TelemetryStoragePort,
    TelemetryStorageReadPayload,
    TelemetryStorageRef,
    TelemetryStorageRequest,
    TelemetryStorageResponse,
)
from library.local_orchestration.telemetry_storage.local_lock_adapter import (
    LocalTelemetryStorageLockAdapter,
)
from library.local_orchestration.telemetry_storage.ownership_ledger import (
    LedgerResolutionDecision,
    LocalTelemetryOwnershipLedger,
    TelemetryOwnershipLedgerBoundaryRejected,
    TelemetryOwnershipLedgerClosed,
    TelemetryOwnershipLedgerFound,
    TelemetryOwnershipLedgerNotFound,
    TelemetryOwnershipLedgerOwnershipMismatch,
    TelemetryOwnershipLedgerPort,
    TelemetryOwnershipLedgerResult,
)
from library.workflow_router.contracts import (
    ConsumerFingerprint,
    DeliveryStage,
    ProcessStage,
)
from library.workflow_router.telemetry import (
    AgentUsage,
    ContextLoadMeasurement,
    ContextUsageRecord,
    JsonlContextUsageStore,
    RunAcceptance,
    TelemetryMode,
)


_ROOT = Path(__file__).resolve().parents[1]
_PROJECT = "prj_0123456789abcdef"
_REVISION = "rev-0123456789abcdef"
_NEXT_REVISION = "rev-fedcba9876543210"
_OTHER_REVISION = "rev-1111111111111111"
_DOMAIN = "johnny-telemetry-ownership-ledger-v1"
_TRANSACTION_DOMAIN = "telemetry-storage-revision-v1"


def _layout(root: str) -> JohnnyRootLayout:
    return JohnnyRootLayout(base=Path(root).resolve() / "johnny")


def _reference(
    *,
    storage_ref: str = "storage-alpha",
    project_id: str = _PROJECT,
    stream_id: str = "stream-alpha",
    ledger_ref: str = "ledger-alpha",
    revision: str = _REVISION,
    lifecycle: TelemetryStorageLifecycle = TelemetryStorageLifecycle.ACTIVE,
) -> TelemetryStorageRef:
    return TelemetryStorageRef(
        storage_ref=storage_ref,
        project_id=project_id,
        stream_id=stream_id,
        ownership_ledger_ref=ledger_ref,
        storage_revision=revision,
        lifecycle=lifecycle,
    )


def _entry_digest(reference: TelemetryStorageRef) -> str:
    material = "\0".join(
        (
            _DOMAIN,
            reference.storage_ref,
            reference.project_id,
            reference.stream_id,
            reference.ownership_ledger_ref,
        )
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _transaction_digest(reference: TelemetryStorageRef) -> str:
    material = "\0".join(
        (
            reference.storage_ref,
            reference.project_id,
            reference.stream_id,
            reference.ownership_ledger_ref,
        )
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _entry_path(layout: JohnnyRootLayout, reference: TelemetryStorageRef) -> Path:
    return (
        layout.telemetry_root
        / "ownership-ledger"
        / "entries"
        / f"{_entry_digest(reference)}.json"
    )


def _stream_path(layout: JohnnyRootLayout, locator: str = "streams/alpha.jsonl") -> Path:
    return layout.telemetry_root / locator


def _transaction_root(layout: JohnnyRootLayout, reference: TelemetryStorageRef) -> Path:
    return layout.telemetry_root / "storage-transactions" / _transaction_digest(reference)


def _json_entry(reference: TelemetryStorageRef, locator: str = "streams/alpha.jsonl") -> dict[str, object]:
    return {
        "storage_ref": {
            "storage_ref": reference.storage_ref,
            "project_id": reference.project_id,
            "stream_id": reference.stream_id,
            "ownership_ledger_ref": reference.ownership_ledger_ref,
            "storage_revision": reference.storage_revision,
            "lifecycle": reference.lifecycle.value,
        },
        "stream_locator": locator,
    }


def _write_json(path: Path, document: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def _seed_entry(
    layout: JohnnyRootLayout,
    reference: TelemetryStorageRef,
    *,
    locator: str = "streams/alpha.jsonl",
) -> Path:
    path = _entry_path(layout, reference)
    _write_json(path, {"schema_version": 1, "entry": _json_entry(reference, locator)})
    return path


def _record(run_id: str = "run-alpha") -> ContextUsageRecord:
    return ContextUsageRecord(
        run_id=run_id,
        comparison_group_id="comparison-alpha",
        attempt=1,
        project_snapshot_id="snapshot-alpha",
        mode=TelemetryMode.BASELINE,
        stage=ProcessStage.IMPLEMENT,
        delivery_stage=DeliveryStage.POC,
        agent=AgentUsage(
            provider="provider-alpha",
            model="model-alpha",
            consumer=ConsumerFingerprint(
                agent_profile="agent-alpha",
                profile_version="version-alpha",
                worktree_id="worktree-alpha",
                execution_id="execution-alpha",
            ),
            provider_input_tokens=10,
            provider_output_tokens=4,
            tool_read_count=1,
            retry_count=0,
            duration_ms=5,
        ),
        context=ContextLoadMeasurement(
            sources=(),
            declared_source_count=0,
            actual_source_count=0,
            undeclared_source_count=0,
            estimated_packet_tokens=0,
            token_budget=None,
            budget_exceeded=False,
            raw_text_in_shared_state=False,
        ),
        acceptance=RunAcceptance.PASSED,
        human_correction_required=False,
    )


def _canonical_records(records: tuple[ContextUsageRecord, ...]) -> bytes:
    if not records:
        return b""
    lines = tuple(
        json.dumps(record.model_dump(mode="json"), ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        for record in records
    )
    return ("\n".join(lines) + "\n").encode("utf-8")


def _expected_revision(
    reference: TelemetryStorageRef,
    operation: TelemetryStorageOperation,
    post_lifecycle: TelemetryStorageLifecycle,
    stream_locator: str,
    pre_raw: bytes,
    post_raw: bytes,
) -> str:
    material = "\0".join(
        (
            _TRANSACTION_DOMAIN,
            reference.storage_ref,
            reference.project_id,
            reference.stream_id,
            reference.ownership_ledger_ref,
            reference.storage_revision,
            operation.value,
            post_lifecycle.value,
            hashlib.sha256(stream_locator.encode("utf-8")).hexdigest(),
            hashlib.sha256(pre_raw).hexdigest(),
            hashlib.sha256(post_raw).hexdigest(),
        )
    )
    return f"rev-{hashlib.sha256(material.encode('utf-8')).hexdigest()}"


def _write_stream(layout: JohnnyRootLayout, records: tuple[ContextUsageRecord, ...]) -> Path:
    path = _stream_path(layout)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical_records(records))
    return path


def _append_request(reference: TelemetryStorageRef, record: ContextUsageRecord) -> AppendTelemetryStorageRequest:
    return AppendTelemetryStorageRequest(
        storage_ref=reference,
        expected_project_id=reference.project_id,
        expected_storage_revision=reference.storage_revision,
        record=record,
    )


def _no_record_request(
    reference: TelemetryStorageRef, operation: TelemetryStorageOperation
) -> NoRecordTelemetryStorageRequest:
    return NoRecordTelemetryStorageRequest(
        storage_ref=reference,
        expected_project_id=reference.project_id,
        expected_storage_revision=reference.storage_revision,
        operation=operation,
    )


def _require_failure(result: TelemetryStorageResponse) -> TelemetryStorageFailure:
    if not isinstance(result, TelemetryStorageFailure):
        raise AssertionError(f"expected failure, got {result!r}")
    return result


def _require_append(result: TelemetryStorageResponse) -> CompletedAppendResponse:
    if not isinstance(result, CompletedAppendResponse):
        raise AssertionError(f"expected append response, got {result!r}")
    return result


def _require_read(result: TelemetryStorageResponse) -> CompletedReadResponse:
    if not isinstance(result, CompletedReadResponse):
        raise AssertionError(f"expected read response, got {result!r}")
    return result


class FakeLock(TelemetryStorageLockPort):
    """Strict test lock seam; production adapter must never instantiate this shape."""

    def __init__(self, *, contended: bool = False, release_failed: bool = False) -> None:
        self.contended = contended
        self.release_failed = release_failed
        self.acquire_calls = 0
        self.release_calls = 0
        self.token: TelemetryStorageLockToken | None = None

    def try_acquire(self, request: TelemetryStorageLockRequest) -> TelemetryStorageLockAcquire:
        self.acquire_calls += 1
        if self.contended:
            return TelemetryStorageLockContended(
                storage_ref=request.storage_ref.storage_ref,
                storage_revision=request.storage_ref.storage_revision,
                failure_ref="contended-lock-alpha",
            )
        self.token = TelemetryStorageLockToken(
            lock_ref="lock-alpha",
            storage_ref=request.storage_ref.storage_ref,
            project_id=request.storage_ref.project_id,
            stream_id=request.storage_ref.stream_id,
            ownership_ledger_ref=request.storage_ref.ownership_ledger_ref,
            storage_revision=request.storage_ref.storage_revision,
        )
        return TelemetryStorageLockAcquired(lock_token=self.token)

    def release(self, token: TelemetryStorageLockToken) -> TelemetryStorageLockRelease:
        self.release_calls += 1
        if self.release_failed:
            return TelemetryStorageLockReleaseFailed(
                lock_ref=token.lock_ref,
                storage_ref=token.storage_ref,
                storage_revision=token.storage_revision,
                failure_ref="release-failed-alpha",
            )
        return TelemetryStorageLockReleased(
            lock_ref=token.lock_ref,
            storage_ref=token.storage_ref,
            storage_revision=token.storage_revision,
        )


class ToctouLedger(TelemetryOwnershipLedgerPort):
    """Return a changed under-lock state on the adapter's final admission."""

    def __init__(self, delegate: TelemetryOwnershipLedgerPort) -> None:
        self.delegate = delegate
        self.resolve_calls = 0

    def resolve(
        self,
        storage_ref: TelemetryStorageRef,
        expected_project_id: str,
        expected_storage_revision: str,
    ) -> TelemetryOwnershipLedgerResult:
        self.resolve_calls += 1
        if self.resolve_calls == 2:
            return TelemetryOwnershipLedgerClosed()
        return self.delegate.resolve(storage_ref, expected_project_id, expected_storage_revision)

    def resolve_current(self, storage_ref: TelemetryStorageRef) -> TelemetryOwnershipLedgerResult:
        return self.delegate.resolve_current(storage_ref)

    def compare_and_swap(
        self,
        storage_ref: TelemetryStorageRef,
        expected_project_id: str,
        expected_storage_revision: str,
        next_lifecycle: TelemetryStorageLifecycle,
        next_storage_revision: str,
    ) -> TelemetryOwnershipLedgerResult:
        return self.delegate.compare_and_swap(
            storage_ref,
            expected_project_id,
            expected_storage_revision,
            next_lifecycle,
            next_storage_revision,
        )


def _process_worker(
    root: str,
    reference_data: dict[str, str],
    operation: str,
    result_queue: multiprocessing.queues.Queue[tuple[str, str]],
) -> None:
    reference = _reference(
        storage_ref=reference_data["storage_ref"],
        project_id=reference_data["project_id"],
        stream_id=reference_data["stream_id"],
        ledger_ref=reference_data["ownership_ledger_ref"],
        revision=reference_data["storage_revision"],
    )
    layout = _layout(root)
    adapter = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
        layout,
        LocalTelemetryOwnershipLedger(layout),
        LocalTelemetryStorageLockAdapter(layout),
    )
    result = adapter.execute(_no_record_request(reference, TelemetryStorageOperation(operation)))
    result_queue.put((reference.stream_id, result.decision.value))


def _lock_holder_worker(
    root: str,
    reference_data: dict[str, str],
    ready: Event,
    release: Event,
) -> None:
    reference = _reference(
        storage_ref=reference_data["storage_ref"],
        project_id=reference_data["project_id"],
        stream_id=reference_data["stream_id"],
        ledger_ref=reference_data["ownership_ledger_ref"],
        revision=reference_data["storage_revision"],
    )
    layout = _layout(root)
    lock = LocalTelemetryStorageLockAdapter(layout)
    request = TelemetryStorageLockRequest(
        storage_ref=reference,
        expected_project_id=reference.project_id,
        expected_storage_revision=reference.storage_revision,
    )
    acquired = lock.try_acquire(request)
    ready.set()
    if isinstance(acquired, TelemetryStorageLockAcquired):
        release.wait(timeout=10)
        lock.release(acquired.lock_token)


def _reference_data(reference: TelemetryStorageRef) -> dict[str, str]:
    return {
        "storage_ref": reference.storage_ref,
        "project_id": reference.project_id,
        "stream_id": reference.stream_id,
        "ownership_ledger_ref": reference.ownership_ledger_ref,
        "storage_revision": reference.storage_revision,
    }


class TelemetryAdapterBehaviorTests(unittest.TestCase):
    """TTA1-TTA5: public operations, lock admission and transaction recovery."""

    def test_tta1_append_and_read_are_canonical_and_revision_bound(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            reference = _reference()
            _seed_entry(layout, reference)
            stream = _write_stream(layout, (_record("run-before"),))
            pre_raw = stream.read_bytes()
            post_raw = _canonical_records((_record("run-before"), _record()))
            lock = FakeLock()
            adapter = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
                layout, LocalTelemetryOwnershipLedger(layout), lock
            )
            appended = _require_append(adapter.execute(_append_request(reference, _record())))
            self.assertEqual(appended.lifecycle, TelemetryStorageLifecycle.ACTIVE)
            self.assertEqual(appended.record_count, 2)
            self.assertEqual(
                appended.storage_revision,
                _expected_revision(
                    reference,
                    TelemetryStorageOperation.APPEND,
                    TelemetryStorageLifecycle.ACTIVE,
                    "streams/alpha.jsonl",
                    pre_raw,
                    post_raw,
                ),
            )
            self.assertNotIn(str(layout.base), appended.model_dump_json())
            self.assertEqual(lock.acquire_calls, 1)
            self.assertEqual(lock.release_calls, 1)
            current = _reference(revision=appended.storage_revision)
            read = _require_read(
                adapter.execute(_no_record_request(current, TelemetryStorageOperation.READ))
            )
            self.assertEqual(read.record_count, 2)
            self.assertIsInstance(read.read_payload, TelemetryStorageReadPayload)
            self.assertEqual(stream.read_bytes(), _canonical_records(read.read_payload.records))
            self.assertFalse((layout.telemetry_root / "storage-transactions").exists())

    def test_tta2_admission_contention_and_under_lock_toctou_have_zero_codec_effect(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            reference = _reference()
            _seed_entry(layout, reference)
            stream = _stream_path(layout)
            contended = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
                layout, LocalTelemetryOwnershipLedger(layout), FakeLock(contended=True)
            )
            result = _require_failure(contended.execute(_append_request(reference, _record())))
            self.assertEqual(result.decision, TelemetryStorageDecision.LOCK_CONTENDED)
            self.assertFalse(stream.exists())
            self.assertFalse((layout.telemetry_root / "storage-transactions").exists())

            delegate = LocalTelemetryOwnershipLedger(layout)
            toctou = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
                layout, ToctouLedger(delegate), FakeLock()
            )
            changed = _require_failure(toctou.execute(_append_request(reference, _record())))
            self.assertEqual(changed.decision, TelemetryStorageDecision.STORAGE_CLOSED)
            self.assertFalse(stream.exists())
            self.assertFalse((layout.telemetry_root / "storage-transactions").exists())

            _seed_entry(layout, reference)
            context = multiprocessing.get_context("spawn")
            ready = context.Event()
            release = context.Event()
            holder = context.Process(
                target=_lock_holder_worker,
                args=(temporary, _reference_data(reference), ready, release),
            )
            holder.start()
            try:
                self.assertTrue(ready.wait(timeout=10))
                independent = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
                    layout,
                    LocalTelemetryOwnershipLedger(layout),
                    LocalTelemetryStorageLockAdapter(layout),
                )
                held = _require_failure(
                    independent.execute(_append_request(reference, _record()))
                )
                self.assertEqual(held.decision, TelemetryStorageDecision.LOCK_CONTENDED)
                self.assertFalse(stream.exists())
                self.assertFalse((layout.telemetry_root / "storage-transactions").exists())
            finally:
                release.set()
                holder.join(timeout=10)
                self.assertFalse(holder.is_alive())

            missing_layout = _layout(temporary + "-missing")
            missing = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
                missing_layout, LocalTelemetryOwnershipLedger(missing_layout), FakeLock()
            )
            missing_result = _require_failure(missing.execute(_append_request(reference, _record())))
            self.assertEqual(missing_result.decision, TelemetryStorageDecision.STORAGE_OWNERSHIP_MISMATCH)

    def test_tta3_validate_detach_and_uninstall_use_finite_responses(self) -> None:
        with TemporaryDirectory() as temporary:
            for operation, lifecycle in (
                (
                    TelemetryStorageOperation.DETACH,
                    TelemetryStorageLifecycle.DETACHED,
                ),
                (
                    TelemetryStorageOperation.UNINSTALL,
                    TelemetryStorageLifecycle.REMOVED,
                ),
            ):
                with self.subTest(operation=operation):
                    root = temporary + operation.value
                    layout = _layout(root)
                    reference = _reference()
                    _seed_entry(layout, reference)
                    _write_stream(layout, (_record(),))
                    unrelated = _reference(storage_ref="storage-beta", stream_id="stream-beta", ledger_ref="ledger-beta")
                    unrelated_path = _seed_entry(layout, unrelated, locator="streams/beta.jsonl")
                    _write_stream_at = layout.telemetry_root / "streams" / "beta.jsonl"
                    _write_stream_at.parent.mkdir(parents=True, exist_ok=True)
                    _write_stream_at.write_bytes(_canonical_records((_record("run-beta"),)))
                    adapter = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
                        layout, LocalTelemetryOwnershipLedger(layout), FakeLock()
                    )
                    result = adapter.execute(_no_record_request(reference, operation))
                    if operation is TelemetryStorageOperation.DETACH:
                        self.assertIsInstance(result, CompletedDetachResponse)
                    else:
                        self.assertIsInstance(result, CompletedUninstallResponse)
                    if not isinstance(result, (CompletedDetachResponse, CompletedUninstallResponse)):
                        raise AssertionError(f"expected removal response, got {result!r}")
                    self.assertEqual(result.lifecycle, lifecycle)
                    self.assertEqual(result.record_count, 1)
                    self.assertFalse(_stream_path(layout).exists())
                    self.assertTrue(unrelated_path.exists())
                    self.assertTrue(_write_stream_at.exists())

            with TemporaryDirectory() as validation_root:
                layout = _layout(validation_root)
                reference = _reference()
                _seed_entry(layout, reference)
                _write_stream(layout, (_record(),))
                adapter = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
                    layout, LocalTelemetryOwnershipLedger(layout), FakeLock()
                )
                validation = adapter.execute(
                    _no_record_request(reference, TelemetryStorageOperation.VALIDATE)
                )
                self.assertIsInstance(validation, CompletedValidateResponse)
                assert isinstance(validation, CompletedValidateResponse)
                self.assertFalse((layout.telemetry_root / "validation-report.json").exists())
                self.assertTrue(validation.validation_report_ref.startswith("validation-"))
                repeat_validation = adapter.execute(
                    _no_record_request(reference, TelemetryStorageOperation.VALIDATE)
                )
                self.assertIsInstance(repeat_validation, CompletedValidateResponse)
                assert isinstance(repeat_validation, CompletedValidateResponse)
                self.assertEqual(
                    validation.validation_report_ref,
                    repeat_validation.validation_report_ref,
                )

                _stream_path(layout).write_text("not-json\n", encoding="utf-8")
                invalid = _require_failure(
                    adapter.execute(_no_record_request(reference, TelemetryStorageOperation.VALIDATE))
                )
                self.assertEqual(invalid.decision, TelemetryStorageDecision.RECORD_INVALID)

    def test_tta4_recovery_accepts_only_complete_pre_post_grid(self) -> None:
        with TemporaryDirectory() as temporary:
            cases = (
                "BEFORE_JOURNAL",
                "AFTER_PREPARED",
                "AFTER_STREAM_APPLIED",
                "AFTER_LEDGER_CAS",
                "AFTER_LEDGER_APPLIED",
            )
            for case in cases:
                with self.subTest(case=case):
                    root = temporary + case
                    layout = _layout(root)
                    reference = _reference()
                    _seed_entry(layout, reference)
                    stream = _write_stream(layout, (_record("run-before"),))
                    original = stream.read_bytes()
                    post_records = (_record("run-before"), _record())
                    post_raw = _canonical_records(post_records)
                    ledger = LocalTelemetryOwnershipLedger(layout)
                    adapter = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
                        layout, ledger, FakeLock()
                    )
                    original_write_journal = adapter._write_journal
                    original_apply_stream = adapter._apply_stream

                    def fail_write(journal: adapter_module._TransactionJournal) -> None:
                        if (
                            case == "BEFORE_JOURNAL"
                            or case == "AFTER_STREAM_APPLIED"
                            and journal.phase is adapter_module._TransactionPhase.STREAM_APPLIED
                            or case == "AFTER_LEDGER_CAS"
                            and journal.phase is adapter_module._TransactionPhase.LEDGER_APPLIED
                        ):
                            raise RuntimeError("forced journal interruption")
                        original_write_journal(journal)

                    def fail_after_apply(
                        paths: adapter_module._TransactionPaths,
                        post: adapter_module._StreamState,
                    ) -> None:
                        original_apply_stream(paths, post)
                        raise RuntimeError("forced stream interruption")

                    if case == "AFTER_PREPARED":
                        patcher = patch.object(adapter, "_apply_stream", side_effect=fail_after_apply)
                    elif case == "AFTER_LEDGER_APPLIED":
                        def fail_cleanup(paths: adapter_module._TransactionPaths) -> None:
                            raise RuntimeError("forced cleanup interruption")

                        patcher = patch.object(adapter, "_cleanup_transaction", side_effect=fail_cleanup)
                    else:
                        patcher = patch.object(adapter, "_write_journal", side_effect=fail_write)
                    with patcher:
                        failed = _require_failure(
                            adapter.execute(_append_request(reference, _record()))
                        )
                    self.assertEqual(
                        failed.decision,
                        TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION,
                    )

                    restarted = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
                        layout, LocalTelemetryOwnershipLedger(layout), FakeLock()
                    )
                    if case in (
                        "BEFORE_JOURNAL",
                        "AFTER_PREPARED",
                        "AFTER_STREAM_APPLIED",
                    ):
                        read = _require_read(
                            restarted.execute(
                                _no_record_request(reference, TelemetryStorageOperation.READ)
                            )
                        )
                        self.assertEqual(read.record_count, 1)
                        self.assertEqual(stream.read_bytes(), original)
                    else:
                        next_revision = _expected_revision(
                            reference,
                            TelemetryStorageOperation.APPEND,
                            TelemetryStorageLifecycle.ACTIVE,
                            "streams/alpha.jsonl",
                            original,
                            post_raw,
                        )
                        read = _require_read(
                            restarted.execute(
                                _no_record_request(
                                    _reference(revision=next_revision),
                                    TelemetryStorageOperation.READ,
                                )
                            )
                        )
                        self.assertEqual(read.record_count, 2)
                        self.assertEqual(stream.read_bytes(), post_raw)
                    self.assertFalse(_transaction_root(layout, reference).exists())

    def test_tta6_release_failure_overrides_complete_response(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            reference = _reference()
            _seed_entry(layout, reference)
            stream = _write_stream(layout, (_record(),))
            lock = FakeLock(release_failed=True)
            adapter = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
                layout, LocalTelemetryOwnershipLedger(layout), lock
            )
            result = _require_failure(adapter.execute(_append_request(reference, _record("run-after"))))
            self.assertEqual(result.decision, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
            self.assertEqual(len(JsonlContextUsageStore.read(path=stream)), 2)
            current = LocalTelemetryOwnershipLedger(layout).resolve_current(reference)
            self.assertIsInstance(current, TelemetryOwnershipLedgerFound)
            assert isinstance(current, TelemetryOwnershipLedgerFound)
            self.assertNotEqual(current.entry.storage_ref.storage_revision, reference.storage_revision)

    def test_tta5_malformed_legacy_redirect_and_restore_failures_are_boundary(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            reference = _reference()
            legacy = layout.telemetry_root / "ownership-ledger" / "ledger.json"
            _write_json(legacy, {"schema_version": 1, "entries": []})
            adapter = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
                layout, LocalTelemetryOwnershipLedger(layout), FakeLock()
            )
            legacy_result = _require_failure(adapter.execute(_append_request(reference, _record())))
            self.assertEqual(legacy_result.decision, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
            self.assertEqual(legacy.read_bytes(), legacy.read_bytes())

            legacy.unlink()
            entry_path = _seed_entry(layout, reference, locator="../outside.jsonl")
            redirected = _require_failure(adapter.execute(_append_request(reference, _record())))
            self.assertEqual(redirected.decision, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
            self.assertTrue(entry_path.exists())

            outside = Path(temporary) / "outside.jsonl"
            outside.write_bytes(_canonical_records((_record("outside"),)))
            base = adapter._base_paths(reference)
            redirected_paths = adapter_module._TransactionPaths(
                telemetry_root=base[0],
                transaction_root=base[1],
                transaction_directory=base[2],
                journal_path=base[3],
                pre_snapshot_path=base[4],
                post_snapshot_path=base[5],
                stream_path=outside,
                legacy_aggregate_path=base[6],
            )
            with patch.object(adapter, "_paths", return_value=redirected_paths):
                with patch.object(adapter, "_read_stream") as read_stream:
                    redirected_before_codec = _require_failure(
                        adapter.execute(_append_request(reference, _record()))
                    )
                    read_stream.assert_not_called()
            self.assertEqual(
                redirected_before_codec.decision,
                TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION,
            )

            _seed_entry(layout, reference)
            stream = _write_stream(layout, (_record(),))
            before = stream.read_bytes()
            with patch.object(os, "replace", side_effect=OSError("injected replacement")):
                failed = _require_failure(adapter.execute(_append_request(reference, _record())))
            self.assertEqual(failed.decision, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
            self.assertEqual(stream.read_bytes(), before)

    def test_tta5_malformed_journal_is_retained_without_repair(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            reference = _reference()
            _seed_entry(layout, reference)
            stream = _write_stream(layout, (_record(),))
            transaction = _transaction_root(layout, reference)
            transaction.mkdir(parents=True)
            journal = transaction / "journal.json"
            journal.write_text("{not-json}\n", encoding="utf-8")
            before = journal.read_bytes()
            adapter = adapter_module.JohnnyOwnedTelemetryStorageAdapter(
                layout, LocalTelemetryOwnershipLedger(layout), FakeLock()
            )
            result = _require_failure(
                adapter.execute(_no_record_request(reference, TelemetryStorageOperation.READ))
            )
            self.assertEqual(result.decision, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
            self.assertEqual(journal.read_bytes(), before)
            self.assertEqual(stream.read_bytes(), _canonical_records((_record(),)))


class TelemetryAdapterSourceTests(unittest.TestCase):
    """TTA6-TTA7: source-direction, response-shape and element-index gates."""

    def test_tta6_source_is_private_typed_and_effect_direction_is_closed(self) -> None:
        source_path = _ROOT / "library" / "local_orchestration" / "telemetry_storage" / "johnny_owned_adapter.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            (node.module, tuple(alias.name for alias in node.names))
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        self.assertIn(("library.local_orchestration.path_containment", ("resolves_within_root",)), imports)
        ledger_imports = {
            name
            for module, names in imports
            if module == "library.local_orchestration.telemetry_storage.ownership_ledger"
            for name in names
        }
        self.assertIn("TelemetryOwnershipLedgerPort", ledger_imports)
        telemetry_imports = {
            name
            for module, names in imports
            if module == "library.workflow_router.telemetry"
            for name in names
        }
        self.assertIn("JsonlContextUsageStore", telemetry_imports)
        self.assertNotIn("JsonlContextUsageStore.append", source)
        self.assertNotIn("TelemetryStorageLockAdapter", source)
        self.assertNotIn("LocalTelemetryStorageLockAdapter", source)
        self.assertNotIn("provider", source.casefold())
        self.assertNotIn("host", source.casefold())
        self.assertNotIn("Any", source)
        self.assertNotIn("cast(", source)
        self.assertNotIn("sleep(", source)
        self.assertNotIn("retry", source.casefold())
        self.assertNotIn("poll", source.casefold())
        self.assertIn("JsonlContextUsageStore.read", source)
        self.assertIn("TelemetryStoragePort", source)
        self.assertIn("TelemetryStorageFailure", source)
        self.assertIn("CompletedAppendResponse", source)
        self.assertIn("CompletedReadResponse", source)
        self.assertIn("CompletedValidateResponse", source)
        self.assertIn("CompletedDetachResponse", source)
        self.assertIn("CompletedUninstallResponse", source)
        self.assertIn("release", source)
        self.assertTrue(
            any(
                isinstance(node, ast.ClassDef) and node.name == "JohnnyOwnedTelemetryStorageAdapter"
                for node in ast.walk(tree)
            )
        )

    def test_tta7_element_index_names_exact_private_closure(self) -> None:
        index = (
            _ROOT
            / "modules"
            / "element"
            / "python"
            / "context-load-telemetry"
            / "12-lock-bound-transaction-adapter"
            / "README.md"
        )
        body = index.read_text(encoding="utf-8")
        for required in (
            "12-lock-bound-transaction-adapter.md",
            "johnny_owned_adapter.py",
            "test_johnny_owned_telemetry_storage_adapter.py",
            "path-containment@cf9e126",
            "exclusive-file-lock@60d2ab0",
            "096d471",
            "e05f03a",
            "ADR-20260827-027",
        ):
            self.assertIn(required, body)
        self.assertIn("public provision", body.casefold())
        self.assertNotIn("composition root", body.casefold())


if __name__ == "__main__":
    unittest.main()
