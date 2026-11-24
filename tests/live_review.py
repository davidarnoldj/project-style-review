#!/usr/bin/env python3
"""Run a blind Codex review. Transcripts are written beside the isolated targets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
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
    subprocess.run(["git", "-C", str(root), "-c", "user.name=Fixture",
                    "-c", "user.email=fixture@example.invalid", *args],
                   check=True, stdout=subprocess.DEVNULL)


def fixture(base, mode):
    root = base / "Rechnung Österreich"
    shutil.copytree(FIXTURES / ("delivery" if mode == "delivery" else "billing"), root)
    if mode == "delivery":
        return root
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
    "folder": '$project-style-review Review the ordinary local folder ".".',
    "git": "$project-style-review Review the current Git changes.",
    "german": "$project-style-review Prüfe nur die deutschsprachige Dokumentation und die deutschen UI-Texte.",
    "delivery": "$project-style-review Check only README.md, NOTICE and example.txt for literal authoring leftovers.",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=PROMPTS)
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--user-config", action="store_true", help="use normal Codex settings")
    args = parser.parse_args()
    base = Path(tempfile.mkdtemp(prefix=f"project-style-review-{args.mode}-"))
    root = fixture(base, args.mode)
    before = inventory(root)
    print(f"Target: {root}\nLogs: {base}", flush=True)
    (base / "before.json").write_text(json.dumps(before, indent=2) + "\n", encoding="utf-8")
    config = ["--sandbox", "read-only", "--json", "--ephemeral", "--skip-git-repo-check"]
    if not args.user_config:
        config.append("--ignore-user-config")
    output = base / "report.md"
    with (base / "events.jsonl").open("w") as stdout, (base / "stderr.log").open("w") as stderr:
        try:
            code = subprocess.run([args.codex, "exec", *config, "-C", str(root),
                                   "-o", str(output), PROMPTS[args.mode]],
                                  stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                  timeout=300, cwd=root).returncode
        except subprocess.TimeoutExpired:
            code = 124
    after = inventory(root)
    (base / "after.json").write_text(json.dumps(after, indent=2) + "\n", encoding="utf-8")
    if before != after:
        print("Target changed:", [key for key in sorted(before.keys() | after.keys())
                                  if before.get(key) != after.get(key)])
    print(f"Codex exit: {code}. Target entries: {len(before)}. Inventory and hashes match: {before == after}")
    if output.exists():
        print(output.read_text(encoding="utf-8"))
    raise SystemExit(code or int(before != after))


if __name__ == "__main__":
    main()
