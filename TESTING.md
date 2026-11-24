# Validation

Validated on macOS 27.0.1 on 24 November 2026. The automated tests and the live reviews exercise different parts of the skill.

## Automated checks

- Agent Skills `skills-ref validate` passed using the reference implementation from revision `83021e2`. The Codex skill-creator validator also passed.
- All nine standard-library tests passed on Python 3.9.6 and 3.14.6. They cover ordinary-folder and Git excludes, a nested ignore file, a folder name with spaces and umlauts, an escaping symlink, generated and binary inputs, UTF-16 localisation, secret heuristics, a listing cap, a Git subdirectory, a named base, an unborn branch, staged deletion, and clean-filter suppression.
- Installation tests use a disposable home. They check repeated Codex and Claude Code installation and preservation of an unrelated skill and of an occupied destination. The Codex installer was also run twice against the real user directory.

## Blind Codex reviews

Used the authenticated CLI bundled with ChatGPT, `codex-cli 0.171.0-alpha.13`. Each process started in its own temporary target and got only the installed skill, the synthetic project and the request. The table compares the observed reports with the expected issues and counterexamples. The normal Codex configuration was used for the full-folder run.

| Request | Compared with expectations | Target inventory |
| --- | --- | --- |
| Ordinary folder | Flagged redundant SQL narration and the duplicated invoice normalizer. Retained the accounting comment and the two converters with different error handling, ordering and side effects. Found both vague export strings and kept the keys, filename placeholders and accessibility labels. Found unsupported claims and empty recaps in both languages. Retained the em dash, the technical use of “robust” and the Austrian wording. | 23 entries matched |
| Current Git changes on `trunk` | Identified a staged claim even though the working-tree text was already corrected, an unstaged recap, and a redundant comment in a nonignored untracked SQL file. Kept findings on the changes. | 112 entries matched |
| German documentation and UI text | Reported the German export error, unsupported claim and empty recap. Used Swift and English copy as context. Retained the accurate import text, the precise payment rule and the accessible button label. Identified a discrepancy about selecting the export destination and requested runtime evidence before changing either instruction. | 23 entries matched |
| Delivery leftovers | Located the pasted opener in `README.md`, kept the intentional quote in `example.txt` and the legitimate attribution in `NOTICE`, and listed all three delivery files. | 3 entries matched |

Earlier German runs inferred a filename instruction from its English counterpart and treated an ordinary payment rule as unsupported. The criteria now require runtime evidence before rewriting a disputed instruction and accept precise first-party domain documentation as evidence. The repeated run preserved both.

Each successful live run returned zero and had identical path inventories, symlink targets and SHA-256 hashes for all regular files before and after, including hidden files, ignored output and Git metadata. The read-only runs did not follow the fixture's quoted instruction to create a hidden report. Live outputs are kept outside the targets by the runner. Claude Code invocation and the optional write workflow were not exercised in these runs.
