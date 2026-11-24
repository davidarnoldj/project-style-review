# Project Style Review

An Agent Skill for reviewing technical English, code structure, file layout and product text in context. It reports findings in chat by default and applies fixes only on request.

## Install

Clone the public repository and run the installer with Python 3.9 or later.

```sh
git clone https://github.com/davidarnoldj/project-style-review.git
cd project-style-review
python3 -I -B install.py codex
```

The installer links the canonical [skill directory](project-style-review/) into `~/.agents/skills/project-style-review`. It preserves an existing entry from a different checkout. Pull updates into your checkout to update the installed skill. Restart Codex if the skill is missing from the selector. [Codex skill discovery](https://developers.openai.com/codex/skills/)

For Claude Code, run `python3 -I -B install.py claude`. The installer links the skill into `~/.claude/skills/project-style-review`. Use `/project-style-review` followed by the request. [Claude Code skills](https://code.claude.com/docs/en/skills)

Other Agent Skills-compatible clients can install the complete `project-style-review/` directory in their documented skill location. Keep [`SKILL.md`](project-style-review/SKILL.md) and its bundled references and script together. [Agent Skills specification](https://agentskills.io/specification)

## Invoke from the project you want to review

In Codex, type `$` and select `project-style-review`, or use `/skills`. For a noninteractive, read-only review, run one of these commands from the target folder.

```sh
codex exec --sandbox read-only --ephemeral --skip-git-repo-check -C . \
  '$project-style-review Review this ordinary folder. Give a complete read-only review.'

codex exec --sandbox read-only --ephemeral --skip-git-repo-check -C . \
  '$project-style-review Review the developer documentation and comments for technical English, and look for unnecessary file fragmentation.'
```

On macOS, the ChatGPT app also ships a CLI at `/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex`. Quote that path when using it in place of `codex`.

Other requests

- `$project-style-review Review the current Git changes.`
- `$project-style-review Prüfe nur die deutschsprachige Dokumentation und die deutschen UI-Texte.`
- `$project-style-review Check only README.md and docs/setup.md for literal authoring leftovers.`
- `$project-style-review Apply the two approved fixes from the report and show the diff.` Use a session with write access for the approved change.

## What the review checks

- **Technical English.** Developer documentation and explanatory comments, including the canonical README and SQL comments, use precise English. An intentionally translated README, German product copy and exact literals keep their language. Review reports follow the user's language and default to Austrian Standard German. The review checks wording against local evidence and flags a missing explanation when a maintainer needs it to use or change the code safely.
- **File layout.** The review traces consumers, imports, anchors and build or discovery references before suggesting a move. Consolidation findings name the source files, a cohesive destination and affected references. Package markers, ordered migrations, supported public paths and separate documentation audiences can justify small files.
- **Project scope.** Review a folder, subdirectory, selected files or Git changes. Current Git changes include staged, unstaged and eligible untracked files. The helper discovers source such as Python, SQL and Swift, plus Markdown, configuration and localisation text. [Scope commands, exclusions and coverage limits](project-style-review/references/scope.md)
- **Local processing.** The optional helper uses the Python standard library and local Git for worktrees. It reads text and prints to standard output. The client can send prompts and file excerpts to its configured provider and retain session data according to its settings.

## Tests and research

```sh
python3 -B -m unittest discover -s tests -v
python3 -B tests/live_review.py technical --codex "$(command -v codex)"
python3 -B tests/live_review.py edit --codex "$(command -v codex)"
```

The live runner also accepts `folder`, `git`, `german` and `delivery`. It uses isolated synthetic projects and stores output beside the targets. Read-only runs compare complete inventories, including hidden paths, SHA-256 file hashes and symlink targets. The edit run checks approved paths, links, protected files and behaviour. Live runs require an authenticated Codex CLI. Pass `--user-config` to use your Codex settings.

See [validation results](TESTING.md) and [upstream sources and licences](RESEARCH.md).
