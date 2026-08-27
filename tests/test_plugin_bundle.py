from __future__ import annotations

import json
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {
    "ai-factory",
    "factory-artifacts",
    "factory-classify",
    "factory-critic",
    "factory-gates",
    "factory-large",
    "factory-medium",
    "factory-qa-loop",
    "factory-release",
    "factory-small",
}


class AiFactoryPluginBundleTest(unittest.TestCase):
    def test_bundle_contains_exactly_the_declared_skills(self) -> None:
        skills_root = PLUGIN_ROOT / "skills"
        actual = {
            path.parent.name
            for path in skills_root.glob("*/SKILL.md")
        }
        self.assertEqual(EXPECTED_SKILLS, actual)

    def test_every_skill_has_matching_front_matter_name(self) -> None:
        for skill_name in EXPECTED_SKILLS:
            content = (PLUGIN_ROOT / "skills" / skill_name / "SKILL.md").read_text()
            self.assertTrue(content.startswith(f"---\nname: {skill_name}\n"))

    def test_manifests_agree_on_identity_and_version(self) -> None:
        codex = json.loads(
            (PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text()
        )
        claude = json.loads(
            (PLUGIN_ROOT / ".claude-plugin/plugin.json").read_text()
        )
        marketplace = json.loads(
            (PLUGIN_ROOT / ".claude-plugin/marketplace.json").read_text()
        )
        metadata = json.loads((PLUGIN_ROOT / "ai-factory.json").read_text())

        self.assertEqual("ai-factory", codex["name"])
        self.assertEqual(codex["name"], claude["name"])
        self.assertEqual(metadata["package"]["name"], codex["name"])
        self.assertEqual(codex["version"], claude["version"])
        self.assertEqual(codex["version"], marketplace["plugins"][0]["version"])
        self.assertEqual(metadata["package"]["version"], codex["version"])
        self.assertEqual(
            f"v{codex['version']}", metadata["package"]["releaseTag"]
        )
        self.assertEqual("./skills/", codex["skills"])
        self.assertEqual("./", marketplace["plugins"][0]["source"])

    def test_metadata_declares_the_canonical_update_contract(self) -> None:
        metadata = json.loads((PLUGIN_ROOT / "ai-factory.json").read_text())

        self.assertEqual(1, metadata["schemaVersion"])
        self.assertEqual(
            "https://github.com/aiatsuk/factory",
            metadata["package"]["repository"],
        )
        self.assertEqual("main", metadata["package"]["defaultBranch"])
        self.assertEqual(
            ".codex-plugin/plugin.json",
            metadata["entrypoints"]["codexManifest"],
        )
        self.assertEqual(
            ".claude-plugin/plugin.json",
            metadata["entrypoints"]["claudeManifest"],
        )
        self.assertEqual(
            ".claude-plugin/marketplace.json",
            metadata["entrypoints"]["claudeMarketplace"],
        )
        self.assertEqual("skills/", metadata["entrypoints"]["skillsDirectory"])
        self.assertTrue(metadata["update"]["remoteMetadataUrl"].startswith("https://"))
        self.assertEqual(4, len(metadata["update"]["versionLocations"]))

    def test_starter_prompts_invoke_the_entrypoint(self) -> None:
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text()
        )
        prompts = manifest["interface"]["defaultPrompt"]
        self.assertGreater(len(prompts), 0)
        self.assertTrue(all("$ai-factory" in prompt for prompt in prompts))

    def test_public_bundle_has_no_project_local_references(self) -> None:
        text = "\n".join(
            (PLUGIN_ROOT / "skills" / skill_name / "SKILL.md").read_text()
            for skill_name in EXPECTED_SKILLS
        ).lower()
        for forbidden in ("arcadia", "yxpro", "tanker", "agents/profiles"):
            self.assertNotIn(forbidden, text)

    def test_bundle_has_no_unshipped_runtime_components(self) -> None:
        self.assertFalse((PLUGIN_ROOT / ".mcp.json").exists())
        self.assertFalse((PLUGIN_ROOT / ".app.json").exists())
        self.assertFalse((PLUGIN_ROOT / "commands").exists())
        self.assertFalse((PLUGIN_ROOT / "hooks").exists())
        self.assertFalse((PLUGIN_ROOT / "hooks.json").exists())


if __name__ == "__main__":
    unittest.main()
