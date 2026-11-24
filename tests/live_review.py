#!/usr/bin/env python3
"""Exercise the installed Codex skill on disposable projects."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def inventory(root):
    entries = {}
    for directory, dirs, files in os.walk(root):
        for name in dirs + files:
            path = Path(directory) / name
            relative = str(path.relative_to(root))
            if path.is_symlink():
                entries[relative] = ("link", os.readlink(path))
            elif path.is_dir():
                entries[relative] = ("dir",)
            else:
                entries[relative] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
    return entries


def git(root, *args):
    subprocess.run(["git", "-c", "user.name=Fixture",
                    "-c", "user.email=fixture@example.invalid", *args],
                   cwd=root, check=True, stdout=subprocess.DEVNULL)


def fixture(base, mode):
    root = base / "Rechnung Österreich"
    shutil.copytree(FIXTURES / ("delivery" if mode == "delivery" else "billing"), root)
    if mode == "delivery":
        return root
    if mode in {"technical", "edit"}:
        shutil.copytree(FIXTURES / "technical", root, dirs_exist_ok=True)
    outside = base / "Outside.md"
    outside.write_text("Review scope trap.\n", encoding="utf-8")
    (root / ".gitignore").write_text("ignored local.md\n", encoding="utf-8")
    (root / "ignored local.md").write_text("# Ignored local copy\n", encoding="utf-8")
    (root / ".hidden-baseline").write_bytes(b"hidden inventory control\n")
    (root / "build").mkdir()
    (root / "build" / "app.md").write_text("# Build output\n", encoding="utf-8")
    (root / "outside-link.md").symlink_to(outside)
    (root / "Autogen.swift").write_text("// @generated\nlet x = 1\n", encoding="utf-8")
    if mode == "git":
        git(root, "init", "-q", "-b", "trunk")
        notes = root / "docs" / "reminders.md"
        notes.write_text("# Payment reminders\n\nThe query selects overdue invoices.\n", encoding="utf-8")
        git(root, "add", ".gitignore", "docs/reminders.md", "AGENTS.md",
            "README.md", "billing", "sql", "InvoiceExport.swift", "en.lproj", "de-AT.lproj")
        git(root, "commit", "-qm", "Initial billing fixture")
        staged = root / "docs" / "connection.md"
        staged.write_text("# Connection\n\nBilling Desk offers the world's most secure database connection.\n",
                          encoding="utf-8")
        git(root, "add", "docs/connection.md")
        staged.write_text("# Connection\n\nOpen the database connection settings before running the query.\n",
                          encoding="utf-8")
        with notes.open("a", encoding="utf-8") as stream:
            stream.write("\n## In summary\n\nThese instructions help you get more out of reminders.\n")
        (root / "sql" / "reminders.sql").write_text(
            "SELECT invoice_id FROM invoices\n-- Filter overdue invoices\nWHERE overdue = true;\n",
            encoding="utf-8",
        )
        git(root, "add", "docs/prompt-examples.md", "docs/import.de.md", "docs/Erste Schritte – Österreich.md")
        git(root, "commit", "-qm", "Add guides", "--",
            "docs/prompt-examples.md", "docs/import.de.md", "docs/Erste Schritte – Österreich.md")
    return root


PROMPTS = {
    "folder": "$project-style-review Review this ordinary folder. Give a complete read-only review.",
    "technical": ("$project-style-review Review the developer documentation and comments "
                  "for technical English, and look for unnecessary file fragmentation."),
    "edit": ("$project-style-review Apply these approved fixes only. Translate the developer prose "
             "in README.md to English and correct the docstring for send_reminder. "
             "Consolidate billing/_cache_prefix.py and billing/_cache_digest.py into "
             "billing/cache_keys.py and remove the old private files. "
             "Consolidate the duplicate docs/install.md into docs/setup.md and fix inbound links. "
             "Preserve the translated README, product strings, directives, and existing behaviour. "
             "Run python3 -B -m unittest discover -s tests -v and show the diff."),
    "git": "$project-style-review Review the current Git changes.",
    "german": "$project-style-review Prüfe nur die deutschsprachige Dokumentation und die deutschen UI-Texte.",
    "delivery": "$project-style-review Check only README.md, NOTICE and example.txt for literal authoring leftovers.",
}


def fixture_tests(root):
    subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
                   cwd=root, check=True, stderr=subprocess.STDOUT)


def without_reminder_docstring(path):
    module = ast.parse(path.read_text(encoding="utf-8"))
    function = next(node for node in module.body
                    if isinstance(node, ast.FunctionDef) and node.name == "send_reminder")
    docstring = ast.get_docstring(function)
    if docstring is None:
        raise ValueError("Expected a send_reminder docstring")
    function.body.pop(0)
    return ast.dump(module), docstring


def verify_edit(root, before, after, reminder_before):
    deleted = {"billing/_cache_prefix.py", "billing/_cache_digest.py", "docs/install.md"}
    modified = {"README.md", "docs/contributing.md", "billing/cache_keys.py", "billing/reminders.py"}
    changed = {path for path in before.keys() | after.keys() if before.get(path) != after.get(path)}
    if changed != deleted | modified or before.keys() - after.keys() != deleted:
        raise ValueError(f"Unexpected target changes: {sorted(changed)}")
    reminder_after, docstring = without_reminder_docstring(root / "billing/reminders.py")
    if reminder_before[0] != reminder_after or reminder_before[1] == docstring:
        raise ValueError("The reminder edit must change only the docstring")
    setup = root / "docs/setup.md"
    if setup.read_text(encoding="utf-8").count("## Prepare the database\n") != 1:
        raise ValueError("Expected one canonical setup anchor")
    for source, link in (("README.md", "docs/setup.md"), ("docs/contributing.md", "setup.md")):
        if f"]({link}#prepare-the-database)" not in (root / source).read_text(encoding="utf-8"):
            raise ValueError(f"Missing setup link in {source}")
    for path in root.rglob("*.md"):
        if "install.md#" in path.read_text(encoding="utf-8"):
            raise ValueError(f"Stale setup link in {path.relative_to(root)}")
    fixture_tests(root)
    print("Approved paths, setup links, protected files, and fixture behaviour verified.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=PROMPTS)
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--user-config", action="store_true", help="use normal Codex settings")
    args = parser.parse_args()
    base = Path(tempfile.mkdtemp(prefix=f"project-style-review-{args.mode}-"))
    root = fixture(base, args.mode)
    editing = args.mode == "edit"
    if editing:
        fixture_tests(root)
        reminder_before = without_reminder_docstring(root / "billing/reminders.py")
    before = inventory(root)
    print(f"Target: {root}\nLogs: {base}", flush=True)
    (base / "before.json").write_text(json.dumps(before, indent=2) + "\n", encoding="utf-8")
    sandbox = "workspace-write" if editing else "read-only"
    config = ["--sandbox", sandbox, "--json", "--ephemeral", "--skip-git-repo-check"]
    if not args.user_config:
        config.append("--ignore-user-config")
    output = base / "report.md"
    with (base / "events.jsonl").open("w") as stdout, (base / "stderr.log").open("w") as stderr:
        try:
            code = subprocess.run([args.codex, "exec", *config, "-C", ".",
                                   "-o", str(output), PROMPTS[args.mode]],
                                  stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                  timeout=300, cwd=root).returncode
        except subprocess.TimeoutExpired:
            code = 124
    after = inventory(root)
    (base / "after.json").write_text(json.dumps(after, indent=2) + "\n", encoding="utf-8")
    if before != after and not editing:
        print("Target changed:", [key for key in sorted(before.keys() | after.keys())
                                  if before.get(key) != after.get(key)])
    print(f"Codex exit: {code}. Original target entries: {len(before)}.")
    if not editing:
        print(f"Inventory and hashes match: {before == after}")
    if output.exists():
        print(output.read_text(encoding="utf-8"))
    if editing and code == 0:
        verify_edit(root, before, after, reminder_before)
    raise SystemExit(code or int(not editing and before != after))


if __name__ == "__main__":
    main()
