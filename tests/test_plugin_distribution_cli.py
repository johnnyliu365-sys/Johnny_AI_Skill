from __future__ import annotations

import importlib
import io
import json
from contextlib import redirect_stdout
from unittest import TestCase

from library.local_orchestration.johnny_router_cli import main
from library.local_orchestration.johnny_router_contracts import (
    JohnnyRouterBlocked,
    JohnnyRouterCapabilityUnavailable,
    JohnnyRouterOperation,
    JohnnyRouterPreflightPort,
    JohnnyRouterResultCode,
    JohnnyRouterResultStatus,
    PreflightProbe,
)


_PROFILE_ID = "plugin-distribution-poc-r02"
_PROFILE_VERSION = "2"


class _RecordingPort:
    def __init__(self, probe: PreflightProbe) -> None:
        self.calls = 0
        self._probe = probe

    def probe(self) -> PreflightProbe:
        self.calls += 1
        return self._probe


class _ProbePort:
    def __init__(self, probe: PreflightProbe) -> None:
        self.calls = 0
        self._probe = probe

    def probe(self) -> PreflightProbe:
        self.calls += 1
        return self._probe


def _argv(operation: str = "PREFLIGHT") -> tuple[str, str, str]:
    return operation, _PROFILE_ID, _PROFILE_VERSION


class PluginDistributionCliTests(TestCase):
    def test_cli_unknown_operation_returns_blocked_without_preflight_port_call(self) -> None:
        port = _RecordingPort(PreflightProbe(git_available=True, python_version=(3, 11, 9)))

        result = main(("UNKNOWN", _PROFILE_ID, _PROFILE_VERSION), port)

        self.assertIsInstance(result, JohnnyRouterBlocked)
        self.assertEqual(result.status, JohnnyRouterResultStatus.BLOCKED)
        self.assertEqual(result.code, JohnnyRouterResultCode.UNKNOWN_OPERATION)
        self.assertIsNone(result.operation)
        self.assertEqual(port.calls, 0)

    def test_cli_exact_preflight_emits_one_canonical_success_json(self) -> None:
        port = _RecordingPort(PreflightProbe(git_available=True, python_version=(3, 11, 9)))
        output = io.StringIO()

        with redirect_stdout(output):
            result = main(_argv(), port)

        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(json.loads(lines[0]), json.loads(result.model_dump_json()))
        self.assertEqual(result.status, JohnnyRouterResultStatus.SUCCEEDED)
        self.assertEqual(result.code, JohnnyRouterResultCode.PREFLIGHT_PASSED)
        self.assertEqual(result.operation, JohnnyRouterOperation.PREFLIGHT)
        self.assertEqual(port.calls, 1)

    def test_cli_capability_failures_are_finite(self) -> None:
        cases = (
            (PreflightProbe(git_available=False, python_version=(3, 11, 9)), JohnnyRouterResultCode.GIT_UNAVAILABLE),
            (PreflightProbe(git_available=True, python_version=None), JohnnyRouterResultCode.PYTHON_UNAVAILABLE),
            (PreflightProbe(git_available=True, python_version=(3, 14, 0)), JohnnyRouterResultCode.PYTHON_INCOMPATIBLE),
        )
        for probe, code in cases:
            with self.subTest(code=code):
                port = _RecordingPort(probe)
                result = main(_argv(), port)
                self.assertIsInstance(result, JohnnyRouterCapabilityUnavailable)
                self.assertEqual(result.status, JohnnyRouterResultStatus.CAPABILITY_UNAVAILABLE)
                self.assertEqual(result.code, code)
                self.assertEqual(port.calls, 1)

    def test_cli_invalid_shape_stale_profile_and_malformed_probe_do_not_probe(self) -> None:
        cases = (
            ((), JohnnyRouterResultCode.INVALID_ARGUMENTS, None),
            (("PREFLIGHT", _PROFILE_ID), JohnnyRouterResultCode.INVALID_ARGUMENTS, None),
            (("PREFLIGHT", "stale-profile", _PROFILE_VERSION), JohnnyRouterResultCode.STALE_PROFILE, JohnnyRouterOperation.PREFLIGHT),
            (("PREFLIGHT", _PROFILE_ID, "1"), JohnnyRouterResultCode.STALE_PROFILE, JohnnyRouterOperation.PREFLIGHT),
        )
        for argv, code, operation in cases:
            with self.subTest(argv=argv):
                port = _RecordingPort(PreflightProbe(git_available=True, python_version=(3, 11, 9)))
                result = main(argv, port)
                self.assertIsInstance(result, JohnnyRouterBlocked)
                self.assertEqual(result.code, code)
                self.assertEqual(result.operation, operation)
                self.assertEqual(port.calls, 0)

        malformed = PreflightProbe.model_construct(git_available=True, python_version=(3, 11))
        port = _ProbePort(malformed)
        result = main(_argv(), port)
        self.assertIsInstance(result, JohnnyRouterBlocked)
        self.assertEqual(result.code, JohnnyRouterResultCode.INVALID_PROBE)
        self.assertEqual(result.operation, JohnnyRouterOperation.PREFLIGHT)
        self.assertEqual(port.calls, 1)

    def test_cli_deferred_operations_are_unavailable_without_probe(self) -> None:
        for operation in JohnnyRouterOperation:
            if operation is JohnnyRouterOperation.PREFLIGHT:
                continue
            with self.subTest(operation=operation):
                port = _RecordingPort(PreflightProbe(git_available=True, python_version=(3, 11, 9)))
                result = main(_argv(operation.value), port)
                self.assertIsInstance(result, JohnnyRouterCapabilityUnavailable)
                self.assertEqual(result.code, JohnnyRouterResultCode.OPERATION_UNAVAILABLE)
                self.assertEqual(result.operation, operation)
                self.assertEqual(port.calls, 0)

    def test_cli_imports_are_silent(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            importlib.import_module("library.workflow_router.profile")
            importlib.import_module("library.local_orchestration.johnny_router_contracts")
            importlib.import_module("library.local_orchestration.johnny_router_cli")
        self.assertEqual(output.getvalue(), "")
