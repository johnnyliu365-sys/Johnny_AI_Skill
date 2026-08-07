"""Typed policy response formatting for the detachable plugin control plane."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Protocol

from pydantic import Field, model_validator

from .contracts import NonBlankText, RouterModel


CommitReference = Annotated[str, Field(pattern=r"^[0-9a-f]{7,64}$")]
TicketReference = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{2,127}$")]
OwnerReference = Annotated[
    str,
    Field(pattern=r"^[A-Za-z][A-Za-z0-9 _-]{2,95}$"),
]


class RenderOutcome(str, Enum):
    """Stable result states for the fixed response formatter boundary."""

    RENDERED = "rendered"
    HALT = "halt"


class FormatterError(str, Enum):
    """Non-sensitive formatter errors exposed to the Router."""

    INVALID_RESPONSE = "invalid_response"
    FORMATTER_UNAVAILABLE = "formatter_unavailable"
    FORMATTER_FAILURE = "formatter_failure"


class DocumentOutcome(str, Enum):
    """Stable states for loading one policy document through an injected source."""

    LOADED = "loaded"
    HALT = "halt"


class DocumentError(str, Enum):
    """Non-sensitive document-source errors."""

    SOURCE_UNAVAILABLE = "source_unavailable"
    SOURCE_FAILURE = "source_failure"
    INVALID_DOCUMENT = "invalid_document"


class FixedDispatchResponse(RouterModel):
    """The only response shape emitted before the single dispatch question."""

    ticket_docs_commit: CommitReference
    ticket_reference: TicketReference
    handoff_docs_commit: CommitReference
    implementation_owner: OwnerReference

    def render(self) -> str:
        """Render the fixed labels and order without accepting caller text."""

        validated = type(self).model_validate(self.model_dump())
        return "\n".join(
            (
                "工單 ready",
                f"- commit：{validated.ticket_docs_commit}",
                f"- 工單：{validated.ticket_reference}",
                "",
                "文件交接",
                f"- commit：{validated.handoff_docs_commit}",
                f"- implementation owner：{validated.implementation_owner}",
                f"- 工單 {validated.ticket_reference} 是否已交付給 implementation owner {validated.implementation_owner}？",
            )
        )


class RenderedDispatchResponse(RouterModel):
    """A fail-closed formatter result with no mixed success/error shape."""

    outcome: RenderOutcome
    text: NonBlankText | None = None
    error: FormatterError | None = None

    @model_validator(mode="after")
    def enforce_result_shape(self) -> RenderedDispatchResponse:
        """Keep errors stable and prevent a failed formatter from yielding text."""

        if self.outcome is RenderOutcome.RENDERED:
            if self.text is None or self.error is not None:
                raise ValueError("rendered results require text and no error")
        elif self.text is not None or self.error is None:
            raise ValueError("halted results require one error and no text")
        return self


class ResponseFormatter(Protocol):
    """Injected formatting capability; it cannot alter the response contract."""

    def format(self, response: FixedDispatchResponse) -> str:
        """Return the fixed response text."""


class PolicyDocumentSource(Protocol):
    """Injected source for policy text; it carries no filesystem path."""

    def read(self) -> str:
        """Return one policy document's text."""


class PolicyDocumentResult(RouterModel):
    """A metadata-only document load result with stable failure shape."""

    outcome: DocumentOutcome
    text: NonBlankText | None = None
    error: DocumentError | None = None

    @model_validator(mode="after")
    def enforce_result_shape(self) -> PolicyDocumentResult:
        """Keep document failures from being mistaken for valid policy text."""

        if self.outcome is DocumentOutcome.LOADED:
            if self.text is None or self.error is not None:
                raise ValueError("loaded results require text and no error")
        elif self.text is not None or self.error is None:
            raise ValueError("halted results require one error and no text")
        return self


class DispatchResponseFormatter:
    """Deterministic formatter used by the local plugin policy boundary."""

    def format(self, response: FixedDispatchResponse) -> str:
        """Render only validated metadata through the fixed response contract."""

        return response.render()


def render_dispatch_response(
    response: object,
    formatter: ResponseFormatter | None,
) -> RenderedDispatchResponse:
    """Render a typed response and map unavailable or faulty adapters to HALT."""

    if not isinstance(response, FixedDispatchResponse):
        return RenderedDispatchResponse(
            outcome=RenderOutcome.HALT,
            error=FormatterError.INVALID_RESPONSE,
        )
    try:
        response = FixedDispatchResponse.model_validate(response.model_dump())
    except Exception:
        return RenderedDispatchResponse(
            outcome=RenderOutcome.HALT,
            error=FormatterError.INVALID_RESPONSE,
        )
    if formatter is None:
        return RenderedDispatchResponse(
            outcome=RenderOutcome.HALT,
            error=FormatterError.FORMATTER_UNAVAILABLE,
        )
    try:
        rendered = formatter.format(response)
    except Exception:
        return RenderedDispatchResponse(
            outcome=RenderOutcome.HALT,
            error=FormatterError.FORMATTER_FAILURE,
        )
    if not isinstance(rendered, str) or rendered != response.render():
        return RenderedDispatchResponse(
            outcome=RenderOutcome.HALT,
            error=FormatterError.FORMATTER_FAILURE,
        )
    return RenderedDispatchResponse(outcome=RenderOutcome.RENDERED, text=rendered)


def read_policy_document(source: PolicyDocumentSource | None) -> PolicyDocumentResult:
    """Read injected policy text and map unavailable or faulty sources to HALT."""

    if source is None:
        return PolicyDocumentResult(
            outcome=DocumentOutcome.HALT,
            error=DocumentError.SOURCE_UNAVAILABLE,
        )
    try:
        text = source.read()
    except Exception:
        return PolicyDocumentResult(
            outcome=DocumentOutcome.HALT,
            error=DocumentError.SOURCE_FAILURE,
        )
    if not isinstance(text, str) or not text.strip():
        return PolicyDocumentResult(
            outcome=DocumentOutcome.HALT,
            error=DocumentError.INVALID_DOCUMENT,
        )
    return PolicyDocumentResult(outcome=DocumentOutcome.LOADED, text=text)


__all__ = (
    "CommitReference",
    "DispatchResponseFormatter",
    "DocumentError",
    "DocumentOutcome",
    "FixedDispatchResponse",
    "FormatterError",
    "OwnerReference",
    "PolicyDocumentResult",
    "PolicyDocumentSource",
    "RenderOutcome",
    "RenderedDispatchResponse",
    "ResponseFormatter",
    "TicketReference",
    "read_policy_document",
    "render_dispatch_response",
)
