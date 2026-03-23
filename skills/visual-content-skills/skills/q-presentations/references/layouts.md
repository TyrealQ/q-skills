# Layout Gallery

Use this file as the single source of truth for layout selection and overlay-safe placement.

## How To Use

1. Infer content-fit candidates from the `Best For` column.
2. Read `primary_content_bias` for each candidate.
3. Derive the default safe side from bias:
   - `left -> right`
   - `right -> left`
   - `top -> bottom`
   - `center -> none`
4. Apply explicit overrides from the **Exceptions Table**.
5. Filter by requested `video_overlay` side (`right|left|bottom|none`).
6. Rank remaining layouts by content fit and diversity.
7. If no layout remains, use fallback layouts listed below.

Do not mention video-overlay or reserved zones in prompts. Only emit the chosen layout composition.

## Layout Catalog

| Layout | Description | Best For | primary_content_bias |
|--------|-------------|----------|----------------------|
| `title-hero` | Large centered title + subtitle | Cover slides, section breaks | `top` |
| `quote-callout` | Featured quote with attribution | Testimonials, key insights | `center` |
| `key-stat` | Single large number as focal point | Impact statistics, metrics | `center` |
| `split-screen` | Half image, half text | Feature highlights, comparisons | `left` |
| `icon-grid` | Grid of icons with labels | Features, capabilities, benefits | `center` |
| `two-columns` | Content in balanced columns | Paired information, dual points | `center` |
| `three-columns` | Content in three columns | Triple comparisons, categories | `center` |
| `image-caption` | Full-bleed image + text overlay | Visual storytelling, emotional | `center` |
| `agenda` | Numbered list with highlights | Session overview, roadmap | `left` |
| `bullet-list` | Structured bullet points | Simple content, lists | `left` |
| `linear-progression` | Sequential flow left-to-right | Timelines, step-by-step | `left` |
| `binary-comparison` | Side-by-side A vs B | Before/after, pros-cons | `center` |
| `comparison-matrix` | Multi-factor grid | Feature comparisons | `center` |
| `hierarchical-layers` | Pyramid or stacked levels | Priority, importance | `top` |
| `hub-spoke` | Central node with radiating items | Concept maps, ecosystems | `center` |
| `bento-grid` | Varied-size tiles | Overview, summary | `center` |
| `funnel` | Narrowing stages | Conversion, filtering | `top` |
| `dashboard` | Metrics with charts/numbers | KPIs, data display | `center` |
| `venn-diagram` | Overlapping circles | Relationships, intersections | `center` |
| `circular-flow` | Continuous cycle | Recurring processes | `center` |
| `winding-roadmap` | Curved path with milestones | Journey, timeline | `left` |
| `tree-branching` | Parent-child hierarchy | Org charts, taxonomies | `top` |
| `iceberg` | Visible vs hidden layers | Surface vs depth | `top` |
| `bridge` | Gap with connection | Problem-solution | `center` |

## Exceptions Table

Use this table to override derived safe sides when the layout supports controlled variants or must be constrained.

| Layout | Override safe sides | Reason |
|--------|---------------------|--------|
| `split-screen` | `right,left` | Text-image sides can be swapped while keeping hierarchy. |
| `two-columns` | `right,left` | Columns can be weighted toward one side when composing. |
| `binary-comparison` | `right,left` | Side A/B can be mirrored without changing semantics. |
| `agenda` | `right,bottom` | List can stay in upper-left stack, leaving lower band clear. |
| `bullet-list` | `right,bottom` | Bullets can be upper-left aligned with conservative line length. |
| `linear-progression` | `right,bottom` | Sequence can run in top band with compact nodes. |
| `image-caption` | `none` | Full-bleed treatment is not reliably side-safe. |
| `comparison-matrix` | `none` | Matrix spans canvas; side-safe guarantees are weak. |
| `dashboard` | `none` | KPI cards/charts typically need full-width readability. |
| `bento-grid` | `none` | Tile layout distributes weight across the full frame. |

## Fallback Layouts By Overlay Side

Use these only when content-fit filtering produces no valid layout.

| Video Overlay Side | Fallback Layouts |
|--------------------|------------------|
| `right` | `agenda`, `bullet-list`, `split-screen` |
| `left` | `split-screen`, `two-columns`, `binary-comparison` |
| `bottom` | `title-hero`, `hierarchical-layers`, `tree-branching` |
| `none` | Content-fit default ranking only |

## Content Fit Guide

| Content Type | Preferred Layouts |
|--------------|-------------------|
| Single narrative | `bullet-list`, `quote-callout`, `image-caption` |
| Two concepts | `split-screen`, `binary-comparison`, `two-columns` |
| Three items | `three-columns`, `icon-grid` |
| Process / steps | `linear-progression`, `winding-roadmap`, `funnel` |
| Data / metrics | `key-stat`, `dashboard`, `comparison-matrix` |
| Relationships | `hub-spoke`, `venn-diagram`, `bridge` |
| Hierarchy | `hierarchical-layers`, `tree-branching`, `iceberg` |
