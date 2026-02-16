# Organic Positioning Rules

## Content Anchor Rules

- Per-slide `// VISUAL` paragraphs describe where content IS using natural spatial words (e.g., "upper-left", "center-left", "bottom-left")
- Never include a global `## CONTENT PLACEMENT` section in prompts
- Never mention empty space, reserved zones, or percentages
- Never tell the image generator what NOT to put somewhere

## Background Rules

- Background spec in `STYLE_INSTRUCTIONS` is 1-2 lines max (Color + Texture from style file)
- Use words like "flat" and "edge to edge" to imply uniformity
- Never add a Uniformity sub-section
- Never add per-slide "Background must be..." reminder sentences
- Never list what to avoid (no vignettes, no gradients, etc.)

## Video Overlay Integration

- User specifies which side is reserved for post-production video overlay
- Skill derives anchor direction (opposite side) and writes `// VISUAL` descriptions that naturally place content there
- The overlay zone is never mentioned in the prompt — it's simply where content isn't

### Anchor Direction Mapping

| Video Overlay Side | Content Anchor Direction | Natural Spatial Words |
|--------------------|------------------------|-----------------------|
| Right (default) | Left | "upper-left", "center-left", "bottom-left" |
| Left | Right | "upper-right", "center-right", "bottom-right" |
| Bottom | Top | "upper area", "top-center", "upper-left/right" |
| None | Center | "centered", "balanced", freely positioned |
