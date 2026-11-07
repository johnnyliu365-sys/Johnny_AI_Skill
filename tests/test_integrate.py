"""Behavioural tests for the merge-queue integration script (exit codes 0/1/2/3).

Every fixture is generated in a temporary directory: a bare repository is the remote, a working
clone plays the seat that writes candidates, and the configured commands are small Python scripts the
test writes. Nothing is ever pushed to a real remote. Expected values are derived from what a fixture
wrote or from what the tool printed, never copied from the script.

The ticket (revision02) demands that the review record is read at the current tip of the integration
branch and that the candidate is merged into that tip as one merge commit. A record names its candidate
by sha, so a record committed to the tip can never name a descendant of that tip; the candidate is
therefore a sibling of the record's commit, and the merge lands it. Every test of a land runs against
real git. A few tests still replace the one method that fetches the record (`Integrator._record`) to
hand the script a record text directly; none of the tests that show a land succeeding or a record being
refused for its place does so (`RealLandTests`, `AdmissionTests`).
"""
from __future__ import annotations

import atexit
import contextlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from collections.abc import Callable, Iterator, Mapping, Sequence
from pathlib import Path
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "johnny-project-takeover" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import integrate  # noqa: E402

SCRIPT = _SCRIPTS / "integrate.py"
PY = sys.executable
BRANCH = "main"
QUEUE_BRANCH = "main-queue"
QUEUE_PATH = "state/queue.json"
REVIEW = "records/r1.md"
# The shared removed-variable list: the thirteen names of the evidence gate (every GIT_CONFIG* and GIT_TEST_* name besides).
EVIDENCE_GATE_REMOVED = frozenset(
    {
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_NAMESPACE",
        "GIT_CEILING_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_PREFIX",
        "GIT_QUARANTINE_PATH",
        "GIT_REPLACE_REF_BASE",
        "GIT_GRAFT_FILE",
        "GIT_SHALLOW_FILE",
    }
)
SUBMITTER = "seat:impl/run-1"
REVIEWER = "seat:review/run-9"
LINE_SEPARATOR = chr(0x2028)
NEXT_LINE = chr(0x85)
GIT_IDENTITY = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.test",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.test",
}


def _clean_environment() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}


def git(cwd: Path, *args: str, data: bytes | None = None, check: bool = True) -> str:
    env = _clean_environment()
    env.update(GIT_IDENTITY)
    done = subprocess.run(
        ["git", "-c", "core.autocrlf=false", "-c", "commit.gpgsign=false", "-C", str(cwd), *args],
        capture_output=True,
        env=env,
        input=data,
        check=False,
    )
    if check and done.returncode != 0:
        raise AssertionError(f"git {args} failed: {done.stderr.decode('utf-8', 'replace')}")
    return done.stdout.decode("utf-8", "replace").strip()


def _force_remove(path: Path) -> None:
    def writable(function: Callable[..., object], name: str, _: object) -> None:
        os.chmod(name, stat.S_IWRITE)
        function(name)

    shutil.rmtree(path, onerror=writable)


def write_hook(path: Path, text: str) -> None:
    """Write a git hook with LF line ends and the owner's executable bit.

    Git on POSIX runs a hook only when its file is executable, and silently ignores it otherwise.
    Git for Windows runs the file whatever its mode. Every hook this file writes goes through here.
    """
    path.write_text(text, encoding="utf-8", newline="\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def record_text(
    candidate: str,
    verdict: str = "APPROVED",
    reviewer: str = REVIEWER,
    extra: str = "",
    disposition: str | None = None,
) -> str:
    text = f"# Review\n\nProse.\n\n```review-verdict\ncandidate: {candidate}\nverdict: {verdict}\nreviewer: {reviewer}\nreviewed_at: 2026-11-05\n```\n"
    if disposition is not None:
        text += (
            f"\n```convergence-disposition\ncandidate: {candidate}\nreviewer_verdict: {verdict} ({reviewer})\n"
            f"disposition: {disposition}\nrule: CodeReview section 5 rule B\ncarried:\n  - S1\n```\n"
        )
    return text + extra


class Result:
    def __init__(self, code: int, out: str, err: str) -> None:
        self.code, self.out, self.err = code, out, err

    @property
    def out_lines(self) -> list[str]:
        return self.out.splitlines()

    @property
    def codes(self) -> list[str]:
        """The first word of every printed line that is a red (the SPECS note is not one)."""
        return [line.split(" ")[0] for line in self.out_lines if not line.startswith("SPECS ")]

    @property
    def err_lines(self) -> list[str]:
        return self.err.splitlines()

    @property
    def text(self) -> str:
        return self.out + self.err


_TEMPLATES: dict[str, tuple[Path, str]] = {}


def _template(object_format: str) -> tuple[Path, str]:
    """One prepared remote and seat clone per process and object format; every rig starts as a copy of it."""
    if object_format not in _TEMPLATES:
        root = Path(tempfile.mkdtemp(prefix="integ-template-")).resolve()
        atexit.register(_force_remove, root)
        fmt = f"--object-format={object_format}"
        remote, seat = root / "remote.git", root / "seat"
        subprocess.run(["git", "init", "-q", "--bare", "-b", BRANCH, fmt, str(remote)], check=True, env=_clean_environment())
        seat.mkdir()
        subprocess.run(["git", "init", "-q", "-b", BRANCH, fmt, str(seat)], check=True, env=_clean_environment())
        for name, text in (("specs/test_a.py", "# spec a covers src/a.py\n"), ("src/a.py", "a = 1\n"), ("docs/readme.md", "docs\n")):
            (seat / name).parent.mkdir(parents=True, exist_ok=True)
            (seat / name).write_text(text, encoding="utf-8", newline="\n")
        git(seat, "add", "-A")
        git(seat, "commit", "-q", "-m", "base")
        git(seat, "push", "-q", str(remote), f"HEAD:refs/heads/{BRANCH}")
        _TEMPLATES[object_format] = (root, git(seat, "rev-parse", "HEAD"))
    return _TEMPLATES[object_format]


class Rig:
    """A bare remote, a seat clone, the configured command scripts and the control files they read."""

    def __init__(self, case: unittest.TestCase, object_format: str = "sha1") -> None:
        self.case = case
        self.root = Path(tempfile.mkdtemp(prefix="integ-test-")).resolve()
        case.addCleanup(_force_remove, self.root)
        self.tmp = self.root / "tmp"
        self.tmp.mkdir()
        self.tools = self.root / "tools"
        self.tools.mkdir()
        self.ctl = self.root / "ctl"
        self.ctl.mkdir()
        self.remote = self.root / "remote.git"
        self.seat = self.root / "seat"
        template, self.base = _template(object_format)
        shutil.copytree(template / "remote.git", self.remote)
        shutil.copytree(template / "seat", self.seat)
        self.counter = 0
        self.write_tools()
        self.config_path = self.root / "integration.json"
        self.config: dict[str, object] = {
            "remote": str(self.remote),
            "branch": BRANCH,
            "queue_path": QUEUE_PATH,
            "spec_command": [PY, str(self.tools / "spec.py")],
            "invariant_command": [PY, str(self.tools / "invariant.py")],
            "ci_status_command": [PY, str(self.tools / "ci.py"), "{sha}"],
            "timeout_seconds": 60,
        }
        self.write_config()

    # ------------------------------------------------------------------ tools

    def write_tools(self) -> None:
        runner = textwrap.dedent(
            f'''
            import json, os, subprocess, sys, time
            CTL = {str(self.ctl)!r}
            name = os.path.basename(sys.argv[0])[:-3]
            with open(os.path.join(CTL, name + ".log"), "a", encoding="utf-8") as log:
                log.write(json.dumps(sys.argv[1:]) + "\\n")
            src = os.path.join(os.getcwd(), "src", "a.py")
            with open(os.path.join(CTL, name + ".seen"), "a", encoding="utf-8") as seen:
                seen.write(json.dumps({{"cwd": os.getcwd(), "a": open(src, encoding="utf-8", newline="").read() if os.path.exists(src) else None}}) + "\\n")
            hook = os.path.join(CTL, name + ".hook")
            if os.path.exists(hook):
                for argv in json.load(open(hook, encoding="utf-8")):
                    subprocess.run(argv, check=True, capture_output=True)
            sleep = os.path.join(CTL, name + ".sleep")
            if os.path.exists(sleep):
                child = subprocess.Popen([sys.executable, "-c",
                    "import time,sys\\nwhile True:\\n    open(sys.argv[1],'a').write('x'); time.sleep(0.1)",
                    os.path.join(CTL, name + ".beat")])
                time.sleep(120)
            answer = os.path.join(CTL, name + ".answer")
            if len(sys.argv) > 1 and os.path.exists(answer + "." + sys.argv[1]):
                answer = answer + "." + sys.argv[1]
            if os.path.exists(answer):
                sys.stdout.buffer.write(open(answer, "rb").read())
            code = os.path.join(CTL, name + ".exit")
            sys.exit(int(open(code).read()) if os.path.exists(code) else 0)
            '''
        )
        for name in ("spec", "invariant", "ci"):
            (self.tools / f"{name}.py").write_text(runner, encoding="utf-8", newline="\n")

    def control(self, name: str, text: str | bytes) -> None:
        path = self.ctl / name
        if isinstance(text, bytes):
            path.write_bytes(text)
        else:
            path.write_text(text, encoding="utf-8", newline="\n")

    def calls(self, name: str) -> list[list[str]]:
        path = self.ctl / f"{name}.log"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def seen(self, name: str) -> list[dict[str, str | None]]:
        path = self.ctl / f"{name}.seen"
        if not path.exists():
            return []
        rows: list[dict[str, str | None]] = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        return rows

    def write_config(self, raw: str | bytes | None = None) -> None:
        if raw is None:
            raw = json.dumps(self.config, indent=2)
        if isinstance(raw, str):
            self.config_path.write_text(raw, encoding="utf-8", newline="\n")
        else:
            self.config_path.write_bytes(raw)

    # ------------------------------------------------------------------ seat

    def rev_seat(self, rev: str) -> str:
        return git(self.seat, "rev-parse", rev)

    def commit(self, files: Mapping[str, str | None], message: str, parent: str | None = None) -> str:
        """Commit `files` (None deletes) on top of `parent` (default HEAD of the seat) and move HEAD to it."""
        if parent is not None:
            git(self.seat, "checkout", "-q", "--detach", "--force", parent)
        for name, content in files.items():
            path = self.seat / name
            if content is None:
                path.unlink()
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
        git(self.seat, "add", "-A")
        git(self.seat, "commit", "-q", "--allow-empty", "-m", message)
        return self.rev_seat("HEAD")

    def push_seat(self, spec: str, force: bool = False) -> None:
        args = ["push", "-q"] + (["--force"] if force else []) + [str(self.remote), spec]
        git(self.seat, *args)

    def candidate(self, files: Mapping[str, str | None] | None = None, parent: str | None = None) -> str:
        """A commit on top of `parent` (default: the remote tip) published as a branch, so the remote holds it."""
        self.counter += 1
        base = parent or self.tip()
        sha = self.commit(files if files is not None else {f"src/c{self.counter}.py": f"c = {self.counter}\n"}, f"candidate {self.counter}", base)
        self.push_seat(f"{sha}:refs/heads/cand-{self.counter}")
        return sha

    def publish(self, files: Mapping[str, str | None], message: str = "publish") -> str:
        """Commit `files` on the remote tip and move the integration branch there."""
        sha = self.commit(files, message, self.tip())
        self.push_seat(f"{sha}:refs/heads/{BRANCH}")
        return sha

    def publish_record(self, candidate: str, text: str | None = None, path: str = REVIEW) -> str:
        return self.publish({path: text if text is not None else record_text(candidate)}, "record")

    # ------------------------------------------------------------------ remote

    def tip(self) -> str:
        return git(self.remote, "rev-parse", f"refs/heads/{BRANCH}")

    def queue_sha(self) -> str | None:
        out = git(self.remote, "rev-parse", "--verify", "--quiet", f"refs/heads/{QUEUE_BRANCH}", check=False)
        return out or None

    def queue_text(self) -> str | None:
        sha = self.queue_sha()
        if sha is None:
            return None
        done = subprocess.run(["git", "-C", str(self.remote), "show", f"{sha}:{QUEUE_PATH}"], capture_output=True, env=_clean_environment())
        return done.stdout.decode("utf-8") if done.returncode == 0 else None

    def entries(self) -> list[dict[str, str]]:
        text = self.queue_text()
        if text is None:
            return []
        rows: list[dict[str, str]] = json.loads(text)["entries"]
        return rows

    def entry(self, ticket: str, candidate: str | None = None) -> dict[str, str]:
        for row in self.entries():
            if row["ticket"] == ticket and (candidate is None or row["candidate"] == candidate):
                return row
        raise AssertionError(f"no entry {ticket} in {self.entries()}")

    def states(self) -> dict[str, str]:
        return {row["ticket"]: row["state"] for row in self.entries()}

    def refs(self) -> dict[str, str]:
        out = git(self.remote, "for-each-ref", "--format=%(refname) %(objectname)")
        return dict(line.split(" ") for line in out.splitlines())

    def row(self, ticket: str, candidate: str, **changes: str) -> dict[str, str]:
        fields = {
            "ticket": ticket,
            "candidate": candidate,
            "parent": self.base,
            "review": REVIEW,
            "review_candidate": candidate,
            "reviewer": REVIEWER,
            "submitter": SUBMITTER,
            "state": "QUEUED",
            "landed_sha": "",
            "reason": "",
            "clears": "",
        }
        fields.update(changes)
        return fields

    def write_queue(self, rows: Sequence[Mapping[str, str]] | None = None, raw: str | bytes | None = None) -> str:
        """Put a queue file on the queue branch as a new commit (the branch is created when it is absent)."""
        if raw is None:
            raw = json.dumps({"entries": list(rows or [])}, indent=2) + "\n"
        data = raw if isinstance(raw, bytes) else raw.encode("utf-8")
        existing = self.queue_sha()
        env = {**_clean_environment(), **GIT_IDENTITY}
        blob = subprocess.run(["git", "-C", str(self.remote), "hash-object", "-w", "--stdin"], input=data, capture_output=True, check=True, env=env).stdout.decode().strip()
        index = self.root / "queue-index"
        env["GIT_INDEX_FILE"] = str(index)
        if index.exists():
            index.unlink()
        if existing:
            subprocess.run(["git", "-C", str(self.remote), "read-tree", existing], check=True, env=env)
        line = f"100644 {blob}\t{QUEUE_PATH}\n".encode("utf-8")
        subprocess.run(["git", "-C", str(self.remote), "update-index", "--index-info"], input=line, check=True, env=env)
        tree = subprocess.run(["git", "-C", str(self.remote), "write-tree"], capture_output=True, check=True, env=env).stdout.decode().strip()
        parents = ["-p", existing] if existing else []
        commit = subprocess.run(["git", "-C", str(self.remote), "commit-tree", tree, *parents, "-m", "queue"], capture_output=True, check=True, env=env).stdout.decode().strip()
        git(self.remote, "update-ref", f"refs/heads/{QUEUE_BRANCH}", commit)
        return commit

    # ------------------------------------------------------------------ running

    def environment(self, extra: Mapping[str, str] | None = None) -> dict[str, str]:
        env = _clean_environment()
        env["TMP"] = env["TEMP"] = env["TMPDIR"] = str(self.tmp)
        env["PYTHONUTF8"] = "1"
        if extra:
            env.update(extra)
        return env

    def cli(self, *args: str, extra_env: Mapping[str, str] | None = None, path: str | None = None) -> Result:
        env = self.environment(extra_env)
        if path is not None:
            env["PATH"] = path
        done = subprocess.run([PY, str(SCRIPT), *args], capture_output=True, env=env, check=False, timeout=300)
        return Result(done.returncode, done.stdout.decode("utf-8", "replace").replace("\r\n", "\n"), done.stderr.decode("utf-8", "replace").replace("\r\n", "\n"))

    def main(self, *args: str, approving: Mapping[str, str] | None = None) -> Result:
        """Run the script in this process; `approving` maps a record path to the record text read in place of the tip's."""
        out, err = io.StringIO(), io.StringIO()
        patches: list[mock._patch[object]] = [mock.patch.object(tempfile, "tempdir", str(self.tmp))]
        if approving is not None:
            def fake(_self: integrate.Integrator, _clone: integrate.Clone, review: str) -> bytes | None:
                return approving[review].encode("utf-8") if review in approving else None

            patches.append(mock.patch.object(integrate.Integrator, "_record", fake))
        with contextlib.ExitStack() as stack:
            for patch in patches:
                stack.enter_context(patch)
            stack.enter_context(contextlib.redirect_stdout(out))
            stack.enter_context(contextlib.redirect_stderr(err))
            with mock.patch.dict(os.environ, {"PYTHONUTF8": "1"}):
                code = integrate.main(list(args))
        return Result(code, out.getvalue(), err.getvalue())

    def submit(
        self,
        ticket: str,
        candidate: str,
        review: str = REVIEW,
        submitter: str = SUBMITTER,
        clears: str | None = None,
        approving: Mapping[str, str] | None = None,
    ) -> Result:
        args = ["submit", "--config", str(self.config_path), "--ticket", ticket, "--candidate", candidate, "--review", review, "--submitter", submitter]
        if clears is not None:
            args += ["--clears", clears]
        return self.main(*args, approving=approving)

    def land(self, approving: Mapping[str, str] | None = None) -> Result:
        return self.main("land", "--config", str(self.config_path), approving=approving)

    def readback(self) -> Result:
        return self.main("readback", "--config", str(self.config_path))

    def tmp_left(self) -> list[str]:
        return sorted(os.listdir(self.tmp))

    def parents(self, sha: str) -> list[str]:
        return git(self.remote, "rev-list", "--parents", "-n", "1", sha).split()[1:]

    def assert_merge_of(self, merged: str, first: str, second: str) -> None:
        """`merged` is a commit on the remote with exactly the parents `first` (the tip read) and `second` (the candidate)."""
        self.case.assertEqual(self.parents(merged), [first, second])


class RigCase(unittest.TestCase):
    def setUp(self) -> None:
        self.rig = Rig(self)

    def assertClean(self, result: Result) -> None:
        self.assertNotIn("Traceback", result.text)
        self.assertEqual(self.rig.tmp_left(), [], "the integration clone must be removed")

    def prepare(self, ticket: str = "T1", files: Mapping[str, str | None] | None = None) -> tuple[str, dict[str, str]]:
        """A candidate on the tip and the record map that approves it."""
        candidate = self.rig.candidate(files)
        return candidate, {REVIEW: record_text(candidate)}



class NormalFlowTests(RigCase):
    def test_submit_writes_one_queued_entry_on_an_orphan_queue_branch_and_leaves_the_tip(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        tip = self.rig.tip()
        result = self.rig.submit("T1", cand)
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.assertEqual(result.out_lines, [f"QUEUED T1@{cand} parent={tip}"])
        self.assertEqual(self.rig.entry("T1"), self.rig.row("T1", cand, parent=tip))
        self.assertEqual(self.rig.tip(), tip)
        queue = self.rig.queue_sha()
        assert queue is not None
        self.assertEqual(git(self.rig.remote, "rev-list", "--parents", "-n", "1", queue), queue)
        self.assertEqual(git(self.rig.remote, "ls-tree", "-r", "--name-only", queue), QUEUE_PATH)
        self.assertEqual(self.rig.refs()[f"refs/heads/{QUEUE_BRANCH}"], queue)
        self.assertClean(result)

    def test_a_second_submit_adds_one_commit_on_top_and_keeps_the_first_entry(self) -> None:
        first = self.rig.candidate()
        second = self.rig.candidate()
        self.rig.publish_record(first, record_text(first) + record_text(second), REVIEW)
        self.assertEqual(self.rig.submit("T1", first).code, 0)
        before = self.rig.queue_sha()
        self.assertEqual(self.rig.submit("T2", second).code, 0)
        after = self.rig.queue_sha()
        assert after is not None
        self.assertEqual(git(self.rig.remote, "rev-parse", f"{after}^"), before)
        self.assertEqual([row["ticket"] for row in self.rig.entries()], ["T1", "T2"])

    def test_a_submit_on_a_queue_branch_without_the_queue_file_adds_the_file_and_keeps_the_rest(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        blob = subprocess.run(["git", "-C", str(self.rig.remote), "hash-object", "-w", "--stdin"], input=b"keep\n", capture_output=True, check=True).stdout.decode().strip()
        tree = subprocess.run(["git", "-C", str(self.rig.remote), "mktree"], input=f"100644 blob {blob}\tNOTES.txt\n".encode(), capture_output=True, check=True).stdout.decode().strip()
        env = {**_clean_environment(), **GIT_IDENTITY}
        commit = subprocess.run(["git", "-C", str(self.rig.remote), "commit-tree", tree, "-m", "notes"], capture_output=True, check=True, env=env).stdout.decode().strip()
        git(self.rig.remote, "update-ref", f"refs/heads/{QUEUE_BRANCH}", commit)
        result = self.rig.submit("T1", cand)
        self.assertEqual(result.code, 0, result.text)
        queue = self.rig.queue_sha()
        assert queue is not None
        self.assertEqual(sorted(git(self.rig.remote, "ls-tree", "-r", "--name-only", queue).splitlines()), sorted(["NOTES.txt", QUEUE_PATH]))
        self.assertEqual(git(self.rig.remote, "rev-parse", f"{queue}^"), commit)

    def test_land_merges_runs_specs_and_invariants_on_the_merged_tree_and_records_pending(self) -> None:
        cand, records = self.prepare(files={"src/a.py": "a = 2\n"})
        self.assertEqual(self.rig.submit("T1", cand, approving=records).code, 0)
        other_refs = {key: value for key, value in self.rig.refs().items() if key.startswith("refs/heads/cand-")}
        old_tip = self.rig.tip()
        result = self.rig.land(approving=records)
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        merged = self.rig.tip()
        self.assertEqual(result.out_lines, [f"LANDED_PENDING_CI T1@{cand} landed_sha={merged}"])
        self.rig.assert_merge_of(merged, old_tip, cand)
        entry = self.rig.entry("T1")
        self.assertEqual((entry["state"], entry["landed_sha"], entry["reason"]), ("LANDED_PENDING_CI", merged, ""))
        self.assertEqual(self.rig.calls("spec"), [["specs/test_a.py"]])
        self.assertEqual(self.rig.calls("invariant"), [[]])
        for name in ("spec", "invariant"):
            self.assertEqual([row["a"] for row in self.rig.seen(name)], ["a = 2\n"])
        self.assertEqual({key: value for key, value in self.rig.refs().items() if key.startswith("refs/heads/cand-")}, other_refs)
        self.assertClean(result)

    def test_readback_green_records_landed_and_asks_about_the_landed_sha(self) -> None:
        cand, records = self.prepare()
        self.rig.submit("T1", cand, approving=records)
        self.assertEqual(self.rig.land(approving=records).code, 0)
        landed = self.rig.tip()
        self.rig.control("ci.answer", "green\n")
        result = self.rig.readback()
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.assertEqual(self.rig.states(), {"T1": "LANDED"})
        self.assertEqual(self.rig.entry("T1")["landed_sha"], landed)
        self.assertEqual(self.rig.calls("ci"), [[landed]])
        self.assertIn(f"READBACK T1@{cand} LANDED_PENDING_CI -> LANDED", result.out_lines)
        self.assertEqual(self.rig.tip(), landed)
        self.assertClean(result)

    def test_a_convergence_disposition_record_lands_like_an_approved_one(self) -> None:
        cand = self.rig.candidate()
        records = {REVIEW: record_text(cand, verdict="CONVERGENCE_REVIEW_REQUIRED", disposition="APPROVED")}
        self.assertEqual(self.rig.submit("T1", cand, approving=records).code, 0)
        result = self.rig.land(approving=records)
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.assertEqual(self.rig.states(), {"T1": "LANDED_PENDING_CI"})

    def test_nothing_queued_is_exit_zero_and_creates_nothing(self) -> None:
        tip = self.rig.tip()
        refs = self.rig.refs()
        for run in (self.rig.land, self.rig.readback):
            result = run()
            self.assertEqual((result.code, result.err), (0, ""), result.text)
            self.assertClean(result)
        self.assertEqual((self.rig.tip(), self.rig.refs()), (tip, refs))
        self.assertIsNone(self.rig.queue_sha())

    def test_an_empty_queue_file_is_nothing_to_do(self) -> None:
        self.rig.write_queue([])
        self.assertEqual(self.rig.land().code, 0)
        self.assertEqual(self.rig.readback().code, 0)
        self.assertEqual(self.rig.entries(), [])

    def test_one_land_lands_at_most_one_entry_and_the_oldest_goes_first(self) -> None:
        first = self.rig.candidate()
        second = self.rig.candidate(parent=first)
        records = {REVIEW: record_text(first) + record_text(second)}
        self.rig.submit("T1", first, approving=records)
        self.rig.submit("T2", second, approving=records)
        self.assertEqual(self.rig.land(approving=records).code, 0)
        self.assertEqual(self.rig.states(), {"T1": "LANDED_PENDING_CI", "T2": "QUEUED"})
        landed = self.rig.tip()
        self.assertEqual(self.rig.parents(landed)[1], first)
        blocked = self.rig.land(approving=records)
        self.assertEqual(blocked.code, 1)
        self.assertEqual(self.rig.tip(), landed)

    def test_a_queue_write_never_moves_the_integration_tip(self) -> None:
        cand, records = self.prepare()
        tip = self.rig.tip()
        self.rig.submit("T1", cand, approving=records)
        self.assertEqual(self.rig.tip(), tip)
        self.rig.control("spec.exit", "1")
        self.rig.control("invariant.exit", "1")
        self.rig.land(approving=records)
        self.assertEqual(self.rig.tip(), tip)
        self.assertEqual(self.rig.states(), {"T1": "BOUNCED"})


class ReviewRecordTests(RigCase):
    """Every refusal of a record, against real git: the record is read at the tip of the integration branch."""

    def setUp(self) -> None:
        super().setUp()
        self.cand = self.rig.candidate()
        self.other = self.rig.candidate()

    def block(self, **fields: str) -> str:
        values = {"candidate": self.cand, "verdict": "APPROVED", "reviewer": REVIEWER, "reviewed_at": "2026-11-05"}
        values.update(fields)
        return "```review-verdict\n" + "".join(f"{key}: {value}\n" for key, value in values.items() if value != "<absent>") + "```\n"

    def refused(self, variants: Mapping[str, str]) -> None:
        paths = {name: f"records/{name}.md" for name in variants}
        self.rig.publish({path: variants[name] for name, path in paths.items()}, "records")
        tip = self.rig.tip()
        for name, path in paths.items():
            with self.subTest(name):
                result = self.rig.submit("T1", self.cand, review=path)
                self.assertEqual((result.code, result.err), (1, ""), result.text)
                self.assertTrue(
                    any(line.startswith(f"REVIEW_MISMATCH T1@{self.cand}: ") for line in result.out_lines),
                    result.text,
                )
                self.assertEqual(result.out_lines, [line for line in result.out_lines if line.startswith("REVIEW_MISMATCH ")])
                self.assertIsNone(self.rig.queue_sha())
                self.assertEqual(self.rig.tip(), tip)
                self.assertEqual(self.rig.tmp_left(), [])

    def test_a_record_with_no_block_for_the_candidate_is_review_mismatch(self) -> None:
        self.refused(
            {
                "prose": "# Review\n\nThe verdict is APPROVED.\n",
                "other": self.block(candidate=self.other),
                "upper": self.block(candidate=self.cand.upper()),
                "short": self.block(candidate=self.cand[:12]),
                "nested": "````\n" + self.block() + "````\n",
                "untagged": "```\ncandidate: " + self.cand + "\nverdict: APPROVED\nreviewer: " + REVIEWER + "\n```\n",
                "tilde-other": "~~~review-verdict\ncandidate: " + self.other + "\nverdict: APPROVED\nreviewer: " + REVIEWER + "\n~~~\n",
            }
        )

    def test_a_verdict_other_than_approved_is_review_mismatch(self) -> None:
        self.refused(
            {
                "changes": self.block(verdict="CHANGES_REQUESTED"),
                "blocked": self.block(verdict="BLOCKED"),
                "lower": self.block(verdict="approved"),
                "dotted": self.block(verdict="APPROVED."),
                "empty": self.block(verdict=""),
                "absent": self.block(verdict="<absent>"),
                "convergence-none": self.block(verdict="CONVERGENCE_REVIEW_REQUIRED"),
                "convergence-changes": record_text(self.cand, "CONVERGENCE_REVIEW_REQUIRED", disposition="CHANGES_REQUESTED"),
                "convergence-other-candidate": self.block(verdict="CONVERGENCE_REVIEW_REQUIRED")
                + f"```convergence-disposition\ncandidate: {self.other}\ndisposition: APPROVED\n```\n",
                "changes-with-disposition": record_text(self.cand, "CHANGES_REQUESTED", disposition="APPROVED"),
                "disposition-only": f"```convergence-disposition\ncandidate: {self.cand}\ndisposition: APPROVED\n```\n",
            }
        )

    def test_the_last_block_for_the_candidate_decides(self) -> None:
        self.refused(
            {
                "approved-then-changes": self.block() + self.block(verdict="CHANGES_REQUESTED", reviewer="seat:review/run-10"),
                "approved-then-other-candidate-then-changes": self.block() + self.block(candidate=self.other) + self.block(verdict="BLOCKED"),
            }
        )

    def test_submitter_and_reviewer_rules(self) -> None:
        self.refused(
            {
                "same-seat": self.block(reviewer=SUBMITTER),
                "submitter-reviewed-an-earlier-round": self.block(candidate=self.other, verdict="CHANGES_REQUESTED", reviewer=SUBMITTER) + self.block(),
                "submitter-reviewed-a-later-block": self.block() + self.block(candidate=self.other, reviewer=SUBMITTER),
                "submitter-in-a-malformed-block": self.block() + "```review-verdict\nreviewer: " + SUBMITTER + "\nnonsense\n```\n",
            }
        )

    def test_reviewer_identity_must_match_the_seat_format_exactly(self) -> None:
        bad = {
            "no-slash": "seat:review",
            "no-prefix": "review/run-9",
            "two-slashes": "seat:a/b/c",
            "empty-profile": "seat:/run",
            "empty-run": "seat:profile/",
            "space": "seat:a b/c",
            "upper-prefix": "SEAT:a/b",
            "plus": "seat:a+b/c",
            "unicode": "seat:café/run",
        }
        self.refused({name: self.block(reviewer=value) for name, value in bad.items()} | {"absent": self.block(reviewer="<absent>")})

    def test_a_malformed_block_for_the_candidate_is_review_mismatch(self) -> None:
        self.refused(
            {
                "repeated-verdict": self.block() .replace("verdict: APPROVED\n", "verdict: APPROVED\nverdict: APPROVED\n"),
                "repeated-candidate": self.block().replace(f"candidate: {self.cand}\n", f"candidate: {self.cand}\ncandidate: {self.other}\n"),
                "unparseable-line": self.block().replace("reviewed_at", "reviewed at"),
                "unclosed": f"```review-verdict\ncandidate: {self.cand}\nverdict: APPROVED\nreviewer: {REVIEWER}\n",
                "control": self.block(verdict="APPROVED\tx"),
                "lone-hyphen-key": self.block().replace("verdict:", "ver-dict:"),
            }
        )

    def test_a_missing_or_unreadable_record_is_review_mismatch(self) -> None:
        (self.rig.seat / "records").mkdir(parents=True, exist_ok=True)
        (self.rig.seat / "records" / "binary.md").write_bytes(b"\xff\xfe" + self.block().encode("utf-16-le"))
        self.rig.publish({"records/dir/inner.md": self.block()}, "dir")
        for name, path in (("absent", "records/none.md"), ("directory", "records/dir"), ("binary", "records/binary.md")):
            with self.subTest(name):
                result = self.rig.submit("T1", self.cand, review=path)
                self.assertEqual((result.code, result.err), (1, ""), result.text)
                self.assertIn(f"REVIEW_MISMATCH T1@{self.cand}: ", result.out)
                self.assertIsNone(self.rig.queue_sha())

    def test_a_record_that_only_the_seat_branch_holds_is_not_accepted(self) -> None:
        forged = self.rig.commit({REVIEW: self.block()}, "forged record on the seat branch", self.cand)
        self.rig.push_seat(f"{forged}:refs/heads/seat-forged")
        result = self.rig.submit("T1", self.cand)
        self.assertEqual((result.code, result.err), (1, ""), result.text)
        self.assertIn("REVIEW_MISMATCH", result.out)
        self.assertIsNone(self.rig.queue_sha())

    def test_a_record_inside_the_candidate_tree_is_not_read_either(self) -> None:
        # The candidate's own tree holds a record naming another sha; it is not the tip's record.
        inside = self.rig.candidate({REVIEW: record_text("0" * 40)})
        result = self.rig.submit("T1", inside)
        self.assertEqual(result.code, 1, result.text)
        self.assertIn("REVIEW_MISMATCH", result.out)

    def test_accepted_spellings_of_a_record(self) -> None:
        approved_then_changes = self.block(verdict="CHANGES_REQUESTED", reviewer="seat:review/run-8") + self.block()
        cases = {
            "changes-then-approved": approved_then_changes,
            "fenced-example-then-real": "````markdown\n" + self.block(verdict="CHANGES_REQUESTED") + "````\n\n" + self.block(),
            "crlf": self.block().replace("\n", "\r\n"),
            "tilde-fence": self.block().replace("```", "~~~"),
            "long-fence": self.block().replace("```", "`````"),
            "trailing-blanks": self.block().replace("APPROVED\n", "APPROVED   \n"),
            "other-block-first": self.block(candidate=self.other, verdict="CHANGES_REQUESTED", reviewer="seat:review/run-7") + self.block(),
            "convergence": record_text(self.cand, "CONVERGENCE_REVIEW_REQUIRED", disposition="APPROVED"),
        }
        self.rig.publish({f"records/{name}.md": text for name, text in cases.items()}, "records")
        for index, name in enumerate(cases):
            with self.subTest(name):
                result = self.rig.submit(f"A{index}", self.cand, review=f"records/{name}.md")
                self.assertEqual((result.code, result.err), (0, ""), result.text)
                self.assertEqual(self.rig.entry(f"A{index}")["reviewer"], REVIEWER if name != "changes-then-approved" else REVIEWER)

    def test_an_ancestor_commit_does_not_lend_its_record(self) -> None:
        # A record on the previous tip is not at the current tip.
        old = self.rig.publish_record(self.cand)
        self.rig.publish({REVIEW: None}, "record removed")
        result = self.rig.submit("T1", self.cand)
        self.assertEqual(result.code, 1, result.text)
        self.assertIn("REVIEW_MISMATCH", result.out)
        del old


class SubmitRefusalTests(RigCase):
    def test_a_key_in_any_state_is_key_exists_and_nothing_is_written(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        for state in integrate.STATES:
            with self.subTest(state):
                extra: dict[str, str] = {}
                if state in integrate.LANDED_STATES:
                    extra["landed_sha"] = cand
                if state == "BOUNCED":
                    extra["reason"] = "SPEC_RED"
                self.rig.write_queue([self.rig.row("T1", cand, state=state, **extra)])
                before = self.rig.queue_sha()
                result = self.rig.submit("T1", cand)
                self.assertEqual((result.code, result.err), (1, ""), result.text)
                self.assertEqual(result.out_lines, [f"KEY_EXISTS T1@{cand}: the key is already in the queue (any state refuses a resubmission)"])
                self.assertEqual(self.rig.queue_sha(), before)

    def test_the_same_candidate_under_another_ticket_or_another_candidate_under_the_same_ticket_is_a_new_key(self) -> None:
        first = self.rig.candidate()
        second = self.rig.candidate()
        self.rig.publish_record(first, record_text(first) + record_text(second))
        self.assertEqual(self.rig.submit("T1", first).code, 0)
        self.assertEqual(self.rig.submit("T2", first).code, 0)
        self.assertEqual(self.rig.submit("T1", second).code, 0)
        self.assertEqual([(row["ticket"], row["candidate"]) for row in self.rig.entries()], [("T1", first), ("T2", first), ("T1", second)])

    def test_every_red_is_printed_before_exit_one(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand, record_text(cand, verdict="CHANGES_REQUESTED"))
        self.rig.write_queue([self.rig.row("T1", cand, state="BOUNCED", reason="SPEC_RED")])
        result = self.rig.submit("T1", cand)
        self.assertEqual((result.code, result.err), (1, ""), result.text)
        self.assertEqual(result.codes, ["KEY_EXISTS", "REVIEW_MISMATCH"])

    def test_a_queue_that_moved_forward_between_read_and_push_is_queue_moved_and_nothing_is_written(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        first = self.rig.write_queue([])
        original = integrate.Clone.push
        racer = self.rig.write_queue

        def racing(clone: integrate.Clone, updates: Sequence[tuple[str, str, str | None]]) -> integrate.Completed:
            racer([self.rig.row("RACE", cand)])
            return original(clone, updates)

        with mock.patch.object(integrate.Clone, "push", racing):
            result = self.rig.submit("T1", cand)
        self.assertEqual((result.code, result.err), (1, ""), result.text)
        self.assertEqual(result.codes, ["QUEUE_MOVED"])
        self.assertEqual([row["ticket"] for row in self.rig.entries()], ["RACE"])
        self.assertNotEqual(self.rig.queue_sha(), first)
        self.assertEqual(self.rig.tmp_left(), [])

    def test_a_queue_that_was_rewound_between_read_and_push_loses_the_lease(self) -> None:
        # A plain push would succeed here (the new commit descends from the old one); only the lease notices.
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        older = self.rig.write_queue([])
        self.rig.write_queue([])
        original = integrate.Clone.push

        def racing(clone: integrate.Clone, updates: Sequence[tuple[str, str, str | None]]) -> integrate.Completed:
            git(self.rig.remote, "update-ref", f"refs/heads/{QUEUE_BRANCH}", older)
            return original(clone, updates)

        with mock.patch.object(integrate.Clone, "push", racing):
            result = self.rig.submit("T1", cand)
        self.assertEqual((result.code, result.err), (1, ""), result.text)
        self.assertEqual(result.codes, ["QUEUE_MOVED"])
        self.assertEqual(self.rig.queue_sha(), older)

    def test_a_queue_branch_created_between_read_and_push_loses_the_lease_on_an_absent_branch(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        original = integrate.Clone.push

        def racing(clone: integrate.Clone, updates: Sequence[tuple[str, str, str | None]]) -> integrate.Completed:
            self.rig.write_queue([])
            return original(clone, updates)

        with mock.patch.object(integrate.Clone, "push", racing):
            result = self.rig.submit("T1", cand)
        self.assertEqual((result.code, result.err), (1, ""), result.text)
        self.assertEqual(result.codes, ["QUEUE_MOVED"])
        self.assertEqual(self.rig.entries(), [])

    def test_a_push_the_remote_refuses_for_another_reason_is_a_fault_not_queue_moved(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        write_hook(self.rig.remote / "hooks" / "pre-receive", "#!/bin/sh\necho no >&2\nexit 1\n")
        result = self.rig.submit("T1", cand)
        self.assertEqual(result.code, 2, result.text)
        self.assertEqual(result.out, "")
        self.assertEqual(len(result.err_lines), 1, result.err)
        self.assertIn("git push failed", result.err)
        self.assertIsNone(self.rig.queue_sha())
        self.assertClean(result)


class LandCase(RigCase):
    def racing(self, action: Callable[[], object]) -> contextlib.AbstractContextManager[object]:
        """Run `action` once, between the reads of a run and its first push."""
        original = integrate.Clone.push
        fired: list[bool] = []

        def wrapper(clone: integrate.Clone, updates: Sequence[tuple[str, str, str | None]]) -> integrate.Completed:
            if not fired:
                fired.append(True)
                action()
            return original(clone, updates)

        return mock.patch.object(integrate.Clone, "push", wrapper)

    def queued(self, ticket: str = "T1", files: Mapping[str, str | None] | None = None, **changes: str) -> tuple[str, dict[str, str]]:
        """A candidate on the tip, written to the queue as a row (with the given changes) and the record that approves it."""
        cand = self.rig.candidate(files)
        records = {REVIEW: record_text(cand)}
        rows = self.rig.entries()
        rows.append(self.rig.row(ticket, cand, parent=self.rig.tip(), **changes))
        self.rig.write_queue(rows)
        return cand, records

    def bounced_with(self, result: Result, reason: str, ticket: str = "T1") -> dict[str, str]:
        self.assertEqual(result.code, 1, result.text)
        self.assertTrue(any(line.startswith(f"{reason} {ticket}@") for line in result.out_lines), result.text)
        entry = self.rig.entry(ticket)
        self.assertEqual((entry["state"], entry["reason"], entry["landed_sha"]), ("BOUNCED", reason, ""))
        return entry


class LandBounceTests(LandCase):
    def test_a_row_copy_of_review_candidate_that_differs_from_the_record_is_review_mismatch(self) -> None:
        other = self.rig.candidate()
        cand, records = self.queued(review_candidate=other)
        tip = self.rig.tip()
        result = self.rig.land(approving=records)
        self.bounced_with(result, "REVIEW_MISMATCH")
        self.assertEqual(self.rig.tip(), tip)
        self.assertClean(result)

    def test_a_row_copy_of_the_reviewer_that_differs_from_the_record_is_review_mismatch(self) -> None:
        cand, records = self.queued(reviewer="seat:review/run-10")
        self.bounced_with(self.rig.land(approving=records), "REVIEW_MISMATCH")
        self.assertEqual(self.rig.tip(), self.rig.base)

    def test_a_row_whose_submitter_is_the_reviewer_is_review_mismatch(self) -> None:
        cand, records = self.queued(submitter=REVIEWER)
        self.bounced_with(self.rig.land(approving=records), "REVIEW_MISMATCH")

    def test_a_submitter_who_reviewed_another_round_of_the_record_is_review_mismatch(self) -> None:
        cand, _ = self.queued()
        records = {REVIEW: record_text(cand, "CHANGES_REQUESTED", SUBMITTER).replace("candidate: " + cand, "candidate: " + "1" * 40) + record_text(cand)}
        self.bounced_with(self.rig.land(approving=records), "REVIEW_MISMATCH")

    def test_a_record_that_no_longer_approves_at_land_time_is_review_mismatch(self) -> None:
        cand, _ = self.queued()
        for name, text in (("changes", record_text(cand, "CHANGES_REQUESTED")), ("absent", "no block\n")):
            with self.subTest(name):
                self.rig.write_queue([self.rig.row("T1", cand, parent=self.rig.tip())])
                result = self.rig.land(approving={REVIEW: text})
                self.bounced_with(result, "REVIEW_MISMATCH")
                self.assertEqual(self.rig.tip(), self.rig.base)

    def test_the_record_is_read_at_the_tip_of_the_branch_at_land_time(self) -> None:
        cand, _ = self.queued()
        result = self.rig.land()
        self.bounced_with(result, "REVIEW_MISMATCH")
        self.assertEqual(self.rig.tip(), self.rig.base)

    def test_a_candidate_that_does_not_descend_from_the_tip_is_merged_not_bounced(self) -> None:
        cand, records = self.queued()
        newer = self.rig.publish({"docs/newer.md": "newer\n"})
        result = self.rig.land(approving=records)
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        merged = self.rig.tip()
        self.rig.assert_merge_of(merged, newer, cand)
        self.assertEqual(git(self.rig.remote, "show", f"{merged}:docs/newer.md"), "newer")
        self.assertEqual(git(self.rig.remote, "show", f"{merged}:src/c1.py"), "c = 1")
        self.assertEqual(self.rig.entry("T1")["landed_sha"], merged)

    def test_a_candidate_the_remote_does_not_hold_is_merge_conflict_and_no_command_runs(self) -> None:
        cand = self.rig.commit({"src/never.py": "x\n"}, "never pushed", self.rig.tip())
        self.rig.write_queue([self.rig.row("T1", cand)])
        result = self.rig.land(approving={REVIEW: record_text(cand)})
        self.bounced_with(result, "MERGE_CONFLICT")
        self.assertEqual((self.rig.calls("spec"), self.rig.calls("invariant")), ([], []))

    def test_a_candidate_that_is_the_current_tip_is_already_landed(self) -> None:
        tip = self.rig.tip()
        self.rig.write_queue([self.rig.row("T1", tip)])
        result = self.rig.land(approving={REVIEW: record_text(tip)})
        self.bounced_with(result, "ALREADY_LANDED")
        self.assertEqual(self.rig.tip(), tip)
        self.assertEqual((self.rig.calls("spec"), self.rig.calls("invariant")), ([], []))

    def test_a_candidate_contained_in_the_tip_is_already_landed_and_nothing_is_pushed(self) -> None:
        cand = self.rig.candidate()
        git(self.rig.seat, "checkout", "-q", "--detach", "--force", self.rig.tip())
        git(self.rig.seat, "merge", "-q", "--no-ff", "-m", "merge", cand)
        self.rig.push_seat(f"{self.rig.rev_seat('HEAD')}:refs/heads/{BRANCH}")
        before = self.rig.refs()
        self.rig.write_queue([self.rig.row("T1", cand)])
        result = self.rig.land(approving={REVIEW: record_text(cand)})
        self.bounced_with(result, "ALREADY_LANDED")
        after = self.rig.refs()
        self.assertEqual({k: v for k, v in after.items() if k != f"refs/heads/{QUEUE_BRANCH}"}, {k: v for k, v in before.items() if k != f"refs/heads/{QUEUE_BRANCH}"})
        self.assertEqual((self.rig.calls("spec"), self.rig.calls("invariant")), ([], []))

    def test_a_conflicting_candidate_is_merge_conflict_nothing_runs_and_the_tip_stays(self) -> None:
        cand, records = self.queued(files={"src/a.py": "a = 'candidate'\n"})
        tip = self.rig.publish({"src/a.py": "a = 'tip'\n"})
        result = self.rig.land(approving=records)
        self.bounced_with(result, "MERGE_CONFLICT")
        self.assertEqual(self.rig.tip(), tip)
        self.assertEqual((self.rig.calls("spec"), self.rig.calls("invariant")), ([], []))
        self.assertClean(result)

    def test_a_candidate_that_shares_no_history_with_the_tip_is_merge_conflict(self) -> None:
        orphan = subprocess.run(["git", "-C", str(self.rig.seat), "commit-tree", git(self.rig.seat, "rev-parse", "HEAD^{tree}"), "-m", "orphan"], capture_output=True, check=True, env={**_clean_environment(), **GIT_IDENTITY}).stdout.decode().strip()
        self.rig.push_seat(f"{orphan}:refs/heads/orphan")
        self.rig.write_queue([self.rig.row("T1", orphan)])
        result = self.rig.land(approving={REVIEW: record_text(orphan)})
        self.bounced_with(result, "MERGE_CONFLICT")
        self.assertEqual((self.rig.calls("spec"), self.rig.calls("invariant")), ([], []))

    def test_an_object_that_is_not_a_commit_is_merge_conflict(self) -> None:
        blob = git(self.rig.seat, "rev-parse", "HEAD:src/a.py")
        self.rig.write_queue([self.rig.row("T1", blob)])
        self.bounced_with(self.rig.land(approving={REVIEW: record_text(blob)}), "MERGE_CONFLICT")

    def test_the_merge_does_not_change_the_working_copy_of_the_seat_or_the_other_branches(self) -> None:
        cand, records = self.queued()
        refs = {key: value for key, value in self.rig.refs().items() if key not in (f"refs/heads/{BRANCH}", f"refs/heads/{QUEUE_BRANCH}")}
        self.assertEqual(self.rig.land(approving=records).code, 0)
        self.assertEqual({key: value for key, value in self.rig.refs().items() if key not in (f"refs/heads/{BRANCH}", f"refs/heads/{QUEUE_BRANCH}")}, refs)

    def test_every_bounce_reason_is_a_reason_the_queue_file_accepts_and_the_old_one_is_not(self) -> None:
        self.assertEqual(
            set(integrate.BOUNCE_REASONS),
            {"REVIEW_MISMATCH", "ALREADY_LANDED", "MERGE_CONFLICT", "SPEC_RED", "INVARIANT_RED", "TIP_MOVED"},
        )
        for reason in sorted(integrate.BOUNCE_REASONS):
            with self.subTest(reason):
                self.rig.write_queue([self.rig.row("T1", self.rig.base, state="BOUNCED", reason=reason)])
                result = self.rig.land()
                self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.rig.write_queue([self.rig.row("T1", self.rig.base, state="BOUNCED", reason="NOT_FAST_FORWARD")])
        result = self.rig.land()
        self.assertEqual(result.code, 2, result.text)
        self.assertIn("field reason", result.err)

    def test_a_bounce_for_each_new_reason_can_be_read_by_the_next_run(self) -> None:
        cand, records = self.queued(files={"src/a.py": "a = 'k'\n"})
        tip = self.rig.publish({"src/a.py": "a = 'tip'\n"})
        self.bounced_with(self.rig.land(approving=records), "MERGE_CONFLICT")
        self.assertEqual(self.rig.land(approving=records).code, 0)
        self.assertEqual(self.rig.readback().code, 0)
        self.assertEqual(self.rig.tip(), tip)
        contained = self.rig.tip()
        self.rig.write_queue([self.rig.row("T2", contained)])
        self.bounced_with(self.rig.land(approving={REVIEW: record_text(contained)}), "ALREADY_LANDED", ticket="T2")
        self.assertEqual(self.rig.land().code, 0)
        self.assertEqual(self.rig.readback().code, 0)

    def test_a_red_spec_is_spec_red_and_the_invariants_still_run(self) -> None:
        cand, records = self.queued(files={"src/a.py": "a = 3\n"})
        self.rig.control("spec.exit", "1")
        result = self.rig.land(approving=records)
        self.bounced_with(result, "SPEC_RED")
        self.assertEqual(self.rig.calls("invariant"), [[]])
        self.assertEqual(self.rig.tip(), self.rig.base)
        self.assertClean(result)

    def test_a_red_invariant_is_invariant_red(self) -> None:
        cand, records = self.queued()
        self.rig.control("invariant.exit", "7")
        result = self.rig.land(approving=records)
        self.bounced_with(result, "INVARIANT_RED")
        self.assertIn("exited with code 7", result.out)
        self.assertEqual(self.rig.tip(), self.rig.base)

    def test_both_red_prints_both_and_records_the_spec_reason(self) -> None:
        cand, records = self.queued(files={"src/a.py": "a = 4\n"})
        self.rig.control("spec.exit", "1")
        self.rig.control("invariant.exit", "1")
        result = self.rig.land(approving=records)
        self.bounced_with(result, "SPEC_RED")
        self.assertEqual(result.codes, ["SPEC_RED", "INVARIANT_RED"])

    def test_a_review_red_stops_the_run_before_any_configured_command(self) -> None:
        other = self.rig.candidate()
        cand, records = self.queued(files={"src/a.py": "a = 5\n"}, review_candidate=other)
        self.rig.control("invariant.exit", "1")
        self.rig.control("spec.exit", "1")
        result = self.rig.land(approving=records)
        self.bounced_with(result, "REVIEW_MISMATCH")
        self.assertEqual(set(result.codes), {"REVIEW_MISMATCH"})
        self.assertEqual((self.rig.calls("spec"), self.rig.calls("invariant")), ([], []))

    def test_a_red_and_a_fault_in_one_run_exit_one_with_the_fault_on_stderr_and_the_bounce_written(self) -> None:
        cand, records = self.queued(files={"src/a.py": "a = 6\n"})
        self.rig.control("spec.exit", "1")
        self.rig.config["invariant_command"] = [str(self.rig.root / "no-such-program")]
        self.rig.write_config()
        result = self.rig.land(approving=records)
        self.bounced_with(result, "SPEC_RED")
        self.assertEqual(len(result.err_lines), 1, result.err)
        self.assertIn("invariant_command", result.err)
        self.assertEqual(self.rig.tip(), self.rig.base)

    def test_a_fault_alone_exits_two_and_writes_nothing(self) -> None:
        cand, records = self.queued()
        self.rig.config["invariant_command"] = [str(self.rig.root / "no-such-program")]
        self.rig.write_config()
        before = (self.rig.queue_sha(), self.rig.refs())
        result = self.rig.land(approving=records)
        self.assertEqual(result.code, 2, result.text)
        self.assertEqual(result.codes, [])
        self.assertEqual(len(result.err_lines), 1, result.err)
        self.assertEqual((self.rig.queue_sha(), self.rig.refs()), before)
        self.assertEqual(self.rig.states(), {"T1": "QUEUED"})
        self.assertClean(result)

    def test_a_fault_in_the_review_read_runs_no_command_and_is_exit_two(self) -> None:
        cand, records = self.queued()
        self.rig.control("invariant.exit", "1")
        with mock.patch.object(integrate.Integrator, "_record", side_effect=integrate.Fault("the record cannot be read")):
            result = self.rig.main("land", "--config", str(self.rig.config_path))
        self.assertEqual((result.code, result.out), (2, ""), result.text)
        self.assertIn("the record cannot be read", result.err)
        self.assertEqual((self.rig.calls("spec"), self.rig.calls("invariant")), ([], []))
        self.assertEqual(self.rig.states(), {"T1": "QUEUED"})


class LandRaceTests(LandCase):
    def test_a_tip_moved_back_between_read_and_push_loses_the_lease_and_bounces_tip_moved(self) -> None:
        # The candidate descends from the old tip and from the base, so a push without a lease would succeed.
        older = self.rig.tip()
        newer = self.rig.publish({"docs/n.md": "n\n"})
        cand = self.rig.candidate()
        self.rig.write_queue([self.rig.row("T1", cand)])
        records = {REVIEW: record_text(cand)}
        with self.racing(lambda: git(self.rig.remote, "update-ref", f"refs/heads/{BRANCH}", older)):
            result = self.rig.land(approving=records)
        self.bounced_with(result, "TIP_MOVED")
        self.assertEqual(self.rig.tip(), older)
        del newer
        self.assertClean(result)

    def test_a_tip_that_moved_forward_between_read_and_push_bounces_tip_moved(self) -> None:
        cand, records = self.queued()
        moved: list[str] = []
        with self.racing(lambda: moved.append(self.rig.publish({"docs/m.md": "m\n"}))):
            result = self.rig.land(approving=records)
        self.bounced_with(result, "TIP_MOVED")
        self.assertEqual(self.rig.tip(), moved[0])

    def test_a_queue_rewound_between_read_and_push_is_queue_moved_and_both_branches_stay(self) -> None:
        cand = self.rig.candidate()
        older = self.rig.write_queue([self.rig.row("T1", cand)])
        self.rig.write_queue([self.rig.row("T1", cand)])
        tip = self.rig.tip()
        with self.racing(lambda: git(self.rig.remote, "update-ref", f"refs/heads/{QUEUE_BRANCH}", older)):
            result = self.rig.land(approving={REVIEW: record_text(cand)})
        self.assertEqual((result.code, result.err), (1, ""), result.text)
        self.assertEqual(result.codes, ["QUEUE_MOVED"])
        self.assertEqual(self.rig.queue_sha(), older)
        self.assertEqual(self.rig.tip(), tip, "the atomic push must not move the tip when the queue lease is lost")
        self.assertEqual(self.rig.states(), {"T1": "QUEUED"})
        self.assertClean(result)

    def test_a_queue_that_moved_forward_is_queue_moved_and_the_tip_stays(self) -> None:
        cand, records = self.queued()
        tip = self.rig.tip()
        with self.racing(lambda: self.rig.write_queue([self.rig.row("T1", cand), self.rig.row("T2", cand)])):
            result = self.rig.land(approving=records)
        self.assertEqual(result.codes, ["QUEUE_MOVED"])
        self.assertEqual(self.rig.tip(), tip)
        self.assertEqual(self.rig.states(), {"T1": "QUEUED", "T2": "QUEUED"})

    def test_both_leases_lost_is_queue_moved_and_nothing_is_written(self) -> None:
        cand, records = self.queued()

        def both() -> None:
            self.rig.publish({"docs/b.md": "b\n"})
            self.rig.write_queue([self.rig.row("T1", cand)])

        with self.racing(both):
            result = self.rig.land(approving=records)
        self.assertEqual(result.codes, ["QUEUE_MOVED"])
        self.assertEqual(self.rig.states(), {"T1": "QUEUED"})

    def test_a_remote_that_refuses_the_push_for_another_reason_is_a_fault(self) -> None:
        cand, records = self.queued()
        write_hook(self.rig.remote / "hooks" / "pre-receive", "#!/bin/sh\nexit 1\n")
        result = self.rig.land(approving=records)
        self.assertEqual(result.code, 2, result.text)
        self.assertIn("git push failed", result.err)
        self.assertEqual(self.rig.tip(), self.rig.base)


class RealLandTests(LandCase):
    """A land that succeeds against real git: the record is committed on the tip, the candidate is its sibling.

    Nothing here replaces `Integrator._record`; the record is read from the clone of the remote's tip.
    """

    def test_the_record_is_not_patched_in_these_tests(self) -> None:
        self.assertEqual(integrate.Integrator._record.__qualname__, "Integrator._record")
        self.assertNotIsInstance(integrate.Integrator.__dict__["_record"], mock.Mock)

    def test_a_sibling_of_the_record_commit_lands_as_a_merge_commit_and_readback_marks_it_landed(self) -> None:
        cand = self.rig.candidate({"src/a.py": "a = 2\n"})
        record_commit = self.rig.publish_record(cand)
        self.assertEqual(self.rig.parents(cand), [self.rig.base])
        self.assertEqual(self.rig.submit("T1", cand).code, 0)
        result = self.rig.land()
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        merged = self.rig.tip()
        self.rig.assert_merge_of(merged, record_commit, cand)
        self.assertEqual(result.out_lines, [f"LANDED_PENDING_CI T1@{cand} landed_sha={merged}"])
        entry = self.rig.entry("T1")
        self.assertEqual((entry["state"], entry["landed_sha"], entry["parent"]), ("LANDED_PENDING_CI", merged, record_commit))
        self.assertEqual(git(self.rig.remote, "show", f"{merged}:src/a.py"), "a = 2")
        self.assertEqual(git(self.rig.remote, "show", f"{merged}:{REVIEW}").splitlines()[0], "# Review")
        self.assertEqual(self.rig.calls("spec"), [["specs/test_a.py"]])
        for name in ("spec", "invariant"):
            self.assertEqual([row["a"] for row in self.rig.seen(name)], ["a = 2\n"])
        self.rig.control("ci.answer", "green\n")
        read = self.rig.readback()
        self.assertEqual((read.code, read.err), (0, ""), read.text)
        self.assertEqual(self.rig.states(), {"T1": "LANDED"})
        self.assertEqual(self.rig.calls("ci"), [[merged]])
        self.assertEqual(self.rig.tip(), merged)
        self.assertClean(read)

    def test_the_tip_that_moved_after_submit_is_not_a_bounce_reason(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        self.assertEqual(self.rig.submit("T1", cand).code, 0)
        recorded_parent = self.rig.entry("T1")["parent"]
        later = self.rig.publish({"docs/later.md": "later\n"})
        self.assertNotEqual(recorded_parent, later)
        result = self.rig.land()
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.rig.assert_merge_of(self.rig.tip(), later, cand)

    def test_the_merge_commit_is_made_by_the_script_with_the_tip_first(self) -> None:
        cand = self.rig.candidate()
        record_commit = self.rig.publish_record(cand)
        self.assertEqual(self.rig.submit("T1", cand).code, 0)
        self.assertEqual(self.rig.land().code, 0)
        merged = self.rig.tip()
        self.assertEqual(self.rig.parents(merged), [record_commit, cand])
        self.assertEqual(git(self.rig.remote, "log", "-1", "--format=%an <%ae>", merged), "merge-queue <merge-queue@integrate.invalid>")

    def test_a_convergence_disposition_record_lands_against_real_git(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand, record_text(cand, verdict="CONVERGENCE_REVIEW_REQUIRED", disposition="APPROVED"))
        self.assertEqual(self.rig.submit("T1", cand).code, 0)
        result = self.rig.land()
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.assertEqual(self.rig.states(), {"T1": "LANDED_PENDING_CI"})

    def test_the_commands_run_on_the_merged_tree_which_holds_both_sides(self) -> None:
        probe = self.rig.tools / "tree.py"
        out = self.rig.root / "tree.out"
        probe.write_text(
            "import json, os, sys\n"
            "with open(sys.argv[1], 'a', encoding='utf-8') as handle:\n"
            "    handle.write(json.dumps({name: os.path.exists(name) for name in sys.argv[2:]}) + chr(10))\n",
            encoding="utf-8",
            newline="\n",
        )
        names = ["src/c1.py", "docs/newer.md", REVIEW]
        self.rig.config["invariant_command"] = [PY, str(probe), str(out), *names]
        self.rig.write_config()
        cand = self.rig.candidate()
        self.rig.publish({"docs/newer.md": "newer\n"})
        self.rig.publish_record(cand)
        self.assertEqual(self.rig.submit("T1", cand).code, 0)
        result = self.rig.land()
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.assertEqual([json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()], [{name: True for name in names}])

    def test_a_candidate_that_is_not_a_branch_tip_is_fetched_by_its_sha(self) -> None:
        first = self.rig.candidate()
        second = self.rig.commit({"src/more.py": "m\n"}, "more on the same branch", first)
        self.rig.push_seat(f"{second}:refs/heads/cand-1")
        record_commit = self.rig.publish_record(first)
        self.assertEqual(self.rig.submit("T1", first).code, 0)
        result = self.rig.land()
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.rig.assert_merge_of(self.rig.tip(), record_commit, first)
        self.assertEqual(git(self.rig.remote, "ls-tree", "-r", "--name-only", self.rig.tip(), "src/more.py"), "")


class AdmissionTests(LandCase):
    """No configured command runs on a candidate that the record does not admit (finding S50-02)."""

    def marker_commands(self) -> Path:
        marker = self.rig.root / "ran.marker"
        script = self.rig.tools / "marker.py"
        script.write_text(f"import sys\nopen({str(marker)!r}, 'a').write(' '.join(sys.argv[1:]) + chr(10))\n", encoding="utf-8", newline="\n")
        self.rig.config["spec_command"] = [PY, str(script), "spec"]
        self.rig.config["invariant_command"] = [PY, str(script), "invariant"]
        self.rig.write_config()
        return marker

    def test_a_queued_row_written_directly_with_no_record_runs_no_command(self) -> None:
        marker = self.marker_commands()
        cand = self.rig.candidate({"src/a.py": "a = 'hostile'\n", "specs/test_hostile.py": "# covers src/a.py\n"})
        self.rig.write_queue([self.rig.row("T1", cand)])
        tip = self.rig.tip()
        result = self.rig.land()
        self.bounced_with(result, "REVIEW_MISMATCH")
        self.assertFalse(marker.exists(), "a configured command ran on a candidate the record does not admit")
        self.assertEqual(self.rig.tip(), tip)
        self.assertClean(result)

    def test_every_way_the_record_can_fail_to_admit_runs_no_command(self) -> None:
        marker = self.marker_commands()
        cand = self.rig.candidate({"src/a.py": "a = 'x'\n"})
        other = self.rig.candidate()
        variants = {
            "changes-requested": record_text(cand, verdict="CHANGES_REQUESTED"),
            "other-candidate": record_text(other),
            "same-seat": record_text(cand, reviewer=SUBMITTER),
            "convergence-without-disposition": record_text(cand, verdict="CONVERGENCE_REVIEW_REQUIRED"),
            "no-block": "# nothing\n",
        }
        for name, text in variants.items():
            with self.subTest(name):
                self.rig.publish({REVIEW: text}, name)
                self.rig.write_queue([self.rig.row("T1", cand)])
                tip = self.rig.tip()
                result = self.rig.land()
                self.bounced_with(result, "REVIEW_MISMATCH")
                self.assertFalse(marker.exists(), name)
                self.assertEqual(self.rig.tip(), tip)

    def test_a_missing_record_runs_no_command(self) -> None:
        marker = self.marker_commands()
        cand = self.rig.candidate({"src/a.py": "a = 'y'\n"})
        self.rig.write_queue([self.rig.row("T1", cand, review="records/none.md")])
        self.bounced_with(self.rig.land(), "REVIEW_MISMATCH")
        self.assertFalse(marker.exists())

    def test_a_row_whose_copies_differ_from_the_record_runs_no_command(self) -> None:
        marker = self.marker_commands()
        cand = self.rig.candidate({"src/a.py": "a = 'z'\n"})
        self.rig.publish_record(cand)
        self.rig.write_queue([self.rig.row("T1", cand, reviewer="seat:review/run-10")])
        self.bounced_with(self.rig.land(), "REVIEW_MISMATCH")
        self.assertFalse(marker.exists())

    def test_a_conflicting_candidate_runs_no_command_even_with_an_approving_record(self) -> None:
        marker = self.marker_commands()
        cand = self.rig.candidate({"src/a.py": "a = 'candidate'\n"})
        self.rig.publish({"src/a.py": "a = 'tip'\n", REVIEW: record_text(cand)}, "conflicting tip with the record")
        self.rig.write_queue([self.rig.row("T1", cand)])
        self.bounced_with(self.rig.land(), "MERGE_CONFLICT")
        self.assertFalse(marker.exists())

    def test_an_admitted_candidate_does_run_the_commands(self) -> None:
        marker = self.marker_commands()
        cand = self.rig.candidate({"src/a.py": "a = 'ok'\n"})
        self.rig.publish_record(cand)
        self.rig.write_queue([self.rig.row("T1", cand)])
        self.assertEqual(self.rig.land().code, 0)
        self.assertEqual(marker.read_text(encoding="utf-8").splitlines(), ["spec specs/test_a.py", "invariant"])

    def test_a_record_that_only_a_seat_branch_holds_is_review_mismatch_at_land(self) -> None:
        # Finding S50-03: the approving record sits only on a seat branch that descends from the candidate.
        marker = self.marker_commands()
        cand = self.rig.candidate({"src/a.py": "a = 'seat'\n"})
        forged = self.rig.commit({REVIEW: record_text(cand)}, "forged record on the seat branch", cand)
        self.rig.push_seat(f"{forged}:refs/heads/seat-forged")
        self.rig.write_queue([self.rig.row("T1", cand)])
        tip = self.rig.tip()
        refs = {key: value for key, value in self.rig.refs().items() if key != f"refs/heads/{QUEUE_BRANCH}"}
        result = self.rig.land()
        self.bounced_with(result, "REVIEW_MISMATCH")
        self.assertEqual(self.rig.tip(), tip)
        self.assertEqual({key: value for key, value in self.rig.refs().items() if key != f"refs/heads/{QUEUE_BRANCH}"}, refs)
        self.assertFalse(marker.exists())

    def test_a_record_that_only_the_candidates_own_tree_holds_is_review_mismatch_at_land(self) -> None:
        marker = self.marker_commands()
        stand_in = "1" * 40
        cand = self.rig.candidate({REVIEW: record_text(stand_in)})
        self.rig.write_queue([self.rig.row("T1", cand)])
        self.bounced_with(self.rig.land(), "REVIEW_MISMATCH")
        self.assertFalse(marker.exists())

    def test_a_record_that_the_tip_lost_is_review_mismatch(self) -> None:
        marker = self.marker_commands()
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        self.assertEqual(self.rig.submit("T1", cand).code, 0)
        self.rig.publish({REVIEW: None}, "record removed")
        self.bounced_with(self.rig.land(), "REVIEW_MISMATCH")
        self.assertFalse(marker.exists())


class BlockedByCiTests(LandCase):
    def test_a_pending_entry_blocks_every_landing_and_pushes_nothing(self) -> None:
        cand, records = self.queued(ticket="Q1")
        done = self.rig.candidate()
        self.rig.write_queue(
            [self.rig.row("P1", done, state="LANDED_PENDING_CI", landed_sha=done), self.rig.row("Q1", cand)]
        )
        before = (self.rig.queue_sha(), self.rig.refs())
        result = self.rig.land(approving=records)
        self.assertEqual((result.code, result.err), (1, ""), result.text)
        self.assertEqual(result.codes, ["BLOCKED_BY_CI"])
        self.assertIn(f"P1@{done}", result.out)
        self.assertEqual((self.rig.queue_sha(), self.rig.refs()), before)
        self.assertEqual((self.rig.calls("spec"), self.rig.calls("invariant")), ([], []))
        self.assertClean(result)

    def test_a_red_entry_blocks_while_no_queued_entry_clears_it(self) -> None:
        cand = self.rig.candidate()
        red = self.rig.row("R1", self.rig.base, state="LANDED_CI_RED", landed_sha=self.rig.base)
        self.rig.write_queue([red, self.rig.row("Q1", cand)])
        before = (self.rig.queue_sha(), self.rig.refs())
        result = self.rig.land(approving={REVIEW: record_text(cand)})
        self.assertEqual((result.code, result.err), (1, ""), result.text)
        self.assertEqual(result.codes, ["BLOCKED_BY_CI"])
        self.assertEqual((self.rig.queue_sha(), self.rig.refs()), before)

    def test_a_blocked_queue_with_nothing_queued_is_still_blocked(self) -> None:
        self.rig.write_queue([self.rig.row("R1", self.rig.base, state="LANDED_CI_RED", landed_sha=self.rig.base)])
        self.assertEqual(self.rig.land().code, 1)
        self.rig.write_queue([self.rig.row("P1", self.rig.base, state="LANDED_PENDING_CI", landed_sha=self.rig.base)])
        self.assertEqual(self.rig.land().code, 1)

    def test_a_clearing_entry_lands_while_the_block_holds_and_its_green_readback_clears_the_red_entry(self) -> None:
        older = self.rig.candidate()
        clearing = self.rig.candidate()
        red = self.rig.row("R1", self.rig.base, state="LANDED_CI_RED", landed_sha=self.rig.base)
        self.rig.write_queue(
            [
                red,
                self.rig.row("OLD", older),
                self.rig.row("FIX", clearing, clears=f"R1@{self.rig.base}"),
            ]
        )
        records = {REVIEW: record_text(older) + record_text(clearing)}
        result = self.rig.land(approving=records)
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.assertEqual(self.rig.states(), {"R1": "LANDED_CI_RED", "OLD": "QUEUED", "FIX": "LANDED_PENDING_CI"})
        self.assertEqual(self.rig.parents(self.rig.tip())[1], clearing)
        self.assertEqual(self.rig.land(approving=records).code, 1)
        self.rig.control("ci.answer", "green\n")
        self.assertEqual(self.rig.readback().code, 0)
        self.assertEqual(self.rig.states(), {"R1": "CLEARED", "OLD": "QUEUED", "FIX": "LANDED"})

    def test_an_entry_that_clears_only_some_of_the_red_keys_is_not_admitted(self) -> None:
        cand = self.rig.candidate()
        other = self.rig.candidate()
        reds = [
            self.rig.row("R1", self.rig.base, state="LANDED_CI_RED", landed_sha=self.rig.base),
            self.rig.row("R2", other, state="LANDED_CI_RED", landed_sha=other),
        ]
        self.rig.write_queue([*reds, self.rig.row("FIX", cand, clears=f"R1@{self.rig.base}")])
        result = self.rig.land(approving={REVIEW: record_text(cand)})
        self.assertEqual(result.codes, ["BLOCKED_BY_CI", "BLOCKED_BY_CI"])
        self.assertEqual(self.rig.states()["FIX"], "QUEUED")

    def test_an_entry_that_names_every_red_key_is_admitted_and_clears_them_all(self) -> None:
        cand = self.rig.candidate()
        other = self.rig.candidate()
        keys = f"R1@{self.rig.base},R2@{other}"
        self.rig.write_queue(
            [
                self.rig.row("R1", self.rig.base, state="LANDED_CI_RED", landed_sha=self.rig.base),
                self.rig.row("R2", other, state="LANDED_CI_RED", landed_sha=other),
                self.rig.row("FIX", cand, clears=keys),
            ]
        )
        records = {REVIEW: record_text(cand)}
        self.assertEqual(self.rig.land(approving=records).code, 0)
        self.rig.control("ci.answer", "green\n")
        self.assertEqual(self.rig.readback().code, 0)
        self.assertEqual(self.rig.states(), {"R1": "CLEARED", "R2": "CLEARED", "FIX": "LANDED"})

    def test_a_clearing_entry_whose_ci_is_red_adds_a_red_and_the_old_red_stays(self) -> None:
        cand = self.rig.candidate()
        self.rig.write_queue(
            [
                self.rig.row("R1", self.rig.base, state="LANDED_CI_RED", landed_sha=self.rig.base),
                self.rig.row("FIX", cand, clears=f"R1@{self.rig.base}"),
            ]
        )
        self.assertEqual(self.rig.land(approving={REVIEW: record_text(cand)}).code, 0)
        self.rig.control("ci.answer", "red\n")
        self.assertEqual(self.rig.readback().code, 0)
        self.assertEqual(self.rig.states(), {"R1": "LANDED_CI_RED", "FIX": "LANDED_CI_RED"})

    def test_bounced_and_landed_entries_do_not_block(self) -> None:
        cand = self.rig.candidate()
        self.rig.write_queue(
            [
                self.rig.row("B1", self.rig.base, state="BOUNCED", reason="SPEC_RED"),
                self.rig.row("L1", self.rig.base, state="LANDED", landed_sha=self.rig.base),
                self.rig.row("C1", self.rig.base, state="CLEARED", landed_sha=self.rig.base),
                self.rig.row("Q1", cand),
            ]
        )
        self.assertEqual(self.rig.land(approving={REVIEW: record_text(cand)}).code, 0)
        self.assertEqual(self.rig.states()["Q1"], "LANDED_PENDING_CI")


class ReadbackTests(LandCase):
    def pending(self, count: int = 1) -> list[str]:
        shas = [self.rig.candidate() for _ in range(count)]
        self.rig.write_queue([self.rig.row(f"P{number}", sha, state="LANDED_PENDING_CI", landed_sha=sha) for number, sha in enumerate(shas, start=1)])
        return shas

    def test_red_is_recorded_as_landed_ci_red_and_the_exit_is_zero(self) -> None:
        (sha,) = self.pending()
        self.rig.control("ci.answer", "red\n")
        result = self.rig.readback()
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.assertEqual(self.rig.states(), {"P1": "LANDED_CI_RED"})
        self.assertIn(f"READBACK P1@{sha} LANDED_PENDING_CI -> LANDED_CI_RED", result.out_lines)
        self.assertClean(result)

    def test_pending_leaves_the_entry_and_writes_no_commit(self) -> None:
        self.pending()
        before = self.rig.queue_sha()
        self.rig.control("ci.answer", "pending\n")
        result = self.rig.readback()
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.assertEqual(self.rig.queue_sha(), before)
        self.assertEqual(self.rig.states(), {"P1": "LANDED_PENDING_CI"})

    def test_several_entries_move_in_one_commit_and_other_states_are_untouched(self) -> None:
        shas = [self.rig.candidate() for _ in range(3)]
        rows = [self.rig.row(f"P{n}", sha, state="LANDED_PENDING_CI", landed_sha=sha) for n, sha in enumerate(shas, start=1)]
        rows.append(self.rig.row("Q1", shas[0], state="QUEUED"))
        rows.append(self.rig.row("B1", shas[1], state="BOUNCED", reason="SPEC_RED"))
        self.rig.write_queue(rows)
        before = self.rig.queue_sha()
        self.rig.control(f"ci.answer.{shas[0]}", "green\n")
        self.rig.control(f"ci.answer.{shas[1]}", "red\n")
        self.rig.control(f"ci.answer.{shas[2]}", "pending\n")
        result = self.rig.readback()
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.assertEqual(self.rig.states(), {"P1": "LANDED", "P2": "LANDED_CI_RED", "P3": "LANDED_PENDING_CI", "Q1": "QUEUED", "B1": "BOUNCED"})
        after = self.rig.queue_sha()
        assert after is not None
        self.assertEqual(git(self.rig.remote, "rev-parse", f"{after}^"), before)
        self.assertEqual(sorted(call[0] for call in self.rig.calls("ci")), sorted(shas))

    def test_a_green_entry_clears_only_the_red_entries_it_names(self) -> None:
        (sha,) = self.pending()
        rows = self.rig.entries()
        rows[0]["clears"] = f"R1@{self.rig.base},R2@{self.rig.base},GONE@{sha}"
        rows.append(self.rig.row("R1", self.rig.base, state="LANDED_CI_RED", landed_sha=self.rig.base))
        rows.append(self.rig.row("R2", self.rig.base, state="LANDED", landed_sha=self.rig.base))
        rows.append(self.rig.row("R3", self.rig.base, state="LANDED_CI_RED", landed_sha=self.rig.base))
        self.rig.write_queue(rows)
        self.rig.control("ci.answer", "green\n")
        self.assertEqual(self.rig.readback().code, 0)
        self.assertEqual(self.rig.states(), {"P1": "LANDED", "R1": "CLEARED", "R2": "LANDED", "R3": "LANDED_CI_RED"})

    def test_a_red_answer_never_clears_anything(self) -> None:
        (sha,) = self.pending()
        rows = self.rig.entries()
        rows[0]["clears"] = f"R1@{self.rig.base}"
        rows.append(self.rig.row("R1", self.rig.base, state="LANDED_CI_RED", landed_sha=self.rig.base))
        self.rig.write_queue(rows)
        self.rig.control("ci.answer", "red\n")
        self.assertEqual(self.rig.readback().code, 0)
        self.assertEqual(self.rig.states(), {"P1": "LANDED_CI_RED", "R1": "LANDED_CI_RED"})

    def test_a_red_status_is_not_dropped_by_a_fault_on_another_entry(self) -> None:
        first, second = self.pending(2)
        self.rig.control(f"ci.answer.{first}", "red\n")
        self.rig.control(f"ci.answer.{second}", "maybe\n")
        result = self.rig.readback()
        self.assertEqual(result.code, 2, result.text)
        self.assertEqual(self.rig.states(), {"P1": "LANDED_CI_RED", "P2": "LANDED_PENDING_CI"})
        self.assertEqual(len(result.err_lines), 1, result.err)
        self.assertIn(f"P2@{second}", result.err)

    def test_answers_outside_the_format_are_a_fault_and_write_nothing(self) -> None:
        self.pending()
        before = self.rig.queue_sha()
        answers: dict[str, bytes] = {
            "uppercase": b"GREEN\n",
            "leading-blank": b" green\n",
            "trailing-blank": b"green \n",
            "two-newlines": b"green\n\n",
            "empty": b"",
            "two-words": b"green\nred\n",
            "word": b"ok\n",
            "not-utf8": b"gr\xffen\n",
            "separator": ("green" + LINE_SEPARATOR + "\n").encode("utf-8"),
        }
        for name, answer in answers.items():
            with self.subTest(name):
                self.rig.control("ci.answer", answer)
                result = self.rig.readback()
                self.assertEqual(result.code, 2, result.text)
                self.assertEqual(len(result.err_lines), 1, result.err)
                self.assertEqual(self.rig.queue_sha(), before)

    def test_answers_in_the_format_are_accepted(self) -> None:
        for name, answer in (("crlf", b"green\r\n"), ("bare", b"green")):
            with self.subTest(name):
                self.pending()
                self.rig.control("ci.answer", answer)
                self.assertEqual(self.rig.readback().code, 0)
                self.assertEqual(self.rig.states(), {"P1": "LANDED"})

    def test_a_failing_status_command_is_a_fault(self) -> None:
        self.pending()
        self.rig.control("ci.answer", "green\n")
        self.rig.control("ci.exit", "3")
        result = self.rig.readback()
        self.assertEqual(result.code, 2, result.text)
        self.assertIn("exited with code 3", result.err)
        self.assertEqual(self.rig.states(), {"P1": "LANDED_PENDING_CI"})

    def test_only_the_argument_equal_to_the_placeholder_is_replaced(self) -> None:
        (sha,) = self.pending()
        self.rig.config["ci_status_command"] = [PY, str(self.rig.tools / "ci.py"), "{sha}", "x{sha}"]
        self.rig.write_config()
        self.rig.control("ci.answer", "green\n")
        self.assertEqual(self.rig.readback().code, 0)
        self.assertEqual(self.rig.calls("ci"), [[sha, "x{sha}"]])

    def test_a_lost_queue_lease_is_queue_moved_and_records_nothing(self) -> None:
        self.pending()
        older = self.rig.queue_sha()
        self.rig.write_queue(self.rig.entries())
        self.rig.control("ci.answer", "green\n")
        original = integrate.Clone.push

        def racing(clone: integrate.Clone, updates: Sequence[tuple[str, str, str | None]]) -> integrate.Completed:
            git(self.rig.remote, "update-ref", f"refs/heads/{QUEUE_BRANCH}", older or "")
            return original(clone, updates)

        with mock.patch.object(integrate.Clone, "push", racing):
            result = self.rig.readback()
        self.assertEqual((result.code, result.err), (1, ""), result.text)
        self.assertEqual(result.codes[:1], ["QUEUE_MOVED"])
        self.assertNotIn("READBACK P1", result.out)
        self.assertEqual(self.rig.states(), {"P1": "LANDED_PENDING_CI"})

    def test_readback_never_moves_the_tip_and_runs_in_a_clone_of_the_tip(self) -> None:
        self.pending()
        tip = self.rig.tip()
        self.rig.control("ci.answer", "green\n")
        self.assertEqual(self.rig.readback().code, 0)
        self.assertEqual(self.rig.tip(), tip)
        self.assertEqual([row["a"] for row in self.rig.seen("ci")], ["a = 1\n"])


class CommandFaultTests(LandCase):
    def test_a_missing_command_is_a_fault_for_each_configured_command(self) -> None:
        cand, records = self.queued()
        for key in ("invariant_command",):
            with self.subTest(key):
                self.rig.config[key] = [str(self.rig.root / "absent")]
                self.rig.write_config()
                result = self.rig.land(approving=records)
                self.assertEqual((result.code, result.codes), (2, []), result.text)
                self.assertIn(key, result.err)

    def test_a_missing_spec_command_is_a_fault_when_a_spec_is_affected(self) -> None:
        cand, records = self.queued(files={"src/a.py": "a = 8\n"})
        self.rig.config["spec_command"] = [str(self.rig.root / "absent")]
        self.rig.write_config()
        result = self.rig.land(approving=records)
        self.assertEqual(result.code, 2, result.text)
        self.assertIn("spec_command", result.err)
        self.assertEqual(self.rig.states(), {"T1": "QUEUED"})

    def test_a_missing_status_command_is_a_fault(self) -> None:
        sha = self.rig.candidate()
        self.rig.write_queue([self.rig.row("P1", sha, state="LANDED_PENDING_CI", landed_sha=sha)])
        self.rig.config["ci_status_command"] = [str(self.rig.root / "absent"), "{sha}"]
        self.rig.write_config()
        result = self.rig.readback()
        self.assertEqual(result.code, 2, result.text)
        self.assertIn("ci_status_command", result.err)

    def test_a_batch_file_is_refused_and_a_drive_relative_name_is_refused(self) -> None:
        cand, records = self.queued()
        batch = self.rig.root / "run.cmd"
        batch.write_text("@exit 0\r\n", encoding="utf-8")
        for name, argv in (("batch", [str(batch)]), ("drive-relative", ["C:relative.exe"])):
            with self.subTest(name):
                self.rig.config["invariant_command"] = argv
                self.rig.write_config()
                result = self.rig.land(approving=records)
                self.assertEqual(result.code, 2, result.text)
                self.assertEqual(len(result.err_lines), 1)
                self.assertEqual(self.rig.states(), {"T1": "QUEUED"})

    def beats(self) -> int:
        path = self.rig.ctl / "invariant.beat"
        return path.stat().st_size if path.exists() else 0

    def test_a_command_that_exceeds_the_timeout_is_a_fault_and_its_tree_is_killed(self) -> None:
        cand, records = self.queued()
        self.rig.config["timeout_seconds"] = 3
        self.rig.write_config()
        self.rig.control("invariant.sleep", "1")
        started = time.monotonic()
        result = self.rig.land(approving=records)
        self.assertLess(time.monotonic() - started, 60)
        self.assertEqual(result.code, 2, result.text)
        self.assertIn("timed out after 3s and was killed", result.err)
        self.assertEqual(self.rig.states(), {"T1": "QUEUED"})
        self.assertEqual(self.rig.tip(), self.rig.base)
        first = self.beats()
        self.assertGreater(first, 0, "the grandchild must have started")
        time.sleep(1.0)
        self.assertEqual(self.beats(), first, "the grandchild must be dead")
        self.assertClean(result)

    def test_a_status_command_that_exceeds_the_timeout_is_a_fault(self) -> None:
        sha = self.rig.candidate()
        self.rig.write_queue([self.rig.row("P1", sha, state="LANDED_PENDING_CI", landed_sha=sha)])
        self.rig.config["timeout_seconds"] = 3
        self.rig.write_config()
        self.rig.control("ci.sleep", "1")
        result = self.rig.readback()
        self.assertEqual(result.code, 2, result.text)
        self.assertIn("timed out", result.err)
        self.assertEqual(self.rig.states(), {"P1": "LANDED_PENDING_CI"})

    def test_a_timeout_after_a_red_keeps_the_red_and_records_the_bounce(self) -> None:
        cand, records = self.queued(files={"src/a.py": "a = 9\n"})
        self.rig.control("spec.exit", "1")
        self.rig.config["timeout_seconds"] = 3
        self.rig.write_config()
        self.rig.control("invariant.sleep", "1")
        result = self.rig.land(approving=records)
        self.bounced_with(result, "SPEC_RED")
        self.assertEqual(len(result.err_lines), 1)
        self.assertIn("timed out", result.err)

    def test_the_commands_run_without_the_repository_selecting_variables(self) -> None:
        cand, records = self.queued()
        names = ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_CONFIG_COUNT"]
        probe = self.rig.tools / "probe.py"
        probe.write_text(
            "import json, os, sys\njson.dump(sorted(k for k in os.environ if k.upper().startswith('GIT_')), open(sys.argv[1], 'w'))\n",
            encoding="utf-8",
        )
        out = self.rig.root / "probe.out"
        self.rig.config["invariant_command"] = [PY, str(probe), str(out)]
        self.rig.write_config()
        inherited = {"GIT_DIR": str(self.rig.seat / ".git"), "GIT_WORK_TREE": str(self.rig.seat), "GIT_CONFIG_COUNT": "0", "GIT_INDEX_FILE": str(self.rig.root / "x")}
        with mock.patch.dict(os.environ, inherited):
            result = self.rig.land(approving=records)
        self.assertEqual(result.code, 0, result.text)
        seen: list[str] = json.loads(out.read_text(encoding="utf-8"))
        for name in names:
            self.assertNotIn(name, seen)
        self.assertIn("GIT_NO_REPLACE_OBJECTS", seen)


class CorruptQueueTests(LandCase):
    """A queue file that breaks its schema is exit 2 naming the entry and the field; nothing is rewritten."""

    def good(self, **changes: str) -> dict[str, str]:
        ticket = changes.pop("ticket", "T1")
        candidate = changes.pop("candidate", self.rig.base)
        return self.rig.row(ticket, candidate, **changes)

    def refused(self, variants: Mapping[str, str | bytes], needle: str | None = None, runs: Sequence[str] = ("land",)) -> None:
        tip = self.rig.tip()
        for name, raw in variants.items():
            with self.subTest(name):
                sha = self.rig.write_queue(raw=raw)
                for run in runs:
                    if run == "land":
                        result = self.rig.land(approving={REVIEW: record_text(self.rig.base)})
                    elif run == "readback":
                        result = self.rig.readback()
                    else:
                        cand = self.rig.candidate()
                        result = self.rig.submit("N1", cand, approving={REVIEW: record_text(cand)})
                    self.assertEqual(result.code, 2, f"{name} {run}: {result.text}")
                    self.assertEqual(result.out_lines, [], result.text)
                    self.assertEqual(len(result.err_lines), 1, result.err)
                    self.assertIn("queue file", result.err)
                    if needle:
                        self.assertIn(needle, result.err)
                    self.assertEqual(self.rig.queue_sha(), sha, "a corrupt queue must not be rewritten")
                    self.assertEqual(self.rig.tip(), tip)
                    self.assertEqual(self.rig.tmp_left(), [])

    def doc(self, *rows: Mapping[str, str]) -> str:
        return json.dumps({"entries": list(rows)}, indent=2) + "\n"

    def test_a_file_that_is_not_the_documented_shape(self) -> None:
        good = self.good()
        self.refused(
            {
                "not-json": "{",
                "empty": "",
                "list": "[]\n",
                "extra-top-key": json.dumps({"entries": [], "more": 1}),
                "no-entries": "{}",
                "entries-not-a-list": json.dumps({"entries": {}}),
                "entry-not-an-object": json.dumps({"entries": [1]}),
                "repeated-top-key": '{"entries": [], "entries": []}',
                "repeated-entry-key": json.dumps({"entries": [good]}).replace('"ticket": "T1"', '"ticket": "T1", "ticket": "T2"'),
                "nan": '{"entries": [], "n": NaN}',
                "infinity": '{"entries": [], "n": Infinity}',
                "minus-infinity": '{"entries": [], "n": -Infinity}',
                "float-overflow": '{"entries": [], "n": 1e999}',
                "too-deep": "[" * 100000,
                "crlf": self.doc(good).replace("\n", "\r\n"),
                "bom": "﻿" + self.doc(good),
                "not-utf8": b'{"entries": [], "x": "\xff"}',
                "control-character": self.doc(good).replace('"clears": ""', '"clears": "\\u0009"'),
                "lone-surrogate": self.doc(good).replace('"clears": ""', '"clears": "\\ud800"'),
            }
        )

    def test_a_field_that_breaks_its_rule_is_named(self) -> None:
        base = self.good()
        def without(name: str) -> dict[str, str]:
            return {key: value for key, value in base.items() if key != name}

        cases: dict[str, tuple[Mapping[str, object], str]] = {
            "missing-clears": (without("clears"), "clears"),
            "extra-field": ({**base, "extra": "x"}, "extra"),
            "number": ({**base, "reason": 1}, "reason"),
            "null": ({**base, "landed_sha": None}, "landed_sha"),
            "state-unknown": (self.good(state="DONE"), "state"),
            "state-lower": (self.good(state="queued"), "state"),
            "ticket-space": (self.good(ticket="T 1"), "ticket"),
            "ticket-empty": (self.good(ticket=""), "ticket"),
            "candidate-short": (self.good(candidate="abc"), "candidate"),
            "candidate-upper": (self.good(candidate=self.rig.base.upper()), "candidate"),
            "candidate-wide": (self.good(candidate="a" * 64), "candidate"),
            "parent-bad": (self.good(parent="x"), "parent"),
            "review-candidate-bad": (self.good(review_candidate=""), "review_candidate"),
            "review-dotdot": (self.good(review="../r.md"), "review"),
            "review-backslash": (self.good(review="a\\r.md"), "review"),
            "review-absolute": (self.good(review="/r.md"), "review"),
            "review-trailing-slash": (self.good(review="a/"), "review"),
            "review-empty": (self.good(review=""), "review"),
            "reviewer-bad": (self.good(reviewer="reviewer"), "reviewer"),
            "submitter-bad": (self.good(submitter="seat:x"), "submitter"),
            "landed-sha-on-queued": (self.good(landed_sha=self.rig.base), "landed_sha"),
            "landed-sha-missing": (self.good(state="LANDED"), "landed_sha"),
            "landed-sha-bad": (self.good(state="LANDED_PENDING_CI", landed_sha="abc"), "landed_sha"),
            "reason-on-queued": (self.good(reason="SPEC_RED"), "reason"),
            "reason-unknown": (self.good(state="BOUNCED", reason="OTHER"), "reason"),
            "reason-missing": (self.good(state="BOUNCED"), "reason"),
            "reason-queue-moved": (self.good(state="BOUNCED", reason="QUEUE_MOVED"), "reason"),
            "clears-no-at": (self.good(clears="T1"), "clears"),
            "clears-short-sha": (self.good(clears="T1@abc"), "clears"),
            "clears-trailing-comma": (self.good(clears=f"T1@{self.rig.base},"), "clears"),
            "clears-repeated": (self.good(clears=f"T1@{self.rig.base},T1@{self.rig.base}"), "clears"),
            "clears-wide": (self.good(clears="T1@" + "a" * 64), "clears"),
        }
        tip = self.rig.tip()
        for name, (row, field) in cases.items():
            with self.subTest(name):
                sha = self.rig.write_queue(raw=json.dumps({"entries": [row]}))
                result = self.rig.land()
                self.assertEqual((result.code, result.out_lines), (2, []), result.text)
                self.assertEqual(len(result.err_lines), 1, result.err)
                self.assertIn(f"field {field}", result.err, name)
                self.assertIn("entry 1", result.err)
                self.assertEqual((self.rig.queue_sha(), self.rig.tip()), (sha, tip))

    def test_the_entry_is_named_by_its_position_and_ticket(self) -> None:
        self.rig.write_queue(raw=self.doc(self.good(), self.rig.row("T2", self.rig.base, state="BOGUS")))
        result = self.rig.land()
        self.assertEqual(result.code, 2)
        self.assertIn("entry 2 (T2), field state", result.err)

    def test_a_repeated_key_is_refused(self) -> None:
        self.refused({"repeated": self.doc(self.good(), self.good(state="BOUNCED", reason="SPEC_RED"))}, needle="repeated")

    def test_submit_and_readback_refuse_a_corrupt_queue_too(self) -> None:
        self.refused({"bad": "{"}, runs=("land", "readback", "submit"))

    def test_the_queue_path_that_is_a_directory_is_a_fault(self) -> None:
        env = {**_clean_environment(), **GIT_IDENTITY}
        remote = str(self.rig.remote)
        blob = subprocess.run(["git", "-C", remote, "hash-object", "-w", "--stdin"], input=b"x", capture_output=True, check=True).stdout.decode().strip()
        inner = subprocess.run(["git", "-C", remote, "mktree"], input=f"100644 blob {blob}\tinner\n".encode(), capture_output=True, check=True).stdout.decode().strip()
        parts = QUEUE_PATH.split("/")
        tree = inner
        for part in reversed(parts):
            tree = subprocess.run(["git", "-C", remote, "mktree"], input=f"040000 tree {tree}\t{part}\n".encode(), capture_output=True, check=True).stdout.decode().strip()
        commit = subprocess.run(["git", "-C", remote, "commit-tree", tree, "-m", "q"], capture_output=True, check=True, env=env).stdout.decode().strip()
        git(self.rig.remote, "update-ref", f"refs/heads/{QUEUE_BRANCH}", commit)
        result = self.rig.land()
        self.assertEqual(result.code, 2, result.text)
        self.assertEqual(len(result.err_lines), 1)

    def test_a_ticket_with_a_line_separator_prints_on_one_line(self) -> None:
        self.rig.write_queue(raw=self.doc(self.good(ticket="T" + LINE_SEPARATOR + "1")))
        result = self.rig.land()
        self.assertEqual(result.code, 2)
        self.assertEqual(len(result.err_lines), 1, result.err)
        self.assertNotIn(LINE_SEPARATOR, result.text)


class RemoteFaultTests(LandCase):
    def test_an_unreachable_remote_is_a_fault_for_every_subcommand(self) -> None:
        self.rig.config["remote"] = str(self.rig.root / "absent.git")
        self.rig.write_config()
        cand = self.rig.candidate()
        for result in (
            self.rig.land(),
            self.rig.readback(),
            self.rig.submit("T1", cand, approving={REVIEW: record_text(cand)}),
        ):
            self.assertEqual((result.code, result.out), (2, ""), result.text)
            self.assertEqual(len(result.err_lines), 1, result.err)
            self.assertClean(result)

    def test_a_remote_without_the_integration_branch_is_a_fault(self) -> None:
        self.rig.config["branch"] = "absent-branch"
        self.rig.write_config()
        result = self.rig.land()
        self.assertEqual(result.code, 2, result.text)
        self.assertIn("absent-branch", result.err)

    def test_an_unreadable_config_ends_the_run_at_once(self) -> None:
        result = self.rig.main("land", "--config", str(self.rig.root / "none.json"))
        self.assertEqual((result.code, result.out), (2, ""), result.text)
        self.assertEqual(len(result.err_lines), 1)
        directory = self.rig.main("land", "--config", str(self.rig.root))
        self.assertEqual(directory.code, 2)

    def test_git_that_cannot_be_found_is_a_fault(self) -> None:
        empty = self.rig.root / "empty-path"
        empty.mkdir()
        result = self.rig.cli("land", "--config", str(self.rig.config_path), path=str(empty))
        self.assertEqual((result.code, result.out), (2, ""), result.text)
        self.assertIn("git cannot be found", result.err)
        self.assertEqual(len(result.err_lines), 1)

    def test_git_is_looked_up_in_absolute_path_entries_only(self) -> None:
        here = self.rig.root / "cwd"
        here.mkdir()
        for name in ("git", "git.exe", "git.cmd", "git.bat"):
            (here / name).write_text("x", encoding="utf-8")
            os.chmod(here / name, 0o755)
        cwd = os.getcwd()
        try:
            os.chdir(here)
            with mock.patch.dict(os.environ, {"PATH": os.pathsep.join([".", "", "relative-dir", str(self.rig.root / "nowhere")])}):
                with self.assertRaises(integrate.Fault):
                    integrate.find_git()
        finally:
            os.chdir(cwd)

    def test_a_forged_loose_object_in_the_remote_makes_the_fetch_fail_and_nothing_is_pushed(self) -> None:
        import zlib

        cand, records = self.queued()
        blob = git(self.rig.remote, "rev-parse", f"{self.rig.tip()}:src/a.py")
        path = self.rig.remote / "objects" / blob[:2] / blob[2:]
        self.assertTrue(path.exists(), "the fixture needs the blob as a loose object")
        os.chmod(path, 0o666)
        path.write_bytes(zlib.compress(b"blob 6\x00forged"))
        before = (self.rig.refs(), self.rig.queue_sha())
        for name, result in (("land", self.rig.land(approving=records)), ("readback", self.rig.readback())):
            with self.subTest(name):
                self.assertEqual((result.code, result.out), (2, ""), result.text)
                self.assertEqual(len(result.err_lines), 1)
                self.assertEqual((self.rig.refs(), self.rig.queue_sha()), before)
                self.assertClean(result)

    def test_an_object_that_hashes_right_but_breaks_the_format_is_stopped_by_the_fsck_fetch(self) -> None:
        cand, records = self.queued()
        tip = self.rig.tip()
        tree = git(self.rig.remote, "rev-parse", f"{tip}^{{tree}}")
        body = f"tree {tree}\nparent {tip}\ncommitter c <c@c> 1 +0000\n\nno author\n".encode()
        bad = subprocess.run(["git", "-C", str(self.rig.remote), "hash-object", "-t", "commit", "--literally", "-w", "--stdin"], input=body, capture_output=True, check=True).stdout.decode().strip()
        git(self.rig.remote, "update-ref", f"refs/heads/{BRANCH}", bad)
        before = (self.rig.refs(), self.rig.queue_sha())
        for name, result in (("land", self.rig.land(approving=records)), ("submit", self.rig.submit("N1", cand, approving=records))):
            with self.subTest(name):
                self.assertEqual((result.code, result.out), (2, ""), result.text)
                self.assertIn("verified fetch failed", result.err)
                self.assertEqual((self.rig.refs(), self.rig.queue_sha()), before)
                self.assertClean(result)

    def test_the_fetch_and_the_push_carry_the_fsck_options(self) -> None:
        cand, records = self.queued()
        seen: list[list[str]] = []
        original = integrate.run_process

        def spy(argv: Sequence[str], cwd: str, env: Mapping[str, str], timeout: float, stdin: bytes | None = None) -> integrate.Completed:
            seen.append(list(argv))
            return original(argv, cwd, env, timeout, stdin)

        with mock.patch.object(integrate, "run_process", spy):
            self.assertEqual(self.rig.land(approving=records).code, 0)
        fetches = [argv for argv in seen if "fetch" in argv]
        pushes = [argv for argv in seen if "push" in argv]
        self.assertEqual(len(fetches), 2, "one fetch of the two branches and one of the candidate")
        for fetch in fetches:
            for option in ("transfer.fsckObjects=true", "fetch.fsckObjects=true"):
                self.assertIn(option, fetch)
        self.assertIn("transfer.fsckObjects=true", pushes[0])
        self.assertIn("--atomic", pushes[0])
        leases = [argument for argument in pushes[0] if argument.startswith("--force-with-lease=")]
        self.assertEqual(len(leases), 2)
        self.assertTrue(all(lease.rsplit(":", 1)[1] for lease in leases), leases)
        self.assertEqual(len([argv for argv in seen if "push" in argv]), 1, "one atomic push, not two")

    def test_a_land_builds_a_fresh_clone_each_time(self) -> None:
        cand, records = self.queued()
        clones: list[str] = []
        original = integrate.Clone.open

        def spy(config: integrate.Config, exe: str) -> integrate.Clone:
            clone = original(config, exe)
            clones.append(clone.scratch)
            return clone

        with mock.patch.object(integrate.Clone, "open", staticmethod(spy)):
            self.rig.land(approving=records)
            self.rig.land(approving=records)
        self.assertEqual(len(set(clones)), 2)
        self.assertTrue(all(not os.path.exists(path) for path in clones))


class FetchScopeTests(LandCase):
    """The fetch takes the integration branch, the queue branch and the candidate being landed (finding S50-08)."""

    def bad_commit(self, parent: str) -> str:
        tree = git(self.rig.remote, "rev-parse", f"{parent}^{{tree}}")
        body = f"tree {tree}\nparent {parent}\ncommitter c <c@c> 1 +0000\n\nno author\n".encode()
        return subprocess.run(
            ["git", "-C", str(self.rig.remote), "hash-object", "-t", "commit", "--literally", "-w", "--stdin"],
            input=body,
            capture_output=True,
            check=True,
        ).stdout.decode().strip()

    def test_a_malformed_object_on_an_unrelated_branch_stops_no_subcommand(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        git(self.rig.remote, "update-ref", "refs/heads/seat-bad", self.bad_commit(self.rig.base))
        self.assertEqual(self.rig.submit("T1", cand).code, 0)
        landed = self.rig.land()
        self.assertEqual((landed.code, landed.err), (0, ""), landed.text)
        self.rig.control("ci.answer", "green\n")
        read = self.rig.readback()
        self.assertEqual((read.code, read.err), (0, ""), read.text)
        self.assertEqual(self.rig.states(), {"T1": "LANDED"})

    def test_a_malformed_object_on_the_candidate_branch_is_a_fault_and_nothing_is_pushed(self) -> None:
        bad = self.bad_commit(self.rig.tip())
        git(self.rig.remote, "update-ref", "refs/heads/cand-bad", bad)
        self.rig.write_queue([self.rig.row("T1", bad)])
        record = record_text(bad)
        self.rig.publish({REVIEW: record}, "record of the bad candidate")
        before = (self.rig.refs(), self.rig.queue_sha())
        result = self.rig.land()
        self.assertEqual((result.code, result.out), (2, ""), result.text)
        self.assertIn("verified fetch failed", result.err)
        self.assertEqual((self.rig.refs(), self.rig.queue_sha()), before)
        self.assertClean(result)

    def test_the_fetches_name_their_refs_and_never_a_wildcard(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        self.rig.write_queue([self.rig.row("T1", cand)])
        seen: list[list[str]] = []
        original = integrate.run_process

        def spy(argv: Sequence[str], cwd: str, env: Mapping[str, str], timeout: float, stdin: bytes | None = None) -> integrate.Completed:
            seen.append(list(argv))
            return original(argv, cwd, env, timeout, stdin)

        with mock.patch.object(integrate, "run_process", spy):
            self.assertEqual(self.rig.land().code, 0)
        fetches = [argv for argv in seen if "fetch" in argv]
        self.assertEqual(len(fetches), 2)
        for argv in fetches:
            tail = argv[argv.index("--", argv.index("fetch")) + 2 :]
            self.assertFalse([item for item in tail if "*" in item], argv)
        self.assertEqual(
            fetches[0][fetches[0].index("--", fetches[0].index("fetch")) + 2 :],
            [f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}", f"+refs/heads/{QUEUE_BRANCH}:refs/remotes/origin/{QUEUE_BRANCH}"],
        )
        self.assertEqual(fetches[1][-1], "refs/heads/cand-1")

    def test_a_run_without_a_queue_branch_fetches_only_the_integration_branch(self) -> None:
        seen: list[list[str]] = []
        original = integrate.run_process

        def spy(argv: Sequence[str], cwd: str, env: Mapping[str, str], timeout: float, stdin: bytes | None = None) -> integrate.Completed:
            seen.append(list(argv))
            return original(argv, cwd, env, timeout, stdin)

        with mock.patch.object(integrate, "run_process", spy):
            self.assertEqual(self.rig.land().code, 0)
        fetches = [argv for argv in seen if "fetch" in argv]
        self.assertEqual(len(fetches), 1)
        self.assertEqual(fetches[0][-1], f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}")

    def test_a_global_git_configuration_cannot_weaken_the_verified_fetch(self) -> None:
        # Finding S50-07: with the message class downgraded in a global config, a malformed tip would pass the fetch.
        self.queued()
        home = self.rig.root / "home"
        home.mkdir()
        (home / ".gitconfig").write_text("[fetch \"fsck\"]\n\tmissingAuthor = ignore\n[transfer \"fsck\"]\n\tmissingAuthor = ignore\n", encoding="utf-8", newline="\n")
        git(self.rig.remote, "update-ref", f"refs/heads/{BRANCH}", self.bad_commit(self.rig.tip()))
        before = (self.rig.refs(), self.rig.queue_sha())
        inherited = {"HOME": str(home), "USERPROFILE": str(home), "XDG_CONFIG_HOME": str(home)}
        for run in ("land", "readback"):
            with self.subTest(run):
                result = self.rig.cli(run, "--config", str(self.rig.config_path), extra_env=inherited)
                self.assertEqual((result.code, result.out), (2, ""), result.text)
                self.assertIn("verified fetch failed", result.err)
                self.assertEqual((self.rig.refs(), self.rig.queue_sha()), before)

    def test_the_global_configuration_is_what_would_have_weakened_it(self) -> None:
        # The control for the test above: the same configuration does make a plain git fetch accept the object.
        self.rig.candidate()
        home = self.rig.root / "home"
        home.mkdir()
        (home / ".gitconfig").write_text("[fetch \"fsck\"]\n\tmissingAuthor = ignore\n", encoding="utf-8", newline="\n")
        git(self.rig.remote, "update-ref", f"refs/heads/{BRANCH}", self.bad_commit(self.rig.tip()))
        target = self.rig.root / "control"
        target.mkdir()
        env = {**_clean_environment(), "HOME": str(home), "USERPROFILE": str(home), "XDG_CONFIG_HOME": str(home)}
        subprocess.run(["git", "init", "-q", str(target)], check=True, env=env)
        done = subprocess.run(
            ["git", "-C", str(target), "-c", "transfer.fsckObjects=true", "-c", "fetch.fsckObjects=true", "fetch", "-q", str(self.rig.remote), f"refs/heads/{BRANCH}"],
            capture_output=True,
            env=env,
        )
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))


class CorrectionOneTests(LandCase):
    """Correction 1 under revision02: findings S50-10 to S50-14."""

    def bad_commit(self, parent: str) -> str:
        tree = git(self.rig.remote, "rev-parse", f"{parent}^{{tree}}")
        body = f"tree {tree}\nparent {parent}\ncommitter c <c@c> 1 +0000\n\nno author\n".encode()
        return subprocess.run(
            ["git", "-C", str(self.rig.remote), "hash-object", "-t", "commit", "--literally", "-w", "--stdin"],
            input=body,
            capture_output=True,
            check=True,
        ).stdout.decode().strip()

    def rewriting(self, rewrite: Callable[[Sequence[str]], integrate.Completed | None]) -> contextlib.AbstractContextManager[object]:
        """Run the script with `rewrite(argv)` free to answer a child process itself (None lets it run)."""
        original = integrate.run_process

        def wrapper(argv: Sequence[str], cwd: str, env: Mapping[str, str], timeout: float, stdin: bytes | None = None) -> integrate.Completed:
            answer = rewrite(argv)
            return answer if answer is not None else original(argv, cwd, env, timeout, stdin)

        return mock.patch.object(integrate, "run_process", wrapper)

    def unchanged(self) -> tuple[dict[str, str], str | None]:
        return (self.rig.refs(), self.rig.queue_sha())

    def assert_fault_and_nothing_written(self, result: Result, before: tuple[dict[str, str], str | None]) -> None:
        self.assertEqual((result.code, result.out), (2, ""), result.text)
        self.assertEqual(len(result.err_lines), 1, result.err)
        self.assertEqual(self.unchanged(), before)
        self.assertEqual(self.rig.states(), {"T1": "QUEUED"})
        self.assertEqual((self.rig.calls("spec"), self.rig.calls("invariant")), ([], []))
        self.assertClean(result)

    # ------------------------------------------------------------------ S50-10

    def test_a_malformed_candidate_that_is_the_parent_of_a_branch_tip_is_a_fault_not_a_bounce(self) -> None:
        tip = self.rig.tip()
        bad = self.bad_commit(tip)
        tree = git(self.rig.remote, "rev-parse", f"{tip}^{{tree}}")
        child = subprocess.run(
            ["git", "-C", str(self.rig.remote), "commit-tree", tree, "-p", bad, "-m", "child"],
            capture_output=True,
            check=True,
            env={**_clean_environment(), **GIT_IDENTITY},
        ).stdout.decode().strip()
        git(self.rig.remote, "update-ref", "refs/heads/cand-child", child)
        self.rig.publish({REVIEW: record_text(bad)}, "record of the bad candidate")
        self.rig.write_queue([self.rig.row("T1", bad)])
        before = self.unchanged()
        result = self.rig.land()
        self.assertIn("verified fetch failed for the candidate", result.err)
        self.assert_fault_and_nothing_written(result, before)

    def test_a_malformed_candidate_that_is_a_branch_tip_is_a_fault_not_a_bounce(self) -> None:
        bad = self.bad_commit(self.rig.tip())
        git(self.rig.remote, "update-ref", "refs/heads/cand-bad", bad)
        self.rig.publish({REVIEW: record_text(bad)}, "record of the bad candidate")
        self.rig.write_queue([self.rig.row("T1", bad)])
        before = self.unchanged()
        result = self.rig.land()
        self.assertIn("verified fetch", result.err)
        self.assert_fault_and_nothing_written(result, before)

    def test_every_other_failure_of_the_fetch_by_sha_is_a_fault_and_only_not_our_ref_is_a_bounce(self) -> None:
        first = self.rig.candidate()
        second = self.rig.commit({"src/more.py": "m\n"}, "more on the same branch", first)
        self.rig.push_seat(f"{second}:refs/heads/cand-1")
        self.rig.publish_record(first)
        self.rig.write_queue([self.rig.row("T1", first)])
        said = {
            "refused-unadvertised": f"error: Server does not allow request for unadvertised object {first}\n",
            "dropped": "fatal: unable to access: connection reset\n",
            "empty": "",
            "other-sha": f"fatal: remote error: upload-pack: not our ref {'0' * 40}\n",
        }
        for name, text in said.items():
            with self.subTest(name):

                def rewrite(argv: Sequence[str], text: str = text) -> integrate.Completed | None:
                    if "fetch" in argv and argv[-1] == first:
                        return integrate.Completed(128, b"", text.encode("utf-8"), False, None)
                    return None

                before = self.unchanged()
                with self.rewriting(rewrite):
                    result = self.rig.land()
                self.assert_fault_and_nothing_written(result, before)

    def test_the_remote_saying_it_does_not_hold_the_object_is_the_one_bounce(self) -> None:
        first = self.rig.candidate()
        second = self.rig.commit({"src/more.py": "m\n"}, "more on the same branch", first)
        self.rig.push_seat(f"{second}:refs/heads/cand-1")
        self.rig.publish_record(first)
        self.rig.write_queue([self.rig.row("T1", first)])

        def rewrite(argv: Sequence[str]) -> integrate.Completed | None:
            if "fetch" in argv and argv[-1] == first:
                return integrate.Completed(128, b"", f"fatal: remote error: upload-pack: not our ref {first}\n".encode("utf-8"), False, None)
            return None

        with self.rewriting(rewrite):
            result = self.rig.land()
        self.bounced_with(result, "MERGE_CONFLICT")

    # ------------------------------------------------------------------ S50-11

    def test_a_merge_tree_failure_other_than_a_conflict_is_a_fault_not_merge_conflict(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        self.assertEqual(self.rig.submit("T1", cand).code, 0)
        for code, text in ((129, "usage: git merge-tree <base-tree> <branch1> <branch2>\n"), (128, "fatal: something else\n"), (2, "")):
            with self.subTest(code):

                def rewrite(argv: Sequence[str], code: int = code, text: str = text) -> integrate.Completed | None:
                    if "merge-tree" in argv:
                        return integrate.Completed(code, b"", text.encode("utf-8"), False, None)
                    return None

                before = self.unchanged()
                with self.rewriting(rewrite):
                    result = self.rig.land()
                self.assert_fault_and_nothing_written(result, before)
                self.assertIn("merge-tree failed", result.err)
                if code == 129:
                    self.assertIn("2.38", result.err)

    # ------------------------------------------------------------------ S50-12

    def test_a_record_that_does_not_admit_is_decided_before_a_candidate_the_tip_already_holds(self) -> None:
        cand = self.rig.candidate()
        git(self.rig.seat, "checkout", "-q", "--detach", "--force", self.rig.tip())
        git(self.rig.seat, "merge", "-q", "--no-ff", "-m", "merge", cand)
        self.rig.push_seat(f"{self.rig.rev_seat('HEAD')}:refs/heads/{BRANCH}")
        self.rig.publish({REVIEW: record_text(cand, verdict="CHANGES_REQUESTED")}, "record that does not approve")
        self.rig.write_queue([self.rig.row("T1", cand)])
        result = self.rig.land()
        self.bounced_with(result, "REVIEW_MISMATCH")
        self.assertNotIn("ALREADY_LANDED", result.out)

    def test_a_record_that_admits_a_candidate_the_tip_already_holds_is_already_landed(self) -> None:
        cand = self.rig.candidate()
        git(self.rig.seat, "checkout", "-q", "--detach", "--force", self.rig.tip())
        git(self.rig.seat, "merge", "-q", "--no-ff", "-m", "merge", cand)
        self.rig.push_seat(f"{self.rig.rev_seat('HEAD')}:refs/heads/{BRANCH}")
        self.rig.publish_record(cand)
        self.rig.write_queue([self.rig.row("T1", cand)])
        self.bounced_with(self.rig.land(), "ALREADY_LANDED")

    # ------------------------------------------------------------------ S50-13

    def test_an_unadmitted_entry_with_a_malformed_candidate_is_review_mismatch_and_the_candidate_is_not_fetched(self) -> None:
        bad = self.bad_commit(self.rig.tip())
        git(self.rig.remote, "update-ref", "refs/heads/cand-bad", bad)
        self.rig.write_queue([self.rig.row("T1", bad)])
        seen: list[list[str]] = []

        def rewrite(argv: Sequence[str]) -> integrate.Completed | None:
            seen.append(list(argv))
            return None

        with self.rewriting(rewrite):
            result = self.rig.land()
        self.bounced_with(result, "REVIEW_MISMATCH")
        self.assertEqual(result.err, "")
        fetches = [argv for argv in seen if "fetch" in argv]
        self.assertEqual(len(fetches), 1, "only the branch and the queue branch are fetched before admission")
        self.assertFalse([argv for argv in fetches if "refs/heads/cand-bad" in argv or bad in argv])

    # ------------------------------------------------------------------ S50-14

    def version(self, text: str) -> contextlib.AbstractContextManager[object]:
        def rewrite(argv: Sequence[str]) -> integrate.Completed | None:
            if argv and argv[-1] == "version":
                return integrate.Completed(0, text.encode("utf-8"), b"", False, None)
            return None

        return self.rewriting(rewrite)

    def test_a_git_older_than_2_38_is_a_fault_that_names_the_requirement(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        self.assertEqual(self.rig.submit("T1", cand).code, 0)
        for text in ("git version 2.37.9.windows.1\n", "git version 1.99.0\n", "git version 2.9.5\n", "no version here\n", ""):
            with self.subTest(text):
                before = self.unchanged()
                with self.version(text):
                    result = self.rig.land()
                self.assert_fault_and_nothing_written(result, before)
                self.assertIn("git 2.38 or later", result.err)

    def test_git_2_38_and_later_pass_the_check_and_the_minor_number_is_compared_as_a_number(self) -> None:
        for index, text in enumerate(("git version 2.38.0\n", "git version 2.100.1\n", "git version 3.0.0\n")):
            with self.subTest(text):
                git(self.rig.seat, "fetch", "-q", str(self.rig.remote), f"refs/heads/{BRANCH}")
                cand = self.rig.candidate()
                self.rig.publish_record(cand, record_text(cand))
                self.assertEqual(self.rig.submit(f"V{index}", cand).code, 0)
                with self.version(text):
                    result = self.rig.land()
                self.assertEqual((result.code, result.err), (0, ""), result.text)
                self.rig.control("ci.answer", "green\n")
                self.assertEqual(self.rig.readback().code, 0)

    def test_the_version_is_not_asked_for_when_land_is_blocked_before_any_merge(self) -> None:
        self.rig.write_queue([self.rig.row("P1", self.rig.base, state="LANDED_PENDING_CI", landed_sha=self.rig.base)])
        with self.version("git version 1.0.0\n"):
            result = self.rig.land()
        self.assertEqual((result.code, result.err), (1, ""), result.text)
        self.assertEqual(result.codes, ["BLOCKED_BY_CI"])


class ConfigTests(RigCase):
    """Every configuration error is exit 3 naming the key; nothing is read from the remote."""

    def usage(self, raw: str | bytes, key: str | None = None) -> Result:
        self.rig.write_config(raw)
        result = self.rig.main("land", "--config", str(self.rig.config_path))
        self.assertEqual((result.code, result.out), (3, ""), result.text)
        self.assertEqual(result.err_lines[0], integrate.USAGE)
        self.assertEqual(len(result.err_lines), 2, result.err)
        if key is not None:
            self.assertIn(f"`{key}`", result.err)
        self.assertEqual(self.rig.tmp_left(), [])
        self.assertIsNone(self.rig.queue_sha())
        return result

    def changed(self, **changes: object) -> str:
        return json.dumps({**self.rig.config, **changes})

    def test_a_missing_key_is_named(self) -> None:
        for key in integrate.REQUIRED_CONFIG_KEYS:
            with self.subTest(key):
                document = {name: value for name, value in self.rig.config.items() if name != key}
                result = self.usage(json.dumps(document), key)
                self.assertIn("missing key", result.err)

    def test_an_unknown_key_is_named(self) -> None:
        result = self.usage(self.changed(extra="x"), "extra")
        self.assertIn("unknown key", result.err)

    def test_a_repeated_key_is_refused_naming_it(self) -> None:
        raw = self.changed().replace("{", '{"branch": "other", ', 1)
        result = self.usage(raw)
        self.assertIn("repeated key", result.err)
        self.assertIn("branch", result.err)

    def test_non_finite_numbers_are_refused(self) -> None:
        for name, literal in (("nan", "NaN"), ("inf", "Infinity"), ("minus-inf", "-Infinity"), ("overflow", "1e999")):
            with self.subTest(name):
                self.usage(self.changed(timeout_seconds=0).replace('"timeout_seconds": 0', f'"timeout_seconds": {literal}'))
                self.usage(self.changed(extra=0).replace('"extra": 0', f'"extra": {literal}'))

    def test_non_finite_numbers_name_the_key_that_holds_them(self) -> None:
        for name, literal in (("nan", "NaN"), ("inf", "Infinity"), ("minus-inf", "-Infinity"), ("overflow", "1e999")):
            with self.subTest(name):
                result = self.usage(self.changed(timeout_seconds=0).replace('"timeout_seconds": 0', f'"timeout_seconds": {literal}'), "timeout_seconds")
                self.assertIn("holds", result.err)
                result = self.usage(self.changed(extra=0).replace('"extra": 0', f'"extra": {literal}'), "extra")
                result = self.usage(self.changed(spec_command=["x"]).replace('["x"]', f'["x", {literal}]'), "spec_command")

    def test_control_characters_and_lone_surrogates_name_the_key_that_holds_them(self) -> None:
        for name, value, needle in (("tab", "a\\u0009b", "U+0009"), ("nul", "a\\u0000b", "U+0000"), ("delete", "a\\u007fb", "U+007F"), ("surrogate", "a\\ud800b", "U+D800")):
            with self.subTest(name):
                raw = self.changed().replace(f'"remote": {json.dumps(str(self.rig.remote))}', f'"remote": "{value}"')
                result = self.usage(raw, "remote")
                self.assertIn(needle, result.err)
                raw = self.changed(queue_path="x").replace('"queue_path": "x"', f'"queue_path": "{value}"')
                self.usage(raw, "queue_path")
                raw = self.changed(spec_command=["x"]).replace('["x"]', f'["x", "{value}"]')
                self.usage(raw, "spec_command")

    def test_a_key_that_holds_a_control_character_is_named_escaped(self) -> None:
        result = self.usage(self.changed(extra="x").replace('"extra"', '"ex\\u0009tra"'))
        self.assertIn("ex\\x09tra", result.err)
        self.assertIn("control character", result.err)

    def test_a_non_finite_number_outside_an_object_is_still_exit_three(self) -> None:
        result = self.usage("NaN")
        self.assertIn("NaN", result.err)

    def test_a_file_that_is_not_one_json_object_is_refused(self) -> None:
        for name, raw in (("empty", ""), ("list", "[]"), ("string", '"x"'), ("null", "null"), ("truncated", '{"remote": '), ("too-deep", '{"x": ' + "[" * 100000 + "}")):
            with self.subTest(name):
                self.usage(raw)

    def test_bytes_that_are_not_utf8_are_refused(self) -> None:
        self.usage(self.changed().encode("utf-8") + b"\xff")
        self.usage(self.changed().encode("utf-16"))

    def test_a_utf8_byte_order_mark_is_accepted(self) -> None:
        config = integrate.parse_config(b"\xef\xbb\xbf" + self.changed().encode("utf-8"))
        self.assertEqual(config.branch, BRANCH)

    def test_control_characters_and_lone_surrogates_are_refused(self) -> None:
        for name, value in (("tab", "a\\u0009b"), ("nul", "a\\u0000b"), ("delete", "a\\u007fb"), ("newline", "a\\nb"), ("surrogate", "a\\ud800b")):
            with self.subTest(name):
                raw = self.changed().replace(f'"remote": {json.dumps(str(self.rig.remote))}', f'"remote": "{value}"')
                self.usage(raw)
                self.usage(self.changed(extra="x").replace('"extra"', f'"ex{value}"'))

    def test_values_of_the_wrong_kind_are_named(self) -> None:
        cases: dict[str, list[object]] = {
            "remote": [1, "", None, ["x"], "-upload-pack=x"],
            "branch": [1, "", "bad name", "-x", "a..b", "a//b", "x.lock", "/x", "x/", ".x", "HEAD", "a b", "x.", "ü"],
            "queue_branch": [1, "", "a..b", BRANCH, "bad name"],
            "queue_path": [1, "", "a\\b", "../a", "a/../b", "./a", "a/./b", "/a", "C:/a", "c:a", "a/", "a//b", ":(top)a", "a" * 1100],
            "spec_command": ["x", [], [1], [""], None],
            "invariant_command": ["x", [], ["a", 1], [""], {}],
            "ci_status_command": ["x", [], ["prog"], ["prog", "x"], ["prog", "{sha}", "{sha}"], ["{sha}"], ["{sha}", "x"], ["prog", "a{sha}"], [1, "{sha}"]],
            "timeout_seconds": [0, -1, 1.5, True, False, "5", None, 86401, [5]],
        }
        for key, values in cases.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    self.usage(self.changed(**{key: value}), key)

    def test_the_queue_branch_defaults_and_the_timeout_defaults(self) -> None:
        document = {name: value for name, value in self.rig.config.items() if name not in ("timeout_seconds", "queue_branch")}
        config = integrate.parse_config(json.dumps(document).encode("utf-8"))
        self.assertEqual((config.queue_branch, config.timeout_seconds), (f"{BRANCH}-queue", 600))
        custom = integrate.parse_config(self.changed(queue_branch="queue/x", timeout_seconds=7).encode("utf-8"))
        self.assertEqual((custom.queue_branch, custom.timeout_seconds), ("queue/x", 7))
        self.assertEqual(custom.ci_status_command[-1], "{sha}")

    def test_a_custom_queue_branch_is_the_branch_that_is_written(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        self.rig.config["queue_branch"] = "q/custom"
        self.rig.write_config()
        self.assertEqual(self.rig.submit("T1", cand).code, 0)
        self.assertIn("refs/heads/q/custom", self.rig.refs())
        self.assertNotIn(f"refs/heads/{QUEUE_BRANCH}", self.rig.refs())


class ArgumentTests(RigCase):
    def usage(self, *args: str, needle: str | None = None) -> Result:
        result = self.rig.main(*args)
        self.assertEqual((result.code, result.out), (3, ""), result.text)
        self.assertEqual(result.err_lines[0], integrate.USAGE)
        self.assertEqual(len(result.err_lines), 2, result.err)
        if needle is not None:
            self.assertIn(needle, result.err)
        self.assertEqual(self.rig.tmp_left(), [])
        return result

    def submit_args(self, **changes: str | None) -> list[str]:
        values: dict[str, str | None] = {
            "--config": str(self.rig.config_path),
            "--ticket": "T1",
            "--candidate": "a" * 40,
            "--review": REVIEW,
            "--submitter": SUBMITTER,
        }
        values.update(changes)
        args = ["submit"]
        for name, value in values.items():
            if value is not None:
                args += [name, value]
        return args

    def test_no_subcommand_and_unknown_subcommands(self) -> None:
        self.usage()
        self.usage("push", "--config", "x")
        self.usage("--config", "x", "land")
        self.usage("LAND", "--config", "x")

    def test_the_config_option_is_required_single_and_valued(self) -> None:
        self.usage("land")
        self.usage("land", "--config")
        self.usage("land", "--config", "")
        self.usage("land", "--config", "a", "--config", "b")
        self.usage("land", "--config", "--config")

    def test_unknown_options_and_extra_arguments_are_refused(self) -> None:
        self.usage("land", "--config", "x", "--ticket", "T1", needle="--ticket")
        self.usage("readback", "--config", "x", "--force")
        self.usage("land", "--config", "x", "extra")
        self.usage("land", "-c", "x")
        self.usage("land", "--config=x")

    def test_every_submit_option_is_required(self) -> None:
        for name in ("--config", "--ticket", "--candidate", "--review", "--submitter"):
            with self.subTest(name):
                self.usage(*self.submit_args(**{name: None}))

    def test_a_ticket_is_one_plain_id(self) -> None:
        for value in ("", "T 1", "T@1", "T,1", "-T", "T/1", "x" * 129, "T\u00e9", "T" + LINE_SEPARATOR + "1"):
            with self.subTest(value):
                self.usage(*self.submit_args(**{"--ticket": value}))

    def test_a_candidate_is_a_full_lower_case_sha(self) -> None:
        for value in ("a" * 39, "a" * 41, "A" * 40, "g" * 40, "", "a" * 63, "a" * 65, " " + "a" * 40, "HEAD", "main"):
            with self.subTest(value):
                self.usage(*self.submit_args(**{"--candidate": value}))

    def test_a_review_path_is_canonical(self) -> None:
        for value in ("", "a\\b.md", "../a.md", "a/../b.md", "./a.md", "a/./b.md", "/a.md", "C:/a.md", "c:a.md", "a/", "a//b.md", ":(top)a.md", "x" * 1100):
            with self.subTest(value):
                self.usage(*self.submit_args(**{"--review": value}))

    def test_a_submitter_is_a_seat_id(self) -> None:
        for value in ("", "seat:a", "a/b", "seat:a/b/c", "seat:/b", "seat:a/", "seat:a b/c", "SEAT:a/b", "seat:a/b\u00e9"):
            with self.subTest(value):
                self.usage(*self.submit_args(**{"--submitter": value}))

    def test_clears_is_a_list_of_distinct_keys(self) -> None:
        sha = "b" * 40
        for value in ("", "T1", "T1@abc", f"T1@{sha},", f",T1@{sha}", f"T1@{sha},T1@{sha}", f"T 1@{sha}", f"T1@{sha.upper()}", f"@{sha}"):
            with self.subTest(value):
                self.usage(*self.submit_args(**{"--clears": value}))

    def test_a_repeated_option_is_refused(self) -> None:
        self.usage(*self.submit_args(), "--ticket", "T2", needle="twice")

    def test_a_candidate_of_the_wrong_width_for_the_repository_is_a_usage_error(self) -> None:
        self.usage(*self.submit_args(**{"--candidate": "a" * 64}), needle="hex digits")
        self.usage(*self.submit_args(**{"--clears": "T1@" + "b" * 64}), needle="hex digits")

    def test_control_characters_in_an_argument_are_refused_naming_its_place(self) -> None:
        for bad in ("a\tb", "a\x00b" if os.name != "nt" else "a\x01b", "a\x7fb", "a\ud800b"):
            with self.subTest(repr(bad)):
                self.usage("land", "--config", bad, needle="argument 3")

    def test_a_line_separator_in_an_argument_prints_on_one_line(self) -> None:
        result = self.usage("land", "--config", "x", "bad" + LINE_SEPARATOR + "arg" + NEXT_LINE)
        self.assertNotIn(LINE_SEPARATOR, result.text)
        self.assertNotIn(NEXT_LINE, result.text)

    def test_the_real_command_line_exits_three_with_two_lines_and_no_traceback(self) -> None:
        for args in ([], ["land"], ["land", "--config", "x", "y"]):
            result = self.rig.cli(*args)
            self.assertEqual((result.code, result.out), (3, ""), result.text)
            self.assertEqual(len(result.err_lines), 2 if args else 1 + 1, result.err)
            self.assertNotIn("Traceback", result.err)


class GitEnvironmentTests(LandCase):
    def test_the_environment_is_scrubbed_forced_and_fresh(self) -> None:
        inherited = {
            "GIT_DIR": "x",
            "GIT_WORK_TREE": "x",
            "GIT_INDEX_FILE": "x",
            "GIT_OBJECT_DIRECTORY": "x",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": "x",
            "GIT_COMMON_DIR": "x",
            "GIT_NAMESPACE": "x",
            "GIT_CEILING_DIRECTORIES": "x",
            "GIT_SHALLOW_FILE": "x",
            "GIT_REPLACE_REF_BASE": "x",
            "GIT_GRAFT_FILE": "inherited",
            "GIT_PREFIX": "x",
            "GIT_QUARANTINE_PATH": "x",
            "GIT_TEST_FSMONITOR": "x",
            "GIT_TEST_SOMETHING_NEW": "x",
            "GIT_CONFIG": "x",
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.bare",
            "GIT_CONFIG_VALUE_0": "true",
            "GIT_CONFIG_GLOBAL": "x",
            "GIT_CONFIG_SYSTEM": "x",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_PARAMETERS": "'core.bare=true'",
            "GIT_NO_REPLACE_OBJECTS": "0",
            "GIT_NO_LAZY_FETCH": "0",
            "GIT_AUTHOR_NAME": "kept",
            "PATH_KEPT": "kept",
        }
        with mock.patch.dict(os.environ, inherited):
            first = integrate.git_environment("C:/fresh/one")
            second = integrate.git_environment("C:/fresh/two")
        forced = {"GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_GRAFT_FILE"}
        for name in inherited:
            if name.startswith(("GIT_CONFIG", "GIT_TEST_")) or name in EVIDENCE_GATE_REMOVED:
                if name not in forced:
                    self.assertNotIn(name, first, name)
        self.assertEqual(first["GIT_CONFIG_NOSYSTEM"], "1")
        self.assertNotEqual(first["GIT_CONFIG_GLOBAL"], "x")
        self.assertFalse(os.path.exists(first["GIT_CONFIG_GLOBAL"]))
        self.assertNotEqual(first["GIT_CONFIG_GLOBAL"], second["GIT_CONFIG_GLOBAL"])
        self.assertEqual((first["GIT_NO_REPLACE_OBJECTS"], first["GIT_NO_LAZY_FETCH"]), ("1", "1"))
        self.assertEqual((first["GIT_GRAFT_FILE"], second["GIT_GRAFT_FILE"]), ("C:/fresh/one", "C:/fresh/two"))
        self.assertEqual((first["GIT_AUTHOR_NAME"], first["PATH_KEPT"]), ("kept", "kept"))

    def test_the_variable_names_match_in_any_letter_case(self) -> None:
        with mock.patch.dict(os.environ, {"git_dir": "x", "Git_Config_Count": "1"}):
            environment = integrate.git_environment("p")
        self.assertFalse([name for name in environment if name.upper() in {"GIT_DIR", "GIT_CONFIG_COUNT"}])

    def test_every_git_child_gets_the_options_the_ticket_names(self) -> None:
        cand, records = self.queued()
        seen: list[tuple[list[str], dict[str, str]]] = []
        original = integrate.run_process

        def spy(argv: Sequence[str], cwd: str, env: Mapping[str, str], timeout: float, stdin: bytes | None = None) -> integrate.Completed:
            seen.append((list(argv), dict(env)))
            return original(argv, cwd, env, timeout, stdin)

        with mock.patch.dict(os.environ, {"GIT_GRAFT_FILE": "inherited", "GIT_CONFIG_COUNT": "0"}):
            with mock.patch.object(integrate, "run_process", spy):
                self.assertEqual(self.rig.land(approving=records).code, 0)
        git_calls = [(argv, env) for argv, env in seen if os.path.basename(argv[0]).lower().startswith("git")]
        self.assertGreater(len(git_calls), 10)
        grafts: list[str] = []
        for argv, env in git_calls:
            self.assertEqual(argv[1], "--no-replace-objects", argv)
            pairs = list(zip(argv, argv[1:]))
            self.assertIn(("-c", "core.commitGraph=false"), pairs, argv)
            self.assertEqual((env["GIT_NO_REPLACE_OBJECTS"], env["GIT_NO_LAZY_FETCH"]), ("1", "1"))
            self.assertNotIn("GIT_CONFIG_COUNT", env)
            self.assertNotEqual(env["GIT_GRAFT_FILE"], "inherited")
            self.assertFalse(os.path.exists(env["GIT_GRAFT_FILE"]))
            grafts.append(env["GIT_GRAFT_FILE"])
        self.assertEqual(len(set(grafts)), len(grafts), "a fresh graft path for every child")

    def test_git_is_the_program_found_in_an_absolute_path_entry(self) -> None:
        cand, records = self.queued()
        exes: set[str] = set()
        original = integrate.run_process

        def spy(argv: Sequence[str], cwd: str, env: Mapping[str, str], timeout: float, stdin: bytes | None = None) -> integrate.Completed:
            exes.add(argv[0])
            return original(argv, cwd, env, timeout, stdin)

        with mock.patch.object(integrate, "run_process", spy):
            self.rig.land(approving=records)
        gits = {exe for exe in exes if os.path.basename(exe).lower().startswith("git")}
        self.assertEqual(len(gits), 1)
        self.assertTrue(os.path.isabs(next(iter(gits))))

    def test_inherited_selectors_change_nothing_for_a_real_run(self) -> None:
        cand = self.rig.candidate()
        self.rig.publish_record(cand)
        seat_head = git(self.rig.seat, "rev-parse", "HEAD")
        inherited = {
            "GIT_DIR": str(self.rig.seat / ".git"),
            "GIT_WORK_TREE": str(self.rig.seat),
            "GIT_INDEX_FILE": str(self.rig.root / "foreign-index"),
            "GIT_OBJECT_DIRECTORY": str(self.rig.seat / ".git" / "objects"),
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(self.rig.seat / ".git" / "objects"),
            "GIT_COMMON_DIR": str(self.rig.seat / ".git"),
            "GIT_NAMESPACE": "ns",
            "GIT_CEILING_DIRECTORIES": str(self.rig.root),
            "GIT_SHALLOW_FILE": str(self.rig.root / "shallow"),
            "GIT_REPLACE_REF_BASE": "refs/other/",
            "GIT_GRAFT_FILE": str(self.rig.root / "grafts"),
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.bare",
            "GIT_CONFIG_VALUE_0": "true",
            "GIT_CONFIG_PARAMETERS": "'core.bare=true'",
        }
        result = self.rig.cli(
            "submit", "--config", str(self.rig.config_path), "--ticket", "T1", "--candidate", cand, "--review", REVIEW, "--submitter", SUBMITTER,
            extra_env=inherited,
        )
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.assertEqual(self.rig.states(), {"T1": "QUEUED"})
        self.assertEqual(git(self.rig.seat, "rev-parse", "HEAD"), seat_head)
        self.assertEqual(git(self.rig.seat, "status", "--porcelain"), "")
        self.assertFalse((self.rig.root / "foreign-index").exists())

    def test_a_graft_file_in_the_environment_cannot_make_a_new_candidate_look_landed(self) -> None:
        cand, records = self.queued()
        self.rig.publish({"docs/newer.md": "newer\n"})
        tip = self.rig.tip()
        grafts = self.rig.root / "grafts"
        grafts.write_text(f"{tip} {cand}\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"GIT_GRAFT_FILE": str(grafts)}):
            result = self.rig.land(approving=records)
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.rig.assert_merge_of(self.rig.tip(), tip, cand)

    def test_a_replace_ref_in_the_remote_changes_nothing(self) -> None:
        cand, records = self.queued()
        decoy = self.rig.commit({"src/decoy.py": "d\n"}, "decoy", self.rig.base)
        self.rig.push_seat(f"{decoy}:refs/heads/decoy")
        git(self.rig.remote, "update-ref", f"refs/replace/{cand}", decoy)
        old_tip = self.rig.tip()
        result = self.rig.land(approving=records)
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.rig.assert_merge_of(self.rig.tip(), old_tip, cand)


class AffectedSpecTests(LandCase):
    def test_a_spec_names_a_path_on_segment_boundaries_not_as_a_prefix_or_suffix(self) -> None:
        specs = {
            "specs/test_a.py": "uses src/a.py here",
            "specs/test_b.py": "uses mysrc/a.py and src/a.pyc and src/a.py.bak",
            "specs/test_c.py": "uses ./src/a.py",
            "specs/test_d.py": "see (src/a.py).",
            "specs/test_e.py": "unrelated",
            "specs/test_f.py": "src/a.py-extra src/a.py_x",
        }
        self.assertEqual(integrate.affected_specs(["src/a.py"], specs, []), ["specs/test_a.py", "specs/test_c.py", "specs/test_d.py"])

    def test_a_changed_spec_is_affected_and_nothing_changed_affects_nothing(self) -> None:
        specs = {"specs/test_a.py": "x", "specs/test_b.py": "y"}
        self.assertEqual(integrate.affected_specs(["specs/test_b.py"], specs, []), ["specs/test_b.py"])
        self.assertEqual(integrate.affected_specs([], specs, []), [])
        self.assertEqual(integrate.affected_specs(["other"], {}, [integrate.Page(("other",))]), [])

    def test_a_page_owns_paths_by_segment(self) -> None:
        specs = {"specs/test_s.py": "x", "specs2/test_t.py": "y", "specs/sub/test_u.py": "z"}
        pages = [integrate.Page(("specs/", "src/page.py"))]
        self.assertEqual(integrate.affected_specs(["specs2/x.py"], specs, pages), [])
        self.assertEqual(integrate.affected_specs(["src/page.py"], specs, pages), ["specs/sub/test_u.py", "specs/test_s.py"])
        self.assertEqual(integrate.affected_specs(["specs/sub/x.py"], specs, pages), ["specs/sub/test_u.py", "specs/test_s.py"])
        self.assertEqual(integrate.affected_specs(["src/page.pyc"], specs, pages), [])
        self.assertEqual(integrate.affected_specs(["src/page.py/x"], specs, pages), [])

    def test_covers(self) -> None:
        self.assertTrue(integrate.covers("a/", "a/b"))
        self.assertTrue(integrate.covers("a/", "a/b/c"))
        self.assertFalse(integrate.covers("a/", "ab/c"))
        self.assertFalse(integrate.covers("a/", "a"))
        self.assertTrue(integrate.covers("a/b", "a/b"))
        self.assertFalse(integrate.covers("a/b", "a/bc"))
        self.assertFalse(integrate.covers("a/b", "a/b/c"))

    def test_the_page_registry_forms(self) -> None:
        self.assertEqual(integrate.parse_pages(b'[{"paths": ["a/", "b.py"]}]'), [integrate.Page(("a/", "b.py"))])
        self.assertEqual(integrate.parse_pages(b'{"pages": [{"page_id": "p", "paths": []}]}'), [integrate.Page(())])
        for raw in (b"{", b"1", b'{"pages": 1}', b'[1]', b'[{"paths": "a"}]', b'[{"paths": [1]}]', b'[{"paths": ["../a"]}]', b'[{"paths": ["/a"]}]',
                    b'[{"paths": ["a\\\\b"]}]', b'[{"paths": [""]}]', b'[{"paths": ["a", "a"], "x": NaN}]', b'\xff', b'[{"paths": ["a\\u0000"]}]'):
            with self.subTest(raw):
                with self.assertRaises(integrate.PagesError):
                    integrate.parse_pages(raw)

    def test_a_spec_listed_through_the_page_registry_is_passed_to_the_spec_command(self) -> None:
        self.rig.publish({"specs/test_b.py": "# no path named\n", "src/b.py": "b\n"})
        cand, records = self.queued(files={"src/b.py": "b2\n", "pages.json": json.dumps({"pages": [{"page_id": "b", "paths": ["src/b.py", "specs/test_b.py"]}]})})
        result = self.rig.land(approving=records)
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.assertEqual(self.rig.calls("spec"), [["specs/test_b.py"]])

    def test_without_a_registry_only_file_paths_decide(self) -> None:
        self.rig.publish({"specs/test_b.py": "# no path named\n", "src/b.py": "b\n"})
        cand, records = self.queued(files={"src/b.py": "b2\n"})
        self.assertEqual(self.rig.land(approving=records).code, 0)
        self.assertEqual(self.rig.calls("spec"), [])
        self.assertEqual(self.rig.calls("invariant"), [[]])

    def test_a_directory_entry_does_not_own_a_sibling_with_the_same_prefix(self) -> None:
        self.rig.publish({"specs/test_s.py": "# none\n", "specs2/test_t.py": "# none\n", "specs2/x.py": "x\n"})
        pages = json.dumps([{"paths": ["specs/"]}])
        cand, records = self.queued(files={"specs2/x.py": "x2\n", "pages.json": pages})
        self.assertEqual(self.rig.land(approving=records).code, 0)
        self.assertEqual(self.rig.calls("spec"), [])

    def test_a_directory_entry_owns_what_is_below_it(self) -> None:
        self.rig.publish({"specs/test_s.py": "# none\n", "specs/x.py": "x\n"})
        pages = json.dumps([{"paths": ["specs/"]}])
        cand, records = self.queued(files={"specs/x.py": "x2\n", "pages.json": pages})
        self.assertEqual(self.rig.land(approving=records).code, 0)
        self.assertEqual(self.rig.calls("spec"), [["specs/test_a.py", "specs/test_s.py"]])

    def test_a_registry_with_a_utf8_byte_order_mark_is_read(self) -> None:
        self.assertEqual(integrate.parse_pages(b"\xef\xbb\xbf" + b'[{"paths": ["a/", "b.py"]}]'), [integrate.Page(("a/", "b.py"))])
        with self.assertRaises(integrate.PagesError):
            integrate.parse_pages(b"\xef\xbb\xbf\xff")

    def test_a_candidate_whose_registry_starts_with_a_byte_order_mark_is_not_spec_red(self) -> None:
        self.rig.publish({"specs/test_b.py": "# no path named\n", "src/b.py": "b\n"})
        registry = "﻿" + json.dumps({"pages": [{"page_id": "b", "paths": ["src/b.py", "specs/test_b.py"]}]})
        cand = self.rig.candidate({"src/b.py": "b2\n", "pages.json": registry})
        self.rig.publish_record(cand)
        self.assertEqual(self.rig.submit("T1", cand).code, 0)
        result = self.rig.land()
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        self.assertEqual(self.rig.calls("spec"), [["specs/test_b.py"]])
        self.assertEqual(self.rig.states(), {"T1": "LANDED_PENDING_CI"})

    def test_a_malformed_registry_in_the_candidate_is_spec_red(self) -> None:
        cand, records = self.queued(files={"pages.json": '[{"paths": ["../x"]}]'})
        result = self.rig.land(approving=records)
        self.bounced_with(result, "SPEC_RED")
        self.assertIn("pages.json cannot be read", result.out)
        self.assertEqual(self.rig.calls("invariant"), [[]])

    def test_a_path_that_starts_with_a_hyphen_is_not_an_option(self) -> None:
        self.rig.publish({"-x/test_h.py": "# names src/a.py\n"})
        cand, records = self.queued(files={"src/a.py": "a = 11\n"})
        self.assertEqual(self.rig.land(approving=records).code, 0)
        self.assertEqual(self.rig.calls("spec"), [["./-x/test_h.py", "specs/test_a.py"]])

    def test_a_changed_path_that_is_not_clean_text_is_spec_red(self) -> None:
        base_tree = git(self.rig.seat, "rev-parse", f"{self.rig.tip()}^{{tree}}")
        env = {**_clean_environment(), **GIT_IDENTITY, "GIT_INDEX_FILE": str(self.rig.root / "raw-index")}
        blob = subprocess.run(["git", "-C", str(self.rig.seat), "hash-object", "-w", "--stdin"], input=b"x", capture_output=True, check=True).stdout.decode().strip()
        subprocess.run(["git", "-C", str(self.rig.seat), "read-tree", base_tree], check=True, env=env)
        raw_name = b"src/bad\x01name.py"
        subprocess.run(["git", "-c", "core.protectNTFS=false", "-C", str(self.rig.seat), "update-index", "-z", "--add", "--index-info"], input=f"100644 {blob}\t".encode() + raw_name + b"\0", check=True, env=env)
        tree = subprocess.run(["git", "-C", str(self.rig.seat), "write-tree"], capture_output=True, check=True, env=env).stdout.decode().strip()
        cand = subprocess.run(["git", "-C", str(self.rig.seat), "commit-tree", tree, "-p", self.rig.tip(), "-m", "odd name"], capture_output=True, check=True, env=env).stdout.decode().strip()
        self.rig.push_seat(f"{cand}:refs/heads/odd")
        self.rig.write_queue([self.rig.row("T1", cand)])
        result = self.rig.land(approving={REVIEW: record_text(cand)})
        self.bounced_with(result, "SPEC_RED")
        self.assertIn("control character", result.out)


class RecordedBehaviourTests(RigCase):
    def test_a_sha256_repository_works_end_to_end_and_a_sha1_width_is_a_usage_error(self) -> None:
        probe = subprocess.run(["git", "init", "-q", "--bare", "--object-format=sha256", str(self.rig.root / "probe.git")], capture_output=True)
        if probe.returncode != 0:
            self.skipTest("this git cannot make a sha256 repository")
        rig = Rig(self, "sha256")
        cand = rig.candidate()
        rig.publish_record(cand)
        self.assertEqual(len(cand), 64)
        result = rig.submit("T1", cand)
        self.assertEqual((result.code, result.err), (0, ""), result.text)
        wrong = rig.submit("T2", "a" * 40)
        self.assertEqual(wrong.code, 3, wrong.text)
        self.assertIn("hex digits", wrong.err)
        self.assertEqual([row["ticket"] for row in rig.entries()], ["T1"])
        records = {REVIEW: record_text(cand)}
        tip = rig.tip()
        landed = rig.land(approving=records)
        self.assertEqual((landed.code, landed.err), (0, ""), landed.text)  # the record commit moved the tip: the candidate is a sibling, merged
        merged = rig.tip()
        self.assertEqual(len(merged), 64)
        rig.assert_merge_of(merged, tip, cand)
        self.assertEqual((rig.entry("T1")["state"], rig.entry("T1")["landed_sha"]), ("LANDED_PENDING_CI", merged))
        self.assertEqual(rig.tmp_left(), [])


class OutputRuleTests(LandCase):
    def assertOneLines(self, result: Result) -> None:
        for char in result.text:
            self.assertTrue(char == "\n" or char.isprintable(), f"unescaped {char!r} in {result.text!r}")

    def test_a_verdict_with_line_breaking_characters_prints_on_one_line(self) -> None:
        cand = self.rig.candidate()
        text = record_text(cand).replace("verdict: APPROVED", "verdict: AP" + LINE_SEPARATOR + "PR" + NEXT_LINE + "OVED")
        self.rig.publish_record(cand, text)
        result = self.rig.submit("T1", cand)
        self.assertEqual(result.code, 1, result.text)
        self.assertEqual(len(result.out_lines), 1, result.out)
        self.assertIn("\\u2028", result.out)
        self.assertIn("\\x85", result.out)
        self.assertOneLines(result)

    def test_a_status_answer_with_line_breaking_characters_is_one_fault_line(self) -> None:
        sha = self.rig.candidate()
        self.rig.write_queue([self.rig.row("P1", sha, state="LANDED_PENDING_CI", landed_sha=sha)])
        self.rig.control("ci.answer", ("gr" + LINE_SEPARATOR + "een\nred\n").encode("utf-8"))
        result = self.rig.readback()
        self.assertEqual(result.code, 2, result.text)
        self.assertEqual(len(result.err_lines), 1, result.err)
        self.assertOneLines(result)

    def test_an_unknown_configuration_key_with_line_breaking_characters_prints_on_one_line(self) -> None:
        raw = json.dumps({**self.rig.config, "a" + LINE_SEPARATOR + "b" + NEXT_LINE: 1})
        self.rig.write_config(raw)
        result = self.rig.main("land", "--config", str(self.rig.config_path))
        self.assertEqual(result.code, 3, result.text)
        self.assertEqual(len(result.err_lines), 2, result.err)
        self.assertIn("a\\u2028b\\x85", result.err)
        self.assertOneLines(result)

    def test_a_remote_error_message_prints_on_one_line(self) -> None:
        self.rig.config["remote"] = str(self.rig.root / ("no" + LINE_SEPARATOR + "such.git"))
        self.rig.write_config()
        result = self.rig.land()
        self.assertEqual(result.code, 2, result.text)
        self.assertEqual(len(result.err_lines), 1, result.err)
        self.assertOneLines(result)

    def test_an_unwritable_standard_output_or_error_is_exit_two(self) -> None:
        class Broken(io.StringIO):
            def write(self, text: str) -> int:
                raise OSError("closed")

            def flush(self) -> None:
                raise OSError("closed")

        args = ["land", "--config", str(self.rig.config_path)]
        with mock.patch.object(tempfile, "tempdir", str(self.rig.tmp)):
            for name, out, err, argv in (
                ("stdout", Broken(), io.StringIO(), args),
                ("stderr", io.StringIO(), Broken(), ["land"]),
                ("none-out", None, io.StringIO(), args),
                ("none-err", io.StringIO(), None, ["land"]),
            ):
                with self.subTest(name):
                    with mock.patch.object(sys, "stdout", out), mock.patch.object(sys, "stderr", err):
                        self.assertEqual(integrate.main(argv), 2)
        cand, records = self.queued()
        self.rig.control("invariant.exit", "1")
        with mock.patch.object(tempfile, "tempdir", str(self.rig.tmp)), mock.patch.object(sys, "stdout", Broken()), mock.patch.object(sys, "stderr", io.StringIO()):
            with mock.patch.object(integrate.Integrator, "_record", lambda *_: record_text(cand).encode("utf-8")):
                self.assertEqual(integrate.main(args), 2, "a red that cannot be printed is exit 2")


class UnexpectedErrorTests(LandCase):
    def test_an_unexpected_error_is_one_fault_line_and_the_clone_is_removed(self) -> None:
        with mock.patch.object(integrate.Integrator, "_land", side_effect=RuntimeError("a\nb")):
            result = self.rig.land()
        self.assertEqual((result.code, result.out), (2, ""), result.text)
        self.assertEqual(result.err_lines, ["integrate.py: tool fault: unexpected RuntimeError: a\\x0ab"])
        self.assertClean(result)

    def test_an_interrupt_is_exit_two_without_a_traceback_and_removes_the_clone(self) -> None:
        for method in ("_land", "_submit", "_readback"):
            with self.subTest(method):
                with mock.patch.object(integrate.Integrator, method, side_effect=KeyboardInterrupt()):
                    if method == "_submit":
                        result = self.rig.submit("T1", "a" * 40)
                    else:
                        result = self.rig.main("land" if method == "_land" else "readback", "--config", str(self.rig.config_path))
                self.assertEqual((result.code, result.out), (2, ""), result.text)
                self.assertEqual(result.err_lines, ["integrate.py: tool fault: interrupted"])
                self.assertClean(result)

    def test_a_clone_that_cannot_be_removed_is_a_warning_and_changes_no_exit_code(self) -> None:
        with mock.patch.object(integrate, "remove_tree", lambda path: "the clone could not be removed"):
            result = self.rig.land()
        self.assertEqual((result.code, result.out), (0, "NOTHING_TO_LAND no admissible QUEUED entry\n"), result.text)
        self.assertIn("warning: the clone could not be removed", result.err)

    def test_a_failed_fetch_removes_the_clone_it_made(self) -> None:
        self.rig.config["remote"] = str(self.rig.root / "absent.git")
        self.rig.write_config()
        self.assertClean(self.rig.land())

    def test_the_report_decides_the_exit_code(self) -> None:
        report = integrate.Report()
        self.assertEqual(report.code, 0)
        report.fault("f")
        self.assertEqual(report.code, 2)
        report.red("X", "s", "d")
        self.assertEqual(report.code, 1)
        self.assertEqual(report.out, ["X s: d"])
        self.assertEqual(report.err, ["integrate.py: tool fault: f"])


class ResolveArgvZeroTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp(prefix="integ-argv-")).resolve()
        self.addCleanup(_force_remove, self.dir)

    def test_a_name_relative_to_a_drive_is_refused(self) -> None:
        with self.assertRaises(integrate.ArgvZeroError):
            integrate.resolve_argv0("C:relative.exe", str(self.dir))

    def test_an_absolute_name_is_used_as_given_and_a_relative_name_with_a_separator_is_joined(self) -> None:
        absolute = str(self.dir / "tool.exe")
        self.assertEqual(integrate.resolve_argv0(absolute, "elsewhere"), absolute)
        self.assertEqual(integrate.resolve_argv0("sub/tool.exe", str(self.dir)), os.path.abspath(os.path.join(str(self.dir), "sub/tool.exe")))
        self.assertEqual(integrate.resolve_argv0("sub\\tool.exe", str(self.dir)), os.path.abspath(os.path.join(str(self.dir), "sub\\tool.exe")))

    def test_batch_files_are_refused_in_any_letter_case(self) -> None:
        for name in ("a.bat", "a.CMD", "a.Bat", "a.cmd ", "a.bat."):
            with self.subTest(name):
                with self.assertRaises(integrate.ArgvZeroError):
                    integrate.resolve_argv0(str(self.dir / name), str(self.dir))

    def test_a_bare_name_is_found_in_absolute_path_entries_only(self) -> None:
        program = self.dir / ("prog.exe" if sys.platform == "win32" else "prog")
        program.write_text("x", encoding="utf-8")
        os.chmod(program, 0o755)
        with mock.patch.dict(os.environ, {"PATH": str(self.dir)}):
            self.assertEqual(os.path.normcase(integrate.resolve_argv0("prog", "elsewhere")), os.path.normcase(str(program)))
        cwd = os.getcwd()
        try:
            os.chdir(self.dir)
            with mock.patch.dict(os.environ, {"PATH": os.pathsep.join([".", ""])}):
                with self.assertRaises(integrate.ArgvZeroError):
                    integrate.resolve_argv0("prog", str(self.dir))
        finally:
            os.chdir(cwd)


class JsonAndQueueUnitTests(unittest.TestCase):
    def test_the_json_reader_refuses_what_the_ticket_names(self) -> None:
        for text in ('{"a": 1, "a": 2}', "NaN", "[Infinity]", "-Infinity", "1e999", "[" * 100000, "1" * 5000, "{", ""):
            with self.subTest(text[:20]):
                with self.assertRaises(integrate.JsonInputError):
                    integrate.parse_json(text)
        self.assertEqual(integrate.parse_json('{"a": [1, 2.5, "x", null, true]}'), {"a": [1, 2.5, "x", None, True]})

    def test_the_text_walk_finds_a_bad_character_in_a_key_or_a_nested_value(self) -> None:
        self.assertIsNone(integrate.first_bad_text({"a": ["b", {"c": "d"}]}))
        self.assertIn("control", integrate.first_bad_text({"a\x01": 1}) or "")
        self.assertIn("surrogate", integrate.first_bad_text([[["\ud800"]]]) or "")
        self.assertIn("control", integrate.first_bad_text({"a": [{"b": "x\x7f"}]}) or "")

    def test_the_queue_file_is_written_lf_only_and_reads_back(self) -> None:
        entry = integrate.QueueEntry("T1", "a" * 40, "b" * 40, "r.md", "a" * 40, "seat:a/b", "seat:c/d", "QUEUED", "", "", "")
        raw = integrate.serialize_queue([entry, entry.__class__(**{**entry.as_json(), "ticket": "T2"})])
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"\r", raw)
        self.assertEqual([item.ticket for item in integrate.parse_queue(raw, 40)], ["T1", "T2"])
        self.assertEqual(integrate.parse_queue(integrate.serialize_queue([]), 40), [])

    def test_the_review_checker_returns_every_problem_it_finds(self) -> None:
        candidate = "a" * 40
        text = record_text(candidate, "CHANGES_REQUESTED", reviewer="seat:x/y").encode("utf-8")
        check = integrate.check_review(text, candidate, "seat:x/y", "b" * 40, "seat:z/z")
        self.assertIsNone(check.verdict)
        self.assertGreaterEqual(len(check.problems), 4, check.problems)
        approved = integrate.check_review(record_text(candidate).encode("utf-8"), candidate, SUBMITTER, None, None)
        self.assertEqual((approved.problems, approved.verdict), ((), integrate.ReviewVerdict(candidate, "APPROVED", REVIEWER, "2026-11-05")))


class SourceRuleTests(unittest.TestCase):
    def test_the_script_and_its_tests_hold_none_of_the_forbidden_things(self) -> None:
        import ast

        for path in (SCRIPT, Path(__file__)):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)} | {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
            self.assertNotIn("Any", names, path.name)
            self.assertNotIn("type: " + "ignore", source, path.name)
            for word in ("cla" + "ude", "anthro" + "pic", "open" + "ai", "git" + "hub", "son" + "net", "op" + "us", "hai" + "ku", "cod" + "ex", "gem" + "ini"):
                self.assertNotIn(word, source.lower(), f"{path.name}: {word}")
        imports = {alias.name.split(".")[0] for node in ast.walk(ast.parse(SCRIPT.read_text(encoding="utf-8"))) if isinstance(node, ast.Import) for alias in node.names}
        imports |= {node.module.split(".")[0] for node in ast.walk(ast.parse(SCRIPT.read_text(encoding="utf-8"))) if isinstance(node, ast.ImportFrom) and node.module}
        self.assertLessEqual(imports, set(sys.stdlib_module_names) | {"__future__"})


class HookWriterTests(unittest.TestCase):
    def test_the_helper_writes_a_hook_with_lf_line_ends(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            hook = Path(raw) / "pre-receive"
            write_hook(hook, "#!/bin/sh\nexit 1\n")
            self.assertEqual(hook.read_bytes(), b"#!/bin/sh\nexit 1\n")

    @unittest.skipIf(
        os.name == "nt",
        "Windows keeps no POSIX mode bits (chmod there only toggles read-only) and Git for Windows runs a hook whatever its mode, "
        "so there is nothing to assert; the Linux job asserts the bit",
    )
    def test_the_helper_sets_the_owners_executable_bit_on_posix(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            hook = Path(raw) / "pre-receive"
            write_hook(hook, "#!/bin/sh\nexit 1\n")
            self.assertTrue(hook.stat().st_mode & stat.S_IXUSR, oct(hook.stat().st_mode))

    def test_no_hook_is_written_around_the_helper(self) -> None:
        offenders = [
            f"line {number}: {line.strip()}"
            for number, line in enumerate(Path(__file__).read_text(encoding="utf-8").splitlines(), 1)
            if "hoo" + "ks" in line and any(call in line for call in ("write" + "_text", "write" + "_bytes", "op" + "en("))
        ]
        self.assertEqual(offenders, [])


class ReadmeTests(unittest.TestCase):
    def test_the_readme_has_one_integrate_section_with_the_contract(self) -> None:
        readme = (_SCRIPTS / "README.md").read_text(encoding="utf-8")
        self.assertEqual(readme.count("\n## integrate.py\n"), 1)
        section = " ".join(readme.split("\n## integrate.py\n", 1)[1].split("\n## ", 1)[0].split())
        for phrase in (
            "Red before fault",
            "QUEUE_MOVED",
            "TIP_MOVED",
            "BLOCKED_BY_CI",
            "KEY_EXISTS",
            "MERGE_CONFLICT",
            "ALREADY_LANDED",
            "git push --atomic",
            "transfer.fsckObjects=true",
            "fetch.fsckObjects=true",
            "LANDED_PENDING_CI",
            "--no-replace-objects",
            "Merge landing",
        ):
            with self.subTest(phrase):
                self.assertIn(phrase, section)
