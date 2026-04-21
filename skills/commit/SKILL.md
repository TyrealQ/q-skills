---
name: commit
description: "Stage and commit uncommitted changes with conventional commit messages, grouping related changes by topic. Use for git commits, saving changes, staged files, commit messages, or grouping commits by topic."
---

# Git Commit Skill

Stages and commits uncommitted changes with conventional commit messages. Groups files by topic when multiple unrelated changes are pending, runs cascade and CLAUDE.md freshness checks, and sweeps temp files after each commit. Does not push — hand off to `/ship` for that.

## Workflow

### Step 1: Review changes

Run both commands to get the full picture:

```
git status --short
git diff --cached --name-status
```

Use the union of both outputs. **If both return empty**, report "nothing to commit" and stop.

### Step 2: Analyze changes and verify consistency

#### Classify file paths

| Path pattern | Type |
|---|---|
| `posts/`, `articles/`, `content/` | content/writing |
| `.claude/skills/` | skill config |
| `src/`, `*.go`, `*.py`, `*.ts`, `*.R`, `*.r` | code/scripts |
| `*.md` | documentation |
| `*.json`, `*.yaml`, `*.toml`, `*.csv` | config/data |

#### Cascade check (skip if no scripts or data files changed)

If any modified files are scripts or data files:

- **Identify downstream files**: Find all markdown reports, appendices, and documentation that reference outputs or data from the modified files — search for filename references, table headers, variable names, and output patterns
- **Verify consistency**: Check that numbers, table data, file paths, and cross-references in downstream files match the current state of the modified scripts and their outputs
- **Fix discrepancies**: Update any stale numbers, outdated references, or mismatched data in downstream files. Include these fixes in the commit

#### CLAUDE.md freshness (always run)

If the working directory has a `CLAUDE.md`, read it and compare against the current project state — not just the changes being committed, but also decisions made during the session, new or renamed files on disk, and structural changes. Update CLAUDE.md before proceeding if any section reflects outdated state.

### Step 3: Decide commit strategy

- **Single topic**: one commit for all files
- **Multiple topics**: group by directory/topic, one commit per group

Grouping priority:
1. Content (one commit per article/document unit)
2. Skills (one commit per skill)
3. Code changes (group by module)
4. Config files (group together)

### Step 4: Generate commit message

Follow conventional commits format from `rules/git-workflow.md`:
```
<type>: <description>
```
Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`

Examples:
- `docs: add exploratory analysis notebook`
- `feat: add batch processing to pipeline`
- `fix: correct citation formatting in report`
- `chore: update project config`

Keep descriptions concise (under 70 chars).

### Step 5: Stage and commit

```
git add <file1> <file2> ...
git commit -m "<message>"
```

Rules:
- Specify files explicitly — never use `git add .` or `git add -A`
- Exclude temp files (`*.bak-*`, `.DS_Store`, `node_modules/`)

### Step 6: Cleanup temp files

After the commit succeeds, remove these patterns from the working tree (skip `.git/`):

- Files: `*.bak-*`, `*.pyc`, `*.pyo`, `*.swp`, `*.swo`, `*~`, `.DS_Store`, `Thumbs.db`
- Directories: `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`

List matches first, then delete. If nothing matches, note "no temp files to clean" and proceed.

```
find . -not -path '*/.git/*' -type f \( -name '*.bak-*' -o -name '*.pyc' -o -name '*.pyo' -o -name '*.swp' -o -name '*.swo' -o -name '*~' -o -name '.DS_Store' -o -name 'Thumbs.db' \) -print -exec rm -f {} +
find . -not -path '*/.git/*' -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.mypy_cache' -o -name '.ruff_cache' \) -print -exec rm -rf {} +
```

### Step 7: Confirm

Run: `git log --oneline -3`

## Checklist

- [ ] All modified files reviewed and classified
- [ ] Cascade check completed for script/data changes
- [ ] CLAUDE.md updated if project structure or dependencies changed
- [ ] Commit message follows conventional commits format
- [ ] No temp files or sensitive files staged
- [ ] Commit completed successfully
- [ ] Temp files cleaned after commit
