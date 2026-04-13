# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Repository Structure

```
q-skills/
|-- skills/
|   |-- q-scholar/                     # Academic manuscript writing suite
|   |   |-- q-multimodal/
|   |   |-- q-eda/
|   |   |-- q-tf/
|   |   |-- q-intro/
|   |   |-- q-litreview/
|   |   |-- q-methods/
|   |   `-- q-results/
|   |-- q-educator/                    # Course content development toolkit
|   |-- q-infographics/                # Document to infographic conversion
|   |-- q-presentations/               # Content to branded slide decks
|   |-- commit/                        # Git commit with smart file grouping
|   |-- learn/                         # Persist user preferences across sessions
|   `-- ship/                          # Full ship cycle: docs, commit, push
|-- README.md
|-- CHANGELOG.md
`-- LICENSE
```

## Skill Categories

The filesystem is flat, but skills group conceptually:

| Category       | Skills                          | Purpose                                            |
| -------------- | ------------------------------- | -------------------------------------------------- |
| Academic       | q-scholar, q-educator           | Manuscript writing, data analysis, teaching        |
| Visual content | q-infographics, q-presentations | Document-to-visual generation                      |
| Utility        | commit, learn, ship             | Git workflow automation, preference persistence    |

## Skill Guidelines

Each skill follows the standard SKILL.md template (~65-97 lines):
- YAML frontmatter (`name`, `description` — imperative verb lead, concise triggers)
- Plan Mode Guard (script-based skills only)
- `## Script Directory` / `## Dependencies` (if scripts exist)
- `## References` — bulleted pointers to reference files, all referenced in body
- `## Core Principles` — 5-7 terse, actionable bullets
- `## Workflow` — `| Step | Action | Reference |` table format
- `## Scope` (optional) — Include / Exclude
- `## Checklist` — 4-8 verification items

Supporting folders:
- `scripts/` — Python scripts for automation
- `references/` — detailed instructions, templates, examples (extracted from SKILL.md)

Skill bundles (like q-scholar) can contain sub-skills:
- Parent `SKILL.md` orchestrates sub-skills
- Shared `references/` at parent level
- Sub-skill folders with their own `SKILL.md` and `references/`

## Script Path Convention

Skills with scripts or references MUST include a **Script Directory** section that uses the `${SKILL_DIR}` pattern:

```markdown
## Script Directory

Agent execution instructions:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`.
2. Script path = `${SKILL_DIR}/scripts/<script-name>`.
3. Reference path = `${SKILL_DIR}/references/<ref-name>`.
```

All script, prompt, and reference paths in the skill MUST use `${SKILL_DIR}/...` — never hardcode cache-relative paths like `skills/q-foo/scripts/...`. This ensures skills work correctly when loaded from the Claude Code plugin cache.

## Adding New Skills

1. Create folder in `skills/` with lowercase hyphenated name (see Naming Convention below)
2. Add `SKILL.md` with proper frontmatter
3. Add the skill path to the `skills` array in `.claude-plugin/marketplace.json`
4. Update `README.md` to include new skill
5. Update `CHANGELOG.md` with version bump

## Naming Convention

- Skill folders: lowercase, hyphens
- Academic and visual-content skills use the `q-` prefix (e.g., `q-scholar`, `q-infographics`)
- Utility skills use bare verb names matching their invocation syntax (`commit`, `learn`, `ship`)
- Scripts: `snake_case.py`
