"""Wave-2 acceptance 1: one ticket end to end on a fixture project, finished by a fresh process from files alone.

In a temporary directory the test builds a fixture target project from `template/` (a git repository with a
local bare remote, a queue branch, an `integration.json` and a ticket) and drives the committed gate scripts,
each as a subprocess with no patch and no import, through one ticket:

1. `requirement_snapshot.py take` on a one-row requirement list;
2. a ticket written from the ticket template whose state row carries `dispatch=sha256:` of a dispatch file
   that `dispatch_lint.py` passes;
3. an implementation commit on a seat branch and a receipt built from the receipt template around a real
   capture, which `evidence_gate.py` passes;
4. a review record with a `review-verdict` block committed on the integration branch;
5. `integrate.py submit`, `land` and `readback`.

The loop is cut after step 3 (and, in a second case, after `submit`). The second half runs in a new Python
process (`python -I -X utf8 <script> <fixture path>`) that is given the fixture's path and nothing else. It
decides what is left from the ticket state row, the receipt and the queue file, and finishes the loop. The
harness asserts the launch line and the process's own report of what it was given, so a value carried over
from the first half is a red.

Everything here is stdlib only. The fixture and its remote live in a temporary directory removed after each
test. Nothing touches the network: the remote is a bare repository on the local disk.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import NamedTuple

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills" / "johnny-project-takeover" / "scripts"
TEMPLATE = REPO / "template"
PY = sys.executable

BRANCH = "main"
QUEUE_BRANCH = "main-queue"
SEAT_BRANCH = "seat/t-001"
TICKET_ID = "T-001"
SUBMITTER = "seat:impl/run-1"
GOVERNANCE = "doc/handoffs/2026/governance"
CONFIG_REL = f"{GOVERNANCE}/integration.json"
QUEUE_REL = f"{GOVERNANCE}/MERGE-QUEUE.json"
RECEIPT_REL = f"{GOVERNANCE}/receipt-{TICKET_ID}.md"
CAPTURE_REL = f"evidence/{TICKET_ID}-C1.txt"
TICKET_REL = f"modules/tickets/fixture/{TICKET_ID}.md"
DISPATCH_REL = f"modules/tickets/fixture/{TICKET_ID}.dispatch.yaml"
REVIEW_REL = f"doc/reviews/{TICKET_ID}.md"
TOOLS = ("src/feature.py", "tests/test_feature.py")

# The steps of the loop in order; the decision of the second process is one of these names.
STEPS = ("snapshot", "dispatch", "receipt", "review", "submit", "land", "readback")

EXIT_DONE, EXIT_RED, EXIT_REFUSED, EXIT_FAULT = 0, 1, 4, 5

SECOND_HALF = r'''
import json
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__SCRIPTS__)
ENV = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
ENV["PYTHONUTF8"] = "1"
REVIEWER = "seat:review/run-2"


class Stop(Exception):
    def __init__(self, code, reason, detail=""):
        Exception.__init__(self, reason)
        self.code, self.reason, self.detail = code, reason, detail


def run(args, cwd):
    done = subprocess.run(args, cwd=str(cwd), env=ENV, capture_output=True)
    return (
        done.returncode,
        done.stdout.decode("utf-8", "replace").replace("\r\n", "\n"),
        done.stderr.decode("utf-8", "replace").replace("\r\n", "\n"),
    )


def git(cwd, *args):
    base = ["git", "-c", "user.name=Resume Session", "-c", "user.email=resume@example.test",
            "-c", "core.autocrlf=false", "-c", "commit.gpgsign=false"]
    return run(base + list(args), cwd)


def must(result, what):
    if result[0] != 0:
        raise Stop(5, "FAULT", what + ": " + (result[2] or result[1]).strip()[:300])
    return result[1]


def row(text, name):
    found = re.search(r"^\| " + re.escape(name) + r" \| (.*) \|$", text, re.M)
    if found is None:
        raise Stop(4, "STATE_ROW_BROKEN", "no row " + name)
    return found.group(1)


def read_queue(fixture, config):
    branch = config["branch"]
    queue_branch = config.get("queue_branch", branch + "-queue")
    must(git(fixture, "fetch", "--quiet", "origin"), "git fetch origin")
    if git(fixture, "rev-parse", "--verify", "--quiet", "refs/remotes/origin/" + queue_branch)[0] != 0:
        return []
    shown = git(fixture, "show", "origin/" + queue_branch + ":" + config["queue_path"])
    if shown[0] != 0:
        return []
    try:
        entries = json.loads(shown[1])["entries"]
        if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
            raise ValueError("entries")
    except (ValueError, KeyError, TypeError):
        raise Stop(4, "QUEUE_BROKEN", "the queue file does not parse")
    return entries


def entry_for(entries, ticket, candidate):
    for entry in entries:
        if entry.get("ticket") == ticket and entry.get("candidate") == candidate:
            return entry
    return None


def main(report):
    if len(sys.argv) < 2:
        raise Stop(5, "FAULT", "no fixture path")
    fixture = Path(sys.argv[1]).resolve()
    tickets = sorted(p for p in (fixture / "modules" / "tickets").glob("*/*.md") if not p.name.upper().startswith("README"))
    if len(tickets) != 1:
        raise Stop(4, "TICKET_NOT_FOUND", str(len(tickets)) + " tickets")
    ticket = tickets[0]
    stem = ticket.stem
    ticket_text = ticket.read_text(encoding="utf-8")
    state_cell = row(ticket_text, "狀態")
    state = re.match(r"`([A-Z_]+)`", state_cell)
    if state is None:
        raise Stop(4, "STATE_ROW_BROKEN", "no state")
    if state.group(1) in ("DONE", "SUPERSEDED"):
        report.update(decision="none", outcome=state.group(1))
        return EXIT_DONE
    found = re.search(r"dispatch=sha256:([0-9a-f]{64}); receipt `([^`]+)`", state_cell)
    submitter = re.search(r"seat:[a-z]+/[A-Za-z0-9._-]+", row(ticket_text, "實作者"))
    if found is None or submitter is None:
        raise Stop(4, "STATE_ROW_BROKEN", "no dispatch digest, receipt path or implementer")
    digest, receipt_rel, submitter = found.group(1), found.group(2), submitter.group(0)

    dispatch = ticket.with_name(stem + ".dispatch.yaml")
    if not dispatch.is_file():
        raise Stop(4, "DISPATCH_MISSING", dispatch.name)
    if hashlib.sha256(dispatch.read_bytes()).hexdigest() != digest:
        raise Stop(4, "DISPATCH_DIGEST_MISMATCH", dispatch.name)

    receipt = (fixture / receipt_rel).resolve()
    if fixture not in receipt.parents or not receipt.is_file():
        raise Stop(4, "RECEIPT_MISSING", receipt_rel)
    receipt_text = receipt.read_text(encoding="utf-8")
    candidates = set(re.findall(r"^candidate: ([0-9a-f]{40})$", receipt_text, re.M))
    tools = sorted(set(re.findall(r"^- (\S+)=[0-9a-f]{64}$", receipt_text, re.M)))
    if len(candidates) != 1 or not tools:
        raise Stop(4, "RECEIPT_GATE_RED", "the receipt names no single candidate or no tool")
    candidate = candidates.pop()
    args = [sys.executable, str(SCRIPTS / "evidence_gate.py"), str(receipt), "--repo", str(fixture), "--candidate", candidate]
    for tool in tools:
        args += ["--tool", tool]
    gate = run(args, fixture)
    if gate[0] == 1:
        raise Stop(4, "RECEIPT_GATE_RED", gate[1].strip()[:300])
    if gate[0] != 0:
        raise Stop(5, "FAULT", "evidence gate: " + gate[2].strip()[:300])

    configs = sorted(fixture.glob("doc/handoffs/*/governance/integration.json"))
    if len(configs) != 1:
        raise Stop(4, "CONFIG_NOT_FOUND", str(len(configs)))
    config = json.loads(configs[0].read_text(encoding="utf-8"))
    branch = config["branch"]
    report["candidate"] = candidate
    entry = entry_for(read_queue(fixture, config), stem, candidate)
    if entry is None:
        decision = "review"
    elif entry["state"] == "QUEUED":
        decision = "land"
    elif entry["state"] == "LANDED_PENDING_CI":
        decision = "readback"
    else:
        decision = "none"
    report["decision"] = decision
    plan = {"review": ["review", "submit", "land", "readback"], "land": ["land", "readback"], "readback": ["readback"], "none": []}[decision]

    def integrate(command, *extra):
        return run([sys.executable, str(SCRIPTS / "integrate.py"), command, "--config", str(configs[0]), *extra], fixture)

    for step in plan:
        if step == "review":
            if must(git(fixture, "rev-parse", "--abbrev-ref", "HEAD"), "git rev-parse").strip() != branch:
                raise Stop(5, "FAULT", "the work tree is not on " + branch)
            must(git(fixture, "merge", "--ff-only", "origin/" + branch), "git merge --ff-only")
            review_rel = "doc/reviews/" + stem + ".md"
            if git(fixture, "cat-file", "-e", "origin/" + branch + ":" + review_rel)[0] != 0:
                target = fixture / review_rel
                target.parent.mkdir(parents=True, exist_ok=True)
                block = ("# Review of " + stem + "\n\n```review-verdict\ncandidate: " + candidate + "\nverdict: APPROVED\n"
                         "reviewer: " + REVIEWER + "\nreviewed_at: 2026-11-07\n```\n")
                target.write_bytes(block.encode("utf-8"))
                must(git(fixture, "add", "--", review_rel), "git add")
                must(git(fixture, "commit", "-q", "-m", "review record for " + stem), "git commit")
                must(git(fixture, "push", "-q", "origin", "HEAD:refs/heads/" + branch), "git push")
        elif step == "submit":
            done = integrate("submit", "--ticket", stem, "--candidate", candidate, "--review", "doc/reviews/" + stem + ".md", "--submitter", submitter)
        elif step == "land":
            done = integrate("land")
        else:
            done = integrate("readback")
        if step != "review":
            if done[0] == 1:
                raise Stop(4, step.upper() + "_REFUSED", done[1].strip()[:300])
            if done[0] != 0:
                raise Stop(5, "FAULT", step + ": " + done[2].strip()[:300])
        report["performed"].append(step)

    entry = entry_for(read_queue(fixture, config), stem, candidate)
    if entry is None:
        raise Stop(5, "FAULT", "the entry is gone")
    report["outcome"] = entry["state"]
    report["landed_sha"] = entry["landed_sha"]
    if entry["state"] == "LANDED":
        new_row = "| 狀態 | `DONE`; landed " + entry["landed_sha"] + ". |"
        ticket.write_bytes(re.sub(r"^\| 狀態 \| .* \|$", lambda _m: new_row, ticket_text, count=1, flags=re.M).encode("utf-8"))
    return EXIT_DONE if entry["state"] in ("LANDED", "CLEARED") else EXIT_RED


EXIT_DONE, EXIT_RED = 0, 1
report = {"argv_extra": len(sys.argv) - 2, "env_extra": sorted(k for k in os.environ if k.startswith("JAS61_")),
          "decision": None, "performed": [], "outcome": None, "reason": None, "detail": None, "candidate": None, "landed_sha": None}
try:
    code = main(report)
except Stop as stop:
    report.update(outcome="REFUSED" if stop.code == 4 else "FAULT", reason=stop.reason, detail=stop.detail)
    code = stop.code
except Exception as error:
    report.update(outcome="FAULT", reason="FAULT", detail=type(error).__name__ + ": " + str(error)[:300])
    code = 5
sys.stdout.write(json.dumps(report) + "\n")
sys.exit(code)
'''


class Done(NamedTuple):
    code: int
    out: str
    err: str


class SecondHalf(NamedTuple):
    code: int
    report: dict[str, object]
    err: str
    argv: list[str]
    extra_env: list[str]


def clean_environment() -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    env["PYTHONUTF8"] = "1"
    return env


def run(args: Sequence[str], cwd: Path | None = None, env: Mapping[str, str] | None = None) -> Done:
    done = subprocess.run(
        list(args), cwd=None if cwd is None else str(cwd), env=dict(env or clean_environment()), capture_output=True, check=False
    )
    return Done(
        done.returncode,
        done.stdout.decode("utf-8", "replace").replace("\r\n", "\n"),
        done.stderr.decode("utf-8", "replace").replace("\r\n", "\n"),
    )


def force_remove(path: Path) -> None:
    def writable(function: Callable[..., object], name: str, _: object) -> None:
        os.chmod(name, stat.S_IWRITE)
        function(name)

    shutil.rmtree(path, onerror=writable)


def script(name: str, *args: str) -> Done:
    return run([PY, str(SCRIPTS / name), *args])


def put(path: Path, text: str) -> None:
    """Write `text` with LF line ends and UTF-8, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def read_template(*parts: str) -> str:
    return (TEMPLATE.joinpath(*parts)).read_bytes().decode("utf-8").replace("\r\n", "\n")


def json_object(text: str) -> dict[str, object]:
    value: object = json.loads(text)
    if not isinstance(value, dict):
        raise AssertionError("not a JSON object")
    return {str(key): item for key, item in value.items()}


def string_field(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise AssertionError(f"{key} is not text in {data!r}")
    return value


def entries_of(text: str) -> list[dict[str, str]]:
    raw = json_object(text).get("entries")
    if not isinstance(raw, list):
        raise AssertionError("no entries list")
    rows: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise AssertionError("an entry is not an object")
        rows.append({str(key): str(value) for key, value in item.items()})
    return rows


def review_record(candidate: str, verdict: str = "APPROVED", reviewer: str = "seat:review/run-2") -> str:
    return (
        f"# Review of {candidate[:8]}\n\n```review-verdict\ncandidate: {candidate}\nverdict: {verdict}\n"
        f"reviewer: {reviewer}\nreviewed_at: 2026-11-07\n```\n"
    )


class Fixture:
    """A fixture target project built from `template/`: a work tree, a bare remote and a queue branch."""

    def __init__(self, case: unittest.TestCase, ci_answer: str = "green") -> None:
        self.root = Path(tempfile.mkdtemp(prefix="jas61-")).resolve()
        case.addCleanup(force_remove, self.root)
        self.work = self.root / "fixture"
        self.remote = self.root / "remote.git"
        self.aux = self.root / "aux"
        self.aux.mkdir()
        self.child = self.aux / "second_half.py"
        put(self.child, SECOND_HALF.replace("__SCRIPTS__", repr(str(SCRIPTS))))
        self.launches: list[list[str]] = []
        self.ci_answer = ci_answer
        self.base = ""
        self.candidate = ""
        self.dispatch_digest = ""
        self.build()

    # ------------------------------------------------------------------ plumbing

    def git(self, *args: str, cwd: Path | None = None, check: bool = True) -> str:
        done = run(
            ["git", "-c", "user.name=Fixture Seat", "-c", "user.email=seat@example.test", "-c", "core.autocrlf=false",
             "-c", "commit.gpgsign=false", *args],
            cwd=self.work if cwd is None else cwd,
        )
        if check and done.code != 0:
            raise AssertionError(f"git {args} failed: {done.err}")
        return done.out.strip()

    def remote_git(self, *args: str, check: bool = True) -> Done:
        done = run(["git", "--git-dir", str(self.remote), *args])
        if check and done.code != 0:
            raise AssertionError(f"git {args} on the remote failed: {done.err}")
        return done

    def remote_ref(self, ref: str) -> str | None:
        done = self.remote_git("rev-parse", "--verify", "--quiet", ref, check=False)
        return done.out.strip() if done.code == 0 else None

    def queue_text(self) -> str | None:
        done = self.remote_git("show", f"{QUEUE_BRANCH}:{QUEUE_REL}", check=False)
        return done.out if done.code == 0 else None

    def queue_entries(self) -> list[dict[str, str]]:
        text = self.queue_text()
        return [] if text is None else entries_of(text)

    def state(self) -> tuple[str | None, str | None]:
        """What a refusal must leave alone: the remote integration tip and the queue branch tip."""
        return self.remote_ref(f"refs/heads/{BRANCH}"), self.remote_ref(f"refs/heads/{QUEUE_BRANCH}")

    def parents(self, sha: str) -> list[str]:
        return self.remote_git("rev-list", "--parents", "-n", "1", sha).out.split()[1:]

    # ------------------------------------------------------------------ the fixture project

    def build(self) -> None:
        run(["git", "init", "-q", "--bare", "-b", BRANCH, str(self.remote)])
        self.work.mkdir()
        run(["git", "init", "-q", "-b", BRANCH, str(self.work)])
        self.git("config", "core.autocrlf", "false")
        self.git("remote", "add", "origin", str(self.remote))
        put(self.work / ".gitignore", ".v*.claim\n")
        for name, answer in (
            ("ci_green.py", 'print("green", end="")\n'),
            ("ci_red.py", 'print("red", end="")\n'),
            ("spec_ok.py", "import sys\nprint('specs', sys.argv[1:])\n"),
            ("invariant_ok.py", "print('invariants hold')\n"),
        ):
            put(self.work / "tools" / name, answer)
        self.step_snapshot()
        self.step_ticket_and_dispatch()
        self.write_config()
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "fixture base: requirement snapshot, ticket, dispatch, integration config")
        self.base = self.git("rev-parse", "HEAD")
        self.git("push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}")
        self.make_queue_branch()

    def make_queue_branch(self) -> None:
        """The queue branch holds the empty queue copied from the template, at `queue_path`; it is an orphan."""
        queue = self.root / "queue-init"
        queue.mkdir()
        run(["git", "init", "-q", "-b", QUEUE_BRANCH, str(queue)])
        put(queue / QUEUE_REL, read_template("doc", "handoffs", "governance", "MERGE-QUEUE.TEMPLATE.json"))
        self.git("add", "-A", cwd=queue)
        self.git("commit", "-q", "-m", "empty merge queue", cwd=queue)
        self.git("push", "-q", str(self.remote), f"HEAD:refs/heads/{QUEUE_BRANCH}", cwd=queue)

    def write_config(self) -> None:
        config = json_object(read_template("doc", "handoffs", "governance", "integration.TEMPLATE.json"))
        tools = (self.work / "tools").as_posix()
        values: dict[str, object] = {
            "remote": self.remote.as_posix(),
            "branch": BRANCH,
            "queue_branch": QUEUE_BRANCH,
            "queue_path": QUEUE_REL,
            "spec_command": [Path(PY).as_posix(), f"{tools}/spec_ok.py"],
            "invariant_command": [Path(PY).as_posix(), f"{tools}/invariant_ok.py"],
            "ci_status_command": [Path(PY).as_posix(), f"{tools}/ci_{self.ci_answer}.py", "{sha}"],
            "timeout_seconds": 120,
        }
        assert set(config) == set(values), "integration.TEMPLATE.json changed its keys"
        put(self.work / CONFIG_REL, json.dumps(values, indent=2) + "\n")

    @property
    def config_path(self) -> Path:
        return self.work / CONFIG_REL

    # ------------------------------------------------------------------ step 1: the requirement snapshot

    def step_snapshot(self) -> None:
        requirement = "# REQ-FIX-001\n\nThe fixture exposes an add function.\n"
        put(self.work / "doc/requirements/active/2026/fixture/REQ-FIX-001.md", requirement)
        rows = {
            "rows": [
                {
                    "requirement_id": "REQ-FIX-001",
                    "page_id": "fixture-page",
                    "title": "add function",
                    "type": "requirement",
                    "source_ref": "doc/requirements/active/2026/fixture/REQ-FIX-001.md",
                    "source_sha256": hashlib.sha256(requirement.encode("utf-8")).hexdigest(),
                    "status": "active",
                    "version": 1,
                }
            ]
        }
        put(self.aux / "rows.json", json.dumps(rows) + "\n")
        root = self.work / "doc" / "requirements" / "snapshots"
        taken = script(
            "requirement_snapshot.py", "take", "--source", "fixture-reqs", "--input", str(self.aux / "rows.json"),
            "--root", str(root), "--taken-at", "2026-11-07T00:00:00Z",
        )
        assert taken.code == 0, taken
        files = sorted((root / "fixture-reqs").glob("*-v1.json"))
        assert len(files) == 1, files
        verified = script("requirement_snapshot.py", "verify", str(files[0]))
        assert verified.code == 0, verified

    # ------------------------------------------------------------------ step 2: ticket and dispatch

    def step_ticket_and_dispatch(self) -> None:
        dispatch = (
            f'ticket: "{TICKET_REL}"\n'
            'role: "implementation_seat"\n'
            'summary: "add the feature function and the check that proves it"\n'
            "writable:\n"
            '  - "src/feature.py"\n'
            '  - "tests/test_feature.py"\n'
            "prohibited:\n"
            '  - "any other path"\n'
            "receipt:\n"
            f'  path: "{RECEIPT_REL}"\n'
        )
        put(self.work / DISPATCH_REL, dispatch)
        linted = script("dispatch_lint.py", str(self.work / DISPATCH_REL))
        assert linted.code == 0 and "LINT PASS" in linted.out, linted
        self.dispatch_digest = hashlib.sha256((self.work / DISPATCH_REL).read_bytes()).hexdigest()
        state = f"`IN_PROGRESS`; dispatch=sha256:{self.dispatch_digest}; receipt `{RECEIPT_REL}`."
        template = read_template("modules", "tickets", "TEMPLATE.md")
        lines = template.split("\n")
        replaced = {"title": 0, "state": 0, "implementer": 0, "change": 0}
        for index, line in enumerate(lines):
            if line.startswith("# NN"):
                lines[index], replaced["title"] = f"# {TICKET_ID}｜fixture feature", 1
            elif line.startswith("| 狀態 |"):
                lines[index], replaced["state"] = f"| 狀態 | {state} |", 1
            elif line.startswith("| 實作者 |"):
                lines[index], replaced["implementer"] = f"| 實作者 | {SUBMITTER} |", 1
            elif line.startswith("| 需求變更 |"):
                lines[index], replaced["change"] = "| 需求變更 | `CHG-20261107-001` |", 1
        assert all(replaced.values()), f"ticket template changed: {replaced}"
        put(self.work / TICKET_REL, "\n".join(lines))

    # ------------------------------------------------------------------ step 3: implementation and receipt

    def blob(self, sha: str, path: str) -> bytes:
        done = subprocess.run(["git", "-C", str(self.work), "show", f"{sha}:{path}"], capture_output=True, check=False)
        assert done.returncode == 0, done.stderr
        return done.stdout

    def step_implement(self) -> None:
        """An implementation commit on a seat branch, pushed so the integration clone can fetch it."""
        self.git("switch", "-q", "-c", SEAT_BRANCH, self.base)
        put(self.work / "src/feature.py", "def add(left: int, right: int) -> int:\n    return left + right\n")
        put(
            self.work / "tests/test_feature.py",
            "import sys\nfrom pathlib import Path\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n"
            "from src.feature import add\n\nassert add(2, 3) == 5\nprint('feature ok')\n",
        )
        self.git("add", "-A")
        self.git("commit", "-q", "-m", f"{TICKET_ID}: add the feature function and its check")
        self.candidate = self.git("rev-parse", "HEAD")
        self.git("push", "-q", "origin", f"HEAD:refs/heads/{SEAT_BRANCH}")
        checked = run([PY, "tests/test_feature.py"], cwd=self.work)
        assert checked.code == 0, checked
        capture = f"$ python tests/test_feature.py\n{checked.out}exit={checked.code}\n"
        self.git("switch", "-q", BRANCH)
        self.write_receipt(capture, str(checked.code))

    def write_receipt(self, capture: str, exit_codes: str) -> None:
        template = read_template("doc", "handoffs", "governance", "RECEIPT.TEMPLATE.md")
        cells = template[template.index("## <cell>\n"):]
        digests = "\n".join(f"- {path}={hashlib.sha256(self.blob(self.candidate, path)).hexdigest()}" for path in TOOLS)
        cells = cells.replace("- <tool-path>=<tool-sha256>", digests)
        cells = cells.replace("<cell>", "C1").replace("<candidate-sha>", self.candidate)
        cells = cells.replace("<capture-path>", CAPTURE_REL).replace("<exit-codes>", exit_codes)
        cells = cells.replace("<capture-lines>", capture[:-1])
        cells = cells.replace(
            "<statement-text>", "The capture is the output of the check at the candidate, run from the seat branch work tree."
        )
        assert not re.search(r"<[a-z-]+>", cells), "a placeholder is left in the receipt"
        put(self.work / GOVERNANCE / CAPTURE_REL, capture)
        put(self.work / RECEIPT_REL, f"# Receipt: {TICKET_ID} check at the candidate\n\n{cells}")

    def gate(self) -> Done:
        args = [str(self.work / RECEIPT_REL), "--repo", str(self.work), "--candidate", self.candidate, "--require-cell", "C1"]
        for path in TOOLS:
            args += ["--tool", path]
        return script("evidence_gate.py", *args)

    def first_half(self) -> None:
        """Steps 1 to 3 are done by the constructor; this adds the implementation, the receipt and the gate."""
        self.step_implement()
        passed = self.gate()
        assert passed.code == 0 and "defects=0" in passed.out, passed

    # ------------------------------------------------------------------ steps 4 and 5 by hand

    def sync_main(self) -> None:
        self.git("fetch", "-q", "origin")
        self.git("merge", "-q", "--ff-only", f"origin/{BRANCH}")

    def commit_record(self, rel: str, text: str) -> None:
        self.sync_main()
        put(self.work / rel, text)
        self.git("add", "--", rel)
        self.git("commit", "-q", "-m", f"review record {rel}")
        self.git("push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}")

    def integrate(self, command: str, *extra: str) -> Done:
        return script("integrate.py", command, "--config", str(self.config_path), *extra)

    def submit(self, ticket: str, candidate: str, review: str, submitter: str = SUBMITTER) -> Done:
        return self.integrate("submit", "--ticket", ticket, "--candidate", candidate, "--review", review, "--submitter", submitter)

    def reviewed_submit(self) -> Done:
        """Step 4 and the first part of step 5, as the first half would have done them."""
        self.commit_record(REVIEW_REL, review_record(self.candidate))
        return self.submit(TICKET_ID, self.candidate, REVIEW_REL)

    # ------------------------------------------------------------------ the second half

    def second_half(self) -> SecondHalf:
        """A new Python process given the fixture's path and nothing else; the report is its last stdout line."""
        argv = [PY, "-I", "-X", "utf8", str(self.child), str(self.work)]
        self.launches.append(argv)
        env = clean_environment()
        done = run(argv, env=env)
        lines = done.out.strip().splitlines()
        report = json_object(lines[-1]) if lines else {}
        extra = sorted(set(env) - set(clean_environment()))
        return SecondHalf(done.code, report, done.err, argv, extra)

    def ticket_state(self) -> str:
        found = re.search(r"^\| 狀態 \| `([A-Z_]+)`", (self.work / TICKET_REL).read_text(encoding="utf-8"), re.M)
        return "" if found is None else found.group(1)

    # ------------------------------------------------------------------ a second candidate (for the blocked land)

    def second_candidate(self) -> str:
        self.git("switch", "-q", "-c", "seat/t-002", self.base)
        put(self.work / "src/other.py", "OTHER = 2\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "T-002: another change")
        sha = self.git("rev-parse", "HEAD")
        self.git("push", "-q", "origin", "HEAD:refs/heads/seat/t-002")
        self.git("switch", "-q", BRANCH)
        return sha


class LoopCase(unittest.TestCase):
    """Shared assertions: what a finished loop leaves, read from the remote and from the files."""

    def assert_launched_from_the_path_alone(self, fixture: Fixture, half: SecondHalf) -> None:
        self.assertEqual(half.argv[-1], str(fixture.work))
        self.assertEqual(half.argv[1:5], ["-I", "-X", "utf8", str(fixture.child)])
        self.assertEqual(len(half.argv), 6, half.argv)
        self.assertEqual(half.extra_env, [], "the second process received an environment value of the harness")
        self.assertEqual(half.report.get("argv_extra"), 0, "the second process received an argument besides the path")
        self.assertEqual(half.report.get("env_extra"), [], "the second process saw a harness variable")

    def assert_landed(self, fixture: Fixture, half: SecondHalf, before: tuple[str | None, str | None]) -> None:
        self.assertEqual(half.code, EXIT_DONE, (half.report, half.err))
        self.assertEqual(half.report.get("outcome"), "LANDED")
        entries = fixture.queue_entries()
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual((entry["ticket"], entry["candidate"], entry["state"]), (TICKET_ID, fixture.candidate, "LANDED"))
        landed = entry["landed_sha"]
        tip = fixture.remote_ref(f"refs/heads/{BRANCH}")
        self.assertEqual(tip, landed, "the remote integration branch is not at the landed commit")
        parents = fixture.parents(landed)
        self.assertEqual(len(parents), 2, "the landed commit is not a merge commit")
        self.assertEqual(parents[1], fixture.candidate, "the second parent is not the candidate")
        first = parents[0]
        self.assertEqual(fixture.remote_git("merge-base", "--is-ancestor", str(before[0]), first, check=False).code, 0)
        record = fixture.remote_git("show", f"{first}:{REVIEW_REL}").out
        self.assertIn(f"candidate: {fixture.candidate}", record)
        self.assertEqual(half.report.get("landed_sha"), landed)
        self.assertEqual(fixture.ticket_state(), "DONE")

    def assert_nothing_landed(self, fixture: Fixture, before: tuple[str | None, str | None]) -> None:
        self.assertEqual(fixture.state(), before, "a refusal moved the integration tip or the queue branch")
        self.assertEqual(fixture.queue_entries(), [])


class FullLoopTests(LoopCase):
    def test_cut_after_the_receipt_is_finished_by_a_fresh_process_from_files_alone(self) -> None:
        fixture = Fixture(self)
        fixture.first_half()
        self.assertEqual(fixture.queue_entries(), [])
        before = fixture.state()
        half = fixture.second_half()
        self.assert_launched_from_the_path_alone(fixture, half)
        self.assertEqual(half.report.get("decision"), STEPS[3], "the process did not find the review to be the next step")
        self.assertEqual(half.report.get("performed"), list(STEPS[3:]))
        self.assertEqual(half.report.get("candidate"), fixture.candidate)
        self.assert_landed(fixture, half, before)

    def test_cut_after_submit_resumes_at_land(self) -> None:
        fixture = Fixture(self)
        fixture.first_half()
        submitted = fixture.reviewed_submit()
        self.assertEqual(submitted.code, 0, submitted)
        self.assertEqual([entry["state"] for entry in fixture.queue_entries()], ["QUEUED"])
        before = fixture.state()
        half = fixture.second_half()
        self.assert_launched_from_the_path_alone(fixture, half)
        self.assertEqual(half.report.get("decision"), STEPS[5], "the process did not find land to be the next step")
        self.assertEqual(half.report.get("performed"), list(STEPS[5:]))
        self.assertEqual(half.report.get("candidate"), fixture.candidate)
        self.assert_landed(fixture, half, before)

    def test_a_finished_ticket_leaves_nothing_for_a_third_process(self) -> None:
        fixture = Fixture(self)
        fixture.first_half()
        self.assertEqual(fixture.second_half().code, EXIT_DONE)
        landed = fixture.state()
        again = fixture.second_half()
        self.assertEqual((again.code, again.report.get("decision"), again.report.get("performed")), (EXIT_DONE, "none", []))
        self.assertEqual(fixture.state(), landed)

    def test_the_landed_merge_reads_back_green_through_the_scripts_alone(self) -> None:
        fixture = Fixture(self)
        fixture.first_half()
        self.assertEqual(fixture.reviewed_submit().code, 0)
        landed = fixture.integrate("land")
        self.assertEqual(landed.code, 0, landed)
        self.assertEqual([entry["state"] for entry in fixture.queue_entries()], ["LANDED_PENDING_CI"])
        half = fixture.second_half()
        self.assertEqual(half.report.get("decision"), STEPS[6])
        self.assertEqual(half.report.get("performed"), [STEPS[6]])
        self.assertEqual(half.code, EXIT_DONE, half)
        self.assertEqual([entry["state"] for entry in fixture.queue_entries()], ["LANDED"])


class RefusalTests(LoopCase):
    """The second process refuses on what the files say; nothing is landed."""

    def refused(self, fixture: Fixture, reason: str) -> SecondHalf:
        before = fixture.state()
        half = fixture.second_half()
        self.assertEqual(half.code, EXIT_REFUSED, (half.report, half.err))
        self.assertEqual(half.report.get("outcome"), "REFUSED")
        self.assertEqual(half.report.get("reason"), reason)
        self.assertEqual(half.report.get("performed"), [])
        self.assertNotIn("Traceback", half.err)
        self.assert_nothing_landed(fixture, before)
        self.assertNotEqual(fixture.ticket_state(), "DONE")
        return half

    def test_a_dispatch_file_that_no_longer_matches_the_digest_in_the_state_row_is_refused(self) -> None:
        fixture = Fixture(self)
        fixture.first_half()
        put(fixture.work / DISPATCH_REL, (fixture.work / DISPATCH_REL).read_text(encoding="utf-8") + "# edited after the digest\n")
        self.refused(fixture, "DISPATCH_DIGEST_MISMATCH")

    def test_a_receipt_that_fails_the_evidence_gate_is_refused(self) -> None:
        fixture = Fixture(self)
        fixture.first_half()
        capture = fixture.work / GOVERNANCE / CAPTURE_REL
        put(capture, capture.read_text(encoding="utf-8") + "edited after the receipt\n")
        self.assertEqual(fixture.gate().code, 1)
        self.refused(fixture, "RECEIPT_GATE_RED")

    def test_a_receipt_naming_a_stale_tool_digest_is_refused(self) -> None:
        fixture = Fixture(self)
        fixture.first_half()
        receipt = fixture.work / RECEIPT_REL
        text = receipt.read_text(encoding="utf-8")
        digest = hashlib.sha256(fixture.blob(fixture.candidate, TOOLS[0])).hexdigest()
        put(receipt, text.replace(digest, "0" * 64))
        self.refused(fixture, "RECEIPT_GATE_RED")

    def test_a_review_record_that_does_not_admit_the_candidate_lands_nothing(self) -> None:
        for name, record in (
            ("changes requested", review_record("0" * 40) + review_record("0" * 40, "APPROVED")),
            ("verdict not approved", review_record("{candidate}", "CHANGES_REQUESTED")),
            ("self review", review_record("{candidate}", reviewer=SUBMITTER)),
        ):
            with self.subTest(name):
                fixture = Fixture(self)
                fixture.first_half()
                fixture.commit_record(REVIEW_REL, record.replace("{candidate}", fixture.candidate))
                before = fixture.state()
                half = fixture.second_half()
                self.assertEqual(half.code, EXIT_REFUSED, (half.report, half.err))
                self.assertEqual(half.report.get("reason"), "SUBMIT_REFUSED")
                self.assertIn("REVIEW_MISMATCH", str(half.report.get("detail")))
                self.assertEqual(half.report.get("performed"), ["review"])
                self.assert_nothing_landed(fixture, before)

    def test_a_broken_state_row_is_a_refusal_not_a_crash(self) -> None:
        for name, damage in (
            ("no dispatch digest", lambda text: re.sub(r"dispatch=sha256:[0-9a-f]{64}; ", "", text)),
            ("no state word", lambda text: text.replace("`IN_PROGRESS`", "IN_PROGRESS")),
            ("no state row", lambda text: text.replace("| 狀態 |", "| status |")),
            ("short digest", lambda text: re.sub(r"sha256:([0-9a-f]{8})[0-9a-f]+", r"sha256:\1", text)),
        ):
            with self.subTest(name):
                fixture = Fixture(self)
                fixture.first_half()
                ticket = fixture.work / TICKET_REL
                broken = damage(ticket.read_text(encoding="utf-8"))
                self.assertNotEqual(broken, ticket.read_text(encoding="utf-8"))
                put(ticket, broken)
                self.refused(fixture, "STATE_ROW_BROKEN")

    def test_a_missing_receipt_is_a_refusal(self) -> None:
        fixture = Fixture(self)
        fixture.first_half()
        (fixture.work / RECEIPT_REL).unlink()
        self.refused(fixture, "RECEIPT_MISSING")


class FailClosedTests(LoopCase):
    def test_an_unreachable_remote_at_land_is_exit_two_and_the_queue_is_unchanged(self) -> None:
        fixture = Fixture(self)
        fixture.first_half()
        self.assertEqual(fixture.reviewed_submit().code, 0)
        before = fixture.state()
        queue = fixture.queue_text()
        gone = fixture.root / "remote.gone"
        fixture.remote.rename(gone)
        try:
            landed = fixture.integrate("land")
            half = fixture.second_half()
        finally:
            gone.rename(fixture.remote)
        self.assertEqual(landed.code, 2, landed)
        self.assertIn("tool fault", landed.err)
        self.assertEqual(half.code, EXIT_FAULT, (half.report, half.err))
        self.assertEqual(half.report.get("outcome"), "FAULT")
        self.assertEqual(fixture.state(), before)
        self.assertEqual(fixture.queue_text(), queue)
        self.assertEqual([entry["state"] for entry in fixture.queue_entries()], ["QUEUED"])

    def test_a_red_ci_answer_is_landed_ci_red_and_a_second_land_is_blocked(self) -> None:
        fixture = Fixture(self, ci_answer="red")
        fixture.first_half()
        half = fixture.second_half()
        self.assert_launched_from_the_path_alone(fixture, half)
        self.assertEqual(half.code, EXIT_RED, (half.report, half.err))
        self.assertEqual(half.report.get("outcome"), "LANDED_CI_RED")
        self.assertEqual(half.report.get("performed"), list(STEPS[3:]))
        self.assertEqual([entry["state"] for entry in fixture.queue_entries()], ["LANDED_CI_RED"])
        self.assertNotEqual(fixture.ticket_state(), "DONE", "a red CI answer was taken for a landed ticket")
        second = fixture.second_candidate()
        fixture.commit_record("doc/reviews/T-002.md", review_record(second, reviewer="seat:review/run-3"))
        submitted = fixture.submit("T-002", second, "doc/reviews/T-002.md", "seat:impl/run-4")
        self.assertEqual(submitted.code, 0, submitted)
        before = fixture.state()
        queue = fixture.queue_text()
        blocked = fixture.integrate("land")
        self.assertEqual(blocked.code, 1, blocked)
        self.assertIn("BLOCKED_BY_CI", blocked.out)
        self.assertEqual(fixture.state(), before)
        self.assertEqual(fixture.queue_text(), queue)

    def test_a_third_process_on_a_red_entry_reports_it_and_does_not_retry(self) -> None:
        fixture = Fixture(self, ci_answer="red")
        fixture.first_half()
        self.assertEqual(fixture.second_half().code, EXIT_RED)
        before = fixture.state()
        again = fixture.second_half()
        self.assertEqual((again.code, again.report.get("decision"), again.report.get("outcome")), (EXIT_RED, "none", "LANDED_CI_RED"))
        self.assertEqual(fixture.state(), before)


class RegressionTests(unittest.TestCase):
    def test_the_templates_and_scripts_the_loop_uses_exist_as_committed_files(self) -> None:
        for path in (
            TEMPLATE / "modules" / "tickets" / "TEMPLATE.md",
            TEMPLATE / "doc" / "handoffs" / "governance" / "RECEIPT.TEMPLATE.md",
            TEMPLATE / "doc" / "handoffs" / "governance" / "integration.TEMPLATE.json",
            TEMPLATE / "doc" / "handoffs" / "governance" / "MERGE-QUEUE.TEMPLATE.json",
            *(SCRIPTS / name for name in ("requirement_snapshot.py", "dispatch_lint.py", "evidence_gate.py", "integrate.py")),
        ):
            self.assertTrue(path.is_file(), path)

    def test_the_second_half_imports_nothing_from_the_repository_and_the_harness_imports_no_script(self) -> None:
        self.assertNotRegex(SECOND_HALF, r"(?m)^\s*(import|from)\s+(integrate|evidence_gate|dispatch_lint|requirement_snapshot|tests)\b")
        source = Path(__file__).read_text(encoding="utf-8")
        self.assertNotRegex(source, r"(?m)^\s*(import|from)\s+(integrate|evidence_gate|dispatch_lint|requirement_snapshot)\b")
        self.assertNotRegex(source, r"(?m)^\s*(?:import|from)\s+\S*mock")


if __name__ == "__main__":
    unittest.main()
