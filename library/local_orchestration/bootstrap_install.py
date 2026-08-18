"""Stdlib-only live-install bootstrap; the only code that runs before the venv.

Typed contracts need pydantic, and pydantic lives inside the control venv,
so this script does exactly three things with the standard library alone:
stage the bundle, create the hash-locked venv (the same command sequence as
the canonical `venv_effect_port`), and hand off to the typed composition
running on the venv interpreter. Every failure self-cleans what this
bootstrap created and exits with a typed JSON line.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

_BOOTSTRAP_COMMAND: tuple[str, ...] = ("py", "-3.11")
_CREATE_TIMEOUT = 300
_INSTALL_TIMEOUT = 900
_COMPOSITION_TIMEOUT = 600
_LOCK_NAME = "requirements-runtime.lock"
_COMPOSITION_MODULE = "library.local_orchestration.johnny_live_install"


def _emit(code: str, status: str = "BLOCKED") -> int:
    print(json.dumps({"status": status, "code": code}, sort_keys=True))
    return 2


def _clear_read_only(function: object, path: str, excinfo: object) -> None:
    os.chmod(path, stat.S_IWRITE)
    if os.path.isfile(path):
        os.unlink(path)
    else:
        os.rmdir(path)


def _delete_tree(root: Path) -> None:
    try:
        if root.exists():
            shutil.rmtree(root, onerror=_clear_read_only)
    except OSError:
        pass


def _render_requirements(lock_path: Path) -> str | None:
    """Render hash-locked requirements from the committed lock; stdlib parity
    with `venv_effect_port.render_locked_requirements`."""

    try:
        recorded = json.loads(lock_path.read_text(encoding="utf-8"))
        dependencies = recorded["dependencies"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    lines = ["# Generated from the approved runtime dependency lock; do not edit."]
    try:
        for dependency in sorted(
            dependencies, key=lambda item: str(item["normalized_name"])
        ):
            hashes = " ".join(
                f"--hash=sha256:{artifact['sha256']}"
                for artifact in dependency["artifacts"]
            )
            lines.append(
                f"{dependency['normalized_name']}=="
                f"{dependency['exact_version']} {hashes}"
            )
    except (KeyError, TypeError):
        return None
    return "\n".join(lines) + "\n"


def _run(
    command: tuple[str, ...],
    timeout_seconds: int,
    working_directory: Path | None = None,
) -> int | None:
    try:
        completed = subprocess.run(
            command,
            shell=False,
            timeout=timeout_seconds,
            cwd=None if working_directory is None else str(working_directory),
        )
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    return completed.returncode


def run_bootstrap(bundle_zip: Path, johnny_root: Path) -> int:
    if not bundle_zip.is_file():
        return _emit("BUNDLE_NOT_FOUND")
    venv_root = johnny_root / "venv"
    if venv_root.exists() and any(venv_root.iterdir()):
        return _emit("VENV_ALREADY_PRESENT")

    staging = Path(tempfile.mkdtemp(prefix="johnny-install-staging-"))
    venv_created = False
    try:
        try:
            with zipfile.ZipFile(bundle_zip) as archive:
                archive.extractall(staging)
        except (OSError, ValueError, zipfile.BadZipFile):
            return _emit("BUNDLE_UNREADABLE")

        requirements = _render_requirements(staging / _LOCK_NAME)
        if requirements is None:
            return _emit("LOCK_UNREADABLE")
        requirements_path = staging / "locked-requirements.txt"
        requirements_path.write_text(requirements, encoding="utf-8")

        created = _run(
            (*_BOOTSTRAP_COMMAND, "-m", "venv", str(venv_root)), _CREATE_TIMEOUT
        )
        venv_created = True
        venv_python = venv_root / "Scripts" / "python.exe"
        if created != 0 or not venv_python.is_file():
            return _emit("VENV_CREATE_FAILED")

        installed = _run(
            (
                str(venv_python),
                "-m",
                "pip",
                "install",
                "--require-hashes",
                "--only-binary",
                ":all:",
                "--no-deps",
                "--disable-pip-version-check",
                "-r",
                str(requirements_path),
            ),
            _INSTALL_TIMEOUT,
        )
        if installed != 0:
            return _emit("WHEEL_INSTALL_FAILED")

        handed_off = _run(
            (
                str(venv_python),
                "-X",
                "utf8",
                "-m",
                _COMPOSITION_MODULE,
                "--bundle",
                str(bundle_zip),
                "--root",
                str(johnny_root),
            ),
            _COMPOSITION_TIMEOUT,
            working_directory=staging,
        )
        if handed_off is None:
            return _emit("COMPOSITION_UNREACHABLE")
        if handed_off != 0:
            # The typed composition already printed its own result line and
            # compensated its own effects; remove the bootstrap venv too.
            return handed_off
        venv_created = False
        return 0
    finally:
        if venv_created:
            _delete_tree(venv_root)
        _delete_tree(staging)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Johnny live-install bootstrap.")
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    arguments = parser.parse_args(sys.argv[1:] if argv is None else argv)
    return run_bootstrap(arguments.bundle, arguments.root)


if __name__ == "__main__":
    raise SystemExit(main())
