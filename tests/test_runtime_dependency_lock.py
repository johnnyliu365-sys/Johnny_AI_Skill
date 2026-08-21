"""Pins the pytest dev-dependency declaration and its separation from runtime.

Governance ticket 13: pytest was not declared anywhere in the repository
(not in ``requirements-dev.txt``, not in any ``.toml``/``.cfg``/``.ini``).
Without a pinned declaration, "the whole suite is green" is an unanswerable
claim -- which pytest produced that result, and will a rebuilt environment
reproduce it?

This module locks the division of labor between the two dependency files:

- ``requirements-dev.txt`` must declare an exact-pinned pytest version
  (9.1.1, matching every existing green run in this project, including the
  0.4.7 release verification), and declare it exactly once -- a second,
  contradictory line (e.g. a stray ``pytest>=8``) must not slip past a
  first-match check.
- The interpreter actually running this suite must be the version
  ``requirements-dev.txt`` declares. The declaration alone only answers
  "which pytest is written down"; this closes the gap to "which pytest ran
  it," which is what the ticket's sign-off requires.
- ``requirements-runtime.lock`` (the lock for the shipped bundle) must never
  gain a pytest entry -- pytest is a dev-time-only tool; the Router's
  runtime venv has no pytest and needs none.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import pytest as _running_pytest


def _repository_root() -> Path:
    return Path(__file__).parents[1]


def _read_requirements_dev_lines() -> list[str]:
    path = _repository_root() / "requirements-dev.txt"
    return path.read_text(encoding="utf-8").splitlines()


# Anchors on the exact package token "pytest" followed by a comparison
# operator and a version token. Deliberately does NOT use a bare substring
# or startswith() check, so a related-but-different package name (e.g.
# "pytest-cov") can never be mistaken for the "pytest" declaration itself.
_PYTEST_LINE_PATTERN = re.compile(r"^pytest\s*(==|>=|<=|~=|!=|>|<)\s*(\S+)$")


def _find_all_pytest_declarations(lines: list[str]) -> list[tuple[str, str]]:
    """Return every live pytest declaration line, in file order.

    Blank lines and comment lines (leading ``#``, after stripping leading
    whitespace) are skipped, matching how pip parses a requirements file.
    Unlike a first-match lookup, this does not stop after one hit: it exists
    so a second, contradictory declaration (e.g. a stray ``pytest>=8``
    appended after the real ``pytest==9.1.1`` pin) is visible rather than
    silently shadowed by whichever line happens to be found first.
    """
    found: list[tuple[str, str]] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = _PYTEST_LINE_PATTERN.match(line)
        if match is not None:
            found.append((match.group(1), match.group(2)))
    return found


def _find_pytest_declaration(lines: list[str]) -> tuple[str, str] | None:
    """Return (operator, version) for the first pytest declaration line.

    Returns ``None`` when no live pytest declaration line is present. Callers
    that need to know whether *more than one* declaration exists must use
    ``_find_all_pytest_declarations`` instead -- this function's first-match
    behavior cannot detect that by itself.
    """
    declarations = _find_all_pytest_declarations(lines)
    return declarations[0] if declarations else None


class PytestDevDependencyDeclarationTests(unittest.TestCase):
    """TDD case 1 (normal) + case 2 (rule violation: range instead of pin)."""

    def test_requirements_dev_pins_pytest_to_the_project_baseline_version(self) -> None:
        declaration = _find_pytest_declaration(_read_requirements_dev_lines())
        self.assertIsNotNone(
            declaration,
            "pytest is not declared in requirements-dev.txt; every test run "
            "is on an unpinned pytest of unknown provenance.",
        )
        operator, version = declaration  # type: ignore[misc]
        self.assertEqual(
            operator,
            "==",
            "pytest must be pinned with '==', not a range operator "
            f"(found {operator!r}); a range makes 'the whole suite is "
            "green' an unanswerable claim about which pytest ran it.",
        )
        self.assertEqual(
            version,
            "9.1.1",
            "pytest must be pinned to 9.1.1, the version every existing "
            "green run in this project (including the 0.4.7 release "
            "verification) was produced by.",
        )

    def test_commented_out_or_blank_pytest_mentions_do_not_count(self) -> None:
        # Defect class #2 (null/empty/array edge cases): a comment that
        # merely mentions "pytest==9.1.1" as an example, or blank/whitespace
        # lines, must not be misread as a live declaration.
        lines = [
            "# pytest==9.1.1  (example only, not a real declaration)",
            "",
            "   ",
            "mypy==2.3.0",
        ]
        self.assertIsNone(_find_pytest_declaration(lines))

    def test_related_package_names_are_not_mistaken_for_the_pytest_pin(self) -> None:
        # A prefix-matching bug (checking startswith("pytest") instead of
        # the exact token) would let "pytest-cov==1.0.0" satisfy the pin.
        # It must not.
        lines = ["pytest-cov==1.0.0", "pytest-mock~=3.0"]
        self.assertIsNone(_find_pytest_declaration(lines))

    def test_pin_capture_is_an_exact_token_not_a_prefix_match(self) -> None:
        # Defect class #4 (token format/comparison): the captured version
        # must be the full, exact token. "9.1.1" must not be treated as
        # equal to, or a match for, "9.1.10".
        declaration = _find_pytest_declaration(["pytest==9.1.10"])
        self.assertEqual(declaration, ("==", "9.1.10"))
        self.assertNotEqual(declaration[1], "9.1.1")

    def test_exactly_one_pytest_declaration_line_is_present(self) -> None:
        # A first-match lookup would silently accept a second, contradictory
        # declaration appended later in the file (e.g. "pytest>=8" alongside
        # the real "pytest==9.1.1" pin) -- pip would then be free to resolve
        # either one, reintroducing the exact-pin-vs-range ambiguity this
        # ticket exists to close. Scan every line, not just the first hit.
        declarations = _find_all_pytest_declarations(_read_requirements_dev_lines())
        self.assertEqual(
            len(declarations),
            1,
            "requirements-dev.txt must declare pytest exactly once; found "
            f"{len(declarations)} declaration(s): {declarations!r}. A "
            "second, contradictory pytest line leaves pip free to resolve "
            "either one, which makes 'the whole suite is green' an "
            "unanswerable claim again.",
        )


class RunningPytestVersionMatchesDeclarationTests(unittest.TestCase):
    """Checks the declaration against the interpreter actually running it.

    Pinning ``requirements-dev.txt`` only answers "which pytest ran it" if
    the pytest that is *actually executing this suite right now* is the one
    the file declares. A stale venv (installed before a version bump, or
    never reinstalled from requirements-dev.txt at all) would keep this
    module's other tests green while silently running a different pytest.
    """

    def test_running_pytest_version_matches_the_declared_version(self) -> None:
        declaration = _find_pytest_declaration(_read_requirements_dev_lines())
        self.assertIsNotNone(
            declaration,
            "pytest is not declared in requirements-dev.txt; there is "
            "nothing to compare the running interpreter against.",
        )
        _, declared_version = declaration  # type: ignore[misc]
        running_version = _running_pytest.__version__
        self.assertEqual(
            running_version,
            declared_version,
            "The pytest interpreter running this suite is "
            f"{running_version!r}, but requirements-dev.txt declares "
            f"{declared_version!r}. A green run only answers 'which pytest "
            "ran it' when the two agree -- reinstall the venv from "
            "requirements-dev.txt.",
        )


class PytestRuntimeLockExclusionTests(unittest.TestCase):
    """TDD case 3 (external failure / fail-closed) + case 4 (regression)."""

    def _runtime_lock_payload(self) -> dict:
        path = _repository_root() / "requirements-runtime.lock"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_runtime_lock_never_declares_pytest(self) -> None:
        payload = self._runtime_lock_payload()
        normalized_names = {
            dependency["normalized_name"] for dependency in payload["dependencies"]
        }
        self.assertNotIn(
            "pytest",
            normalized_names,
            "pytest is a dev-time test dependency; it must never enter the "
            "shipped requirements-runtime.lock, which would bloat the "
            "bundle and widen the attack surface.",
        )

    def test_runtime_lock_dependencies_and_digest_are_unchanged_by_this_ticket(
        self,
    ) -> None:
        # Regression guard: this ticket only touches requirements-dev.txt.
        # requirements-runtime.lock and its contents must be untouched.
        payload = self._runtime_lock_payload()
        normalized_names = [
            dependency["normalized_name"] for dependency in payload["dependencies"]
        ]
        self.assertEqual(
            normalized_names,
            [
                "pydantic",
                "pydantic_core",
                "pywin32",
                "annotated_types",
                "typing_extensions",
                "typing_inspection",
            ],
        )
        self.assertEqual(
            payload["lock_digest"],
            "f31cc1ac9a4414a58d18549f1c3d6935817e5cb0fbbaac6b00847d680680efa8",
        )


if __name__ == "__main__":
    unittest.main()
