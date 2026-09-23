# Conventions

This file describes the target state that detectors A to I check a project against.

## Naming

Every name is lowercase snake_case unless a row below says otherwise.

| Element | Convention | Examples |
|---|---|---|
| Folders | lowercase snake_case | `data/`, `topic_models/`, `video_captions/` |
| Markdown files | lowercase snake_case | `outline.md`, `design_notes.md`, `glossary.md` |
| Scripts | lowercase snake_case | `run_pipeline.py`, `build_report.R`, `fetch_records.sh` |
| Generated data files | stage name, then identifier, then an optional date, joined by underscores | `cleaning_batch_001.jsonl`, `models_batch_001_2026-04-14.parquet` |
| Dated items (correspondence, meeting notes, shared drafts, returned material) | `YYYY-MM-DD_slug` | `2026-09-23_budget_request.md`, `2026-08-14_draft_review.docx` |
| Date tokens | ISO `YYYY-MM-DD` only | `snapshot_2026-03-09.xlsx` |
| `README.md`, `CLAUDE.md`, `AGENTS.md`, `STYLE.md`, `CHANGELOG.md`, `LICENSE`, and other files that a tool reads by a fixed uppercase name | uppercase name, lowercase extension when there is one | `README.md`, `CLAUDE.md`, `AGENTS.md`, `STYLE.md`, `CHANGELOG.md`, `LICENSE` |
| Acronyms | write the acronym in capitals inside a snake_case name when the project's own docs write it in capitals; otherwise lowercase | `IRB_protocol/`, `NSF_budget.xlsx`, `2026-09-23_IRB_amendment.md` |

Names that break the convention, and the names they take:

| Found | Corrected |
|---|---|
| `Topic-Models/` | `topic_models/` |
| `DesignNotes.md` | `design_notes.md` |
| `Run Pipeline.py` | `run_pipeline.py` |
| `readme.md` | `README.md` |
| `Irb_protocol/` (the project's docs write IRB) | `IRB_protocol/` |
| `meeting_09-23-2026.md` | `2026-09-23_meeting.md` |
| `snapshot_20260309.xlsx` | `snapshot_2026-03-09.xlsx` |
| `review_09Mar2026.docx` | `2026-03-09_review.docx` |

Any other Markdown file is lowercase, including `notes.md` and `todo.md`.

The date leads the name for dated items and trails it for generated data files. When a name lacks the year or another part of the date, do not supply it; list the file for the user to date.

Collections of like items sit in one flat folder, with each item keyed by a unique identifier such as a record ID, a DOI, or a date. Do not nest a collection into subfolders by meaning (by theme, by status, by year) when an identifier already tells the items apart; a flat folder can be listed, sorted, and joined against a table without knowing the grouping scheme.

```
records/                     not    records/
|-- rec_0001/                       |-- by_theme/
|-- rec_0002/                       |   `-- pricing/rec_0002/
`-- rec_0003/                       `-- pending/rec_0003/
```

## Layout

The top level of a project holds the role folders below, the root documentation files, and configuration files, with no wrapper folder (such as `work/` or `project/`) around the role folders. Each folder below fills one role, and a project uses only the roles it needs.

| Folder | Role |
|---|---|
| `data/` or `source/` | Canonical raw inputs, often gitignored when large |
| `scripts/` or `analysis/` | Code and automation |
| `outputs/` | Generated files, often gitignored when large |
| `references/` | Reference material, source documents, citations |
| `assets/` | Media, images, logos |
| `docs/` or a deliverable folder such as `manuscript/` or `report/` | Written deliverables |
| `emails/` or `correspondence/` | Sent and received correspondence |

Create a folder only when at least two items belong in it. A single file stays in its parent until a second item of the same kind arrives. The role folders in the table above, and the same-layout rules for unit folders and new root folders, take precedence over this rule.

A repeated unit, such as a check, a figure, or a pipeline stage, gets one folder per unit. The rule is that siblings share one inside layout; the names below show a set of checks.

```
checks/
|-- README.md          # index: one row per unit
|-- row_counts/
|   |-- README.md      # the unit report
|   |-- scripts/
|   `-- evidence/
`-- date_ranges/
    |-- README.md
    |-- scripts/
    `-- evidence/
```

A unit whose files support a verdict (a check) keeps them in `evidence/`; a unit whose files are read by a later stage keeps them in `outputs/`. A reader who knows one unit folder can then find the same parts in every other one.

When a new root folder is added, its subfolders follow the split the project already uses. If the project divides its work into `data/`, `scripts/`, and `outputs/`, a new root folder for a second study holds the same three subfolders rather than a new scheme.

The subfolders of `outputs/` match the stages under `scripts/` one to one. A script in `scripts/cleaning/` writes to `outputs/cleaning/`, and a script in `scripts/models/` writes to `outputs/models/`.

```
scripts/                outputs/
|-- cleaning/           |-- cleaning/
|-- models/             |-- models/
`-- figures/            `-- figures/
```

## Reusable versus project code

Reusable tools live in a shared scripts repository, and the project calls them by path. A tool is reusable when it takes no project-specific paths, names, or prompts and at least two projects call it, or are expected to. Scripts, prompts, and outputs that belong to one project stay inside that project. The root map names the external paths; the guidance for a shared tool is kept in the shared repository beside the tool.

## Documentation model

The root `CLAUDE.md` is a short map: what lives where, the rules that hold across the whole project, and a pointer to each top-level folder's README. Each top-level folder and each unit folder has a `README.md` that gives the full account of that folder. Each topic has one owning file, and every other file that mentions the topic points to the owner.

Each document type has a fixed job and fixed parts, in this order:

| Type | Job | Fixed parts, in order |
|---|---|---|
| Root `CLAUDE.md` (the map) | What lives where, and the rules that hold everywhere | What the project is (one paragraph: purpose, deliverable, current stage); project-wide rules and known errors to avoid; layout, one entry per top-level folder with what it holds and a pointer to its README; external paths (one paragraph); documentation and git rules |
| Folder `README.md` (full account) | Everything about one folder | Opening paragraph (what the folder holds and what it is for); authority order, only if sources compete; file table (file, content), or one section per subfolder that has no README of its own; how to run or rebuild; inputs and outputs |
| Index `README.md` | List repeated units | A table only: one row per unit with its latest result, next action, and link |
| Unit `README.md` (a check, a figure, a stage) | Report one unit | Current result with the date obtained; findings; limits; the run line |
| Owner file (`STYLE.md`, `AGENTS.md`, decision record) | The one file that holds a topic | Whatever the topic needs; other files point to it |

A pointer names the owning file and says in one clause what that file covers, for example: "`STYLE.md` owns prose style: banned words, voice, fixed terms." A pointer never repeats the owner's content, so that a change to the rule is made in one file only.

A folder README that restates the owner copies the rule itself ("Use the active voice, avoid the word 'utilize', and write numbers under ten as words"). The same README written to the rule carries only the pointer above.

## Current-state rule

Docs describe the current state. When something changes, rewrite the passage rather than append to it. A passage breaks the rule when it describes an earlier state of the project: a date on a change, or a clause with "added," "changed from," "replaced," "previously," "now," "no longer," "used to," "until," or "instead of" that contrasts the current state with an earlier one. The same words used for present behavior ("the script replaces missing values") do not break it. Git holds the history. Exceptions: `CHANGELOG.md`, a dated decision record, a run log, and a date that states when a result was obtained.

A passage that breaks the rule reads: "The cleaning script, added in March, now writes to `outputs/cleaning/` instead of `data/clean/`." The same passage written to the rule reads: "The cleaning script writes to `outputs/cleaning/`."

## Superseded content

What happens to an old version depends on whether git tracks it.

- Tracked content: delete the old version and let git hold the history. Do not keep version archives, snapshot folders, or numbered recheck reports (`report_v2.md`, `recheck_3.md`) beside the current file.
- Untracked or gitignored content: move the old version into a sibling `_archive/` folder at the level where it was produced, for example `outputs/models/_archive/`. The first generation sits directly in `_archive/`. When a second arrives, each generation moves into a subfolder named for the date it was produced, such as `_archive/2026-04-14/`. Each generation keeps its own name inside the date folder, for example `_archive/2026-04-14/run_2026-04-14/`. Do not leave `*_old`, `*_backup`, or `*_v1` folders elsewhere in the tree.

A dated folder is superseded when a later sibling replaces it: the docs and scripts read only the later one. Dated siblings that are all read, such as a series of snapshots analyzed together, form a collection (see Naming) and stay in place.

| Found | Tracked by git | Action |
|---|---|---|
| `report_v1.md` beside `report.md` | yes | delete `report_v1.md` |
| `figures_old/` beside `figures/` | yes | delete `figures_old/` |
| `outputs/models/run_2026-04-14/` beside the current run | no (gitignored) | move to `outputs/models/_archive/run_2026-04-14/` |
| `data/raw_backup/` | no (gitignored) | move to `data/_archive/raw_backup/` |

## .gitignore categories

Every project's `.gitignore` contains the patterns listed below. Add further patterns for files of the same kinds that the project holds.

- Secrets: `.env`, `credentials*.json` (keep `.env.example` tracked)
- Large media: `*.mp4`, `*.mov`
- OS and editor files: `.DS_Store`, `*.swp`
- Per-machine agent settings: `**/.claude/settings.local.json`

A tool folder at the root (`.<tool>/`) in which every file is per-user is ignored as a whole. A tool folder that mixes shared and per-user files, such as `.claude/` with a shared `settings.json` and a per-user `settings.local.json`, ignores only the per-user files, which are marked by names such as `settings.local.*` or `preferences.json`.
