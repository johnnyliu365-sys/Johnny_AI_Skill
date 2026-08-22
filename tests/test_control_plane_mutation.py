"""19: the control plane's own commits enter by a door that can refuse them.

Like the sister gate's tests, the integration cells run against a real
repository. The claim is not "the function returned REFUSED" — it is "`main`
is at the commit it was already at", and only a real `main` can answer that.
A fake would let every refusal be green while the merge happened anyway, which
is family C6 of the pitfall register.

The cells are grouped by the property they nail, and the two properties that
have no natural home in a single scenario — "no refusal path runs a mutating
Git verb" and "the two doors are not interchangeable" — get their own classes
so they are nailed on the path production actually takes rather than on a copy
of it.
"""

from __future__ import annotations

import getpass
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

from pydantic import ValidationError

from library.local_orchestration import control_plane_mutation as door
from library.local_orchestration.control_plane_mutation import (
    ControlPlaneMutationFailure,
    ControlPlaneMutationRequest,
    ControlPlaneMutationStatus,
    admit_control_plane_mutation,
    candidate_is_control_plane,
    mixed_change_failure,
    policy_digest,
    policy_document_id,
    policy_pins,
)
from library.local_orchestration.document_mutation_gate import (
    DocumentMutationFailure,
    DocumentMutationRequest,
    DocumentMutationStatus,
    admit_document_mutation,
    journal_path,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_CANDIDATE = "control/writeback"
_TICKET = "modules/tickets/demo.md"
_POLICY = "skills/johnny-project-takeover/references/review-checks.md"
_PROFILE = "library/workflow_router/profile.py"
_PROFILE_TEST = "tests/test_workflow_router.py"

#: Every Git verb that can move a ref or a working tree. A refusal that ran
#: any of these would have moved something before deciding not to.
_MUTATING_VERBS = frozenset(
    {
        "add",
        "am",
        "apply",
        "branch",
        "checkout",
        "cherry-pick",
        "clean",
        "commit",
        "fetch",
        "gc",
        "init",
        "merge",
        "mv",
        "pull",
        "push",
        "rebase",
        "reset",
        "restore",
        "rm",
        "stash",
        "switch",
        "tag",
        "update-ref",
        "worktree",
    }
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


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
        ("user.name", "Control Plane Test"),
        ("user.email", "control@example.com"),
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


def _blocked_layout(base: Path) -> JohnnyRootLayout:
    """A layout whose queue directory is occupied by a file, so no line lands."""

    layout = JohnnyRootLayout(base=(base / "blocked").resolve())
    layout.base.mkdir(parents=True, exist_ok=True)
    layout.queue_root.write_text("not a directory\n", encoding="utf-8")
    return layout


def _pin_literals(text: str) -> tuple[str, str]:
    body = text.replace("\r\n", "\n").encode("utf-8")
    hexdigest = hashlib.sha256(body).hexdigest()
    return "rev-" + hexdigest[:16], "sha256_" + hexdigest


def _profile_text(revision: str, digest: str) -> str:
    return (
        "REFERENCES = (\n"
        "    SkillReference(\n"
        '        reference_id="review-checks",\n'
        f'        source_revision="{revision}",\n'
        f'        content_digest="{digest}",\n'
        "    ),\n"
        ")\n"
    )


def _profile_test_text(revision: str, digest: str) -> str:
    return (
        "_EXPECTED_POLICIES = (\n"
        '    _ExpectedPolicy(\n'
        '        "review-checks",\n'
        f'        "{revision}",\n'
        f'        "{digest}",\n'
        "    ),\n"
        ")\n"
    )


def _seed(base: Path, *, policy_body: str = "policy one\n") -> Path:
    """A repository whose `main` holds a rule tree, a ticket tree and a policy."""

    root = _repository(base)
    revision, digest = _pin_literals(policy_body)
    _write(root, "library/local_orchestration/thing.py", "keep\n")
    _write(root, _TICKET, "# demo\n")
    _write(root, _POLICY, policy_body)
    _write(root, _PROFILE, _profile_text(revision, digest))
    _write(root, _PROFILE_TEST, _profile_test_text(revision, digest))
    _commit(root, "baseline")
    return root


def _request(
    root: Path,
    *,
    candidate_ref: str = _CANDIDATE,
    principal: str | None = None,
    integration_branch: str = "main",
) -> ControlPlaneMutationRequest:
    return ControlPlaneMutationRequest(
        repository_root=str(root),
        integration_branch=integration_branch,
        candidate_ref=candidate_ref,
        principal=getpass.getuser() if principal is None else principal,
    )


def _candidate(
    root: Path, mutate: Callable[[Path], None], *, name: str = _CANDIDATE
) -> str:
    """Build one candidate branch and leave `main` checked out again."""

    _run(root, "checkout", "-q", "-b", name)
    mutate(root)
    head = _commit(root, "control-plane work")
    _run(root, "checkout", "-q", "main")
    return head


def _journal_lines(layout: JohnnyRootLayout) -> list[dict[str, object]]:
    path = journal_path(layout)
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


# ---------------------------------------------------------------------------
# Namespace: which door a candidate belongs at
# ---------------------------------------------------------------------------


class NamespaceTests(unittest.TestCase):
    def test_the_control_namespace_is_what_this_door_admits(self) -> None:
        self.assertTrue(candidate_is_control_plane("control/gov-19-writeback"))

    def test_an_implementer_candidate_is_not_admissible_here(self) -> None:
        self.assertFalse(
            candidate_is_control_plane("implement/gov-19-control-plane-gate")
        )

    def test_the_prohibition_is_case_folded(self) -> None:
        """`Implement/x` walking past a rule naming `implement/` is the bypass."""

        self.assertFalse(candidate_is_control_plane("Implement/gov-19"))
        self.assertFalse(candidate_is_control_plane("CODEX/implementation-x"))

    def test_an_implementer_branch_cannot_be_re_parented_under_this_door(self) -> None:
        """The legible form of the bypass, and the only thing the prohibition
        catches that the allow list does not."""

        self.assertFalse(candidate_is_control_plane("control/implement/gov-19"))
        self.assertFalse(candidate_is_control_plane("control/codex/registration"))
        self.assertFalse(candidate_is_control_plane("control/x/Implement/y"))

    def test_a_component_that_merely_starts_with_a_namespace_is_not_one(self) -> None:
        self.assertTrue(candidate_is_control_plane("control/codex-notes"))
        self.assertTrue(candidate_is_control_plane("control/implementation-notes"))

    def test_the_permission_is_compared_exactly(self) -> None:
        """A ref is a name somebody chose; `CONTROL/x` is a different name."""

        self.assertFalse(candidate_is_control_plane("CONTROL/writeback"))
        self.assertFalse(candidate_is_control_plane("Control/writeback"))

    def test_the_namespace_prefix_is_not_a_word_prefix(self) -> None:
        self.assertFalse(candidate_is_control_plane("controlled/x"))
        self.assertFalse(candidate_is_control_plane("control-plane/x"))

    def test_the_bare_prefix_names_no_branch(self) -> None:
        self.assertFalse(candidate_is_control_plane("control/"))

    def test_a_trunk_name_is_not_a_control_plane_candidate(self) -> None:
        self.assertFalse(candidate_is_control_plane("main"))
        self.assertFalse(candidate_is_control_plane(""))


# ---------------------------------------------------------------------------
# Rule one: the rule and its subject may not move in one commit
# ---------------------------------------------------------------------------


class MixedChangeTests(unittest.TestCase):
    def test_the_rule_and_its_subject_together_is_the_refused_shape(self) -> None:
        self.assertEqual(
            mixed_change_failure(("library/a.py", "modules/tickets/x.md")),
            ("library/a.py", "modules/tickets/x.md"),
        )

    def test_either_tree_alone_is_admissible(self) -> None:
        self.assertIsNone(mixed_change_failure(("library/a.py", "doc/b.md")))
        self.assertIsNone(mixed_change_failure(("modules/tickets/x.md", "doc/b.md")))

    def test_an_adjacent_tree_is_not_the_ticket_tree(self) -> None:
        """`modules/tickets-archive/` is defect class 1 in one line."""

        self.assertIsNone(
            mixed_change_failure(("library/a.py", "modules/tickets-archive/x.md"))
        )
        self.assertIsNone(
            mixed_change_failure(("library/a.py", "modules/ticketsx.md"))
        )

    def test_an_adjacent_tree_is_not_the_rule_tree(self) -> None:
        self.assertIsNone(
            mixed_change_failure(("libraryx/a.py", "modules/tickets/x.md"))
        )
        self.assertIsNone(
            mixed_change_failure(("library.py", "modules/tickets/x.md"))
        )

    def test_a_root_file_named_like_a_tree_is_not_that_tree(self) -> None:
        self.assertIsNone(mixed_change_failure(("library", "modules/tickets/x.md")))

    def test_an_empty_change_set_offends_nothing(self) -> None:
        self.assertIsNone(mixed_change_failure(()))

    def test_the_named_pair_is_the_same_on_every_run(self) -> None:
        offending = mixed_change_failure(
            (
                "library/z.py",
                "library/a.py",
                "modules/tickets/z.md",
                "modules/tickets/a.md",
            )
        )
        self.assertEqual(offending, ("library/a.py", "modules/tickets/a.md"))


# ---------------------------------------------------------------------------
# Rule two: a pinned policy document arrives with its pins
# ---------------------------------------------------------------------------


class PolicyPinTests(unittest.TestCase):
    def test_a_reference_document_carries_its_reference_id(self) -> None:
        self.assertEqual(policy_document_id(_POLICY), "review-checks")

    def test_an_adjacent_directory_is_not_the_reference_directory(self) -> None:
        self.assertIsNone(
            policy_document_id(
                "skills/johnny-project-takeover/references-old/review-checks.md"
            )
        )

    def test_a_nested_path_is_not_a_reference_document(self) -> None:
        self.assertIsNone(
            policy_document_id(
                "skills/johnny-project-takeover/references/old/review-checks.md"
            )
        )

    def test_a_non_markdown_neighbour_is_not_a_reference_document(self) -> None:
        self.assertIsNone(
            policy_document_id("skills/johnny-project-takeover/references/notes.txt")
        )
        self.assertIsNone(
            policy_document_id("skills/johnny-project-takeover/references/.md")
        )

    def test_the_pin_reader_reads_the_repository_s_own_pinning_module(self) -> None:
        """Nailed on the real artifact: a regex that only parses the fixture
        would be a copy of the format, not the format."""

        pins = policy_pins((_PROJECT_ROOT / _PROFILE).read_text(encoding="utf-8"))
        self.assertIn("review-checks", pins)
        self.assertIn("router-control", pins)
        # A floor, not an equality: an eighth pinned policy is a legitimate
        # future change, but a regex that stopped matching would make the
        # digest cell below pass over an empty set.
        self.assertGreaterEqual(len(pins), 7)

    def test_the_recomputed_digest_matches_the_repository_s_own_pin(self) -> None:
        """The rule is only worth anything if its arithmetic is the project's."""

        pins = policy_pins((_PROJECT_ROOT / _PROFILE).read_text(encoding="utf-8"))
        for identifier, pinned in sorted(pins.items()):
            with self.subTest(policy=identifier):
                document = (
                    _PROJECT_ROOT
                    / "skills/johnny-project-takeover/references"
                    / f"{identifier}.md"
                )
                self.assertEqual(policy_digest(document.read_bytes()), pinned)

    def test_the_digest_does_not_depend_on_the_working_copy_s_line_endings(
        self,
    ) -> None:
        self.assertEqual(policy_digest(b"a\r\nb\r\n"), policy_digest(b"a\nb\n"))


# ---------------------------------------------------------------------------
# The request: attribution, and the three empty answers kept apart
# ---------------------------------------------------------------------------


class RequestTests(unittest.TestCase):
    def test_a_principal_cannot_be_absent_at_all(self) -> None:
        with self.assertRaises(ValidationError):
            ControlPlaneMutationRequest(
                repository_root="C:/repo",
                integration_branch="main",
                candidate_ref=_CANDIDATE,
                principal="",
            )

    def test_a_blank_principal_is_its_own_named_refusal(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            _candidate(root, lambda repo: _write(repo, _TICKET, "# edited\n"))

            result = admit_control_plane_mutation(
                _layout(base), _request(root, principal="   ")
            )

            self.assertIs(result.status, ControlPlaneMutationStatus.REFUSED)
            self.assertIs(
                result.failure, ControlPlaneMutationFailure.PRINCIPAL_UNDECLARED
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_principal_who_is_not_at_this_machine_is_refused(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            _candidate(root, lambda repo: _write(repo, _TICKET, "# edited\n"))

            result = admit_control_plane_mutation(
                _layout(base), _request(root, principal="somebody-else")
            )

            self.assertIs(
                result.failure, ControlPlaneMutationFailure.PRINCIPAL_NOT_HOST
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_an_empty_change_set_is_not_an_integration(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            _run(root, "branch", _CANDIDATE)

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(
                result.failure, ControlPlaneMutationFailure.NOTHING_TO_INTEGRATE
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_an_object_that_is_not_a_request_is_refused_by_name(self) -> None:
        with TemporaryDirectory() as name:
            layout = _layout(Path(name))
            result = admit_control_plane_mutation(layout, object())  # type: ignore[arg-type]
            self.assertIs(result.failure, ControlPlaneMutationFailure.REQUEST_INVALID)


# ---------------------------------------------------------------------------
# Integration: what actually reaches `main`
# ---------------------------------------------------------------------------


class IntegrationTests(unittest.TestCase):
    def test_the_control_plane_may_still_open_a_ticket(self) -> None:
        """The point of the ticket: this is a door, not a cage."""

        with TemporaryDirectory() as name:
            base = Path(name)
            layout = _layout(base)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            head = _candidate(
                root,
                lambda repo: _write(
                    repo, "modules/tickets/workflow-governance/20-new.md", "# 20\n"
                ),
            )

            result = admit_control_plane_mutation(layout, _request(root))

            self.assertIs(result.status, ControlPlaneMutationStatus.INTEGRATED)
            self.assertEqual(result.integrated_commit, head)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), head)
            self.assertNotEqual(head, before)

    def test_the_same_ticket_write_is_refused_at_the_implementer_door(self) -> None:
        """Different rules, same standard: each door enforces its own."""

        with TemporaryDirectory() as name:
            base = Path(name)
            root = _repository(base)
            _write(
                root,
                _TICKET,
                "```johnny-boundary\nmodify = doc/\nforbid = modules/tickets/\n```\n",
            )
            _write(root, "doc/existing.md", "before\n")
            _commit(root, "baseline")
            before = _run(root, "rev-parse", "HEAD")
            _candidate(
                root,
                lambda repo: _write(repo, "modules/tickets/new.md", "# new\n"),
                name="implement/thing",
            )

            result = admit_document_mutation(
                _layout(base),
                DocumentMutationRequest(
                    repository_root=str(root),
                    ticket_path=_TICKET,
                    integration_branch="main",
                    candidate_ref="implement/thing",
                ),
            )

            self.assertIs(result.status, DocumentMutationStatus.REFUSED)
            self.assertIs(result.failure, DocumentMutationFailure.PATH_FORBIDDEN)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_one_commit_touching_the_rule_and_its_subject_never_reaches_main(
        self,
    ) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")

            def mutate(repo: Path) -> None:
                _write(repo, "library/local_orchestration/thing.py", "changed\n")
                _write(repo, _TICKET, "# edited\n")

            _candidate(root, mutate)

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(
                result.failure,
                ControlPlaneMutationFailure.RULE_AND_SUBJECT_IN_ONE_CHANGE,
            )
            self.assertEqual(
                result.offending_path, "library/local_orchestration/thing.py"
            )
            self.assertIn(_TICKET, result.detail or "")
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_violation_in_a_middle_commit_is_not_missed(self) -> None:
        """Every commit in the range is read, not the first and not the tip.

        The offending commit is deliberately at neither end of the range: a
        loop truncated to `[:1]` and a check collapsed to the tip both walk
        past this, and both leave every rule in this module textually intact.
        The detail is asserted to name the offending commit itself, so the
        cell also fails if the refusal arrives from the wrong place.
        """

        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            _run(root, "checkout", "-q", "-b", _CANDIDATE)
            _write(root, _TICKET, "# opened\n")
            _commit(root, "open a ticket, which this door exists to allow")
            _write(root, "library/local_orchestration/thing.py", "changed\n")
            _write(root, "modules/tickets/second.md", "# second\n")
            offending = _commit(root, "change the rule and its subject together")
            _write(root, "modules/tickets/third.md", "# third\n")
            _commit(root, "open one more ticket")
            _run(root, "checkout", "-q", "main")

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(
                result.failure,
                ControlPlaneMutationFailure.RULE_AND_SUBJECT_IN_ONE_CHANGE,
            )
            self.assertEqual(
                result.offending_path, "library/local_orchestration/thing.py"
            )
            self.assertEqual(
                result.detail, f"{offending} also changed modules/tickets/second.md"
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_the_same_two_changes_in_two_commits_are_admissible(self) -> None:
        """The unit is the commit, because the commit is what a reviewer reads.

        This is the cell that forbids collapsing the loop into one diff over
        the whole candidate: the aggregate touches both trees, so a per-tip
        check would refuse this candidate and this cell would go red.
        """

        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            _run(root, "checkout", "-q", "-b", _CANDIDATE)
            _write(root, "library/local_orchestration/thing.py", "changed\n")
            _commit(root, "change the rule")
            _write(root, _TICKET, "# edited\n")
            head = _commit(root, "change what the rule governs")
            _run(root, "checkout", "-q", "main")

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(result.status, ControlPlaneMutationStatus.INTEGRATED)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), head)

    def test_a_policy_edit_without_its_repin_never_reaches_main(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            _candidate(root, lambda repo: _write(repo, _POLICY, "policy two\n"))

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(
                result.failure, ControlPlaneMutationFailure.POLICY_REPIN_STALE
            )
            self.assertEqual(result.offending_path, _POLICY)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_policy_edit_repinned_in_both_places_is_admitted(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            revision, digest = _pin_literals("policy two\n")

            def mutate(repo: Path) -> None:
                _write(repo, _POLICY, "policy two\n")
                _write(repo, _PROFILE, _profile_text(revision, digest))
                _write(repo, _PROFILE_TEST, _profile_test_text(revision, digest))

            head = _candidate(root, mutate)

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(result.status, ControlPlaneMutationStatus.INTEGRATED)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), head)

    def test_a_repin_that_lands_in_only_one_of_the_two_places_is_refused(self) -> None:
        """The failure the rule was written for: half a repin looks like a repin."""

        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            revision, digest = _pin_literals("policy two\n")

            def mutate(repo: Path) -> None:
                _write(repo, _POLICY, "policy two\n")
                _write(repo, _PROFILE, _profile_text(revision, digest))

            _candidate(root, mutate)

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(
                result.failure, ControlPlaneMutationFailure.POLICY_REPIN_STALE
            )
            self.assertIn(_PROFILE_TEST, result.detail or "")
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_repin_that_lands_only_in_the_regression_test_is_refused(self) -> None:
        """The mirror of the cell above, and the only one that reaches the
        pinning module's own comparison. Without it the two sites overlap and
        the regression file's check masks the module's — the overlap-masking
        shape from governance 17."""

        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            revision, digest = _pin_literals("policy two\n")

            def mutate(repo: Path) -> None:
                _write(repo, _POLICY, "policy two\n")
                _write(repo, _PROFILE_TEST, _profile_test_text(revision, digest))

            _candidate(root, mutate)

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(
                result.failure, ControlPlaneMutationFailure.POLICY_REPIN_STALE
            )
            self.assertIn(_PROFILE, result.detail or "")
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_touching_the_pinning_module_is_not_by_itself_a_repin(self) -> None:
        """A structural check would call this repinned. The digest disagrees."""

        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            stale_revision, stale_digest = _pin_literals("policy one\n")

            def mutate(repo: Path) -> None:
                _write(repo, _POLICY, "policy two\n")
                _write(
                    repo,
                    _PROFILE,
                    _profile_text(stale_revision, stale_digest) + "# touched\n",
                )
                _write(
                    repo,
                    _PROFILE_TEST,
                    _profile_test_text(stale_revision, stale_digest) + "# touched\n",
                )

            _candidate(root, mutate)

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(
                result.failure, ControlPlaneMutationFailure.POLICY_REPIN_STALE
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_an_unpinned_neighbour_in_the_same_directory_is_not_restricted(
        self,
    ) -> None:
        """Eleven of the eighteen documents there are pinned by nobody."""

        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            head = _candidate(
                root,
                lambda repo: _write(
                    repo,
                    "skills/johnny-project-takeover/references/language-policy.md",
                    "unpinned\n",
                ),
            )

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(result.status, ControlPlaneMutationStatus.INTEGRATED)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), head)

    def test_a_symlink_is_a_redirection_this_door_cannot_bound(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            _run(root, "checkout", "-q", "-b", _CANDIDATE)
            blob = subprocess.run(
                ("git", "-C", str(root), "hash-object", "-w", "--stdin"),
                input=b"../../library/local_orchestration/thing.py",
                capture_output=True,
                check=True,
            ).stdout.decode("utf-8").strip()
            _run(
                root, "update-index", "--add", "--cacheinfo", f"120000,{blob},doc/link"
            )
            _run(root, "commit", "-q", "-m", "a link this door cannot bound")
            _run(root, "checkout", "-q", "--force", "main")

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(
                result.failure,
                ControlPlaneMutationFailure.REDIRECTION_ENTRY_NOT_ADMISSIBLE,
            )
            self.assertEqual(result.offending_path, "doc/link")
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_candidate_that_does_not_fast_forward_leaves_main_alone(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            _candidate(root, lambda repo: _write(repo, _TICKET, "# candidate\n"))
            _write(root, "doc/diverged.md", "main moved\n")
            before = _commit(root, "main moves on")

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(
                result.failure, ControlPlaneMutationFailure.INTEGRATION_FAILED
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_an_unclean_integration_worktree_refuses(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            _candidate(root, lambda repo: _write(repo, _TICKET, "# candidate\n"))
            before = _run(root, "rev-parse", "HEAD")
            _write(root, "doc/unjudged.md", "nobody looked at this\n")

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(
                result.failure, ControlPlaneMutationFailure.REPOSITORY_UNREADABLE
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_integrating_from_the_wrong_branch_refuses(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            _run(root, "checkout", "-q", "-b", _CANDIDATE)
            _write(root, _TICKET, "# candidate\n")
            before = _commit(root, "control-plane work")

            result = admit_control_plane_mutation(_layout(base), _request(root))

            self.assertIs(
                result.failure, ControlPlaneMutationFailure.REPOSITORY_UNREADABLE
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_repository_root_that_is_not_a_directory_refuses(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            missing = (base / "nowhere").resolve()
            result = admit_control_plane_mutation(
                _layout(base), _request(missing)
            )
            self.assertIs(
                result.failure, ControlPlaneMutationFailure.REPOSITORY_UNREADABLE
            )


# ---------------------------------------------------------------------------
# Fail-closed: the record is written before `main` moves
# ---------------------------------------------------------------------------


class JournalTests(unittest.TestCase):
    def test_an_admitted_integration_leaves_the_decision_and_the_outcome(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            layout = _layout(base)
            root = _seed(base)
            head = _candidate(
                root, lambda repo: _write(repo, _TICKET, "# edited\n")
            )

            admit_control_plane_mutation(layout, _request(root))

            lines = _journal_lines(layout)
            self.assertEqual([entry["outcome"] for entry in lines], ["ADMITTED", "INTEGRATED"])
            for entry in lines:
                self.assertEqual(entry["door"], "CONTROL_PLANE")
                self.assertEqual(entry["principal"], getpass.getuser())
                self.assertEqual(entry["candidate_commit"], head)
                self.assertEqual(entry["changed_paths"], [_TICKET])
                self.assertEqual(entry["candidate_ref"], _CANDIDATE)

    def test_the_decision_is_recorded_before_main_moves(self) -> None:
        """Recorded first, not merged first: the line names the commit `main`
        is about to become, so a crash between the two is still answerable."""

        with TemporaryDirectory() as name:
            base = Path(name)
            layout = _layout(base)
            root = _seed(base)
            head = _candidate(
                root, lambda repo: _write(repo, _TICKET, "# edited\n")
            )
            observed: list[list[dict[str, object]]] = []
            original = door._git

            def watching(repository_root: Path, *arguments: str) -> bytes | None:
                if arguments and arguments[0] == "merge":
                    observed.append(_journal_lines(layout))
                return original(repository_root, *arguments)

            door._git = watching  # type: ignore[assignment]
            try:
                admit_control_plane_mutation(layout, _request(root))
            finally:
                door._git = original  # type: ignore[assignment]

            self.assertEqual(len(observed), 1)
            self.assertEqual([entry["outcome"] for entry in observed[0]], ["ADMITTED"])
            self.assertEqual(observed[0][0]["candidate_commit"], head)

    def test_a_record_that_cannot_be_written_refuses_the_integration(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            _candidate(root, lambda repo: _write(repo, _TICKET, "# edited\n"))

            result = admit_control_plane_mutation(
                _blocked_layout(base), _request(root)
            )

            self.assertIs(
                result.failure, ControlPlaneMutationFailure.JOURNAL_UNWRITABLE
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_a_refusal_names_the_path_and_the_reason(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            layout = _layout(base)
            root = _seed(base)

            def mutate(repo: Path) -> None:
                _write(repo, "library/local_orchestration/thing.py", "changed\n")
                _write(repo, _TICKET, "# edited\n")

            _candidate(root, mutate)
            admit_control_plane_mutation(layout, _request(root))

            lines = _journal_lines(layout)
            self.assertEqual(len(lines), 1)
            self.assertEqual(
                lines[0]["outcome"],
                ControlPlaneMutationFailure.RULE_AND_SUBJECT_IN_ONE_CHANGE.value,
            )
            self.assertEqual(
                lines[0]["offending_path"], "library/local_orchestration/thing.py"
            )
            self.assertEqual(lines[0]["principal"], getpass.getuser())


# ---------------------------------------------------------------------------
# The property the whole module exists for
# ---------------------------------------------------------------------------


class NoMutationOnRefusalTests(unittest.TestCase):
    """Nailed at the choke point every refusal actually passes through."""

    def _scenarios(
        self,
    ) -> tuple[tuple[str, Callable[[Path], None], str, str], ...]:
        def mixed(repo: Path) -> None:
            _write(repo, "library/local_orchestration/thing.py", "changed\n")
            _write(repo, _TICKET, "# edited\n")

        def stale_policy(repo: Path) -> None:
            _write(repo, _POLICY, "policy two\n")

        def ticket_edit(repo: Path) -> None:
            _write(repo, _TICKET, "# edited\n")

        return (
            ("mixed", mixed, _CANDIDATE, getpass.getuser()),
            ("stale-repin", stale_policy, _CANDIDATE, getpass.getuser()),
            ("wrong-door", ticket_edit, "implement/thing", getpass.getuser()),
            ("wrong-principal", ticket_edit, _CANDIDATE, "somebody-else"),
        )

    def test_no_refusal_runs_a_mutating_git_verb(self) -> None:
        for label, mutate, candidate_ref, principal in self._scenarios():
            with self.subTest(scenario=label), TemporaryDirectory() as name:
                base = Path(name)
                root = _seed(base)
                _candidate(root, mutate, name=candidate_ref)
                before = _run(root, "rev-parse", "HEAD")
                verbs: list[str] = []
                original = door._git

                def recording(
                    repository_root: Path, *arguments: str
                ) -> bytes | None:
                    if arguments:
                        verbs.append(arguments[0])
                    return original(repository_root, *arguments)

                door._git = recording  # type: ignore[assignment]
                try:
                    result = admit_control_plane_mutation(
                        _layout(base),
                        _request(
                            root, candidate_ref=candidate_ref, principal=principal
                        ),
                    )
                finally:
                    door._git = original  # type: ignore[assignment]

                self.assertIs(result.status, ControlPlaneMutationStatus.REFUSED)
                self.assertEqual(set(verbs) & _MUTATING_VERBS, set())
                self.assertEqual(_run(root, "rev-parse", "HEAD"), before)


# ---------------------------------------------------------------------------
# The two doors are not interchangeable
# ---------------------------------------------------------------------------


class DoorSeparationTests(unittest.TestCase):
    def test_the_implementer_door_will_not_read_a_control_plane_request(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            _candidate(root, lambda repo: _write(repo, _TICKET, "# edited\n"))

            result = admit_document_mutation(
                _layout(base), _request(root)  # type: ignore[arg-type]
            )

            self.assertIs(result.status, DocumentMutationStatus.REFUSED)
            self.assertIs(result.failure, DocumentMutationFailure.REQUEST_INVALID)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_this_door_will_not_read_an_implementer_request(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            _candidate(
                root,
                lambda repo: _write(repo, _TICKET, "# edited\n"),
                name="implement/thing",
            )

            result = admit_control_plane_mutation(
                _layout(base),
                DocumentMutationRequest(  # type: ignore[arg-type]
                    repository_root=str(root),
                    ticket_path=_TICKET,
                    integration_branch="main",
                    candidate_ref="implement/thing",
                ),
            )

            self.assertIs(result.failure, ControlPlaneMutationFailure.REQUEST_INVALID)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_an_implementer_candidate_cannot_enter_by_this_door(self) -> None:
        with TemporaryDirectory() as name:
            base = Path(name)
            root = _seed(base)
            before = _run(root, "rev-parse", "HEAD")
            _candidate(
                root,
                lambda repo: _write(repo, _TICKET, "# edited\n"),
                name="implement/gov-19-control-plane-gate",
            )

            result = admit_control_plane_mutation(
                _layout(base),
                _request(root, candidate_ref="implement/gov-19-control-plane-gate"),
            )

            self.assertIs(
                result.failure,
                ControlPlaneMutationFailure.CANDIDATE_NOT_CONTROL_PLANE,
            )
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)

    def test_this_door_holds_no_implementer_admission_capability(self) -> None:
        """Identity, not names: an aliased import is the family C5 bypass."""

        from library.local_orchestration import document_mutation_gate

        forbidden = {id(document_mutation_gate.admit_document_mutation)}
        held = {id(value) for value in vars(door).values()}
        self.assertEqual(forbidden & held, set())

    def test_the_implementer_door_still_admits_a_declared_change(self) -> None:
        """Regression: ticket 19 does not change ticket 08's behaviour."""

        with TemporaryDirectory() as name:
            base = Path(name)
            root = _repository(base)
            _write(root, _TICKET, "```johnny-boundary\nmodify = doc/\n```\n")
            _write(root, "doc/existing.md", "before\n")
            _commit(root, "baseline")
            head = _candidate(
                root,
                lambda repo: _write(repo, "doc/existing.md", "after\n"),
                name="implement/thing",
            )

            result = admit_document_mutation(
                _layout(base),
                DocumentMutationRequest(
                    repository_root=str(root),
                    ticket_path=_TICKET,
                    integration_branch="main",
                    candidate_ref="implement/thing",
                ),
            )

            self.assertIs(result.status, DocumentMutationStatus.INTEGRATED)
            self.assertEqual(_run(root, "rev-parse", "HEAD"), head)


if __name__ == "__main__":
    unittest.main()
