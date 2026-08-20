"""08: a change that touches what its ticket never declared does not reach main.

The integration tests here run against a real repository on purpose. The claim
this ticket makes is not "the function returns REFUSED" — it is "`main` is at
the same commit afterwards", and only a real `main` can answer that. A fake
would let the refusal be green while the merge happened anyway, which is
family C6 of the pitfall register: the mechanism passes, the real artifact
still breaks.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import ValidationError

from library.local_orchestration import document_mutation_gate as gate
from library.local_orchestration.dispatch_authority import (
    DispatchAdmissionFailure,
    DispatchAdmissionStatus,
    admit_dispatch,
    create_dispatch_grant,
)
from library.local_orchestration.document_mutation_gate import (
    BoundaryReadStatus,
    ChangeKind,
    DocumentBoundary,
    DocumentChange,
    DocumentMutationFailure,
    DocumentMutationRequest,
    DocumentMutationStatus,
    admit_document_mutation,
    evaluate_change,
    evaluate_changes,
    journal_path,
    normalize_change_path,
    parse_boundary_block,
    parse_raw_diff,
    read_boundary,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout

_TICKET = "modules/tickets/demo.md"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _ticket_text(
    *,
    modify: tuple[str, ...] = ("doc/",),
    create: tuple[str, ...] = (),
    delete: tuple[str, ...] = (),
    forbid: tuple[str, ...] = (),
    block: bool = True,
) -> str:
    lines = ["# 08 示範工單", "", "| 欄位 | 內容 |", "| 責任邊界 | 給人看的摘要 |", ""]
    if block:
        lines.append("```johnny-boundary")
        for key, entries in (
            ("modify", modify),
            ("create", create),
            ("delete", delete),
            ("forbid", forbid),
        ):
            lines.extend(f"{key} = {entry}" for entry in entries)
        lines.append("```")
    lines.append("")
    return "\n".join(lines)


def _boundary(
    *,
    modify: tuple[str, ...] = ("doc/",),
    create: tuple[str, ...] = (),
    delete: tuple[str, ...] = (),
    forbid: tuple[str, ...] = (),
) -> DocumentBoundary:
    return DocumentBoundary(
        modify=modify, create=create, delete=delete, forbid=forbid
    )


def _run(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments), capture_output=True, shell=False
    )
    if completed.returncode != 0:
        raise AssertionError(
            "git " + " ".join(arguments) + " failed: "
            + completed.stderr.decode("utf-8", errors="replace")
        )
    return completed.stdout.decode("utf-8", errors="replace").strip()


def _repository(base: Path) -> Path:
    root = (base / "repo").resolve()
    root.mkdir()
    subprocess.run(
        ("git", "init", "-q", "-b", "main", str(root)),
        check=True,
        capture_output=True,
    )
    for name, value in (
        ("user.name", "Gate Test"),
        ("user.email", "gate@example.com"),
        ("commit.gpgsign", "false"),
        ("core.autocrlf", "false"),
    ):
        _run(root, "config", name, value)
    return root


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _commit(root: Path, message: str) -> str:
    _run(root, "add", "-A")
    _run(root, "commit", "-q", "-m", message)
    return _run(root, "rev-parse", "HEAD")


def _layout(base: Path) -> JohnnyRootLayout:
    layout = JohnnyRootLayout(base=(base / "johnny").resolve())
    layout.queue_root.mkdir(parents=True, exist_ok=True)
    return layout


def _seed(base: Path, ticket: str) -> Path:
    """A repository whose `main` already holds the ticket and two real files."""

    root = _repository(base)
    _write(root, _TICKET, ticket)
    _write(root, "doc/existing.md", "before\n")
    _write(root, "library/untouchable.py", "keep\n")
    _commit(root, "baseline")
    return root


def _request(root: Path, *, ticket_path: str = _TICKET) -> DocumentMutationRequest:
    return DocumentMutationRequest(
        repository_root=str(root),
        ticket_path=ticket_path,
        integration_branch="main",
        candidate_ref="candidate",
    )


# ---------------------------------------------------------------------------
# The declaration block: absent, broken and declared are three answers
# ---------------------------------------------------------------------------


class BoundaryDeclarationTests(unittest.TestCase):
    def test_a_ticket_with_no_block_is_undeclared_rather_than_unbounded(self) -> None:
        status, boundary, _ = read_boundary("# 一張沒有宣告區塊的票\n")
        self.assertIs(status, BoundaryReadStatus.UNDECLARED)
        self.assertIsNone(boundary)

    def test_a_declared_block_reads_all_four_lists(self) -> None:
        status, boundary, _ = read_boundary(
            _ticket_text(
                modify=("doc/", "README.md"),
                create=("doc/new/",),
                delete=("doc/old.md",),
                forbid=("AGENTS.md",),
            )
        )
        self.assertIs(status, BoundaryReadStatus.DECLARED)
        assert boundary is not None
        self.assertEqual(boundary.modify, ("doc/", "README.md"))
        self.assertEqual(boundary.create, ("doc/new/",))
        self.assertEqual(boundary.delete, ("doc/old.md",))
        self.assertEqual(boundary.forbid, ("AGENTS.md",))

    def test_an_unknown_key_refuses_instead_of_dropping_the_line(self) -> None:
        # Dropping a mistyped `forbid` line would turn a prohibition into
        # permission, silently.
        status, _, reason = read_boundary("```johnny-boundary\nforbidden = AGENTS.md\n```")
        self.assertIs(status, BoundaryReadStatus.UNPARSABLE)
        assert reason is not None
        self.assertIn("forbidden", reason)

    def test_a_block_that_declares_no_modify_entry_is_unparsable(self) -> None:
        status, boundary, _ = read_boundary(
            "```johnny-boundary\nforbid = AGENTS.md\n```"
        )
        self.assertIs(status, BoundaryReadStatus.UNPARSABLE)
        self.assertIsNone(boundary)

    def test_delete_refuses_a_wildcard(self) -> None:
        with self.assertRaises(ValueError) as raised:
            parse_boundary_block("modify = doc/\ndelete = doc/*.md\n")
        self.assertIn("delete", str(raised.exception))

    def test_delete_refuses_a_directory_prefix(self) -> None:
        with self.assertRaises(ValueError):
            parse_boundary_block("modify = doc/\ndelete = doc/\n")

    def test_a_line_without_an_equals_sign_refuses(self) -> None:
        with self.assertRaises(ValueError):
            parse_boundary_block("modify = doc/\njust some prose\n")

    def test_an_empty_value_refuses(self) -> None:
        with self.assertRaises(ValueError):
            parse_boundary_block("modify = doc/\ncreate =\n")

    def test_a_repeated_entry_refuses(self) -> None:
        with self.assertRaises(ValueError):
            parse_boundary_block("modify = doc/\nmodify = doc/\n")

    def test_comments_and_blank_lines_are_not_entries(self) -> None:
        boundary = parse_boundary_block("# 說明\n\nmodify = doc/\n")
        self.assertEqual(boundary.modify, ("doc/",))
        self.assertEqual(boundary.create, ())

    def test_a_malformed_path_in_a_declaration_refuses(self) -> None:
        with self.assertRaises(ValueError):
            parse_boundary_block("modify = ../outside/\n")


# ---------------------------------------------------------------------------
# Defect class 1: all seven path-boundary cells
# ---------------------------------------------------------------------------


class PathBoundaryTests(unittest.TestCase):
    """`doc/` is the boundary in every cell below; only the path changes."""

    def _verdict(self, path: str, **kwargs: object) -> DocumentMutationFailure | None:
        boundary = _boundary(**kwargs)  # type: ignore[arg-type]
        return evaluate_change(
            boundary, DocumentChange(path=path, kind=ChangeKind.MODIFY)
        )

    def test_cell_1_an_exactly_equal_path_is_inside(self) -> None:
        self.assertIsNone(self._verdict("README.md", modify=("README.md",)))

    def test_cell_2_one_extra_character_is_a_different_directory(self) -> None:
        # `doc2/` shares a prefix with `doc/` and nothing else. A string
        # `startswith` here is the whole family.
        self.assertIs(
            self._verdict("doc2/note.md"),
            DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY,
        )

    def test_cell_3_the_trailing_slash_is_what_makes_an_entry_a_directory(self) -> None:
        self.assertIsNone(self._verdict("doc/note.md", modify=("doc/",)))
        # Without the slash the author named one file, so it covers one file.
        self.assertIs(
            self._verdict("doc/note.md", modify=("doc",)),
            DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY,
        )

    def test_cell_4_allow_lists_compare_case_exactly(self) -> None:
        # On Windows `DOC/note.md` is the same file, but admitting it would
        # admit a path the ticket never wrote. Fail closed: refuse.
        self.assertIs(
            self._verdict("DOC/note.md"),
            DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY,
        )

    def test_cell_4_the_forbid_list_compares_case_insensitively(self) -> None:
        # And here fail-closed points the other way: on a case-insensitive
        # filesystem `Dispatch_Authority.py` *is* the forbidden file.
        self.assertIs(
            self._verdict(
                "library/Dispatch_Authority.py",
                modify=("library/",),
                forbid=("library/dispatch_authority.py",),
            ),
            DocumentMutationFailure.PATH_FORBIDDEN,
        )

    def test_cell_5_percent_encoding_is_never_decoded(self) -> None:
        # `%2F` is a character in a file name here, not a separator.
        self.assertIs(
            self._verdict("doc%2Fnote.md"),
            DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY,
        )

    def test_cell_6_traversal_is_resolved_before_it_is_matched(self) -> None:
        # Matched as written, `doc/../library/x.py` starts with `doc/`.
        self.assertIs(
            self._verdict("doc/../library/x.py"),
            DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY,
        )

    def test_cell_6_traversal_out_of_the_repository_has_no_relative_form(self) -> None:
        self.assertIs(
            self._verdict("doc/../../elsewhere.md"),
            DocumentMutationFailure.PATH_NOT_REPOSITORY_RELATIVE,
        )

    def test_cell_7_an_empty_path_is_refused_by_name(self) -> None:
        self.assertIs(
            self._verdict(""),
            DocumentMutationFailure.PATH_NOT_REPOSITORY_RELATIVE,
        )

    def test_a_backslash_is_a_separator_here_not_a_character(self) -> None:
        self.assertIsNone(normalize_change_path("doc\\..\\library\\x.py"))
        self.assertIs(
            self._verdict("doc\\..\\library\\x.py"),
            DocumentMutationFailure.PATH_NOT_REPOSITORY_RELATIVE,
        )

    def test_an_absolute_path_is_refused(self) -> None:
        self.assertIsNone(normalize_change_path("/etc/passwd"))
        self.assertIsNone(normalize_change_path("C:/Windows/system32"))

    def test_a_single_star_does_not_cross_a_separator(self) -> None:
        self.assertIsNone(self._verdict("doc/note.md", modify=("doc/*",)))
        self.assertIs(
            self._verdict("doc/deep/note.md", modify=("doc/*",)),
            DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY,
        )


# ---------------------------------------------------------------------------
# The three thresholds, each with its own code
# ---------------------------------------------------------------------------


class ThresholdTests(unittest.TestCase):
    def test_a_modification_inside_the_boundary_is_admitted(self) -> None:
        self.assertIsNone(
            evaluate_change(
                _boundary(), DocumentChange(path="doc/a.md", kind=ChangeKind.MODIFY)
            )
        )

    def test_creation_needs_its_own_authorization_not_the_modify_envelope(self) -> None:
        # Inside `modify`, and still refused: creating a file is not the same
        # act as editing one.
        self.assertIs(
            evaluate_change(
                _boundary(modify=("doc/",)),
                DocumentChange(path="doc/new.md", kind=ChangeKind.CREATE),
            ),
            DocumentMutationFailure.CREATION_NOT_AUTHORIZED,
        )

    def test_an_authorized_creation_is_admitted(self) -> None:
        self.assertIsNone(
            evaluate_change(
                _boundary(modify=("doc/",), create=("doc/new/",)),
                DocumentChange(path="doc/new/page.md", kind=ChangeKind.CREATE),
            )
        )

    def test_deletion_is_not_covered_by_modify_or_create(self) -> None:
        self.assertIs(
            evaluate_change(
                _boundary(modify=("doc/",), create=("doc/",)),
                DocumentChange(path="doc/a.md", kind=ChangeKind.DELETE),
            ),
            DocumentMutationFailure.DELETION_NOT_AUTHORIZED,
        )

    def test_an_exactly_named_deletion_is_admitted(self) -> None:
        self.assertIsNone(
            evaluate_change(
                _boundary(modify=("doc/",), delete=("doc/a.md",)),
                DocumentChange(path="doc/a.md", kind=ChangeKind.DELETE),
            )
        )

    def test_the_three_threshold_codes_are_distinct(self) -> None:
        codes = {
            DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY,
            DocumentMutationFailure.CREATION_NOT_AUTHORIZED,
            DocumentMutationFailure.DELETION_NOT_AUTHORIZED,
        }
        self.assertEqual(len(codes), 3)
        values = [failure.value for failure in DocumentMutationFailure]
        self.assertEqual(len(values), len(set(values)))

    def test_forbid_outranks_every_allow_list(self) -> None:
        for kind in ChangeKind:
            with self.subTest(kind=kind):
                self.assertIs(
                    evaluate_change(
                        _boundary(
                            modify=("doc/",),
                            create=("doc/",),
                            delete=("doc/a.md",),
                            forbid=("doc/a.md",),
                        ),
                        DocumentChange(path="doc/a.md", kind=kind),
                    ),
                    DocumentMutationFailure.PATH_FORBIDDEN,
                )

    def test_the_first_refusal_in_a_set_is_deterministic(self) -> None:
        changes = (
            DocumentChange(path="zzz.md", kind=ChangeKind.MODIFY),
            DocumentChange(path="aaa.md", kind=ChangeKind.MODIFY),
        )
        failure, path = evaluate_changes(_boundary(), changes)
        self.assertIs(failure, DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY)
        self.assertEqual(path, "aaa.md")
        self.assertEqual(evaluate_changes(_boundary(), tuple(reversed(changes)))[1], "aaa.md")


# ---------------------------------------------------------------------------
# Defect class 3: the indirect routes
# ---------------------------------------------------------------------------


class BypassTests(unittest.TestCase):
    def test_a_symlink_inside_the_boundary_is_still_refused(self) -> None:
        # The path is inside `doc/`; what it points at is not something the
        # gate can see, so admitting it by path would admit anything.
        self.assertIs(
            evaluate_change(
                _boundary(modify=("doc/",), create=("doc/",)),
                DocumentChange(
                    path="doc/link", kind=ChangeKind.CREATE, entry_mode="120000"
                ),
            ),
            DocumentMutationFailure.REDIRECTION_ENTRY_NOT_ADMISSIBLE,
        )

    def test_a_submodule_entry_is_refused_the_same_way(self) -> None:
        self.assertIs(
            evaluate_change(
                _boundary(modify=("doc/",), create=("doc/",)),
                DocumentChange(
                    path="doc/vendor", kind=ChangeKind.CREATE, entry_mode="160000"
                ),
            ),
            DocumentMutationFailure.REDIRECTION_ENTRY_NOT_ADMISSIBLE,
        )

    def test_converting_a_file_into_a_symlink_is_refused(self) -> None:
        self.assertIs(
            evaluate_change(
                _boundary(modify=("doc/",)),
                DocumentChange(
                    path="doc/a.md", kind=ChangeKind.MODIFY, entry_mode="120000"
                ),
            ),
            DocumentMutationFailure.REDIRECTION_ENTRY_NOT_ADMISSIBLE,
        )

    def test_deleting_a_symlink_is_judged_by_the_deletion_threshold(self) -> None:
        # Removing a redirection redirects nothing; it is a deletion, and the
        # deletion threshold is the one that applies.
        self.assertIs(
            evaluate_change(
                _boundary(modify=("doc/",)),
                DocumentChange(
                    path="doc/link", kind=ChangeKind.DELETE, entry_mode="120000"
                ),
            ),
            DocumentMutationFailure.DELETION_NOT_AUTHORIZED,
        )
        self.assertIsNone(
            evaluate_change(
                _boundary(modify=("doc/",), delete=("doc/link",)),
                DocumentChange(
                    path="doc/link", kind=ChangeKind.DELETE, entry_mode="120000"
                ),
            )
        )

    def test_an_executable_bit_is_content_not_redirection(self) -> None:
        self.assertIsNone(
            evaluate_change(
                _boundary(modify=("doc/",)),
                DocumentChange(
                    path="doc/run.sh", kind=ChangeKind.MODIFY, entry_mode="100755"
                ),
            )
        )

    def test_gitignore_gets_no_exemption_from_the_boundary(self) -> None:
        # Editing what the repository ignores changes what a later reader can
        # see, so it is a change like any other and needs the same authority.
        self.assertIs(
            evaluate_change(
                _boundary(modify=("doc/",)),
                DocumentChange(path=".gitignore", kind=ChangeKind.MODIFY),
            ),
            DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY,
        )


# ---------------------------------------------------------------------------
# Defect class 2: empty lists, empty sets, empty strings
# ---------------------------------------------------------------------------


class EmptyInputTests(unittest.TestCase):
    def test_an_empty_change_set_has_nothing_to_refuse(self) -> None:
        self.assertEqual(evaluate_changes(_boundary(), ()), (None, None))

    def test_an_empty_modify_list_cannot_be_declared_at_all(self) -> None:
        with self.assertRaises(ValidationError):
            DocumentBoundary(modify=())

    def test_an_absent_create_list_authorizes_no_creation(self) -> None:
        self.assertEqual(_boundary().create, ())
        self.assertIs(
            evaluate_change(
                _boundary(), DocumentChange(path="doc/new.md", kind=ChangeKind.CREATE)
            ),
            DocumentMutationFailure.CREATION_NOT_AUTHORIZED,
        )

    def test_an_absent_delete_list_authorizes_no_deletion(self) -> None:
        self.assertEqual(_boundary().delete, ())
        self.assertIs(
            evaluate_change(
                _boundary(), DocumentChange(path="doc/a.md", kind=ChangeKind.DELETE)
            ),
            DocumentMutationFailure.DELETION_NOT_AUTHORIZED,
        )

    def test_an_empty_path_string_is_its_own_named_answer(self) -> None:
        self.assertIsNone(normalize_change_path(""))
        self.assertIs(
            evaluate_change(
                _boundary(), DocumentChange(path="", kind=ChangeKind.MODIFY)
            ),
            DocumentMutationFailure.PATH_NOT_REPOSITORY_RELATIVE,
        )


# ---------------------------------------------------------------------------
# Reading the change set out of git rather than out of the request
# ---------------------------------------------------------------------------


class RawDiffTests(unittest.TestCase):
    def test_added_modified_and_deleted_entries_parse(self) -> None:
        payload = (
            b":000000 100644 0000000 aaaaaaa A\x00doc/new.md\x00"
            b":100644 100644 aaaaaaa bbbbbbb M\x00doc/old.md\x00"
            b":100644 000000 bbbbbbb 0000000 D\x00doc/gone.md\x00"
        )
        changes = parse_raw_diff(payload)
        assert changes is not None
        self.assertEqual(
            [(change.path, change.kind) for change in changes],
            [
                ("doc/new.md", ChangeKind.CREATE),
                ("doc/old.md", ChangeKind.MODIFY),
                ("doc/gone.md", ChangeKind.DELETE),
            ],
        )

    def test_a_symlink_mode_survives_into_the_change(self) -> None:
        changes = parse_raw_diff(b":000000 120000 0000000 aaaaaaa A\x00doc/link\x00")
        assert changes is not None
        self.assertEqual(changes[0].entry_mode, "120000")

    def test_a_rename_is_a_deletion_and_a_creation(self) -> None:
        changes = parse_raw_diff(
            b":100644 100644 aaaaaaa aaaaaaa R100\x00doc/a.md\x00library/a.md\x00"
        )
        assert changes is not None
        self.assertEqual(
            [(change.path, change.kind) for change in changes],
            [("doc/a.md", ChangeKind.DELETE), ("library/a.md", ChangeKind.CREATE)],
        )

    def test_an_unmerged_entry_is_not_a_finished_change(self) -> None:
        self.assertIsNone(
            parse_raw_diff(b":000000 000000 0000000 0000000 U\x00doc/a.md\x00")
        )

    def test_malformed_output_parses_to_nothing_rather_than_something(self) -> None:
        self.assertIsNone(parse_raw_diff(b"doc/a.md\x00"))
        self.assertIsNone(parse_raw_diff(b":100644 100644 aaa M\x00doc/a.md\x00"))
        self.assertIsNone(parse_raw_diff(b":000000 100644 0000000 aaaaaaa A\x00"))

    def test_a_cjk_path_survives_the_console_encoding(self) -> None:
        payload = ":000000 100644 0000000 aaaaaaa A\x00文件/新頁.md\x00".encode("utf-8")
        changes = parse_raw_diff(payload)
        assert changes is not None
        self.assertEqual(changes[0].path, "文件/新頁.md")


# ---------------------------------------------------------------------------
# The guarantee itself: on refusal, main does not move
# ---------------------------------------------------------------------------


class IntegrationTests(unittest.TestCase):
    def test_a_declared_change_reaches_main(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base, _ticket_text(modify=("doc/",)))
            before = _run(root, "rev-parse", "HEAD")
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(root, "doc/existing.md", "after\n")
            candidate = _commit(root, "edit inside the boundary")
            _run(root, "checkout", "-q", "main")

            result = admit_document_mutation(_layout(base), _request(root))

            self.assertIs(result.status, DocumentMutationStatus.INTEGRATED)
            self.assertEqual(result.integrated_commit, candidate)
            self.assertNotEqual(_run(root, "rev-parse", "HEAD"), before)
            self.assertEqual(
                (root / "doc" / "existing.md").read_text(encoding="utf-8"), "after\n"
            )

    def _refused(
        self, base: Path, ticket: str, mutate: object
    ) -> tuple[Path, str, object]:
        root = _seed(base, ticket)
        before = _run(root, "rev-parse", "HEAD")
        _run(root, "checkout", "-q", "-b", "candidate")
        mutate(root)  # type: ignore[operator]
        _commit(root, "candidate work")
        _run(root, "checkout", "-q", "main")
        result = admit_document_mutation(_layout(base), _request(root))
        return root, before, result

    def test_a_modification_outside_the_boundary_never_reaches_main(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)

            def mutate(root: Path) -> None:
                _write(root, "library/untouchable.py", "changed\n")

            root, before, result = self._refused(
                base, _ticket_text(modify=("doc/",)), mutate
            )

            self.assertIs(result.status, DocumentMutationStatus.REFUSED)  # type: ignore[union-attr]
            self.assertIs(
                result.failure,  # type: ignore[union-attr]
                DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY,
            )
            self.assertEqual(result.offending_path, "library/untouchable.py")  # type: ignore[union-attr]
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)
            self.assertEqual(
                (root / "library" / "untouchable.py").read_text(encoding="utf-8"),
                "keep\n",
            )

    def test_an_unauthorized_creation_never_reaches_main(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)

            def mutate(root: Path) -> None:
                _write(root, "doc/invented.md", "new\n")

            root, before, result = self._refused(
                base, _ticket_text(modify=("doc/",)), mutate
            )

            self.assertIs(
                result.failure,  # type: ignore[union-attr]
                DocumentMutationFailure.CREATION_NOT_AUTHORIZED,
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)
            self.assertFalse((root / "doc" / "invented.md").exists())

    def test_an_unauthorized_deletion_never_reaches_main(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)

            def mutate(root: Path) -> None:
                (root / "doc" / "existing.md").unlink()

            root, before, result = self._refused(
                base, _ticket_text(modify=("doc/",)), mutate
            )

            self.assertIs(
                result.failure,  # type: ignore[union-attr]
                DocumentMutationFailure.DELETION_NOT_AUTHORIZED,
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)
            self.assertTrue((root / "doc" / "existing.md").is_file())

    def test_the_boundary_is_read_from_main_not_from_the_candidate(self) -> None:
        """The branch under judgement does not get to rewrite the rule.

        Under the candidate's own declaration both of its changes are allowed.
        Only the copy on `main` refuses them, so a green here is only possible
        if the gate read `main`.
        """

        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base, _ticket_text(modify=("doc/",)))
            before = _run(root, "rev-parse", "HEAD")
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(
                root,
                _TICKET,
                _ticket_text(modify=("doc/", "library/", _TICKET)),
            )
            _write(root, "library/untouchable.py", "changed\n")
            _commit(root, "widen my own boundary, then use it")
            _run(root, "checkout", "-q", "main")

            result = admit_document_mutation(_layout(base), _request(root))

            self.assertIs(result.status, DocumentMutationStatus.REFUSED)
            self.assertIs(
                result.failure, DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_ticket_main_cannot_read_refuses_rather_than_admits(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base, _ticket_text(modify=("doc/",)))
            before = _run(root, "rev-parse", "HEAD")
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(root, "doc/existing.md", "after\n")
            _commit(root, "edit inside the boundary")
            _run(root, "checkout", "-q", "main")

            result = admit_document_mutation(
                _layout(base), _request(root, ticket_path="modules/tickets/absent.md")
            )

            self.assertIs(result.failure, DocumentMutationFailure.TICKET_UNREADABLE)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_ticket_without_a_block_refuses_rather_than_admits(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)

            def mutate(root: Path) -> None:
                _write(root, "doc/existing.md", "after\n")

            root, before, result = self._refused(
                base, _ticket_text(block=False), mutate
            )

            self.assertIs(
                result.failure,  # type: ignore[union-attr]
                DocumentMutationFailure.BOUNDARY_UNDECLARED,
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_broken_block_refuses_and_says_what_broke(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)

            def mutate(root: Path) -> None:
                _write(root, "doc/existing.md", "after\n")

            root, before, result = self._refused(
                base, "# 壞掉的票\n\n```johnny-boundary\nmodifyy = doc/\n```\n", mutate
            )

            self.assertIs(
                result.failure,  # type: ignore[union-attr]
                DocumentMutationFailure.BOUNDARY_UNPARSABLE,
            )
            self.assertIn("modifyy", result.detail or "")  # type: ignore[union-attr]
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_symlink_committed_through_the_index_never_reaches_main(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base, _ticket_text(modify=("doc/",), create=("doc/",)))
            before = _run(root, "rev-parse", "HEAD")
            _run(root, "checkout", "-q", "-b", "candidate")
            blob = subprocess.run(
                ("git", "-C", str(root), "hash-object", "-w", "--stdin"),
                input=b"../../library/untouchable.py",
                capture_output=True,
                check=True,
            ).stdout.decode("utf-8").strip()
            _run(root, "update-index", "--add", "--cacheinfo", f"120000,{blob},doc/link")
            _run(root, "commit", "-q", "-m", "a link that points out of the boundary")
            _run(root, "checkout", "-q", "--force", "main")

            result = admit_document_mutation(_layout(base), _request(root))

            self.assertIs(
                result.failure,
                DocumentMutationFailure.REDIRECTION_ENTRY_NOT_ADMISSIBLE,
            )
            self.assertEqual(result.offending_path, "doc/link")
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_candidate_that_does_not_fast_forward_leaves_main_alone(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base, _ticket_text(modify=("doc/",)))
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(root, "doc/existing.md", "candidate\n")
            _commit(root, "edit inside the boundary")
            _run(root, "checkout", "-q", "main")
            _write(root, "doc/existing.md", "main moved on\n")
            before = _commit(root, "main advances")

            result = admit_document_mutation(_layout(base), _request(root))

            self.assertIs(result.failure, DocumentMutationFailure.INTEGRATION_FAILED)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_an_unclean_integration_worktree_refuses(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base, _ticket_text(modify=("doc/",)))
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(root, "doc/existing.md", "after\n")
            _commit(root, "edit inside the boundary")
            _run(root, "checkout", "-q", "main")
            before = _run(root, "rev-parse", "HEAD")
            _write(root, "doc/unjudged.md", "nobody reviewed this\n")

            result = admit_document_mutation(_layout(base), _request(root))

            self.assertIs(result.failure, DocumentMutationFailure.REPOSITORY_UNREADABLE)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_integrating_from_the_wrong_branch_refuses(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base, _ticket_text(modify=("doc/",)))
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(root, "doc/existing.md", "after\n")
            before = _commit(root, "edit inside the boundary")

            result = admit_document_mutation(_layout(base), _request(root))

            self.assertIs(result.failure, DocumentMutationFailure.REPOSITORY_UNREADABLE)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_repository_root_that_is_not_a_directory_refuses(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            result = admit_document_mutation(
                _layout(base),
                DocumentMutationRequest(
                    repository_root=str(base / "absent"),
                    ticket_path=_TICKET,
                    integration_branch="main",
                    candidate_ref="candidate",
                ),
            )
            self.assertIs(result.failure, DocumentMutationFailure.REPOSITORY_UNREADABLE)

    def test_every_outcome_leaves_a_journal_line_naming_the_path(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            layout = _layout(base)
            root = _seed(base, _ticket_text(modify=("doc/",)))
            _run(root, "checkout", "-q", "-b", "candidate")
            _write(root, "library/untouchable.py", "changed\n")
            _commit(root, "outside")
            _run(root, "checkout", "-q", "main")

            admit_document_mutation(layout, _request(root))

            lines = journal_path(layout).read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            entry = json.loads(lines[0])
            self.assertEqual(
                entry["outcome"],
                DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY.value,
            )
            self.assertEqual(entry["offending_path"], "library/untouchable.py")
            self.assertEqual(entry["ticket_path"], _TICKET)
            self.assertTrue(entry["principal"])


# ---------------------------------------------------------------------------
# Regression: this gate is not an issuance route, and does not become one
# ---------------------------------------------------------------------------


class IssuanceSeparationTests(unittest.TestCase):
    def test_the_gate_holds_no_issuance_capability(self) -> None:
        """Identity, not names: an aliased import is family C5's bypass."""

        from library.local_orchestration import dispatch_authority
        from library.local_orchestration import issuance_scoped_boundary

        forbidden = {
            id(dispatch_authority.admit_dispatch),
            id(dispatch_authority.create_dispatch_grant),
            id(dispatch_authority.read_dispatch_grant),
            id(issuance_scoped_boundary.IssuanceScopedDispatchBoundary),
        }
        held = {id(value) for value in vars(gate).values()}
        self.assertEqual(forbidden & held, set())

    def test_dispatch_admission_still_refuses_without_a_grant(self) -> None:
        with TemporaryDirectory() as name:
            layout = _layout(Path(name))
            result = admit_dispatch(layout, object())  # type: ignore[arg-type]
            self.assertIs(result.status, DispatchAdmissionStatus.REFUSED)
            self.assertIs(
                result.failure, DispatchAdmissionFailure.DISPATCH_AUTHORITY_ABSENT
            )

    def test_a_grant_is_still_what_dispatch_admission_reads(self) -> None:
        with TemporaryDirectory() as name:
            layout = _layout(Path(name))
            status, grant = create_dispatch_grant(layout)
            self.assertEqual(status.value, "GRANTED")
            assert grant is not None
            # The document gate must not be able to satisfy this gate's
            # precondition, and does not touch its grant file.
            result = admit_dispatch(layout, object())  # type: ignore[arg-type]
            self.assertIs(result.failure, DispatchAdmissionFailure.REQUEST_INVALID)


if __name__ == "__main__":
    unittest.main()
