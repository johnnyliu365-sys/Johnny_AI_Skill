"""Acceptance and reverse-mutation tests for WA-01 activation contracts."""

from __future__ import annotations

import ast
import hashlib
import inspect
from pathlib import Path
import unittest

from pydantic import TypeAdapter, ValidationError

from library.workflow_router.project_adoption_contracts import (
    ACTIVATION_BEGIN_MARKER,
    ACTIVATION_END_MARKER,
    ActivationAction,
    ActivationRefusalReason,
    ActivationState,
    CreateBlockPlan,
    HostBehaviorGateClassification,
    HostBehaviorGateState,
    HostInstructionKind,
    NoChangePlan,
    ProjectActivationPlannedResult,
    ProjectActivationRefusedResult,
    ProjectActivationRequest,
    ProjectActivationResult,
    SupportedHost,
    UpdateBlockPlan,
    plan_project_activation,
)


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _block(*, plugin: str = "johnny-ai-skill", version: str = "0.4.12", skill: str = "johnny-ai-skill:johnny-project-takeover", newline: str = "\n") -> str:
    return newline.join(
        (
            ACTIVATION_BEGIN_MARKER,
            "For software-change work in this repository, load and follow the installed",
            f"`{skill}` skill from plugin `{plugin}` version `{version}` as the entry route.",
            "Load only the stage/reference it routes. If that installed identity is absent or stale,",
            "stop before governed mutation and report the mismatch; do not copy plugin governance here.",
            ACTIVATION_END_MARKER,
        )
    )


def _request(
    document: str = "",
    *,
    host: SupportedHost = SupportedHost.CODEX,
    instruction_kind: HostInstructionKind = HostInstructionKind.CODEX_AGENTS,
    plugin: str = "johnny-ai-skill",
    version: str = "0.4.13",
    skill: str = "johnny-ai-skill:johnny-project-takeover",
    expected_digest: str | None = None,
) -> ProjectActivationRequest:
    return ProjectActivationRequest(
        request_ref="request-plugin-adoption-wa01",
        repository_id="repo-plugin-adoption",
        host=host,
        instruction_kind=instruction_kind,
        target_document_id="codex-agents-document",
        expected_current_digest=_digest(document) if expected_digest is None else expected_digest,
        current_document_text=document,
        installed_plugin_id=plugin,
        installed_plugin_version=version,
        takeover_skill_id=skill,
    )


_EFFECT_FREE_ALLOWED_IMPORT_MODULES = frozenset(
    {"__future__", "re", "enum", "hashlib", "typing", "pydantic", "contracts"}
)
_EFFECT_FREE_FORBIDDEN_IMPORT_MODULES = frozenset(
    {
        "os",
        "pathlib",
        "shutil",
        "tempfile",
        "glob",
        "fileinput",
        "io",
        "subprocess",
        "multiprocessing",
        "signal",
        "psutil",
        "sys",
        "runpy",
        "socket",
        "requests",
        "httpx",
        "urllib",
        "http",
        "ssl",
        "websocket",
        "platform",
        "dotenv",
        "openai",
        "anthropic",
        "boto3",
        "google",
        "azure",
        "codex",
        "claude",
        "powershell",
        "winreg",
        "git",
        "dulwich",
        "importlib",
        "builtins",
    }
)
_EFFECT_FREE_FORBIDDEN_NAMES = frozenset(
    {
        "Any",
        "cast",
        "spawn_agent",
        "send_message",
        "wait_agent",
        "interrupt_agent",
        "subagent",
        "provider",
        "host_cli",
        "git",
        "dynamic_lookup",
        "raw_mapping",
        "dict",
        "Mapping",
        "MutableMapping",
        "defaultdict",
    }
)
_EFFECT_FREE_FORBIDDEN_CALL_NAMES = frozenset(
    {
        "open",
        "eval",
        "exec",
        "compile",
        "__import__",
        "import_module",
        "getattr",
        "setattr",
        "delattr",
        "globals",
        "locals",
        "vars",
    }
)
_EFFECT_FREE_FORBIDDEN_ATTRIBUTES = frozenset(
    {
        "spawn_agent",
        "send_message",
        "wait_agent",
        "interrupt_agent",
        "import_module",
        "getattr",
        "setattr",
        "subprocess",
        "socket",
        "request",
    }
)


def _assert_closed_effect_free_source_gate(source: str) -> None:
    """Run the bounded production source gate before planner-path tests."""

    tree = ast.parse(source)
    imported = {
        alias.name.split(".", maxsplit=1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported.update(
        (node.module or "").split(".", maxsplit=1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        if node.module is not None
    )
    assert imported == _EFFECT_FREE_ALLOWED_IMPORT_MODULES
    assert imported.isdisjoint(_EFFECT_FREE_FORBIDDEN_IMPORT_MODULES)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert names.isdisjoint(_EFFECT_FREE_FORBIDDEN_NAMES)
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert calls.isdisjoint(_EFFECT_FREE_FORBIDDEN_CALL_NAMES)
    attributes = {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    assert attributes.isdisjoint(_EFFECT_FREE_FORBIDDEN_ATTRIBUTES)


class WA01StrictContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        import library.workflow_router.project_adoption_contracts as module

        _assert_closed_effect_free_source_gate(inspect.getsource(module))

    def test_wa1_enums_requests_and_tagged_results_round_trip(self) -> None:
        for enum_type in (
            SupportedHost,
            HostInstructionKind,
            ActivationState,
            ActivationAction,
            HostBehaviorGateState,
            ActivationRefusalReason,
        ):
            for member in enum_type:
                self.assertEqual(member, enum_type(member.value))

        request = _request()
        rebuilt_request = ProjectActivationRequest.model_validate_json(request.model_dump_json())
        self.assertEqual(request, rebuilt_request)
        planned = plan_project_activation(request)
        adapter: TypeAdapter[ProjectActivationResult] = TypeAdapter(ProjectActivationResult)
        rebuilt_result = adapter.validate_json(planned.model_dump_json())
        self.assertEqual(planned, rebuilt_result)

        for raw in (
            {**request.model_dump(), "request_ref": ""},
            {**request.model_dump(), "request_ref": " request-with-space"},
            {**request.model_dump(), "repository_id": "C:\\repo"},
            {**request.model_dump(), "target_document_id": "https://example.invalid"},
            {**request.model_dump(), "expected_current_digest": "A" * 64},
            {**request.model_dump(), "installed_plugin_version": "1.2"},
            {**request.model_dump(), "takeover_skill_id": "johnny-ai-skill:{takeover}"},
            {**request.model_dump(), "host": 1},
            {**request.model_dump(), "current_document_text": None},
            {**request.model_dump(), "unexpected": "field"},
        ):
            with self.subTest(raw=raw):
                with self.assertRaises(ValidationError):
                    ProjectActivationRequest.model_validate(raw)

    def test_wa1_success_and_refusal_shapes_have_no_action_nullable_fields(self) -> None:
        digest = _digest("document")
        with self.assertRaises(ValidationError):
            CreateBlockPlan(
                expected_current_digest=digest,
                expected_post_digest=digest,
                proposed_text="different",
            )
        with self.assertRaises(ValidationError):
            NoChangePlan.model_validate(
                {"verified_existing_digest": digest, "proposed_text": "forbidden"}
            )
        with self.assertRaises(ValidationError):
            ProjectActivationPlannedResult.model_validate(
                {
                    "request_ref": "request-plugin-adoption-wa01",
                    "plan": {"action": "NO_CHANGE", "verified_existing_digest": digest},
                    "extra": "forbidden",
                }
            )

    def test_wa1_each_plan_variant_round_trips_through_its_tagged_validator(self) -> None:
        create = CreateBlockPlan(
            expected_current_digest=_digest("before"),
            expected_post_digest=_digest("after"),
            proposed_text="after",
        )
        update = UpdateBlockPlan(
            expected_current_digest=_digest("before"),
            expected_post_digest=_digest("after"),
            proposed_text="after",
        )
        no_change = NoChangePlan(verified_existing_digest=_digest("same"))
        adapter: TypeAdapter[ProjectActivationResult] = TypeAdapter(ProjectActivationResult)
        for plan in (create, update, no_change):
            envelope = ProjectActivationPlannedResult(
                request_ref="request-plugin-adoption-wa01",
                plan=plan,
            )
            rebuilt = adapter.validate_json(envelope.model_dump_json())
            self.assertEqual(envelope, rebuilt)
        with self.assertRaises(ValidationError):
            ProjectActivationRefusedResult.model_validate(
                {
                    "request_ref": "request-plugin-adoption-wa01",
                    "reason": ActivationRefusalReason.INPUT_INVALID,
                    "field_identifier": "request",
                    "proposed_text": "forbidden",
                }
            )

    def test_wa1_every_refusal_variant_round_trips_through_tagged_validator(self) -> None:
        adapter: TypeAdapter[ProjectActivationResult] = TypeAdapter(ProjectActivationResult)
        for reason in ActivationRefusalReason:
            refusal = ProjectActivationRefusedResult(
                request_ref="request-plugin-adoption-wa01",
                reason=reason,
                field_identifier="current_document_text",
            )
            rebuilt = adapter.validate_json(refusal.model_dump_json())
            self.assertEqual(refusal, rebuilt)

    def test_wa1_unencodable_text_rejects_but_legal_large_text_remains_valid(self) -> None:
        invalid = _request().model_dump()
        invalid["current_document_text"] = chr(0xD800)
        with self.assertRaises(ValidationError):
            ProjectActivationRequest(**invalid)

        large_document = "測試😀" * 10_000
        request = _request(large_document)
        result = plan_project_activation(request)
        self.assertIsInstance(result, ProjectActivationPlannedResult)
        if isinstance(result, ProjectActivationPlannedResult):
            self.assertIsInstance(result.plan, CreateBlockPlan)
            if isinstance(result.plan, CreateBlockPlan):
                self.assertTrue(result.plan.proposed_text.startswith(large_document + "\n"))
                self.assertEqual(_digest(result.plan.proposed_text), result.plan.expected_post_digest)

    def test_wa2_absent_block_creates_exact_document_and_digest(self) -> None:
        original = "# Repository instructions\r\nKeep this line exact.\r\n"
        result = plan_project_activation(_request(original))
        self.assertIsInstance(result, ProjectActivationPlannedResult)
        if isinstance(result, ProjectActivationPlannedResult):
            self.assertIsInstance(result.plan, CreateBlockPlan)
            if isinstance(result.plan, CreateBlockPlan):
                self.assertEqual(_digest(original), result.plan.expected_current_digest)
                self.assertEqual(_digest(result.plan.proposed_text), result.plan.expected_post_digest)
                self.assertTrue(result.plan.proposed_text.startswith(original))
                self.assertEqual(ACTIVATION_BEGIN_MARKER, result.plan.proposed_text[len(original) : len(original) + len(ACTIVATION_BEGIN_MARKER)])
                self.assertIn("\r\n", result.plan.proposed_text)
                self.assertEqual(1, result.plan.proposed_text.count(ACTIVATION_BEGIN_MARKER))
                self.assertEqual(1, result.plan.proposed_text.count(ACTIVATION_END_MARKER))

    def test_wa2_mixed_document_uses_tail_newline_without_normalizing_outside_text(self) -> None:
        original = "first\r\nsecond\nlast"
        result = plan_project_activation(_request(original))
        self.assertIsInstance(result, ProjectActivationPlannedResult)
        if isinstance(result, ProjectActivationPlannedResult):
            self.assertIsInstance(result.plan, CreateBlockPlan)
            if isinstance(result.plan, CreateBlockPlan):
                expected = original + "\n" + _block(version="0.4.13")
                self.assertEqual(expected, result.plan.proposed_text)
                self.assertEqual(original, result.plan.proposed_text[: len(original)])
                self.assertNotIn("\r\n", result.plan.proposed_text[len(original) + 1 :])

    def test_wa3_existing_different_block_updates_only_delimited_bytes(self) -> None:
        prefix = "# Prefix\r\nUnrelated instruction stays.\r\n"
        suffix = "\r\n# Suffix\r\n"
        current = prefix + _block(version="0.4.12", newline="\r\n") + suffix
        result = plan_project_activation(_request(current))
        self.assertIsInstance(result, ProjectActivationPlannedResult)
        if isinstance(result, ProjectActivationPlannedResult):
            self.assertIsInstance(result.plan, UpdateBlockPlan)
            if isinstance(result.plan, UpdateBlockPlan):
                proposed = result.plan.proposed_text
                begin = proposed.index(ACTIVATION_BEGIN_MARKER)
                end = proposed.index(ACTIVATION_END_MARKER) + len(ACTIVATION_END_MARKER)
                self.assertEqual(prefix, proposed[:begin])
                self.assertEqual(suffix, proposed[end:])
                self.assertIn("version `0.4.13`", proposed)
                self.assertIn("Unrelated instruction stays.", proposed)
                self.assertEqual(_digest(proposed), result.plan.expected_post_digest)

    def test_wa4_exact_content_is_no_change_and_idempotent(self) -> None:
        current = "# Header\n" + _block(version="0.4.13") + "\n# Footer"
        request = _request(current)
        first = plan_project_activation(request)
        second = plan_project_activation(request)
        self.assertEqual(first.model_dump_json(), second.model_dump_json())
        self.assertIsInstance(first, ProjectActivationPlannedResult)
        if isinstance(first, ProjectActivationPlannedResult):
            self.assertIsInstance(first.plan, NoChangePlan)
            self.assertNotIn("proposed_text", NoChangePlan.model_fields)
            if isinstance(first.plan, NoChangePlan):
                self.assertEqual(_digest(current), first.plan.verified_existing_digest)

    def test_wa5_stale_host_marker_and_identity_refusals_are_finite(self) -> None:
        stale = plan_project_activation(_request("current", expected_digest="0" * 64))
        self.assertIsInstance(stale, ProjectActivationRefusedResult)
        if isinstance(stale, ProjectActivationRefusedResult):
            self.assertEqual(ActivationRefusalReason.STALE_PRESTATE, stale.reason)
            self.assertNotIn("proposed_text", ProjectActivationRefusedResult.model_fields)

        cross_pair = plan_project_activation(
            _request(host=SupportedHost.CODEX, instruction_kind=HostInstructionKind.CLAUDE_PROJECT_INSTRUCTION)
        )
        self.assertIsInstance(cross_pair, ProjectActivationRefusedResult)
        if isinstance(cross_pair, ProjectActivationRefusedResult):
            self.assertEqual(ActivationRefusalReason.HOST_KIND_MISMATCH, cross_pair.reason)

        duplicate = _block() + "\n" + _block()
        nested = _block().replace(ACTIVATION_END_MARKER, ACTIVATION_BEGIN_MARKER + "\n" + ACTIVATION_END_MARKER, 1)
        reversed_markers = ACTIVATION_END_MARKER + "\n" + ACTIVATION_BEGIN_MARKER
        partial = ACTIVATION_BEGIN_MARKER[:-4]
        for document, expected in (
            (duplicate, ActivationRefusalReason.BLOCK_DUPLICATED),
            (nested, ActivationRefusalReason.BLOCK_DUPLICATED),
            (reversed_markers, ActivationRefusalReason.BLOCK_MALFORMED),
            (partial, ActivationRefusalReason.BLOCK_MALFORMED),
        ):
            with self.subTest(expected=expected):
                result = plan_project_activation(_request(document))
                self.assertIsInstance(result, ProjectActivationRefusedResult)
                if isinstance(result, ProjectActivationRefusedResult):
                    self.assertEqual(expected, result.reason)
                    self.assertNotIn("proposed_text", ProjectActivationRefusedResult.model_fields)

        identity_mismatch = plan_project_activation(
            _request(plugin="foreign-plugin", skill="johnny-ai-skill:johnny-project-takeover")
        )
        self.assertIsInstance(identity_mismatch, ProjectActivationRefusedResult)
        if isinstance(identity_mismatch, ProjectActivationRefusedResult):
            self.assertEqual(ActivationRefusalReason.INPUT_INVALID, identity_mismatch.reason)

    def test_wa5_unknown_project_marker_version_refuses_without_create(self) -> None:
        unknown_version_block = "\n".join(
            (
                "<!-- johnny-ai-skill:project-adoption:v2:begin -->",
                "future activation grammar",
                "<!-- johnny-ai-skill:project-adoption:v2:end -->",
            )
        )
        refused = plan_project_activation(_request(unknown_version_block))
        self.assertIsInstance(refused, ProjectActivationRefusedResult)
        if isinstance(refused, ProjectActivationRefusedResult):
            self.assertEqual(ActivationRefusalReason.BLOCK_MALFORMED, refused.reason)
            self.assertNotIn("proposed_text", refused.model_dump())

        unrelated = plan_project_activation(_request("ordinary instruction text"))
        self.assertIsInstance(unrelated, ProjectActivationPlannedResult)

    def test_wa6_classification_is_separate_and_never_in_planner_result(self) -> None:
        classification_adapter: TypeAdapter[HostBehaviorGateClassification] = TypeAdapter(
            HostBehaviorGateClassification
        )
        classifications = tuple(
            HostBehaviorGateClassification(host=SupportedHost.CODEX, state=state)
            for state in HostBehaviorGateState
        )
        self.assertEqual(set(HostBehaviorGateState), {item.state for item in classifications})
        for classification in classifications:
            rebuilt = classification_adapter.validate_json(classification.model_dump_json())
            self.assertEqual(classification, rebuilt)
        instruction_only = classifications[1]
        self.assertEqual(HostBehaviorGateState.INSTRUCTION_ONLY, instruction_only.state)
        result = plan_project_activation(_request())
        self.assertNotIn("HOST_GATE_ENFORCED", result.model_dump_json())
        self.assertNotIn("HostBehaviorGateClassification", type(result).__name__)

    def test_wa7_ast_has_one_pure_planner_and_private_module_boundary(self) -> None:
        import library.workflow_router as package
        import library.workflow_router.project_adoption_contracts as module

        self.assertNotIn("project_adoption_contracts", package.__all__)
        package_init = Path(package.__file__).read_bytes() if package.__file__ is not None else b""
        self.assertNotIn(b"project_adoption_contracts", package_init)
        source = inspect.getsource(module)
        _assert_closed_effect_free_source_gate(source)
        tree = ast.parse(source)
        planner_entries = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "plan_project_activation"
        ]
        self.assertEqual(1, len(planner_entries))
        forbidden_modules = {
            "os",
            "pathlib",
            "shutil",
            "tempfile",
            "glob",
            "fileinput",
            "io",
            "subprocess",
            "multiprocessing",
            "signal",
            "psutil",
            "sys",
            "runpy",
            "socket",
            "requests",
            "httpx",
            "urllib",
            "http",
            "ssl",
            "websocket",
            "platform",
            "dotenv",
            "openai",
            "anthropic",
            "boto3",
            "google",
            "azure",
            "codex",
            "claude",
            "powershell",
            "winreg",
            "git",
            "dulwich",
            "importlib",
            "builtins",
        }
        imported = {
            alias.name.split(".", maxsplit=1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            (node.module or "").split(".", maxsplit=1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            if node.module is not None
        )
        allowed_import_modules = {
            "__future__",
            "re",
            "enum",
            "hashlib",
            "typing",
            "pydantic",
            "contracts",
        }
        self.assertEqual(allowed_import_modules, imported)
        self.assertTrue(imported.isdisjoint(forbidden_modules))

        forbidden_names = {
            "Any",
            "cast",
            "spawn_agent",
            "send_message",
            "wait_agent",
            "interrupt_agent",
            "subagent",
            "provider",
            "host_cli",
            "git",
            "dynamic_lookup",
            "raw_mapping",
            "dict",
            "Mapping",
            "MutableMapping",
            "defaultdict",
        }
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        self.assertTrue(names.isdisjoint(forbidden_names))

        forbidden_call_names = {
            "open",
            "eval",
            "exec",
            "compile",
            "__import__",
            "import_module",
            "getattr",
            "setattr",
            "delattr",
            "globals",
            "locals",
            "vars",
        }
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue(calls.isdisjoint(forbidden_call_names))

        forbidden_attributes = {
            "spawn_agent",
            "send_message",
            "wait_agent",
            "interrupt_agent",
            "import_module",
            "getattr",
            "setattr",
            "subprocess",
            "socket",
            "request",
        }
        attributes = {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        self.assertTrue(attributes.isdisjoint(forbidden_attributes))


if __name__ == "__main__":
    unittest.main()
