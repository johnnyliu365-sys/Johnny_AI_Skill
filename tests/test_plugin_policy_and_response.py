"""TDD acceptance tests for the plugin policy and fixed dispatch response."""

from __future__ import annotations

import unittest
from pathlib import Path

from pydantic import ValidationError

from library.workflow_router.policy_response import (
    DispatchResponseFormatter,
    DocumentError,
    DocumentOutcome,
    FixedDispatchResponse,
    FormatterError,
    read_policy_document,
    RenderOutcome,
    render_dispatch_response,
)


class RaisingFormatter:
    """A formatter failure must become a stable halt, not a fake response."""

    def format(self, response: FixedDispatchResponse) -> str:
        raise RuntimeError("formatter unavailable")


class RaisingDocumentSource:
    """A document source failure must not escape the policy boundary."""

    def read(self) -> str:
        raise RuntimeError("document unavailable")


class PluginPolicyAndResponseTests(unittest.TestCase):
    """Keep the policy response deterministic and metadata-only."""

    def setUp(self) -> None:
        self.response = FixedDispatchResponse(
            ticket_docs_commit="b84c2a5",
            ticket_reference="03-plugin-policy-and-response",
            handoff_docs_commit="c569056",
            implementation_owner="Codex implementation Agent",
        )

    def test_fixed_response_preserves_required_order_and_question(self) -> None:
        rendered = self.response.render()
        self.assertEqual(
            "\n".join(
                (
                    "工單 ready",
                    "- commit：b84c2a5",
                    "- 工單：03-plugin-policy-and-response",
                    "",
                    "文件交接",
                    "- commit：c569056",
                    "- implementation owner：Codex implementation Agent",
                    "- 工單 03-plugin-policy-and-response 是否已交付給 implementation owner Codex implementation Agent？",
                )
            ),
            rendered,
        )

    def test_seven_path_and_uri_boundary_forms_are_rejected(self) -> None:
        path_forms = (
            "/repo",
            "C:\\repo",
            "\\\\server\\share",
            "file://repo",
            "https://repo",
            "../repo",
            ".\\repo",
        )
        fields = ("ticket_docs_commit", "ticket_reference", "handoff_docs_commit", "implementation_owner")
        for field in fields:
            for value in path_forms:
                with self.subTest(field=field, value=value):
                    payload = self.response.model_dump()
                    payload[field] = value
                    with self.assertRaises(ValidationError):
                        FixedDispatchResponse.model_validate(payload)

    def test_null_empty_and_empty_container_inputs_are_rejected(self) -> None:
        for field in ("ticket_docs_commit", "ticket_reference", "handoff_docs_commit", "implementation_owner"):
            values: tuple[object, ...] = (None, "", "   ", [], {})
            for value in values:
                with self.subTest(field=field, value=value):
                    payload = self.response.model_dump()
                    payload[field] = value
                    with self.assertRaises(ValidationError):
                        FixedDispatchResponse.model_validate(payload)

    def test_direct_and_indirect_untyped_response_bypasses_halt(self) -> None:
        direct = render_dispatch_response(self.response, DispatchResponseFormatter())
        self.assertEqual(RenderOutcome.RENDERED, direct.outcome)
        self.assertIsNotNone(direct.text)

        with self.assertRaises(ValidationError):
            FixedDispatchResponse.model_validate(
                {**self.response.model_dump(), "raw_response": "工單 ready"}
            )
        indirect = render_dispatch_response(
            {**self.response.model_dump(), "raw_response": "工單 ready"},
            DispatchResponseFormatter(),
        )
        self.assertEqual(RenderOutcome.HALT, indirect.outcome)
        self.assertEqual(FormatterError.INVALID_RESPONSE, indirect.error)
        self.assertIsNone(indirect.text)

        forged = self.response.model_copy(update={"ticket_docs_commit": "C:/repo"})
        forged_result = render_dispatch_response(forged, DispatchResponseFormatter())
        self.assertEqual(RenderOutcome.HALT, forged_result.outcome)
        self.assertEqual(FormatterError.INVALID_RESPONSE, forged_result.error)

    def test_formatter_absence_and_exception_use_stable_errors(self) -> None:
        unavailable = render_dispatch_response(self.response, None)
        self.assertEqual(RenderOutcome.HALT, unavailable.outcome)
        self.assertEqual(FormatterError.FORMATTER_UNAVAILABLE, unavailable.error)
        failed = render_dispatch_response(self.response, RaisingFormatter())
        self.assertEqual(RenderOutcome.HALT, failed.outcome)
        self.assertEqual(FormatterError.FORMATTER_FAILURE, failed.error)
        self.assertIsNone(failed.text)

    def test_document_source_absence_exception_and_empty_text_halt_stably(self) -> None:
        unavailable = read_policy_document(None)
        self.assertEqual(DocumentOutcome.HALT, unavailable.outcome)
        self.assertEqual(DocumentError.SOURCE_UNAVAILABLE, unavailable.error)
        failed = read_policy_document(RaisingDocumentSource())
        self.assertEqual(DocumentOutcome.HALT, failed.outcome)
        self.assertEqual(DocumentError.SOURCE_FAILURE, failed.error)

        class EmptyDocumentSource:
            def read(self) -> str:
                return "   "

        empty = read_policy_document(EmptyDocumentSource())
        self.assertEqual(DocumentOutcome.HALT, empty.outcome)
        self.assertEqual(DocumentError.INVALID_DOCUMENT, empty.error)

    def test_policy_documents_state_topology_waits_halt_and_historical_boundary(self) -> None:
        document_paths = (
            Path("Workflow.md"),
            Path("AGENTS.md"),
            Path("README.md"),
            Path("skills/johnny-project-takeover/SKILL.md"),
            Path("template/README.md"),
        )
        text = "\n".join(path.read_text(encoding="utf-8") for path in document_paths)
        for required in (
            "可用 coding Agent 數量",
            "工單 ready",
            "文件交接",
            "TICKET_DISPATCH_REQUIRED",
            "WAIT_FOR_HUMAN",
            "AUTO_CONTINUE",
            "HALT",
            "歷史",
            "non-commercial",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)
        self.assertNotIn("TICKETS + APPROVAL_GRANTED → IMPLEMENT", text)

        policy_source = Path("library/workflow_router/policy_response.py").read_text(encoding="utf-8")
        self.assertNotIn("token", policy_source.lower())


if __name__ == "__main__":
    unittest.main()
