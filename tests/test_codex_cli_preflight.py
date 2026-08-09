from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

from pydantic import ValidationError

from library.local_orchestration.codex_cli_adapter import CodexCliPreflight
from library.local_orchestration.contracts import CANONICAL_INSTALL_ROOT, InstallRoot, InstallationId, OwnedRelativePath
from library.local_orchestration.host_contracts import (
    CodexBlockReason, CodexBlocked, CodexCommandPort, CodexCommandResponse, CodexFilesystemPort,
    CodexMarketplaceName, CodexPluginName, CodexPreflightRequest,
    CodexSourceProof, CodexPreflightEligible,
)

INSTALL = InstallationId(value="installation-0123456789abcdef")
ROOT = InstallRoot(value=CANONICAL_INSTALL_ROOT)
MARKET = CodexMarketplaceName(value="probe-market")
PLUGIN = CodexPluginName(value="probe-plugin")
SOURCE = OwnedRelativePath(value="marketplaces/probe-market")


class Commands(CodexCommandPort):
    def __init__(self, values: list[str | dict[str, object] | Exception]) -> None:
        self.values: list[str | dict[str, object] | Exception] = values
        self.calls: list[tuple[str, ...]] = []

    def execute(self, arguments: tuple[str, ...], timeout_seconds: float) -> CodexCommandResponse:
        self.calls.append(arguments)
        value = self.values.pop(0)
        if isinstance(value, Exception):
            raise value
        return CodexCommandResponse(exit_code=0, stdout=value if isinstance(value, str) else json.dumps(value), stderr="")


class Source(CodexFilesystemPort):
    def __init__(self, proof: CodexSourceProof | Exception | None = None) -> None:
        self.proof, self.calls = proof, 0

    def resolve_source(self, request: CodexPreflightRequest) -> CodexSourceProof:
        self.calls += 1
        if isinstance(self.proof, Exception):
            raise self.proof
        return self.proof or CodexSourceProof(installation_id=request.installation_id, root=request.root,
            locator=request.marketplace_source, absolute_path=r"C:\Users\tester\JohnnyAIWorkflow\marketplaces\probe-market")


class Nonzero(Commands):
    def execute(self, arguments: tuple[str, ...], timeout_seconds: float) -> CodexCommandResponse:
        self.calls.append(arguments)
        return CodexCommandResponse(exit_code=1, stdout="", stderr="denied")


def request(source: OwnedRelativePath = SOURCE) -> CodexPreflightRequest:
    return CodexPreflightRequest(installation_id=INSTALL, root=ROOT, marketplace=MARKET,
        plugin=PLUGIN, marketplace_source=source)


def version() -> str:
    return "codex-cli 0.144.0-alpha.4\n"


def marketplace(items: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {"marketplaces": items or []}


def plugin_list(items: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {"installed": items or [], "available": []}


def plugin(name: str = PLUGIN.value, market: str = MARKET.value) -> dict[str, object]:
    return {"pluginId": f"{name}@{market}", "name": name, "marketplaceName": market,
        "version": "1.0.0", "installed": True, "enabled": True, "source": "local",
        "installPolicy": "trusted", "authPolicy": "none"}


class CodexCliPreflightTests(unittest.TestCase):
    def test_a1_official_shapes_and_invented_fields(self) -> None:
        command = Commands([version(), marketplace(), plugin_list()])
        result = CodexCliPreflight(command, Source()).check(request())
        self.assertIsInstance(result, CodexPreflightEligible)
        for payload in ({}, {"marketplaces": [], "extra": 1}):
            with self.subTest(payload=payload):
                result = CodexCliPreflight(Commands([version(), payload, plugin_list()]), Source()).check(request())
                self.assertIsInstance(result, CodexBlocked)

    def test_a1_wrong_plugin_shape_is_rejected_before_mutation(self) -> None:
        result = CodexCliPreflight(Commands([version(), marketplace(), {"installed": [{"id": "x", "root": "y"}], "available": []}]), Source()).check(request())
        self.assertEqual(CodexBlockReason.MALFORMED_OUTPUT, cast(CodexBlocked, result).reason)

    def test_a1_invalid_encoding_nonzero_and_unsupported_are_finite(self) -> None:
        for failure in (UnicodeDecodeError("utf-8", b"x", 0, 1, "bad"),):
            result = CodexCliPreflight(Commands([failure]), Source()).check(request())
            self.assertEqual(CodexBlockReason.INVALID_ENCODING, cast(CodexBlocked, result).reason)
        self.assertEqual(CodexBlockReason.COMMAND_FAILED, cast(CodexBlocked, CodexCliPreflight(Nonzero([]), Source()).check(request())).reason)
        self.assertEqual(CodexBlockReason.UNSUPPORTED_CLI, cast(CodexBlocked, CodexCliPreflight(Commands(["unknown"]), Source()).check(request())).reason)

    def test_a2_source_variants_and_constructed_proof_fail_closed(self) -> None:
        values: tuple[object, ...] = (None, "", " ", "/absolute", "file:///x", "../x", "marketplaces/Probe", "marketplaces/probe-suffix")
        for value in values:
            with self.subTest(value=value):
                with self.assertRaises((ValidationError, TypeError)):
                    CodexPreflightRequest.model_validate({**request().model_dump(), "marketplace_source": value})
        forged = CodexSourceProof.model_construct(installation_id=INSTALL, root=ROOT, locator=[], absolute_path="foreign")
        result = CodexCliPreflight(Commands([version(), marketplace(), plugin_list()]), Source(forged)).check(request())
        self.assertIsInstance(result, CodexBlocked)

    def test_a2_foreign_filesystem_proof_is_blocked_before_lists(self) -> None:
        proof = CodexSourceProof(installation_id=INSTALL, root=ROOT, locator=OwnedRelativePath(value="marketplaces/other"),
            absolute_path=r"C:\Users\tester\JohnnyAIWorkflow\marketplaces\other")
        command = Commands([version()])
        result = CodexCliPreflight(command, Source(proof)).check(request())
        self.assertEqual(CodexBlockReason.SOURCE_MISMATCH, cast(CodexBlocked, result).reason)
        self.assertEqual((('codex', '--version'),), tuple(command.calls))

    def test_a2_filesystem_oserror_is_finite(self) -> None:
        result = CodexCliPreflight(Commands([version()]), Source(OSError("source unavailable"))).check(request())
        self.assertEqual(CodexBlockReason.FILESYSTEM_FAILED, cast(CodexBlocked, result).reason)

    def test_a3_market_and_same_plugin_collisions_do_not_mutate(self) -> None:
        cases: tuple[tuple[dict[str, object], dict[str, object]], ...] = (
            (marketplace([{ "name": MARKET.value, "root": "root" }]), plugin_list()),
            (marketplace([{ "name": "other", "root": "root" }]), plugin_list([plugin(market="other")])),
        )
        for markets, plugins in cases:
            command = Commands([version(), markets, plugins])
            result = CodexCliPreflight(command, Source()).check(request())
            self.assertIsInstance(result, CodexBlocked)
            self.assertEqual(3, len(command.calls))

    def test_a4_declared_failures_are_finite(self) -> None:
        failures: tuple[Exception, ...] = (FileNotFoundError(), PermissionError(), subprocess.TimeoutExpired("codex", 1), OSError())
        for failure in failures:
            result = CodexCliPreflight(Commands([failure]), Source()).check(request())
            self.assertIsInstance(result, CodexBlocked)
        self.assertIsInstance(CodexCliPreflight(Commands([version()]), Source(), 0.0).check(request()), CodexBlocked)
        self.assertIsInstance(CodexCliPreflight(cast(CodexCommandPort, None), Source()).check(request()), CodexBlocked)

    def test_a5_existing_and_empty_git_snapshots_are_unchanged(self) -> None:
        with TemporaryDirectory() as directory:
            for name in ("existing", "empty"):
                repo = Path(directory) / name
                repo.mkdir()
                subprocess.run(("git", "init", "--quiet", str(repo)), check=True, shell=False, capture_output=True)
                if name == "existing":
                    (repo / "kept.txt").write_bytes(b"kept")
                    subprocess.run(("git", "-C", str(repo), "add", "kept.txt"), check=True, shell=False, capture_output=True)
                    subprocess.run(("git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--quiet", "-m", "seed"), check=True, shell=False, capture_output=True)
                before_status = subprocess.run(("git", "-C", str(repo), "status", "--porcelain"), check=True, shell=False, capture_output=True).stdout
                before_bytes = tuple(sorted((p.relative_to(repo).as_posix(), p.read_bytes()) for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts))
                CodexCliPreflight(Commands([FileNotFoundError()]), Source()).check(request())
                after_status = subprocess.run(("git", "-C", str(repo), "status", "--porcelain"), check=True, shell=False, capture_output=True).stdout
                after_bytes = tuple(sorted((p.relative_to(repo).as_posix(), p.read_bytes()) for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts))
                self.assertEqual((before_status, before_bytes), (after_status, after_bytes))


if __name__ == "__main__":
    unittest.main()
