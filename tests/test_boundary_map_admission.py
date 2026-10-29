from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pytest

from library.local_orchestration.boundary_map import (
    BoundaryChange,
    ChangeKind,
    EvaluationStatus,
    TicketModuleSelection,
    evaluate_module_changes,
    map_digest,
    parse_boundary_map,
)
from library.local_orchestration.boundary_map_admission import (
    BoundaryAdmissionFailure,
    BoundaryAdmissionRequest,
    BoundaryAdmissionResult,
    BoundaryAdmissionStatus,
    admit_module_boundary,
)
from library.local_orchestration.boundary_map_python import observe_python_dependencies
from library.local_orchestration.document_mutation_gate import (
    DocumentMutationFailure,
    DocumentMutationResult,
    DocumentMutationStatus,
    admit_document_mutation,
    normalize_change_path,
    path_matches_entry,
)
from shared.git_fixture import (
    _commit,
    _layout,
    _request as _git_request,
    _run,
    _seed_mapped,
    _write,
)

_BASELINE = "a" * 40
_TICKET_PATH = "modules/tickets/38b.md"
_DEMO_TICKET_PATH = "modules/tickets/demo.md"
_MODULE_MAP_PATH = "shared/BOUNDARY_MAP.toml"


def _map_bytes() -> bytes:
    return (
        "schema_revision = 1\n"
        'scope = "LOCAL_SOURCE_BOUNDARY"\n'
        f'baseline = "{_BASELINE}"\n\n'
        '[[modules]]\nid = "feature"\nroots = ["src/feature.py"]\n'
        'owner = "feature-team"\nresponsibility = "Own the feature entry point."\n'
        'kind = "LIBRARY"\nallowed_dependencies = ["shared"]\n\n'
        '[[modules]]\nid = "shared"\nroots = ["src/shared.py"]\n'
        'owner = "platform-team"\nresponsibility = "Provide shared feature contracts."\n'
        'kind = "SHARED"\nallowed_dependencies = []\n'
    ).encode("utf-8")


def _ticket(map_bytes: bytes, *, selected: tuple[str, ...] = ("feature",)) -> bytes:
    selected_text = ", ".join(f'"{module_id}"' for module_id in selected)
    return (
        "```johnny-module-boundary\n"
        "schema_revision = 1\n"
        f'map_sha256 = "{map_digest(map_bytes)}"\n'
        f'baseline = "{_BASELINE}"\n'
        f"selected_modules = [{selected_text}]\n"
        "```\n"
    ).encode("utf-8")


def _request(
    ticket: bytes,
    changes: tuple[BoundaryChange, ...] = (
        BoundaryChange("src/feature.py", ChangeKind.MODIFY, "100644"),
    ),
) -> BoundaryAdmissionRequest:
    return BoundaryAdmissionRequest(
        integration_ref="main",
        candidate_ref="candidate",
        merge_base=_BASELINE,
        ticket_path=_TICKET_PATH,
        integration_ticket=ticket,
        changes=changes,
    )


def _run_admission(
    request: BoundaryAdmissionRequest,
    blobs: dict[tuple[str, str], bytes],
    *,
    ancestor: Callable[[str, str], bool] | None = None,
) -> tuple[
    BoundaryAdmissionResult,
    list[tuple[str, str]],
    list[tuple[str, str]],
]:
    reads: list[tuple[str, str]] = []
    ancestry: list[tuple[str, str]] = []

    def read_blob(reference: str, path: str) -> bytes | None:
        reads.append((reference, path))
        return blobs.get((reference, path))

    def is_ancestor(base: str, reference: str) -> bool:
        ancestry.append((base, reference))
        return ancestor(base, reference) if ancestor is not None else base == _BASELINE

    result = admit_module_boundary(
        request,
        read_blob=read_blob,
        is_ancestor=is_ancestor,
        normalize_path=normalize_change_path,
        path_matches=path_matches_entry,
    )
    return result, reads, ancestry


def test_admission_reads_trusted_map_and_candidate_blobs_through_gate_callbacks() -> None:
    boundary_map = _map_bytes()
    ticket = _ticket(boundary_map)
    request = _request(ticket)
    result, reads, ancestry = _run_admission(
        request,
        {
            ("main", "shared/BOUNDARY_MAP.toml"): boundary_map,
            ("candidate", "src/feature.py"): b"from src.shared import VALUE\n",
        },
    )

    assert result.status is BoundaryAdmissionStatus.VERIFIED
    assert reads == [
        ("main", "shared/BOUNDARY_MAP.toml"),
        ("candidate", "src/feature.py"),
    ]
    assert ancestry == [(_BASELINE, "main"), (_BASELINE, _BASELINE)]


def test_repository_map_covers_the_implemented_admission_source_graph() -> None:
    repository = Path(__file__).resolve().parents[1]
    map_bytes = (repository / "shared/BOUNDARY_MAP.toml").read_bytes()
    parsed = parse_boundary_map(map_bytes, normalize_change_path, path_matches_entry)
    assert parsed.status.value == "VALID", parsed.detail
    assert parsed.boundary_map is not None
    boundary_map = parsed.boundary_map
    changed_paths = (
        "library/local_orchestration/boundary_map.py",
        "library/local_orchestration/boundary_map_python.py",
        "library/local_orchestration/boundary_map_admission.py",
        "library/local_orchestration/document_mutation_gate.py",
        "shared/__init__.py",
        "shared/git_fixture.py",
        "tests/test_boundary_map.py",
        "tests/test_boundary_map_admission.py",
        "tests/test_document_mutation_gate.py",
    )
    created_paths = {"shared/__init__.py", "shared/git_fixture.py"}
    changes = tuple(
        BoundaryChange(
            path,
            ChangeKind.CREATE if path in created_paths else ChangeKind.MODIFY,
            "100644",
        )
        for path in changed_paths
    )
    observations = {
        path: observe_python_dependencies(path, (repository / path).read_bytes())
        for path in changed_paths
    }
    selection = TicketModuleSelection(
        map_sha256=map_digest(map_bytes),
        baseline=boundary_map.baseline,
        selected_modules=tuple(module.module_id for module in boundary_map.modules),
    )

    result = evaluate_module_changes(
        boundary_map,
        selection,
        changes,
        observations,
        normalize_change_path,
        path_matches_entry,
    )

    assert result.status is EvaluationStatus.VERIFIED, result


def test_unpinned_legacy_ticket_does_not_read_map_or_candidate() -> None:
    request = _request(b"# no module boundary pin\n")
    result, reads, ancestry = _run_admission(request, {})

    assert result.status is BoundaryAdmissionStatus.UNDECLARED
    assert reads == []
    assert ancestry == []


def test_candidate_map_replacement_is_refused_before_candidate_reads() -> None:
    boundary_map = _map_bytes()
    request = _request(
        _ticket(boundary_map),
        changes=(BoundaryChange("shared/BOUNDARY_MAP.toml", ChangeKind.MODIFY, "100644"),),
    )
    result, reads, ancestry = _run_admission(
        request, {("main", "shared/BOUNDARY_MAP.toml"): boundary_map}
    )

    assert result.status is BoundaryAdmissionStatus.REFUSED
    assert result.failure is BoundaryAdmissionFailure.VIOLATION
    assert reads == [("main", "shared/BOUNDARY_MAP.toml")]
    assert ancestry == [(_BASELINE, "main"), (_BASELINE, _BASELINE)]


def test_candidate_ticket_pin_rewrite_is_refused_before_source_observation() -> None:
    boundary_map = _map_bytes()
    ticket = _ticket(boundary_map)
    request = _request(
        ticket,
        changes=(
            BoundaryChange(_TICKET_PATH, ChangeKind.MODIFY, "100644"),
            BoundaryChange("src/feature.py", ChangeKind.MODIFY, "100644"),
        ),
    )
    result, reads, _ = _run_admission(
        request,
        {
            ("main", "shared/BOUNDARY_MAP.toml"): boundary_map,
            ("candidate", _TICKET_PATH): _ticket(boundary_map, selected=("feature", "shared")),
        },
    )

    assert result.status is BoundaryAdmissionStatus.REFUSED
    assert result.failure is BoundaryAdmissionFailure.MISMATCH
    assert reads == [
        ("main", "shared/BOUNDARY_MAP.toml"),
        ("candidate", _TICKET_PATH),
    ]


@pytest.mark.parametrize(
    "failure",
    ("missing-map", "bad-ancestry", "unreadable-source"),
)
def test_unverified_admission_inputs_fail_closed(failure: str) -> None:
    boundary_map = _map_bytes()
    request = _request(_ticket(boundary_map))
    blobs: dict[tuple[str, str], bytes] = {}
    ancestor: Callable[[str, str], bool] | None = None
    if failure != "missing-map":
        blobs[("main", "shared/BOUNDARY_MAP.toml")] = boundary_map
    if failure == "bad-ancestry":
        def reject_merge_base(base: str, reference: str) -> bool:
            return reference == "main"

        ancestor = reject_merge_base
    if failure == "unreadable-source":
        def accept_ancestry(base: str, reference: str) -> bool:
            return True

        ancestor = accept_ancestry

    result, _, _ = _run_admission(request, blobs, ancestor=ancestor)

    if failure == "bad-ancestry":
        assert result.status is BoundaryAdmissionStatus.REFUSED
        assert result.failure is BoundaryAdmissionFailure.MISMATCH
    else:
        assert result.status is BoundaryAdmissionStatus.NOT_VERIFIED
        assert result.failure is BoundaryAdmissionFailure.NOT_VERIFIED


class RealGitAdmissionTests(unittest.TestCase):
    def test_opt_in_map_allows_a_selected_python_change_through_real_merge(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed_mapped(base)
            before = _run(root, "rev-parse", "HEAD")
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(root, "src/feature.py", "import src.shared\nVALUE = 2\n")
            candidate = _commit(root, "edit selected module with an allowed import")
            _run(root, "checkout", "-q", "main")

            result = admit_document_mutation(_layout(base), _git_request(root))

            self.assertIs(result.status, DocumentMutationStatus.INTEGRATED)
            self.assertEqual(result.integrated_commit, candidate)
            self.assertNotEqual(_run(root, "rev-parse", "HEAD"), before)

    def _mapped_refused(
        self,
        base: Path,
        mutate: Callable[[Path], None],
        *,
        selected_modules: tuple[str, ...] = ("feature",),
    ) -> tuple[Path, str, DocumentMutationResult]:
        root = _seed_mapped(base, selected_modules=selected_modules)
        before = _run(root, "rev-parse", "HEAD")
        _run(root, "checkout", "-q", "-b", "candidate")
        mutate(root)
        _commit(root, "module-map candidate")
        _run(root, "checkout", "-q", "main")
        result = admit_document_mutation(_layout(base), _git_request(root))
        return root, before, result

    def test_a_ticket_map_digest_mismatch_refuses_without_moving_main(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed_mapped(base, pin_digest="0" * 64)
            before = _run(root, "rev-parse", "HEAD")
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(root, "src/feature.py", "VALUE = 2\n")
            _commit(root, "candidate with a stale map pin")
            _run(root, "checkout", "-q", "main")

            result = admit_document_mutation(_layout(base), _git_request(root))

            self.assertIs(result.failure, DocumentMutationFailure.MODULE_BOUNDARY_MISMATCH)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_ticket_baseline_mismatch_refuses_without_moving_main(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed_mapped(base, pin_baseline="b" * 40)
            before = _run(root, "rev-parse", "HEAD")
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(root, "src/feature.py", "VALUE = 2\n")
            _commit(root, "candidate with a stale baseline pin")
            _run(root, "checkout", "-q", "main")

            result = admit_document_mutation(_layout(base), _git_request(root))

            self.assertIs(result.failure, DocumentMutationFailure.MODULE_BOUNDARY_MISMATCH)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_well_formed_but_unreachable_baseline_never_merges(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed_mapped(base, map_baseline="f" * 40)
            before = _run(root, "rev-parse", "HEAD")
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(root, "src/feature.py", "VALUE = 2\n")
            _commit(root, "candidate pinned to an unreachable baseline")
            _run(root, "checkout", "-q", "main")

            result = admit_document_mutation(_layout(base), _git_request(root))

            self.assertIs(result.failure, DocumentMutationFailure.MODULE_BOUNDARY_MISMATCH)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_opt_in_pin_without_an_integration_map_is_not_verified(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed_mapped(base, include_map=False)
            before = _run(root, "rev-parse", "HEAD")
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(root, "src/feature.py", "VALUE = 2\n")
            _commit(root, "candidate while pinned map is absent")
            _run(root, "checkout", "-q", "main")

            result = admit_document_mutation(_layout(base), _git_request(root))

            self.assertIs(result.failure, DocumentMutationFailure.MODULE_BOUNDARY_NOT_VERIFIED)
            self.assertIn("NOT_VERIFIED", result.detail or "")
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_candidate_cannot_replace_the_map_that_judges_its_changes(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)

            def mutate(root: Path) -> None:
                with (root / _MODULE_MAP_PATH).open("a", encoding="utf-8") as handle:
                    handle.write("# candidate attempted map rewrite\n")
                _write(root, "src/feature.py", "VALUE = 2\n")

            root, before, result = self._mapped_refused(base, mutate)
            self.assertIs(result.failure, DocumentMutationFailure.MODULE_BOUNDARY_VIOLATION)
            self.assertEqual(result.offending_path, _MODULE_MAP_PATH)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_candidate_cannot_rewrite_its_integration_pinned_module_selection(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)

            def mutate(root: Path) -> None:
                ticket_path = root / _DEMO_TICKET_PATH
                ticket_path.write_text(
                    ticket_path.read_text(encoding="utf-8").replace(
                        'selected_modules = ["feature"]',
                        'selected_modules = ["feature", "shared"]',
                    ),
                    encoding="utf-8",
                )
                _write(root, "src/feature.py", "VALUE = 2\n")

            root, before, result = self._mapped_refused(base, mutate)
            self.assertIs(result.failure, DocumentMutationFailure.MODULE_BOUNDARY_MISMATCH)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_unselected_or_unowned_source_never_reaches_main(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)

            def mutate(root: Path) -> None:
                _write(root, "src/shared.py", "VALUE = 2\n")

            root, before, result = self._mapped_refused(base, mutate)
            self.assertIs(result.failure, DocumentMutationFailure.MODULE_BOUNDARY_VIOLATION)
            self.assertEqual(result.offending_path, "src/shared.py")
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

        with TemporaryDirectory() as name:
            base = Path(name)

            def mutate_unowned(root: Path) -> None:
                _write(root, "src/unowned.py", "VALUE = 3\n")

            root, before, result = self._mapped_refused(base, mutate_unowned)
            self.assertIs(result.failure, DocumentMutationFailure.MODULE_BOUNDARY_VIOLATION)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_product_import_of_a_test_module_refuses_without_moving_main(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)

            def mutate(root: Path) -> None:
                _write(root, "src/feature.py", "import tests.test_feature\n")

            root, before, result = self._mapped_refused(base, mutate)
            self.assertIs(result.failure, DocumentMutationFailure.MODULE_BOUNDARY_VIOLATION)
            self.assertIn("TEST", result.detail or "")
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_unresolved_python_import_forms_refuse_without_moving_main(self) -> None:
        sources = (
            ("relative escape", b"from ..peer import Thing\n"),
            ("mixed from-list", b"from src import shared, unowned\n"),
            (
                "builtins loader alias",
                b"from builtins import __import__ as load_module\nload_module('src.shared')\n",
            ),
            (
                "importlib loader walrus",
                b"import importlib as il\n(loader := il.import_module)('src.shared')\n",
            ),
            (
                "importlib loader getattr alias",
                b"import importlib as il\nloader = getattr(il, 'import_module')\nloader('src.shared')\n",
            ),
        )
        for label, source in sources:
            with self.subTest(label=label), TemporaryDirectory() as name:
                base = Path(name)

                def mutate(root: Path) -> None:
                    _write(root, "src/feature.py", source.decode("utf-8"))

                root, before, result = self._mapped_refused(base, mutate)
                self.assertIs(
                    result.failure,
                    DocumentMutationFailure.MODULE_BOUNDARY_NOT_VERIFIED,
                )
                self.assertIn("NOT_VERIFIED", result.detail or "")
                self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_from_mapped_module_importing_a_symbol_reaches_main(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed_mapped(base)
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(root, "src/feature.py", "from src.shared import VALUE\nVALUE = 2\n")
            candidate = _commit(root, "import a symbol from the mapped module")
            _run(root, "checkout", "-q", "main")

            result = admit_document_mutation(_layout(base), _git_request(root))

            self.assertIs(result.status, DocumentMutationStatus.INTEGRATED)
            self.assertEqual(result.integrated_commit, candidate)

    def test_unsupported_changed_script_is_not_verified_and_does_not_merge(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)

            def mutate(root: Path) -> None:
                _write(root, "scripts/run.ps1", "Write-Output 'changed'\n")

            root, before, result = self._mapped_refused(
                base, mutate, selected_modules=("shell_entry",)
            )
            self.assertIs(result.failure, DocumentMutationFailure.MODULE_BOUNDARY_NOT_VERIFIED)
            self.assertIn("NOT_VERIFIED", result.detail or "")
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)
