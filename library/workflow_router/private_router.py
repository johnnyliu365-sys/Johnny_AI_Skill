"""Metadata-only Private Router POC with safe automatic continuation planning.

This module is deliberately an in-process, test-only boundary.  A later approved MVP
may replace ``RouterServicePort`` with a protected remote transport, but no source text,
URI, path, prompt, or ContextPacket crosses this boundary here.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from typing import Annotated, Literal, Protocol
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field, ValidationError, model_validator

from .contracts import (
    ArtifactKind,
    ArtifactRef,
    AuthorityState,
    ConsumerFingerprint,
    ContinuationDirective,
    DeliveryStage,
    NonBlankText,
    PositiveTokenBudget,
    ProcessStage,
    ResolvedContext,
    RouterEvent,
    RouterEventKind,
    RouterModel,
    RouterOutcome,
    RouterState,
)
from .profile import ProjectWorkflowProfile
from .router import ContextResolver, RouterEngine


OpaqueAccountSubjectId = Annotated[str, Field(pattern=r"^acct_[0-9a-f]{16}$")]
OpaqueProjectId = Annotated[str, Field(pattern=r"^prj_[0-9a-f]{16}$")]
OpaqueRequestId = Annotated[str, Field(pattern=r"^req_[0-9a-f]{32}$")]
OpaqueDecisionId = Annotated[str, Field(pattern=r"^dec_[0-9a-f]{32}$")]
OpaqueEventId = Annotated[str, Field(pattern=r"^evt_[0-9a-f]{32}$")]
RevisionDigest = Annotated[str, Field(pattern=r"^rev_[0-9a-f]{64}$")]
ClientVersion = Annotated[str, Field(pattern=r"^v[1-9][0-9]*$")]


class EntitlementMode(str, Enum):
    """The POC's closed entitlement categories; this is not payment processing."""

    FIRST_PROJECT_FREE = "first_project_free"
    STANDARD_PROJECT = "standard_project"
    ACTIVE_AUDIT = "active_audit"
    DENIED = "denied"


class RouterServiceErrorCode(str, Enum):
    """Stable public error codes that reveal no Profile or source detail."""

    ROUTER_INPUT_INVALID = "router_input_invalid"
    ROUTER_ENTITLEMENT_DENIED = "router_entitlement_denied"
    ROUTER_SERVICE_UNAVAILABLE = "router_service_unavailable"
    ROUTER_RESPONSE_INVALID = "router_response_invalid"
    ROUTER_POLICY_BLOCKED = "router_policy_blocked"


class ProductActionLabel(str, Enum):
    """Product-language labels.  Internal stage and Profile names are never UI labels."""

    DEFINE_STARTING_POINT = "define_starting_point"
    SHAPE_SOLUTION = "shape_solution"
    CONFIRM_ASSUMPTIONS = "confirm_assumptions"
    ORGANIZE_WORKSPACE = "organize_workspace"
    DRAFT_DELIVERY_PLAN = "draft_delivery_plan"
    PLAN_EXECUTION = "plan_execution"
    BUILD_AND_TEST = "build_and_test"
    VERIFY_DELIVERY = "verify_delivery"
    COMPLETE_HANDOFF = "complete_handoff"
    REQUEST_APPROVAL = "request_approval"


class ContinuationMode(str, Enum):
    """Local execution disposition after a validated private Router response."""

    AUTO_RUN = "auto_run"
    WAIT_FOR_HUMAN = "wait_for_human"
    HALT = "halt"


class RedactedSummary(RouterModel):
    """A finite, content-free summary; free prose and arbitrary dictionaries are impossible."""

    evidence_codes: tuple[Literal["goal_captured", "evidence_available", "validation_recorded"], ...]
    risk_codes: tuple[Literal["none", "requires_review", "external_dependency"], ...]
    source_count_bucket: Annotated[int, Field(ge=0, le=100)]

    @model_validator(mode="after")
    def has_at_least_one_finite_claim(self) -> RedactedSummary:
        """Reject empty summaries rather than treating missing evidence as a safe default."""

        if not self.evidence_codes and not self.risk_codes and self.source_count_bucket == 0:
            raise ValueError("structured_redacted_summary must contain a finite claim")
        return self


class RouterRequestEnvelope(RouterModel):
    """The complete local-to-private boundary; every field is typed and allowlisted."""

    request_id: OpaqueRequestId
    account_subject_id: OpaqueAccountSubjectId
    opaque_project_id: OpaqueProjectId
    project_entry_mode: Literal[
        "new_project", "inherited_audit", "repair", "deployment_preparation"
    ]
    entitlement_mode: EntitlementMode
    workflow_stage: ProcessStage
    authority_state: AuthorityState
    delivery_stage: DeliveryStage
    router_event_kind: RouterEventKind
    event_correlation_id: OpaqueEventId
    available_source_kinds: tuple[ArtifactKind, ...]
    revision_digests: tuple[RevisionDigest, ...]
    structured_redacted_summary: RedactedSummary
    client_version: ClientVersion

    @model_validator(mode="after")
    def has_minimum_metadata_without_locations(self) -> RouterRequestEnvelope:
        """Require finite availability and digest metadata before the request may travel."""

        if not self.available_source_kinds:
            raise ValueError("available_source_kinds must not be empty")
        if not self.revision_digests:
            raise ValueError("revision_digests must not be empty")
        if len(set(self.available_source_kinds)) != len(self.available_source_kinds):
            raise ValueError("available_source_kinds must not repeat")
        if len(set(self.revision_digests)) != len(self.revision_digests):
            raise ValueError("revision_digests must not repeat")
        return self


class RouterResponseEnvelope(RouterModel):
    """The service response contains only a safe action and metadata-only grants."""

    request_id: OpaqueRequestId
    decision_id: OpaqueDecisionId
    outcome: RouterOutcome
    continuation: ContinuationDirective
    next_stage: ProcessStage | None
    action_label: ProductActionLabel | None
    allowed_action_labels: tuple[ProductActionLabel, ...]
    required_source_kinds: tuple[ArtifactKind, ...]
    context_budget: PositiveTokenBudget | None
    error_code: RouterServiceErrorCode | None = None

    @model_validator(mode="after")
    def response_shape_is_safe_and_unambiguous(self) -> RouterResponseEnvelope:
        """Reject responses that could accidentally grant work after a failure."""

        if self.continuation is ContinuationDirective.AUTO_CONTINUE:
            if self.outcome not in (RouterOutcome.ADVANCE, RouterOutcome.RETRY):
                raise ValueError("automatic continuation requires an advancing decision")
            if self.next_stage is None or self.action_label is None or self.context_budget is None:
                raise ValueError("automatic continuation requires a complete local grant")
            if self.allowed_action_labels != (self.action_label,):
                raise ValueError("automatic continuation must grant exactly its displayed action")
            if self.error_code is not None:
                raise ValueError("automatic continuation cannot carry an error code")
        elif self.continuation is ContinuationDirective.WAIT_FOR_HUMAN:
            if self.outcome is not RouterOutcome.SUSPEND:
                raise ValueError("human waits must be suspensions")
            if self.next_stage is not None or self.action_label is not ProductActionLabel.REQUEST_APPROVAL:
                raise ValueError("human waits must expose only the approval action")
            if self.allowed_action_labels or self.context_budget is not None or self.error_code is not None:
                raise ValueError("human waits cannot grant execution or report a service failure")
        else:
            if self.allowed_action_labels or self.context_budget is not None:
                raise ValueError("halted responses cannot grant capabilities or Context")
            if self.action_label is not None:
                raise ValueError("halted responses cannot invent a next action")
            if self.error_code is None:
                raise ValueError("halted responses require a stable error code")
        return self


class EntitlementGrant(RouterModel):
    """A test-only typed entitlement record; it holds no account secret or payment detail."""

    account_subject_id: OpaqueAccountSubjectId
    opaque_project_id: OpaqueProjectId
    permitted_modes: tuple[EntitlementMode, ...]

    @model_validator(mode="after")
    def grant_has_at_least_one_mode(self) -> EntitlementGrant:
        """Reject an ambiguous empty grant."""

        if not self.permitted_modes:
            raise ValueError("permitted_modes must not be empty")
        return self


class EntitlementPort(Protocol):
    """Private entitlement boundary; a future service replaces this fake implementation."""

    def permits(self, *, request: RouterRequestEnvelope) -> bool:
        """Return whether the metadata-only request is entitled to use the product path."""


class FakeEntitlementProvider:
    """In-memory POC entitlement provider with exact opaque identity comparison."""

    def __init__(self, *, grants: tuple[EntitlementGrant, ...]) -> None:
        self._grants = grants

    def permits(self, *, request: RouterRequestEnvelope) -> bool:
        """Permit only an exact account, project, and declared mode match."""

        if request.entitlement_mode is EntitlementMode.DENIED:
            return False
        return any(
            grant.account_subject_id == request.account_subject_id
            and grant.opaque_project_id == request.opaque_project_id
            and request.entitlement_mode in grant.permitted_modes
            for grant in self._grants
        )


class RouterServicePort(Protocol):
    """The only client-facing private Router boundary in this POC."""

    def decide(self, request: RouterRequestEnvelope) -> object:
        """Return a serialized response shape from the private decision service."""


class FakePrivateRouterService:
    """Test-only service stand-in that keeps the Profile evaluation behind a port."""

    def __init__(
        self,
        *,
        profile: ProjectWorkflowProfile,
        entitlement_provider: EntitlementPort,
        context_budget: PositiveTokenBudget = 1_000,
    ) -> None:
        self._profile = profile
        self._entitlement_provider = entitlement_provider
        self._context_budget = context_budget
        self._captured_requests: list[RouterRequestEnvelope] = []
        self.request_count = 0

    def decide(self, request: RouterRequestEnvelope) -> RouterResponseEnvelope:
        """Evaluate only strictly validated metadata and return a typed public projection."""

        self.request_count += 1
        self._captured_requests.append(request)
        decision_id = self._decision_id(request=request)
        if not self._entitlement_provider.permits(request=request):
            return self._halted_response(
                request_id=request.request_id,
                decision_id=decision_id,
                outcome=RouterOutcome.SUSPEND,
                error_code=RouterServiceErrorCode.ROUTER_ENTITLEMENT_DENIED,
            )
        decision = RouterEngine().decide(
            state=RouterState(
                project_id=request.opaque_project_id,
                stage=request.workflow_stage,
                authority_state=request.authority_state,
                delivery_stage=request.delivery_stage,
                artifact_refs=self._private_artifact_refs(request=request),
            ),
            event=RouterEvent(event_id=request.event_correlation_id, kind=request.router_event_kind),
            profile=self._profile,
        )
        if decision.continuation is ContinuationDirective.AUTO_CONTINUE:
            assert decision.next_stage is not None
            action_label = self._action_for(stage=decision.next_stage)
            return RouterResponseEnvelope(
                request_id=request.request_id,
                decision_id=decision_id,
                outcome=decision.outcome,
                continuation=decision.continuation,
                next_stage=decision.next_stage,
                action_label=action_label,
                allowed_action_labels=(action_label,),
                required_source_kinds=tuple(source.kind for source in decision.required_sources),
                context_budget=self._context_budget,
            )
        if decision.continuation is ContinuationDirective.WAIT_FOR_HUMAN:
            return RouterResponseEnvelope(
                request_id=request.request_id,
                decision_id=decision_id,
                outcome=RouterOutcome.SUSPEND,
                continuation=ContinuationDirective.WAIT_FOR_HUMAN,
                next_stage=None,
                action_label=ProductActionLabel.REQUEST_APPROVAL,
                allowed_action_labels=(),
                required_source_kinds=(),
                context_budget=None,
            )
        return self._halted_response(
            request_id=request.request_id,
            decision_id=decision_id,
            outcome=decision.outcome,
            error_code=RouterServiceErrorCode.ROUTER_POLICY_BLOCKED,
        )

    def captured_requests_json(self) -> str:
        """Expose POC test evidence only; it serializes no local source or ContextPacket."""

        return "\n".join(request.model_dump_json() for request in self._captured_requests)

    def _private_artifact_refs(self, *, request: RouterRequestEnvelope) -> tuple[ArtifactRef, ...]:
        """Convert source-kind availability to private synthetic refs without receiving locators."""

        return tuple(
            ArtifactRef(
                kind=kind,
                identifier=f"available-{kind.value}",
                uri=f"private://availability/{kind.value}",
                revision="metadata-only",
            )
            for kind in request.available_source_kinds
        )

    def _decision_id(self, *, request: RouterRequestEnvelope) -> OpaqueDecisionId:
        """Make retries stable while ensuring a different event yields a different opaque ID."""

        seed = "\x1f".join(
            (
                request.account_subject_id,
                request.opaque_project_id,
                request.event_correlation_id,
                self._profile.profile_id,
                self._profile.profile_version,
            )
        )
        return f"dec_{uuid5(NAMESPACE_URL, seed).hex}"

    @staticmethod
    def _halted_response(
        *,
        request_id: OpaqueRequestId,
        decision_id: OpaqueDecisionId,
        outcome: RouterOutcome,
        error_code: RouterServiceErrorCode,
    ) -> RouterResponseEnvelope:
        """Create the one non-grant response shape."""

        return RouterResponseEnvelope(
            request_id=request_id,
            decision_id=decision_id,
            outcome=outcome,
            continuation=ContinuationDirective.HALT,
            next_stage=ProcessStage.STOPPED if outcome is RouterOutcome.STOP else None,
            action_label=None,
            allowed_action_labels=(),
            required_source_kinds=(),
            context_budget=None,
            error_code=error_code,
        )

    @staticmethod
    def _action_for(*, stage: ProcessStage) -> ProductActionLabel:
        """Map internal stage output to the closed product-language action surface."""

        labels = {
            ProcessStage.WAYFINDER: ProductActionLabel.DEFINE_STARTING_POINT,
            ProcessStage.ARCHITECTURE: ProductActionLabel.SHAPE_SOLUTION,
            ProcessStage.GRILL: ProductActionLabel.CONFIRM_ASSUMPTIONS,
            ProcessStage.CONTEXT: ProductActionLabel.ORGANIZE_WORKSPACE,
            ProcessStage.SPEC: ProductActionLabel.DRAFT_DELIVERY_PLAN,
            ProcessStage.TICKETS: ProductActionLabel.PLAN_EXECUTION,
            ProcessStage.IMPLEMENT: ProductActionLabel.BUILD_AND_TEST,
            ProcessStage.SMOKE_TEST: ProductActionLabel.VERIFY_DELIVERY,
            ProcessStage.REVIEW: ProductActionLabel.VERIFY_DELIVERY,
            ProcessStage.HANDOFF: ProductActionLabel.COMPLETE_HANDOFF,
        }
        try:
            return labels[stage]
        except KeyError as error:
            raise ValueError("no product action is declared for the requested transition") from error


class LocalMetadataNormalizer:
    """Validate untrusted local boundary data before any transport is called."""

    @staticmethod
    def normalize(*, raw_request: Mapping[str, object]) -> RouterRequestEnvelope:
        """Normalize a closed metadata mapping or raise a validation-only failure."""

        try:
            return RouterRequestEnvelope.model_validate(raw_request)
        except ValidationError as error:
            raise ValueError("private Router request is invalid") from error


class ContinuationPlan(RouterModel):
    """The single local command surface; an Agent never decides Context access itself."""

    mode: ContinuationMode
    action_label: ProductActionLabel | None
    required_source_kinds: tuple[ArtifactKind, ...]
    context_budget: PositiveTokenBudget | None
    error_code: RouterServiceErrorCode | None
    response: RouterResponseEnvelope | None = None

    @model_validator(mode="after")
    def plan_shape_is_safe(self) -> ContinuationPlan:
        """Make an accidental action or Context grant impossible after a stop or wait."""

        if self.mode is ContinuationMode.AUTO_RUN:
            if self.action_label is None or self.context_budget is None or self.response is None:
                raise ValueError("automatic plans require a validated Router response and Context budget")
            if self.error_code is not None:
                raise ValueError("automatic plans cannot have an error")
        elif self.mode is ContinuationMode.WAIT_FOR_HUMAN:
            if self.action_label is not ProductActionLabel.REQUEST_APPROVAL:
                raise ValueError("human waits require the approval action")
            if self.required_source_kinds or self.context_budget is not None or self.error_code is not None:
                raise ValueError("human waits cannot grant Context or report a transport error")
        elif self.action_label is not None or self.required_source_kinds or self.context_budget is not None:
            raise ValueError("halted plans cannot grant a local action or Context")
        return self


class PrivateRouterClient:
    """Fail-closed local adapter for the private service boundary and replay checks."""

    def __init__(self, *, service: RouterServicePort) -> None:
        self._service = service
        self._decision_for_event: dict[str, str] = {}
        self._event_for_decision: dict[str, str] = {}
        self._request_for_event: dict[str, str] = {}

    def route(self, *, raw_request: Mapping[str, object]) -> ContinuationPlan:
        """Return one validated plan; every boundary error becomes an explicit halt."""

        try:
            request = LocalMetadataNormalizer.normalize(raw_request=raw_request)
        except (TypeError, ValueError):
            return self._halt(code=RouterServiceErrorCode.ROUTER_INPUT_INVALID)
        try:
            raw_response = self._service.decide(request)
        except Exception:
            return self._halt(code=RouterServiceErrorCode.ROUTER_SERVICE_UNAVAILABLE)
        try:
            response = RouterResponseEnvelope.model_validate(raw_response)
        except ValidationError:
            return self._halt(code=RouterServiceErrorCode.ROUTER_RESPONSE_INVALID)
        if response.request_id != request.request_id or not self._accept_correlation(
            event_id=request.event_correlation_id,
            request_id=request.request_id,
            decision_id=response.decision_id,
        ):
            return self._halt(code=RouterServiceErrorCode.ROUTER_RESPONSE_INVALID)
        if response.continuation is ContinuationDirective.AUTO_CONTINUE:
            return ContinuationPlan(
                mode=ContinuationMode.AUTO_RUN,
                action_label=response.action_label,
                required_source_kinds=response.required_source_kinds,
                context_budget=response.context_budget,
                error_code=None,
                response=response,
            )
        if response.continuation is ContinuationDirective.WAIT_FOR_HUMAN:
            return ContinuationPlan(
                mode=ContinuationMode.WAIT_FOR_HUMAN,
                action_label=ProductActionLabel.REQUEST_APPROVAL,
                required_source_kinds=(),
                context_budget=None,
                error_code=None,
                response=response,
            )
        return self._halt(code=response.error_code or RouterServiceErrorCode.ROUTER_RESPONSE_INVALID)

    def _accept_correlation(
        self,
        *,
        event_id: OpaqueEventId,
        request_id: OpaqueRequestId,
        decision_id: OpaqueDecisionId,
    ) -> bool:
        """Use exact opaque IDs: retries stay stable and cross-event replay is rejected."""

        known_decision = self._decision_for_event.get(event_id)
        known_event = self._event_for_decision.get(decision_id)
        known_request = self._request_for_event.get(event_id)
        if known_decision is not None and known_decision != decision_id:
            return False
        if known_event is not None and known_event != event_id:
            return False
        if known_request is not None and known_request != request_id:
            return False
        self._decision_for_event[event_id] = decision_id
        self._event_for_decision[decision_id] = event_id
        self._request_for_event[event_id] = request_id
        return True

    @staticmethod
    def _halt(*, code: RouterServiceErrorCode) -> ContinuationPlan:
        """Create the only local error result; never invent a next action or Context grant."""

        return ContinuationPlan(
            mode=ContinuationMode.HALT,
            action_label=None,
            required_source_kinds=(),
            context_budget=None,
            error_code=code,
        )


class LocalContextGate:
    """Permit local Context resolution only for a currently validated automatic plan."""

    def resolve(
        self,
        *,
        plan: ContinuationPlan,
        resolver: ContextResolver,
        event_id: NonBlankText,
        required_sources: tuple[ArtifactRef, ...],
        target_artifact: ArtifactRef,
        consumer: ConsumerFingerprint,
    ) -> ResolvedContext:
        """Enforce decision source kinds and budget before the resolver reads local text."""

        if plan.mode is not ContinuationMode.AUTO_RUN or plan.context_budget is None:
            raise PermissionError("private Router did not grant local Context access")
        actual_kinds = tuple(source.kind for source in required_sources)
        if actual_kinds != plan.required_source_kinds:
            raise PermissionError("local sources do not exactly match the Router Context grant")
        return resolver.resolve(
            event_id=event_id,
            required_sources=required_sources,
            target_artifact=target_artifact,
            consumer=consumer,
            token_budget=plan.context_budget,
        )


class AutomaticContinuationExecutor(Protocol):
    """Local capability runner port.  Production model dispatch remains outside this POC."""

    def execute(self, *, action_label: ProductActionLabel) -> RouterRequestEnvelope:
        """Run the granted local action and return its next metadata-only event request."""


class ContinuityRunResult(RouterModel):
    """A bounded run stops only at a human gate, a failure, or its declared safety ceiling."""

    auto_steps: Annotated[int, Field(ge=0)]
    final_plan: ContinuationPlan


class AutomaticContinuationRunner:
    """Execute consecutive safe product actions without pausing between non-human stages."""

    def __init__(self, *, client: PrivateRouterClient, executor: AutomaticContinuationExecutor) -> None:
        self._client = client
        self._executor = executor

    def run_until_pause(
        self,
        *,
        initial_request: RouterRequestEnvelope,
        max_auto_steps: Annotated[int, Field(gt=0)],
    ) -> ContinuityRunResult:
        """Continue while exactly one valid action is granted; fail closed at the safety ceiling."""

        if max_auto_steps <= 0:
            raise ValueError("max_auto_steps must be greater than zero")
        request = initial_request
        auto_steps = 0
        while True:
            plan = self._client.route(raw_request=request.model_dump())
            if plan.mode is not ContinuationMode.AUTO_RUN:
                return ContinuityRunResult(auto_steps=auto_steps, final_plan=plan)
            if auto_steps >= max_auto_steps or plan.action_label is None:
                return ContinuityRunResult(
                    auto_steps=auto_steps,
                    final_plan=PrivateRouterClient._halt(
                        code=RouterServiceErrorCode.ROUTER_POLICY_BLOCKED
                    ),
                )
            try:
                raw_next_request = self._executor.execute(action_label=plan.action_label)
                request = RouterRequestEnvelope.model_validate(raw_next_request)
            except Exception:
                return ContinuityRunResult(
                    auto_steps=auto_steps,
                    final_plan=PrivateRouterClient._halt(
                        code=RouterServiceErrorCode.ROUTER_POLICY_BLOCKED
                    ),
                )
            auto_steps += 1
