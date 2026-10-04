from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "scripts" / "release.py"

_spec = importlib.util.spec_from_file_location("release_script", SCRIPT)
release = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(release)


def run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = release.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class ReleaseScriptTest(unittest.TestCase):
    def setUp(self) -> None:
        self.version = release.primary_version(PLUGIN_ROOT)
        self.tag = f"v{self.version}"
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        for file_name, _ in release.VERSION_FILES:
            target = self.tmp / file_name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PLUGIN_ROOT / file_name, target)
        (self.tmp / "CHANGELOG.md").write_text(
            "# Changelog\n\n"
            f"## {self.version} — 2026-10-01\n\n"
            "- New thing.\n"
            "- Fixed thing.\n\n"
            "## 0.0.1 — 2026-01-01\n\n"
            "- Old thing.\n",
            encoding="utf-8",
        )

    def test_version_files_list_matches_the_update_contract(self) -> None:
        metadata = json.loads((PLUGIN_ROOT / "ai-factory.json").read_text())
        declared = [
            f"{name}#/" + "/".join(str(key) for key in keys)
            for name, keys in release.VERSION_FILES
        ]
        self.assertEqual(metadata["update"]["versionLocations"], declared)

    def test_version_prints_the_primary_version(self) -> None:
        code, out, _ = run("version")
        self.assertEqual(0, code)
        self.assertEqual(self.version, out.strip())

    def test_repository_agrees_with_its_current_version(self) -> None:
        code, _, err = run("check", "--tag", self.tag)
        self.assertEqual(0, code, err)

    def test_agreement_passes(self) -> None:
        code, out, err = run("--root", str(self.tmp), "check", "--tag", self.tag)
        self.assertEqual(0, code, err)
        self.assertIn("passed", out)

    def test_mismatched_version_file_fails(self) -> None:
        path = self.tmp / ".claude-plugin" / "marketplace.json"
        data = json.loads(path.read_text())
        data["plugins"][0]["version"] = "9.9.9"
        path.write_text(json.dumps(data))
        code, _, err = run("--root", str(self.tmp), "check", "--tag", self.tag)
        self.assertEqual(1, code)
        self.assertIn(".claude-plugin/marketplace.json", err)

    def test_mismatched_release_tag_fails(self) -> None:
        path = self.tmp / "ai-factory.json"
        data = json.loads(path.read_text())
        data["package"]["releaseTag"] = "v9.9.9"
        path.write_text(json.dumps(data))
        code, _, err = run("--root", str(self.tmp), "check", "--tag", self.tag)
        self.assertEqual(1, code)
        self.assertIn("releaseTag", err)

    def test_other_tag_fails(self) -> None:
        code, _, err = run("--root", str(self.tmp), "check", "--tag", "v9.9.9")
        self.assertEqual(1, code)
        self.assertIn("expected '9.9.9'", err)

    def test_missing_changelog_section_fails(self) -> None:
        (self.tmp / "CHANGELOG.md").write_text(
            "# Changelog\n\n## 0.0.1 — 2026-01-01\n\n- Old thing.\n",
            encoding="utf-8",
        )
        code, _, err = run("--root", str(self.tmp), "check", "--tag", self.tag)
        self.assertEqual(1, code)
        self.assertIn(f"no '## {self.version} — ' section", err)

    def test_malformed_tag_fails(self) -> None:
        code, _, err = run("--root", str(self.tmp), "check", "--tag", self.version)
        self.assertEqual(1, code)
        self.assertIn("vX.Y.Z", err)

    def test_notes_returns_exactly_the_section_body(self) -> None:
        code, out, err = run("--root", str(self.tmp), "notes", "--tag", self.tag)
        self.assertEqual(0, code, err)
        self.assertEqual("- New thing.\n- Fixed thing.\n", out)

    def test_notes_for_last_section(self) -> None:
        code, out, _ = run("--root", str(self.tmp), "notes", "--tag", "v0.0.1")
        self.assertEqual(0, code)
        self.assertEqual("- Old thing.\n", out)


if __name__ == "__main__":
    unittest.main()
