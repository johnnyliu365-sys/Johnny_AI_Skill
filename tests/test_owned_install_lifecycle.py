"""Executable C1..C8 closure for the reopened owned install lifecycle."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from pydantic import ValidationError

from library.local_orchestration import (
    CANONICAL_INSTALL_ROOT,
    BlockReason,
    FakeHostLifecycle,
    FakeInstallLedger,
    FakeOwnedFilesystem,
    FakeProcessLifecycle,
    HostId,
    HostRegistrationReceipt,
    InstallBlocked,
    InstallRequest,
    InstallRoot,
    InstallSucceeded,
    InstallationId,
    LedgerAbsent,
    ManifestEntry,
    OwnedInstallLedger,
    OwnedInstallLifecycle,
    OwnedManifest,
    OwnedRelativePath,
    UninstallBlocked,
    UninstallNotInstalled,
    UninstallRemoved,
    UninstallRequest,
    digest_bytes,
)


@dataclass(frozen=True)
class LifecycleStack:
    service: OwnedInstallLifecycle
    request: InstallRequest
    uninstall_request: UninstallRequest
    filesystem: FakeOwnedFilesystem
    ledger: FakeInstallLedger
    host: FakeHostLifecycle
    process: FakeProcessLifecycle


class OwnedInstallLifecycleTests(unittest.TestCase):
    def test_c1_valid_install_persists_exact_ledger_and_receipt(self) -> None:
        with TemporaryDirectory() as directory:
            stack = build_stack(Path(directory))
            result = stack.service.install(stack.request)

            self.assertIsInstance(result, InstallSucceeded)
            assert isinstance(result, InstallSucceeded)
            self.assertEqual(result.ledger, stack.ledger.read())
            self.assertEqual(result.host_receipt, result.ledger.host_receipt)
            self.assertEqual(stack.request.installation_id, result.host_receipt.installation_id)
            self.assertTrue(stack.filesystem.manifest_matches(stack.request.installation_id, stack.request.manifest))

    def test_c2_owned_uninstall_is_exact_and_idempotent(self) -> None:
        with TemporaryDirectory() as directory:
            stack = build_stack(Path(directory))
            helper = stack.filesystem.write_unowned(
                OwnedRelativePath(value="payload/unowned-helper.txt"), b"foreign"
            )
            self.assertIsInstance(stack.service.install(stack.request), InstallSucceeded)

            removed = stack.service.uninstall(stack.uninstall_request)
            repeated = stack.service.uninstall(stack.uninstall_request)

            self.assertIsInstance(removed, UninstallRemoved)
            self.assertIsInstance(repeated, UninstallNotInstalled)
            self.assertEqual(b"foreign", helper.read_bytes())
            self.assertIsInstance(stack.ledger.read(), LedgerAbsent)
            self.assertFalse(stack.host.has_registration(stack.request.installation_id))
            self.assertFalse(stack.filesystem.has_owned_effects(stack.request.installation_id))

    def test_c3_only_the_canonical_root_is_accepted_before_effects(self) -> None:
        self.assertEqual(CANONICAL_INSTALL_ROOT, InstallRoot(value=CANONICAL_INSTALL_ROOT).value)
        variants = (
            CANONICAL_INSTALL_ROOT + "-extra",
            CANONICAL_INSTALL_ROOT + "\\",
            CANONICAL_INSTALL_ROOT.lower(),
            CANONICAL_INSTALL_ROOT.replace("\\", "%5C"),
            CANONICAL_INSTALL_ROOT + "\\..",
            "",
        )
        with TemporaryDirectory() as directory:
            stack = build_stack(Path(directory))
            for value in variants:
                with self.subTest(value=value), self.assertRaises(ValidationError):
                    InstallRoot.model_validate_json(json.dumps({"value": value}))
            self.assertEqual(0, total_effect_calls(stack))

    def test_c4_required_identity_manifest_and_path_values_fail_closed(self) -> None:
        invalid_values = (
            '{"value":null}',
            "{}",
            '{"value":""}',
            '{"value":" "}',
            '{"value":[]}',
        )
        for payload in invalid_values:
            with self.subTest(model="InstallationId", payload=payload), self.assertRaises(ValidationError):
                InstallationId.model_validate_json(payload)
            with self.subTest(model="OwnedRelativePath", payload=payload), self.assertRaises(ValidationError):
                OwnedRelativePath.model_validate_json(payload)

        invalid_manifests = (
            '{"entries":null}',
            "{}",
            '{"entries":""}',
            '{"entries":" "}',
            '{"entries":[]}',
        )
        for payload in invalid_manifests:
            with self.subTest(model="OwnedManifest", payload=payload), self.assertRaises(ValidationError):
                OwnedManifest.model_validate_json(payload)

        with TemporaryDirectory() as directory:
            self.assertEqual(0, total_effect_calls(build_stack(Path(directory))))

    def test_c5_foreign_tampered_and_indirect_deletion_are_blocked(self) -> None:
        with TemporaryDirectory() as directory:
            foreign = build_stack(Path(directory) / "foreign")
            self.assertIsInstance(foreign.service.install(foreign.request), InstallSucceeded)
            before = snapshot_tree(Path(directory) / "foreign")
            result = foreign.service.uninstall(
                UninstallRequest(
                    installation_id=InstallationId(value="foreign-installation"),
                    root=InstallRoot(value=CANONICAL_INSTALL_ROOT),
                )
            )
            assert_blocked(result, BlockReason.FOREIGN_INSTALLATION)
            self.assertEqual(before, snapshot_tree(Path(directory) / "foreign"))

        with TemporaryDirectory() as directory:
            tampered = build_stack(Path(directory))
            installed = tampered.service.install(tampered.request)
            assert isinstance(installed, InstallSucceeded)
            forged_manifest = OwnedManifest(
                entries=(
                    ManifestEntry(
                        path=installed.ledger.manifest.entries[0].path,
                        digest=digest_bytes(b"tampered"),
                    ),
                )
            )
            tampered.ledger.replace_for_test(
                OwnedInstallLedger(
                    installation_id=installed.ledger.installation_id,
                    root=installed.ledger.root,
                    manifest=forged_manifest,
                    host_receipt=installed.host_receipt,
                )
            )
            before = snapshot_tree(Path(directory))
            assert_blocked(
                tampered.service.uninstall(tampered.uninstall_request), BlockReason.MANIFEST_MISMATCH
            )
            self.assertEqual(before, snapshot_tree(Path(directory)))

        with TemporaryDirectory() as directory:
            foreign_receipt = build_stack(Path(directory))
            installed = foreign_receipt.service.install(foreign_receipt.request)
            assert isinstance(installed, InstallSucceeded)
            forged_receipt = HostRegistrationReceipt(
                installation_id=installed.ledger.installation_id,
                host_id=HostId.LOCAL_FAKE,
                registration_ref="owned:somebody-else",
            )
            foreign_receipt.ledger.replace_for_test(
                OwnedInstallLedger(
                    installation_id=installed.ledger.installation_id,
                    root=installed.ledger.root,
                    manifest=installed.ledger.manifest,
                    host_receipt=forged_receipt,
                )
            )
            before = snapshot_tree(Path(directory))
            assert_blocked(
                foreign_receipt.service.uninstall(foreign_receipt.uninstall_request),
                BlockReason.FOREIGN_HOST_RECEIPT,
            )
            self.assertEqual(before, snapshot_tree(Path(directory)))

        with TemporaryDirectory() as directory:
            indirect = build_stack(Path(directory))
            installed = indirect.service.install(indirect.request)
            assert isinstance(installed, InstallSucceeded)
            helper = indirect.filesystem.write_unowned(
                OwnedRelativePath(value="payload/helper.txt"), b"must-remain"
            )
            directory_manifest = OwnedManifest(
                entries=(ManifestEntry(path=OwnedRelativePath(value="payload"), digest=digest_bytes(b"x")),)
            )
            indirect.ledger.replace_for_test(
                OwnedInstallLedger(
                    installation_id=installed.ledger.installation_id,
                    root=installed.ledger.root,
                    manifest=directory_manifest,
                    host_receipt=installed.host_receipt,
                )
            )
            assert_blocked(
                indirect.service.uninstall(indirect.uninstall_request), BlockReason.MANIFEST_MISMATCH
            )
            self.assertEqual(b"must-remain", helper.read_bytes())
            self.assertTrue(indirect.filesystem.has_owned_effects(indirect.request.installation_id))

    def test_c6_four_declared_one_shot_failures_are_contained(self) -> None:
        with TemporaryDirectory() as directory:
            stage = build_stack(Path(directory) / "stage")
            stage.filesystem.fail_next_stage()
            assert_install_blocked(
                stage.service.install(stage.request), BlockReason.FILESYSTEM_STAGE_FAILED
            )
            assert_clean_install_effects(stage)

            register = build_stack(Path(directory) / "register")
            register.host.fail_next_register()
            assert_install_blocked(
                register.service.install(register.request), BlockReason.HOST_REGISTER_FAILED
            )
            assert_clean_install_effects(register)

            save = build_stack(Path(directory) / "save")
            save.ledger.fail_next_save()
            assert_install_blocked(save.service.install(save.request), BlockReason.LEDGER_SAVE_FAILED)
            assert_clean_install_effects(save)

            remove = build_stack(Path(directory) / "remove")
            self.assertIsInstance(remove.service.install(remove.request), InstallSucceeded)
            remove.host.fail_next_remove()
            assert_blocked(
                remove.service.uninstall(remove.uninstall_request), BlockReason.HOST_REMOVE_FAILED
            )
            self.assertTrue(remove.filesystem.has_owned_effects(remove.request.installation_id))
            self.assertTrue(remove.host.has_registration(remove.request.installation_id))
            self.assertIsInstance(remove.ledger.read(), OwnedInstallLedger)

    def test_c7_temporary_git_repositories_remain_byte_identical(self) -> None:
        with TemporaryDirectory() as directory:
            sandbox = Path(directory)
            existing_repository = make_minimal_repository(sandbox / "existing", b"existing")
            empty_repository = make_minimal_repository(sandbox / "empty", b"")
            before_existing = snapshot_tree(existing_repository)
            before_empty = snapshot_tree(empty_repository)
            status_existing = porcelain_for_minimal_repository(existing_repository)
            status_empty = porcelain_for_minimal_repository(empty_repository)

            successful = build_stack(sandbox / "install")
            self.assertIsInstance(successful.service.install(successful.request), InstallSucceeded)
            blocked = build_stack(sandbox / "blocked")
            self.assertIsInstance(blocked.service.install(blocked.request), InstallSucceeded)
            blocked.host.fail_next_remove()
            self.assertIsInstance(blocked.service.uninstall(blocked.uninstall_request), UninstallBlocked)

            self.assertEqual(before_existing, snapshot_tree(existing_repository))
            self.assertEqual(before_empty, snapshot_tree(empty_repository))
            self.assertEqual(status_existing, porcelain_for_minimal_repository(existing_repository))
            self.assertEqual(status_empty, porcelain_for_minimal_repository(empty_repository))

    def test_c8_ticket_source_has_no_forbidden_capability(self) -> None:
        production = Path(__file__).parents[1] / "library" / "local_orchestration"
        files = (
            production / "__init__.py",
            production / "contracts.py",
            production / "ports.py",
            production / "installation.py",
            production / "fakes.py",
        )
        forbidden_exact = ("Any", "type: ignore")
        forbidden_folded = (
            "credential",
            "auth" + "token",
            "sub" + "process",
            "socket",
            "http://",
            "https://",
            "git checkout",
            "git reset",
            "git commit",
            "git push",
            "target_project",
            "target-project",
        )
        for source in files:
            text = source.read_text(encoding="utf-8")
            for fragment in forbidden_exact:
                self.assertNotIn(fragment, text, f"{source.name}: {fragment}")
            for fragment in forbidden_folded:
                self.assertNotIn(fragment, text.casefold(), f"{source.name}: {fragment}")


def build_stack(sandbox: Path) -> LifecycleStack:
    path = OwnedRelativePath(value="payload/plugin.txt")
    content = b"owned-payload"
    manifest = OwnedManifest(entries=(ManifestEntry(path=path, digest=digest_bytes(content)),))
    installation_id = InstallationId(value="install-001")
    filesystem = FakeOwnedFilesystem(sandbox=sandbox, payloads={path: content})
    ledger = FakeInstallLedger()
    host = FakeHostLifecycle()
    process = FakeProcessLifecycle()
    service = OwnedInstallLifecycle(filesystem, ledger, host, process)
    return LifecycleStack(
        service=service,
        request=InstallRequest(
            installation_id=installation_id,
            root=InstallRoot(value=CANONICAL_INSTALL_ROOT),
            manifest=manifest,
            host_id=HostId.LOCAL_FAKE,
        ),
        uninstall_request=UninstallRequest(
            installation_id=installation_id,
            root=InstallRoot(value=CANONICAL_INSTALL_ROOT),
        ),
        filesystem=filesystem,
        ledger=ledger,
        host=host,
        process=process,
    )


def total_effect_calls(stack: LifecycleStack) -> int:
    return (
        stack.filesystem.effect_calls
        + stack.ledger.effect_calls
        + stack.host.effect_calls
        + stack.process.effect_calls
    )


def assert_install_blocked(result: object, reason: BlockReason) -> None:
    if not isinstance(result, InstallBlocked):
        raise AssertionError(f"expected InstallBlocked, got {type(result).__name__}")
    if result.reason is not reason:
        raise AssertionError(f"expected {reason.value}, got {result.reason.value}")


def assert_blocked(result: object, reason: BlockReason) -> None:
    if not isinstance(result, UninstallBlocked):
        raise AssertionError(f"expected UninstallBlocked, got {type(result).__name__}")
    if result.reason is not reason:
        raise AssertionError(f"expected {reason.value}, got {result.reason.value}")


def assert_clean_install_effects(stack: LifecycleStack) -> None:
    if stack.filesystem.has_owned_effects(stack.request.installation_id):
        raise AssertionError("owned filesystem effect remained")
    if stack.host.has_registration(stack.request.installation_id):
        raise AssertionError("owned host effect remained")
    if not isinstance(stack.ledger.read(), LedgerAbsent):
        raise AssertionError("owned ledger remained")


def snapshot_tree(root: Path) -> tuple[tuple[str, bytes], ...]:
    if not root.exists():
        return ()
    return tuple(
        (path.relative_to(root).as_posix(), path.read_bytes())
        for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file())
    )


def make_minimal_repository(root: Path, worktree_content: bytes) -> Path:
    metadata = root / ".git"
    (metadata / "objects" / "info").mkdir(parents=True)
    (metadata / "objects" / "pack").mkdir(parents=True)
    (metadata / "refs" / "heads").mkdir(parents=True)
    (metadata / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (metadata / "config").write_text(
        "[core]\n\trepositoryformatversion = 0\n\tbare = false\n",
        encoding="utf-8",
    )
    if worktree_content:
        (root / "existing.txt").write_bytes(worktree_content)
    return root


def porcelain_for_minimal_repository(root: Path) -> tuple[str, ...]:
    return tuple(
        f"?? {path.relative_to(root).as_posix()}"
        for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file())
        if ".git" not in path.relative_to(root).parts
    )


if __name__ == "__main__":
    unittest.main()
