---
name: organize
description: Audit project structure, align layout to conventions, and archive superseded content. Use for cleaning up folders, standardizing layout, or preparing a workspace before committing.
---

# Organize Skill

Audits any project directory, aligns it to a consistent structural convention, and archives superseded content under `_archive/`. Detects drift between docs and disk, flags stale or orphan content, and proposes a reversible cleanup. Hands off to `/commit` or `/ship`.

## Core Principles

- **Plan before act.** Write every proposed operation to a plan file and confirm before moving anything.
- **Reversible moves only.** Archive superseded content; never delete without explicit approval.
- **Match disk to docs.** Where a project-level docs file exists, treat it as the source of truth and reconcile drift.
- **Sync-safe moves.** Use `shutil.copytree` + retry for folder moves on cloud-synced paths (Dropbox, OneDrive, iCloud); never `os.rename` / `mv`.
- **Conservative by default.** Naming, docs, and archiving only. Do not restructure pipelines, scripts, or generated artifacts without explicit scope.
- **Hand off, don't chain.** End with a clean working tree; `/commit` or `/ship` handles commit and push.

## Target Structure

These are the structural conventions the skill enforces. They are project-agnostic and can be adapted to any type of work (research, content production, software, data pipelines).

### Folder layout

Each project root has a flat top level with these roles, as needed:

| Folder | Purpose |
|---|---|
| `data/` or `source/` | Canonical raw inputs (often gitignored when large) |
| `scripts/` | Code or automation |
| `output/` or `results/` | Generated artifacts (often gitignored when large) |
| `refs/` | Reference material, source documents, citations |
| `assets/` | Media, images, logos |
| `docs/` or `manuscript/` | Written deliverables, reports |
| `_archive/` | Superseded content at any level (see below) |

Not every project needs every folder. Create folders only when at least two items belong there.

### Naming rules

| Element | Convention | Examples |
|---|---|---|
| Folder names (asset / content subfolders) | lowercase, hyphens for word-breaks | `refs/`, `video-captions/`, `topic-models/` |
| Folder names (nested by identifier) | lowercase, underscores when grouping by id | `player_<handle>/`, `study_01/` |
| Top-level documentation markdown | `UPPER_SNAKE_CASE.md` | `README.md`, `CHANGELOG.md`, `CLAUDE.md`, `VIDEO_SCRIPT.md` |
| Other markdown under folders | kebab-case or lowercase | `outline.md`, `design-notes.md` |
| Scripts | snake_case | `run_pipeline.py`, `generate_report.py` |
| Generated data files | stage/prefix + identifier + optional date | `summary_2026-04-14.parquet`, `batch_001.jsonl` |
| Date tokens in filenames | ISO `YYYY-MM-DD` or compact `YYYYMMDD` | `snapshot_2026-03-09.xlsx` |

Root-level folders for distinct projects or subprojects: lowercase kebab-case (`video-one/`, `data-pipeline/`).

### The `_archive/` convention

When a folder produces a superseded version of something (regenerated images, old pipeline output, abandoned drafts), move the old content into a sibling `_archive/` folder **at the same level it was produced**. Do not scatter `*_old`, `*_backup`, `*_v1` folders around the tree.

- Preserves history without polluting the active workspace
- Date-stamp inside `_archive/` when multiple generations accumulate: `_archive/2026-04-14/`, `_archive/v1/`
- Archived content stays gitignored only if the originals were; otherwise it remains tracked for historical diffing

### Docs-as-anchor

One project-level documentation file (conventionally `CLAUDE.md` at the repo root) serves as the single source of truth:

- Contains a structure diagram listing every non-ignored top-level folder and the purpose of each
- Documents naming conventions, pipeline order, and any project-specific identifiers
- Is updated whenever folders are added, renamed, or archived

If no such file exists, the skill proposes creating a minimal one.

### `.gitignore` baseline

Every project should ignore at least these categories:

```
# Secrets
.env
.env.local
*.pem
credentials*.json
token*.json

# Large media (project-specific — adjust)
*.mp3
*.mp4
*.mov

# OS / editor noise
.DS_Store
Thumbs.db
*.swp

# Coding-agent harness state (per-machine)
.claude/settings.local.json
**/.claude/settings.local.json
```

Specific plugin- or tool-managed directories that live in the project root (non-standard `.<tool>/` folders with per-user config) should also be ignored if the tool treats them as per-user. The skill identifies these by the presence of `EXTEND.md`, `settings.local.*`, or similar per-user marker files.

## Workflow

### Step 1: Audit disk vs. docs

Resolve the repo root:

```
git rev-parse --show-toplevel
```

If a path argument is provided, scope to that subtree; otherwise scan the whole repo. Enumerate every folder and file under root, skipping `.git/`, gitignored paths, and any folder already named `_archive`.

If a project-level docs file exists (`CLAUDE.md`, `README.md`), parse any structure diagram it contains and compare against actual disk state.

### Step 2: Detect anti-patterns

Run all four detectors and collect findings:

#### A. Case drift
Compare folder names in the docs structure diagram to disk. On case-insensitive filesystems (Windows, macOS default), disk wins silently. Flag each mismatch.

Default resolution: keep lowercase on disk (Target Structure convention) and update the docs. Only rename folders on disk if the user explicitly asks.

#### B. Superseded generations next to current
Flag any of these living outside an `_archive/` folder:

- Folders named `v1/`, `v2/`, ..., `old/`, `backup/`, `bak/`, `deprecated/`, `legacy/`
- Siblings with suffix patterns: `<name>_v1/`, `<name>_old/`, `<name>_backup/`, `<name>.bak/`
- Dated folders sitting next to current content (e.g., `2024-03-09/`, `MAR09/`) with no `_archive/` parent

Verify each candidate by diffing contents against the current canonical folder. If the candidate genuinely supersedes current content, propose moving it under a sibling `_archive/`. Watch for misnamed folders (e.g., a folder named `prompts-v1/` whose content actually matches current PNGs in the parent — propose rename to `prompts/`, not archive).

#### C. Orphan files
A file is an orphan if no reference to it appears in:

- The project-level docs file (if any)
- Any `README.md` in the repo
- Any script in the repo (grep for filename and basename across `*.py`, `*.ts`, `*.r`, `*.R`, `*.sh`, `*.js`)
- Any other markdown under the repo (`git ls-files '*.md'`)

Common orphans: ad-hoc PDFs, one-off datasets, test images, manual downloads, screenshots. Propose a destination (`refs/`, `assets/`, `data/`) based on file type, or ask the user for intent. Never delete an orphan without explicit confirmation.

#### D. Tracked per-machine or per-user state
Check `git ls-files` for patterns that should be local-only:

- `**/.env` (allow `.env.example` through)
- `**/.claude/settings.local.json`
- Any folder named like `.<tool>/` at the repo root whose contents look per-user (marker files such as `EXTEND.md`, `settings.local.*`, `preferences.json`)
- `**/.DS_Store`, `**/Thumbs.db`, `**/*.swp`

For any hits, propose `git rm --cached <path>` plus the matching `.gitignore` entry. The file stays on disk — only the index entry is removed.

### Step 3: Write plan file

Write all proposed operations to `~/.claude/plans/organize-<repo>-<YYYYMMDD>.md` with this structure:

- **Context** — what triggered this pass, what the repo is, one-sentence goal
- **Findings** — grouped by the four detectors, each with file paths
- **Operations** — numbered list of moves, renames, `git rm --cached` calls, and docs edits
- **Out of scope** — what was flagged but deliberately not touched, with a reason
- **Verification** — git status walk, tree walk, cross-check
- **Rollback** — reverse-move instructions; confirm no destructive ops

### Step 4: Clarify ambiguous calls

Use `AskUserQuestion` for decisions that cannot be inferred:

- Case convention when docs and disk disagree: keep disk + update docs (default), or rename on disk
- Archive vs. delete for superseded content: archive (default), delete only with explicit confirmation
- Destination for orphan files: propose 2-3 existing folders (`refs/`, `assets/`, `data/`); suggest creating a new one only if none fit and user confirms
- Scope: conservative (naming + docs + `_archive/`) vs. expanded (include pipeline or script reorganization)

### Step 5: Apply approved operations

Use a single Python block for all moves, with retries for cloud-sync locks:

```python
import shutil, time
from pathlib import Path

def safe_move(src: Path, dst: Path, retries: int = 5, delay: float = 1.0):
    if not src.exists():
        return
    if dst.exists():
        raise FileExistsError(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(retries):
        try:
            shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)
            break
        except (PermissionError, OSError):
            time.sleep(delay)
    else:
        raise
    for _ in range(retries):
        try:
            shutil.rmtree(src) if src.is_dir() else src.unlink()
            break
        except (PermissionError, OSError):
            time.sleep(delay)
    else:
        raise
```

Rules:

- Never `os.rename` / `mv` a folder in a cloud-synced path
- Let git detect renames automatically after the move completes; do not `git mv`
- For tracked harness/plugin state, run `git rm --cached <path>` (file stays on disk, just untracked)

### Step 6: Refresh docs

After operations succeed:

- Update the project-level docs file's structure diagram to match final disk state
- Append convention notes if missing: `_archive/` placement rule, subfolder casing rule, gitignored-local-state list
- Update any session-persistent memory files if their path references changed

### Step 7: Verify

Run, in order:

```
git status --short
git ls-files --others --ignored --exclude-standard
```

Walk the final tree and confirm:

- Every folder named in the docs structure diagram exists on disk
- Every top-level folder on disk is named in the docs (except `.git/` and gitignored paths)
- Paths newly gitignored by Detector D no longer appear in `git ls-files`

### Step 8: Hand off

Report a concise structural summary:

- Folders archived / renamed / moved (counts and paths)
- Files untracked via `git rm --cached`
- Docs edited
- Anything out-of-scope flagged for a follow-up pass

Tell the user: run `/commit` for a single conventional-commits commit (`chore: standardize <repo> structure`), or `/ship` to also update `CHANGELOG.md` and push.

## Scope

**Include**

- Subfolder casing alignment (docs and disk)
- Archiving superseded generations under `_archive/`
- Moving orphan files to `refs/` / `assets/` / `data/` (with user confirmation on destination)
- Untracking per-machine or per-user state; extending `.gitignore`
- Refreshing the project-level docs file (structure diagram and conventions)
- Refreshing session-persistent memory path references

**Exclude**

- Splitting or merging pipeline, data, or script folders
- Consolidating parallel generation outputs (e.g., two folders holding the same artifacts)
- Deleting files (archive-only unless user explicitly confirms deletion)
- Running `/commit` or `/ship` (explicit hand-off)
- Renaming folders across casing conventions on disk (only on explicit request)
- Reorganizing anything inside `.git/` or gitignored paths

## Checklist

- [ ] Audit walked disk and parsed the project-level docs structure diagram
- [ ] All four detectors ran (case drift, superseded, orphans, tracked local state)
- [ ] Plan file written to `~/.claude/plans/organize-<repo>-<date>.md`
- [ ] Ambiguous calls resolved via `AskUserQuestion`, not assumed
- [ ] Moves used sync-safe `copytree` + retry pattern, not `rename` / `mv`
- [ ] Project-level docs file reflects final disk state
- [ ] `.gitignore` covers any per-machine or per-user state flagged by Detector D
- [ ] Hand-off message tells the user to run `/commit` or `/ship`
