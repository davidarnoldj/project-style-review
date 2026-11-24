#!/usr/bin/env python3
"""Link the canonical skill into a coding client's user skill directory."""
import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("client", nargs="?", default="codex", choices=("codex", "claude"))
    args = parser.parse_args()
    directory = ".agents" if args.client == "codex" else ".claude"
    source = Path(__file__).resolve().parent / "project-style-review"
    destination = Path.home() / directory / "skills" / source.name
    if not (source / "SKILL.md").is_file():
        parser.exit(1, f"Canonical skill not found at {source}\n")
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            destination.symlink_to(source, target_is_directory=True)
        except FileExistsError:
            if not destination.is_symlink() or os.readlink(destination) != str(source):
                parser.exit(1, f"Existing skill left in place: {destination}\n")
    except OSError as error:
        parser.exit(1, f"Skill installation failed: {error}\n")
    print(f"{destination} -> {source}")


if __name__ == "__main__":
    main()
