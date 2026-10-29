"""Small temporary-Git fixtures shared by integration test modules."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from library.local_orchestration.document_mutation_gate import DocumentMutationRequest
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout

_TICKET = "modules/tickets/demo.md"
_MODULE_MAP = "shared/BOUNDARY_MAP.toml"


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


def _mapped_ticket(
    map_sha256: str,
    baseline: str,
    selected_modules: tuple[str, ...] = ("feature",),
) -> str:
    ticket = _ticket_text(
        modify=("doc/", "src/", "tests/", "scripts/", "shared/", "modules/"),
        create=("src/", "tests/", "scripts/", "shared/"),
    )
    selected = ", ".join(f'"{module_id}"' for module_id in selected_modules)
    return (
        ticket
        + "```johnny-module-boundary\n"
        + "schema_revision = 1\n"
        + f'map_sha256 = "{map_sha256}"\n'
        + f'baseline = "{baseline}"\n'
        + f"selected_modules = [{selected}]\n"
        + "```\n"
    )


def _mapped_map(baseline: str) -> str:
    return (
        "schema_revision = 1\n"
        'scope = "LOCAL_SOURCE_BOUNDARY"\n'
        f'baseline = "{baseline}"\n\n'
        '[[modules]]\nid = "feature"\nroots = ["src/feature.py"]\n'
        'owner = "feature-team"\nresponsibility = "Own the feature entry point."\n'
        'kind = "LIBRARY"\nallowed_dependencies = ["shared"]\n\n'
        '[[modules]]\nid = "shared"\nroots = ["src/shared.py"]\n'
        'owner = "platform-team"\nresponsibility = "Provide the shared normalization function."\n'
        'kind = "SHARED"\nallowed_dependencies = []\nshared_alias = "normalizer"\n\n'
        '[[modules]]\nid = "contract_tests"\nroots = ["tests/test_feature.py"]\n'
        'owner = "feature-tests"\nresponsibility = "Verify the feature contract."\n'
        'kind = "TEST"\nallowed_dependencies = ["feature"]\n\n'
        '[[modules]]\nid = "shell_entry"\nroots = ["scripts/run.ps1"]\n'
        'owner = "operations"\nresponsibility = "Run the bounded feature script."\n'
        'kind = "SCRIPT"\nallowed_dependencies = []\n'
    )


def _seed_mapped(
    base: Path,
    *,
    selected_modules: tuple[str, ...] = ("feature",),
    pin_digest: str | None = None,
    pin_baseline: str | None = None,
    map_baseline: str | None = None,
    include_map: bool = True,
) -> Path:
    root = _seed(
        base,
        _ticket_text(
            modify=("doc/", "src/", "tests/", "scripts/", "shared/", "modules/"),
            create=("src/", "tests/", "scripts/", "shared/"),
        ),
    )
    _write(root, "src/feature.py", "import src.shared\n")
    _write(root, "src/shared.py", "VALUE = 1\n")
    _write(root, "tests/test_feature.py", "def test_feature():\n    assert True\n")
    _write(root, "scripts/run.ps1", "Write-Output 'ready'\n")
    baseline = _commit(root, "seed module-source baseline")
    declared_baseline = map_baseline or baseline
    map_text = _mapped_map(declared_baseline)
    map_bytes = map_text.encode("utf-8")
    digest = hashlib.sha256(map_bytes).hexdigest()
    ticket = _mapped_ticket(
        pin_digest or digest,
        pin_baseline or declared_baseline,
        selected_modules,
    )
    _write(root, _TICKET, ticket)
    if include_map:
        map_path = root / _MODULE_MAP
        map_path.parent.mkdir(parents=True, exist_ok=True)
        map_path.write_bytes(map_bytes)
    _commit(root, "pin module map on integration branch")
    return root
