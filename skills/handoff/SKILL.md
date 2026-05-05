---
name: handoff
description: Capture session decisions, conventions, and lessons into plan files, auto-memory, and CLAUDE.md so a fresh session resumes cleanly. Use for "hand off," "wrap up," "update docs for next session," or before /compact.
---

# handoff

Captures the load-bearing outcomes of a session and writes them to the right durable location. Goal: a future session can pick up without re-deriving context from the transcript.

## Workflow

### Step 1 — Survey the session

Identify what changed beyond the literal edits.

```bash
git log --oneline <session-start>..HEAD
git diff <session-start>..HEAD --stat
```

If session-start is unclear, infer from the first commit timestamp after a context reset, or ask the user.

For each commit, note:
- **Decisions**: terminology choices, structural conventions, methodological positions taken
- **Conventions reinforced or established**: subtitle patterns, voice rules, argument structures, naming schemes
- **Controversies resolved**: where the user pushed back and a final position landed
- **Lessons that emerged**: when an early draft failed, what symptom triggered the fix, what rule the fix expressed (latent rules > literal pushbacks)

Skip routine work: typo fixes, formatting-only changes, mechanical refactors. Only capture outcomes a future session would otherwise have to re-derive.

### Step 2 — Locate destinations

Discover what already exists; do not create new doc locations without asking.

```bash
# Plan files (task tracking, current state, open items)
ls ~/.claude/plans/ 2>/dev/null | grep -i <project-keyword>

# Auto-memory (cross-session learnings keyed to project)
ls ~/.claude/projects/<project-id>/memory/ 2>/dev/null

# Project CLAUDE.md (project conventions, structure, banned terms)
ls <project-root>/CLAUDE.md 2>/dev/null

# User CLAUDE.md (cross-project preferences)
ls ~/CLAUDE.md 2>/dev/null
```

Match each session outcome to the right destination:

| Outcome type | Destination |
|---|---|
| Task progress, completed items, residual open items | Plan file |
| Verified-state anchors (specific phrasings that mark current correct state) | Plan file |
| Writing/coding lessons, symptom → rule patterns | Auto-memory `*_lessons.md` |
| Banned terms, terminology decisions | Auto-memory `*_terms.md` (or project CLAUDE.md if it already lists them) |
| Project-level conventions (file layout, naming, structure) | Project CLAUDE.md |
| Cross-project user preferences | User CLAUDE.md |

Do not duplicate. If a rule lives in CLAUDE.md, do not also add it to memory; if a lesson lives in memory, do not restate it in the plan.

### Step 3 — Apply updates

Read every target file before editing. Match the existing style, depth, and section conventions.

- **Plan files**: mark resolved items with strikethrough or `RESOLVED YYYY-MM-DD` tag; append new open items; refresh "verified state" anchors with the line content as it stands now (not as drafted earlier in the session).
- **Auto-memory `*_lessons.md`**: append numbered lessons (L7, L8, ...) with **trigger** + **corrective move** + brief rationale. Update the file's frontmatter `description` if the scope expanded.
- **MEMORY.md index**: add a pointer line only if a new memory file was created. Update the existing entry's hook only if its underlying content shifted materially. Keep each line under ~150 chars.
- **Project CLAUDE.md**: insert into the appropriate existing section (style rules, structure, etc.). Do not create a session log section. If a new convention does not fit any section, ask before adding.
- **User CLAUDE.md**: only for preferences that generalize beyond the current project. Be conservative.

### Step 4 — Produce a resume prompt

Output a single message the user can copy-paste verbatim into a fresh session as the opening prompt. The next Claude reads this message and a fresh, cold-started auto-memory load — nothing else from the prior transcript carries over. The resume prompt must be self-contained.

Wrap the resume prompt in a clearly delimited block (e.g., ` ```text ... ``` `) so the user can copy it cleanly.

Required sections, in order:

1. **Context** — one sentence on what project this is and what stage the work is at.
2. **Read first** — explicit absolute paths to the files the next Claude should load before acting (plan file, key memory files if not auto-loaded, the canonical source document, the active downstream document). Annotate each with one phrase on why.
3. **Where we left off** — last 2–4 commits relevant to the resumed thread (hash + one-line summary). Do not list every commit; only the load-bearing ones.
4. **Conventions to honor** — only conventions established or reinforced THIS session that have not yet propagated into memory or CLAUDE.md. If everything is durable, write "All conventions are captured in memory and the plan file."
5. **Next task** — the single most actionable next item with a `file:line` pointer and a one-sentence statement of the change to make. If multiple, list up to 3 in priority order.
6. **Known gotchas** — only if relevant: discrepancies, blockers, or non-obvious traps the next session should be aware of. Omit the section if none.

After the wrapped resume prompt, add a 2-line operator note for the user (outside the block):
- where the new commits and doc updates landed (commit-hash range, files touched)
- whether anything is uncommitted

Keep the resume prompt itself under ~250 words. The user pastes it; the next Claude executes from there.

## Anti-patterns

- **Don't write session logs into project files.** Permanent docs capture conventions, not session narratives.
- **Don't update CLAUDE.md with rules already in memory** (and vice versa). Each rule has one durable home.
- **Don't create new doc locations** without asking. Use what exists.
- **Don't restate edits as "decisions."** A typo fix is not a decision. A terminology choice the user pushed back on twice is.
- **Don't bloat memory.** Each memory file should have a clear scope. If a new lesson does not fit any existing file, ask before creating a new one.
- **Don't extract lessons the user has not validated.** A first-draft pattern from one session is a hypothesis, not a rule. Wait for repeated correction or explicit confirmation before persisting.
