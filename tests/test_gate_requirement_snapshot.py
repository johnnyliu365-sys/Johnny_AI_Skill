"""Behavioural tests for the requirement_snapshot script (exit codes 0/1/2/3).

Every fixture is built in a temporary directory; every expected digest is computed here from the
format definition (sorted keys, `,` and `:` separators, UTF-8, rows sorted by requirement id).
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import cast
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "johnny-project-takeover" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import requirement_snapshot  # noqa: E402

SCRIPT = _SCRIPTS / "requirement_snapshot.py"
T1 = "2026-11-04T10:00:00Z"
T2 = "2026-11-05T11:30:00Z"
HEX_A = "a" * 64
HEX_B = "b" * 64
DEFECT_LINE = re.compile(r"^([A-Z_]+) (\S.*?): (.+)$")

Row = dict[str, object]


def make_row(identifier: str, **overrides: object) -> Row:
    row: Row = {
        "requirement_id": identifier,
        "page_id": "page-1",
        "title": f"title of {identifier}",
        "type": "feature",
        "source_ref": "docs/spec.md",
        "source_sha256": HEX_A,
        "status": "active",
        "version": 1,
    }
    row.update(overrides)
    return row


def rows_of(document: dict[str, object]) -> list[dict[str, object]]:
    return cast("list[dict[str, object]]", document["rows"])


def without(row: Row, field: str) -> Row:
    clone = copy.deepcopy(row)
    del clone[field]
    return clone


def expected_digest(rows: list[Row]) -> str:
    ordered = sorted(rows, key=lambda row: str(row["requirement_id"]))
    text = json.dumps(ordered, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Env:
    """A temporary directory holding the snapshot root and the input files."""

    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="reqsnap-")
        self.dir = Path(self.tmp.name)
        self.root = self.dir / "snapshots"
        self.count = 0

    def close(self) -> None:
        self.tmp.cleanup()

    def write_input(self, rows: object, newline: str = "\n") -> Path:
        self.count += 1
        path = self.dir / f"rows{self.count}.json"
        text = json.dumps({"rows": rows}, indent=2).replace("\n", newline)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        return path

    def write_raw_input(self, data: bytes) -> Path:
        self.count += 1
        path = self.dir / f"raw{self.count}.json"
        path.write_bytes(data)
        return path

    def main(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = requirement_snapshot.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def take(self, rows: object, source: str = "src", taken_at: str = T1) -> tuple[int, str, str]:
        return self.main(
            "take", "--source", source, "--input", str(self.write_input(rows)),
            "--root", str(self.root), "--taken-at", taken_at,
        )

    def files(self, source: str = "src") -> list[str]:
        directory = self.root / source
        return sorted(entry.name for entry in directory.iterdir()) if directory.is_dir() else []

    def snapshot(self, source: str, name: str) -> Path:
        return self.root / source / name

    def tree(self) -> dict[str, bytes]:
        if not self.root.exists():
            return {}
        return {
            str(path.relative_to(self.root)): path.read_bytes()
            for path in sorted(self.root.rglob("*")) if path.is_file()
        }


class SnapshotCase(unittest.TestCase):
    def setUp(self) -> None:
        self.env = Env()
        self.addCleanup(self.env.close)

    def assert_red(self, rows: object, code: str, source: str = "src") -> str:
        """take refuses with exit 1 naming the code and leaves the store byte-identical."""
        before = self.env.tree()
        exit_code, out, err = self.env.take(rows, source=source, taken_at=T2)
        self.assertEqual(exit_code, 1, out + err)
        self.assertIn(code, [match.group(1) for line in out.splitlines() if (match := DEFECT_LINE.match(line))], out)
        self.assertEqual(self.env.tree(), before)
        return out


class NormalBehaviourTests(SnapshotCase):
    def test_take_twice_gives_v1_then_v2_and_prints_the_path(self) -> None:
        code, out, _ = self.env.take([make_row("r1")], taken_at=T1)
        self.assertEqual(code, 0, out)
        self.assertEqual(Path(out.strip()), self.env.snapshot("src", "2026-11-04-v1.json"))
        code, out, _ = self.env.take([make_row("r1"), make_row("r2")], taken_at=T2)
        self.assertEqual(code, 0, out)
        self.assertEqual(Path(out.strip()), self.env.snapshot("src", "2026-11-05-v2.json"))
        self.assertEqual(self.env.files(), ["2026-11-04-v1.json", "2026-11-05-v2.json"])

    def test_equal_rows_write_nothing_and_print_unchanged(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        before = self.env.tree()
        code, out, _ = self.env.take([make_row("r1")], taken_at=T2)
        self.assertEqual(code, 0)
        self.assertTrue(out.strip().endswith(" unchanged"), out)
        self.assertEqual(Path(out.strip().removesuffix(" unchanged")), self.env.snapshot("src", "2026-11-04-v1.json"))
        self.assertEqual(self.env.tree(), before)

    def test_only_the_latest_version_decides_unchanged(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        self.env.take([make_row("r1", title="edited")], taken_at=T2)
        code, out, _ = self.env.take([make_row("r1")], taken_at="2026-11-06T00:00:00Z")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.env.files(), ["2026-11-04-v1.json", "2026-11-05-v2.json", "2026-11-06-v3.json"])

    def test_diff_lists_added_removed_and_changed_ids(self) -> None:
        self.env.take([make_row("keep"), make_row("gone"), make_row("edit")], taken_at=T1)
        self.env.take([make_row("keep"), make_row("new"), make_row("edit", status="retired")], taken_at=T2)
        code, out, _ = self.env.main("diff", "--source", "src", "v1", "v2", "--root", str(self.env.root))
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), ["added new", "removed gone", "changed edit"])
        code, out, _ = self.env.main("diff", "--source", "src", "2", "1", "--root", str(self.env.root))
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), ["added gone", "removed new", "changed edit"])

    def test_diff_of_identical_versions_prints_nothing(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        code, out, _ = self.env.main("diff", "--source", "src", "v1", "v1", "--root", str(self.env.root))
        self.assertEqual((code, out), (0, ""))

    def test_verify_passes_on_every_version(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        self.env.take([make_row("r1"), make_row("r2")], taken_at=T2)
        for name in self.env.files():
            code, out, err = self.env.main("verify", str(self.env.snapshot("src", name)))
            self.assertEqual(code, 0, out + err)

    def test_an_empty_rows_list_is_a_valid_version(self) -> None:
        code, out, _ = self.env.take([], taken_at=T1)
        self.assertEqual(code, 0, out)
        path = self.env.snapshot("src", "2026-11-04-v1.json")
        self.assertEqual(self.env.main("verify", str(path))[0], 0)
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["source_sha256"], expected_digest([]))

    def test_the_file_is_lf_with_a_final_lf_and_holds_the_four_fields(self) -> None:
        self.env.take([make_row("b", title="標題"), make_row("a")], taken_at=T1)
        raw = self.env.snapshot("src", "2026-11-04-v1.json").read_bytes()
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"}\n") and not raw.endswith(b"\n\n"))
        document = json.loads(raw.decode("utf-8"))
        self.assertEqual(list(document), ["source", "taken_at", "source_sha256", "rows"])
        self.assertEqual((document["source"], document["taken_at"]), ("src", T1))
        self.assertEqual([row["requirement_id"] for row in document["rows"]], ["a", "b"])
        self.assertIn("標題", raw.decode("utf-8"))

    def test_the_default_root_is_doc_requirements_snapshots_under_the_working_directory(self) -> None:
        self.assertEqual(requirement_snapshot.DEFAULT_ROOT, "doc/requirements/snapshots")
        source = self.env.write_input([make_row("r1")])
        with contextlib.chdir(self.env.dir):
            code, out, err = self.env.main("take", "--source", "src", "--input", str(source), "--taken-at", T1)
        self.assertEqual(code, 0, out + err)
        self.assertTrue((self.env.dir / "doc" / "requirements" / "snapshots" / "src" / "2026-11-04-v1.json").is_file())

    def test_the_default_taken_at_is_now_in_utc(self) -> None:
        code, out, err = self.env.main(
            "take", "--source", "src", "--input", str(self.env.write_input([])), "--root", str(self.env.root))
        self.assertEqual(code, 0, out + err)
        document = json.loads(Path(out.strip()).read_text(encoding="utf-8"))
        self.assertRegex(document["taken_at"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class DigestRegressionTests(SnapshotCase):
    def test_the_digest_is_the_canonical_json_sha256(self) -> None:
        rows = [make_row("b", title="標題"), make_row("a")]
        self.env.take(rows, taken_at=T1)
        document = json.loads(self.env.snapshot("src", "2026-11-04-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(document["source_sha256"], expected_digest(rows))

    def test_the_digest_matches_a_literal_canonical_text(self) -> None:
        row = make_row("a", title="t")
        literal = (
            '[{"page_id":"page-1","requirement_id":"a","source_ref":"docs/spec.md","source_sha256":"' + HEX_A
            + '","status":"active","title":"t","type":"feature","version":1}]'
        )
        self.env.take([row], taken_at=T1)
        document = json.loads(self.env.snapshot("src", "2026-11-04-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(document["source_sha256"], hashlib.sha256(literal.encode("utf-8")).hexdigest())

    def test_the_digest_does_not_depend_on_input_key_order_row_order_or_line_endings(self) -> None:
        rows = [make_row("a"), make_row("b", title="x")]
        reordered = [dict(reversed(list(row.items()))) for row in reversed(rows)]
        digests: list[str] = []
        for index, (variant, newline) in enumerate(((rows, "\n"), (reordered, "\n"), (rows, "\r\n"), (reordered, "\r\n"))):
            root = self.env.dir / f"root{index}"
            path = self.env.write_input(variant, newline=newline)
            code, out, err = self.env.main(
                "take", "--source", "src", "--input", str(path), "--root", str(root), "--taken-at", T1)
            self.assertEqual(code, 0, out + err)
            raw = (root / "src" / "2026-11-04-v1.json").read_bytes()
            digests.append(json.loads(raw.decode("utf-8"))["source_sha256"])
        self.assertEqual(set(digests), {expected_digest(rows)})

    def test_taken_at_is_not_part_of_the_digest(self) -> None:
        self.env.take([make_row("a")], taken_at=T1, source="one")
        self.env.take([make_row("a")], taken_at=T2, source="two")
        first = json.loads(self.env.snapshot("one", "2026-11-04-v1.json").read_text(encoding="utf-8"))
        second = json.loads(self.env.snapshot("two", "2026-11-05-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(first["source_sha256"], second["source_sha256"])
        self.assertEqual(first["source_sha256"], expected_digest([make_row("a")]))

    def test_a_different_taken_at_with_equal_rows_is_unchanged(self) -> None:
        self.env.take([make_row("a")], taken_at=T1)
        code, out, _ = self.env.take([make_row("a")], taken_at="2030-01-01T00:00:00Z")
        self.assertEqual(code, 0)
        self.assertIn("unchanged", out)
        self.assertEqual(self.env.files(), ["2026-11-04-v1.json"])


class RowDefectTests(SnapshotCase):
    def test_row_field_missing_for_every_field(self) -> None:
        for field in requirement_snapshot.ROW_FIELDS:
            with self.subTest(field=field):
                self.assert_red([without(make_row("r1"), field)], "ROW_FIELD_MISSING")

    def test_row_field_type_for_null_and_wrong_types(self) -> None:
        cases: list[tuple[str, object]] = [
            ("page_id", None), ("title", None), ("type", 3), ("source_ref", None), ("source_sha256", None),
            ("status", None), ("status", 1), ("version", None), ("version", "1"), ("version", 1.5),
            ("version", True), ("version", 0), ("version", -2), ("requirement_id", None), ("requirement_id", 7),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                self.assert_red([make_row("r1", **{field: value})], "ROW_FIELD_TYPE")

    def test_an_empty_or_blank_requirement_id_is_a_type_defect(self) -> None:
        for value in ("", " ", "\t \n"):
            with self.subTest(value=value):
                self.assert_red([make_row("r1", requirement_id=value)], "ROW_FIELD_TYPE")

    def test_an_unexpected_row_field_is_a_type_defect(self) -> None:
        self.assert_red([make_row("r1", extra="x")], "ROW_FIELD_TYPE")

    def test_a_row_that_is_not_an_object_is_a_type_defect(self) -> None:
        self.assert_red(["r1"], "ROW_FIELD_TYPE")
        self.assert_red([[1, 2]], "ROW_FIELD_TYPE")

    def test_duplicate_requirement(self) -> None:
        out = self.assert_red([make_row("r1"), make_row("r2"), make_row("r1", title="again")], "DUPLICATE_REQUIREMENT")
        self.assertIn("DUPLICATE_REQUIREMENT r1:", out)

    def test_status_unknown(self) -> None:
        for value in ("ACTIVE", "done", "", "retired "):
            with self.subTest(value=value):
                self.assert_red([make_row("r1", status=value)], "STATUS_UNKNOWN")

    def test_both_status_values_are_accepted(self) -> None:
        code, out, _ = self.env.take([make_row("r1", status="active"), make_row("r2", status="retired")])
        self.assertEqual(code, 0, out)

    def test_source_ref_absolute(self) -> None:
        for value in ("/etc/spec.md", "\\srv\\share\\spec.md", "\\\\srv\\share", "C:\\x\\spec.md", "c:/x/spec.md",
                      "C:spec.md", "file:///x/spec.md", "FILE:///x"):
            with self.subTest(value=value):
                self.assert_red([make_row("r1", source_ref=value)], "SOURCE_REF_ABSOLUTE")

    def test_urls_and_relative_paths_are_accepted_as_source_ref(self) -> None:
        rows = [
            make_row("r1", source_ref="https://example.invalid/spec#a:b"),
            make_row("r2", source_ref="doc/spec.md"),
            make_row("r3", source_ref="spec.md"),
            make_row("r4", source_ref="b/c"),
        ]
        code, out, _ = self.env.take(rows)
        self.assertEqual(code, 0, out)

    def test_digest_format(self) -> None:
        for value in (HEX_A[:63], HEX_A + "a", HEX_A.upper(), "g" + HEX_A[1:], "", " " + HEX_A[1:], HEX_A + "\n"):
            with self.subTest(value=value):
                self.assert_red([make_row("r1", source_sha256=value)], "DIGEST_FORMAT")

    def test_a_valid_digest_is_accepted(self) -> None:
        code, out, _ = self.env.take([make_row("r1", source_sha256="0123456789abcdef" * 4)])
        self.assertEqual(code, 0, out)

    def test_every_defect_is_listed_once_per_line(self) -> None:
        rows = [make_row("r1", status="x", source_sha256="zz"), make_row("r1")]
        _, out, _ = self.env.take(rows)
        codes = [match.group(1) for line in out.splitlines() if (match := DEFECT_LINE.match(line))]
        self.assertEqual(sorted(codes), ["DIGEST_FORMAT", "DUPLICATE_REQUIREMENT", "STATUS_UNKNOWN"])
        self.assertEqual(len(out.splitlines()), 3)

    def test_the_defect_codes_are_distinct_and_printed_with_subject_and_detail(self) -> None:
        values = [code.value for code in requirement_snapshot.DefectCode]
        self.assertEqual(len(values), len(set(values)))
        self.assertEqual(
            set(values),
            {"ROW_FIELD_MISSING", "ROW_FIELD_TYPE", "DUPLICATE_REQUIREMENT", "STATUS_UNKNOWN",
             "SOURCE_REF_ABSOLUTE", "DIGEST_FORMAT", "SNAPSHOT_DIGEST_MISMATCH", "NAME_INVALID"},
        )
        _, out, _ = self.env.take([make_row("r1", status="x")])
        match = DEFECT_LINE.match(out.strip())
        self.assertIsNotNone(match, out)
        assert match is not None
        self.assertEqual((match.group(1), match.group(2)), ("STATUS_UNKNOWN", "r1"))

    def test_a_defect_refusal_leaves_earlier_versions_byte_identical(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        before = self.env.tree()
        code, _, _ = self.env.take([make_row("r1", status="x")], taken_at=T2)
        self.assertEqual(code, 1)
        self.assertEqual(self.env.tree(), before)


class InputShapeTests(SnapshotCase):
    def test_input_that_is_not_json_is_a_red(self) -> None:
        for data in (b"not json", b"", b"\xff\xfe\x00", b"{'rows': []}"):
            with self.subTest(data=data):
                before = self.env.tree()
                code, out, err = self.env.main(
                    "take", "--source", "src", "--input", str(self.env.write_raw_input(data)),
                    "--root", str(self.env.root), "--taken-at", T1)
                self.assertEqual(code, 1, err)
                self.assertIn("ROW_FIELD_TYPE", out)
                self.assertEqual(self.env.tree(), before)

    def test_json_without_a_rows_list_is_a_red(self) -> None:
        for data in (b"{}", b'{"rows": null}', b'{"rows": {}}', b'{"rows": "x"}', b"[]", b"[{}]", b"3", b"null",
                     b'{"other": []}'):
            with self.subTest(data=data):
                before = self.env.tree()
                code, out, err = self.env.main(
                    "take", "--source", "src", "--input", str(self.env.write_raw_input(data)),
                    "--root", str(self.env.root), "--taken-at", T1)
                self.assertEqual(code, 1, err)
                self.assertIn("ROW_FIELD_TYPE", out)
                self.assertEqual(self.env.tree(), before)


class SourceNameTests(SnapshotCase):
    def test_name_invalid_for_unsafe_names(self) -> None:
        for name in ("..", ".", "a/b", "a\\b", "/abs", "C:\\abs", "C:abs", "", "a.", "a b", "ä", "a:b", "a*", "con",
                     "NUL.txt", "../x", "x/..", "a\n"):
            with self.subTest(name=name):
                before = self.env.tree()
                code, out, err = self.env.main(
                    "take", "--source", name, "--input", str(self.env.write_input([make_row("r1")])),
                    "--root", str(self.env.root), "--taken-at", T1)
                self.assertEqual(code, 1, err)
                self.assertIn("NAME_INVALID", out)
                self.assertEqual(self.env.tree(), before)
                self.assertFalse(self.env.root.exists() and any(self.env.root.iterdir()))

    def test_a_refused_name_never_writes_outside_the_root(self) -> None:
        self.env.main("take", "--source", "../escape", "--input", str(self.env.write_input([])),
                      "--root", str(self.env.root), "--taken-at", T1)
        self.assertFalse((self.env.dir / "escape").exists())

    def test_safe_names_are_accepted(self) -> None:
        for name in ("src", "a.b", "a-b_c", "A1", ".hidden", "v1.2"):
            with self.subTest(name=name):
                code, out, _ = self.env.take([make_row("r1")], source=name)
                self.assertEqual(code, 0, out)

    def test_a_case_variant_of_an_existing_source_is_refused_as_the_same_directory(self) -> None:
        self.env.take([make_row("r1")], source="Source")
        before = self.env.tree()
        code, out, _ = self.env.take([make_row("r2")], source="source", taken_at=T2)
        self.assertEqual(code, 1)
        self.assertIn("NAME_INVALID", out)
        self.assertEqual(self.env.tree(), before)
        code, out, _ = self.env.take([make_row("r3")], source="Source", taken_at=T2)
        self.assertEqual(code, 0, out)

    def test_diff_refuses_an_invalid_name_as_a_red(self) -> None:
        code, out, _ = self.env.main("diff", "--source", "..", "1", "2", "--root", str(self.env.root))
        self.assertEqual(code, 1)
        self.assertIn("NAME_INVALID", out)


class VerifyTests(SnapshotCase):
    def written(self, rows: list[Row] | None = None) -> tuple[Path, dict[str, object]]:
        self.env.take([make_row("r1")] if rows is None else rows, taken_at=T1)
        path = self.env.snapshot("src", "2026-11-04-v1.json")
        return path, json.loads(path.read_text(encoding="utf-8"))

    def rewrite(self, path: Path, document: object) -> None:
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")

    def verify(self, path: Path) -> tuple[int, str]:
        code, out, err = self.env.main("verify", str(path))
        return code, out + err

    def test_an_edited_row_is_a_snapshot_digest_mismatch(self) -> None:
        path, document = self.written()
        rows = document["rows"]
        assert isinstance(rows, list)
        rows[0]["title"] = "edited by hand"
        self.rewrite(path, document)
        code, out = self.verify(path)
        self.assertEqual(code, 1, out)
        self.assertIn("SNAPSHOT_DIGEST_MISMATCH", out)

    def test_a_recorded_digest_of_the_right_format_but_wrong_value_is_a_mismatch(self) -> None:
        path, document = self.written()
        document["source_sha256"] = HEX_B
        self.rewrite(path, document)
        code, out = self.verify(path)
        self.assertEqual(code, 1, out)
        self.assertIn("SNAPSHOT_DIGEST_MISMATCH", out)

    def test_a_top_level_digest_of_the_wrong_format(self) -> None:
        path, document = self.written()
        for value in (HEX_A[:63], HEX_A + "a", HEX_A.upper()):
            with self.subTest(value=value):
                document["source_sha256"] = value
                self.rewrite(path, document)
                code, out = self.verify(path)
                self.assertEqual(code, 1, out)
                self.assertIn("DIGEST_FORMAT", out)

    def test_row_defects_are_reported_by_verify(self) -> None:
        for mutate, code_name in (
            (lambda rows: rows[0].pop("title"), "ROW_FIELD_MISSING"),
            (lambda rows: rows[0].update(title=None), "ROW_FIELD_TYPE"),
            (lambda rows: rows[0].update(status="x"), "STATUS_UNKNOWN"),
            (lambda rows: rows[0].update(source_ref="/abs"), "SOURCE_REF_ABSOLUTE"),
            (lambda rows: rows[0].update(source_sha256="ZZ"), "DIGEST_FORMAT"),
            (lambda rows: rows.append(copy.deepcopy(rows[0])), "DUPLICATE_REQUIREMENT"),
        ):
            with self.subTest(code=code_name):
                path, document = self.written()
                rows = document["rows"]
                assert isinstance(rows, list)
                mutate(rows)
                self.rewrite(path, document)
                code, out = self.verify(path)
                self.assertEqual(code, 1, out)
                self.assertIn(code_name, out)
                path.unlink()

    def test_top_level_shape_defects(self) -> None:
        path, document = self.written()
        for name in ("source", "taken_at", "source_sha256", "rows"):
            with self.subTest(missing=name):
                clone = {key: value for key, value in document.items() if key != name}
                self.rewrite(path, clone)
                code, out = self.verify(path)
                self.assertEqual(code, 1, out)
                self.assertIn("ROW_FIELD_MISSING", out)
        for patch in ({"taken_at": "yesterday"}, {"taken_at": "2026-11-04T10:00:00+02:00"}, {"taken_at": 5},
                      {"rows": {}}, {"extra": 1}):
            with self.subTest(patch=patch):
                self.rewrite(path, {**document, **patch})
                code, out = self.verify(path)
                self.assertEqual(code, 1, out)
                self.assertIn("ROW_FIELD_TYPE", out)

    def test_an_invalid_source_name_inside_the_file_is_name_invalid(self) -> None:
        path, document = self.written()
        document["source"] = "../x"
        self.rewrite(path, document)
        code, out = self.verify(path)
        self.assertEqual(code, 1, out)
        self.assertIn("NAME_INVALID", out)

    def test_a_file_that_is_not_json_is_a_red(self) -> None:
        path = self.env.dir / "bad.json"
        for data in (b"", b"nope", b"\xff\xfe", b"[]"):
            path.write_bytes(data)
            code, out = self.verify(path)
            self.assertEqual(code, 1, out)
            self.assertIn("ROW_FIELD_TYPE", out)

    def test_a_crlf_copy_of_a_good_snapshot_still_verifies(self) -> None:
        path, _ = self.written()
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(self.verify(path)[0], 0)

    def test_a_file_that_cannot_be_read_is_a_tool_fault(self) -> None:
        code, out = self.verify(self.env.dir / "absent.json")
        self.assertEqual(code, 2, out)
        self.assertEqual(self.verify(self.env.dir)[0], 2)


class FaultTests(SnapshotCase):
    def test_a_root_that_cannot_be_created_is_exit_2(self) -> None:
        blocker = self.env.dir / "blocker"
        blocker.write_text("a file, not a directory", encoding="utf-8")
        code, out, err = self.env.main(
            "take", "--source", "src", "--input", str(self.env.write_input([make_row("r1")])),
            "--root", str(blocker), "--taken-at", T1)
        self.assertEqual(code, 2, out)
        self.assertEqual(out, "")
        self.assertIn("tool fault", err)

    def test_a_source_directory_that_is_a_file_is_exit_2(self) -> None:
        self.env.root.mkdir()
        (self.env.root / "src").write_text("a file", encoding="utf-8")
        code, _, _ = self.env.take([make_row("r1")])
        self.assertEqual(code, 2)

    def test_an_unreadable_input_is_exit_2(self) -> None:
        for path in (self.env.dir / "absent.json", self.env.dir):
            with self.subTest(path=path):
                code, out, err = self.env.main(
                    "take", "--source", "src", "--input", str(path), "--root", str(self.env.root), "--taken-at", T1)
                self.assertEqual(code, 2, out)
                self.assertEqual(out, "")
                self.assertEqual(self.env.tree(), {})

    def test_an_existing_target_at_write_time_is_exit_2_and_never_overwritten(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        target = self.env.snapshot("src", "2026-11-04-v1.json")
        before = target.read_bytes()
        # A stale view of the store: the version listing does not show the file that already exists.
        with mock.patch.object(requirement_snapshot, "list_versions", return_value=[]):
            code, out, err = self.env.take([make_row("r2")], taken_at=T1)
        self.assertEqual(code, 2, out + err)
        self.assertEqual(out, "")
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(self.env.files(), ["2026-11-04-v1.json"])

    def test_a_version_that_appears_while_writing_is_exit_2(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        real = requirement_snapshot.list_versions
        calls: list[int] = []

        def stale_first(directory: Path) -> list[requirement_snapshot.VersionFile]:
            calls.append(1)
            return [] if len(calls) == 1 else real(directory)

        with mock.patch.object(requirement_snapshot, "list_versions", side_effect=stale_first):
            code, _, _ = self.env.take([make_row("r2")], taken_at="2030-01-01T00:00:00Z")
        self.assertEqual(code, 2)
        self.assertEqual(self.env.files(), ["2026-11-04-v1.json"])

    def test_a_colliding_temporary_name_is_not_overwritten(self) -> None:
        directory = self.env.root / "src"
        directory.mkdir(parents=True)
        temporary = directory / ".2026-11-04-v1.json.fixed.tmp"
        temporary.write_bytes(b"sentinel")
        with mock.patch.object(requirement_snapshot.secrets, "token_hex", return_value="fixed"):
            code, _, _ = self.env.take([make_row("r1")], taken_at=T1)
        self.assertEqual(code, 2)
        self.assertEqual(temporary.read_bytes(), b"sentinel")
        self.assertFalse((directory / "2026-11-04-v1.json").exists())

    def test_a_write_failure_mid_file_leaves_no_partial_file_and_exit_2(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        before = self.env.tree()

        def half_then_fail(descriptor: int, data: bytes) -> None:
            import os
            os.write(descriptor, data[: len(data) // 2])
            raise OSError("disk full")

        with mock.patch.object(requirement_snapshot, "_write_all", side_effect=half_then_fail):
            code, out, err = self.env.take([make_row("r2")], taken_at=T2)
        self.assertEqual(code, 2, out)
        self.assertIn("disk full", err)
        self.assertEqual(self.env.tree(), before)
        self.assertEqual(self.env.files(), ["2026-11-04-v1.json"])

    def test_a_failing_publish_removes_the_temporary_file(self) -> None:
        with mock.patch.object(requirement_snapshot, "_publish_exclusive", side_effect=OSError("denied")):
            code, _, _ = self.env.take([make_row("r1")], taken_at=T1)
        self.assertEqual(code, 2)
        self.assertEqual(self.env.files(), [])

    def test_an_unexpected_error_is_exit_2_never_1(self) -> None:
        with mock.patch.object(requirement_snapshot, "rows_digest", side_effect=RuntimeError("boom")):
            code, out, err = self.env.take([make_row("r1")])
        self.assertEqual(code, 2, out)
        self.assertIn("RuntimeError", err)

    def test_diff_of_a_missing_version_is_exit_2(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        code, out, _ = self.env.main("diff", "--source", "src", "1", "9", "--root", str(self.env.root))
        self.assertEqual((code, out), (2, ""))
        code, _, _ = self.env.main("diff", "--source", "none", "1", "2", "--root", str(self.env.root))
        self.assertEqual(code, 2)

    def test_two_files_for_one_version_are_exit_2(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        twin = self.env.snapshot("src", "2026-11-09-v1.json")
        twin.write_bytes(self.env.snapshot("src", "2026-11-04-v1.json").read_bytes())
        code, _, _ = self.env.take([make_row("r2")], taken_at=T2)
        self.assertEqual(code, 2)
        code, _, _ = self.env.main("diff", "--source", "src", "1", "1", "--root", str(self.env.root))
        self.assertEqual(code, 2)

    def test_a_damaged_latest_version_refuses_take_with_exit_1(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        latest = self.env.snapshot("src", "2026-11-04-v1.json")
        latest.write_text(latest.read_text(encoding="utf-8").replace("title of r1", "tampered"), encoding="utf-8", newline="\n")
        before = self.env.tree()
        code, out, _ = self.env.take([make_row("r1", title="next")], taken_at=T2)
        self.assertEqual(code, 1)
        self.assertIn("SNAPSHOT_DIGEST_MISMATCH", out)
        self.assertEqual(self.env.tree(), before)

    def test_diff_of_a_damaged_version_is_exit_1(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        self.env.take([make_row("r2")], taken_at=T2)
        latest = self.env.snapshot("src", "2026-11-05-v2.json")
        latest.write_text(latest.read_text(encoding="utf-8").replace("title of r2", "tampered"), encoding="utf-8", newline="\n")
        code, out, _ = self.env.main("diff", "--source", "src", "1", "2", "--root", str(self.env.root))
        self.assertEqual(code, 1)
        self.assertIn("SNAPSHOT_DIGEST_MISMATCH", out)

    def test_a_red_is_never_exit_2_and_a_fault_is_never_exit_1(self) -> None:
        red, _, _ = self.env.take([make_row("r1", status="x")])
        fault, _, _ = self.env.main("verify", str(self.env.dir / "absent.json"))
        self.assertEqual((red, fault), (1, 2))


class UsageTests(SnapshotCase):
    def test_bad_arguments_are_exit_3_with_a_usage_line(self) -> None:
        good = str(self.env.write_input([]))
        cases = [
            (),
            ("bogus",),
            ("take",),
            ("take", "--source", "s"),
            ("take", "--input", good),
            ("take", "--source", "s", "--input", good, "--taken-at", "yesterday"),
            ("take", "--source", "s", "--input", good, "--taken-at", "2026-11-04T10:00:00"),
            ("take", "--source", "s", "--input", good, "--taken-at", "2026-11-04"),
            ("take", "--source", "s", "--input", good, "--taken-at", "2026-11-04T10:00:00+02:00"),
            ("take", "--source", "s", "--input", good, "--unknown", "x"),
            ("take", "--source", "s", "--source", "t", "--input", good),
            ("take", "--source", "s", "--input"),
            ("take", "--source", "s", "--input", good, "extra"),
            ("verify",),
            ("verify", "a.json", "b.json"),
            ("verify", "--root"),
            ("diff",),
            ("diff", "--source", "s"),
            ("diff", "--source", "s", "v1"),
            ("diff", "--source", "s", "v1", "v2", "v3"),
            ("diff", "--source", "s", "vx", "v2"),
            ("diff", "--source", "s", "v0", "v2"),
            ("diff", "v1", "v2"),
            ("diff", "--source", "s", "v1", "v2", "--bogus", "x"),
        ]
        for args in cases:
            with self.subTest(args=args):
                code, out, err = self.env.main(*args)
                self.assertEqual(code, 3, out + err)
                self.assertEqual(out, "")
                self.assertTrue(err.startswith("usage:"), err)

    def test_a_taken_at_with_a_zero_offset_or_fraction_is_accepted_and_normalised(self) -> None:
        for given in ("2026-11-04T10:00:00+00:00", "2026-11-04T10:00:00.250Z"):
            with self.subTest(given=given):
                root = self.env.dir / f"root-{len(given)}"
                code, out, err = self.env.main(
                    "take", "--source", "s", "--input", str(self.env.write_input([])), "--root", str(root),
                    "--taken-at", given)
                self.assertEqual(code, 0, out + err)
                document = json.loads(Path(out.strip()).read_text(encoding="utf-8"))
                self.assertEqual(document["taken_at"], "2026-11-04T10:00:00Z")


class ProcessTests(SnapshotCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-I", "-X", "utf8", str(SCRIPT), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=self.env.dir,
        )

    def test_the_script_runs_as_a_command_with_the_documented_exit_codes(self) -> None:
        good = self.env.write_input([make_row("r1")])
        bad = self.env.write_input([make_row("r1", status="x")])
        root = str(self.env.root)
        done = self.run_cli("take", "--source", "s", "--input", str(good), "--root", root, "--taken-at", T1)
        self.assertEqual(done.returncode, 0, done.stderr)
        path = done.stdout.strip()
        self.assertEqual(self.run_cli("verify", path).returncode, 0)
        refused = self.run_cli("take", "--source", "s", "--input", str(bad), "--root", root)
        self.assertEqual((refused.returncode, refused.stdout.split()[0]), (1, "STATUS_UNKNOWN"))
        self.assertEqual(self.run_cli("verify", str(self.env.dir / "absent.json")).returncode, 2)
        self.assertEqual(self.run_cli("nonsense").returncode, 3)

    def test_a_defect_line_with_an_unencodable_character_still_exits_1_under_cp950(self) -> None:
        rows = [make_row("r1", status="\u0e01")]
        path = self.env.write_input(rows)
        done = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), "take", "--source", "s", "--input", str(path),
             "--root", str(self.env.root)],
            capture_output=True, env={"PYTHONIOENCODING": "cp950", "SYSTEMROOT": "C:\\Windows"}, cwd=self.env.dir,
        )
        self.assertEqual(done.returncode, 1, done.stderr)
        self.assertIn(b"STATUS_UNKNOWN", done.stdout)

    def test_a_lone_surrogate_exits_1_as_a_command_in_take_and_verify(self) -> None:
        path = self.env.write_input([make_row("r1", title="a\ud800b")])
        taken = self.run_cli("take", "--source", "s", "--input", str(path), "--root", str(self.env.root))
        self.assertEqual((taken.returncode, taken.stdout.split()[0]), (1, "ROW_FIELD_TYPE"), taken.stderr)
        self.assertFalse(self.env.root.exists() and any(self.env.root.rglob("*")))
        good = self.run_cli(
            "take", "--source", "s", "--input", str(self.env.write_input([make_row("r1")])),
            "--root", str(self.env.root), "--taken-at", T1)
        stored = Path(good.stdout.strip())
        document: dict[str, object] = json.loads(stored.read_text(encoding="utf-8"))
        rows_of(document)[0]["title"] = "a\ud800b"
        stored.write_text(json.dumps(document), encoding="ascii", newline="\n")
        verified = self.run_cli("verify", str(stored))
        self.assertEqual((verified.returncode, verified.stdout.split()[0]), (1, "ROW_FIELD_TYPE"), verified.stderr)


TEXT_FIELDS = ("requirement_id", "page_id", "title", "type", "source_ref", "source_sha256", "status")


class TextValueTests(SnapshotCase):
    def lines(self, out: str) -> list[str]:
        return out.splitlines()

    def test_a_lone_surrogate_in_any_text_field_is_a_red_exit_1_never_a_fault(self) -> None:
        for field in TEXT_FIELDS:
            for value in ("a\ud800b", "\udc80", "x\udfff"):
                with self.subTest(field=field, value=value):
                    out = self.assert_red([make_row("r1", **{field: value})], "ROW_FIELD_TYPE")
                    for line in self.lines(out):
                        self.assertIsNotNone(DEFECT_LINE.match(line), line)
                    self.assertTrue(all(ord(character) < 0xD800 for character in out), "an escaped form is printed")

    def test_a_control_character_in_any_text_field_is_a_red(self) -> None:
        for field in TEXT_FIELDS:
            for value in ("a\nb", "a\tb", "a\x00b", "a\x1fb", "a\x7fb", "a\rb", "\n"):
                with self.subTest(field=field, value=value):
                    out = self.assert_red([make_row("r1", **{field: value})], "ROW_FIELD_TYPE")
                    for line in self.lines(out):
                        self.assertIsNotNone(DEFECT_LINE.match(line), line)

    def test_one_text_defect_is_one_line(self) -> None:
        _, out, _ = self.env.take([make_row("r1", title="two\nlines\nCODE forged: line")])
        self.assertEqual(len(self.lines(out)), 1, out)
        self.assertTrue(out.startswith("ROW_FIELD_TYPE r1: "), out)

    def test_a_surrogate_pair_and_ordinary_unicode_are_accepted(self) -> None:
        rows = [make_row("r1", title="\U0001F600 emoji and 標題"), make_row("r2", title="😀")]
        code, out, err = self.env.take(rows)
        self.assertEqual(code, 0, out + err)
        document = json.loads(self.env.snapshot("src", "2026-11-04-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(document["source_sha256"], expected_digest(rows))

    def test_verify_reports_a_lone_surrogate_in_a_stored_file_as_a_red(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        path = self.env.snapshot("src", "2026-11-04-v1.json")
        base: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
        cases: list[tuple[str, dict[str, object]]] = []
        for field in TEXT_FIELDS:
            document = copy.deepcopy(base)
            rows_of(document)[0][field] = "a\ud800"
            cases.append((f"row {field}", document))
        document = copy.deepcopy(base)
        document["source"] = "a\ud800"
        cases.append(("source", document))
        document = copy.deepcopy(base)
        document["taken_at"] = "\ud800"
        cases.append(("taken_at", document))
        document = copy.deepcopy(base)
        rows_of(document)[0]["x\ud800"] = 1
        cases.append(("row key", document))
        document = copy.deepcopy(base)
        document["x\ud800"] = 1
        cases.append(("top key", document))
        for label, document in cases:
            with self.subTest(case=label):
                path.write_text(json.dumps(document, indent=2) + "\n", encoding="ascii", newline="\n")
                code, out, err = self.env.main("verify", str(path))
                self.assertEqual(code, 1, out + err)
                for line in self.lines(out):
                    self.assertIsNotNone(DEFECT_LINE.match(line), line)

    def test_a_lone_surrogate_in_a_stored_version_makes_take_and_diff_exit_1(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        self.env.take([make_row("r2")], taken_at=T2)
        path = self.env.snapshot("src", "2026-11-05-v2.json")
        document: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
        rows_of(document)[0]["title"] = "a\ud800"
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="ascii", newline="\n")
        code, out, err = self.env.main("diff", "--source", "src", "1", "2", "--root", str(self.env.root))
        self.assertEqual(code, 1, out + err)
        code, out, err = self.env.take([make_row("r3")], taken_at="2026-11-06T00:00:00Z")
        self.assertEqual(code, 1, out + err)


class RequirementIdTests(SnapshotCase):
    def test_the_allowed_characters_and_lengths_are_accepted(self) -> None:
        rows = [make_row(value) for value in ("REQ-001", "a.b_c:d/e-f", "x", "9", "a" * 128)]
        code, out, err = self.env.take(rows)
        self.assertEqual(code, 0, out + err)

    def test_anything_else_is_a_type_defect(self) -> None:
        for value in ("a" * 129, "a b", "é", "a#b", "a\\b", "a;b", "a,b", "a(b)", "標題", "a b", "a b", " r1", "r1 "):
            with self.subTest(value=value):
                self.assert_red([make_row(value)], "ROW_FIELD_TYPE")

    def test_an_id_with_a_newline_is_one_defect_on_one_line(self) -> None:
        _, out, _ = self.env.take([make_row("r1\nadded forged", title="t")])
        lines = out.splitlines()
        self.assertEqual(len(lines), 1, out)
        match = DEFECT_LINE.match(lines[0])
        self.assertIsNotNone(match, out)
        assert match is not None
        self.assertEqual(match.group(1), "ROW_FIELD_TYPE")
        self.assertEqual(match.group(2), repr("r1\nadded forged"))

    def test_a_plain_id_is_printed_as_it_is_and_an_odd_one_escaped(self) -> None:
        _, out, _ = self.env.take([make_row("ok-1", status="x"), make_row("a b", status="x")])
        subjects = [match.group(2) for line in out.splitlines() if (match := DEFECT_LINE.match(line))]
        self.assertEqual(subjects, ["ok-1", "'a b'", "'a b'"])
        self.assertEqual(len(out.splitlines()), 3)

    def test_a_duplicate_odd_id_is_still_one_line_each(self) -> None:
        _, out, _ = self.env.take([make_row("a\nb", title="t"), make_row("a\nb", title="t")])
        self.assertTrue(all(DEFECT_LINE.match(line) for line in out.splitlines()), out)
        self.assertIn("DUPLICATE_REQUIREMENT", out)

    def test_an_unexpected_field_name_is_escaped_on_one_line(self) -> None:
        _, out, _ = self.env.take([make_row("r1", **{"x\ny": 1})])
        self.assertEqual(len(out.splitlines()), 1, out)
        self.assertTrue(DEFECT_LINE.match(out.strip()), out)

    def test_diff_never_prints_a_forged_line_for_a_hand_edited_id(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        self.env.take([make_row("r2")], taken_at=T2)
        path = self.env.snapshot("src", "2026-11-05-v2.json")
        document: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
        rows_of(document)[0]["requirement_id"] = "r2\nadded forged"
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")
        code, out, _ = self.env.main("diff", "--source", "src", "1", "2", "--root", str(self.env.root))
        self.assertEqual(code, 1)
        self.assertFalse(any(line.startswith(("added", "removed", "changed")) for line in out.splitlines()), out)
        self.assertTrue(all(DEFECT_LINE.match(line) for line in out.splitlines()), out)

    def test_diff_prints_one_id_per_line(self) -> None:
        ids = [f"r{number}" for number in range(5)]
        self.env.take([make_row("base")], taken_at=T1)
        self.env.take([make_row("base"), *[make_row(identifier) for identifier in ids]], taken_at=T2)
        code, out, _ = self.env.main("diff", "--source", "src", "1", "2", "--root", str(self.env.root))
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), [f"added {identifier}" for identifier in ids])


class SourceRefTests(SnapshotCase):
    def test_empty_tilde_and_dot_dot_references_are_refused(self) -> None:
        for value in ("", "~", "~/x", "..", "../x", "a/../b", "a\\..\\b", "x/..", "../../..", "\\x", "/x"):
            with self.subTest(value=value):
                self.assert_red([make_row("r1", source_ref=value)], "SOURCE_REF_ABSOLUTE")

    def test_relative_paths_and_urls_with_dots_in_names_are_accepted(self) -> None:
        rows = [
            make_row("r1", source_ref="docs/a..b.md"),
            make_row("r2", source_ref="docs/.hidden/x"),
            make_row("r3", source_ref="./docs/x.md"),
            make_row("r4", source_ref="https://example.invalid/a/../b"),
            make_row("r5", source_ref="a~b"),
        ]
        code, out, err = self.env.take(rows)
        self.assertEqual(code, 0, out + err)


class DamagedVersionTests(SnapshotCase):
    def damage(self, name: str) -> None:
        path = self.env.snapshot("src", name)
        path.write_text(path.read_text(encoding="utf-8").replace("title of", "tampered"), encoding="utf-8", newline="\n")

    def test_take_and_diff_report_a_damaged_version_whenever_they_read_it(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        self.env.take([make_row("r2")], taken_at=T2)
        self.damage("2026-11-04-v1.json")
        code, out, _ = self.env.main("diff", "--source", "src", "1", "2", "--root", str(self.env.root))
        self.assertEqual(code, 1)
        self.assertIn("SNAPSHOT_DIGEST_MISMATCH", out)
        # take reads only the latest version, which is intact
        code, out, _ = self.env.take([make_row("r3")], taken_at="2026-11-06T00:00:00Z")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.env.main("verify", str(self.env.snapshot("src", "2026-11-04-v1.json")))[0], 1)


class CaseCollisionTests(SnapshotCase):
    def test_diff_refuses_a_case_variant_of_an_existing_source(self) -> None:
        self.env.take([make_row("r1")], source="Source", taken_at=T1)
        self.env.take([make_row("r2")], source="Source", taken_at=T2)
        code, out, _ = self.env.main("diff", "--source", "source", "1", "2", "--root", str(self.env.root))
        self.assertEqual(code, 1)
        self.assertIn("NAME_INVALID", out)
        self.assertNotIn("added", out)
        code, out, _ = self.env.main("diff", "--source", "Source", "1", "2", "--root", str(self.env.root))
        self.assertEqual((code, out), (0, "added r2\nremoved r1\n"))


RACE_RUNNER = """
import os, sys, time
sys.path.insert(0, sys.argv[1])
import requirement_snapshot
ready, go = sys.argv[2], sys.argv[3]
open(ready, "w").close()
while not os.path.exists(go):
    time.sleep(0.0005)
sys.exit(requirement_snapshot.main(sys.argv[4:]))
"""


class VersionClaimTests(SnapshotCase):
    def versions(self) -> list[int]:
        found = [requirement_snapshot.VERSION_FILE_PATTERN.fullmatch(name) for name in self.env.files()]
        return sorted(int(match.group(2)) for match in found if match is not None)

    def test_a_published_take_leaves_no_claim_or_temporary_file(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        self.env.take([make_row("r2")], taken_at=T2)
        self.assertEqual(self.env.files(), ["2026-11-04-v1.json", "2026-11-05-v2.json"])

    def test_a_stale_claim_is_exit_2_naming_the_claim_file_and_publishes_nothing(self) -> None:
        directory = self.env.root / "src"
        directory.mkdir(parents=True)
        (directory / ".v1.claim").write_bytes(b"left by a crash")
        code, out, err = self.env.take([make_row("r1")], taken_at=T1)
        self.assertEqual(code, 2, out)
        self.assertEqual(out, "")
        self.assertIn(".v1.claim", err)
        self.assertEqual(self.env.files(), [".v1.claim"])
        self.assertEqual((directory / ".v1.claim").read_bytes(), b"left by a crash")

    def test_a_stale_claim_of_any_number_blocks_later_takes(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        (self.env.root / "src" / ".v7.claim").write_bytes(b"")
        before = self.env.tree()
        code, out, err = self.env.take([make_row("r2")], taken_at=T2)
        self.assertEqual((code, out), (2, ""))
        self.assertIn(".v7.claim", err)
        self.assertEqual(self.env.tree(), before)

    def test_removing_the_stale_claim_lets_take_continue(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        claim = self.env.root / "src" / ".v2.claim"
        claim.write_bytes(b"")
        self.assertEqual(self.env.take([make_row("r2")], taken_at=T2)[0], 2)
        claim.unlink()
        self.assertEqual(self.env.take([make_row("r2")], taken_at=T2)[0], 0)
        self.assertEqual(self.versions(), [1, 2])

    def test_a_claim_held_by_a_writer_that_started_after_our_scan_is_exit_2(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        real = requirement_snapshot.list_versions
        calls: list[int] = []

        def scan_then_competitor_claims(directory: Path) -> list[requirement_snapshot.VersionFile]:
            calls.append(1)
            result = real(directory)
            if len(calls) == 1:
                (directory / ".v2.claim").write_bytes(b"competitor")
            return result

        with mock.patch.object(requirement_snapshot, "list_versions", side_effect=scan_then_competitor_claims):
            code, out, err = self.env.take([make_row("r2")], taken_at=T2)
        self.assertEqual((code, out), (2, ""))
        self.assertIn(".v2.claim", err)
        self.assertEqual(self.env.files(), [".v2.claim", "2026-11-04-v1.json"])
        self.assertEqual((self.env.root / "src" / ".v2.claim").read_bytes(), b"competitor")

    def test_a_version_published_between_our_scan_and_our_claim_loses_with_exit_2(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        real = requirement_snapshot.list_versions
        calls: list[int] = []
        competitor = "2026-12-01-v2.json"

        def scan_then_competitor_publishes(directory: Path) -> list[requirement_snapshot.VersionFile]:
            calls.append(1)
            result = real(directory)
            if len(calls) == 1:
                other = Env()
                try:
                    other.take([make_row("other")], taken_at="2026-12-01T00:00:00Z")
                    (directory / competitor).write_bytes(other.snapshot("src", "2026-12-01-v1.json").read_bytes())
                finally:
                    other.close()
            return result

        with mock.patch.object(requirement_snapshot, "list_versions", side_effect=scan_then_competitor_publishes):
            code, out, err = self.env.take([make_row("r2")], taken_at=T2)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("another writer", err)
        self.assertEqual(self.env.files(), ["2026-11-04-v1.json", competitor])
        self.assertEqual(self.versions(), [1, 2])

    def test_a_claim_that_cannot_be_removed_after_publishing_is_exit_2_naming_it(self) -> None:
        with mock.patch.object(requirement_snapshot, "_remove_claim", return_value=False):
            code, out, err = self.env.take([make_row("r1")], taken_at=T1)
        self.assertEqual((code, out), (2, ""))
        self.assertIn(".v1.claim", err)
        self.assertEqual(self.env.files(), [".v1.claim", "2026-11-04-v1.json"])

    def test_the_next_version_is_the_highest_plus_one_not_the_count_plus_one(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        other = Env()
        self.addCleanup(other.close)
        other.take([make_row("r3")], taken_at="2026-11-06T00:00:00Z")
        (self.env.root / "src" / "2026-11-06-v3.json").write_bytes(
            other.snapshot("src", "2026-11-06-v1.json").read_bytes())
        self.assertEqual(self.env.files(), ["2026-11-04-v1.json", "2026-11-06-v3.json"])
        code, out, err = self.env.take([make_row("r4")], taken_at="2026-11-07T00:00:00Z")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(Path(out.strip()), self.env.snapshot("src", "2026-11-07-v4.json"))
        self.assertEqual(self.versions(), [1, 3, 4])

    def test_a_single_old_version_numbered_above_one_continues_from_it(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        (self.env.root / "src" / "2026-11-04-v1.json").rename(self.env.root / "src" / "2026-11-04-v5.json")
        code, out, err = self.env.take([make_row("r2")], taken_at=T2)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.versions(), [5, 6])

    def test_two_real_processes_with_different_dates_never_publish_one_version_twice(self) -> None:
        runner = self.env.dir / "race_runner.py"
        runner.write_text(RACE_RUNNER, encoding="utf-8", newline="\n")
        trials = int(os.environ.get("REQSNAP_RACE_TRIALS", "5"))
        outcomes: dict[tuple[int, int], int] = {}
        for trial in range(trials):
            root = self.env.dir / f"race{trial}"
            base = self.env.write_input([make_row("base")])
            self.assertEqual(self.env.main(
                "take", "--source", "src", "--input", str(base), "--root", str(root), "--taken-at", T1)[0], 0)
            go = self.env.dir / f"go{trial}"
            procs: list[subprocess.Popen[str]] = []
            for number, date in enumerate(("2026-11-05T00:00:00Z", "2026-11-06T00:00:00Z")):
                rows = self.env.write_input([make_row("base"), make_row(f"writer{number}")])
                procs.append(subprocess.Popen(
                    [sys.executable, "-X", "utf8", str(runner), str(_SCRIPTS), str(self.env.dir / f"ready{trial}-{number}"),
                     str(go), "take", "--source", "src", "--input", str(rows), "--root", str(root), "--taken-at", date],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", cwd=self.env.dir))
            deadline = time.monotonic() + 60
            while not all((self.env.dir / f"ready{trial}-{number}").exists() for number in (0, 1)):
                self.assertLess(time.monotonic(), deadline, "the writers did not start")
                time.sleep(0.01)
            go.write_text("", encoding="utf-8")
            results = [(proc.wait(timeout=60), proc.stdout.read() if proc.stdout else "") for proc in procs]
            exits = tuple(sorted(code for code, _ in results))
            outcomes[exits] = outcomes.get(exits, 0) + 1
            names = sorted(entry.name for entry in (root / "src").iterdir())
            numbers = [
                int(match.group(2)) for name in names
                if (match := requirement_snapshot.VERSION_FILE_PATTERN.fullmatch(name)) is not None
            ]
            with self.subTest(trial=trial, exits=exits, names=names):
                self.assertEqual(len(numbers), len(set(numbers)), "one version number published twice")
                self.assertEqual(len(names), len(numbers), f"claim or temporary file left behind: {names}")
                self.assertTrue(all(code in (0, 2) for code in exits), exits)
                self.assertEqual(sum(1 for code in exits if code == 0), len(numbers) - 1)
                self.assertGreaterEqual(exits.count(0), 1)
                self.assertEqual(sorted(numbers), list(range(1, len(numbers) + 1)))
        self.assertEqual(sum(outcomes.values()), trials)


class EchoedDetailTests(SnapshotCase):
    """A raw value echoed in a defect detail is escaped, so one defect is one line."""

    def codes(self, out: str) -> list[str]:
        matches = [DEFECT_LINE.match(line) for line in out.splitlines()]
        self.assertTrue(all(match is not None for match in matches), out)
        return [match.group(1) for match in matches if match is not None]

    def test_a_newline_in_an_otherwise_invalid_source_ref_keeps_its_defect_on_one_line(self) -> None:
        for value in ("/abs\nROW_FIELD_MISSING r1: forged", "../x\nforged", "~\nforged", "C:\\x\nforged"):
            with self.subTest(value=value):
                _, out, _ = self.env.take([make_row("r1", source_ref=value)])
                codes = self.codes(out)
                self.assertEqual(sorted(codes), ["ROW_FIELD_TYPE", "SOURCE_REF_ABSOLUTE"], out)
                self.assertEqual(len(out.splitlines()), 2, out)
                ref_line = next(line for line in out.splitlines() if line.startswith("SOURCE_REF_ABSOLUTE "))
                self.assertIn(repr(value), ref_line)

    def test_a_newline_in_an_otherwise_invalid_source_name_keeps_its_defect_on_one_line(self) -> None:
        for name in ("../x\nforged", "a b\nNAME_INVALID source: forged", "con\nx"):
            with self.subTest(name=name):
                _, out, _ = self.env.take([make_row("r1")], source=name)
                self.assertEqual(self.codes(out), ["NAME_INVALID"], out)
                self.assertEqual(len(out.splitlines()), 1, out)
                self.assertIn(repr(name), out)
                code, out, _ = self.env.main("diff", "--source", name, "1", "2", "--root", str(self.env.root))
                self.assertEqual(code, 1, out)
                self.assertEqual(self.codes(out), ["NAME_INVALID"], out)
                self.assertEqual(len(out.splitlines()), 1, out)


class TopLevelTextTests(SnapshotCase):
    def stored(self, **patch: object) -> tuple[int, str]:
        if not self.env.files():
            self.env.take([make_row("r1")], taken_at=T1)
        path = self.env.snapshot("src", "2026-11-04-v1.json")
        document: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
        document.update(patch)
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="ascii", newline="\n")
        code, out, err = self.env.main("verify", str(path))
        return code, out + err

    def test_a_top_level_source_that_breaks_the_text_rule_is_also_row_field_type(self) -> None:
        for value in ("a\nb", "a\tb", "a\x00b", "a\x7fb", "a\ud800", "\udfff"):
            with self.subTest(value=value):
                code, out = self.stored(source=value)
                self.assertEqual(code, 1, out)
                lines = out.splitlines()
                self.assertTrue(all(DEFECT_LINE.match(line) for line in lines), out)
                self.assertEqual(
                    sorted(line.split(" ", 1)[0] for line in lines), ["NAME_INVALID", "ROW_FIELD_TYPE"], out)
                type_line = next(line for line in lines if line.startswith("ROW_FIELD_TYPE "))
                self.assertTrue(type_line.startswith("ROW_FIELD_TYPE source: field source holds a "), type_line)

    def test_a_top_level_source_sha256_that_breaks_the_text_rule_is_also_row_field_type(self) -> None:
        for value in ("a\nb", HEX_A + "\n", "x\x00", "a\ud800", "\x7f"):
            with self.subTest(value=value):
                code, out = self.stored(source_sha256=value)
                self.assertEqual(code, 1, out)
                lines = out.splitlines()
                self.assertTrue(all(DEFECT_LINE.match(line) for line in lines), out)
                self.assertEqual(
                    sorted(line.split(" ", 1)[0] for line in lines), ["DIGEST_FORMAT", "ROW_FIELD_TYPE"], out)
                type_line = next(line for line in lines if line.startswith("ROW_FIELD_TYPE "))
                self.assertTrue(
                    type_line.startswith("ROW_FIELD_TYPE source_sha256: field source_sha256 holds a "), type_line)

    def test_a_clean_top_level_value_with_a_wrong_format_adds_no_text_defect(self) -> None:
        code, out = self.stored(source_sha256="ABC")
        self.assertEqual(code, 1, out)
        self.assertEqual([line.split(" ", 1)[0] for line in out.splitlines()], ["DIGEST_FORMAT"], out)
        code, out = self.stored(source_sha256=expected_digest([make_row("r1")]), source="a b")
        self.assertEqual(code, 1, out)
        self.assertEqual([line.split(" ", 1)[0] for line in out.splitlines()], ["NAME_INVALID"], out)


class VerifyScopeTests(SnapshotCase):
    def test_verify_applies_the_name_rules_to_the_files_source_only(self) -> None:
        self.env.take([make_row("r1")], source="Source", taken_at=T1)
        self.env.take([make_row("r1")], source="other", taken_at=T1)
        path = self.env.snapshot("other", "2026-11-04-v1.json")
        document: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
        for value in ("source", "Source", "SOURCE", "other"):
            with self.subTest(source=value):
                document["source"] = value
                path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")
                code, out, err = self.env.main("verify", str(path))
                self.assertEqual(code, 0, out + err)
        document["source"] = "con"
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")
        code, out, err = self.env.main("verify", str(path))
        self.assertEqual(code, 1, out + err)
        self.assertIn("NAME_INVALID", out)

    def test_the_docstring_and_the_readme_state_the_same_scope(self) -> None:
        doc = " ".join((requirement_snapshot.__doc__ or "").split())
        readme = " ".join((_SCRIPTS / "README.md").read_text(encoding="utf-8").split())
        self.assertNotIn("applied by take, verify and diff alike", doc)
        self.assertIn("verify takes a single file and applies the name rules to the file's `source` value only", doc)
        self.assertIn("`verify` takes a single file and applies the name rules to the file's `source` value only", readme)


class JsonInputTests(SnapshotCase):
    ROW_HEAD = (
        '{"requirement_id": "r1", "page_id": "p", "title": "t", "type": "f", "source_ref": "a/b", '
        f'"source_sha256": "{HEX_A}", "status": "active"'
    )

    def raw_take(self, text: str) -> tuple[int, str, str]:
        path = self.env.write_raw_input(text.encode("utf-8"))
        return self.env.main(
            "take", "--source", "src", "--input", str(path), "--root", str(self.env.root), "--taken-at", T1)

    def test_a_repeated_key_in_a_row_or_the_top_level_is_a_type_defect_in_take(self) -> None:
        cases = {
            "row": '{"rows": [' + self.ROW_HEAD + ', "version": 1, "title": "again"}]}',
            "top": '{"rows": [' + self.ROW_HEAD + ', "version": 1}], "rows": []}',
            "nested": '{"rows": [' + self.ROW_HEAD + ', "version": {"a": 1, "a": 2}}]}',
            "empty rows twice": '{"rows": [], "rows": []}',
        }
        for label, text in cases.items():
            with self.subTest(case=label):
                before = self.env.tree()
                code, out, err = self.raw_take(text)
                self.assertEqual(code, 1, out + err)
                lines = out.splitlines()
                self.assertTrue(all(DEFECT_LINE.match(line) for line in lines), out)
                self.assertEqual({line.split(" ", 1)[0] for line in lines}, {"ROW_FIELD_TYPE"}, out)
                self.assertIn("repeated", out)
                self.assertEqual(self.env.tree(), before)

    def test_every_repeated_key_gets_one_line_and_a_repeated_odd_key_is_escaped(self) -> None:
        code, out, err = self.raw_take('{"rows": [], "rows": [], "x\\ny": 1, "x\\ny": 2, "x\\ny": 3}')
        self.assertEqual(code, 1, out + err)
        self.assertEqual(len(out.splitlines()), 2, out)
        self.assertIn(repr("x\ny"), out)

    def test_a_repeated_key_in_a_stored_file_is_a_type_defect_in_verify_take_and_diff(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        self.env.take([make_row("r2")], taken_at=T2)
        path = self.env.snapshot("src", "2026-11-05-v2.json")
        original = path.read_text(encoding="utf-8")
        damaged = original.replace('"source": "src",', '"source": "src",\n  "source": "src",', 1)
        self.assertNotEqual(damaged, original)
        path.write_text(damaged, encoding="utf-8", newline="\n")
        code, out, err = self.env.main("verify", str(path))
        self.assertEqual(code, 1, out + err)
        self.assertEqual([line.split(" ", 1)[0] for line in out.splitlines()], ["ROW_FIELD_TYPE"], out)
        code, out, err = self.env.main("diff", "--source", "src", "1", "2", "--root", str(self.env.root))
        self.assertEqual(code, 1, out + err)
        code, out, err = self.env.take([make_row("r3")], taken_at="2026-11-06T00:00:00Z")
        self.assertEqual(code, 1, out + err)
        path.write_text(original.replace('"rows": [', '"rows": [], "rows": [', 1), encoding="utf-8", newline="\n")
        code, out, err = self.env.main("verify", str(path))
        self.assertEqual(code, 1, out + err)
        self.assertIn("ROW_FIELD_TYPE", out)

    def test_distinct_keys_are_accepted(self) -> None:
        code, out, err = self.env.take([make_row("r1"), make_row("r2")])
        self.assertEqual(code, 0, out + err)


class AsciiVersionTests(SnapshotCase):
    UNICODE_DIGITS = ("\uff11", "\u0663", "\u0e51", "\u00b2")

    def test_the_file_name_pattern_matches_ascii_digits_only(self) -> None:
        pattern = requirement_snapshot.VERSION_FILE_PATTERN
        self.assertIsNotNone(pattern.fullmatch("2026-11-04-v12.json"))
        for digit in self.UNICODE_DIGITS:
            with self.subTest(digit=digit):
                self.assertIsNone(pattern.fullmatch(f"2026-11-04-v{digit}.json"))
                self.assertIsNone(pattern.fullmatch(f"202{digit}-11-04-v1.json"))
                self.assertIsNone(pattern.fullmatch(f"2026-1{digit}-04-v1.json"))

    def test_a_file_with_unicode_digits_is_not_a_version_file(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        directory = self.env.root / "src"
        stray = directory / "2026-11-05-v\uff12.json"
        stray.write_bytes((directory / "2026-11-04-v1.json").read_bytes())
        code, out, err = self.env.take([make_row("r2")], taken_at=T2)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.env.files(), ["2026-11-04-v1.json", "2026-11-05-v2.json", "2026-11-05-v\uff12.json"])
        self.assertTrue(out.strip().endswith("2026-11-05-v2.json"), out)

    def test_a_version_argument_with_unicode_digits_is_a_usage_error(self) -> None:
        for digit in self.UNICODE_DIGITS:
            for text in (digit, f"v{digit}", f"1{digit}"):
                with self.subTest(text=text):
                    code, out, err = self.env.main("diff", "--source", "src", text, "1", "--root", str(self.env.root))
                    self.assertEqual(code, 3, out + err)
                    self.assertTrue(err.startswith("usage:"), err)
        self.env.take([make_row("r1")], taken_at=T1)
        code, out, err = self.env.main("diff", "--source", "src", "v1", "1", "--root", str(self.env.root))
        self.assertEqual(code, 0, out + err)

    def test_a_claim_file_named_with_a_non_ascii_digit_does_not_block_take(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        directory = self.env.root / "src"
        for digit in self.UNICODE_DIGITS:
            with self.subTest(digit=digit):
                self.assertIsNone(requirement_snapshot.CLAIM_PATTERN.fullmatch(f".v{digit}.claim"))
        stray = directory / ".v２.claim"
        stray.write_bytes(b"not a claim")
        code, out, err = self.env.take([make_row("r2")], taken_at=T2)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(
            self.env.files(), [".v２.claim", "2026-11-04-v1.json", "2026-11-05-v2.json"])
        self.assertIsNotNone(requirement_snapshot.CLAIM_PATTERN.fullmatch(".v12.claim"))

    def test_a_version_argument_too_long_to_name_a_stored_version_does_not_exist(self) -> None:
        self.env.take([make_row("r1")], taken_at=T1)
        for text in ("1" * 4301, "v" + "9" * 5000, "0" * 5000 + "1" + "0" * 300):
            with self.subTest(length=len(text)):
                code, out, err = self.env.main("diff", "--source", "src", text, "1", "--root", str(self.env.root))
                self.assertEqual((code, out), (2, ""), err)
                self.assertIn("requested version does not exist", err)
                self.assertEqual(len(err.strip().splitlines()), 1, err)
                for raw in ("ValueError", "Traceback", "invalid literal", "Exceeds the limit"):
                    self.assertNotIn(raw, err)
        code, out, err = self.env.main("diff", "--source", "src", "1", "0", "--root", str(self.env.root))
        self.assertEqual(code, 3, out + err)
        code, out, err = self.env.main("diff", "--source", "src", "9" * 5000, "x", "--root", str(self.env.root))
        self.assertEqual(code, 3, out + err)
        code, out, err = self.env.main("diff", "--source", "src", "1" * 255, "1", "--root", str(self.env.root))
        self.assertEqual(code, 2, out + err)
        self.assertIn("does not exist", err)


if __name__ == "__main__":
    unittest.main()
