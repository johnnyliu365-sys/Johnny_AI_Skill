"""Report a poisoned runtime root once, instead of eighty times.

`DisposableEnvironmentAllocator` admits a provisioning request only when every
child of `tests/.johnny-runtime` is in `_CLAIMED_MARKERS`, which is a
module-level dict and therefore per-process. An orphan lease left by another
process is unclaimable by construction, so every provision is refused and
roughly eighty unrelated tests fail with `project-runtime provisioning must
succeed` — a message that names neither the cause nor the cure.

Two separate things, easily conflated. The *refusal* is correct and
deliberate: `ADR-20260813-007` forbids deleting residue whose ownership
cannot be proven, and this guard changes nothing about that. The *orphan* is
not correct and never routine — it means a lease was created and never torn
down. Single-process runs do not leak, verified across repeated runs
including the tests that deliberately block teardown, so an orphan always
means something abnormal happened.

The known cause is two `pytest` processes running against the same checkout
at once; a crashed or killed run leaks the same way. The guard reports rather
than repairs, and it runs first: the file name sorts ahead of the suites that
would otherwise fail in a heap.
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
            "An orphan lease is never normal: it means a lease was created "
            "and never torn down. A single-process run does not leak, "
            "including the tests that deliberately block teardown, so if this "
            "fires something abnormal happened and is worth understanding "
            "before deleting the evidence.\n\n"
            "What is *not* a defect is the refusal itself: the allocator will "
            "not delete residue whose ownership it cannot prove "
            "(ADR-20260813-007), which is why nothing recovers automatically.\n\n"
            "Known cause: two pytest processes running against this checkout "
            "at the same time. A crashed or killed run can leak the same way. "
            "If neither happened, treat this as an unexplained leak and find "
            "out why before clearing it.\n\n"
            f"Remedy once understood: remove {_RUNTIME_ROOT} and run again."
        )


if __name__ == "__main__":
    unittest.main()
