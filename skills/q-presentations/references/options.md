# Q-Presentations: Options, Usage & Partial Workflows

## Usage

```bash
/q-presentations path/to/content.md
/q-presentations path/to/content.md --style sketch-notes
/q-presentations path/to/content.md --audience executives
/q-presentations path/to/content.md --lang en
/q-presentations path/to/content.md --slides 10
/q-presentations path/to/content.md --outline-only
/q-presentations  # Then paste content
```

## Options

| Option | Description |
|--------|-------------|
| `--style <name>` | Visual style: preset name, `custom`, or custom style name |
| `--audience <type>` | Target: beginners, intermediate, experts, executives, general |
| `--lang <code>` | Output language (en, zh, ja, etc.) |
| `--slides <number>` | Target slide count (8-25 recommended, max 30) |
| `--outline-only` | Generate outline only, skip image generation |
| `--prompts-only` | Generate outline + prompts, skip images |
| `--images-only` | Generate images from existing prompts directory |
| `--regenerate <N>` | Regenerate specific slide(s): `--regenerate 3` or `--regenerate 2,5,8` |
| `--logo <position>` | Logo placement: top-right (default), bottom-right, top-left, bottom-left, none |
| `--video-overlay <side>` | Side reserved for video overlay: right (default), left, bottom, none |

## Partial Workflows

| Option | Workflow |
|--------|----------|
| `--outline-only` | Steps 1-3 only |
| `--prompts-only` | Steps 1-5 only |
| `--images-only` | Start from Step 7 (requires prompts/) |
| `--regenerate N` | Regenerate specific slide(s) only |
