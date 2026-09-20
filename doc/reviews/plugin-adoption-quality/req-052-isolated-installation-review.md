# REQ-052 | Payload and isolated-host installation review

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-PLUGIN-ADOPTION-QUALITY-REQ-052` / `CODE_REVIEW` / `01` |
| Authority | Owner: repair shipped profile/source-content policy, then rerun packaging and installation verification |
| Source | Policy commit `de624ec43ea047955a395dee4ec4e697d8f6d767`; materialised from control `1e50d2ef457a7a5de392fb8b34eb9fc2a8f51011` |
| Conclusion | `LOCAL_PAYLOAD_AND_INSTALLATION_VERIFIED / PUBLICATION_INCOMPLETE / EXECUTABLE_GATES_PENDING` |
| Reviewer | root; retained profile_delivery_audit supplies evidence only |
| Requirement | [REQ-052](../../requirements/active/2026/plugin-adoption-quality/REQ-20260920-052.md) |

## Scope and result

This qualification concerns the missing bundled model-profile and source-content policy repair.
The source reuses the existing shipped skill tree; development docs are not added to payload.
The retained helper examined exact control b70b6978 (including de624ec43) and returned no further
scoped policy finding. Root confirmed new-target/default-profile routing, broken explicit ref
HALT, and unconfigured Claude mapping as a named owner decision rather than an invented model.
This does not implement or qualify a protected dispatch, source-content or module-coupling gate.

Root generated the existing declaration-driven payload through materialise_publication_tree,
with .claude-plugin/marketplace.json as its pin carrier. No ref-producing/repin API was called.
154 selected files, no .git or development doc/tests tree. The generated inner pin is neutral.
The local test marketplace carrier is separate from that payload and points at ./payload;
it is not a changed public descriptor or installation from the development checkout.

Lab root: `C:/Users/GameBoy/AppData/Local/Temp/johnny-req052-b9f0285d`.
Local marketplace `johnny-req052-lab`, plugin `johnny-ai-skill`. The existing manifest label
0.4.14 was retained for this disposable local test; no new release named0.4.14 was published.
Archive `johnny-req052-local-qualification.zip`, SHA-256
`492b10a6607d82afae5d519ff73628e3d48b6eba3a51abd4d01b6625a59e3ecd`.
ZIP extraction and both host caches matched all154 exact relative paths and file hashes.

## Actual host qualification

Codex CLI0.153.4 and Claude Code2.1.231 were read back locally. Commands used child-process-only
CODEX_HOME, CLAUDE_CONFIG_DIR and CLAUDE_CODE_PLUGIN_CACHE_DIR under the lab, with cwd there;
no user-global cache/configuration, current desktop session or provider account was changed.
Existing Python subprocess timeout60s bounded each command; no model request or login was made.
The command forms were confirmed by local --help and official local-marketplace documentation.

Commands (paths below resolve under the lab root):

```text
codex plugin marketplace add <lab>/market --json
codex plugin add johnny-ai-skill@johnny-req052-lab --json
codex plugin list --marketplace johnny-req052-lab --json
claude plugin marketplace add <lab>/market --scope user
claude plugin install johnny-ai-skill@johnny-req052-lab --scope user
claude plugin list --json
claude plugin validate <lab>/market/payload/.claude-plugin/plugin.json
claude plugin details johnny-ai-skill@johnny-req052-lab
codex plugin remove johnny-ai-skill@johnny-req052-lab --json
claude plugin uninstall johnny-ai-skill@johnny-req052-lab --scope user
```

Both install/list operations returned exit0 and enabled/installed0.4.14 in the isolated paths.
Claude's fresh details process found the two skills, with Agents0/Hooks0/MCP0/LSP0; no hook is
claimed. Its manifest validation returned exit0 with the existing unknown payload-key warning.
Codex warned that helper PATH aliases cannot be created under Temp; install/readback still
succeeded. These warnings are not hidden or presented as runtime enforcement evidence.

Both native uninstalls returned exit0; fresh lists were empty. Codex removed its isolated cache;
Claude left its cache directory. No recursive manual cleanup was performed. The lab/archive
remain available for recovery. This is installation/removal qualification, not an in-place
upgrade, signed MSIX lifecycle, public remote publication, or active-session reload proof.
The future no-old-payload-cache objective is not claimed met.

## Tests and release boundary

Existing tests.test_plugin_payload_boundary: exit0, 41 tests in2.907s. The previously recorded
missing-reference reverse controls in REQ-052 remain separate evidence, not rerun here.
Full tests.test_plugin_publication was attempted once with timeout60s. It did NOT complete:
L5 stale-candidate test printed FAIL; nine pin-binding tests skipped with the explicit current
pin-is-stale reason; the outer subprocess timed out in the actual publication-anchor test.
No final suite summary/failure traceback was emitted before timeout. Do not invent a passing
count or assign the unprinted L5 assertion trace. Source inspection shows L5 first asserts the
current live pin matches the declaration (lines804–810), consistent with the known unrepinned
source change, but that is an inference, not a captured traceback.

No retry, timeout expansion, pin/ref movement, version bump, tag, push or release occurred.
Other publication/cache suites are NOT_RUN this turn. A read-only post-timeout snapshot found
no matching Python/Git command line for this publication test; it is not a universal claim
that every descendant process on the machine was inventoried or terminated.

Before a public release: admit the scoped source correction into the authority line, generate
and bind the new publication artifact under its release authority, verify the actual pin and
remote publication path, and complete the bounded release suite. This report does not grant
those effects or silently replace them with local CLI success. Responsibility/content hard
checks remain in the undelivered WA-04/CVE-04 contract work.

## Captured output

The following process-output captures are unfiltered; CRLF is represented as LF. Outputs whose
commands ran in separate processes retain their returned order. The publication capture ends
with the real timeout, not a fabricated completion.

### req052_codex_install

Exit `0`.

```text
WARNING: proceeding, even though we could not create PATH aliases: Refusing to create helper binaries under temporary dir "C:\\Users\\GameBoy\\AppData\\Local\\Temp\\" (codex_home: AbsolutePathBuf("C:\\Users\\GameBoy\\AppData\\Local\\Temp\\johnny-req052-b9f0285d\\codex-home"))
{
  "pluginId": "johnny-ai-skill@johnny-req052-lab",
  "name": "johnny-ai-skill",
  "marketplaceName": "johnny-req052-lab",
  "version": "0.4.14",
  "installedPath": "C:\\Users\\GameBoy\\AppData\\Local\\Temp\\johnny-req052-b9f0285d\\codex-home\\plugins\\cache\\johnny-req052-lab\\johnny-ai-skill\\0.4.14",
  "authPolicy": "ON_INSTALL"
}
```

### req052_claude_marketplace

Exit `0`.

```text
Adding marketplace…√ Successfully added marketplace: johnny-req052-lab (declared in user settings)
```

### req052_claude_install

Exit `0`.

```text
Installing plugin "johnny-ai-skill@johnny-req052-lab"...√ Successfully installed plugin: johnny-ai-skill@johnny-req052-lab (scope: user)
```

### req052_installed_lists

Exit `0`.

```text
WARNING: proceeding, even though we could not create PATH aliases: Refusing to create helper binaries under temporary dir "C:\\Users\\GameBoy\\AppData\\Local\\Temp\\" (codex_home: AbsolutePathBuf("C:\\Users\\GameBoy\\AppData\\Local\\Temp\\johnny-req052-b9f0285d\\codex-home"))
{
  "installed": [
    {
      "pluginId": "johnny-ai-skill@johnny-req052-lab",
      "name": "johnny-ai-skill",
      "marketplaceName": "johnny-req052-lab",
      "version": "0.4.14",
      "installed": true,
      "enabled": true,
      "source": {
        "source": "local",
        "path": "C:\\Users\\GameBoy\\AppData\\Local\\Temp\\johnny-req052-b9f0285d\\market\\payload"
      },
      "marketplaceSource": {
        "sourceType": "local",
        "source": "\\\\?\\C:\\Users\\GameBoy\\AppData\\Local\\Temp\\johnny-req052-b9f0285d\\market"
      },
      "installPolicy": "AVAILABLE",
      "authPolicy": "ON_INSTALL"
    }
  ],
  "available": []
}
[
  {
    "id": "johnny-ai-skill@johnny-req052-lab",
    "version": "0.4.14",
    "scope": "user",
    "enabled": true,
    "installPath": "C:\\Users\\GameBoy\\AppData\\Local\\Temp\\johnny-req052-b9f0285d\\claude-home\\plugins\\cache\\johnny-req052-lab\\johnny-ai-skill\\0.4.14",
    "installedAt": "2026-09-20T04:04:32.384Z",
    "lastUpdated": "2026-09-20T04:04:32.384Z"
  }
]
```

### req052_install_bytes

Exit `0`.

```text
EXACT_PAYLOAD_MATCH files=154 root=C:\Users\GameBoy\AppData\Local\Temp\johnny-req052-b9f0285d\archive-readback
EXACT_PAYLOAD_MATCH files=154 root=C:\Users\GameBoy\AppData\Local\Temp\johnny-req052-b9f0285d\codex-home\plugins\cache\johnny-req052-lab\johnny-ai-skill\0.4.14
EXACT_PAYLOAD_MATCH files=154 root=C:\Users\GameBoy\AppData\Local\Temp\johnny-req052-b9f0285d\claude-home\plugins\cache\johnny-req052-lab\johnny-ai-skill\0.4.14
skills/johnny-project-takeover/references/dispatch-model-profile.md SHA256=8bcac03837177959cc680e31985ea280693bb333360314b40e43cf7b39b67cc4
skills/johnny-project-takeover/references/source-content-boundary.md SHA256=c7d1fdf328924bfca8b9f91db6eb5384640aa8762e34125b594c06f3ce7e0a71
ARCHIVE_SHA256=492b10a6607d82afae5d519ff73628e3d48b6eba3a51abd4d01b6625a59e3ecd
```

### req052_uninstall

Exit `0`.

```text
WARNING: proceeding, even though we could not create PATH aliases: Refusing to create helper binaries under temporary dir "C:\\Users\\GameBoy\\AppData\\Local\\Temp\\" (codex_home: AbsolutePathBuf("C:\\Users\\GameBoy\\AppData\\Local\\Temp\\johnny-req052-b9f0285d\\codex-home"))
{
  "pluginId": "johnny-ai-skill@johnny-req052-lab",
  "name": "johnny-ai-skill",
  "marketplaceName": "johnny-req052-lab"
}
√ Successfully uninstalled plugin: johnny-ai-skill (scope: user)
WARNING: proceeding, even though we could not create PATH aliases: Refusing to create helper binaries under temporary dir "C:\\Users\\GameBoy\\AppData\\Local\\Temp\\" (codex_home: AbsolutePathBuf("C:\\Users\\GameBoy\\AppData\\Local\\Temp\\johnny-req052-b9f0285d\\codex-home"))
{
  "installed": [],
  "available": []
}
[]
CODEX_LAB_CACHE_EXISTS=False
CLAUDE_LAB_CACHE_EXISTS=True
```

### req052_payload_boundary

Exit `0`.

```text
test_the_committed_source_survives_the_validator (tests.test_plugin_payload_boundary.CommittedPinTests.test_the_committed_source_survives_the_validator) ... ok
test_the_pinned_sha_exists (tests.test_plugin_payload_boundary.CommittedPinTests.test_the_pinned_sha_exists) ... ok
test_the_pinned_sha_is_a_full_lowercase_sha (tests.test_plugin_payload_boundary.CommittedPinTests.test_the_pinned_sha_is_a_full_lowercase_sha) ... ok
test_the_plugin_and_marketplace_versions_agree (tests.test_plugin_payload_boundary.CommittedPinTests.test_the_plugin_and_marketplace_versions_agree) ... ok
test_the_source_is_no_longer_the_rest_of_the_repository (tests.test_plugin_payload_boundary.CommittedPinTests.test_the_source_is_no_longer_the_rest_of_the_repository) ... ok
test_level_one_does_not_import_the_level_two_manifest (tests.test_plugin_payload_boundary.ManifestIndependenceTests.test_level_one_does_not_import_the_level_two_manifest) ... ok
test_the_level_two_manifest_is_untouched_by_this_ticket (tests.test_plugin_payload_boundary.ManifestIndependenceTests.test_the_level_two_manifest_is_untouched_by_this_ticket)
Its exclusion of tests/ is the precedent Level 1 copied, not shared. ... ok
test_the_two_payload_lists_are_different_literals (tests.test_plugin_payload_boundary.ManifestIndependenceTests.test_the_two_payload_lists_are_different_literals)
Same shape, separate data: Level 2 ships no template/, Level 1 no root lock. ... ok
test_a_closure_error_is_not_a_declaration_error (tests.test_plugin_payload_boundary.PayloadClosureTests.test_a_closure_error_is_not_a_declaration_error)
Two failures, two names: the gate must say which one it hit. ... ok
test_a_shrunken_payload_raises_a_closure_error (tests.test_plugin_payload_boundary.PayloadClosureTests.test_a_shrunken_payload_raises_a_closure_error)
Dropping a tree the skills read must be caught, not tolerated. ... ok
test_every_path_shaped_token_resolving_nowhere_is_declared (tests.test_plugin_payload_boundary.PayloadClosureTests.test_every_path_shaped_token_resolving_nowhere_is_declared) ... ok
test_every_reference_that_escapes_is_a_declared_exception (tests.test_plugin_payload_boundary.PayloadClosureTests.test_every_reference_that_escapes_is_a_declared_exception) ... ok
test_no_skill_or_command_points_at_our_own_development_material (tests.test_plugin_payload_boundary.PayloadClosureTests.test_no_skill_or_command_points_at_our_own_development_material)
A skill may name a path in the *user's* project; it may not name ours. ... ok
test_target_owned_references_are_never_shipped (tests.test_plugin_payload_boundary.PayloadClosureTests.test_target_owned_references_are_never_shipped)
Naming a target-owned path is correct; carrying our copy of it is not. ... ok
test_the_committed_payload_is_closed (tests.test_plugin_payload_boundary.PayloadClosureTests.test_the_committed_payload_is_closed) ... ok
test_the_documents_the_skills_read_are_carried (tests.test_plugin_payload_boundary.PayloadClosureTests.test_the_documents_the_skills_read_are_carried)
The closure the skills actually walk: Workflow, CodeReview, wayfinder, catalog. ... ok
test_the_skills_and_commands_are_carried (tests.test_plugin_payload_boundary.PayloadClosureTests.test_the_skills_and_commands_are_carried) ... ok
test_a_declaration_naming_an_excluded_tree_is_rejected (tests.test_plugin_payload_boundary.PayloadDeclarationTests.test_a_declaration_naming_an_excluded_tree_is_rejected) ... ok
test_a_declaration_naming_modules_tickets_is_rejected (tests.test_plugin_payload_boundary.PayloadDeclarationTests.test_a_declaration_naming_modules_tickets_is_rejected) ... ok
test_an_absent_declaration_is_rejected (tests.test_plugin_payload_boundary.PayloadDeclarationTests.test_an_absent_declaration_is_rejected) ... ok
test_every_declared_entry_exists (tests.test_plugin_payload_boundary.PayloadDeclarationTests.test_every_declared_entry_exists) ... ok
test_excluded_payload_admission_is_a_reversible_red_mutation (tests.test_plugin_payload_boundary.PayloadDeclarationTests.test_excluded_payload_admission_is_a_reversible_red_mutation) ... ok
test_nested_trees_are_segment_exact_and_clean_at_the_manifest_boundary (tests.test_plugin_payload_boundary.PayloadDeclarationTests.test_nested_trees_are_segment_exact_and_clean_at_the_manifest_boundary) ... ok
test_the_declared_payload_is_a_list_not_a_remainder (tests.test_plugin_payload_boundary.PayloadDeclarationTests.test_the_declared_payload_is_a_list_not_a_remainder)
Every repository top-level entry is either enumerated or not shipped. ... ok
test_the_excluded_trees_are_not_shipped (tests.test_plugin_payload_boundary.PayloadDeclarationTests.test_the_excluded_trees_are_not_shipped)
tests/, doc/ and modules/tickets/ never appear in the payload. ... ok
test_the_plugin_surface_is_declared (tests.test_plugin_payload_boundary.PayloadDeclarationTests.test_the_plugin_surface_is_declared) ... ok
test_a_similar_prefix_does_not_join_the_payload (tests.test_plugin_payload_boundary.PayloadPathMatchingTests.test_a_similar_prefix_does_not_join_the_payload) ... ok
test_empty_and_traversing_paths_are_refused (tests.test_plugin_payload_boundary.PayloadPathMatchingTests.test_empty_and_traversing_paths_are_refused) ... ok
test_excluded_segments_and_suffixes_are_honoured (tests.test_plugin_payload_boundary.PayloadPathMatchingTests.test_excluded_segments_and_suffixes_are_honoured) ... ok
test_modules_and_modules_tickets_stay_distinguishable (tests.test_plugin_payload_boundary.PayloadPathMatchingTests.test_modules_and_modules_tickets_stay_distinguishable)
The exclusion mechanism can name modules/tickets without naming modules/spec. ... ok
test_no_payload_module_imports_an_excluded_tree (tests.test_plugin_payload_boundary.PayloadPythonImportTests.test_no_payload_module_imports_an_excluded_tree) ... ok
test_a_bare_relative_source_is_rejected (tests.test_plugin_payload_boundary.PinnedSourceValidatorTests.test_a_bare_relative_source_is_rejected) ... ok
test_a_floating_ref_is_rejected (tests.test_plugin_payload_boundary.PinnedSourceValidatorTests.test_a_floating_ref_is_rejected) ... ok
test_a_nonexistent_sha_is_observable (tests.test_plugin_payload_boundary.PinnedSourceValidatorTests.test_a_nonexistent_sha_is_observable) ... ok
test_an_abbreviated_sha_is_rejected (tests.test_plugin_payload_boundary.PinnedSourceValidatorTests.test_an_abbreviated_sha_is_rejected) ... ok
test_a_readable_document_without_references_returns_empty (tests.test_plugin_payload_boundary.ReferenceScanTests.test_a_readable_document_without_references_returns_empty) ... ok
test_an_absent_document_raises_instead_of_returning_empty (tests.test_plugin_payload_boundary.ReferenceScanTests.test_an_absent_document_raises_instead_of_returning_empty) ... ok
test_an_undecodable_document_raises (tests.test_plugin_payload_boundary.ReferenceScanTests.test_an_undecodable_document_raises) ... ok
test_every_payload_document_is_actually_readable (tests.test_plugin_payload_boundary.ReferenceScanTests.test_every_payload_document_is_actually_readable)
Fail closed: the closure proof is worthless if a document was skipped. ... ok
test_markdown_link_targets_are_found_and_link_text_is_not (tests.test_plugin_payload_boundary.ReferenceScanTests.test_markdown_link_targets_are_found_and_link_text_is_not) ... ok
test_placeholders_and_urls_are_not_paths (tests.test_plugin_payload_boundary.ReferenceScanTests.test_placeholders_and_urls_are_not_paths) ... ok

----------------------------------------------------------------------
Ran 41 tests in 2.907s

OK
```

### req052_publication_run

Exit `1`.

```text
test_l1_candidate_metadata_names_release_and_publication_source (tests.test_plugin_publication.CandidateMetadataTests.test_l1_candidate_metadata_names_release_and_publication_source) ... ok
test_l3_readme_uses_raw_descriptor_and_complete_user_commands (tests.test_plugin_publication.CandidateMetadataTests.test_l3_readme_uses_raw_descriptor_and_complete_user_commands) ... ok
test_l3_rejects_suspended_or_publication_routes_and_restores_green (tests.test_plugin_publication.CandidateMetadataTests.test_l3_rejects_suspended_or_publication_routes_and_restores_green) ... ok
test_l5_stale_candidate_pin_is_named_before_generation (tests.test_plugin_publication.CandidateMetadataTests.test_l5_stale_candidate_pin_is_named_before_generation) ... FAIL
test_a_neighbouring_prefix_is_not_swept_in (tests.test_plugin_publication.DeclarationDrivenTreeTests.test_a_neighbouring_prefix_is_not_swept_in)
``alphax`` and ``alpha-old`` are not ``alpha`` (defect class 1). ... ok
test_an_empty_declaration_is_refused_rather_than_publishing_nothing (tests.test_plugin_publication.DeclarationDrivenTreeTests.test_an_empty_declaration_is_refused_rather_than_publishing_nothing) ... ok
test_excluded_segments_and_suffixes_do_not_reach_the_tree (tests.test_plugin_publication.DeclarationDrivenTreeTests.test_excluded_segments_and_suffixes_do_not_reach_the_tree) ... ok
test_narrowing_the_declaration_narrows_the_tree (tests.test_plugin_publication.DeclarationDrivenTreeTests.test_narrowing_the_declaration_narrows_the_tree) ... ok
test_publishing_does_not_move_the_development_branch (tests.test_plugin_publication.DeclarationDrivenTreeTests.test_publishing_does_not_move_the_development_branch) ... ok
test_the_generator_cannot_guess_which_manifest_to_read (tests.test_plugin_publication.DeclarationDrivenTreeTests.test_the_generator_cannot_guess_which_manifest_to_read)
No default manifest path means no way to read a manifest nobody named. ... ok
test_the_generator_holds_no_payload_path_of_its_own (tests.test_plugin_publication.DeclarationDrivenTreeTests.test_the_generator_holds_no_payload_path_of_its_own)
A second enumeration is a second truth, so there must not be one. ... ok
test_the_produced_commit_is_a_reproducible_root (tests.test_plugin_publication.DeclarationDrivenTreeTests.test_the_produced_commit_is_a_reproducible_root)
Re-running on unchanged content reproduces the id, and starts a new history. ... ok
test_the_produced_tree_is_exactly_the_declaration (tests.test_plugin_publication.DeclarationDrivenTreeTests.test_the_produced_tree_is_exactly_the_declaration) ... ok
test_widening_the_declaration_widens_the_tree (tests.test_plugin_publication.DeclarationDrivenTreeTests.test_widening_the_declaration_widens_the_tree) ... ok
test_a_declaration_naming_an_excluded_tree_is_refused_by_the_generator (tests.test_plugin_publication.FailClosedTests.test_a_declaration_naming_an_excluded_tree_is_refused_by_the_generator) ... ok
test_a_difference_set_is_empty_only_when_the_trees_really_agree (tests.test_plugin_publication.FailClosedTests.test_a_difference_set_is_empty_only_when_the_trees_really_agree) ... ok
test_a_malformed_sha_is_a_declaration_failure_not_a_missing_commit (tests.test_plugin_publication.FailClosedTests.test_a_malformed_sha_is_a_declaration_failure_not_a_missing_commit) ... ok
test_a_sha_that_names_no_commit_is_its_own_failure (tests.test_plugin_publication.FailClosedTests.test_a_sha_that_names_no_commit_is_its_own_failure) ... ok
test_a_tree_missing_one_declared_file_is_named_as_missing (tests.test_plugin_publication.FailClosedTests.test_a_tree_missing_one_declared_file_is_named_as_missing) ... ok
test_an_absent_declaration_is_a_declaration_failure (tests.test_plugin_publication.FailClosedTests.test_an_absent_declaration_is_a_declaration_failure) ... ok
test_an_empty_tree_is_refused_rather_than_reported_as_a_match (tests.test_plugin_publication.FailClosedTests.test_an_empty_tree_is_refused_rather_than_reported_as_a_match) ... ok
test_an_uncomputable_tree_raises_instead_of_reading_as_empty (tests.test_plugin_publication.FailClosedTests.test_an_uncomputable_tree_raises_instead_of_reading_as_empty)
An unreadable tree compared against anything would otherwise "match". ... ok
test_an_undecodable_declaration_is_a_declaration_failure (tests.test_plugin_publication.FailClosedTests.test_an_undecodable_declaration_is_a_declaration_failure) ... ok
test_the_four_failures_are_four_distinguishable_names (tests.test_plugin_publication.FailClosedTests.test_the_four_failures_are_four_distinguishable_names) ... ok
test_a_non_empty_destination_is_refused (tests.test_plugin_publication.MaterialisedTreeTests.test_a_non_empty_destination_is_refused) ... ok
test_the_materialised_tree_matches_the_declaration_and_the_commit (tests.test_plugin_publication.MaterialisedTreeTests.test_the_materialised_tree_matches_the_declaration_and_the_commit) ... ok
test_a_pin_carrier_outside_the_payload_is_refused (tests.test_plugin_publication.PinCarrierTests.test_a_pin_carrier_outside_the_payload_is_refused) ... ok
test_a_published_copy_that_kept_a_usable_pin_is_rejected (tests.test_plugin_publication.PinCarrierTests.test_a_published_copy_that_kept_a_usable_pin_is_rejected)
The exemption covers the placeholder, not any content the pin slot holds. ... ok
test_carrier_outside_payload_and_bypass_pin_are_named_refusals (tests.test_plugin_publication.PinCarrierTests.test_carrier_outside_payload_and_bypass_pin_are_named_refusals) ... ok
test_closure_rejects_a_second_generated_placeholder_occurrence (tests.test_plugin_publication.PinCarrierTests.test_closure_rejects_a_second_generated_placeholder_occurrence) ... ok
test_closure_rejects_a_usable_generated_pin (tests.test_plugin_publication.PinCarrierTests.test_closure_rejects_a_usable_generated_pin) ... ok
test_closure_rejects_malformed_live_pin_and_restores_green (tests.test_plugin_publication.PinCarrierTests.test_closure_rejects_malformed_live_pin_and_restores_green) ... ok
test_closure_rejects_non_pin_carrier_mutation_and_restores_green (tests.test_plugin_publication.PinCarrierTests.test_closure_rejects_non_pin_carrier_mutation_and_restores_green) ... ok
test_closure_rejects_wrong_live_pin_and_restores_green (tests.test_plugin_publication.PinCarrierTests.test_closure_rejects_wrong_live_pin_and_restores_green) ... ok
test_publishing_twice_reproduces_the_same_id (tests.test_plugin_publication.PinCarrierTests.test_publishing_twice_reproduces_the_same_id)
Without this the step chases its own tail: every run repins to a new tree. ... ok
test_second_pin_occurrence_is_refused_and_restored (tests.test_plugin_publication.PinCarrierTests.test_second_pin_occurrence_is_refused_and_restored) ... ok
test_the_directory_form_and_the_commit_form_are_the_same_artifact (tests.test_plugin_publication.PinCarrierTests.test_the_directory_form_and_the_commit_form_are_the_same_artifact)
Two forms of one release must not differ by a live pin. ... ok
test_the_generator_and_closure_share_the_same_codec (tests.test_plugin_publication.PinCarrierTests.test_the_generator_and_closure_share_the_same_codec) ... ok
test_the_published_copy_differs_from_the_working_copy_only_in_the_pin (tests.test_plugin_publication.PinCarrierTests.test_the_published_copy_differs_from_the_working_copy_only_in_the_pin) ... ok
test_the_published_copy_records_an_id_that_names_nothing (tests.test_plugin_publication.PinCarrierTests.test_the_published_copy_records_an_id_that_names_nothing) ... ok
test_the_shared_carrier_codec_round_trips_source_and_generated_forms (tests.test_plugin_publication.PinCarrierTests.test_the_shared_carrier_codec_round_trips_source_and_generated_forms) ... ok
test_pinning_the_development_head_is_rejected (tests.test_plugin_publication.PinnedTreeBindingTests.test_pinning_the_development_head_is_rejected)
Pinning the development tree ships the excluded trees; that must not pass. ... ok
test_pinning_the_root_commit_is_rejected (tests.test_plugin_publication.PinnedTreeBindingTests.test_pinning_the_root_commit_is_rejected)
The reviewer's mutation, kept as a permanent case rather than a memory. ... ok
test_the_declared_hashes_are_computed_for_every_declared_path (tests.test_plugin_publication.PinnedTreeBindingTests.test_the_declared_hashes_are_computed_for_every_declared_path) ... ok
test_the_only_unbindable_path_is_the_one_that_records_the_pin (tests.test_plugin_publication.PinnedTreeBindingTests.test_the_only_unbindable_path_is_the_one_that_records_the_pin) ... skipped 'reviewer-generated publication pin C is pending; current pin is stale'
test_the_pin_and_the_tree_are_one_fact (tests.test_plugin_publication.PinnedTreeBindingTests.test_the_pin_and_the_tree_are_one_fact) ... skipped 'reviewer-generated publication pin C is pending; current pin is stale'
test_the_pinned_commit_carries_exactly_the_declared_paths (tests.test_plugin_publication.PinnedTreeBindingTests.test_the_pinned_commit_carries_exactly_the_declared_paths)
The reviewer's mutation dies here: a tree of three files is not this one. ... skipped 'reviewer-generated publication pin C is pending; current pin is stale'
test_the_pinned_commit_carries_no_development_history (tests.test_plugin_publication.PinnedTreeBindingTests.test_the_pinned_commit_carries_no_development_history)
A right tree on a wrong parent chain still hands over the whole history. ... skipped 'reviewer-generated publication pin C is pending; current pin is stale'
test_the_pinned_commit_carries_no_development_tree (tests.test_plugin_publication.PinnedTreeBindingTests.test_the_pinned_commit_carries_no_development_tree) ... skipped 'reviewer-generated publication pin C is pending; current pin is stale'
test_the_pinned_commit_carries_the_declared_content (tests.test_plugin_publication.PinnedTreeBindingTests.test_the_pinned_commit_carries_the_declared_content) ... skipped 'reviewer-generated publication pin C is pending; current pin is stale'
test_the_pinned_commit_is_smaller_than_the_development_tree (tests.test_plugin_publication.PinnedTreeBindingTests.test_the_pinned_commit_is_smaller_than_the_development_tree) ... skipped 'reviewer-generated publication pin C is pending; current pin is stale'
test_the_pinned_sha_names_a_commit_here (tests.test_plugin_publication.PinnedTreeBindingTests.test_the_pinned_sha_names_a_commit_here) ... skipped 'reviewer-generated publication pin C is pending; current pin is stale'
test_the_published_copy_of_the_pin_carrier_cannot_install_anything (tests.test_plugin_publication.PinnedTreeBindingTests.test_the_published_copy_of_the_pin_carrier_cannot_install_anything)
The shipped copy must not be a working pin at some older tree. ... skipped 'reviewer-generated publication pin C is pending; current pin is stale'
test_a_clean_clone_proves_local_and_last_fetch_remote_reachability (tests.test_plugin_publication.PublicationReachabilityTests.test_a_clean_clone_proves_local_and_last_fetch_remote_reachability)
The proof is about the checkout a user can clone, not this worktree. ... ok
test_a_local_only_branch_is_not_fetchability_evidence (tests.test_plugin_publication.PublicationReachabilityTests.test_a_local_only_branch_is_not_fetchability_evidence) ... ok
test_a_ref_query_failure_is_not_silently_reported_as_no_ref (tests.test_plugin_publication.PublicationReachabilityTests.test_a_ref_query_failure_is_not_silently_reported_as_no_ref) ... ok
test_a_remote_tracking_ref_is_explicitly_last_fetch_evidence (tests.test_plugin_publication.PublicationReachabilityTests.test_a_remote_tracking_ref_is_explicitly_last_fetch_evidence) ... ok
test_an_invalid_remote_tracking_ref_is_rejected_as_input (tests.test_plugin_publication.PublicationReachabilityTests.test_an_invalid_remote_tracking_ref_is_rejected_as_input) ... ok
test_an_unpushable_anchor_ref_is_rejected_as_input (tests.test_plugin_publication.PublicationReachabilityTests.test_an_unpushable_anchor_ref_is_rejected_as_input) ... ok
test_deleting_the_actual_publication_anchor_makes_the_marketplace_pin_unreachable (tests.test_plugin_publication.PublicationReachabilityTests.test_deleting_the_actual_publication_anchor_makes_the_marketplace_pin_unreachable)
Deleting the clean-clone tracking anchor must turn fetchability red. ... ok
test_moving_the_anchor_to_an_unpushable_namespace_makes_reachability_fail (tests.test_plugin_publication.PublicationReachabilityTests.test_moving_the_anchor_to_an_unpushable_namespace_makes_reachability_fail) ... ok
test_null_empty_and_malformed_fetchable_refs_are_named_input_errors (tests.test_plugin_publication.PublicationReachabilityTests.test_null_empty_and_malformed_fetchable_refs_are_named_input_errors) ... ok
test_removing_the_anchor_ref_makes_reachability_fail (tests.test_plugin_publication.PublicationReachabilityTests.test_removing_the_anchor_ref_makes_reachability_fail)
The reviewer's mutation must turn this proof red. ... ok
test_the_marketplace_pin_is_bound_to_the_actual_publication_anchor (tests.test_plugin_publication.PublicationReachabilityTests.test_the_marketplace_pin_is_bound_to_the_actual_publication_anchor) ... Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\subprocess.py", line 550, in run
    stdout, stderr = process.communicate(input, timeout=timeout)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\subprocess.py", line 1228, in communicate
    sts = self.wait(timeout=self._remaining_time(endtime))
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\subprocess.py", line 1264, in wait
    return self._wait(timeout=timeout)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\subprocess.py", line 1593, in _wait
    raise TimeoutExpired(self.args, timeout)
subprocess.TimeoutExpired: Command '['C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe', '-X', 'utf8', '-B', '-m', 'unittest', '-v', 'tests.test_plugin_publication']' timed out after 60.0 seconds
```
