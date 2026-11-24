import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from live_review import fixture, git, inventory


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "project-style-review" / "scripts" / "scope.py"


class ScopeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="style-review-tests-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "Übungs Projekt"
        self.root.mkdir()

    def put(self, name, value="Example text.\n"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value.encode("utf-8") if isinstance(value, str) else value)
        return path

    def run_helper(self, *args, code=0, env=None, root=None):
        result = subprocess.run([sys.executable, "-I", "-B", str(HELPER),
                                 str(self.root if root is None else root), *args],
                                text=True, capture_output=True, env=env, check=False)
        self.assertEqual(result.returncode, code, result.stderr)
        return json.loads(result.stdout) if code == 0 else result.stderr

    def test_ordinary_folder_ignores_and_read_only(self):
        self.put(".gitignore", "/sole.md\nignored/\n*.log\n**/private-?.md\n"
                               "draft*.md\n!draft-final.md\n\\#frag.md\nwith\\ \n"
                               "cache/**\n")
        self.put(".ignore", "other.md\n")
        self.put("docs/.gitignore", "/anchored.md\n[ab].md\n")
        expected = {
            ".gitignore", ".ignore", "docs/.gitignore", "draft-final.md",
            "docs/sole.md", "docs/reference.md", "docs/nested/anchored.md",
            "docs/de-AT.strings", "docs/Erste Schritte.md",
        }
        for name in expected - {".gitignore", ".ignore", "docs/.gitignore", "docs/de-AT.strings"}:
            self.put(name)
        self.put("docs/de-AT.strings", '"save" = "Änderungen sichern";\n'.encode("utf-16"))
        for name in ("sole.md", "ignored/keep.md", "docs/private-a.md", "draft-tmp.md",
                     "other.md", "#frag.md", "with ", "cache/a.md", "docs/anchored.md",
                     "docs/a.md", "docs/a.log", "build/README.md", "node_modules/index.js",
                     "Generated.generated.swift", ".env.local", "creds.pem", "docs/blob.txt"):
            self.put(name)
        self.put("Auto.swift", "// @generated from a schema\nlet option = 1\n")
        self.put("opaque.md", b"\0\1\2")
        self.put("big.md", b"x" * (192 * 1024 + 1))
        self.put("config.toml", 'api_key = "fixture-local-token"\n')
        self.put(".hidden", b"control")
        self.put("docs/blob.txt", b"\xc0\x80")
        outside = self.base / "outside.md"
        outside.write_text("Outside content\n", encoding="utf-8")
        (self.root / "external.md").symlink_to(outside)
        (self.root / "other-dir").symlink_to(self.base, target_is_directory=True)

        before = inventory(self.root)
        manifest = self.run_helper(env={**os.environ, "PATH": ""})
        self.assertEqual(manifest["mode"], "folder")
        self.assertEqual({entry["path"] for entry in manifest["files"]}, expected)
        self.assertEqual(manifest["skipped_entries"]["symlink"], 2)
        self.assertEqual(manifest["skipped_entries"]["ignored entry"], 11)
        self.assertEqual(manifest["skipped_entries"]["possible secret"], 1)
        result = self.run_helper("--read", "docs/de-AT.strings", "other-dir/outside.md",
                                 "external.md", "docs/Erste Schritte.md",
                                 "ignored/keep.md", "config.toml")
        self.assertEqual({entry["path"] for entry in result["files"]},
                         {"docs/de-AT.strings", "docs/Erste Schritte.md"})
        self.assertIn('1\t"save" = "Änderungen sichern";', result["files"][1]["numbered_text"])
        self.assertEqual(len(result["unresolved_selections"]), 4)
        self.assertEqual(before, inventory(self.root))
        self.assertFalse((self.root / ".git").exists())
        self.assertEqual(outside.read_text(encoding="utf-8"), "Outside content\n")

    def test_limits_root_and_literal_paths(self):
        self.put("AGENTS.md")
        self.put("nested/CLAUDE.md")
        self.put("nested/[literal].md")
        self.put("nested/another.md")
        result = self.run_helper("--limit", "2")
        self.assertEqual(result["eligible"], 4)
        self.assertEqual(result["omitted_by_limit"], 2)
        self.assertEqual(result["instructions"], ["AGENTS.md", "nested/CLAUDE.md"])
        result = self.run_helper("--read", str((self.root / "nested/[literal].md").resolve()))
        self.assertEqual(result["files"][0]["path"], "nested/[literal].md")
        result = self.run_helper("--read", str(self.root / "nested/[literal].md"))
        self.assertEqual(result["files"][0]["path"], "nested/[literal].md")
        link = self.base / "folder link"
        link.symlink_to(self.root, target_is_directory=True)
        self.assertIn("symlink", self.run_helper(root=link / "nested", code=2))
        self.assertIn("outside", self.run_helper("--read", "../secret.md", code=2))
        self.assertIn("Git working tree", self.run_helper("--changes", code=2))

    def test_unusable_ignore_rules_prune_subtree(self):
        self.put("README.md")
        self.put("docs/.gitignore", "[[:upper:]].md\n")
        self.put("docs/secret-note.md")
        self.assertEqual(self.run_helper()["skipped_entries"],
                         {"unusable ignore rules (directory pruned)": 1})

    def test_delivery_read_is_explicit(self):
        self.put("notice.md", "<!-- Generated by Billing Desk -->\n")
        self.put("ordinary.md")
        self.put("secret.pem")
        result = self.run_helper("--read", "notice.md")
        self.assertEqual(result["files"], [])
        result = self.run_helper("--read", "--delivery", "notice.md", "secret.pem")
        self.assertIn("Generated by Billing Desk", result["files"][0]["numbered_text"])
        self.assertEqual(result["unresolved_selections"]["secret.pem"], "possible secret path")

    def test_git_unchanged_inventory_and_patch_layers(self):
        self.root = fixture(self.base, "git")
        before = inventory(self.root)
        result = self.run_helper("--changes")
        self.assertEqual({entry["path"]: entry["layers"] for entry in result["files"]}, {
            "docs/connection.md": ["staged", "unstaged"],
            "docs/reminders.md": ["unstaged"],
            "sql/reminders.sql": ["untracked"],
        })
        self.assertEqual(result["skipped_entries"]["Git-ignored entries"], 1)
        self.assertEqual(result["skipped_entries"]["generated header"], 1)
        self.assertEqual(result["skipped_entries"]["symlink"], 1)
        result = self.run_helper("--changes", "--patch", "docs/connection.md", "docs/reminders.md",
                                 "sql/reminders.sql")
        changes = {entry["path"]: entry["patches"] for entry in result["files"]}
        self.assertIn("+Billing Desk offers", changes["docs/connection.md"]["staged"])
        self.assertIn("-Billing Desk offers", changes["docs/connection.md"]["unstaged"])
        self.assertIn("+## In summary", changes["docs/reminders.md"]["unstaged"])
        self.assertIn("+-- Filter overdue", changes["sql/reminders.sql"]["untracked"])
        self.assertEqual(inventory(self.root), before)

    def test_git_subdirectory_and_explicit_base(self):
        git(self.root, "init", "-qb", "trunk")
        self.put("a/outside.md")
        self.put("b/[literal].md", "before\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "original")
        self.put("a/outside.md", "changed outside\n")
        self.put("b/[literal].md", "changed inside\n")
        git(self.root, "commit", "-qam", "change")
        result = self.run_helper("--base", "HEAD~1", "--patch", "[literal].md",
                                 root=self.root / "b")
        self.assertEqual([entry["path"] for entry in result["files"]], ["[literal].md"])
        self.assertIn("+changed inside", result["files"][0]["patches"]["committed"])
        self.assertIn("rev-parse", self.run_helper("--base=--nonsense", code=2))

    def test_git_unborn_and_staged_deletion(self):
        git(self.root, "init", "-qb", "trunk")
        self.put("first.md", "First line.\n")
        git(self.root, "add", "first.md")
        result = self.run_helper("--changes", "--patch", "first.md")
        self.assertIn("+First line.", result["files"][0]["patches"]["staged"])
        git(self.root, "commit", "-qm", "first")
        git(self.root, "rm", "-q", "first.md")
        result = self.run_helper("--changes", "--patch", "first.md")
        self.assertFalse(result["files"][0]["present"])
        self.assertIn("-First line.", result["files"][0]["patches"]["staged"])

    def test_git_keeps_git_excludes_and_never_runs_clean_filter(self):
        git(self.root, "init", "-qb", "trunk")
        self.put(".gitattributes", "*.md filter=probe\n")
        self.put("attached.md")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "initial")
        self.put(".git/info/exclude", "local.md\n")
        self.put("local.md")
        self.put("attached.md", "A much longer and newer text file.\n")
        git(self.root, "config", "filter.probe.clean", "touch .filter-executed && cat")
        git(self.root, "config", "filter.probe.required", "true")
        before = inventory(self.root)
        result = self.run_helper("--changes")
        self.assertEqual([entry["path"] for entry in result["files"]], ["attached.md"])
        self.assertEqual(inventory(self.root), before)
        self.assertFalse((self.root / ".filter-executed").exists())

    def test_technical_fixture_scope_and_behaviour(self):
        self.root = fixture(self.base, "technical")
        before = inventory(self.root)
        requested = ("README.md", "README.de.md", "de-AT.lproj/Localizable.strings",
                     "billing/__init__.py", "billing/cache_keys.py", "sql/customer_billing.sql",
                     "migrations/001_create_customers.sql", "migrations/002_add_suspensions.sql")
        result = self.run_helper("--read", *requested)
        records = {entry["path"]: entry["numbered_text"] for entry in result["files"]}
        self.assertEqual(set(records), set(requested))
        self.assertEqual(records["billing/__init__.py"], "")
        self.assertIn("%@", records["de-AT.lproj/Localizable.strings"])
        self.assertIn(":next_billing_month_start", records["sql/customer_billing.sql"])
        result = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"],
                                cwd=self.root, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(inventory(self.root), before)

    def test_install_is_idempotent_and_preserves_other_skills(self):
        fake_home = self.base / "test home"
        env = {**os.environ, "HOME": str(fake_home)}
        directory = fake_home / ".agents/skills"
        other = directory / "unrelated"
        other.mkdir(parents=True)
        (other / "SKILL.md").write_text("Unrelated\n", encoding="utf-8")
        command = [sys.executable, "-I", "-B", str(ROOT / "install.py")]
        for scope, target_dir in (("codex", directory), ("claude", fake_home / ".claude/skills")):
            for _ in range(2):
                subprocess.run([*command, scope], env=env, check=True, capture_output=True)
            target = target_dir / "project-style-review"
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.resolve(), ROOT / "project-style-review")
        target = directory / "project-style-review"
        target.unlink()
        target.mkdir()
        (target / "SKILL.md").write_text("Existing same-name skill\n", encoding="utf-8")
        before = inventory(directory)
        result = subprocess.run([*command, "codex"], env=env, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(inventory(directory), before)


if __name__ == "__main__":
    unittest.main()
