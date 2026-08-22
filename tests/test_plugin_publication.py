"""03: the pinned sha and the tree it points at are the same fact.

Ticket 02 declared what the plugin ships and pinned a commit.  Nothing joined the
two: the reviewer repinned the marketplace entry at the repository's root commit
-- three files, no skills at all -- and the whole suite stayed green, because
every proof was about the *document* rather than about the artifact.

This module closes that.  It builds the publication tree from the declaration and
nothing else, and it recomputes both sides of the pin from repository facts, so
"someone ran the publication step once" is never what the green comes from.

Three things are deliberately proved by construction rather than by inspection:

* the generator has no payload list of its own -- asserted by walking its own
  syntax tree for any string that names a payload path, and by changing the
  declaration in a scratch repository and watching the produced tree change;
* the four ways this can fail have four names, and none of them degrades into an
  empty result that a comparison would read as agreement;
* the pinned commit's tree is compared to the declaration path by path *and*
  blob by blob.

One exception exists and it is structural, not a concession.  The file that
records the pin is inside the tree the pin names, so a byte-identical copy would
have to state its own object id.  That path is bound by a stricter rule instead:
it must become byte-identical once the id it records is substituted, so the
exemption covers the pin and cannot cover anything else.
"""

from __future__ import annotations

import ast
import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final

from library.local_orchestration.plugin_publication import (
    PayloadDeclarationError,
    PinnedCommitError,
    PublicationError,
    PublicationMismatchError,
    PublicationTreeError,
    assert_commit_matches_declaration,
    compare_commit_to_declaration,
    declared_blob_ids,
    declared_payload_paths,
    is_payload_path,
    load_payload_declaration,
    materialise_publication_tree,
    pinned_plugin_source,
    repin_marketplace,
    require_existing_commit,
    tree_blob_ids,
    write_publication_commit,
)

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
_PLUGIN_MANIFEST: Final[Path] = _REPO_ROOT / ".claude-plugin" / "plugin.json"
_MARKETPLACE_MANIFEST: Final[Path] = _REPO_ROOT / ".claude-plugin" / "marketplace.json"
_GENERATOR: Final[Path] = (
    _REPO_ROOT / "library" / "local_orchestration" / "plugin_publication.py"
)

# The one path that cannot be bound by content, derived rather than spelled out.
_PIN_CARRIER: Final[str] = _MARKETPLACE_MANIFEST.relative_to(_REPO_ROOT).as_posix()

# The repository's root commit: three files, no skills, no library.  Ticket 03
# exists because pinning it left the suite green.
_ROOT_COMMIT: Final[str] = "fcb4604572e7a325b970c19303829c42226802ed"

_EXCLUDED_PROBES: Final[tuple[str, ...]] = (
    "tests/",
    "doc/",
    "modules/tickets/",
)


def _git(root: Path, *arguments: str, stdin: str | None = None) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=str(root),
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return completed.stdout


def _scratch_manifest(trees: list[str], files: list[str]) -> dict[str, object]:
    return {
        "name": "scratch-plugin",
        "version": "1.2.3",
        "author": {"name": "Scratch Owner"},
        "payload": {
            "schemaVersion": 1,
            "trees": trees,
            "files": files,
            "excludedSegments": ["__pycache__", ".git"],
            "excludedSuffixes": [".pyc"],
        },
    }


class _ScratchRepository:
    """A throwaway repository whose declaration this suite is free to rewrite.

    The real repository is read-only here on purpose: proving that the generator
    follows the declaration requires *changing* the declaration, and doing that
    to the shipped one would prove it about a payload nobody ships.
    """

    #: Laid out so that a prefix-matching implementation is caught: ``alpha`` is
    #: declared while ``alphax`` and ``alpha-old`` are not, and ``nest/keep`` is
    #: declared while ``nest/keep-out`` is not.
    LAYOUT: Final[dict[str, str]] = {
        "ROOT.md": "root document\n",
        "OUTSIDE.md": "not declared\n",
        "MARKET.json": json.dumps(
            {
                "plugins": [
                    {
                        "name": "scratch-plugin",
                        "source": {
                            "source": "url",
                            "url": "http://example.invalid/scratch.git",
                            "sha": "a" * 40,
                        },
                    }
                ]
            },
            indent=2,
        )
        + "\n",
        "alpha/one.txt": "one\n",
        "alpha/deep/two.txt": "two\n",
        "alpha/deep/skip.pyc": "binary-ish\n",
        "alpha/__pycache__/cached.txt": "cached\n",
        "alphax/impostor.txt": "impostor\n",
        "alpha-old/impostor.txt": "impostor\n",
        "beta/three.txt": "three\n",
    }

    DECLARED: Final[frozenset[str]] = frozenset(
        {"ROOT.md", "alpha/one.txt", "alpha/deep/two.txt"}
    )

    def __init__(self, root: Path) -> None:
        self.root = root
        for relative, content in self.LAYOUT.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        self.manifest = root / ".claude-plugin" / "plugin.json"
        self.declare(["alpha"], ["ROOT.md"])
        _git(root, "init", "-q")
        _git(root, "add", "-A")
        _git(
            root,
            "-c",
            "user.name=Scratch",
            "-c",
            "user.email=scratch@invalid",
            "commit",
            "-q",
            "-m",
            "development tree",
        )

    def declare(self, trees: list[str], files: list[str]) -> Path:
        self.manifest.parent.mkdir(parents=True, exist_ok=True)
        self.manifest.write_text(
            json.dumps(_scratch_manifest(trees, files), indent=2), encoding="utf-8"
        )
        return self.manifest

    def payload(self) -> dict[str, object]:
        return load_payload_declaration(self.manifest)


class DeclarationDrivenTreeTests(unittest.TestCase):
    """The declaration is the only input; the generator holds no list."""

    def test_the_generator_holds_no_payload_path_of_its_own(self) -> None:
        """A second enumeration is a second truth, so there must not be one."""

        payload = load_payload_declaration(_PLUGIN_MANIFEST)
        module = ast.parse(_GENERATOR.read_text(encoding="utf-8"))
        literals = {
            node.value
            for node in ast.walk(module)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        offenders = sorted(text for text in literals if is_payload_path(text, payload))
        self.assertEqual(offenders, [], f"the generator names payload paths: {offenders}")
        declared = set(payload["trees"]) | set(payload["files"])  # type: ignore[arg-type]
        self.assertEqual(literals & declared, set())

    def test_the_generator_cannot_guess_which_manifest_to_read(self) -> None:
        """No default manifest path means no way to read a manifest nobody named."""

        import inspect

        for function in (load_payload_declaration, write_publication_commit):
            with self.subTest(function=function.__name__):
                parameters = list(inspect.signature(function).parameters.values())
                required = [
                    parameter
                    for parameter in parameters
                    if parameter.default is inspect.Parameter.empty
                    and parameter.kind is not inspect.Parameter.KEYWORD_ONLY
                ]
                self.assertTrue(required, "the manifest is not a required argument")

    def test_the_produced_tree_is_exactly_the_declaration(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            sha = write_publication_commit(scratch.root, scratch.manifest)
            self.assertEqual(set(tree_blob_ids(scratch.root, sha)), set(scratch.DECLARED))

    def test_widening_the_declaration_widens_the_tree(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            before = set(tree_blob_ids(scratch.root, write_publication_commit(scratch.root, scratch.manifest)))
            scratch.declare(["alpha", "beta"], ["ROOT.md", "OUTSIDE.md"])
            after = set(tree_blob_ids(scratch.root, write_publication_commit(scratch.root, scratch.manifest)))
            self.assertEqual(after - before, {"beta/three.txt", "OUTSIDE.md"})

    def test_narrowing_the_declaration_narrows_the_tree(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            scratch.declare(["alpha", "beta"], ["ROOT.md", "OUTSIDE.md"])
            wide = set(tree_blob_ids(scratch.root, write_publication_commit(scratch.root, scratch.manifest)))
            scratch.declare(["alpha"], ["ROOT.md"])
            narrow = set(tree_blob_ids(scratch.root, write_publication_commit(scratch.root, scratch.manifest)))
            self.assertEqual(wide - narrow, {"beta/three.txt", "OUTSIDE.md"})
            self.assertEqual(narrow, set(scratch.DECLARED))

    def test_an_empty_declaration_is_refused_rather_than_publishing_nothing(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            scratch.manifest.write_text(
                json.dumps(_scratch_manifest([], ["ROOT.md"]), indent=2), encoding="utf-8"
            )
            with self.assertRaises(PayloadDeclarationError):
                write_publication_commit(scratch.root, scratch.manifest)

    def test_a_neighbouring_prefix_is_not_swept_in(self) -> None:
        """``alphax`` and ``alpha-old`` are not ``alpha`` (defect class 1)."""

        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            carried = set(tree_blob_ids(scratch.root, write_publication_commit(scratch.root, scratch.manifest)))
            for impostor in ("alphax/impostor.txt", "alpha-old/impostor.txt"):
                with self.subTest(path=impostor):
                    self.assertNotIn(impostor, carried)

    def test_excluded_segments_and_suffixes_do_not_reach_the_tree(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            carried = set(tree_blob_ids(scratch.root, write_publication_commit(scratch.root, scratch.manifest)))
            for excluded in ("alpha/deep/skip.pyc", "alpha/__pycache__/cached.txt"):
                with self.subTest(path=excluded):
                    self.assertNotIn(excluded, carried)

    def test_the_produced_commit_is_a_reproducible_root(self) -> None:
        """Re-running on unchanged content reproduces the id, and starts a new history."""

        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            first = write_publication_commit(scratch.root, scratch.manifest)
            second = write_publication_commit(scratch.root, scratch.manifest)
            self.assertEqual(first, second)
            parents = _git(scratch.root, "rev-list", "--parents", "-n", "1", first).split()
            self.assertEqual(parents, [first], "the publication commit carries a parent")

    def test_publishing_does_not_move_the_development_branch(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            before = _git(scratch.root, "rev-parse", "HEAD").strip()
            published = write_publication_commit(scratch.root, scratch.manifest)
            after = _git(scratch.root, "rev-parse", "HEAD").strip()
            self.assertEqual(before, after)
            self.assertNotEqual(before, published)
            still_whole = set(_git(scratch.root, "ls-tree", "-r", "--name-only", "HEAD").split())
            self.assertIn("beta/three.txt", still_whole)


class PinCarrierTests(unittest.TestCase):
    """The file that records the pin sits inside the tree the pin names.

    It cannot state its own id, so what it states instead is the whole question.
    Shipping the *previous* id would be a working pin at an older tree; shipping
    an id that resolves to nothing is the only form that fails closed.
    """

    def _publish(self, scratch: _ScratchRepository) -> tuple[str, str]:
        scratch.declare(["alpha"], ["ROOT.md", "MARKET.json"])
        sha = write_publication_commit(scratch.root, scratch.manifest, pin_carrier="MARKET.json")
        blob = tree_blob_ids(scratch.root, sha)["MARKET.json"]
        return sha, _git(scratch.root, "cat-file", "blob", blob)

    def test_the_published_copy_records_an_id_that_names_nothing(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            _sha, published = self._publish(scratch)
            recorded = json.loads(published)["plugins"][0]["source"]["sha"]
            self.assertNotEqual(recorded, "a" * 40, "the previous pin shipped as a live pin")
            self.assertEqual(recorded, "0" * 40)
            with self.assertRaises(PinnedCommitError):
                require_existing_commit(scratch.root, recorded)

    def test_the_published_copy_differs_from_the_working_copy_only_in_the_pin(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            sha, published = self._publish(scratch)
            repin_marketplace(scratch.root / "MARKET.json", sha)
            working = (scratch.root / "MARKET.json").read_text(encoding="utf-8")
            healed = published.replace("0" * 40, sha)
            self.assertEqual(healed.replace("\r\n", "\n"), working.replace("\r\n", "\n"))
            self.assertNotEqual(published, working)
            assert_commit_matches_declaration(
                scratch.root, scratch.payload(), sha, pin_carrier="MARKET.json"
            )

    def test_publishing_twice_reproduces_the_same_id(self) -> None:
        """Without this the step chases its own tail: every run repins to a new tree."""

        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            first, _ = self._publish(scratch)
            repin_marketplace(scratch.root / "MARKET.json", first)
            second = write_publication_commit(
                scratch.root, scratch.manifest, pin_carrier="MARKET.json"
            )
            self.assertEqual(first, second)

    def test_a_pin_carrier_outside_the_payload_is_refused(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw) / "repo")
            scratch.declare(["alpha"], ["ROOT.md"])
            with self.assertRaises(PayloadDeclarationError):
                write_publication_commit(
                    scratch.root, scratch.manifest, pin_carrier="MARKET.json"
                )
            with self.assertRaises(PayloadDeclarationError):
                materialise_publication_tree(
                    scratch.root, scratch.payload(), Path(raw) / "out",
                    pin_carrier="MARKET.json",
                )

    def test_the_directory_form_and_the_commit_form_are_the_same_artifact(self) -> None:
        """Two forms of one release must not differ by a live pin."""

        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw) / "repo")
            destination = Path(raw) / "out"
            scratch.declare(["alpha"], ["ROOT.md", "MARKET.json"])
            written = materialise_publication_tree(
                scratch.root, scratch.payload(), destination, pin_carrier="MARKET.json"
            )
            sha = write_publication_commit(
                scratch.root, scratch.manifest, pin_carrier="MARKET.json"
            )
            carried = tree_blob_ids(scratch.root, sha)
            self.assertEqual(set(written), set(carried))
            for path in written:
                with self.subTest(path=path):
                    published = _git(scratch.root, "cat-file", "blob", carried[path])
                    on_disk = (destination / path).read_text(encoding="utf-8")
                    self.assertEqual(
                        published.replace("\r\n", "\n"), on_disk.replace("\r\n", "\n")
                    )
            recorded = json.loads(
                (destination / "MARKET.json").read_text(encoding="utf-8")
            )["plugins"][0]["source"]["sha"]
            self.assertEqual(recorded, "0" * 40)

    def test_a_published_copy_that_kept_a_usable_pin_is_rejected(self) -> None:
        """The exemption covers the placeholder, not any content the pin slot holds."""

        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            scratch.declare(["alpha"], ["ROOT.md", "MARKET.json"])
            unneutralised = write_publication_commit(scratch.root, scratch.manifest)
            diff = compare_commit_to_declaration(
                scratch.root, scratch.payload(), unneutralised, pin_carrier="MARKET.json"
            )
            self.assertTrue(diff.is_empty, "the carrier is byte-identical, so nothing differs")
            with self.assertRaises(PublicationMismatchError) as caught:
                assert_commit_matches_declaration(
                    scratch.root,
                    scratch.payload(),
                    unneutralised,
                    pin_carrier="MARKET.json",
                )
            self.assertIn("usable pin", str(caught.exception))


class MaterialisedTreeTests(unittest.TestCase):
    """The directory form and the commit form are the same set of files."""

    def test_the_materialised_tree_matches_the_declaration_and_the_commit(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw) / "repo")
            destination = Path(raw) / "out"
            written = materialise_publication_tree(scratch.root, scratch.payload(), destination)
            self.assertEqual(set(written), set(scratch.DECLARED))
            on_disk = {
                path.relative_to(destination).as_posix()
                for path in destination.rglob("*")
                if path.is_file()
            }
            self.assertEqual(on_disk, set(scratch.DECLARED))
            sha = write_publication_commit(scratch.root, scratch.manifest)
            self.assertEqual(on_disk, set(tree_blob_ids(scratch.root, sha)))

    def test_a_non_empty_destination_is_refused(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw) / "repo")
            destination = Path(raw) / "out"
            destination.mkdir()
            (destination / "leftover.txt").write_text("stale\n", encoding="utf-8")
            with self.assertRaises(PublicationTreeError):
                materialise_publication_tree(scratch.root, scratch.payload(), destination)


class FailClosedTests(unittest.TestCase):
    """Four failures, four names, and none of them is an empty answer."""

    def test_an_absent_declaration_is_a_declaration_failure(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            with self.assertRaises(PayloadDeclarationError):
                load_payload_declaration(Path(raw) / "missing.json")

    def test_an_undecodable_declaration_is_a_declaration_failure(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            manifest = Path(raw) / "plugin.json"
            manifest.write_bytes(b"\xff\xfe not json at all \x00")
            with self.assertRaises(PayloadDeclarationError):
                load_payload_declaration(manifest)

    def test_a_declaration_naming_an_excluded_tree_is_refused_by_the_generator(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            scratch.declare(["alpha", "tests"], ["ROOT.md"])
            with self.assertRaises(PayloadDeclarationError):
                write_publication_commit(scratch.root, scratch.manifest)

    def test_a_sha_that_names_no_commit_is_its_own_failure(self) -> None:
        with self.assertRaises(PinnedCommitError):
            require_existing_commit(_REPO_ROOT, "0" * 40)

    def test_a_malformed_sha_is_a_declaration_failure_not_a_missing_commit(self) -> None:
        for malformed in ("9073ac54", "main", "v0.4.9", "9073AC54511D54157F4D5B54F32DF2C8D9206547"):
            with self.subTest(sha=malformed):
                with self.assertRaises(PayloadDeclarationError):
                    require_existing_commit(_REPO_ROOT, malformed)

    def test_an_uncomputable_tree_raises_instead_of_reading_as_empty(self) -> None:
        """An unreadable tree compared against anything would otherwise "match"."""

        with self.assertRaises(PinnedCommitError):
            tree_blob_ids(_REPO_ROOT, "0" * 40)

    def test_an_empty_tree_is_refused_rather_than_reported_as_a_match(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            empty_tree = _git(scratch.root, "hash-object", "-t", "tree", "-w", "--stdin", stdin="").strip()
            empty_commit = _git(
                scratch.root,
                "-c",
                "user.name=Scratch",
                "-c",
                "user.email=scratch@invalid",
                "commit-tree",
                empty_tree,
                "-m",
                "nothing",
            ).strip()
            with self.assertRaises(PublicationTreeError):
                tree_blob_ids(scratch.root, empty_commit)

    def test_the_four_failures_are_four_distinguishable_names(self) -> None:
        named = (
            PayloadDeclarationError,
            PublicationTreeError,
            PinnedCommitError,
            PublicationMismatchError,
        )
        self.assertEqual(len(set(named)), 4)
        for error in named:
            with self.subTest(error=error.__name__):
                self.assertTrue(issubclass(error, PublicationError))
            for other in named:
                if other is error:
                    continue
                with self.subTest(error=error.__name__, other=other.__name__):
                    self.assertFalse(issubclass(error, other))

    def test_a_difference_set_is_empty_only_when_the_trees_really_agree(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            sha = write_publication_commit(scratch.root, scratch.manifest)
            payload = scratch.payload()
            self.assertTrue(compare_commit_to_declaration(scratch.root, payload, sha).is_empty)
            (scratch.root / "alpha" / "one.txt").write_text("changed\n", encoding="utf-8")
            drifted = compare_commit_to_declaration(scratch.root, payload, sha)
            self.assertFalse(drifted.is_empty)
            self.assertEqual(drifted.differing, ("alpha/one.txt",))
            with self.assertRaises(PublicationMismatchError):
                assert_commit_matches_declaration(scratch.root, payload, sha)

    def test_a_tree_missing_one_declared_file_is_named_as_missing(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as raw:
            scratch = _ScratchRepository(Path(raw))
            sha = write_publication_commit(scratch.root, scratch.manifest)
            scratch.declare(["alpha", "beta"], ["ROOT.md"])
            diff = compare_commit_to_declaration(scratch.root, scratch.payload(), sha)
            self.assertEqual(diff.missing, ("beta/three.txt",))
            self.assertEqual(diff.extra, ())
            self.assertFalse(diff.is_empty)


class PinnedTreeBindingTests(unittest.TestCase):
    """What the committed pin actually points at, recomputed from the repository."""

    def setUp(self) -> None:
        self.payload = load_payload_declaration(_PLUGIN_MANIFEST)
        self.sha = str(pinned_plugin_source(_MARKETPLACE_MANIFEST)["sha"])

    def test_the_pinned_sha_names_a_commit_here(self) -> None:
        self.assertEqual(require_existing_commit(_REPO_ROOT, self.sha), self.sha)

    def test_the_pinned_commit_carries_exactly_the_declared_paths(self) -> None:
        """The reviewer's mutation dies here: a tree of three files is not this one."""

        diff = compare_commit_to_declaration(
            _REPO_ROOT, self.payload, self.sha, pin_carrier=_PIN_CARRIER
        )
        self.assertEqual(diff.missing, (), "declared paths the pinned commit does not carry")
        self.assertEqual(diff.extra, (), "paths the pinned commit carries but nobody declared")

    def test_the_pinned_commit_carries_the_declared_content(self) -> None:
        diff = compare_commit_to_declaration(
            _REPO_ROOT, self.payload, self.sha, pin_carrier=_PIN_CARRIER
        )
        self.assertEqual(diff.differing, (), "declared paths whose shipped content differs")

    def test_the_only_unbindable_path_is_the_one_that_records_the_pin(self) -> None:
        diff = compare_commit_to_declaration(
            _REPO_ROOT, self.payload, self.sha, pin_carrier=_PIN_CARRIER
        )
        self.assertLessEqual(set(diff.unbindable), {_PIN_CARRIER})
        self.assertIn(_PIN_CARRIER, declared_payload_paths(_REPO_ROOT, self.payload))

    def test_the_pin_and_the_tree_are_one_fact(self) -> None:
        assert_commit_matches_declaration(
            _REPO_ROOT, self.payload, self.sha, pin_carrier=_PIN_CARRIER
        )

    def test_the_pinned_commit_carries_no_development_tree(self) -> None:
        carried = tree_blob_ids(_REPO_ROOT, self.sha)
        for path in carried:
            with self.subTest(path=path):
                self.assertTrue(is_payload_path(path, self.payload))
        for probe in _EXCLUDED_PROBES:
            with self.subTest(prefix=probe):
                self.assertEqual([p for p in carried if p.startswith(probe)], [])

    def test_the_pinned_commit_carries_no_development_history(self) -> None:
        """A right tree on a wrong parent chain still hands over the whole history."""

        parents = _git(_REPO_ROOT, "rev-list", "--parents", "-n", "1", self.sha).split()
        self.assertEqual(parents, [self.sha], "the publication commit has a parent")

    def test_the_published_copy_of_the_pin_carrier_cannot_install_anything(self) -> None:
        """The shipped copy must not be a working pin at some older tree."""

        blob = tree_blob_ids(_REPO_ROOT, self.sha)[_PIN_CARRIER]
        published = json.loads(_git(_REPO_ROOT, "cat-file", "blob", blob))
        recorded = published["plugins"][0]["source"]["sha"]
        self.assertNotEqual(recorded, self.sha, "a commit cannot record its own id")
        with self.assertRaises(PinnedCommitError):
            require_existing_commit(_REPO_ROOT, recorded)

    def test_the_pinned_commit_is_smaller_than_the_development_tree(self) -> None:
        development = len(_git(_REPO_ROOT, "ls-tree", "-r", "--name-only", "HEAD").splitlines())
        self.assertLess(len(tree_blob_ids(_REPO_ROOT, self.sha)), development)

    def test_pinning_the_root_commit_is_rejected(self) -> None:
        """The reviewer's mutation, kept as a permanent case rather than a memory."""

        require_existing_commit(_REPO_ROOT, _ROOT_COMMIT)
        with self.assertRaises(PublicationMismatchError) as caught:
            assert_commit_matches_declaration(
                _REPO_ROOT, self.payload, _ROOT_COMMIT, pin_carrier=_PIN_CARRIER
            )
        self.assertIn("missing", str(caught.exception))

    def test_pinning_the_development_head_is_rejected(self) -> None:
        """Pinning the development tree ships the excluded trees; that must not pass."""

        head = _git(_REPO_ROOT, "rev-parse", "HEAD").strip()
        diff = compare_commit_to_declaration(
            _REPO_ROOT, self.payload, head, pin_carrier=_PIN_CARRIER
        )
        self.assertFalse(diff.is_empty)
        for probe in _EXCLUDED_PROBES:
            with self.subTest(prefix=probe):
                self.assertTrue(
                    [path for path in diff.extra if path.startswith(probe)],
                    f"{probe} would have shipped unnoticed",
                )
        with self.assertRaises(PublicationMismatchError):
            assert_commit_matches_declaration(
                _REPO_ROOT, self.payload, head, pin_carrier=_PIN_CARRIER
            )

    def test_the_declared_hashes_are_computed_for_every_declared_path(self) -> None:
        declared = declared_blob_ids(_REPO_ROOT, self.payload)
        self.assertEqual(set(declared), set(declared_payload_paths(_REPO_ROOT, self.payload)))
        self.assertGreater(len(declared), 0)


if __name__ == "__main__":
    unittest.main()
