"""Acceptance tests for the immutable plugin runtime dependency lock."""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import TypedDict

from pydantic import ValidationError

from library.local_orchestration.runtime_dependency_lock import (
    LockedArtifact,
    RuntimeDependency,
    RuntimeDependencyLock,
    build_approved_runtime_lock,
    load_runtime_dependency_lock,
)


class _ArtifactPayload(TypedDict):
    filename: str
    sha256: str


class _DependencyPayload(TypedDict):
    normalized_name: str
    exact_version: str
    environment_marker: str | None
    source_kind: str
    artifacts: list[_ArtifactPayload]


class _LockPayload(TypedDict):
    schema_version: int
    python_constraint: str
    dependencies: list[_DependencyPayload]
    lock_digest: str


def _repository_root() -> Path:
    return Path(__file__).parents[1]


def _payload(lock: RuntimeDependencyLock) -> _LockPayload:
    dependencies: list[_DependencyPayload] = []
    for dependency in lock.dependencies:
        artifacts: list[_ArtifactPayload] = [
            {"filename": artifact.filename, "sha256": artifact.sha256}
            for artifact in dependency.artifacts
        ]
        dependencies.append(
            {
                "normalized_name": dependency.normalized_name,
                "exact_version": dependency.exact_version,
                "environment_marker": dependency.environment_marker,
                "source_kind": dependency.source_kind,
                "artifacts": artifacts,
            }
        )
    return {
        "schema_version": lock.schema_version,
        "python_constraint": lock.python_constraint,
        "dependencies": dependencies,
        "lock_digest": lock.lock_digest,
    }


def _clone_payload(payload: _LockPayload) -> _LockPayload:
    return {
        "schema_version": payload["schema_version"],
        "python_constraint": payload["python_constraint"],
        "dependencies": [
            {
                "normalized_name": dependency["normalized_name"],
                "exact_version": dependency["exact_version"],
                "environment_marker": dependency["environment_marker"],
                "source_kind": dependency["source_kind"],
                "artifacts": [
                    {
                        "filename": artifact["filename"],
                        "sha256": artifact["sha256"],
                    }
                    for artifact in dependency["artifacts"]
                ],
            }
            for dependency in payload["dependencies"]
        ],
        "lock_digest": payload["lock_digest"],
    }


class RuntimeDependencyLockTests(unittest.TestCase):
    def _lock(self) -> RuntimeDependencyLock:
        return load_runtime_dependency_lock(
            _repository_root() / "requirements-runtime.lock"
        )

    def test_runtime_lock_rejects_unhashed_wheel_before_install(self) -> None:
        payload = _payload(self._lock())
        payload["dependencies"][0]["artifacts"][0]["sha256"] = ""
        with self.assertRaises(ValidationError):
            RuntimeDependencyLock.model_validate(payload)

    def test_runtime_lock_round_trips_through_strict_models(self) -> None:
        lock = self._lock()
        rebuilt = RuntimeDependencyLock.model_validate_json(lock.model_dump_json())
        self.assertEqual(rebuilt, lock)
        self.assertEqual(rebuilt.lock_digest, lock.lock_digest)

    def test_runtime_lock_contains_the_exact_six_approved_wheels(self) -> None:
        lock = self._lock()
        identity = tuple(
            (
                dependency.normalized_name,
                dependency.exact_version,
                dependency.artifacts[0].filename,
                dependency.artifacts[0].sha256,
            )
            for dependency in lock.dependencies
        )
        self.assertEqual(
            identity,
            (
                (
                    "pydantic",
                    "2.13.4",
                    "pydantic-2.13.4-py3-none-any.whl",
                    "45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba",
                ),
                (
                    "pydantic_core",
                    "2.46.4",
                    "pydantic_core-2.46.4-cp311-cp311-win_amd64.whl",
                    "6f2eeda33a839975441c86a4119e1383c50b47faf0cbb5176985565c6bb02c33",
                ),
                (
                    "pywin32",
                    "311",
                    "pywin32-311-cp311-cp311-win_amd64.whl",
                    "3ce80b34b22b17ccbd937a6e78e7225d80c52f5ab9940fe0506a1a16f3dab503",
                ),
                (
                    "annotated_types",
                    "0.8.0",
                    "annotated_types-0.8.0-py3-none-any.whl",
                    "f072f4d804ea359e4eaf198b1af7a8b0943881a87f31bb764f8bf219bb9419e0",
                ),
                (
                    "typing_extensions",
                    "4.15.0",
                    "typing_extensions-4.15.0-py3-none-any.whl",
                    "f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548",
                ),
                (
                    "typing_inspection",
                    "0.4.2",
                    "typing_inspection-0.4.2-py3-none-any.whl",
                    "4ed1cacbdc298c220f1bd249ed5287caa16f34d44ef4e9c3d0cbad5b521545e7",
                ),
            ),
        )

    def test_runtime_lock_digest_is_canonical_and_stable(self) -> None:
        lock = self._lock()
        rebuilt = build_approved_runtime_lock()
        self.assertEqual(lock.lock_digest, rebuilt.lock_digest)
        self.assertEqual(lock.canonical_json(), rebuilt.canonical_json())

    def test_runtime_lock_rejects_unknown_dependency(self) -> None:
        payload = _payload(self._lock())
        payload["dependencies"].append(
            {
                "normalized_name": "unknown_package",
                "exact_version": "1.0.0",
                "environment_marker": None,
                "source_kind": "wheel",
                "artifacts": [{"filename": "unknown-1.0.0.whl", "sha256": "a" * 64}],
            }
        )
        with self.assertRaises(ValidationError):
            RuntimeDependencyLock.model_validate(payload)

    def test_runtime_lock_rejects_duplicate_dependency(self) -> None:
        payload = _payload(self._lock())
        payload["dependencies"].append(payload["dependencies"][0])
        with self.assertRaises(ValidationError):
            RuntimeDependencyLock.model_validate(payload)

    def test_runtime_lock_rejects_environment_mismatch(self) -> None:
        payload = _payload(self._lock())
        payload["dependencies"][1]["environment_marker"] = "platform_system == 'Linux'"
        with self.assertRaises(ValidationError):
            RuntimeDependencyLock.model_validate(payload)

    def test_runtime_lock_rejects_wrong_source_kind(self) -> None:
        payload = _payload(self._lock())
        payload["dependencies"][0]["source_kind"] = "sdist"
        with self.assertRaises(ValidationError):
            RuntimeDependencyLock.model_validate(payload)

    def test_runtime_dependency_rejects_unknown_field(self) -> None:
        with self.assertRaises(ValidationError):
            RuntimeDependency.model_validate(
                {
                    "normalized_name": "sample",
                    "exact_version": "1.0.0",
                    "environment_marker": None,
                    "source_kind": "wheel",
                    "artifacts": [
                        {
                            "filename": "sample-1.0.0.whl",
                            "sha256": "a" * 64,
                        }
                    ],
                    "unexpected": "forbidden",
                }
            )

    def test_runtime_lock_rejects_digest_mutation(self) -> None:
        payload = _payload(self._lock())
        payload["lock_digest"] = "0" * 64
        with self.assertRaises(ValidationError):
            RuntimeDependencyLock.model_validate(payload)

    def test_locked_artifact_rejects_non_sha256_value(self) -> None:
        with self.assertRaises(ValidationError):
            LockedArtifact(filename="sample.whl", sha256="not-a-digest")

    def test_runtime_dependency_requires_an_artifact(self) -> None:
        with self.assertRaises(ValidationError):
            RuntimeDependency(
                normalized_name="sample",
                exact_version="1.0.0",
                environment_marker=None,
                source_kind="wheel",
                artifacts=(),
            )

    def test_lock_module_has_no_install_or_network_effect_surface(self) -> None:
        source = (
            _repository_root() / "library" / "local_orchestration" / "runtime_dependency_lock.py"
        ).read_text(encoding="utf-8")
        for forbidden in ("subprocess", "pip", "urllib", "requests", "socket"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
