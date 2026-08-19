"""A1: Antigravity loads the canonical skills; foreign entries survive."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.antigravity_registration import (
    SkillRegistrationFailure,
    SkillRegistrationStatus,
    register_johnny_skills,
    remove_johnny_skills,
    skills_config_path,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_FOREIGN = {"path": "~/personal-skills", "exclude": ["experimental-.*"]}


def _skills_dir(base: Path) -> Path:
    skills = base / "skills" / "johnny-project-takeover"
    skills.mkdir(parents=True)
    (skills / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")
    return base / "skills"


class ProjectSurfaceTests(unittest.TestCase):
    """A1-R1: the committed project surface matches the documented schema."""

    def test_the_project_skills_config_points_at_the_canonical_tree(self) -> None:
        document = json.loads(
            (_REPO_ROOT / ".agents" / "skills.json").read_text(encoding="utf-8")
        )
        self.assertEqual(document, {"entries": [{"path": "skills"}]})
        for skill in ("johnny-project-takeover", "apply-reusable-modules"):
            with self.subTest(skill=skill):
                self.assertTrue((_REPO_ROOT / "skills" / skill / "SKILL.md").is_file())

    def test_the_plugin_marker_and_rule_are_present(self) -> None:
        plugin = _REPO_ROOT / ".agents" / "plugins" / "johnny-ai-skill"
        self.assertEqual(
            json.loads((plugin / "plugin.json").read_text(encoding="utf-8")),
            {"name": "johnny-ai-skill"},
        )
        rule = (plugin / "rules" / "worktree-containment.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(".worktrees/", rule)

    def test_the_undocumented_marketplace_descriptor_is_gone(self) -> None:
        """It matched no Antigravity schema shipped with the product."""

        self.assertFalse(
            (_REPO_ROOT / ".agents" / "plugins" / "marketplace.json").exists()
        )

    def test_a1_r3_the_skills_tree_has_exactly_one_source_of_truth(self) -> None:
        copies = [
            path
            for path in _REPO_ROOT.rglob("SKILL.md")
            if ".git" not in path.parts and ".worktrees" not in path.parts
        ]
        for path in copies:
            with self.subTest(path=str(path.relative_to(_REPO_ROOT))):
                self.assertEqual(path.parts[-3], "skills")


class RegistrationTests(unittest.TestCase):
    def test_a1_r4_registration_is_idempotent(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            skills = _skills_dir(base)
            root = base / "config"
            first, failure = register_johnny_skills(root, skills)
            self.assertIs(first, SkillRegistrationStatus.REGISTERED)
            self.assertIsNone(failure)
            second, _ = register_johnny_skills(root, skills)
            self.assertIs(second, SkillRegistrationStatus.ALREADY_REGISTERED)
            document = json.loads(
                skills_config_path(root).read_text(encoding="utf-8")
            )
            matching = [
                entry
                for entry in document["entries"]
                if Path(entry["path"]) == skills.resolve()
            ]
            self.assertEqual(len(matching), 1)

    def test_a1_r5_removal_preserves_pre_existing_foreign_entries(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            skills = _skills_dir(base)
            root = base / "config"
            root.mkdir()
            skills_config_path(root).write_text(
                json.dumps({"entries": [_FOREIGN]}, indent=2), encoding="utf-8"
            )
            register_johnny_skills(root, skills)
            removed, _ = remove_johnny_skills(root, skills)
            self.assertIs(removed, SkillRegistrationStatus.REMOVED)
            document = json.loads(
                skills_config_path(root).read_text(encoding="utf-8")
            )
            self.assertEqual(document["entries"], [_FOREIGN])

    def test_removal_is_idempotent_and_never_deletes_a_foreign_file(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            skills = _skills_dir(base)
            root = base / "config"
            root.mkdir()
            config = skills_config_path(root)
            config.write_text(
                json.dumps({"entries": [_FOREIGN]}, indent=2), encoding="utf-8"
            )
            before = config.read_bytes()
            first, _ = remove_johnny_skills(root, skills)
            self.assertIs(first, SkillRegistrationStatus.NOT_REGISTERED)
            self.assertTrue(config.is_file())
            self.assertEqual(config.read_bytes(), before)

    def test_an_absent_skills_tree_is_refused_before_any_write(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            root = base / "config"
            status, failure = register_johnny_skills(root, base / "missing")
            self.assertIs(status, SkillRegistrationStatus.REFUSED)
            self.assertIs(failure, SkillRegistrationFailure.SKILLS_DIRECTORY_ABSENT)
            self.assertFalse(skills_config_path(root).exists())

    def test_a_malformed_config_is_refused_without_overwriting_it(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            skills = _skills_dir(base)
            root = base / "config"
            root.mkdir()
            config = skills_config_path(root)
            config.write_text("not json", encoding="utf-8")
            status, failure = register_johnny_skills(root, skills)
            self.assertIs(status, SkillRegistrationStatus.REFUSED)
            self.assertIs(failure, SkillRegistrationFailure.CONFIG_NOT_AN_OBJECT)
            self.assertEqual(config.read_text(encoding="utf-8"), "not json")


if __name__ == "__main__":
    unittest.main()
