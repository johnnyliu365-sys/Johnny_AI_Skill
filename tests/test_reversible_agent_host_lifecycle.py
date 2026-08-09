"""Executable H1..H8 closure for the recorded host capability gate."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from pydantic import ValidationError

try:
    from library.local_orchestration import (
        CANONICAL_HOST_REGISTRATION_KEY,
        AgentHost,
        AgentHostReceipt,
        AgentHostRemovalProof,
        HostBlockReason,
        HostCapabilityBlocked,
        HostCapabilityRequest,
        HostCapabilitySupported,
        HostCapabilityUnverified,
        HostCommandResult,
        HostCommandStatus,
        HostEvidenceId,
        HostFailureCode,
        HostRegistrationKey,
        HostRemovalBlocked,
        HostRemovalRequest,
        HostRemovalSucceeded,
        InstallationId,
        RecordedHostLifecycle,
        ReversibleHostCapabilityGate,
    )
except ImportError as import_error:
    FEATURE_IMPORT_ERROR = str(import_error)
else:
    FEATURE_IMPORT_ERROR = ""


class ReversibleAgentHostLifecycleTests(unittest.TestCase):
    def test_h1_recorded_exact_lifecycle_is_supported_and_ends_absent(self) -> None:
        require_feature("H1 recorded exact lifecycle")
        request, fake, gate = build_stack()

        result = gate.verify_recorded(request)

        self.assertIsInstance(result, HostCapabilitySupported)
        if not isinstance(result, HostCapabilitySupported):
            raise AssertionError("H1 expected a supported recorded result")
        self.assertEqual(request.installation_id, result.receipt.installation_id)
        self.assertEqual(result.host, result.receipt.host)
        self.assertEqual(request.host, result.receipt.host)
        self.assertEqual(request.registration_key, result.receipt.registration_key)
        self.assertEqual(result.receipt.installation_id, result.removal_proof.installation_id)
        self.assertEqual(result.receipt.host, result.removal_proof.host)
        self.assertEqual(result.receipt.registration_key, result.removal_proof.registration_key)
        self.assertEqual(
            ("detect", "register", "verify", "receipt", "unregister", "verify_absent"),
            fake.call_order,
        )
        self.assertFalse(fake.has_registration)
        self.assertEqual(2, fake.mutation_count)

    def test_h2_codex_and_claude_remain_unverified_without_live_adapter(self) -> None:
        require_feature("H2 public hosts remain unverified")
        _, fake, gate = build_stack()

        for host in (AgentHost.CODEX, AgentHost.CLAUDE):
            with self.subTest(host=host.value):
                result = gate.public_capability(host)
                self.assertIsInstance(result, HostCapabilityUnverified)
                self.assertEqual(host, result.host)
                forged = build_stack()[0].model_copy(update={"host": host})
                self.assertIsInstance(gate.verify_recorded(forged), HostCapabilityBlocked)
        self.assertEqual((), fake.call_order)
        self.assertEqual(0, fake.mutation_count)

    def test_h3_only_exact_canonical_registration_key_reaches_effects(self) -> None:
        require_feature("H3 canonical registration key")
        request, fake, gate = build_stack()
        canonical = CANONICAL_HOST_REGISTRATION_KEY
        accepted = HostRegistrationKey(value=canonical)
        self.assertEqual(canonical, accepted.value)
        variants = (
            canonical + "-suffix",
            canonical + "/",
            canonical.swapcase(),
            canonical.replace("/", "%2F"),
            canonical + "/..",
            "",
        )

        for value in variants:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                gate.verify_recorded(
                    HostCapabilityRequest(
                        installation_id=request.installation_id,
                        host=request.host,
                        registration_key=HostRegistrationKey(value=value),
                    )
                )
        self.assertEqual((), fake.call_order)
        self.assertEqual(0, fake.mutation_count)

    def test_h4_required_nested_metadata_rejects_every_empty_shape(self) -> None:
        require_feature("H4 strict empty-shape boundary")
        request, _, _ = build_stack()
        value_shapes: tuple[object, ...] = (None, "", " ", [], {})

        for shape in value_shapes:
            with self.subTest(model="InstallationId", shape=shape), self.assertRaises(ValidationError):
                InstallationId.model_validate({"value": shape})
            with self.subTest(model="HostRegistrationKey", shape=shape), self.assertRaises(
                ValidationError
            ):
                HostRegistrationKey.model_validate({"value": shape})
        for shape in value_shapes:
            with self.subTest(model="HostEvidenceId", shape=shape), self.assertRaises(
                ValidationError
            ):
                HostEvidenceId.model_validate({"value": shape})
        for model in (InstallationId, HostRegistrationKey, HostEvidenceId):
            with self.subTest(model=model.__name__, shape="omitted"), self.assertRaises(
                ValidationError
            ):
                model.model_validate({})

        base = request.model_dump(mode="python")
        for shape in value_shapes:
            invalid_host = dict(base)
            invalid_host["host"] = shape
            with self.subTest(model="AgentHost", shape=shape), self.assertRaises(ValidationError):
                HostCapabilityRequest.model_validate(invalid_host)
        omitted_host = dict(base)
        omitted_host.pop("host")
        with self.assertRaises(ValidationError):
            HostCapabilityRequest.model_validate(omitted_host)

        invalid_models: tuple[type[HostCommandResult] | type[AgentHostRemovalProof], ...] = (
            HostCommandResult,
            AgentHostRemovalProof,
        )
        for result_model in invalid_models:
            for shape in (None, "", " ", [], {}):
                with self.subTest(model=result_model.__name__, shape=shape), self.assertRaises(
                    ValidationError
                ):
                    result_model.model_validate(shape)

    def test_h5_direct_and_full_removal_require_exact_receipt_identity(self) -> None:
        require_feature("H5 exact receipt ownership")
        request, fake, gate = build_stack()
        receipt = fake.seed_registration(request)
        initial_mutations = fake.mutation_count

        foreign_receipt = receipt.model_copy(
            update={"evidence_id": HostEvidenceId(value="evidence-ffffffffffffffff")}
        )
        foreign_result = gate.remove(
            HostRemovalRequest(
                installation_id=request.installation_id,
                host=request.host,
                registration_key=request.registration_key,
                receipt=foreign_receipt,
            )
        )
        self.assertIsInstance(foreign_result, HostRemovalBlocked)
        if not isinstance(foreign_result, HostRemovalBlocked):
            raise AssertionError("H5 expected foreign removal to block")
        self.assertEqual(HostBlockReason.FOREIGN_REGISTRATION, foreign_result.reason)
        self.assertTrue(fake.has_registration)
        self.assertEqual(initial_mutations, fake.mutation_count)

        with self.assertRaises(ValidationError):
            HostRemovalRequest(
                installation_id=InstallationId(value="installation-ffffffffffffffff"),
                host=request.host,
                registration_key=request.registration_key,
                receipt=receipt,
            )
        with self.assertRaises(ValidationError):
            HostRemovalRequest(
                installation_id=request.installation_id,
                host=AgentHost.CODEX,
                registration_key=request.registration_key,
                receipt=receipt,
            )
        self.assertTrue(fake.has_registration)
        self.assertEqual(initial_mutations, fake.mutation_count)

        exact_request = HostRemovalRequest.from_receipt(receipt)
        exact_result = gate.remove(exact_request)
        self.assertIsInstance(exact_result, HostRemovalSucceeded)
        self.assertFalse(fake.has_registration)
        after_remove = fake.mutation_count
        retry = gate.remove(exact_request)
        self.assertIsInstance(retry, HostRemovalBlocked)
        if not isinstance(retry, HostRemovalBlocked):
            raise AssertionError("H5 expected removal retry to block")
        self.assertEqual(HostBlockReason.REMOVAL_PROOF_FAILED, retry.reason)
        self.assertEqual(after_remove, fake.mutation_count)

        other_request, other_fake, other_gate = build_stack()
        other_fake.return_foreign_receipt = True
        result = other_gate.verify_recorded(other_request)
        self.assertIsInstance(result, HostCapabilityBlocked)
        if not isinstance(result, HostCapabilityBlocked):
            raise AssertionError("H5 expected foreign verification receipt to block")
        self.assertEqual(HostBlockReason.RECEIPT_MISMATCH, result.reason)
        self.assertTrue(other_fake.has_registration)

    def test_h6_five_recorded_failures_map_to_finite_block_reasons(self) -> None:
        require_feature("H6 finite recorded failures")
        cases = (
            (HostFailureCode.EXECUTABLE_UNAVAILABLE, HostBlockReason.EXECUTABLE_UNAVAILABLE),
            (HostFailureCode.ACCESS_DENIED, HostBlockReason.ACCESS_DENIED),
            (HostFailureCode.REGISTER_FAILED, HostBlockReason.REGISTER_FAILED),
            (HostFailureCode.VERIFY_FAILED, HostBlockReason.VERIFY_FAILED),
            (HostFailureCode.REMOVAL_PROOF_FAILED, HostBlockReason.REMOVAL_PROOF_FAILED),
        )

        for failure, reason in cases:
            with self.subTest(failure=failure.value):
                request, fake, gate = build_stack()
                fake.fail_on(failure)
                result = gate.verify_recorded(request)
                self.assertIsInstance(result, HostCapabilityBlocked)
                if not isinstance(result, HostCapabilityBlocked):
                    raise AssertionError("H6 expected recorded failure to block")
                self.assertEqual(reason, result.reason)
                self.assertNotIsInstance(result, HostCapabilitySupported)
                self.assertEqual("unrelated-effect", fake.unrelated_marker)

    def test_h7_only_opaque_metadata_crosses_reports_and_git_is_unchanged(self) -> None:
        require_feature("H7 privacy and repository isolation")
        sentinels = (
            "RAW-COMMAND-SENTINEL",
            "SOURCE-SENTINEL",
            "PATH-SENTINEL",
            "URI-SENTINEL",
            "SECRET-SENTINEL",
            "PII-SENTINEL",
        )
        request, fake, gate = build_stack()
        request_json = request.model_dump_json()
        for index, sentinel in enumerate(sentinels):
            injected = request_json[:-1] + f',"raw_{index}":"{sentinel}"' + "}"
            with self.assertRaises(ValidationError):
                HostCapabilityRequest.model_validate_json(injected)

        with TemporaryDirectory() as directory:
            root = Path(directory)
            existing = make_minimal_repository(root / "existing", b"existing")
            empty = make_minimal_repository(root / "empty", b"")
            existing_before = snapshot_tree(existing)
            empty_before = snapshot_tree(empty)
            existing_status = porcelain(existing)
            empty_status = porcelain(empty)

            supported = gate.verify_recorded(request)
            blocked_request, blocked_fake, blocked_gate = build_stack()
            blocked_fake.fail_on(HostFailureCode.EXECUTABLE_UNAVAILABLE)
            blocked = blocked_gate.verify_recorded(blocked_request)
            serialized = supported.model_dump_json() + blocked.model_dump_json()
            for sentinel in sentinels:
                self.assertNotIn(sentinel, serialized)
            self.assertEqual(existing_before, snapshot_tree(existing))
            self.assertEqual(empty_before, snapshot_tree(empty))
            self.assertEqual(existing_status, porcelain(existing))
            self.assertEqual(empty_status, porcelain(empty))
        self.assertFalse(fake.has_registration)

    def test_h8_production_source_has_no_forbidden_capability(self) -> None:
        require_feature("H8 forbidden-capability sentinel")
        root = Path(__file__).parents[1] / "library" / "local_orchestration"
        sources = (
            root / "__init__.py",
            root / "host_contracts.py",
            root / "host_lifecycle.py",
            root / "host_fakes.py",
        )
        exact = ("Any", "type: ignore")
        folded = (
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
            "cache write",
            "config write",
            "target_project",
            "target-project",
            "codex exec",
            "claude --",
        )
        for source in sources:
            text = source.read_text(encoding="utf-8")
            for fragment in exact:
                self.assertNotIn(fragment, text, f"{source.name}: {fragment}")
            for fragment in folded:
                self.assertNotIn(fragment, text.casefold(), f"{source.name}: {fragment}")


def require_feature(closure: str) -> None:
    if FEATURE_IMPORT_ERROR:
        raise AssertionError(f"{closure} not implemented: {FEATURE_IMPORT_ERROR}")


def build_stack() -> tuple[
    HostCapabilityRequest, RecordedHostLifecycle, ReversibleHostCapabilityGate
]:
    request = HostCapabilityRequest(
        installation_id=InstallationId(value="installation-0123456789abcdef"),
        host=AgentHost.RECORDED,
        registration_key=HostRegistrationKey(value=CANONICAL_HOST_REGISTRATION_KEY),
    )
    fake = RecordedHostLifecycle()
    return request, fake, ReversibleHostCapabilityGate(fake)


def snapshot_tree(root: Path) -> tuple[tuple[str, bytes], ...]:
    return tuple(
        (path.relative_to(root).as_posix(), path.read_bytes())
        for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file())
    )


def make_minimal_repository(root: Path, content: bytes) -> Path:
    metadata = root / ".git"
    (metadata / "objects" / "info").mkdir(parents=True)
    (metadata / "objects" / "pack").mkdir(parents=True)
    (metadata / "refs" / "heads").mkdir(parents=True)
    (metadata / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (metadata / "config").write_text(
        "[core]\n\trepositoryformatversion = 0\n\tbare = false\n", encoding="utf-8"
    )
    if content:
        (root / "existing.txt").write_bytes(content)
    return root


def porcelain(root: Path) -> tuple[str, ...]:
    return tuple(
        f"?? {path.relative_to(root).as_posix()}"
        for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file())
        if ".git" not in path.relative_to(root).parts
    )


if __name__ == "__main__":
    unittest.main()
