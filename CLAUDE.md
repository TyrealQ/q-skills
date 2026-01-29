# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Repository Structure

```
q-skills/
├── skills/              # All skills in subdirectory
│   ├── q-methods/
│   ├── q-topic-finetuning/
│   └── q_descriptive-analysis/
├── README.md
├── CHANGELOG.md
└── LICENSE
```

## Skill Guidelines

Each skill follows the standard structure:
- `SKILL.md` - Main skill file with YAML frontmatter (name, description)
- `scripts/` - Python scripts for automation
- `references/` - Reference documentation and examples

## Adding New Skills

1. Create folder in `skills/` with lowercase name using hyphens
2. Add `SKILL.md` with proper frontmatter
3. Update `README.md` to include new skill
4. Update `CHANGELOG.md` with version bump

## Naming Convention

- Skill folders: `q-{name}` (lowercase, hyphens)
- Scripts: `snake_case.py`
- Always prefix with `q-` for consistency
