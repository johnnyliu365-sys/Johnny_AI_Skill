"""Report a poisoned runtime root once, instead of eighty times.

`DisposableEnvironmentAllocator` admits a provisioning request only when every
child of `tests/.johnny-runtime` is in `_CLAIMED_MARKERS`, which is a
module-level dict and therefore per-process. An orphan lease left by another
process is unclaimable by construction, so every provision is refused and
roughly eighty unrelated tests fail with `project-runtime provisioning must
succeed` — a message that names neither the cause nor the cure.

The refusal is correct and deliberate: `ADR-20260813-007` forbids deleting
residue whose ownership cannot be proven. This guard changes nothing about
that. It only makes the situation legible, and it deliberately runs first:
the file name sorts ahead of the suites that would otherwise fail in a heap.

An orphan appears when two `pytest` processes run against the same checkout
at once. If this guard fires, that is very likely what happened.
"""

from __future__ import annotations

import unittest
from pathlib import Path

_RUNTIME_ROOT = Path(__file__).resolve().parents[0] / ".johnny-runtime"


def orphan_leases(runtime_root: Path = _RUNTIME_ROOT) -> tuple[Path, ...]:
    """Lease directories present before this process provisioned anything.

    At import time no lease can legitimately exist: every claim lives in a
    per-process dict that is empty until the first provision. Anything here
    now belongs to a process that is gone.
    """

    if not runtime_root.is_dir():
        return ()
    try:
        return tuple(sorted(child for child in runtime_root.iterdir()))
    except OSError:
        return ()


_ORPHANS_AT_IMPORT = orphan_leases()


class ProjectRuntimeRootGuardTests(unittest.TestCase):
    def test_the_shared_runtime_root_is_not_poisoned(self) -> None:
        if not _ORPHANS_AT_IMPORT:
            return
        listing = "\n".join(f"    {path}" for path in _ORPHANS_AT_IMPORT)
        self.fail(
            "The project-owned test runtime root holds leases from a process "
            "that is gone, so every disposable-environment provisioning in "
            "this run will be refused and roughly eighty unrelated tests will "
            "fail with 'project-runtime provisioning must succeed'.\n\n"
            f"Orphan leases:\n{listing}\n\n"
            "This is not a code defect. The allocator refuses residue it "
            "cannot prove it owns, by design (ADR-20260813-007), and nothing "
            "deletes it automatically.\n\n"
            "Most likely cause: two pytest processes ran against this "
            "checkout at the same time.\n\n"
            f"Remedy: remove {_RUNTIME_ROOT} and run again."
        )


if __name__ == "__main__":
    unittest.main()
