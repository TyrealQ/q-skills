---
name: organize
description: Audit project structure and documentation, align names and layout to conventions, remove or archive superseded content, and refine READMEs and CLAUDE.md. Use for cleaning up folders, standardizing layout, fixing stale docs, or streamlining documentation before a commit.
---

# Organize Skill

Audits a repository's layout and its project documentation against one set of conventions, using nine detectors, a plan file, and approval by group, and then hands off to `/commit` or `/ship`.

## References

- `references/conventions.md`: the target state the detectors check against. It covers naming, layout, reusable versus project code, the documentation model, the current-state rule, superseded content, and the `.gitignore` categories.

## Core Principles

- **Plan before acting.** Write every finding and every proposed operation to the plan file. Change no file until the user has approved the group that contains it; the one exception is a group labeled "fixes a written rule" (see Plan file), which is applied without asking.
- **Take each answer from its source.** Disk and `git ls-files` decide what exists; the project's docs decide what a thing is for and which project rules hold; `conventions.md` decides what a thing is called and how it is laid out wherever the project's docs state no rule. List every mismatch between these sources in the plan; the user decides which side changes, except in a group labeled "fixes a written rule". Where a rule written in the project's docs conflicts with `conventions.md`, follow the project rule and list the conflict as a note.
- **Ask for approval per group.** The user approves or rejects each group of operations in the plan. A clear violation of a rule already written in the project's own docs is fixed without asking. New files and consolidations of duplicated content always wait for approval.
- **List every move and deletion for approval.** Every move and every deletion appears in the plan as its own operation, and none is applied before the user approves it.
- **Edit project documentation only.** Among Markdown files, edit only those whose job is describing the repository. Deliverable prose is outside this skill; see Scope.
- **Move files safely on synced paths.** Copy the file or folder with retry, confirm the copy, then remove the source. Never rename a folder in place on a cloud-synced path such as Dropbox, OneDrive, or iCloud. Let git detect renames after the move; do not use `git mv`. A rename that changes only case uses the same method twice, through the temporary name that detector A gives.

## Workflow

| Step | Action | Reference |
|---|---|---|
| 1. Audit | Resolve the repository root with `git rev-parse --show-toplevel`, and limit the pass to a path argument when one is given. Record `git status --short` as the baseline for Step 7. List `git ls-files` and the gitignored paths (`git ls-files --others --ignored --exclude-standard --directory`), and walk the disk with those paths included so that detector B can see untracked generations. Read the root `CLAUDE.md` first, then every `README.md` in the tree and every owner file the docs point to. When the project's docs forbid sending a file's contents to this model (for example proprietary text), use only its name and path, and list any check that needs the contents (a diff, a count) under Open questions with the reason. | `conventions.md` § Documentation model |
| 2. Layout detectors | Run detectors A to D. | Detectors A to D; `conventions.md` § Naming, § Layout, § Superseded content, § .gitignore categories |
| 3. Documentation detectors | Run detectors E to I. | Detectors E to I; `conventions.md` § Documentation model, § Current-state rule, § Layout, § Naming |
| 4. Plan file | Write the plan to `~/.claude/plans/organize-<repo>-<YYYYMMDD>.md`, or to the path the user names, with the seven sections below. | Plan file, below |
| 5. Clarify | Ask with `AskUserQuestion` for each open question, such as the date of a name that lacks part of its date, the destination of an orphan file, or the owner of duplicated content. | Step 1; Detectors A, C, and G |
| 6. Apply | Apply the approved groups and the groups labeled "fixes a written rule", one group at a time in plan order, and stop at the first error. Within a group, make the moves and deletions before the documentation edits. | Core Principles; Plan file, below |
| 7. Verify | Run `git status --short` and walk the final tree. Confirm that every folder the root map names exists; every folder that `conventions.md` § Documentation model requires a README for has one, and the root map points to each top-level README; no approved finding is left open; the paths untracked under detector D are gone from `git ls-files`; and `git status --short` shows only the baseline and the changes the plan lists. Report any check that fails and leave it open. | Plan file, below (Verification) |
| 8. Hand off | Summarize what moved, what was deleted, what was untracked, which documentation files changed, and which findings were left out of scope. Name `/commit` for a single commit, or `/ship` to also update `CHANGELOG.md` and push. | Scope |

With the argument `audit`, or when the user asks for an audit only, stop after Step 4 and leave the open questions in the plan file unasked.

### Plan file

The plan file has seven sections, in this order:

1. **Context:** what started the pass, what the repository holds, and the path scope, if any.
2. **Findings:** grouped under the detector letters A to I, each with its path and the line or name at issue. A note is a finding listed for the user with no operation proposed. Notes stay in Findings and are not repeated under Out of scope.
3. **Operations:** numbered and grouped for approval. Each group lists its moves, deletions, `git rm --cached` calls, and documentation edits. A documentation edit shows the old and the new text. A new file, such as a missing README, is drafted in full. Each move or rename carries, in the same group, the edit to every project document that names the old path, and to any note in the project's memory folder (`~/.claude/projects/<project>/memory/*.md`) that names it.
4. **Out of scope:** each finding that will not be acted on, with the reason.
5. **Open questions:** each decision the audit cannot settle, with what the answer changes.
6. **Verification:** the checks from Step 7 that apply to this plan.
7. **Rollback:** how to reverse each group. A deleted tracked file or an edited document comes back with `git checkout HEAD -- <path>` before a commit; a path untracked with `git rm --cached` is tracked again with `git add <path>`; an archived folder moves back from `_archive/`.

An operations group reads like this:

```
### Group 2: superseded generations (detector B), needs approval

2.1  delete   report_v1.md                         tracked; report.md is current
2.2  move     outputs/models/run_2026-04-14/  ->  outputs/models/_archive/run_2026-04-14/
2.3  edit     outputs/README.md, line 12
     old: "Results are in run_2026-04-14/ and run_2026-05-02/."
     new: "Results are in run_2026-05-02/."
```

Label each group "needs approval" or "fixes a written rule". Use the second label only for a group of documentation edits with no move, deletion, new file, or consolidation, and that removes no information: no sentence, clause, finding, or recorded reason that the edit does not restate as a current fact; give the file and line where the project states the rule.

## Detectors

Run every detector over the whole tree, gitignored paths included, and record each finding in the plan file under its letter. The target state that each detector checks against is in `references/conventions.md`.

### A. Name drift

- **Looks for:** folder and file names that break `conventions.md` § Naming, and names that differ in case or spelling between the docs and disk.
- **Verify:** compare `git ls-files` and a walk of the disk against every name the root map and the READMEs give.
- **Resolve:** propose the rename and the matching docs edit as one operation. On a case-insensitive filesystem, rename in two steps through a temporary name (`Data/` to `data_tmp/` to `data/`) so that git and the sync client both record the change. When a name lacks part of its date, list it under Open questions instead of proposing a name.
- **Never flag:** names that `conventions.md` § Naming writes in capitals (files a tool reads by a fixed name, owner files, and acronyms the project's docs write in capitals), or a name that follows a naming rule written in the project's docs (list the conflict with `conventions.md` as a note).

### B. Superseded generations

- **Looks for:** folders named `v1/`, `v2/`, `old/`, `backup/`, `bak/`, `deprecated/`, or `legacy/`; siblings named `<name>_old`, `<name>_backup`, `<name>_v1`, or `<name>_v2`; dated siblings of current content; and a plan or design document whose work is complete, that describes no part of the current project, and that no current doc points to. Search everywhere outside `_archive/`, including inside gitignored paths such as `outputs/`.
- **Verify:** for dated siblings, apply the test in `conventions.md` § Superseded content: a sibling is superseded only when the docs and scripts read the later one alone. Diff each remaining candidate against the current folder beside it; when it holds the current content under a wrong name, propose a rename, not a removal.
- **Resolve:** delete the old version or move it to `_archive/`, following the tracking split in `conventions.md` § Superseded content.
- **Never flag:** anything already inside `_archive/`, or dated siblings that form a collection under `conventions.md` § Superseded content. List received material that the docs mark as superseded as a note.

### C. Orphan files

- **Looks for:** files outside gitignored paths whose name and path appear in no root map, README, script, or tracked Markdown file, and which do not sit inside a folder that the root map or a README describes; and files at the root that `conventions.md` § Layout does not allow, listed as a note when gitignored.
- **Verify:** search for the basename and the relative path across `git ls-files '*.md'` and the scripts (`*.py`, `*.R`, `*.sh`, `*.js`, `*.ts`). Then check the file's own folder; the file counts as covered when the root map or a README describes that folder. A covered file that nothing names, in a folder whose README has a file table that omits it, is a note.
- **Resolve:** propose a destination among the existing folders based on file type, or ask the user what the file is for. Never delete an orphan without approval.
- **Never flag:** files a tool reads by a fixed name and owner files, as `conventions.md` § Naming defines them, or deliverables.

### D. Tracked per-machine state

- **Looks for:** tracked paths that match a pattern in `conventions.md` § .gitignore categories, tracked per-user files inside a root `.<tool>/` folder as that section defines them, and a `.gitignore` missing one of that section's categories.
- **Verify:** confirm each path appears in `git ls-files`, and check whether `.gitignore` already has a line covering it.
- **Resolve:** propose `git rm --cached <path>`, plus the matching `.gitignore` line when none exists. The file stays on disk; only the index entry is removed.
- **Never flag:** `.env.example` or other templates meant to be shared.

### E. Stale facts

- **Looks for:** every path, filename, folder, command, and count named in project documentation.
- **Verify:** check each path and name against disk and `git ls-files`, and each count against the file or script that produces it. For a command, confirm the script exists and read its argument parser to confirm it accepts the flags named.
- **Resolve:** correct the doc to match disk. Never change a number without its source; when the source cannot be found, list the count under out of scope.
- **Never flag:** placeholder patterns such as `<name>_old` or `YYYY-MM-DD_slug`, external paths that the root map names as outside the repository, or a gitignored path that the docs describe as local to one machine or created at run time (an `.env` file, a virtual environment).

### F. History clauses

- **Looks for:** a date on a change, and the phrases listed in `conventions.md` § Current-state rule.
- **Verify:** for every date and every phrase found, read the whole sentence and flag it only when it contrasts the current state with an earlier one. The same words used for present behavior ("runs until the queue is empty") describe a current fact.
- **Resolve:** rewrite the sentence to state the current fact, as in the example in `conventions.md` § Current-state rule, or propose deleting the clause when the sentence holds no current fact.
- **Never flag:** the exceptions listed in `conventions.md` § Current-state rule, or the date in a `YYYY-MM-DD_slug` filename.

### G. Duplication

- **Looks for:** the same rule or fact stated in two or more files.
- **Verify:** compare the statements and confirm they give the same content rather than two related rules.
- **Resolve:** choose the owner: the file the project's docs name as the owner of the topic, or, when they name none, the file whose type in the table in `conventions.md` § Documentation model matches the topic; ask the user when more than one type fits. Keep the statement in the owner and replace every other statement with a pointer in the form that `conventions.md` § Documentation model gives.
- **Never flag:** a pointer that names its owner, or the one-line entry the root map gives a folder whose README holds the full account.

### H. Structure

- **Looks for:** a document missing the fixed parts of its type; a folder that `conventions.md` § Documentation model requires a README for, without one; a top-level folder README the root map does not point to, or a unit README the index does not link; an index written as prose; detail in the root map that belongs in a folder README; a unit README that reports a result without the date it was obtained; sibling unit folders with different inside layouts; a root folder whose subfolders do not mirror the project's existing split, or that holds different kinds of file (scripts, documents, media) directly with no subfolders; a section with fewer than two substantive sentences; a wrapper folder around the role folders; a folder holding one item (unit folders and the role folders in `conventions.md` § Layout excepted); a collection nested by meaning; `outputs/` subfolders that do not match the stages under `scripts/`.
- **Verify:** name each document's type from the table in `conventions.md` § Documentation model and check its fixed parts in order; compare folders against `conventions.md` § Layout and collections against § Naming.
- **Resolve:** propose the missing README, table, or date, drafted in full in the plan file; move root-map detail to the folder README that owns it and leave a pointer; propose the moves that give each folder the layout in § Layout, except that matching `outputs/` to `scripts/` goes under Out of scope when it would split or merge pipeline folders.
- **Never flag:** folders below a gitignored top-level folder or inside `_archive/`, item folders in a collection keyed by identifier, which the collection's own README covers, or an index README, a table, a code block, or a run line under the two-sentence rule.

### I. Prose

- **Looks for:** sentences that announce what follows, restatement of a point already made, padding, and figures of speech.
- **Verify:** check each candidate against the user's global writing rules (for example, files under `~/.claude/rules/` and `~/CLAUDE.md`) when they exist. The user's writing rules take precedence over the categories above; apply each rule only to the kinds of text it names.
- **Resolve:** propose the rewrite, with the old and new sentence side by side in the plan file.
- **Never flag:** quoted text, code, command lines, or a banned phrase quoted to state a rule.

### Scope of E to I

Detectors E, F, G, and I, and the document checks in H, read only Markdown whose job is describing the repository: the root map, folder READMEs, index and unit READMEs, owner files, and `AGENTS.md`. Anything the root map lists as a deliverable is outside their scope, and so are correspondence and reports written for readers. Detectors A to D still check the names and locations of those files.

## Scope

**Include**

- Layout and naming alignment between disk, docs, and `conventions.md`
- Removal of tracked superseded content and archiving of untracked superseded content
- Placement of orphan files
- Untracking per-machine state and extending `.gitignore`
- Refining and restructuring project documentation: creating missing READMEs, consolidating duplicated content into one owner, and moving detail from the root map into folder READMEs
- Updating path references in the project's memory notes (`~/.claude/projects/<project>/memory/`), listed in the plan with the move they follow

**Exclude**

- Deliverable prose: anything the root map lists as a deliverable, correspondence, and reports written for readers
- Splitting or merging pipeline, data, or script folders without an explicit request
- Running workbook, build, or pipeline scripts
- Anything inside `.git/`
- Changes inside gitignored paths other than moves into `_archive/`; a finding there from detectors A to D that needs another change, such as a rename, goes under Out of scope
- Committing or pushing
