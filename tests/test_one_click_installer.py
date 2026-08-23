"""L9 one-click installer wrapper tests: R1 - R5 acceptance closure."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from library.local_orchestration.plugin_bundle_builder import (
    PluginBundleBuilder,
    PluginBundleBuildRequest,
    PluginBundleBuildStatus,
)
from library.local_orchestration.runtime_dependency_lock import (
    build_approved_runtime_lock,
)
from library.local_orchestration.windows_package_manifest import (
    build_payload_manifest,
)
from tests.staging.plugin_distribution_vita.harness import delete_disposable_tree
from tests.test_plugin_distribution_bundle import _run_git

_REPO_ROOT = Path(__file__).resolve().parents[1]
_WRAPPER_NAME = "johnny-install.cmd"
_BUNDLE_NAME = "johnny-ai-skill-0.4.9.zip"
_APPROVED_DIGEST = (
    "2365b6f70a06f00ae0aed008371f7cc0b5afd0cb148a77e7476416bf25854aef"
)


def _decoded_console_stream(stream: bytes | None, name: str) -> str:
    """Decode one captured Windows console stream without a code-page assumption."""

    if stream is None:
        raise AssertionError(f"{name} was not captured")
    return stream.decode("utf-8", errors="replace")


def _console_observation(completed: subprocess.CompletedProcess[bytes]) -> str:
    """Return the complete decoded observation from both console output streams."""

    stdout = _decoded_console_stream(completed.stdout, "stdout")
    stderr = _decoded_console_stream(completed.stderr, "stderr")
    observation = f"stdout:\n{stdout}\nstderr:\n{stderr}"
    if not stdout and not stderr:
        raise AssertionError("console observation was empty")
    return observation


def _module_suppressed_environment(module_root: Path) -> dict[str, str]:
    """Mask the utility module in a disposable environment."""

    module_root.mkdir()
    (module_root / "Microsoft.PowerShell.Utility.psd1").write_text(
        "@{\n"
        "ModuleVersion = '1.0.0'\n"
        "GUID = '5a7e1c9d-6ad9-4df9-8f07-4d5e12eb4f14'\n"
        "FunctionsToExport = @()\n"
        "CmdletsToExport = @()\n"
        "VariablesToExport = @()\n"
        "AliasesToExport = @()\n"
        "}\n",
        encoding="ascii",
    )
    environment = os.environ.copy()
    environment["PSModulePath"] = str(module_root)
    return environment


def _system_powershell_environment() -> dict[str, str]:
    """Use the Windows PowerShell modules for the delegated install prompt."""

    environment = os.environ.copy()
    environment["PSModulePath"] = r"C:\Windows\System32\WindowsPowerShell\v1.0\Modules"
    return environment


class OneClickInstallerWrapperFormatTests(unittest.TestCase):
    """R1: wrapper format, double-entry digest pin, and line endings."""

    def test_wrapper_is_ascii_and_crlf_only(self) -> None:
        wrapper_path = _REPO_ROOT / _WRAPPER_NAME
        self.assertTrue(wrapper_path.is_file(), f"{_WRAPPER_NAME} must exist")
        raw_bytes = wrapper_path.read_bytes()

        try:
            text = raw_bytes.decode("ascii")
        except UnicodeDecodeError as err:
            self.fail(f"{_WRAPPER_NAME} contains non-ASCII characters: {err}")

        lines_with_lf = raw_bytes.split(b"\n")
        for line in lines_with_lf[:-1]:
            self.assertTrue(
                line.endswith(b"\r"),
                f"Line endings must be CRLF: found bare LF in {line!r}",
            )

        self.assertIn(f'set "BUNDLE_NAME={_BUNDLE_NAME}"', text)
        self.assertIn(f'set "APPROVED_DIGEST={_APPROVED_DIGEST}"', text)
        self.assertNotIn("Get-FileHash", text)
        self.assertIn("[System.Security.Cryptography.SHA256]::Create()", text)
        self.assertIn(".Replace('-', '').ToLowerInvariant()", text)
        self.assertIn("DIGEST_UNREADABLE", text)
        self.assertLess(
            text.index("DIGEST_UNREADABLE"), text.index("Add-Type -AssemblyName")
        )


class OneClickInstallerGateTests(unittest.TestCase):
    """R2 & R3: missing bundle and tampered digest block before extraction."""

    def test_missing_bundle_fails_with_bundle_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp_dir = Path(temporary)
            wrapper_dst = temp_dir / _WRAPPER_NAME
            shutil.copy2(_REPO_ROOT / _WRAPPER_NAME, wrapper_dst)

            completed = subprocess.run(
                ["cmd.exe", "/c", str(wrapper_dst)],
                cwd=str(temp_dir),
                capture_output=True,
                check=False,
            )
            console = _console_observation(completed)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("BUNDLE_NOT_FOUND", console)
            self.assertFalse((temp_dir / "install.ps1").exists())

    def test_tampered_bundle_fails_with_digest_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp_dir = Path(temporary)
            module_root = temp_dir / "suppressed-powershell-modules"
            wrapper_dst = temp_dir / _WRAPPER_NAME
            shutil.copy2(_REPO_ROOT / _WRAPPER_NAME, wrapper_dst)

            tampered_zip = temp_dir / _BUNDLE_NAME
            with zipfile.ZipFile(tampered_zip, "w") as zf:
                zf.writestr("install.ps1", "# dummy\n")

            completed = subprocess.run(
                ["cmd.exe", "/c", str(wrapper_dst)],
                cwd=str(temp_dir),
                capture_output=True,
                check=False,
                env=_module_suppressed_environment(module_root),
            )
            console = _console_observation(completed)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("DIGEST_MISMATCH", console)
            self.assertFalse((temp_dir / "install.ps1").exists())


class BlockedPathVisibilityTests(unittest.TestCase):
    """Every exit holds the console, or a double-click user reads nothing.

    Explorer closes the window the moment the script ends, so an unpaused
    `exit /b` means the digest refusal this wrapper exists to deliver is
    never seen. Asserted structurally: matching the localized pause prompt
    in captured output would bind the test to the host's console codepage.
    """

    def test_every_exit_is_preceded_by_a_pause(self) -> None:
        lines = (
            (_REPO_ROOT / _WRAPPER_NAME)
            .read_bytes()
            .decode("ascii")
            .replace("\r\n", "\n")
            .split("\n")
        )
        exit_lines = [
            index
            for index, line in enumerate(lines)
            if line.strip().startswith("exit /b")
        ]
        self.assertGreaterEqual(len(exit_lines), 3)
        for index in exit_lines:
            preceding = [
                line.strip() for line in lines[max(0, index - 3) : index] if line.strip()
            ]
            with self.subTest(exit_line=lines[index].strip()):
                self.assertIn("pause", preceding)


class OneClickInstallerSmokeAndPayloadTests(unittest.TestCase):
    """R4 & R5: chain smoke with real zip and clean bundle build payload check.

    The cell below builds a synthetic bundle and rewrites the pinned digest to
    match it, so it proves the wrapper's mechanism only. It is deliberately not
    the R4 real-artifact evidence: the released 443,765-byte zip is a build
    output that cannot live in the repository. The real-artifact chain is
    recorded as an owner/control-plane execution in the L9 registry row.
    """

    def test_smoke_with_synthetic_matching_bundle_reaches_install_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp_dir = Path(temporary)
            bundle_path = temp_dir / _BUNDLE_NAME
            real_install_ps1 = (_REPO_ROOT / "install.ps1").read_text(encoding="utf-8")
            real_lock = (_REPO_ROOT / "requirements-runtime.lock").read_text(
                encoding="utf-8"
            )

            with zipfile.ZipFile(bundle_path, "w") as zf:
                zf.writestr("install.ps1", real_install_ps1)
                zf.writestr("requirements-runtime.lock", real_lock)

            bundle_hash = hashlib.sha256(bundle_path.read_bytes()).hexdigest()

            wrapper_content = (
                (_REPO_ROOT / _WRAPPER_NAME)
                .read_text(encoding="ascii")
                .replace(_APPROVED_DIGEST, bundle_hash)
            )
            synthetic_wrapper = temp_dir / _WRAPPER_NAME
            synthetic_wrapper.write_bytes(
                wrapper_content.replace("\r\n", "\n")
                .replace("\n", "\r\n")
                .encode("ascii")
            )

            completed = subprocess.run(
                ["cmd.exe", "/c", str(synthetic_wrapper)],
                cwd=str(temp_dir),
                input=b"\n",
                capture_output=True,
                check=False,
                env=_system_powershell_environment(),
            )
            console = _console_observation(completed)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("USER_DECLINED", console)
            self.assertFalse((temp_dir / "install.ps1").exists())

    def test_clean_clone_bundle_build_remains_bundled(self) -> None:
        workspace = Path(tempfile.mkdtemp(prefix="johnny-bundle-build-"))
        try:
            source = workspace / "src"
            _run_git(_REPO_ROOT, "clone", "--no-hardlinks", str(_REPO_ROOT), str(source))
            head = _run_git(source, "rev-parse", "HEAD")
            manifest = build_payload_manifest(
                source, head, build_approved_runtime_lock()
            )
            dist = workspace / "dist"
            dist.mkdir()
            build_result = PluginBundleBuilder().build(
                PluginBundleBuildRequest(
                    repository_root=source, output_root=dist, manifest=manifest
                )
            )
            self.assertIs(
                build_result.status,
                PluginBundleBuildStatus.BUNDLED,
                f"Bundle build failed: {build_result.failure}",
            )
        finally:
            delete_disposable_tree(workspace)


if __name__ == "__main__":
    unittest.main()
