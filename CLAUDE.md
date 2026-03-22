# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Repository Structure

```
q-skills/
|-- plugins/
|   |-- academic-skills/skills/        # Academic writing & teaching
|   |   |-- q-scholar/                 # Academic manuscript writing suite
|   |   |   |-- q-intro/
|   |   |   |-- q-eda/
|   |   |   |-- q-topic-finetuning/
|   |   |   |-- q-methods/
|   |   |   `-- q-results/
|   |   `-- q-educator/                # Course content development toolkit
|   |-- visual-content-skills/skills/  # Visual content generation
|   |   |-- q-infographics/            # Document to infographic conversion
|   |   `-- q-presentations/           # Content to branded slide decks
|   `-- utility-skills/skills/         # Git workflow automation
|       |-- commit/                    # Git commit with smart file grouping
|       |-- learn/                     # Persist user preferences across sessions
|       `-- ship/                      # Full ship cycle: docs, commit, push
|-- README.md
|-- CHANGELOG.md
`-- LICENSE
```

Each plugin has its own `source` directory in `plugins/`, so Claude Code caches only the skills that belong to that plugin.

## Skill Guidelines

Each skill follows the standard structure:
- `SKILL.md` - Main skill file with YAML frontmatter (name, description)
- `scripts/` - Python scripts for automation
- `references/` - Reference documentation and examples

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

1. Identify which plugin the skill belongs to (academic, visual-content, or utility)
2. Create folder in `plugins/<plugin-name>/skills/` with lowercase name using hyphens
3. Add `SKILL.md` with proper frontmatter
4. Add the skill path to the plugin's `skills` array in `.claude-plugin/marketplace.json`
5. Update `README.md` to include new skill
6. Update `CHANGELOG.md` with version bump

## Naming Convention

- Skill folders: `q-{name}` (lowercase, hyphens)
- Scripts: `snake_case.py`
- Always prefix with `q-` for consistency
