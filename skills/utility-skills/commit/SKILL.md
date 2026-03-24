---
name: commit
description: Stage and commit all uncommitted changes. Analyzes changed files, groups by topic, and generates descriptive conventional commit messages.
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

### Step 2: Analyze file paths to determine change type

| Path pattern | Type |
|---|---|
| `posts/`, `articles/`, `content/` | content/writing |
| `.claude/skills/` | skill config |
| `src/`, `*.go`, `*.py`, `*.ts` | code |
| `*.md` | documentation |
| `*.json`, `*.yaml`, `*.toml` | config |

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
- `docs: add Amodei NYT interview notes`
- `feat: add auto-commit stop hook`
- `fix: correct citation formatting in review`
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
