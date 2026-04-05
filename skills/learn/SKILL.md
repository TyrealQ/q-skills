---
name: learn
description: Persist user preferences and styles across sessions. Use for remember this, save preference, update CLAUDE.md, update CM, or after repeated corrections in a session.
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

Review all user messages for extractable patterns:

- **Corrections**: "don't do X", "stop doing Y", user rewording Claude's output
- **Explicit rules**: "always use...", "never include...", "I prefer..."
- **Positive reinforcement**: user thanking Claude for a specific behavior, accepting a non-obvious approach without pushback
- **Domain context**: role, expertise, institutional affiliation, teaching approach
- **Style edits**: user modifying prose, formatting, or structure Claude produced

Skip these (already handled elsewhere):
- Code error resolutions and library workarounds (covered by `continuous-learning`)
- Patterns Claude's auto memory already captured in this session

### Step 2: Read current state

1. Read `~/CLAUDE.md` in full. Parse the section hierarchy (it evolves — always re-read).
2. List files in `~/.claude/rules/` to check existing rule files.
3. Read the current project's `~/.claude/projects/<project>/memory/MEMORY.md` if it exists.
4. Identify what is already captured across all three tiers to avoid duplication.

### Step 3: Classify each extraction

For each pattern found in Step 1, decide its tier:

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

### Step 4: Present proposed changes

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

### Step 5: Apply approved changes

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

## Safety Rules

- ALWAYS show proposed changes and get explicit approval before writing any file
- NEVER delete or modify existing preferences — only add or refine
- NEVER rewrite entire sections
- If unsure which tier a preference belongs to, ask the user
- If zero preferences are extracted, say so honestly — do not fabricate rules
- If `~/CLAUDE.md` would exceed 200 lines after changes, warn and suggest moving content to `~/.claude/rules/`
- New sections in `~/CLAUDE.md` must use `##` level to maintain flat hierarchy
- For project memory, respect the existing MEMORY.md structure and index pattern
