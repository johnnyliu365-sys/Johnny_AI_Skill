"""22: a refusal names a category and a next step, or the audit is red.

The cells are grouped by the property they nail rather than by the function
they call, because most of the properties here are about what the module
refuses to do -- hand back a category it does not have, keep guidance that
carries the way around, or report full coverage of a file it could not open.

Two of the groups run against a synthetic repository root instead of this one.
`audit_classification` is only worth anything if its answers are read from the
sources rather than recited, and the only way to show that is to hand it a tree
whose contents this suite chose.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from pydantic import ValidationError

from library.local_orchestration.control_plane_mutation import (
    ControlPlaneMutationFailure,
)
from library.local_orchestration.document_mutation_gate import (
    DocumentMutationFailure,
)
from library.local_orchestration.refusal_guidance import (
    BYPASS_TERMS,
    CONTROL_PLANE_SURFACE,
    COVERED_SURFACES,
    DOCUMENT_GATE_SURFACE,
    GUIDANCE,
    INSTALL_SCRIPT_SURFACE,
    INSTALL_WRAPPER_SURFACE,
    LOOKUP_SURFACE,
    REGISTRY,
    ClassificationAuditStatus,
    GuidanceLookupFailure,
    GuidanceLookupStatus,
    RefusalCategory,
    RefusalGuidance,
    audit_classification,
    bypass_terms_in,
    discover_install_script_codes,
    discover_install_wrapper_codes,
    guidance_for,
    guidance_is_transport_safe,
    never_auto_resolve_violations,
    parse_install_script_guidance,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_INSTALL_SCRIPT = _REPO_ROOT / "install.ps1"
_INSTALL_WRAPPER = _REPO_ROOT / "johnny-install.cmd"

#: Every `Failure` enum under `library/` that this ticket does not classify.
#: Written out rather than computed, and deliberately not imported from the
#: module under test: a remainder the module derives from itself would agree
#: with itself no matter what it did. Later batches shrink this list one entry
#: at a time, and a batch that empties it has to say so here.
_UNCOVERED_ROSTER: frozenset[str] = frozenset(
    {
        "library/local_orchestration/antigravity_registration.py::SkillRegistrationFailure",
        "library/local_orchestration/antigravity_wake_command.py::WakeSendFailure",
        "library/local_orchestration/claude_wake_command.py::ClaudeWakeFailure",
        "library/local_orchestration/commit_trigger_intake.py::CommitTriggerFailure",
        "library/local_orchestration/dispatch_authority.py::DispatchAdmissionFailure",
        "library/local_orchestration/dispatch_authority.py::ReceiptRevocationFailure",
        "library/local_orchestration/dispatch_session.py::WorkIntegrationFailure",
        "library/local_orchestration/dispatch_session.py::WorkerDispatchFailure",
        "library/local_orchestration/dispatch_session.py::WorkerRedispatchFailure",
        "library/local_orchestration/dispatch_session.py::WorkerReturnFailure",
        "library/local_orchestration/johnny_router_composition.py::JohnnyRouterCompositionFailure",
        "library/local_orchestration/live_dispatch_metadata_boundary.py::ReceiptRevokeFailure",
        "library/local_orchestration/plugin_bundle_builder.py::PluginBundleBuildFailure",
        "library/local_orchestration/plugin_install_transaction.py::PluginInstallFailure",
        "library/local_orchestration/plugin_uninstall_transaction.py::PluginUninstallFailure",
        "library/local_orchestration/project_subscription_runtime.py::ProjectSubscriptionFailure",
        "library/local_orchestration/release_pin_guard.py::ReleasePinFailure",
        "library/local_orchestration/review_return.py::ReviewReturnFailure",
        "library/local_orchestration/review_return_consumption.py::ConsumptionFailure",
        "library/local_orchestration/runner_receipt_seeding.py::ReceiptVerificationFailure",
        "library/local_orchestration/subscription_builder.py::SubscriptionBuildFailure",
        "library/local_orchestration/wake_capability.py::WakeCapabilityFailure",
        "library/local_orchestration/windows_native_git_ref.py::RefWatchCapabilityFailure",
        "library/local_orchestration/work_queue.py::WorkEnqueueFailure",
        "library/local_orchestration/work_queue.py::WorkPullFailure",
        "library/local_orchestration/worker_assignment.py::WorkerClaimFailure",
        "library/local_orchestration/worker_assignment.py::WorkerSettlementFailure",
        "library/local_orchestration/worktree_containment.py::WorktreeContainmentFailure",
        "library/workflow_router/context_load_report.py::ContextLoadReportFailure",
        "library/workflow_router/execution_replacement.py::ExecutionReplacementFailure",
        "library/workflow_router/git_handoff_contracts.py::GitEventAdapterFailure",
        "library/workflow_router/live_dispatch_contracts.py::ArtifactReadFailure",
        "library/workflow_router/live_dispatch_contracts.py::ArtifactRegistrationFailure",
        "library/workflow_router/live_dispatch_contracts.py::ReceiptIssueFailure",
        "library/workflow_router/live_dispatch_contracts.py::ReceiptReadFailure",
        "library/workflow_router/role_supervision_contracts.py::HandoffValidationFailure",
        "library/workflow_router/role_wake_contracts.py::RoleWakeChainFailure",
        "library/workflow_router/supervision_runtime_contracts.py::SupervisionRuntimeFailure",
        "library/workflow_router/target_document_contracts.py::DocumentWriteFailure",
        "library/workflow_router/telemetry.py::TelemetryReportFailure",
        "library/workflow_router/thread_dispatch_contracts.py::CodexThreadDispatchFailure",
        "library/workflow_router/thread_dispatch_contracts.py::DispatchClaimFailure",
        "library/workflow_router/thread_dispatch_contracts.py::DispatchSettlementFailure",
        "library/workflow_router/thread_host_contracts.py::ThreadHostBindingFailure",
        "library/workflow_router/thread_host_contracts.py::ThreadHostResolutionFailure",
    }
)

#: The three `Failure` enums this ticket does classify, plus the two installer
#: scripts, which are not enums and are the whole reason the ticket exists.
_COVERED_ENUM_ROSTER: frozenset[str] = frozenset(
    {DOCUMENT_GATE_SURFACE, CONTROL_PLANE_SURFACE, LOOKUP_SURFACE}
)


def _entry(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "surface": "surface",
        "code": "CODE",
        "category": RefusalCategory.AGENT_MAY_RESOLVE,
        "next_steps": ("do the thing",),
    }
    base.update(overrides)
    return base


class ClassificationHasNoDefaultTests(unittest.TestCase):
    """Forgetting must be loud, because the quiet answer would be permissive.

    If an entry could omit its category and land somewhere, the somewhere it
    landed would be whichever value was written first or read as mildest, and
    every code somebody forgot would arrive pre-approved for an agent to
    settle. So the model has no default and no empty guidance: an entry either
    says what it is and what to do, or it does not exist.
    """

    def test_an_entry_that_omits_its_category_does_not_construct(self) -> None:
        fields = _entry()
        del fields["category"]
        with self.assertRaises(ValidationError):
            RefusalGuidance(**fields)

    def test_an_entry_that_omits_its_category_gets_no_value_by_another_route(
        self,
    ) -> None:
        # A default declared as None, or a category field that accepts None,
        # would satisfy the cell above while restoring the hole it closes.
        with self.assertRaises(ValidationError):
            RefusalGuidance(**_entry(category=None))

    def test_an_entry_with_no_next_step_does_not_construct(self) -> None:
        with self.assertRaises(ValidationError):
            RefusalGuidance(**_entry(next_steps=()))

    def test_the_taxonomy_is_exactly_three_values(self) -> None:
        self.assertEqual(
            tuple(member.value for member in RefusalCategory),
            (
                "AGENT_MAY_RESOLVE",
                "OWNER_MUST_DECIDE",
                "NEVER_AUTO_RESOLVE",
            ),
        )


class LookupTests(unittest.TestCase):
    """A classified code answers; everything else fails closed and says why."""

    def test_a_classified_code_yields_its_category_and_its_next_steps(self) -> None:
        result = guidance_for(
            DOCUMENT_GATE_SURFACE,
            DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY.value,
        )

        self.assertIs(result.status, GuidanceLookupStatus.FOUND)
        self.assertIsNone(result.failure)
        assert result.guidance is not None
        self.assertIs(result.guidance.category, RefusalCategory.NEVER_AUTO_RESOLVE)
        self.assertTrue(result.guidance.next_steps)

    def test_an_unclassified_code_is_a_named_failure_and_never_a_category(
        self,
    ) -> None:
        result = guidance_for(DOCUMENT_GATE_SURFACE, "A_CODE_NOBODY_CLASSIFIED")

        self.assertIs(result.status, GuidanceLookupStatus.UNAVAILABLE)
        self.assertIs(result.failure, GuidanceLookupFailure.CODE_UNCLASSIFIED)
        self.assertIsNone(result.guidance)

    def test_an_unknown_surface_is_told_apart_from_an_unclassified_code(self) -> None:
        result = guidance_for("library/nowhere.py::NoFailure", "REQUEST_INVALID")

        self.assertIs(result.failure, GuidanceLookupFailure.SURFACE_UNKNOWN)
        self.assertIsNone(result.guidance)

    def test_one_code_string_on_two_surfaces_answers_differently(self) -> None:
        # `REQUEST_INVALID` names a code in both mutation gates, and
        # `INTEGRATION_FAILED` does too. A registry keyed on the bare code
        # would answer one of them with the other one and look like an answer.
        for code in ("REQUEST_INVALID", "INTEGRATION_FAILED"):
            with self.subTest(code=code):
                gate = guidance_for(DOCUMENT_GATE_SURFACE, code)
                door = guidance_for(CONTROL_PLANE_SURFACE, code)
                self.assertIs(gate.status, GuidanceLookupStatus.FOUND)
                self.assertIs(door.status, GuidanceLookupStatus.FOUND)
                assert gate.guidance is not None and door.guidance is not None
                self.assertNotEqual(gate.guidance.next_steps, door.guidance.next_steps)

    def test_a_code_held_as_an_enum_member_resolves_to_the_same_entry(self) -> None:
        # Callers hold the member, not the string. Every failure enum here
        # derives from `str`, so the member is the value and both forms have to
        # reach the same guidance or callers will learn to stringify by hand.
        member = guidance_for(
            DOCUMENT_GATE_SURFACE, DocumentMutationFailure.PATH_FORBIDDEN
        )
        plain = guidance_for(DOCUMENT_GATE_SURFACE, "PATH_FORBIDDEN")

        self.assertIs(member.status, GuidanceLookupStatus.FOUND)
        self.assertEqual(member.guidance, plain.guidance)

    def test_a_key_that_is_not_a_string_at_all_is_refused(self) -> None:
        for surface, code in (
            (DOCUMENT_GATE_SURFACE, None),
            (None, "PATH_FORBIDDEN"),
            (DOCUMENT_GATE_SURFACE, 7),
        ):
            with self.subTest(surface=surface, code=code):
                result = guidance_for(surface, code)  # type: ignore[arg-type]
                self.assertIs(
                    result.failure, GuidanceLookupFailure.REQUEST_INVALID
                )
                self.assertIsNone(result.guidance)

    def test_a_registry_that_is_not_a_table_fails_closed(self) -> None:
        result = guidance_for(DOCUMENT_GATE_SURFACE, "PATH_FORBIDDEN", registry=object())  # type: ignore[arg-type]

        self.assertIs(result.failure, GuidanceLookupFailure.REGISTRY_UNREADABLE)
        self.assertIsNone(result.guidance)

    def test_a_registry_holding_something_else_fails_closed(self) -> None:
        # The wrong answer this cell exists to forbid is "the table is broken,
        # so treat everything as resolvable". Fail-closed here means no
        # category at all, not the mildest one.
        poisoned = {(DOCUMENT_GATE_SURFACE, "PATH_FORBIDDEN"): "AGENT_MAY_RESOLVE"}
        result = guidance_for(DOCUMENT_GATE_SURFACE, "PATH_FORBIDDEN", registry=poisoned)  # type: ignore[arg-type]

        self.assertIs(result.failure, GuidanceLookupFailure.REGISTRY_UNREADABLE)
        self.assertIsNone(result.guidance)

    def test_an_empty_registry_is_unreadable_rather_than_permissive(self) -> None:
        result = guidance_for(DOCUMENT_GATE_SURFACE, "PATH_FORBIDDEN", registry={})

        self.assertIs(result.status, GuidanceLookupStatus.UNAVAILABLE)
        self.assertIsNone(result.guidance)


class NeverAutoResolveGuidanceTests(unittest.TestCase):
    """The third category may not carry the way around it.

    The ban has no carve-out for prohibitions. "Do not recompute the digest"
    has already put the verb and the object in front of a reader who is
    scanning for an action, and the reader is an agent. Guidance in this
    category therefore says what holds and who to tell, and never names the
    move.
    """

    def test_no_shipped_guidance_in_this_category_carries_a_bypass_term(self) -> None:
        self.assertEqual(never_auto_resolve_violations(GUIDANCE), ())

    def test_the_checker_catches_a_bypass_term_that_is_planted(self) -> None:
        planted = (
            RefusalGuidance(
                surface="surface",
                code="CODE",
                category=RefusalCategory.NEVER_AUTO_RESOLVE,
                next_steps=(
                    "Stop. This is serious.",
                    "You can skip the check if you are in a hurry.",
                    "Then tell the person.",
                ),
            ),
        )

        violations = never_auto_resolve_violations(planted)

        self.assertEqual(len(violations), 1)
        self.assertIn("skip", violations[0])

    def test_the_checker_catches_a_prohibition_that_still_names_the_move(self) -> None:
        planted = (
            RefusalGuidance(
                surface="surface",
                code="CODE",
                category=RefusalCategory.NEVER_AUTO_RESOLVE,
                next_steps=(
                    "Stop. Do not recompute the digest yourself.",
                    "Tell the person.",
                ),
            ),
        )

        self.assertIn("recompute", " ".join(never_auto_resolve_violations(planted)))

    def test_the_category_must_also_earn_its_name_positively(self) -> None:
        # A lexicon only refuses phrasings somebody thought of. These two
        # requirements are what catches guidance that dodges every listed term
        # and still fails to stop or to route anywhere.
        quiet = (
            RefusalGuidance(
                surface="surface",
                code="CODE",
                category=RefusalCategory.NEVER_AUTO_RESOLVE,
                next_steps=("Have another look at the archive and try again.",),
            ),
        )

        violations = never_auto_resolve_violations(quiet)

        self.assertIn("the first step does not stop", " ".join(violations))
        self.assertIn("routes this to a person", " ".join(violations))

    def test_the_lexicon_anchors_at_word_starts_and_allows_inflections(self) -> None:
        # Open at the end because these verbs arrive inflected; anchored at the
        # start so `enforcement` is not a hit on `force`.
        self.assertEqual(bypass_terms_in("enforcement is the point"), ())
        self.assertEqual(bypass_terms_in("forced through"), ("force",))
        self.assertEqual(bypass_terms_in("skipped the check"), ("skip",))
        self.assertEqual(bypass_terms_in("widening the boundary"), ("widen",))
        self.assertEqual(bypass_terms_in("a work around exists"), ("work around",))
        self.assertEqual(bypass_terms_in("a workaround exists"), ("workaround",))

    def test_the_lexicon_is_not_empty(self) -> None:
        # A checker with nothing to check passes every cell above it.
        self.assertGreaterEqual(len(BYPASS_TERMS), 15)

    def test_the_codes_the_ticket_names_are_in_the_third_category(self) -> None:
        named = (
            (INSTALL_WRAPPER_SURFACE, "DIGEST_MISMATCH"),
            (CONTROL_PLANE_SURFACE, "POLICY_REPIN_STALE"),
            (DOCUMENT_GATE_SURFACE, "PATH_FORBIDDEN"),
            (DOCUMENT_GATE_SURFACE, "MODIFICATION_OUTSIDE_BOUNDARY"),
            (DOCUMENT_GATE_SURFACE, "CREATION_NOT_AUTHORIZED"),
            (DOCUMENT_GATE_SURFACE, "DELETION_NOT_AUTHORIZED"),
            (DOCUMENT_GATE_SURFACE, "BOUNDARY_UNDECLARED"),
            (DOCUMENT_GATE_SURFACE, "BOUNDARY_UNPARSABLE"),
        )
        for surface, code in named:
            with self.subTest(code=code):
                self.assertIs(
                    REGISTRY[(surface, code)].category,
                    RefusalCategory.NEVER_AUTO_RESOLVE,
                )

    def test_a_declined_confirmation_is_not_an_owner_decision_to_relay(self) -> None:
        # `USER_DECLINED` has the shape of `OWNER_MUST_DECIDE` -- a person
        # supplies a value -- and is not one. The value lands inside the check
        # that was reaching for the person, so a relayed answer manufactures
        # consent instead of carrying it.
        self.assertIs(
            REGISTRY[(INSTALL_SCRIPT_SURFACE, "USER_DECLINED")].category,
            RefusalCategory.NEVER_AUTO_RESOLVE,
        )

    def test_an_unreadable_classification_table_is_in_the_third_category(self) -> None:
        self.assertIs(
            REGISTRY[(LOOKUP_SURFACE, "REGISTRY_UNREADABLE")].category,
            RefusalCategory.NEVER_AUTO_RESOLVE,
        )


class ClassificationAuditTests(unittest.TestCase):
    """Every code that exists is classified, and every enum is accounted for."""

    def test_this_repository_is_complete_on_every_covered_surface(self) -> None:
        audit = audit_classification(_REPO_ROOT)

        self.assertEqual(audit.unclassified_codes, ())
        self.assertEqual(audit.orphan_entries, ())
        self.assertEqual(audit.unreadable_surfaces, ())
        self.assertEqual(audit.guidance_violations, ())
        self.assertEqual(audit.unaccounted_enums, ())
        self.assertIs(audit.status, ClassificationAuditStatus.COMPLETE)

    def test_a_code_with_no_entry_is_reported_rather_than_defaulted(self) -> None:
        thinned = tuple(
            entry
            for entry in GUIDANCE
            if entry.key != (DOCUMENT_GATE_SURFACE, "PATH_FORBIDDEN")
        )

        audit = audit_classification(_REPO_ROOT, thinned)

        self.assertIs(audit.status, ClassificationAuditStatus.INCOMPLETE)
        self.assertIn(
            f"{DOCUMENT_GATE_SURFACE}::PATH_FORBIDDEN", audit.unclassified_codes
        )

    def test_an_entry_for_a_code_that_no_longer_exists_is_reported(self) -> None:
        # This is what a renamed enum value looks like from here: guidance
        # still present, pointing at a string nothing raises any more, while
        # whatever replaced it is silently unclassified.
        widened = GUIDANCE + (
            RefusalGuidance(
                surface=DOCUMENT_GATE_SURFACE,
                code="PATH_FORBIDDEN_V2",
                category=RefusalCategory.NEVER_AUTO_RESOLVE,
                next_steps=("Stop.", "Tell the person."),
            ),
        )

        audit = audit_classification(_REPO_ROOT, widened)

        self.assertIs(audit.status, ClassificationAuditStatus.INCOMPLETE)
        self.assertIn(
            f"{DOCUMENT_GATE_SURFACE}::PATH_FORBIDDEN_V2", audit.orphan_entries
        )

    def test_guidance_violations_make_the_audit_incomplete(self) -> None:
        planted = GUIDANCE + (
            RefusalGuidance(
                surface=DOCUMENT_GATE_SURFACE,
                code="PATH_FORBIDDEN_V2",
                category=RefusalCategory.NEVER_AUTO_RESOLVE,
                next_steps=("Stop.", "You can override it.", "Tell the person."),
            ),
        )

        audit = audit_classification(_REPO_ROOT, planted)

        self.assertIs(audit.status, ClassificationAuditStatus.INCOMPLETE)
        self.assertTrue(audit.guidance_violations)

    def test_every_failure_enum_in_the_library_is_covered_or_uncovered(self) -> None:
        audit = audit_classification(_REPO_ROOT)

        self.assertEqual(set(audit.covered_enums), _COVERED_ENUM_ROSTER)
        self.assertEqual(set(audit.uncovered_enums), _UNCOVERED_ROSTER)
        self.assertEqual(
            set(audit.discovered_enums),
            _COVERED_ENUM_ROSTER | _UNCOVERED_ROSTER,
        )
        self.assertEqual(len(audit.discovered_enums), 48)
        self.assertEqual(len(audit.uncovered_enums), 45)

    def test_the_uncovered_list_is_read_from_the_sources_not_recited(self) -> None:
        # Nailed on a tree this cell wrote, so a constant returned in place of
        # the list cannot pass: nothing hard-coded could name this enum.
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "library").mkdir()
            (root / "library" / "planted.py").write_text(
                "from enum import Enum\n\n\n"
                "class PlantedFailure(str, Enum):\n"
                '    ONE = "ONE"\n'
                '    TWO = "TWO"\n',
                encoding="utf-8",
            )

            audit = audit_classification(root, ())

            self.assertEqual(
                audit.uncovered_enums, ("library/planted.py::PlantedFailure",)
            )
            self.assertEqual(audit.unaccounted_enums, ())

    def test_a_covered_surface_that_cannot_be_read_is_not_a_surface_with_no_codes(
        self,
    ) -> None:
        # The fail-closed case. An unreadable installer treated as an empty one
        # would report full coverage of a file nobody could open.
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "library").mkdir()

            audit = audit_classification(root, ())

            self.assertIs(audit.status, ClassificationAuditStatus.INCOMPLETE)
            self.assertIn(INSTALL_SCRIPT_SURFACE, audit.unreadable_surfaces)
            self.assertIn(INSTALL_WRAPPER_SURFACE, audit.unreadable_surfaces)

    def test_every_covered_surface_has_at_least_one_entry(self) -> None:
        for surface in COVERED_SURFACES:
            with self.subTest(surface=surface):
                self.assertTrue(
                    any(entry.surface == surface for entry in GUIDANCE),
                    f"{surface} is declared covered and has no guidance",
                )


class GuidanceTransportTests(unittest.TestCase):
    """The text has to survive a JSON literal and a PowerShell literal.

    Guidance is built into JSON by string formatting in PowerShell and stored
    in single-quoted PowerShell strings, and a checker that had to reason about
    escaping in two languages would eventually get one of them wrong. Banning
    the three characters costs a little prose and removes the whole question.
    """

    def test_every_step_is_ascii_and_needs_no_escaping(self) -> None:
        for entry in GUIDANCE:
            with self.subTest(surface=entry.surface, code=entry.code):
                self.assertTrue(
                    guidance_is_transport_safe(entry),
                    f"{entry.code}: guidance must be ASCII with no quote, "
                    "apostrophe or backslash",
                )

    def test_installer_guidance_survives_a_json_round_trip(self) -> None:
        for (surface, code), entry in REGISTRY.items():
            if surface != INSTALL_SCRIPT_SURFACE:
                continue
            payload = (
                '{"status":"BLOCKED","code":"%s","category":"%s","next_steps":[%s]}'
                % (
                    code,
                    entry.category.value,
                    ",".join('"' + step + '"' for step in entry.next_steps),
                )
            )
            with self.subTest(code=code):
                decoded = json.loads(payload)
                self.assertEqual(tuple(decoded["next_steps"]), entry.next_steps)


class InstallScriptTests(unittest.TestCase):
    """The installer carries the same table, and nobody keeps it in step by hand.

    PowerShell cannot reach into a Python module, so the script holds a copy.
    A copy that a person has to remember to update is the drift this ticket
    would otherwise create, so these cells parse the script and compare it.
    """

    def test_the_script_table_matches_the_module_registry_exactly(self) -> None:
        parsed = parse_install_script_guidance(_INSTALL_SCRIPT)
        self.assertIsNotNone(parsed)
        assert parsed is not None

        expected = {
            code: entry
            for (surface, code), entry in REGISTRY.items()
            if surface == INSTALL_SCRIPT_SURFACE
        }

        self.assertEqual(set(parsed), set(expected))
        for code, entry in sorted(expected.items()):
            with self.subTest(code=code):
                self.assertEqual(parsed[code].category, entry.category)
                self.assertEqual(parsed[code].next_steps, entry.next_steps)

    def test_every_refusal_the_script_can_raise_has_an_entry(self) -> None:
        codes = discover_install_script_codes(_INSTALL_SCRIPT)
        self.assertIsNotNone(codes)
        assert codes is not None

        parsed = parse_install_script_guidance(_INSTALL_SCRIPT)
        assert parsed is not None

        self.assertEqual(set(codes), set(parsed))
        for code in codes:
            with self.subTest(code=code):
                self.assertIn((INSTALL_SCRIPT_SURFACE, code), REGISTRY)

    def test_every_refusal_the_wrapper_can_raise_has_an_entry(self) -> None:
        codes = discover_install_wrapper_codes(_INSTALL_WRAPPER)
        self.assertIsNotNone(codes)
        assert codes is not None

        self.assertIn("DIGEST_MISMATCH", codes)
        for code in codes:
            with self.subTest(code=code):
                self.assertIn((INSTALL_WRAPPER_SURFACE, code), REGISTRY)

    def test_the_script_refuses_in_the_same_order_it_always_has(self) -> None:
        # This ticket adds what happens after a refusal and changes nothing
        # about when one happens. The call sites in source order are that
        # decision sequence, pinned here so a later edit to the guidance cannot
        # quietly move a gate.
        text = _INSTALL_SCRIPT.read_text(encoding="utf-8")
        order = [
            line.split("-Code '")[1].split("'")[0]
            for line in text.splitlines()
            if "Write-TypedResult -Status" in line and "-Code '" in line
        ]

        self.assertEqual(
            order,
            [
                "INSTALL_BLOCKED_INSIDE_REPOSITORY",
                "GIT_UNAVAILABLE",
                "BUNDLE_NOT_FOUND",
                "PYTHON_311_UNAVAILABLE",
                "RUNTIME_LOCK_MISSING",
                "USER_DECLINED",
                "BOOTSTRAP_MISSING",
            ],
        )

    def test_a_real_refusal_keeps_status_and_code_where_they_were(self) -> None:
        # The released wrapper and the acceptance suite already read this line.
        # The ticket adds fields; it does not move the two that were there.
        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(_INSTALL_SCRIPT),
                "-BundleZip",
                "a-bundle-that-is-not-here.zip",
            ],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            check=False,
        )
        stdout = completed.stdout.decode("utf-8", errors="replace")
        line = next(
            candidate
            for candidate in stdout.splitlines()
            if candidate.startswith('{"status":')
        )

        self.assertEqual(completed.returncode, 2)
        self.assertTrue(line.startswith('{"status":"BLOCKED","code":"'))

        payload = json.loads(line)
        self.assertEqual(payload["status"], "BLOCKED")
        entry = REGISTRY[(INSTALL_SCRIPT_SURFACE, payload["code"])]
        self.assertEqual(payload["category"], entry.category.value)
        self.assertEqual(tuple(payload["next_steps"]), entry.next_steps)
        # The steps are also printed as plain lines, because the person who
        # double-clicked this is not going to read JSON.
        for step in entry.next_steps:
            self.assertIn(step, stdout)


class DecisionLogicIsUnchangedTests(unittest.TestCase):
    """The enum values are the contract, and this ticket does not touch them.

    Something outside this repository already reads these strings. Ticket 22
    adds a second thing to say about a refusal; it does not rename the first.
    """

    def test_document_mutation_failure_values_are_unchanged(self) -> None:
        self.assertEqual(
            tuple(member.value for member in DocumentMutationFailure),
            (
                "REQUEST_INVALID",
                "REPOSITORY_UNREADABLE",
                "TICKET_UNREADABLE",
                "BOUNDARY_UNDECLARED",
                "BOUNDARY_UNPARSABLE",
                "PATH_NOT_REPOSITORY_RELATIVE",
                "REDIRECTION_ENTRY_NOT_ADMISSIBLE",
                "PATH_FORBIDDEN",
                "MODIFICATION_OUTSIDE_BOUNDARY",
                "CREATION_NOT_AUTHORIZED",
                "DELETION_NOT_AUTHORIZED",
                "INTEGRATION_FAILED",
            ),
        )

    def test_control_plane_mutation_failure_values_are_unchanged(self) -> None:
        self.assertEqual(
            tuple(member.value for member in ControlPlaneMutationFailure),
            (
                "REQUEST_INVALID",
                "PRINCIPAL_UNDECLARED",
                "PRINCIPAL_NOT_HOST",
                "CANDIDATE_NOT_CONTROL_PLANE",
                "REPOSITORY_UNREADABLE",
                "NOTHING_TO_INTEGRATE",
                "PATH_NOT_REPOSITORY_RELATIVE",
                "REDIRECTION_ENTRY_NOT_ADMISSIBLE",
                "RULE_AND_SUBJECT_IN_ONE_CHANGE",
                "POLICY_REPIN_STALE",
                "JOURNAL_UNWRITABLE",
                "INTEGRATION_FAILED",
            ),
        )

    def test_every_member_of_both_gates_is_classified(self) -> None:
        for surface, enum in (
            (DOCUMENT_GATE_SURFACE, DocumentMutationFailure),
            (CONTROL_PLANE_SURFACE, ControlPlaneMutationFailure),
        ):
            for member in enum:
                with self.subTest(surface=surface, code=member.value):
                    self.assertIn((surface, member.value), REGISTRY)


if __name__ == "__main__":
    unittest.main()
