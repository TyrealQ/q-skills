---
name: ship
description: Update docs (CHANGELOG, CLAUDE.md, READMEs), commit, and push. Use for shipping changes, deploying updates, or publishing to remote.
user_invocable: true
---

# Ship Skill

Automates the full cycle: update documentation -> stage -> commit -> push.

## Workflow

### Step 1: Review changes

Run all three commands to get the full picture:

```
git status --short
git diff --cached --name-status
git log @{upstream}..HEAD --oneline 2>/dev/null
```

Also identify the current branch and remote tracking status:

```
git branch --show-current
git rev-parse --abbrev-ref @{upstream} 2>/dev/null
```

Classify uncommitted changes from `git status`:

- `M` — modified, `??` — untracked, `D` — deleted, `R` — renamed

**If the working tree is clean but unpushed commits exist**, this is the **doc catch-up path**:

1. Run `git diff @{upstream}..HEAD --name-status` to list all files changed in unpushed commits
2. Analyze those files in Step 2 as if they were uncommitted changes
3. Proceed to Step 3 to check for missing documentation updates (CHANGELOG, README, CLAUDE.md, marketplace.json)
4. If documentation updates are needed, make them, commit, and push
5. If no documentation updates are needed, just push

**If both the working tree is clean AND no unpushed commits exist**, report "nothing to ship" and stop.

### Step 2: Analyze what changed

Read every modified/untracked file (or every file from unpushed commits in the doc catch-up path) to understand the nature of the changes.


| Path pattern                                 | Type                                           |
| -------------------------------------------- | ---------------------------------------------- |
| `posts/`, `articles/`, `content/`            | content/writing                                |
| `.claude/skills/`                            | skill config                                   |
| `src/`, `*.go`, `*.py`, `*.ts`, `*.R`, `*.r` | code/scripts                                   |
| `*.md`                                       | documentation                                  |
| `*.json`, `*.yaml`, `*.toml`, `*.csv`        | config/data                                    |
| `Resources/`, `resources/`                   | resource list                                  |
| `*.ipynb`                                    | notebook                                       |
| `.r2-upload-map/`                            | resource mapping (commit with related content) |


### Step 3: Update documentation

For each applicable documentation file, read the current contents first, then update.

#### CHANGELOG.md

- **When**: Always, if the file exists in the repo root
- **Format**: Follow [Keep a Changelog](https://keepachangelog.com/)
- Add a new `## [YYYY-MM-DD]` section (today's date) at the top of the log
- If today's date section already exists, append to it instead of creating a duplicate
- Subsections: `Added`, `Changed`, `Removed`, `Fixed` — only include relevant ones
- Each entry: one concise line describing the change from a user/reader perspective

#### CLAUDE.md (always run)

- **When**: Always. Read CLAUDE.md and compare against the current project state — not just the changes being shipped, but also decisions made during the session, new or renamed files on disk, and structural changes
- **Skip when**: Changes are limited to content additions (e.g., adding a link to Resources) AND no session-level decisions or structural changes occurred
- Update only the affected sections — do not rewrite the entire file
- Check for temporal markers (e.g., "Current position," dates, deadlines, status tables) that may be stale given the changes being shipped

#### README files (root or section-level)

- **When**: Changes affect content described by that README
- Examples: adding a notebook -> update the directory's README; renaming a section -> update root README
- **Skip when**: The change is self-evident from the file itself (e.g., adding a row to a resource table — the table IS the README)

#### Cascade check (skip if no scripts or data files changed)

If any modified files are scripts or data files:

- **Identify downstream files**: Find all markdown reports, appendices, and documentation that reference outputs or data from the modified files — search for filename references, table headers, variable names, and output patterns
- **Verify consistency**: Check that numbers, table data, file paths, and cross-references in downstream files match the current state of the modified scripts and their outputs
- **Fix discrepancies**: Update any stale numbers, outdated references, or mismatched data in downstream files. Include these fixes in the commit

#### Stale and missing reference check

After identifying all changed, added, and deleted files, **check documentation files for stale or missing references**:

- **Deleted files**: Search README.md, CLAUDE.md, and any doc that might reference them (folder trees, file lists, dependency mentions)
- **Renamed/moved files**: Update all path references
- **Removed features or dependencies**: Remove or update mentions in all docs
- **New directories or files**: If CLAUDE.md or README.md contain folder trees, check whether newly added directories or files should appear in those trees
- Run: `git diff --name-status` to get the full list of added (`A`/`??`), deleted (`D`), and renamed (`R`) files, then search docs for entries that need adding or removing

#### Other docs

- If any other documentation file is directly affected by the changes, update it too

### Step 4: Decide commit strategy

Examine the changes identified in Step 2 and choose a strategy:

- **Single topic** -> one commit for all files
- **Multiple topics** -> group by directory/topic, one commit per group

Grouping priority (highest first):

1. **Content directories** — one commit per article/document unit (e.g., each notebook directory, each post)
2. **Skill directories** — one commit per skill (`.claude/skills/<name>/`)
3. **Code changes** — merge all code changes into one commit
4. **Config / documentation files** — merge into one commit

Rules:

- `.r2-upload-map/*.json` files belong with their related content group, not standalone
- Documentation updates from Step 3 (CHANGELOG, README, etc.) go into the commit of the group that triggered them
- If all changes fall under one group, use a single commit regardless of file count

### Step 5: Generate commit messages

Generate one message per commit group from Step 4.

Follow conventional commits:

```
<type>: <description>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`

Rules:

- Under 70 characters
- Describe the user-facing change, not the documentation update
- If the only changes are documentation, use `docs:` type
- If code + docs changed together, use the type that matches the code change

Examples by group type:

- Content: `docs: add exploratory analysis notebook`
- Skills: `chore: update commit skill workflow`
- Code: `feat: add batch processing to pipeline`
- Config: `chore: update project config`

### Step 6: Stage and commit

For each commit group (from Step 4), in grouping-priority order:

```
git add <group-file1> <group-file2> ...
git commit -m "<group-message>"
```

Repeat for each group until all changes are committed.

Rules:

- Stage files explicitly — never use `git add .` or `git add -A`
- Include the documentation files updated in Step 3 with the commit group that triggered them
- Exclude temp files (`*.bak-*`, `.DS_Store`, `node_modules/`, `.claude/`)
- `.r2-upload-map/*.json` files go with their related content commit, not standalone

### Step 7: Push

```
git push
```

If no upstream is set:

```
git push -u origin <current-branch>
```

### Step 8: Cleanup temp files

After the push succeeds, remove these patterns from the working tree (skip `.git/`):

- Files: `*.bak-*`, `*.pyc`, `*.pyo`, `*.swp`, `*.swo`, `*~`, `.DS_Store`, `Thumbs.db`
- Directories: `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`

List matches first, then delete. If nothing matches, note "no temp files to clean" and proceed.

```
find . -not -path '*/.git/*' -type f \( -name '*.bak-*' -o -name '*.pyc' -o -name '*.pyo' -o -name '*.swp' -o -name '*.swo' -o -name '*~' -o -name '.DS_Store' -o -name 'Thumbs.db' \) -print -exec rm -f {} +
find . -not -path '*/.git/*' -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.mypy_cache' -o -name '.ruff_cache' \) -print -exec rm -rf {} +
```

### Step 9: Confirm

Run: `git log --oneline -3`

Display the commit hash and message to confirm success.

## Verification Checklist

- [ ] All modified files reviewed and classified
- [ ] Cascade check completed for script/data changes
- [ ] CHANGELOG.md updated with today's date section
- [ ] CLAUDE.md updated if project structure or dependencies changed
- [ ] README files updated if content they describe changed
- [ ] Stale and missing references resolved (deleted files, renamed paths)
- [ ] Commit messages follow conventional commits format
- [ ] No temp files or sensitive files staged
- [ ] Push completed successfully
- [ ] Temp files cleaned after push
