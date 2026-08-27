"""Private composition factory for the owned telemetry storage port."""

from __future__ import annotations

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.telemetry_storage.contracts import TelemetryStoragePort
from library.local_orchestration.telemetry_storage.johnny_owned_adapter import (
    JohnnyOwnedTelemetryStorageAdapter,
)
from library.local_orchestration.telemetry_storage.local_lock_adapter import (
    LocalTelemetryStorageLockAdapter,
)
from library.local_orchestration.telemetry_storage.ownership_ledger import (
    LocalTelemetryOwnershipLedger,
)


def compose_johnny_owned_telemetry_storage(
    layout: JohnnyRootLayout,
) -> TelemetryStoragePort:
    """Construct one fresh private storage graph for the supplied layout."""

    ledger = LocalTelemetryOwnershipLedger(layout)
    lock = LocalTelemetryStorageLockAdapter(layout)
    return JohnnyOwnedTelemetryStorageAdapter(layout, ledger, lock)


__all__ = ("compose_johnny_owned_telemetry_storage",)
