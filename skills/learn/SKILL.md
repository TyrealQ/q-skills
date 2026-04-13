---
name: learn
description: Persist user preferences and styles across sessions. Use for remember this, save preference, learn this, always do X, never do Y, from now on, update CLAUDE.md, update CM, forget X, what do you remember, or after repeated corrections in a session.
---

# Personal Preference Learning

Extract preferences, styles, and behavioral patterns from the current conversation and persist them for all future sessions.

**Scope:** This skill captures how the user works, writes, and wants agents to behave. It does NOT capture code patterns, error fixes, or debugging techniques.

## Three-Tier Target Architecture

| Tier | Location | Loaded | Use for |
|------|----------|--------|---------|
| **User instructions** | `~/CLAUDE.md` | Every session, in full | Concise behavioral rules that apply to all projects |
| **User rules** | `~/.claude/rules/*.md` | Every session (or on file match) | Structured rule sets on a single topic; optionally path-scoped |
| **Project memory** | `~/.claude/projects/<project>/memory/` | First 200 lines of MEMORY.md; topic files on demand | Project-specific conventions, domain context |

`~/CLAUDE.md` should stay under 200 lines. When it grows, move coherent rule groups to `~/.claude/rules/`.

## Workflow

### Step 1: Scan conversation

Review all user messages for extractable patterns. Use the phrase families below as signals — do not infer preferences from silence or context alone.

**Explicit rules** (highest priority, save immediately):
- "always…", "never…", "from now on…", "I prefer…"
- "remember that I…", "make sure you…"

**Corrections** (save if repeated, see Step 2):
- "don't do X", "stop doing Y", "that's not right"
- "actually, it should be…", "I told you before…"
- User rewording or editing Claude's output in place

**Positive reinforcement** (save when the approach was non-obvious):
- User thanking Claude for a specific behavior
- Accepting an unusual choice without pushback (quieter signal — note *why* it was non-obvious)

**Domain context** (save as user-tier facts):
- Role, expertise, institutional affiliation, teaching approach
- Tools, frameworks, or workflows the user commits to long-term

**Style edits** (save as style rules):
- User modifying prose, formatting, or structure Claude produced
- Terminology corrections ("use X not Y")

**Non-signals — skip these**:
- One-time instructions ("do X now", "for this file only")
- Hypotheticals ("what if I wanted…", "could you also…")
- Third-party preferences ("my coauthor likes…", "reviewers want…")
- Silence (user didn't push back ≠ user approved)
- Code error resolutions and library workarounds (covered by `continuous-learning`)
- Patterns Claude's auto memory already captured this session

### Step 2: Apply the repetition threshold

A single off-hand correction is not a durable preference. Before promoting any pattern to later steps:

- **Explicit rule** ("always…", "never…", "from now on…") → save immediately
- **Repeated correction** (same pattern corrected 2+ times this session or referenced as "I told you before") → save as tentative, note the repetition
- **One-time correction** with no repetition and no explicit framing → skip, do not fabricate a rule
- **Inferred from silence or hypothetical** → skip unconditionally (see `## Anti-Patterns` below)

If a tentative pattern has been corrected 3+ times across sessions (check existing `~/CLAUDE.md` for near-duplicates), surface it in Step 6 with a "**Confirm as permanent rule?**" flag so the user decides explicitly.

### Step 3: Read current state

1. Read `~/CLAUDE.md` in full. Parse the section hierarchy (it evolves — always re-read).
2. List files in `~/.claude/rules/` to check existing rule files.
3. Read the current project's `~/.claude/projects/<project>/memory/MEMORY.md` if it exists.
4. Identify what is already captured across all three tiers to avoid duplication.

### Step 4: Detect conflicts with existing preferences

For each extraction, search the already-loaded `~/CLAUDE.md` and rule files for contradicting text. If a conflict is found:

1. Do NOT silently overwrite the existing rule.
2. In Step 6's preview, show both entries side-by-side under a `## Conflicts` heading and ask which supersedes which.
3. Resolution defaults: more specific scope wins (project > user rule > `~/CLAUDE.md`); within the same tier, the newer instruction wins only after explicit approval.

### Step 5: Classify each extraction

For each pattern that survived Steps 1–4, decide its tier:

| If the pattern... | Route to | Example |
|-------------------|----------|---------|
| Is a concise rule for all projects | `~/CLAUDE.md` — match to existing section or propose new `##` section | "Never use em-dashes in emails" |
| Is part of 5+ rules on one topic | `~/.claude/rules/new-topic.md` | A full set of workflow preferences |
| Is specific to the current project | Project memory | "TGL uses SDT framework with 1-7 scales" |
| Is already covered by an existing rule | Skip — note the existing rule | |
| Is a one-time correction | Skip | |

Categories and typical tiers:

| Category | Typical Tier | Typical Location |
|----------|-------------|-----------------|
| Writing style | User instructions | `~/CLAUDE.md` under `## Academic Writing` subsections |
| Email conventions | User instructions | `~/CLAUDE.md` under `## Email Drafting` |
| Communication preferences | User instructions | `~/CLAUDE.md` under `## Communication` (create if needed) |
| Workflow preferences | User instructions or rules | `~/CLAUDE.md` or `~/.claude/rules/workflow.md` |
| Agent behavior | User instructions or rules | `~/CLAUDE.md` or `~/.claude/rules/agent-behavior.md` |
| Project domain context | Project memory | `~/.claude/projects/<project>/memory/` |

### Step 6: Present proposed changes

Show a numbered preview grouped by tier:

```
## Tier 1: User Instructions (~/CLAUDE.md)

### [1] Add to "## Academic Writing > ### Style" (existing section)
+ - Do not use semicolons to join independent clauses in academic prose

### [2] New section: "## Workflow" (after last existing ## section)
+ - When re-running a pipeline, first check what outputs already exist in cache
+ - Prefer flat directory structures keyed by ID over nested semantic hierarchies

## Tier 2: User Rules (~/.claude/rules/)

### [3] New file: ~/.claude/rules/communication.md
+ # Communication Preferences
+ - Lead with the answer, not the reasoning

## Tier 3: Project Memory

### [4] Add to project memory MEMORY.md
+ - TGL project uses SDT framework (autonomy, competence, relatedness) scored 1-7

## Skipped

- "Use precise terminology" → already in ~/CLAUDE.md ### Word Choice

Approve all? Or specify numbers to modify/reject.
```

### Step 7: Apply approved changes

**Tier 1 — `~/CLAUDE.md`:**
- Use the Edit tool for surgical insertions
- Insert new bullets at the end of the target section, before the next heading
- For new sections, use `##` heading level (same as `## Email Drafting`)
- Report the final line count

**Tier 2 — `~/.claude/rules/`:**
- Create new rule files as plain markdown with a descriptive `# Heading`
- Use `paths` frontmatter only if the rules apply to specific file types
- One topic per file; use descriptive filenames (e.g., `workflow.md`, `communication.md`)

**Tier 3 — Project memory:**
- Write to `~/.claude/projects/<project>/memory/`
- Follow the auto memory format: `MEMORY.md` as index, topic files for details
- Use the same frontmatter format as existing memory files (name, description, type)

Confirm all changes applied.

## Query Mode

The skill can also answer questions about what has already been remembered, without writing anything. Trigger phrases:

| User says | Action |
|-----------|--------|
| "What do you remember about me?" / "Show preferences" | Summarize `##` sections in `~/CLAUDE.md` + list `~/.claude/rules/*.md` files with one-line descriptions |
| "What's in [topic]?" | Quote the matching section verbatim with its file path and line range |
| "Forget X" | Locate X across all three tiers, show the exact lines, and ask for confirmation before deletion |
| "What did you learn this session?" | List entries added in the current session only |

Query mode is read-only — only "Forget X" writes, and only after explicit confirmation. Never infer intent: if the request is ambiguous, ask before reading.

## Anti-Patterns

Common failure modes this skill must avoid. When any of these fire, skip the extraction and do not save anything.

| Trap | Why it fails | Correct move |
|------|--------------|--------------|
| Inferring from silence | User didn't object ≠ user approved | Wait for explicit correction or repeated evidence |
| Promoting after one mention | Fabricated rules pollute `~/CLAUDE.md` | Require explicit framing ("always…", "never…") or 2+ repetitions (see Step 2) |
| Learning from hypotheticals | "What if I wanted X?" is a question, not a preference | Skip unless the user commits to the framing |
| Learning third-party preferences | Belongs to someone else, may be wrong for current user | Only capture first-person statements |
| Over-generalizing from narrow context | "For this one file" becomes a global rule | Preserve the scope in the saved entry, or route to project memory |
| Learning style over substance | Echoing Claude's own phrasing back as rules | Save the behavior the user demanded, not metacommentary about it |
| Silently rewriting an existing rule | User loses the audit trail | Surface as a conflict in Step 4; get explicit approval |

## Safety Rules

- ALWAYS show proposed changes and get explicit approval before writing any file
- NEVER delete or modify existing preferences — only add or refine
- NEVER rewrite entire sections
- NEVER log preferences inferred from silence, context, or a single off-hand remark (see `## Anti-Patterns` above)
- NEVER save third-party preferences (e.g., "my coauthor likes…") — only the current user's own preferences
- NEVER store credentials, API keys, health information, or PII, even if the user explicitly asks
- If unsure which tier a preference belongs to, ask the user
- If zero preferences are extracted, say so honestly — do not fabricate rules
- If `~/CLAUDE.md` would exceed 200 lines after changes, warn and suggest moving content to `~/.claude/rules/`
- New sections in `~/CLAUDE.md` must use `##` level to maintain flat hierarchy
- For project memory, respect the existing MEMORY.md structure and index pattern

## Out of Scope

This skill does NOT:

- Track numeric confidence scores or usage-decay timers
- Auto-sync to any external agent product config (Cursor, Gemini, OpenClaw, …)
- Modify its own SKILL.md
- Edit `CHANGELOG.md`, `README.md`, or git history
- Capture code error resolutions or library workarounds (that is `continuous-learning`'s job)
