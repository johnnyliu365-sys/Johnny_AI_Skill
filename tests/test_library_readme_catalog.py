from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]


class LibraryReadmeCatalogTest(unittest.TestCase):
    def test_every_catalog_directory_has_a_responsibility_and_prohibition_readme(self) -> None:
        expected_directories: tuple[str, ...] = (
            "library",
            "library/NLP",
            "library/NLP/python",
            "library/金流串接",
            "library/金流串接/python",
            "library/功能集群",
            "library/功能集群/python",
            "library/功能集群/kotlin",
            "library/功能集群/csharp",
        )

        for relative_directory in expected_directories:
            readme_path: Path = PROJECT_ROOT / relative_directory / "README.md"
            self.assertTrue(readme_path.is_file(), readme_path)
            readme_text: str = readme_path.read_text(encoding="utf-8")
            self.assertIn("## 責任", readme_text)
            self.assertIn("## 禁止用途", readme_text)

    def test_root_catalog_readme_preserves_the_read_only_source_boundary(self) -> None:
        readme_path: Path = PROJECT_ROOT / "library" / "README.md"

        self.assertTrue(readme_path.is_file(), readme_path)
        readme_text: str = readme_path.read_text(encoding="utf-8")
        self.assertIn("唯讀", readme_text)
        self.assertIn("不得修改", readme_text)


if __name__ == "__main__":
    unittest.main()
