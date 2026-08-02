"""Reusable, profile-driven project workflow router POC."""

from .contracts import (
    ArtifactKind,
    ArtifactRef,
    AuthorityState,
    ConsumerFingerprint,
    DeliveryStage,
    ProcessStage,
    ReferenceStatus,
    RouterEvent,
    RouterEventKind,
    RouterOutcome,
    RouterState,
    SourceSnippet,
)
from .graph import build_router_graph
from .profile import build_router_poc_profile
from .router import CitationLedger, ContextResolver, InMemorySourceGateway, RouterEngine
from .telemetry import (
    AgentUsage,
    ContextLoadComparison,
    ContextLoadMeasurement,
    ContextLoadValidationReport,
    ContextSourceUsage,
    ContextUsageRecord,
    ContextUsageValidator,
    JsonlContextUsageStore,
    RunAcceptance,
    TelemetryIssueCode,
    TelemetryMode,
)

__all__ = (
    "ArtifactKind",
    "ArtifactRef",
    "AgentUsage",
    "AuthorityState",
    "CitationLedger",
    "ConsumerFingerprint",
    "ContextResolver",
    "ContextLoadComparison",
    "ContextLoadMeasurement",
    "ContextLoadValidationReport",
    "ContextSourceUsage",
    "ContextUsageRecord",
    "ContextUsageValidator",
    "DeliveryStage",
    "InMemorySourceGateway",
    "JsonlContextUsageStore",
    "ProcessStage",
    "ReferenceStatus",
    "RouterEngine",
    "RouterEvent",
    "RouterEventKind",
    "RouterOutcome",
    "RouterState",
    "RunAcceptance",
    "SourceSnippet",
    "TelemetryIssueCode",
    "TelemetryMode",
    "build_router_graph",
    "build_router_poc_profile",
)
