"""L10: the wrapper's pin cannot silently drift from the released bundle."""

from __future__ import annotations

import hashlib
import os
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.plugin_bundle_builder import _CANDIDATE_NAME
from library.local_orchestration.release_pin_guard import (
    ReleasePinFailure,
    ReleasePinStatus,
    declared_plugin_version,
    expected_bundle_name,
    read_wrapper_pin,
    verify_release_pin,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_WRAPPER = _REPO_ROOT / "johnny-install.cmd"
_MANIFEST = _REPO_ROOT / ".codex-plugin" / "plugin.json"
_RELEASED_BUNDLE = Path.home() / "Desktop" / "johnny-ai-skill-dist" / "live-candidate"


def _write_wrapper(path: Path, bundle_name: str, digest: str) -> None:
    path.write_bytes(
        (
            "@echo off\r\n"
            f'set "BUNDLE_NAME={bundle_name}"\r\n'
            f'set "APPROVED_DIGEST={digest}"\r\n'
        ).encode("ascii")
    )


def _bundle(path: Path, payload: bytes) -> str:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("install.ps1", payload.decode("ascii"))
    return hashlib.sha256(path.read_bytes()).hexdigest()


class VersionAgreementTests(unittest.TestCase):
    """L10-R1: one declared version, and every name agrees with it."""

    def test_every_pinned_name_agrees_with_the_declared_version(self) -> None:
        version, failure = declared_plugin_version(_MANIFEST)
        self.assertIsNone(failure)
        assert version is not None
        expected = expected_bundle_name(version)

        self.assertEqual(_CANDIDATE_NAME, expected)

        pin, pin_failure = read_wrapper_pin(_WRAPPER)
        self.assertIsNone(pin_failure)
        assert pin is not None
        self.assertEqual(pin.bundle_name, expected)


class WrapperParsingTests(unittest.TestCase):
    """L10-R2: the pin is read as data, and a bad wrapper is refused."""

    def test_the_real_wrapper_yields_both_literals(self) -> None:
        pin, failure = read_wrapper_pin(_WRAPPER)
        self.assertIsNone(failure)
        assert pin is not None
        self.assertTrue(pin.bundle_name.endswith(".zip"))
        self.assertEqual(len(pin.digest), 64)

    def test_a_missing_wrapper_is_refused(self) -> None:
        with TemporaryDirectory() as temporary:
            pin, failure = read_wrapper_pin(Path(temporary) / "absent.cmd")
            self.assertIsNone(pin)
            self.assertIs(failure, ReleasePinFailure.WRAPPER_UNREADABLE)

    def test_a_wrapper_without_pins_is_refused(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "johnny-install.cmd"
            path.write_bytes(b"@echo off\r\nexit /b 0\r\n")
            pin, failure = read_wrapper_pin(path)
            self.assertIsNone(pin)
            self.assertIs(failure, ReleasePinFailure.WRAPPER_PIN_MALFORMED)


class PreflightTests(unittest.TestCase):
    """L10-R3: the preflight compares the pin to a real built artifact."""

    def test_a_matching_bundle_is_admitted(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            bundle = base / "johnny-ai-skill-9.9.9.zip"
            digest = _bundle(bundle, b"# install")
            wrapper = base / "johnny-install.cmd"
            _write_wrapper(wrapper, bundle.name, digest)
            status, failure = verify_release_pin(wrapper, bundle)
            self.assertIs(status, ReleasePinStatus.MATCHED)
            self.assertIsNone(failure)

    def test_a_rebuilt_bundle_with_a_stale_pin_is_refused(self) -> None:
        """The exact release defect: version kept, content changed."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            bundle = base / "johnny-ai-skill-9.9.9.zip"
            stale_digest = _bundle(bundle, b"# install")
            wrapper = base / "johnny-install.cmd"
            _write_wrapper(wrapper, bundle.name, stale_digest)
            _bundle(bundle, b"# install, rebuilt with new payload")
            status, failure = verify_release_pin(wrapper, bundle)
            self.assertIs(status, ReleasePinStatus.REFUSED)
            self.assertIs(failure, ReleasePinFailure.DIGEST_MISMATCH)

    def test_a_version_bump_that_forgot_the_wrapper_is_refused(self) -> None:
        """The other release defect: version bumped, wrapper untouched."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            published = base / "johnny-ai-skill-9.9.10.zip"
            digest = _bundle(published, b"# install")
            wrapper = base / "johnny-install.cmd"
            _write_wrapper(wrapper, "johnny-ai-skill-9.9.9.zip", digest)
            status, failure = verify_release_pin(wrapper, published)
            self.assertIs(status, ReleasePinStatus.REFUSED)
            self.assertIs(failure, ReleasePinFailure.BUNDLE_NAME_MISMATCH)

    def test_an_absent_bundle_is_refused(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            wrapper = base / "johnny-install.cmd"
            _write_wrapper(wrapper, "johnny-ai-skill-9.9.9.zip", "0" * 64)
            status, failure = verify_release_pin(
                wrapper, base / "johnny-ai-skill-9.9.9.zip"
            )
            self.assertIs(status, ReleasePinStatus.REFUSED)
            self.assertIs(failure, ReleasePinFailure.BUNDLE_UNREADABLE)


@unittest.skipUnless(
    os.environ.get("JOHNNY_LIVE_QUAL") == "1",
    "gated: requires the built release artifact on this host",
)
class ReleasedArtifactTests(unittest.TestCase):
    """L10-R4: the shipped wrapper approves the shipped bundle."""

    def test_the_wrapper_matches_the_released_bundle(self) -> None:
        pin, failure = read_wrapper_pin(_WRAPPER)
        self.assertIsNone(failure)
        assert pin is not None
        bundle = _RELEASED_BUNDLE / pin.bundle_name
        if not bundle.is_file():
            self.skipTest(f"released bundle not present: {bundle}")
        status, verify_failure = verify_release_pin(_WRAPPER, bundle)
        self.assertIs(status, ReleasePinStatus.MATCHED, f"{verify_failure}")


if __name__ == "__main__":
    unittest.main()
