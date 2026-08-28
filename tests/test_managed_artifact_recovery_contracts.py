"""Acceptance tests for recoverable managed-artifact outcome contracts."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from pydantic import ValidationError

from library.workflow_router.target_document_contracts import (
    ArtifactDocumentKind,
    DocumentMutationMode,
    DocumentWriteResult,
    DocumentWriteStatus,
    ManagedArtifactRecoveryResult,
    ManagedArtifactRecoveryStatus,
    ManagedArtifactWriteFailure,
    ManagedArtifactWriteResult,
    ManagedArtifactWriteStatus,
    RecoveryEvidenceRef,
    TargetDocumentMutation,
    TargetDocumentPlan,
    derive_document_digest,
)


_RECOVERY_REF: RecoveryEvidenceRef = "recovery-0123456789abcdef0123456789abcdef"


def _digest(content: str) -> str:
    return derive_document_digest(content)


def _applied() -> ManagedArtifactWriteResult:
    return ManagedArtifactWriteResult(
        status=ManagedArtifactWriteStatus.APPLIED,
        written_artifact_refs=("leaf-alpha", "leaf-zeta"),
        written_digests=(_digest("candidate-alpha\n"), _digest("candidate-zeta\n")),
        failure=None,
        recovery_ref=None,
    )


def _rejected(
    failure: ManagedArtifactWriteFailure,
) -> ManagedArtifactWriteResult:
    return ManagedArtifactWriteResult(
        status=ManagedArtifactWriteStatus.REJECTED,
        written_artifact_refs=(),
        written_digests=(),
        failure=failure,
        recovery_ref=None,
    )


def _storage_unavailable() -> ManagedArtifactWriteResult:
    return ManagedArtifactWriteResult(
        status=ManagedArtifactWriteStatus.STORAGE_UNAVAILABLE,
        written_artifact_refs=(),
        written_digests=(),
        failure=ManagedArtifactWriteFailure.STORAGE_UNAVAILABLE,
        recovery_ref=None,
    )


def _recovery_required() -> ManagedArtifactWriteResult:
    return ManagedArtifactWriteResult(
        status=ManagedArtifactWriteStatus.RECOVERY_REQUIRED,
        written_artifact_refs=(),
        written_digests=(),
        failure=ManagedArtifactWriteFailure.RECOVERY_REQUIRED,
        recovery_ref=_RECOVERY_REF,
    )


def _contract_source_path() -> Path:
    return (
        Path(__file__).parents[1]
        / "library"
        / "workflow_router"
        / "target_document_contracts.py"
    )


def _mutated_contract_accepts(source: str, payload: str) -> bool:
    with TemporaryDirectory() as temporary_directory:
        module_path = Path(temporary_directory) / "target_document_contracts.py"
        module_path.write_text(source, encoding="utf-8")
        script = f"""
import importlib.util
import sys
from pydantic import ValidationError

spec = importlib.util.spec_from_file_location(
    "library.workflow_router._r09b1_mutated_contracts", {str(module_path)!r}
)
if spec is None or spec.loader is None:
    raise SystemExit(2)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
try:
    module.ManagedArtifactWriteResult.model_validate_json({payload!r})
except ValidationError:
    raise SystemExit(1)
raise SystemExit(0)
"""
        completed = subprocess.run(
            (sys.executable, "-c", script),
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
        return completed.returncode == 0


class ManagedArtifactRecoveryContractTests(unittest.TestCase):
    def test_rrc1_every_valid_outcome_round_trips_through_json(self) -> None:
        results = (
            _applied(),
            _rejected(ManagedArtifactWriteFailure.RUNTIME_INVARIANT_FAILED),
            _storage_unavailable(),
            _recovery_required(),
        )
        for result in results:
            with self.subTest(status=result.status):
                self.assertEqual(
                    result,
                    ManagedArtifactWriteResult.model_validate_json(
                        result.model_dump_json()
                    ),
                )
        for status in (
            ManagedArtifactRecoveryStatus.RECOVERED,
            ManagedArtifactRecoveryStatus.RECOVERY_REQUIRED,
        ):
            recovery_result = ManagedArtifactRecoveryResult(
                status=status,
                recovery_ref=_RECOVERY_REF,
            )
            self.assertEqual(
                recovery_result,
                ManagedArtifactRecoveryResult.model_validate_json(
                    recovery_result.model_dump_json()
                ),
            )

    def test_rrc2_missing_null_extra_wrong_and_misaligned_values_reject(self) -> None:
        valid_json = _applied().model_dump_json()
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult.model_validate_json(
                valid_json.replace(',"recovery_ref":null', "")
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult.model_validate_json(
                valid_json.replace(
                    '"written_artifact_refs":["leaf-alpha","leaf-zeta"]',
                    '"written_artifact_refs":null',
                )
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult.model_validate_json(
                valid_json[:-1] + ',"unexpected":"field"}'
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult.model_validate_json(
                valid_json.replace('"status":"APPLIED"', '"status":7')
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult.model_validate_json(
                valid_json.replace(
                    '"written_artifact_refs":["leaf-alpha","leaf-zeta"]',
                    '"written_artifact_refs":7',
                )
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult(
                status=ManagedArtifactWriteStatus.APPLIED,
                written_artifact_refs=("modules/tickets/demo/leaf.md",),
                written_digests=(_digest("candidate\n"),),
                failure=None,
                recovery_ref=None,
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult(
                status=ManagedArtifactWriteStatus.APPLIED,
                written_artifact_refs=(),
                written_digests=(),
                failure=None,
                recovery_ref=None,
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult(
                status=ManagedArtifactWriteStatus.APPLIED,
                written_artifact_refs=("leaf-recovery",),
                written_digests=(),
                failure=None,
                recovery_ref=None,
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult(
                status=ManagedArtifactWriteStatus.APPLIED,
                written_artifact_refs=("leaf-alpha", "leaf-alpha"),
                written_digests=(_digest("alpha\n"), _digest("alpha-copy\n")),
                failure=None,
                recovery_ref=None,
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult(
                status=ManagedArtifactWriteStatus.APPLIED,
                written_artifact_refs=("leaf-zeta", "leaf-alpha"),
                written_digests=(_digest("zeta\n"), _digest("alpha\n")),
                failure=None,
                recovery_ref=None,
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult(
                status=ManagedArtifactWriteStatus.APPLIED,
                written_artifact_refs=("leaf-recovery",),
                written_digests=(_digest("candidate\n"),),
                failure=None,
                recovery_ref=_RECOVERY_REF,
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult(
                status=ManagedArtifactWriteStatus.REJECTED,
                written_artifact_refs=(),
                written_digests=(),
                failure=ManagedArtifactWriteFailure.PATH_STATE_MISMATCH,
                recovery_ref=_RECOVERY_REF,
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult.model_validate_json(
                valid_json.replace('"recovery_ref":null', f'"recovery_ref":"{_RECOVERY_REF}"')
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult.model_validate_json(
                json.dumps(
                    {
                        "status": "RECOVERY_REQUIRED",
                        "written_artifact_refs": [],
                        "written_digests": [],
                        "failure": "RECOVERY_REQUIRED",
                    }
                )
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult(
                status=ManagedArtifactWriteStatus.RECOVERY_REQUIRED,
                written_artifact_refs=(),
                written_digests=(),
                failure=ManagedArtifactWriteFailure.RECOVERY_REQUIRED,
                recovery_ref=None,
            )
        for invalid_recovery_ref in (
            "snapshot-body",
            "exception-detail",
            "workspace-record",
        ):
            with self.subTest(invalid_recovery_ref=invalid_recovery_ref):
                with self.assertRaises(ValidationError):
                    ManagedArtifactWriteResult(
                        status=ManagedArtifactWriteStatus.RECOVERY_REQUIRED,
                        written_artifact_refs=(),
                        written_digests=(),
                        failure=ManagedArtifactWriteFailure.RECOVERY_REQUIRED,
                        recovery_ref=invalid_recovery_ref,
                    )
                with self.assertRaises(ValidationError):
                    ManagedArtifactRecoveryResult(
                        status=ManagedArtifactRecoveryStatus.RECOVERED,
                        recovery_ref=invalid_recovery_ref,
                    )
        recovery_json = ManagedArtifactRecoveryResult(
            status=ManagedArtifactRecoveryStatus.RECOVERED,
            recovery_ref=_RECOVERY_REF,
        ).model_dump_json()
        for invalid_recovery_json in (
            recovery_json.replace(f'"recovery_ref":"{_RECOVERY_REF}"', '"recovery_ref":null'),
            recovery_json[:-1] + ',"unexpected":"field"}',
            recovery_json.replace(f'"recovery_ref":"{_RECOVERY_REF}"', '"recovery_ref":7'),
        ):
            with self.assertRaises(ValidationError):
                ManagedArtifactRecoveryResult.model_validate_json(invalid_recovery_json)
        mismatches = (
            (ManagedArtifactWriteStatus.REJECTED, ManagedArtifactWriteFailure.STORAGE_UNAVAILABLE),
            (ManagedArtifactWriteStatus.REJECTED, ManagedArtifactWriteFailure.RECOVERY_REQUIRED),
            (ManagedArtifactWriteStatus.STORAGE_UNAVAILABLE, ManagedArtifactWriteFailure.PATH_ESCAPE),
            (ManagedArtifactWriteStatus.STORAGE_UNAVAILABLE, ManagedArtifactWriteFailure.RUNTIME_INVARIANT_FAILED),
            (ManagedArtifactWriteStatus.RECOVERY_REQUIRED, ManagedArtifactWriteFailure.STORAGE_UNAVAILABLE),
            (ManagedArtifactWriteStatus.RECOVERY_REQUIRED, ManagedArtifactWriteFailure.RUNTIME_INVARIANT_FAILED),
        )
        for status, failure in mismatches:
            with self.subTest(status=status, failure=failure):
                with self.assertRaises(ValidationError):
                    ManagedArtifactWriteResult(
                        status=status,
                        written_artifact_refs=(),
                        written_digests=(),
                        failure=failure,
                        recovery_ref=(
                            _RECOVERY_REF
                            if status is ManagedArtifactWriteStatus.RECOVERY_REQUIRED
                            else None
                        ),
                    )

    def test_rrc3_runtime_invariant_is_rejected_and_sanitized(self) -> None:
        result = _rejected(ManagedArtifactWriteFailure.RUNTIME_INVARIANT_FAILED)
        serialized = result.model_dump_json()
        self.assertNotIn("exception", serialized.casefold())
        self.assertNotIn("modules/", serialized)
        self.assertNotIn("workspace", serialized.casefold())
        self.assertNotIn("snapshot", serialized.casefold())
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult(
                status=ManagedArtifactWriteStatus.STORAGE_UNAVAILABLE,
                written_artifact_refs=(),
                written_digests=(),
                failure=ManagedArtifactWriteFailure.RUNTIME_INVARIANT_FAILED,
                recovery_ref=None,
            )

    def test_rrc4_legacy_target_document_contracts_round_trip_unchanged(self) -> None:
        content = "# Legacy\n"
        mutation = TargetDocumentMutation(
            path="README.md",
            artifact_kind=ArtifactDocumentKind.ROOT_README,
            mode=DocumentMutationMode.CREATE,
            expected_current_digest=None,
            content=content,
            content_digest=_digest(content),
            sealed=False,
        )
        plan = TargetDocumentPlan(
            project_id="prj_0123456789abcdef",
            baseline_commit="a" * 40,
            mutations=(mutation,),
        )
        write_result = DocumentWriteResult(
            status=DocumentWriteStatus.APPLIED,
            written_paths=("README.md",),
            written_digests=(_digest(content),),
            failure=None,
        )
        self.assertEqual(
            mutation,
            TargetDocumentMutation.model_validate_json(mutation.model_dump_json()),
        )
        self.assertEqual(
            plan,
            TargetDocumentPlan.model_validate_json(plan.model_dump_json()),
        )
        self.assertEqual(
            write_result,
            DocumentWriteResult.model_validate_json(write_result.model_dump_json()),
        )

    def test_rrc5_new_names_are_exported_only_by_the_contract_module(self) -> None:
        source_path = _contract_source_path()
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        }
        self.assertTrue(
            {
                "ManagedArtifactWriteStatus",
                "ManagedArtifactWriteFailure",
                "ManagedArtifactWriteResult",
                "ManagedArtifactRecoveryStatus",
                "ManagedArtifactRecoveryResult",
            }.issubset(names)
        )
        self.assertIn(
            "RecoveryEvidenceRef",
            {
                node.target.id
                for node in tree.body
                if isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
            },
        )
        for public_name in (
            "ManagedArtifactWriteStatus",
            "ManagedArtifactWriteFailure",
            "ManagedArtifactWriteResult",
            "ManagedArtifactRecoveryStatus",
            "ManagedArtifactRecoveryResult",
            "RecoveryEvidenceRef",
        ):
            self.assertIn(f'"{public_name}"', source)
        self.assertNotIn("library.local_orchestration", source)
        self.assertNotIn("plan_managed_artifact(", source)
        self.assertNotIn("ArtifactTreeResolver", source)
        self.assertNotIn("import os", source)
        self.assertNotIn("import subprocess", source)

    def test_rtm1_recovery_required_missing_ref_guard_remains_red(self) -> None:
        payload = (
            '{"status":"RECOVERY_REQUIRED","written_artifact_refs":[],'
            '"written_digests":[],"failure":"RECOVERY_REQUIRED"}'
        )
        source = _contract_source_path().read_text(encoding="utf-8")
        mutated = source.replace(
            "            or self.recovery_ref is None\n        ):\n            raise ValueError(\"recovery-required results require one recovery reference\")",
            "        ):\n            raise ValueError(\"recovery-required results require one recovery reference\")",
            1,
        )
        self.assertNotEqual(source, mutated)
        self.assertTrue(_mutated_contract_accepts(mutated, payload))
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult.model_validate_json(payload)
        self.assertEqual(ManagedArtifactWriteStatus.RECOVERY_REQUIRED, _recovery_required().status)

    def test_rtm2_runtime_invariant_pairing_guard_remains_red(self) -> None:
        payload = (
            '{"status":"REJECTED","written_artifact_refs":[],'
            '"written_digests":[],"failure":"STORAGE_UNAVAILABLE",'
            '"recovery_ref":null}'
        )
        source = _contract_source_path().read_text(encoding="utf-8")
        mutated = source.replace(
            "                    ManagedArtifactWriteFailure.STORAGE_UNAVAILABLE,\n",
            "",
            1,
        )
        self.assertNotEqual(source, mutated)
        self.assertTrue(_mutated_contract_accepts(mutated, payload))
        with self.assertRaises(ValidationError):
            ManagedArtifactWriteResult.model_validate_json(payload)
        self.assertEqual(
            ManagedArtifactWriteFailure.RUNTIME_INVARIANT_FAILED,
            _rejected(ManagedArtifactWriteFailure.RUNTIME_INVARIANT_FAILED).failure,
        )


if __name__ == "__main__":
    unittest.main()
