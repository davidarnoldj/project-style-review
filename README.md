# Project Style Review

A reusable Agent Skill for reviewing source code, comments, documentation and user-facing text against a project's own conventions. Findings explain what a maintainer could improve, where it matters and the smallest useful change. Reviews are read-only by default.

## Install on macOS

Clone the private repository into a dedicated checkout using an authenticated GitHub account with access.

```sh
gh repo clone davidarnoldj/project-style-review "$HOME/Projects/project-style-review"
cd "$HOME/Projects/project-style-review"
python3 -I -B install.py codex
```

The installer links the canonical [skill directory](project-style-review) into `~/.agents/skills/project-style-review`. Running it again with the same checkout is safe. A different existing entry at the destination is preserved and reported. Pull updates into the checkout when you want them. New reviews use the installed directory. If Codex does not show the new skill, restart the client. [Codex skill discovery documentation](https://developers.openai.com/codex/skills/)

For Claude Code, run `python3 -I -B install.py claude` from the same checkout. The link goes into `~/.claude/skills/project-style-review`. Invoke `/project-style-review` followed by your request. The same instructions and helper are used by both clients. [Claude Code skills documentation](https://code.claude.com/docs/en/skills)

## Invoke from the project you want to review

Start Codex in the desired folder. In the prompt, type `$` and select `project-style-review`, or use `/skills`. These prompts also work with `codex exec`.

```text
$project-style-review Review the ordinary local folder ".".
$project-style-review Review the current Git changes.
$project-style-review Prüfe nur die deutschsprachige Dokumentation und die deutschen UI-Texte.
```

For a noninteractive review of the current folder on either a Git or non-Git project, run:

```sh
codex exec --sandbox read-only --ephemeral --skip-git-repo-check -C . '$project-style-review Review the ordinary local folder ".".'
```

On macOS with a working ChatGPT app bundle, its CLI can also be used by replacing `codex` with `"/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"`.

Additional examples:

- `$project-style-review Review only scripts/import.py and docs/import.md. Report in Austrian Standard German.`
- `$project-style-review Review the Git diff from release/2.8 to HEAD, plus current working-tree changes, under Sources/.`
- `$project-style-review Check only README.md and docs/setup.md for literal authoring leftovers.`
- `$project-style-review Apply the two documentation fixes from your report and show the diff.` For a subsequent editing request, use a session with write access.

## Scope and limits

- **Code and project text.** The helper discovers Python, SQL, Swift, Markdown, common configuration such as TOML, YAML, JSON, INI and XML, and localisation text such as Apple `.strings`, `.stringsdict`, `.xcstrings` and PO files. It reads UTF-8 and BOM-marked UTF-16. The agent reads source and text in context. There is no language parser, compiler, automated rewrite or authorship detector.
- **Working trees and folders.** A review can cover a folder, a subdirectory or selected files. Git change review distinguishes staged, unstaged and nonignored untracked files. An optional named revision adds a direct comparison to HEAD. The helper applies Git's standard excludes in a worktree and local `.gitignore` and `.ignore` rules in ordinary folders. It skips symlinks, known credential locations, binaries, common output directories and recognised generated text. See [scope and coverage](project-style-review/references/scope.md) for ignore details, caps and encoding limits.
- **Reports.** Results go to chat or stdout. The report uses the user's language and defaults to Austrian Standard German when unspecified. Quotes and suggested wording stay in the language of the file. A project may need sampling, and coverage belongs in the report.
- **Local processing.** The optional helper uses Python 3.9+ standard library and local Git for worktrees. It neither executes project code nor downloads catalogues. It creates no project files. The coding client can still send prompts and selected file excerpts to its configured model provider and retain out-of-project session data according to its settings.

## Tests and research

```sh
python3 -B -m unittest discover -s tests -v
python3 -B tests/live_review.py folder --codex "$(command -v codex)"
```

The live runner uses isolated synthetic folders. It accepts `folder`, `git`, `german` or `delivery`. It prints the review and compares pre/post inventories, including hidden files, SHA-256 content hashes and symlink targets. Transcripts and inventories are stored beside the temporary targets. An authenticated Codex CLI is required for live runs. Use the runner’s `--user-config` option to include your normal Codex settings.

See [validation results](TESTING.md) and [upstream research and licenses](RESEARCH.md).
