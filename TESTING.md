# Validation

Validated on macOS 27.0.1 on 24 November 2026. Ran the Agent Skills `skills-ref` validator from revision `83021e2` and the Codex skill-creator validator. The full suite passed on Python 3.9.6 and 3.14.6 with 10 tests on each version. The suite covers Git change layers and comparison revisions, ordinary-folder exclusions, symlinks, secret and generated-file heuristics, UTF-16 localisation, repeat installation and the technical fixture's file inventory and behaviour.

## Live Codex checks

The checks used the authenticated CLI bundled with ChatGPT, `codex-cli 0.171.0-alpha.13`, from separate temporary projects. Read-only prompts contained the request and gave the reviewer no expected findings. The runner kept reports outside the targets.

| Request | Observed result | Target inventory |
| --- | --- | --- |
| Full review of an ordinary folder | Found the SQL narration and translated the separate billing rationale. Reviewed the existing Python, guides and UI scenarios. | 23 entries matched |
| Technical English and file layout | Quoted and translated the German canonical README and SQL rationale. Corrected grammar in `send_reminder` with three total attempts, an immediate stop on success and conditional `RuntimeError`. Found the two private cache-key modules and the two duplicate setup pages. Cited the operator docs and test for the missing cache compatibility rationale. | 38 entries matched |
| Current Git changes | Used separate patches and found the staged claim, unstaged recap and nonignored untracked SQL comment. | 112 entries matched |
| German documentation and UI | Produced a German report, proposed German UI wording with the existing `%@` placeholder and left the disputed picker instructions pending confirmation. | 23 entries matched |
| Literal delivery leftovers | Found the pasted opener and kept the intentional quotation and attribution. | 3 entries matched |

In the focused review, the translated README, German UI text, precise `next_pending_id` docstring, empty Python package marker and numbered migrations all remained eligible for inspection. The review identified the role of the package marker and the order dependency of the migrations. It kept the operator and contributor pages as distinct destinations while proposing one setup procedure. The reviewer cited the existing anchors and left external references as an evidence gap.

The inventory check compares names, SHA-256 hashes of regular files and symlink targets. It includes hidden and ignored entries and Git metadata. An early review omitted the reason to keep nearby small files, and an early Git run opened an excluded file. The repeated runs reported the relevant retained boundaries and used the scope helper for review evidence. The billing fixture now tests the inclusive month start and exclusive next-month start, which makes the SQL translation independently checkable.

## Explicit edit check

A separate fixture run authorised specific edits. Codex translated the canonical README, corrected the reminder docstring, moved the two private cache helpers into `billing/cache_keys.py`, and removed the duplicate setup page after updating its two inbound links to `docs/setup.md#prepare-the-database`. It showed a diff and ran all five fixture tests. The harness reran those tests and checked the exact changed and removed paths, preserved files, canonical anchor and links. The cache key kept its public import and exact UTF-8 digest format. The tests verified the retry limit, stop on success, conditional error, billing bounds and pending ID order. The German README, both locale files and their placeholders, and the package marker and migrations matched their original hashes.

## Review of this skill

Codex reviewed a disposable copy of the repository. The scope reference explains how to obtain evidence. The criteria reference explains how to evaluate it. The installer, review helper and live runner have distinct entry points and different effects. The review found two inaccurate link labels, which were corrected. The scope helper now explains why it drops inherited Git settings.

Claude Code installation passed in a disposable home. Live Claude Code invocation remains unverified.
