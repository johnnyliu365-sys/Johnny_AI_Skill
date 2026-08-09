"""Executable D1..D8 closure for Ticket 02."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from pydantic import ValidationError

from library.local_orchestration import (
    CorrelationId,
    EventId,
    FakeProjectLock,
    FakeRepositorySnapshotPort,
    FakeRuntimeRouter,
    FastForwardAllowed,
    FastForwardBlocked,
    GuardedBlockReason,
    GuardedDecisionRequest,
    GuardedGitDecision,
    InMemoryMetadataEventStore,
    InMemoryProjectRegistry,
    InstallationId,
    ProjectReference,
    ProjectRegistration,
    RegistryLocator,
    RepositorySnapshot,
    ResumeOrchestration,
    RevisionDigest,
    RouterResumeStatus,
    RuntimeCompleted,
    RuntimeEvent,
    RuntimeHalted,
    RuntimeHaltReason,
    RuntimeNeedsUserAction,
)


@dataclass(frozen=True)
class RuntimeStack:
    event: RuntimeEvent
    store: InMemoryMetadataEventStore
    router: FakeRuntimeRouter
    registry: InMemoryProjectRegistry
    lock: FakeProjectLock
    snapshots: FakeRepositorySnapshotPort
    guarded: GuardedGitDecision
    runtime: ResumeOrchestration


class MetadataRuntimeAndGuardedGitTests(unittest.TestCase):
    def test_d1_first_event_completes_and_replay_halts_without_calls(self) -> None:
        with TemporaryDirectory() as directory:
            stack = build_stack(Path(directory))

            first = stack.runtime.resume(stack.event)
            replay = stack.runtime.resume(stack.event)

            self.assertIsInstance(first, RuntimeCompleted)
            assert_halted(replay, RuntimeHaltReason.REPLAYED)
            self.assertEqual(1, stack.router.resume_calls)
            self.assertEqual(1, stack.guarded.decision_calls)
            self.assertEqual(0, stack.guarded.git_mutation_count)
            self.assertEqual(1, len(stack.store.checkpoints))

    def test_d2_human_wait_never_reaches_guarded_decision(self) -> None:
        with TemporaryDirectory() as directory:
            stack = build_stack(Path(directory), RouterResumeStatus.NEEDS_USER_ACTION)
            result = stack.runtime.resume(stack.event)

            self.assertIsInstance(result, RuntimeNeedsUserAction)
            self.assertEqual(1, stack.router.resume_calls)
            self.assertEqual(0, stack.guarded.decision_calls)
            self.assertEqual(0, stack.guarded.git_mutation_count)

    def test_d3_only_exact_canonical_registry_root_is_admitted(self) -> None:
        with TemporaryDirectory() as directory:
            stack = build_stack(Path(directory))
            exact = stack.guarded.decide(GuardedDecisionRequest.from_event(stack.event))
            self.assertIsInstance(exact, FastForwardAllowed)
            initial_mutations = stack.registry.mutation_count
            canonical = stack.event.locator.value
            variants = (
                canonical + "-extra",
                canonical + "\\",
                canonical.lower(),
                canonical.replace("\\", "%5C"),
                canonical + "\\..",
                "",
            )
            for value in variants:
                with self.subTest(value=value):
                    try:
                        locator = RegistryLocator(value=value)
                    except ValidationError:
                        continue
                    result = stack.guarded.decide(
                        GuardedDecisionRequest(
                            installation_id=stack.event.installation_id,
                            project=stack.event.project,
                            expected_base=stack.event.expected_base,
                            locator=locator,
                        )
                    )
                    assert_guarded_blocked(result, GuardedBlockReason.LOCATOR_MISMATCH)
            self.assertEqual(initial_mutations, stack.registry.mutation_count)
            self.assertEqual(0, stack.guarded.git_mutation_count)

    def test_d4_required_metadata_values_reject_all_empty_shapes(self) -> None:
        invalid = ('{"value":null}', "{}", '{"value":""}', '{"value":" "}', '{"value":[]}')
        for payload in invalid:
            with self.subTest(model="EventId", payload=payload), self.assertRaises(ValidationError):
                EventId.model_validate_json(payload)
            with self.subTest(model="InstallationId", payload=payload), self.assertRaises(ValidationError):
                InstallationId.model_validate_json(payload)
            with self.subTest(model="ProjectReference", payload=payload), self.assertRaises(ValidationError):
                ProjectReference.model_validate_json(payload)
            with self.subTest(model="RevisionDigest", payload=payload), self.assertRaises(ValidationError):
                RevisionDigest.model_validate_json(payload)
            with self.subTest(model="CorrelationId", payload=payload), self.assertRaises(ValidationError):
                CorrelationId.model_validate_json(payload)
            with self.subTest(model="RegistryLocator", payload=payload), self.assertRaises(ValidationError):
                RegistryLocator.model_validate_json(payload)

    def test_d5_direct_and_runtime_paths_share_all_guard_conditions(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            cases: tuple[tuple[RuntimeStack, RuntimeEvent, GuardedBlockReason], ...] = ()

            foreign_install = build_stack(root / "foreign-install")
            event = foreign_install.event.model_copy(
                update={"installation_id": InstallationId(value="install-foreign")}
            )
            cases += ((foreign_install, event, GuardedBlockReason.INSTALLATION_MISMATCH),)

            foreign_project = build_stack(root / "foreign-project")
            event = foreign_project.event.model_copy(
                update={"project": ProjectReference(value="prj_ffffffffffffffff")}
            )
            cases += ((foreign_project, event, GuardedBlockReason.PROJECT_UNREGISTERED),)

            wrong_locator = build_stack(root / "wrong-locator")
            event = wrong_locator.event.model_copy(
                update={"locator": RegistryLocator(value=wrong_locator.event.locator.value + "-other")}
            )
            cases += ((wrong_locator, event, GuardedBlockReason.LOCATOR_MISMATCH),)

            dirty = build_stack(root / "dirty")
            dirty.snapshots.replace(snapshot_for(dirty.event, is_clean=False))
            cases += ((dirty, dirty.event, GuardedBlockReason.DIRTY),)

            stale = build_stack(root / "stale")
            event = stale.event.model_copy(
                update={"expected_base": RevisionDigest(value="rev-ffffffffffffffff")}
            )
            cases += ((stale, event, GuardedBlockReason.STALE_BASE),)

            non_ff = build_stack(root / "non-ff")
            non_ff.snapshots.replace(snapshot_for(non_ff.event, can_fast_forward=False))
            cases += ((non_ff, non_ff.event, GuardedBlockReason.NON_FAST_FORWARD),)

            contended = build_stack(root / "contended")
            contended.lock.contended = True
            cases += ((contended, contended.event, GuardedBlockReason.LOCK_CONTENDED),)

            for stack, blocked_event, reason in cases:
                with self.subTest(reason=reason.value):
                    direct = stack.guarded.decide(GuardedDecisionRequest.from_event(blocked_event))
                    indirect = stack.runtime.resume(blocked_event)
                    assert_guarded_blocked(direct, reason)
                    assert_halted(indirect, RuntimeHaltReason(reason.value))
                    self.assertEqual(0, stack.guarded.git_mutation_count)

    def test_d6_four_declared_failures_halt_with_unique_reasons(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            claim = build_stack(root / "claim")
            claim.store.fail_next_claim()
            claim_result = claim.runtime.resume(claim.event)

            router = build_stack(root / "router")
            router.router.fail_next_resume()
            router_result = router.runtime.resume(router.event)

            registry = build_stack(root / "registry")
            registry.registry.fail_next_resolve()
            registry_result = registry.runtime.resume(registry.event)

            guarded = build_stack(root / "guarded")
            guarded.guarded.fail_next_decision()
            guarded_result = guarded.runtime.resume(guarded.event)

            reasons = (
                RuntimeHaltReason.EVENT_CLAIM_FAILED,
                RuntimeHaltReason.ROUTER_RESUME_FAILED,
                RuntimeHaltReason.REGISTRY_RESOLVE_FAILED,
                RuntimeHaltReason.GUARDED_DECISION_FAILED,
            )
            for result, reason in zip(
                (claim_result, router_result, registry_result, guarded_result), reasons, strict=True
            ):
                assert_halted(result, reason)
            self.assertEqual(4, len(set(reasons)))
            self.assertEqual(0, sum(stack.guarded.git_mutation_count for stack in (claim, router, registry, guarded)))

    def test_d7_persistence_is_metadata_only_and_repositories_are_unchanged(self) -> None:
        sentinels = (
            "RAW-SOURCE-SENTINEL",
            "CONTEXT-SENTINEL",
            "PROMPT-SENTINEL",
            "SECRET-SENTINEL",
            "PII-SENTINEL",
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            existing = make_minimal_repository(root / "existing", b"existing")
            empty = make_minimal_repository(root / "empty", b"")
            before_existing = snapshot_tree(existing)
            before_empty = snapshot_tree(empty)
            status_existing = porcelain_for_minimal_repository(existing)
            status_empty = porcelain_for_minimal_repository(empty)

            allowed = build_stack(root / "allowed")
            raw_json = allowed.event.model_dump_json()
            for index, sentinel in enumerate(sentinels):
                injected = raw_json[:-1] + f',"raw_{index}":"{sentinel}"' + "}"
                with self.assertRaises(ValidationError):
                    RuntimeEvent.model_validate_json(injected)
            self.assertIsInstance(allowed.runtime.resume(allowed.event), RuntimeCompleted)
            router_metadata = "".join(request.model_dump_json() for request in allowed.router.requests)

            blocked = build_stack(root / "blocked")
            blocked.lock.contended = True
            self.assertIsInstance(blocked.runtime.resume(blocked.event), RuntimeHalted)

            persisted = "".join(allowed.store.serialized_checkpoints())
            persisted += "".join(blocked.store.serialized_checkpoints())
            for sentinel in sentinels:
                self.assertNotIn(sentinel, persisted)
            self.assertNotIn('"locator"', persisted)
            self.assertNotIn('"locator"', router_metadata)
            self.assertNotIn(allowed.event.locator.value, persisted)
            self.assertEqual(before_existing, snapshot_tree(existing))
            self.assertEqual(before_empty, snapshot_tree(empty))
            self.assertEqual(status_existing, porcelain_for_minimal_repository(existing))
            self.assertEqual(status_empty, porcelain_for_minimal_repository(empty))

    def test_d8_ticket_source_has_no_forbidden_capability(self) -> None:
        root = Path(__file__).parents[1] / "library" / "local_orchestration"
        files = (
            root / "__init__.py",
            root / "runtime_contracts.py",
            root / "runtime.py",
            root / "project_registry.py",
            root / "guarded_git.py",
        )
        exact = ("Any", "type: ignore")
        folded = (
            "credential",
            "auth" + "token",
            "sub" + "process",
            "socket",
            "http://",
            "https://",
            "git checkout",
            "git reset",
            "git commit",
            "git push",
            "target_project",
            "target-project",
            "guardedintegrationcoordinator",
            "routerengine",
            "temporal",
            "telemetry",
        )
        for source in files:
            text = source.read_text(encoding="utf-8")
            for fragment in exact:
                self.assertNotIn(fragment, text, f"{source.name}: {fragment}")
            for fragment in folded:
                self.assertNotIn(fragment, text.casefold(), f"{source.name}: {fragment}")


def build_stack(
    sandbox: Path, router_status: RouterResumeStatus = RouterResumeStatus.COMPLETED
) -> RuntimeStack:
    locator = RegistryLocator(value=str(sandbox.resolve()))
    event = RuntimeEvent(
        event_id=EventId(value="event-001"),
        installation_id=InstallationId(value="install-001"),
        project=ProjectReference(value="prj_0123456789abcdef"),
        expected_base=RevisionDigest(value="rev-0123456789abcdef"),
        correlation_id=CorrelationId(value="correlation-001"),
        locator=locator,
    )
    registry = InMemoryProjectRegistry()
    registry.register(
        ProjectRegistration(
            installation_id=event.installation_id,
            project=event.project,
            locator=event.locator,
        )
    )
    lock = FakeProjectLock()
    snapshots = FakeRepositorySnapshotPort(snapshot_for(event))
    guarded = GuardedGitDecision(registry, lock, snapshots)
    store = InMemoryMetadataEventStore()
    router = FakeRuntimeRouter(router_status)
    return RuntimeStack(
        event=event,
        store=store,
        router=router,
        registry=registry,
        lock=lock,
        snapshots=snapshots,
        guarded=guarded,
        runtime=ResumeOrchestration(store, router, guarded),
    )


def snapshot_for(
    event: RuntimeEvent,
    is_clean: bool = True,
    can_fast_forward: bool = True,
) -> RepositorySnapshot:
    return RepositorySnapshot(
        installation_id=event.installation_id,
        project=event.project,
        locator=event.locator,
        head_revision=RevisionDigest(value="rev-0123456789abcdef"),
        is_clean=is_clean,
        can_fast_forward=can_fast_forward,
    )


def assert_guarded_blocked(result: object, reason: GuardedBlockReason) -> None:
    if not isinstance(result, FastForwardBlocked):
        raise AssertionError(f"expected FastForwardBlocked, got {type(result).__name__}")
    if result.reason is not reason:
        raise AssertionError(f"expected {reason.value}, got {result.reason.value}")


def assert_halted(result: object, reason: RuntimeHaltReason) -> None:
    if not isinstance(result, RuntimeHalted):
        raise AssertionError(f"expected RuntimeHalted, got {type(result).__name__}")
    if result.reason is not reason:
        raise AssertionError(f"expected {reason.value}, got {result.reason.value}")


def snapshot_tree(root: Path) -> tuple[tuple[str, bytes], ...]:
    return tuple(
        (path.relative_to(root).as_posix(), path.read_bytes())
        for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file())
    )


def make_minimal_repository(root: Path, content: bytes) -> Path:
    metadata = root / ".git"
    (metadata / "objects" / "info").mkdir(parents=True)
    (metadata / "objects" / "pack").mkdir(parents=True)
    (metadata / "refs" / "heads").mkdir(parents=True)
    (metadata / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (metadata / "config").write_text(
        "[core]\n\trepositoryformatversion = 0\n\tbare = false\n", encoding="utf-8"
    )
    if content:
        (root / "existing.txt").write_bytes(content)
    return root


def porcelain_for_minimal_repository(root: Path) -> tuple[str, ...]:
    return tuple(
        f"?? {path.relative_to(root).as_posix()}"
        for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file())
        if ".git" not in path.relative_to(root).parts
    )


if __name__ == "__main__":
    unittest.main()
