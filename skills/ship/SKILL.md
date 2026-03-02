---
name: ship
description: Update relevant documentation, commit all changes, and push to remote. Handles CHANGELOG.md, CLAUDE.md, READMEs, and any other docs affected by the current changes.
user_invocable: true
---

# Ship Skill

Automates the full cycle: update documentation -> stage -> commit -> push.

## Workflow

### Step 1: Review changes

Run: `git status --short`

Classify each change:
- `M` — modified, `??` — untracked, `D` — deleted, `R` — renamed

Identify the current branch and remote tracking status:
```
git branch --show-current
git rev-parse --abbrev-ref @{upstream} 2>/dev/null
```

### Step 2: Analyze what changed

Read every modified/untracked file to understand the nature of the changes.

| Path pattern | Type |
|---|---|
| `posts/`, `articles/`, `content/` | content/writing |
| `.claude/skills/` | skill config |
| `src/`, `*.go`, `*.py`, `*.ts` | code |
| `*.md` | documentation |
| `*.json`, `*.yaml`, `*.toml` | config |
| `Resources/`, `resources/` | resource list |
| `*.ipynb` | notebook |
| `.r2-upload-map/` | resource mapping (commit with related content) |

### Step 3: Update documentation

For each applicable documentation file, read the current contents first, then update.

#### CHANGELOG.md
- **When**: Always, if the file exists in the repo root
- **Format**: Follow [Keep a Changelog](https://keepachangelog.com/)
- Add a new `## [YYYY-MM-DD]` section (today's date) at the top of the log
- If today's date section already exists, append to it instead of creating a duplicate
- Subsections: `Added`, `Changed`, `Removed`, `Fixed` — only include relevant ones
- Each entry: one concise line describing the change from a user/reader perspective

#### CLAUDE.md
- **When**: Changes affect project structure, dependencies, code patterns, or repo organization
- **Skip when**: Changes are limited to content additions (e.g., adding a link to Resources)
- Update only the affected sections — do not rewrite the entire file

#### README files (root or section-level)
- **When**: Changes affect content described by that README
- Examples: adding a notebook -> update the directory's README; renaming a section -> update root README
- **Skip when**: The change is self-evident from the file itself (e.g., adding a row to a resource table — the table IS the README)

#### Stale reference check
After identifying all changed, added, and deleted files, **grep documentation files for references that are now stale**:
- **Deleted files**: Search README.md, CLAUDE.md, and any doc that might reference them (folder trees, file lists, dependency mentions)
- **Renamed/moved files**: Update all path references
- **Removed features or dependencies**: Remove or update mentions in all docs
- Run: `git diff --name-status` to get the full list of deleted (`D`) and renamed (`R`) files, then search docs for those filenames

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
- Content: `docs: add Basic-NLP sentiment analysis notebook`
- Skills: `chore: update ship skill commit strategy`
- Code: `feat: add batch processing to ScholarAnalyzer`
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

### Step 8: Confirm

Run: `git log --oneline -3`

Display the commit hash and message to confirm success.
