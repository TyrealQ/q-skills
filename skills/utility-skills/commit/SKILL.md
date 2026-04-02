---
name: commit
description: Stage and commit uncommitted changes with conventional commit messages. Use for committing changes or grouping commits by topic.
---

# Git Commit Skill

## Workflow

### Step 1: Review changes

Run both commands to get the full picture:

```
git status --short
git diff --cached --name-status
```

`git status --short` shows unstaged modifications and untracked files. `git diff --cached` catches files that are already staged but not yet committed. Use the union of both outputs.

**If both commands return empty**, report "nothing to commit" and stop.

Classify each change:
- `M` — modified, `??` — untracked, `D` — deleted, `R` — renamed, `A` — staged new file

### Step 2: Analyze changes and verify consistency

#### Classify file paths

| Path pattern | Type |
|---|---|
| `posts/`, `articles/`, `content/` | content/writing |
| `.claude/skills/` | skill config |
| `src/`, `*.go`, `*.py`, `*.ts`, `*.R`, `*.r` | code/scripts |
| `*.md` | documentation |
| `*.json`, `*.yaml`, `*.toml`, `*.csv` | config/data |

#### Cascade check

If any modified files are scripts or data files:

- **Identify downstream files**: Find all markdown reports, appendices, and documentation that reference outputs or data from the modified files — search for filename references, table headers, variable names, and output patterns
- **Verify consistency**: Check that numbers, table data, file paths, and cross-references in downstream files match the current state of the modified scripts and their outputs
- **Fix discrepancies**: Update any stale numbers, outdated references, or mismatched data in downstream files. Include these fixes in the commit

Skip if changes are limited to documentation, config, or content files with no upstream scripts or data dependencies.

#### CLAUDE.md freshness

If the working directory has a `CLAUDE.md`, scan it for file paths, folder names, project structure references, or temporal markers that may be stale given the changes being committed. Update CLAUDE.md before proceeding if any section reflects outdated state.

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

### Step 6: Confirm

Run: `git log --oneline -3`
