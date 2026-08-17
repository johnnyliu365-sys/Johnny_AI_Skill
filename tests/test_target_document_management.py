"""Target-owned document planning and transactional write tests."""

from __future__ import annotations

from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from library.local_orchestration.target_document_management import (
    TargetWorkspace,
    TransactionalTargetDocumentWriter,
    build_handoff_tree_bootstrap_plan,
    detach_target_documents,
)
from library.workflow_router.role_supervision_contracts import (
    HandoffLeafBody,
    ImplementationTerminalKind,
    ObservedControlPlaneState,
    seal_handoff_leaf,
)
from library.workflow_router.target_document_contracts import (
    ArtifactDocumentKind,
    DocumentMutationMode,
    DocumentWriteStatus,
    HandoffTreeBootstrapRequest,
    TargetDocumentMutation,
    TargetDocumentPlan,
    derive_document_digest,
)


def _run_git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


def _repository(root: Path) -> str:
    _run_git(root, "init", "-b", "main")
    _run_git(root, "config", "user.email", "document-test@example.invalid")
    _run_git(root, "config", "user.name", "Document Test")
    (root / "README.md").write_text("# Vita test project\n", encoding="utf-8")
    (root / "product.txt").write_text("product-unchanged\n", encoding="utf-8")
    _run_git(root, "add", "--all")
    _run_git(root, "commit", "-m", "baseline")
    return _run_git(root, "rev-parse", "HEAD")


def _mutation(
    path: str,
    content: str,
    *,
    kind: ArtifactDocumentKind,
    mode: DocumentMutationMode = DocumentMutationMode.CREATE,
    expected: str | None = None,
    sealed: bool = False,
) -> TargetDocumentMutation:
    return TargetDocumentMutation(
        path=path,
        artifact_kind=kind,
        mode=mode,
        expected_current_digest=expected,
        content=content,
        content_digest=derive_document_digest(content),
        sealed=sealed,
    )


class TargetDocumentTransactionTests(unittest.TestCase):
    def test_requirement_grill_spec_ticket_and_handoff_create_without_product_change(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            baseline = _repository(root)
            product_before = (root / "product.txt").read_bytes()
            plan = TargetDocumentPlan(
                project_id="prj_0123456789abcdef",
                baseline_commit=baseline,
                mutations=(
                    _mutation(
                        "doc/requirements/active/2026/vita/REQ-20260817-001.md",
                        "# Requirement\nCreate a simulated dispatch rule.\n",
                        kind=ArtifactDocumentKind.REQUIREMENT,
                    ),
                    _mutation(
                        "doc/context/vita-simulation/grill.md",
                        "# Grill\nAll decisions confirmed for simulation.\n",
                        kind=ArtifactDocumentKind.GRILL_CONTEXT,
                    ),
                    _mutation(
                        "modules/spec/vita-simulation.md",
                        "# SPEC\nOne observable simulation behavior.\n",
                        kind=ArtifactDocumentKind.SPECIFICATION,
                    ),
                    _mutation(
                        "modules/tickets/vita-simulation/TICKET-001.md",
                        "# Ticket\nImplement the approved simulation behavior.\n",
                        kind=ArtifactDocumentKind.TICKET,
                    ),
                ),
            )
            result = TransactionalTargetDocumentWriter(TargetWorkspace(root)).apply(plan)
            self.assertEqual(DocumentWriteStatus.APPLIED, result.status)
            self.assertEqual(4, len(result.written_paths))
            self.assertEqual(product_before, (root / "product.txt").read_bytes())

    def test_update_requires_exact_digest_and_wrong_digest_writes_nothing(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            baseline = _repository(root)
            target = root / "PRD.md"
            target.write_text("# PRD\nOld requirement.\n", encoding="utf-8")
            _run_git(root, "add", "PRD.md")
            _run_git(root, "commit", "-m", "add prd")
            baseline = _run_git(root, "rev-parse", "HEAD")
            before = target.read_bytes()
            plan = TargetDocumentPlan(
                project_id="prj_0123456789abcdef",
                baseline_commit=baseline,
                mutations=(
                    _mutation(
                        "PRD.md",
                        "# PRD\nChanged requirement.\n",
                        kind=ArtifactDocumentKind.REQUIREMENT,
                        mode=DocumentMutationMode.UPDATE,
                        expected="sha256_" + ("0" * 64),
                    ),
                ),
            )
            result = TransactionalTargetDocumentWriter(TargetWorkspace(root)).apply(plan)
            self.assertEqual(DocumentWriteStatus.REJECTED, result.status)
            self.assertEqual(before, target.read_bytes())

            correct = TargetDocumentPlan(
                project_id=plan.project_id,
                baseline_commit=baseline,
                mutations=(
                    _mutation(
                        "PRD.md",
                        "# PRD\nChanged requirement.\n",
                        kind=ArtifactDocumentKind.REQUIREMENT,
                        mode=DocumentMutationMode.UPDATE,
                        expected=derive_document_digest(before.decode("utf-8")),
                    ),
                ),
            )
            applied = TransactionalTargetDocumentWriter(TargetWorkspace(root)).apply(correct)
            self.assertEqual(DocumentWriteStatus.APPLIED, applied.status)
            self.assertIn("Changed requirement", target.read_text(encoding="utf-8"))

    def test_sealed_leaf_cannot_be_updated_and_failed_replace_rolls_back(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            baseline = _repository(root)
            first = root / "CONTEXT.md"
            second = root / "PRD.md"
            first.write_text("context-before\n", encoding="utf-8")
            second.write_text("prd-before\n", encoding="utf-8")
            _run_git(root, "add", "CONTEXT.md", "PRD.md")
            _run_git(root, "commit", "-m", "add documents")
            baseline = _run_git(root, "rev-parse", "HEAD")
            first_before = first.read_bytes()
            second_before = second.read_bytes()
            plan = TargetDocumentPlan(
                project_id="prj_0123456789abcdef",
                baseline_commit=baseline,
                mutations=(
                    _mutation(
                        "CONTEXT.md",
                        "context-after\n",
                        kind=ArtifactDocumentKind.CONTEXT,
                        mode=DocumentMutationMode.UPDATE,
                        expected=derive_document_digest(first_before.decode("utf-8")),
                    ),
                    _mutation(
                        "PRD.md",
                        "prd-after\n",
                        kind=ArtifactDocumentKind.REQUIREMENT,
                        mode=DocumentMutationMode.UPDATE,
                        expected=derive_document_digest(second_before.decode("utf-8")),
                    ),
                ),
            )
            from library.local_orchestration import target_document_management as module

            real_replace = module.os.replace
            calls = 0

            def fail_second(source: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected replace failure")
                real_replace(source, destination)

            with patch.object(module.os, "replace", side_effect=fail_second):
                result = TransactionalTargetDocumentWriter(TargetWorkspace(root)).apply(plan)
            self.assertEqual(DocumentWriteStatus.STORAGE_UNAVAILABLE, result.status)
            self.assertEqual(first_before, first.read_bytes())
            self.assertEqual(second_before, second.read_bytes())

            with self.assertRaises(ValueError):
                _mutation(
                    "doc/handoffs/2026/vita/ticket/handoff.json",
                    "changed\n",
                    kind=ArtifactDocumentKind.HANDOFF_LEAF,
                    mode=DocumentMutationMode.UPDATE,
                    expected=derive_document_digest("prior\n"),
                    sealed=True,
                )


class HandoffBootstrapTests(unittest.TestCase):
    def test_bootstrap_plan_is_target_owned_plugin_neutral_and_complete(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            baseline = _repository(root)
            root_readme = (root / "README.md").read_text(encoding="utf-8")
            leaf = seal_handoff_leaf(
                HandoffLeafBody(
                    handoff_id="handoff-vita-feature-001",
                    schema_revision="handoff-schema-v1",
                    project_id="prj_0123456789abcdef",
                    spec_ref="spec-vita-feature",
                    spec_revision="rev-1111111111111111",
                    ticket_ref="ticket-vita-feature-001",
                    ticket_revision="rev-2222222222222222",
                    router_receipt_ref="receipt-vita-feature-001",
                    source_role_ref="role-implementation-owner",
                    source_task_ref="task-vita-implementation",
                    target_role_ref="role-supervisor-reviewer",
                    target_task_ref="task-vita-reviewer",
                    worktree_ref="worktree-vitafeature-01",
                    branch_ref="branch-vitafeature-01",
                    baseline_commit="1" * 40,
                    result_commit="2" * 40,
                    terminal_kind=ImplementationTerminalKind.COMPLETED,
                    previous_handoff_ref=None,
                    supersedes_ref=None,
                    evidence_refs=("evidence-tests-green",),
                    correlation_id="correlation-vita-feature-001",
                )
            )
            plan = build_handoff_tree_bootstrap_plan(
                HandoffTreeBootstrapRequest(
                    project_id=leaf.project_id,
                    baseline_commit=baseline,
                    year=2026,
                    feature_slug="vita-feature",
                    ticket_slug="ticket-vita-feature-001",
                    leaf=leaf,
                    root_readme_content=root_readme,
                    root_readme_digest=derive_document_digest(root_readme),
                    spec_path="modules/spec/vita-simulation.md",
                    protocol_id="protocol-receipt-bound-handoff",
                    schema_revision="handoff-manifest-v1",
                    compatibility_revision="compatibility-v1",
                    minimum_adoption_capabilities=(
                        "capability-git-ref-event",
                        "capability-role-wake",
                    ),
                    control_plane_state=ObservedControlPlaneState.ATTACHED,
                )
            )
            paths = {mutation.path for mutation in plan.mutations}
            self.assertIn("README.md", paths)
            self.assertIn("doc/handoffs/index.json", paths)
            self.assertIn(
                "doc/handoffs/2026/vita-feature/ticket-vita-feature-001/"
                "handoff-vita-feature-001.json",
                paths,
            )
            self.assertEqual(10, len(paths))
            serialized = plan.model_dump_json()
            self.assertNotIn(".codex", serialized.casefold())
            self.assertNotIn("plugin", serialized.casefold())
            result = TransactionalTargetDocumentWriter(TargetWorkspace(root)).apply(plan)
            self.assertEqual(DocumentWriteStatus.APPLIED, result.status)
            rendered_readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("No heartbeat", rendered_readme)
            self.assertIn("Deployment remains separate", rendered_readme)
            self.assertIn("successor", rendered_readme.casefold())

    def test_detach_plan_never_writes_or_removes_target_documents(self) -> None:
        self.assertEqual((), detach_target_documents())


if __name__ == "__main__":
    unittest.main()
