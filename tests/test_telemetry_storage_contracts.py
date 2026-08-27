"""TDD cells for the pure opaque telemetry-storage request/response boundary."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from pydantic import ValidationError

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
    TelemetryStorageLockDecision,
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
from library.workflow_router.contracts import (
    ConsumerFingerprint,
    DeliveryStage,
    ProcessStage,
)
from library.workflow_router.telemetry import (
    AgentUsage,
    ContextLoadMeasurement,
    ContextUsageRecord,
    RunAcceptance,
    TelemetryMode,
)


_ROOT = Path(__file__).resolve().parents[1]
_CONTRACTS = _ROOT / "library" / "local_orchestration" / "telemetry_storage" / "contracts.py"
_INIT = _ROOT / "library" / "local_orchestration" / "telemetry_storage" / "__init__.py"
_EXPECTED_WORKFLOW_ROUTER_IMPORTS = {
    ("library.workflow_router.contracts", "OpaqueMetadataId", None),
    ("library.workflow_router.contracts", "ProjectId", None),
    ("library.workflow_router.contracts", "RevisionDigest", None),
    ("library.workflow_router.contracts", "RouterModel", None),
    ("library.workflow_router.telemetry", "ContextUsageRecord", None),
    ("library.workflow_router.telemetry", "NonNegativeCount", None),
}
_EXPECTED_IMPORT_FROM = {
    _CONTRACTS: (
        (0, "__future__", "annotations", None),
        (0, "enum", "Enum", None),
        (0, "typing", "Protocol", None),
        (0, "typing", "Self", None),
        (0, "typing", "TypeAlias", None),
        (0, "typing", "runtime_checkable", None),
        (0, "pydantic", "ConfigDict", None),
        (0, "pydantic", "model_validator", None),
        (0, "library.workflow_router.contracts", "OpaqueMetadataId", None),
        (0, "library.workflow_router.contracts", "ProjectId", None),
        (0, "library.workflow_router.contracts", "RevisionDigest", None),
        (0, "library.workflow_router.contracts", "RouterModel", None),
        (0, "library.workflow_router.telemetry", "ContextUsageRecord", None),
        (0, "library.workflow_router.telemetry", "NonNegativeCount", None),
    ),
    _INIT: (
        (1, "contracts", "AppendTelemetryStorageRequest", None),
        (1, "contracts", "CompletedAppendResponse", None),
        (1, "contracts", "CompletedDetachResponse", None),
        (1, "contracts", "CompletedReadResponse", None),
        (1, "contracts", "CompletedUninstallResponse", None),
        (1, "contracts", "CompletedValidateResponse", None),
        (1, "contracts", "NoRecordTelemetryStorageRequest", None),
        (1, "contracts", "TelemetryStorageDecision", None),
        (1, "contracts", "TelemetryStorageFailure", None),
        (1, "contracts", "TelemetryStorageLifecycle", None),
        (1, "contracts", "TelemetryStorageLockAcquire", None),
        (1, "contracts", "TelemetryStorageLockAcquired", None),
        (1, "contracts", "TelemetryStorageLockContended", None),
        (1, "contracts", "TelemetryStorageLockDecision", None),
        (1, "contracts", "TelemetryStorageLockPort", None),
        (1, "contracts", "TelemetryStorageLockRelease", None),
        (1, "contracts", "TelemetryStorageLockReleaseFailed", None),
        (1, "contracts", "TelemetryStorageLockReleased", None),
        (1, "contracts", "TelemetryStorageLockRequest", None),
        (1, "contracts", "TelemetryStorageLockToken", None),
        (1, "contracts", "TelemetryStorageOperation", None),
        (1, "contracts", "TelemetryStoragePort", None),
        (1, "contracts", "TelemetryStorageReadPayload", None),
        (1, "contracts", "TelemetryStorageRef", None),
        (1, "contracts", "TelemetryStorageRequest", None),
        (1, "contracts", "TelemetryStorageResponse", None),
    ),
}
_EXPECTED_CALL_TARGETS = {
    _CONTRACTS: {
        "ConfigDict",
        "ValueError",
        "_validate_completed_shape",
        "len",
        "model_validator",
    },
    _INIT: set(),
}


def _expression_dump(source: str) -> str:
    statement = ast.parse(source).body[0]
    if not isinstance(statement, ast.Expr):
        raise AssertionError("decorator source must be an expression")
    return ast.dump(statement.value, include_attributes=False)


_EXPECTED_DECORATORS = {
    _CONTRACTS: {
        _expression_dump("runtime_checkable"),
        _expression_dump('model_validator(mode="after")'),
    },
    _INIT: set(),
}


def _record() -> ContextUsageRecord:
    """Construct one valid metadata-only baseline record without bypass helpers."""

    return ContextUsageRecord(
        run_id="run-alpha",
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


def _ref(
    lifecycle: TelemetryStorageLifecycle = TelemetryStorageLifecycle.ACTIVE,
) -> TelemetryStorageRef:
    return TelemetryStorageRef(
        storage_ref="storage-alpha",
        project_id="prj_0123456789abcdef",
        stream_id="stream-alpha",
        ownership_ledger_ref="ledger-alpha",
        storage_revision="rev-0123456789abcdef",
        lifecycle=lifecycle,
    )


def _append() -> AppendTelemetryStorageRequest:
    return AppendTelemetryStorageRequest(
        storage_ref=_ref(),
        expected_project_id="prj_0123456789abcdef",
        expected_storage_revision="rev-0123456789abcdef",
        operation=TelemetryStorageOperation.APPEND,
        record=_record(),
    )


def _no_record(operation: TelemetryStorageOperation) -> NoRecordTelemetryStorageRequest:
    return NoRecordTelemetryStorageRequest(
        storage_ref=_ref(),
        expected_project_id="prj_0123456789abcdef",
        expected_storage_revision="rev-0123456789abcdef",
        operation=operation,
    )


def _lock_request() -> TelemetryStorageLockRequest:
    return TelemetryStorageLockRequest(
        storage_ref=_ref(),
        expected_project_id="prj_0123456789abcdef",
        expected_storage_revision="rev-0123456789abcdef",
    )


def _lock_token() -> TelemetryStorageLockToken:
    return TelemetryStorageLockToken(
        lock_ref="lock-alpha",
        storage_ref="storage-alpha",
        project_id="prj_0123456789abcdef",
        stream_id="stream-alpha",
        ownership_ledger_ref="ledger-alpha",
        storage_revision="rev-0123456789abcdef",
    )


class TestValidContracts:
    def test_sc1_valid_reference_requests_and_all_response_variants(self) -> None:
        assert _ref().lifecycle is TelemetryStorageLifecycle.ACTIVE
        assert _append().record.run_id == "run-alpha"
        for operation in (
            TelemetryStorageOperation.READ,
            TelemetryStorageOperation.VALIDATE,
            TelemetryStorageOperation.DETACH,
            TelemetryStorageOperation.UNINSTALL,
        ):
            assert _no_record(operation).operation is operation

        append = CompletedAppendResponse(
            storage_ref="storage-alpha",
            storage_revision="rev-0123456789abcdef",
            record_count=0,
        )
        read = CompletedReadResponse(
            storage_ref="storage-alpha",
            storage_revision="rev-0123456789abcdef",
            record_count=0,
            read_payload=TelemetryStorageReadPayload(records=()),
        )
        validate = CompletedValidateResponse(
            storage_ref="storage-alpha",
            storage_revision="rev-0123456789abcdef",
            record_count=0,
            validation_report_ref="report-alpha",
        )
        detach = CompletedDetachResponse(
            storage_ref="storage-alpha",
            storage_revision="rev-0123456789abcdef",
            record_count=0,
        )
        uninstall = CompletedUninstallResponse(
            storage_ref="storage-alpha",
            storage_revision="rev-0123456789abcdef",
            record_count=0,
        )
        assert append.operation is TelemetryStorageOperation.APPEND
        assert read.operation is TelemetryStorageOperation.READ
        assert validate.operation is TelemetryStorageOperation.VALIDATE
        assert detach.lifecycle is TelemetryStorageLifecycle.DETACHED
        assert uninstall.lifecycle is TelemetryStorageLifecycle.REMOVED

    def test_lc1_valid_lock_shapes_and_typed_fake_round_trip(self) -> None:
        token = _lock_token()
        acquired = TelemetryStorageLockAcquired(lock_token=token)
        contended = TelemetryStorageLockContended(
            storage_ref="storage-alpha",
            storage_revision="rev-0123456789abcdef",
            failure_ref="lock-busy",
        )
        released = TelemetryStorageLockReleased(
            lock_ref=token.lock_ref,
            storage_ref=token.storage_ref,
            storage_revision=token.storage_revision,
        )
        release_failed = TelemetryStorageLockReleaseFailed(
            lock_ref=token.lock_ref,
            storage_ref=token.storage_ref,
            storage_revision=token.storage_revision,
            failure_ref="release-failed",
        )
        failure = TelemetryStorageFailure(
            storage_ref=token.storage_ref,
            storage_revision=token.storage_revision,
            operation=TelemetryStorageOperation.READ,
            decision=TelemetryStorageDecision.LOCK_CONTENDED,
            failure_ref=contended.failure_ref,
        )
        assert acquired.decision is TelemetryStorageLockDecision.LOCK_ACQUIRED
        assert acquired.lock_token == token
        assert contended.decision is TelemetryStorageLockDecision.LOCK_CONTENDED
        assert released.decision is TelemetryStorageLockDecision.RELEASED
        assert release_failed.decision is TelemetryStorageLockDecision.RELEASE_FAILED
        assert failure.decision is TelemetryStorageDecision.LOCK_CONTENDED

        class FakeLockPort:
            def __init__(self, acquire_result: TelemetryStorageLockAcquire) -> None:
                self._acquire_result = acquire_result

            def try_acquire(
                self, request: TelemetryStorageLockRequest
            ) -> TelemetryStorageLockAcquire:
                assert request == _lock_request()
                return self._acquire_result

            def release(
                self, received: TelemetryStorageLockToken
            ) -> TelemetryStorageLockRelease:
                assert received == token
                return released

        contended_port: TelemetryStorageLockPort = FakeLockPort(contended)
        round_trip_contention = contended_port.try_acquire(_lock_request())
        assert isinstance(round_trip_contention, TelemetryStorageLockContended)

        port: TelemetryStorageLockPort = FakeLockPort(acquired)
        round_trip_acquire = port.try_acquire(_lock_request())
        assert isinstance(round_trip_acquire, TelemetryStorageLockAcquired)
        round_trip_release = port.release(round_trip_acquire.lock_token)
        assert isinstance(round_trip_release, TelemetryStorageLockReleased)

    def test_sc5_typed_fake_port_round_trips_a_validated_response(self) -> None:
        class FakePort:
            def execute(self, request: TelemetryStorageRequest) -> TelemetryStorageResponse:
                assert request.operation is TelemetryStorageOperation.READ
                return CompletedReadResponse(
                    storage_ref=request.storage_ref.storage_ref,
                    storage_revision=request.expected_storage_revision,
                    record_count=0,
                    read_payload=TelemetryStorageReadPayload(records=()),
                )

        port: TelemetryStoragePort = FakePort()
        result = port.execute(_no_record(TelemetryStorageOperation.READ))
        assert isinstance(result, CompletedReadResponse)
        assert result.record_count == 0


class TestInvalidContracts:
    def test_sc2_invalid_identifiers_nulls_and_extra_fields_are_rejected(self) -> None:
        with pytest.raises(ValidationError):
            TelemetryStorageRef.model_validate(
                {
                    "storage_ref": 42,
                    "project_id": "prj_0123456789abcdef",
                    "stream_id": "stream-alpha",
                    "ownership_ledger_ref": "ledger-alpha",
                    "storage_revision": "rev-0123456789abcdef",
                    "lifecycle": TelemetryStorageLifecycle.ACTIVE,
                }
            )
        with pytest.raises(ValidationError):
            TelemetryStorageRef(
                storage_ref="",
                project_id="prj_0123456789abcdef",
                stream_id="stream-alpha",
                ownership_ledger_ref="ledger-alpha",
                storage_revision="rev-0123456789abcdef",
                lifecycle=TelemetryStorageLifecycle.ACTIVE,
            )
        with pytest.raises(ValidationError):
            TelemetryStorageRef(
                storage_ref="storage-alpha",
                project_id="prj_0123456789abcdef",
                stream_id="stream-alpha",
                ownership_ledger_ref="ledger-alpha",
                storage_revision="rev-0123456789abcdef",
                lifecycle=TelemetryStorageLifecycle.ACTIVE,
                unknown="nope",  # type: ignore[call-arg]
            )
        with pytest.raises(ValidationError):
            TelemetryStorageRef.model_validate(
                {
                    "storage_ref": None,
                    "project_id": "prj_0123456789abcdef",
                    "stream_id": "stream-alpha",
                    "ownership_ledger_ref": "ledger-alpha",
                    "storage_revision": "rev-0123456789abcdef",
                    "lifecycle": TelemetryStorageLifecycle.ACTIVE,
                }
            )
        with pytest.raises(ValidationError):
            TelemetryStorageRef(
                storage_ref="   ",
                project_id="prj_0123456789abcdef",
                stream_id="stream-alpha",
                ownership_ledger_ref="ledger-alpha",
                storage_revision="rev-0123456789abcdef",
                lifecycle=TelemetryStorageLifecycle.ACTIVE,
            )
        with pytest.raises(ValidationError):
            TelemetryStorageRef.model_validate(
                {
                    "storage_ref": "storage-alpha",
                    "project_id": "prj_0123456789abcdef",
                    "stream_id": "stream-alpha",
                    "ownership_ledger_ref": "ledger-alpha",
                    "storage_revision": "rev-0123456789abcdef",
                    "lifecycle": "UNKNOWN",
                }
            )

    def test_sc3_operation_payload_combinations_are_discriminated(self) -> None:
        with pytest.raises(ValidationError):
            AppendTelemetryStorageRequest(
                storage_ref=_ref(),
                expected_project_id="prj_0123456789abcdef",
                expected_storage_revision="rev-0123456789abcdef",
                operation=TelemetryStorageOperation.APPEND,
            )  # type: ignore[call-arg]
        with pytest.raises(ValidationError):
            AppendTelemetryStorageRequest(
                storage_ref=_ref(),
                expected_project_id="prj_0123456789abcdef",
                expected_storage_revision="rev-0123456789abcdef",
                operation=TelemetryStorageOperation.READ,
                record=_record(),
            )
        with pytest.raises(ValidationError):
            NoRecordTelemetryStorageRequest(
                storage_ref=_ref(),
                expected_project_id="prj_0123456789abcdef",
                expected_storage_revision="rev-0123456789abcdef",
                operation=TelemetryStorageOperation.APPEND,
            )
        with pytest.raises(ValidationError):
            NoRecordTelemetryStorageRequest(
                storage_ref=_ref(),
                expected_project_id="prj_0123456789abcdef",
                expected_storage_revision="rev-0123456789abcdef",
                operation=TelemetryStorageOperation.READ,
                record=_record(),  # type: ignore[call-arg]
            )
        for operation in (
            TelemetryStorageOperation.READ,
            TelemetryStorageOperation.VALIDATE,
            TelemetryStorageOperation.DETACH,
            TelemetryStorageOperation.UNINSTALL,
        ):
            with pytest.raises(ValidationError):
                NoRecordTelemetryStorageRequest(
                    storage_ref=_ref(),
                    expected_project_id="prj_0123456789abcdef",
                    expected_storage_revision="rev-0123456789abcdef",
                    operation=operation,
                    record=_record(),  # type: ignore[call-arg]
                )
        with pytest.raises(ValidationError):
            NoRecordTelemetryStorageRequest.model_validate(
                {
                    "storage_ref": _ref(),
                    "expected_project_id": "prj_0123456789abcdef",
                    "expected_storage_revision": "rev-0123456789abcdef",
                    "operation": TelemetryStorageOperation.READ,
                    "validation_report_ref": "report-alpha",
                }
            )

    def test_sc4_read_count_and_response_field_exclusivity_are_enforced(self) -> None:
        with pytest.raises(ValidationError):
            CompletedReadResponse(
                storage_ref="storage-alpha",
                storage_revision="rev-0123456789abcdef",
                record_count=1,
                read_payload=TelemetryStorageReadPayload(records=()),
            )
        with pytest.raises(ValidationError):
            CompletedValidateResponse(
                storage_ref="storage-alpha",
                storage_revision="rev-0123456789abcdef",
                record_count=0,
                validation_report_ref="report-alpha",
                read_payload=TelemetryStorageReadPayload(records=()),  # type: ignore[call-arg]
            )
        with pytest.raises(ValidationError):
            TelemetryStorageFailure(
                storage_ref="storage-alpha",
                storage_revision="rev-0123456789abcdef",
                operation=TelemetryStorageOperation.READ,
                decision=TelemetryStorageDecision.COMPLETED,
                failure_ref="failure-alpha",
            )
        with pytest.raises(ValidationError):
            TelemetryStorageFailure(
                storage_ref="storage-alpha",
                storage_revision="rev-0123456789abcdef",
                operation=TelemetryStorageOperation.READ,
                decision=TelemetryStorageDecision.STORAGE_CLOSED,
            )  # type: ignore[call-arg]
        with pytest.raises(ValidationError):
            TelemetryStorageFailure.model_validate(
                {
                    "storage_ref": "storage-alpha",
                    "storage_revision": "rev-0123456789abcdef",
                    "operation": TelemetryStorageOperation.READ,
                    "decision": TelemetryStorageDecision.STORAGE_CLOSED,
                    "failure_ref": "failure-alpha",
                    "lifecycle": TelemetryStorageLifecycle.ACTIVE,
                }
            )

    def test_lc2_lock_identity_grammar_and_bypass_values_are_rejected(self) -> None:
        with pytest.raises(ValidationError):
            TelemetryStorageLockRequest(
                storage_ref=None,  # type: ignore[arg-type]
                expected_project_id="prj_0123456789abcdef",
                expected_storage_revision="rev-0123456789abcdef",
            )
        with pytest.raises(ValidationError):
            TelemetryStorageLockRequest(
                storage_ref=_ref(),
                expected_project_id="project-alpha",
                expected_storage_revision="rev-0123456789abcdef",
            )
        with pytest.raises(ValidationError):
            TelemetryStorageLockRequest(
                storage_ref=_ref(),
                expected_project_id="prj_0123456789abcdef",
                expected_storage_revision="revision-alpha",
            )
        with pytest.raises(ValidationError):
            TelemetryStorageLockToken(
                lock_ref=42,  # type: ignore[arg-type]
                storage_ref="storage-alpha",
                project_id="prj_0123456789abcdef",
                stream_id="stream-alpha",
                ownership_ledger_ref="ledger-alpha",
                storage_revision="rev-0123456789abcdef",
            )
        with pytest.raises(ValidationError):
            TelemetryStorageLockToken(
                lock_ref="lock-alpha",
                storage_ref="storage-alpha",
                project_id="prj_0123456789abcdef",
                stream_id="stream-alpha",
                ownership_ledger_ref="ledger-alpha",
                storage_revision="rev-0123456789abcdef",
                extra="forbidden",  # type: ignore[call-arg]
            )
        bypassed = TelemetryStorageLockToken.model_construct(lock_ref="lock-alpha")
        with pytest.raises(ValidationError):
            TelemetryStorageLockAcquired(lock_token=bypassed)

    def test_lc3_lock_decisions_and_payloads_are_exclusive(self) -> None:
        token = _lock_token()
        with pytest.raises(ValidationError):
            TelemetryStorageLockAcquired(
                decision=TelemetryStorageLockDecision.LOCK_CONTENDED,
                lock_token=token,
            )
        with pytest.raises(ValidationError):
            TelemetryStorageLockAcquired(
                lock_token=token,
                failure_ref="unexpected",  # type: ignore[call-arg]
            )
        with pytest.raises(ValidationError):
            TelemetryStorageLockContended(
                decision=TelemetryStorageLockDecision.LOCK_ACQUIRED,
                storage_ref="storage-alpha",
                storage_revision="rev-0123456789abcdef",
                failure_ref="lock-busy",
            )
        with pytest.raises(ValidationError):
            TelemetryStorageLockContended(
                storage_ref="storage-alpha",
                storage_revision="rev-0123456789abcdef",
                failure_ref="lock-busy",
                lock_token=token,  # type: ignore[call-arg]
            )
        with pytest.raises(ValidationError):
            TelemetryStorageLockReleased(
                lock_ref=token.lock_ref,
                storage_ref=token.storage_ref,
                storage_revision=token.storage_revision,
                failure_ref="unexpected",  # type: ignore[call-arg]
            )
        with pytest.raises(ValidationError):
            TelemetryStorageLockReleaseFailed(
                lock_ref=token.lock_ref,
                storage_ref=token.storage_ref,
                storage_revision=token.storage_revision,
            )  # type: ignore[call-arg]
        with pytest.raises(ValidationError):
            TelemetryStorageLockReleaseFailed(
                decision=TelemetryStorageLockDecision.RELEASED,
                lock_ref=token.lock_ref,
                storage_ref=token.storage_ref,
                storage_revision=token.storage_revision,
                failure_ref="release-failed",
            )

    def test_lc4_only_lock_contention_is_a_storage_failure(self) -> None:
        contention = TelemetryStorageFailure(
            storage_ref="storage-alpha",
            storage_revision="rev-0123456789abcdef",
            operation=TelemetryStorageOperation.READ,
            decision=TelemetryStorageDecision.LOCK_CONTENDED,
            failure_ref="lock-busy",
        )
        assert contention.decision is TelemetryStorageDecision.LOCK_CONTENDED
        with pytest.raises(ValidationError):
            TelemetryStorageFailure(
                storage_ref="storage-alpha",
                storage_revision="rev-0123456789abcdef",
                operation=TelemetryStorageOperation.READ,
                decision=TelemetryStorageDecision.COMPLETED,
                failure_ref="not-completed",
            )
        with pytest.raises(ValidationError):
            TelemetryStorageFailure(
                storage_ref="storage-alpha",
                storage_revision="rev-0123456789abcdef",
                operation=TelemetryStorageOperation.READ,
                decision=TelemetryStorageDecision.LOCK_CONTENDED,
                failure_ref="lock-busy",
                lock_token=_lock_token(),  # type: ignore[call-arg]
            )
        with pytest.raises(ValidationError):
            CompletedReadResponse(
                storage_ref="storage-alpha",
                storage_revision="rev-0123456789abcdef",
                decision=TelemetryStorageDecision.LOCK_CONTENDED,
                record_count=0,
                read_payload=TelemetryStorageReadPayload(records=()),
            )

    def test_lc2_unknown_lock_decision_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            TelemetryStorageLockAcquired.model_validate(
                {
                    "decision": "UNKNOWN",
                    "lock_token": _lock_token().model_dump(),
                }
            )


class TestSourceBoundary:
    def test_sc6_owned_modules_are_strict_and_effect_free(self) -> None:
        forbidden_names = {
            "Any",
            "object",
            "cast",
            "model_construct",
            "model_copy",
            "open",
        }
        forbidden_imports = {
            "pathlib",
            "os",
            "subprocess",
            "socket",
            "shutil",
            "JsonlContextUsageStore",
        }
        allowed_import_families = {
            _CONTRACTS: {
                "__future__",
                "enum",
                "typing",
                "pydantic",
                "library.workflow_router.contracts",
                "library.workflow_router.telemetry",
            },
            _INIT: {".contracts"},
        }
        for source_path in (_CONTRACTS, _INIT):
            tree = ast.parse(source_path.read_text(encoding="utf-8"))
            names = {
                node.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Name)
            }
            assert not names.intersection(forbidden_names)
            imported_modules = {
                node.module or ""
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
            }
            imported_names = {
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
                for alias in node.names
            }
            import_families = {
                (("." * node.level) + (node.module or ""))
                if isinstance(node, ast.ImportFrom)
                else alias.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
                for alias in node.names
            }
            assert not any(isinstance(node, ast.Import) for node in ast.walk(tree))
            import_from_entries = sorted(
                (
                    node.level,
                    node.module or "",
                    alias.name,
                    alias.asname,
                )
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
                for alias in node.names
            )
            assert import_from_entries == sorted(_EXPECTED_IMPORT_FROM[source_path])
            assert import_families <= allowed_import_families[source_path]
            workflow_router_imports = {
                (node.module or "", alias.name, alias.asname)
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
                and (node.module or "").startswith("library.workflow_router.")
                for alias in node.names
            }
            expected_workflow_router_imports = (
                _EXPECTED_WORKFLOW_ROUTER_IMPORTS if source_path == _CONTRACTS else set()
            )
            assert workflow_router_imports == expected_workflow_router_imports
            plain_workflow_router_imports = {
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
                if alias.name == "library.workflow_router"
                or alias.name.startswith("library.workflow_router.")
            }
            assert not plain_workflow_router_imports
            assert not imported_modules.intersection(forbidden_imports)
            assert not imported_names.intersection(forbidden_imports)
            assert "library.local_orchestration" not in imported_modules
            assert "library.local_orchestration" not in imported_names
            assert "BaseModel" not in names
            call_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
            assert all(isinstance(node.func, ast.Name) for node in call_nodes)
            call_targets = {
                node.func.id
                for node in call_nodes
                if isinstance(node.func, ast.Name)
            }
            assert call_targets == _EXPECTED_CALL_TARGETS[source_path]
            dynamic_attribute_calls = {
                node.func.attr
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            }
            assert not dynamic_attribute_calls.intersection(
                {
                    "__getattribute__",
                    "__getattr__",
                    "__setattr__",
                    "__delattr__",
                }
            )
            decorator_dumps = {
                ast.dump(decorator, include_attributes=False)
                for node in ast.walk(tree)
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                for decorator in node.decorator_list
            }
            assert decorator_dumps == _EXPECTED_DECORATORS[source_path]
            if source_path == _CONTRACTS:
                assert "Protocol" in names

    def test_lc5_lock_port_surface_is_only_acquire_and_release(self) -> None:
        tree = ast.parse(_CONTRACTS.read_text(encoding="utf-8"))
        lock_port = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "TelemetryStorageLockPort"
        )
        method_names = {
            node.name
            for node in lock_port.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert method_names == {"try_acquire", "release"}

    def test_sc6_models_are_frozen_and_extra_forbidden(self) -> None:
        assert _ref().model_config["frozen"] is True
        assert _ref().model_config["extra"] == "forbid"
        with pytest.raises(ValidationError):
            _ref().storage_ref = "storage-other"


class TestReverseMutations:
    def test_sm1_extra_fields_are_not_a_success_path(self) -> None:
        with pytest.raises(ValidationError):
            TelemetryStorageRef(
                storage_ref="storage-alpha",
                project_id="prj_0123456789abcdef",
                stream_id="stream-alpha",
                ownership_ledger_ref="ledger-alpha",
                storage_revision="rev-0123456789abcdef",
                lifecycle=TelemetryStorageLifecycle.ACTIVE,
                bypass=True,  # type: ignore[call-arg]
            )

    def test_sm2_no_record_variant_cannot_carry_a_record(self) -> None:
        with pytest.raises(ValidationError):
            NoRecordTelemetryStorageRequest(
                storage_ref=_ref(),
                expected_project_id="prj_0123456789abcdef",
                expected_storage_revision="rev-0123456789abcdef",
                operation=TelemetryStorageOperation.READ,
                record=_record(),  # type: ignore[call-arg]
            )

    def test_sm3_read_count_cannot_disagree_with_payload(self) -> None:
        with pytest.raises(ValidationError):
            CompletedReadResponse(
                storage_ref="storage-alpha",
                storage_revision="rev-0123456789abcdef",
                record_count=1,
                read_payload=TelemetryStorageReadPayload(records=()),
            )

    def test_sm4_effectful_imports_are_absent(self) -> None:
        source = _CONTRACTS.read_text(encoding="utf-8")
        assert "pathlib" not in source
        assert "shutil" not in source
        assert "subprocess" not in source
        assert "model_construct" not in source

    def test_dynamic_lookup_is_absent(self) -> None:
        tree = ast.parse(_CONTRACTS.read_text(encoding="utf-8"))
        dynamic_calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert not dynamic_calls.intersection({"getattr", "setattr", "delattr"})
        dynamic_attribute_calls = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        assert not dynamic_attribute_calls.intersection(
            {
                "__getattribute__",
                "__getattr__",
                "__setattr__",
                "__delattr__",
            }
        )

    def test_sm5_package_root_import_is_absent(self) -> None:
        tree = ast.parse(_CONTRACTS.read_text(encoding="utf-8"))
        imported_modules = {
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        imported_names = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        assert "library.local_orchestration" not in imported_modules
        assert "library.local_orchestration" not in imported_names

    def test_sm6_workflow_router_imports_are_exact(self) -> None:
        tree = ast.parse(_CONTRACTS.read_text(encoding="utf-8"))
        workflow_router_imports = {
            (node.module or "", alias.name, alias.asname)
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and (node.module or "").startswith("library.workflow_router.")
            for alias in node.names
        }
        assert workflow_router_imports == _EXPECTED_WORKFLOW_ROUTER_IMPORTS
        plain_workflow_router_imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
            if alias.name == "library.workflow_router"
            or alias.name.startswith("library.workflow_router.")
        }
        assert not plain_workflow_router_imports

    def test_sm7_deferred_import_call_is_absent(self) -> None:
        tree = ast.parse(_CONTRACTS.read_text(encoding="utf-8"))
        call_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        assert all(isinstance(node.func, ast.Name) for node in call_nodes)
        call_targets = {
            node.func.id
            for node in call_nodes
            if isinstance(node.func, ast.Name)
        }
        assert call_targets == _EXPECTED_CALL_TARGETS[_CONTRACTS]
